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
