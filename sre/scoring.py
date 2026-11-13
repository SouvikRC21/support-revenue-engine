"""Churn and expansion scoring.

The same formulas are mirrored in dashboard/index.html (function scoreAccount) so the
dashboard can re-score live when someone edits an assumption. Keep the two in step;
tests/test_parity.py checks they agree.
"""
import math


def clamp(x, lo=0.0, hi=1.0):
    return max(lo, min(hi, x))


def churn_components(s, whatif=None):
    """Five indicators, each normalised to 0 (healthy) .. 1 (severe)."""
    w = whatif or {}
    esc_cut = w.get("escalation_reduction", 0.0)
    adoption_lift = w.get("adoption_lift", 0.0)

    tickets = max(1, s["tickets_90d"])
    # rates per 100 tickets, measured against a healthy baseline (about 9 escalations and 3 Sev1s per 100)
    esc_per_100 = 100 * s["escalations_90d"] * (1 - esc_cut) / tickets
    sev1_per_100 = 100 * s["sev1_90d"] * (1 - esc_cut) / tickets
    escalation = (0.6 * clamp((esc_per_100 - 9) / 12)
                  + 0.25 * clamp((sev1_per_100 - 3) / 5)
                  + 0.15 * clamp((s["reopen_rate"] - 0.12) / 0.3))

    util = clamp(s["seats_active"] / max(1, s["seats_licensed"]) + adoption_lift)
    breadth = len(s["modules_used"]) / max(1, len(s["modules_licensed"]))
    adoption = 0.6 * clamp((0.75 - util) / 0.5) + 0.4 * clamp((0.6 - breadth) / 0.5)

    csat = s["csat"] if s["csat"] is not None else 4.2
    voice = (0.5 * clamp((0.2 - s["sentiment"]) / 0.8)
             + 0.3 * clamp((4.4 - csat) / 1.8)
             + 0.2 * clamp(s["churn_mentions_90d"] / 4))

    disengagement = (0.5 * clamp(-s["usage_trend"] / 0.35)
                     + 0.2 * clamp(s["days_since_exec_touch"] / 120)
                     + 0.3 * (1.0 if s["champion_left"] else 0.0))

    # complaint surge and handling time: the customer is hurting and each ticket takes longer to close
    aht_cut = w.get("aht_reduction", 0.0)
    comp = s["complaints_monthly"]
    last = comp[-1] * (1 - esc_cut)
    base = max(1.0, sum(comp[-4:-1]) / 3)
    ratio = last / base if last >= 4 else 1.0
    share = sum(comp[-3:]) * (1 - esc_cut) / tickets
    aht_change = (s["aht_recent_hours"] * (1 - aht_cut)) / max(0.01, s["aht_prior_hours"]) - 1
    service_strain = (0.4 * clamp((ratio - 1.2) / 1.5)
                      + 0.2 * clamp((share - 0.04) / 0.08)
                      + 0.4 * clamp((aht_change - 0.05) / 0.35))

    return {"escalation": escalation, "adoption": adoption, "voice": voice, "disengagement": disengagement,
            "service_strain": service_strain}


def churn_probability(score, curve):
    return 1 / (1 + math.exp(-curve["steepness"] * (score - curve["midpoint"])))


def band(p, bands):
    if p >= bands["red"]:
        return "red"
    if p >= bands["amber"]:
        return "amber"
    return "green"


def expansion(s, cfg, churn_band, whatif=None):
    e = cfg["expansion"]
    w = whatif or {}
    util = clamp(s["seats_active"] / max(1, s["seats_licensed"]) + w.get("adoption_lift", 0.0))
    breadth = len(s["modules_used"]) / max(1, len(s["modules_licensed"]))
    seat_signal = 0.7 * clamp((util - 0.7) / (e["seat_threshold"] - 0.7)) + 0.3 * clamp((breadth - 0.6) / 0.4)
    seat_trigger = util >= e["seat_threshold"]

    surges = []
    for use_case, series in s["howto_by_use_case"].items():
        if use_case in s["addons_licensed"] or use_case in s["modules_licensed"]:
            continue  # only care about things they have not bought yet
        last = series[-1]
        baseline = max(1.0, sum(series[-4:-1]) / 3)
        ratio = last / baseline
        if last >= e["surge_min_queries"] and ratio >= e["surge_ratio"]:
            surges.append({"use_case": use_case, "last_month": last, "baseline": round(baseline, 1), "ratio": round(ratio, 2)})
    surges.sort(key=lambda x: -x["ratio"])
    surge_signal = clamp((surges[0]["ratio"] - 1) / (2 * (e["surge_ratio"] - 1))) if surges else 0.0

    blocked = churn_band == "red"  # never pitch an upsell into a burning account
    value = 0.0
    if not blocked:
        if seat_trigger:
            value += s["arr"] * e["seat_uplift"]
        if surges:
            value += s["arr"] * e["addon_uplift"]
    return {
        "score": round(0.5 * seat_signal + 0.5 * surge_signal, 3),
        "seat_trigger": seat_trigger,
        "surges": surges,
        "blocked_by_risk": blocked and (seat_trigger or bool(surges)),
        "pipeline_value": round(value),
    }


def score_account(s, cfg, whatif=None):
    comps = churn_components(s, whatif)
    wts = cfg["weights"]
    total_w = sum(wts.values()) or 1
    score = sum(wts[k] * comps[k] for k in comps) / total_w
    p = churn_probability(score, cfg["churn_curve"])
    b = band(p, cfg["bands"])
    exp = expansion(s, cfg, b, whatif)
    weighted_exp = exp["pipeline_value"] * cfg["expansion"]["win_rate"] * (1 - p)
    primary = max(comps, key=lambda k: wts[k] * comps[k])
    return {
        "components": {k: round(v, 3) for k, v in comps.items()},
        "risk_score": round(score, 3),
        "churn_probability": round(p, 3),
        "band": b,
        "primary_driver": primary,
        "arr_at_risk": round(p * s["arr"]),
        "expansion": exp,
        "expansion_weighted": round(weighted_exp),
    }
