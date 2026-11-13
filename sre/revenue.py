"""Roll account results up into the numbers leadership reads: ARR at risk, ARR we can save,
expansion pipeline, and the ratio of revenue influenced to what support costs."""


def rollup(cfg, scored):
    clients = {}
    for cid, c in cfg["clients"].items():
        rows = [r for r in scored if r["client"] == cid]
        arr = sum(r["arr"] for r in rows)
        at_risk = sum(r["result"]["arr_at_risk"] for r in rows)
        actionable = sum(r["result"]["arr_at_risk"] for r in rows if r["result"]["band"] != "green")
        saved = actionable * cfg["save_rate"]
        pipeline = sum(r["result"]["expansion"]["pipeline_value"] for r in rows)
        exp_weighted = sum(r["result"]["expansion_weighted"] for r in rows)
        cost = c["engineers"] * cfg["cost_per_engineer_usd"]
        clients[cid] = {
            "name": c["name"],
            "accounts": len(rows),
            "arr": arr,
            "tickets_per_month": c["tickets_per_month"],
            "red": sum(r["result"]["band"] == "red" for r in rows),
            "amber": sum(r["result"]["band"] == "amber" for r in rows),
            "arr_at_risk": round(at_risk),
            "arr_saveable": round(saved),
            "expansion_pipeline": round(pipeline),
            "expansion_weighted": round(exp_weighted),
            "support_cost": cost,
            "support_contract_value": c["support_contract_value_usd"],
            "revenue_influenced": round(saved + exp_weighted),
        }
    total = {k: sum(v[k] for v in clients.values()) for k in
             ("accounts", "arr", "red", "amber", "arr_at_risk", "arr_saveable", "expansion_pipeline",
              "expansion_weighted", "support_cost", "support_contract_value", "revenue_influenced", "tickets_per_month")}
    prog = cfg.get("program", {"pod_headcount": 0, "tooling_usd": 0})
    total["program_cost"] = prog["pod_headcount"] * cfg["cost_per_engineer_usd"] + prog["tooling_usd"]
    # revenue influenced per dollar of the whole support org (does support pay for itself?)
    total["multiplier"] = round(total["revenue_influenced"] / total["support_cost"], 2) if total["support_cost"] else 0
    # revenue influenced per dollar spent running the revenue intelligence programme
    total["program_roi"] = round(total["revenue_influenced"] / total["program_cost"], 1) if total["program_cost"] else 0
    return {"clients": clients, "total": total}


def glide_path(cfg, scored):
    """Quarter by quarter view of what the programme returns, with a floor (minimum) and an expected case.

    Retention value lands only in the quarter an account renews. Expansion briefs start at day 61, so
    nothing closes in quarter 1. Capacity released is engineer time freed by lower handling time.
    """
    g = cfg["glide"]
    cost = cfg["cost_per_engineer_usd"]
    tickets_q = sum(c["tickets_per_month"] for c in cfg["clients"].values()) * 3
    t90 = sum(r["tickets_90d"] for r in scored) or 1
    aht = sum(r["aht_recent_hours"] * r["tickets_90d"] for r in scored) / t90
    esc100 = 100 * sum(r["escalations_90d"] for r in scored) / t90
    complaints = sum(r["complaints_monthly"][-1] for r in scored)
    csats = [r["csat"] for r in scored if r["csat"] is not None]
    csat = sum(csats) / len(csats)
    hours_per_q = g["engineer_hours_per_year"] / 4
    exp_weighted = sum(r["result"]["expansion_weighted"] for r in scored)
    win_ratio = g["floor_win_rate"] / cfg["expansion"]["win_rate"]

    quarters = []
    cum_floor = cum_exp = 0.0
    for q in range(4):
        renewing = [r for r in scored if r["renewal_quarter"] == q + 1 and r["result"]["band"] != "green"]
        at_risk = sum(r["result"]["arr_at_risk"] for r in renewing)
        ret_exp = at_risk * cfg["save_rate"] * g["retention_ramp"][q]
        ret_floor = at_risk * g["floor_save_rate"] * g["retention_ramp"][q]
        exp_exp = exp_weighted / 4 * g["expansion_ramp"][q]
        exp_floor = exp_exp * win_ratio
        hours = tickets_q * aht * g["aht_reduction"][q]
        cap_exp = hours / hours_per_q * cost / 4
        cap_floor = cap_exp * 0.5
        floor = ret_floor + exp_floor + cap_floor
        expected = ret_exp + exp_exp + cap_exp
        cum_floor += floor
        cum_exp += expected
        quarters.append({
            "quarter": q + 1,
            "renewals_flagged": len(renewing),
            "arr_renewing_at_risk": round(at_risk),
            "retention_floor": round(ret_floor), "retention_expected": round(ret_exp),
            "expansion_floor": round(exp_floor), "expansion_expected": round(exp_exp),
            "capacity_floor": round(cap_floor), "capacity_expected": round(cap_exp),
            "engineer_hours_released": round(hours),
            "fte_released": round(hours / hours_per_q, 1),
            "total_floor": round(floor), "total_expected": round(expected),
            "cumulative_floor": round(cum_floor), "cumulative_expected": round(cum_exp),
            "escalations_per_100": round(esc100 * (1 - g["escalation_reduction"][q]), 1),
            "aht_hours": round(aht * (1 - g["aht_reduction"][q]), 2),
            "complaints_per_month": round(complaints * (1 - g["complaint_reduction"][q])),
            "csat": round(csat + g["csat_lift"][q], 2),
        })
    return {
        "baseline": {"escalations_per_100": round(esc100, 1), "aht_hours": round(aht, 2),
                     "complaints_per_month": complaints, "csat": round(csat, 2)},
        "quarters": quarters,
        "day90_minimum": quarters[0]["total_floor"],
        "year1_floor": round(cum_floor),
        "year1_expected": round(cum_exp),
    }
