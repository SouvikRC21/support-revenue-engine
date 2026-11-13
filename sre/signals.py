"""Turn raw tickets plus telemetry into per-account signals.

This is the part a support team owns: ticket data is already in our hands, so these
features cost nothing extra to collect. Text sentiment uses a small transparent lexicon
so every score can be explained to an account team; swap in an LLM classifier later
without changing the downstream contract.
"""
import re
from collections import defaultdict

POSITIVE = {"thanks", "great", "resolved", "appreciate", "helpful", "quick", "set"}
NEGATIVE = {"broken", "frustrated", "unacceptable", "disappointed", "delay", "escalate", "again", "still", "waiting"}
CHURN_TERMS = {"alternatives", "competitor", "renewal", "contract", "cancel", "terminate", "switch"}
WORD = re.compile(r"[a-z]+")


def sentiment(text):
    """Return (score in [-1, 1], churn_mention bool) for one ticket comment."""
    words = WORD.findall(text.lower())
    pos = sum(w in POSITIVE for w in words)
    neg = sum(w in NEGATIVE for w in words)
    churn = any(w in CHURN_TERMS for w in words)
    if churn:
        neg += 2
    total = pos + neg
    score = 0.0 if total == 0 else (pos - neg) / total
    return score, churn


def build_signals(cfg, accounts, telemetry, tickets):
    months = cfg["months"]
    recent = set(months[-3:])
    by_acc = defaultdict(list)
    for t in tickets:
        by_acc[t["account_id"]].append(t)

    out = []
    for a in accounts:
        ts = by_acc[a["id"]]
        r = [t for t in ts if t["month"] in recent]
        monthly = [sum(1 for t in ts if t["month"] == m) for m in months]
        sev1 = sum(1 for t in r if t["severity"] == "S1")
        esc = sum(1 for t in r if t["escalated"])
        defects = [t for t in r if t["category"] in ("defect", "outage")]
        reopen = (sum(1 for t in defects if t["reopened"]) / len(defects)) if defects else 0.0
        sents, churn_mentions = [], 0
        for t in r:
            s, c = sentiment(t["text"])
            sents.append(s)
            churn_mentions += c
        csats = [t["csat"] for t in r if t["csat"] is not None]

        howto = defaultdict(lambda: [0] * len(months))
        for t in ts:
            if t["category"] == "how_to":
                howto[t["use_case"]][months.index(t["month"])] += 1

        complaints = [sum(1 for t in ts if t["month"] == m and t["category"] == "complaint") for m in months]
        prior = [t for t in ts if t["month"] not in recent]
        aht_recent = sum(t["handle_hours"] for t in r) / len(r) if r else 0.0
        aht_prior = sum(t["handle_hours"] for t in prior) / len(prior) if prior else aht_recent

        tel = telemetry[a["id"]]
        out.append({
            **{k: a[k] for k in ("id", "client", "name", "segment", "region", "arr", "archetype",
                                 "seats_licensed", "seats_active", "modules_licensed", "modules_used",
                                 "addons_licensed", "renewal_quarter")},
            "tickets_monthly": monthly,
            "tickets_90d": len(r),
            "complaints_monthly": complaints,
            "aht_recent_hours": round(aht_recent, 2),
            "aht_prior_hours": round(aht_prior, 2),
            "aht_monthly": [round(sum(t["handle_hours"] for t in ts if t["month"] == m) / max(1, n), 2)
                            for m, n in zip(months, monthly)],
            "escalations_90d": esc,
            "sev1_90d": sev1,
            "reopen_rate": round(reopen, 3),
            "sentiment": round(sum(sents) / len(sents), 3) if sents else 0.0,
            "csat": round(sum(csats) / len(csats), 2) if csats else None,
            "churn_mentions_90d": churn_mentions,
            "usage_trend": tel["usage_trend"],
            "days_since_exec_touch": tel["days_since_exec_touch"],
            "champion_left": tel["champion_left"],
            "howto_by_use_case": dict(howto),
        })
    return out
