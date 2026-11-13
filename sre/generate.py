"""Synthetic data generator.

Produces two things a real deployment would pull from source systems:
  * tickets    - what the ticketing tool holds (Jira Service Management, Zendesk, ServiceNow)
  * telemetry  - what product analytics and the CRM hold (seat usage, logins, exec touchpoints, champion changes)

Every company and account name is fictional. The two clients are modelled on a social/CX SaaS
platform and a streaming media platform; neither is a real company.
"""
import math
import random

PREFIXES = [
    "Aurelia", "Bluefin", "Cobalt", "Driftwood", "Ember", "Fernhill", "Granite", "Harborlight",
    "Ironleaf", "Juniper", "Kestrel", "Larkspur", "Meridian", "Northgate", "Oakridge", "Pinecrest",
    "Quarrystone", "Redwing", "Silverline", "Tidewater", "Umberfield", "Vantor", "Willowmere",
    "Yarrowby", "Zephyrine", "Alderbrook", "Brightwater", "Copperfield", "Dunmore", "Evermoor",
    "Falconridge", "Glenhaven", "Holloway", "Indigo Bay", "Jasperline", "Kingsmere",
]
SUFFIXES = {
    "lumora": ["Retail", "Bank", "Airways", "Telecom", "Insurance", "Foods", "Motors", "Hotels", "Health", "Apparel"],
    "streamhaus": ["Media", "Mobile", "Broadband", "Ads", "Studios", "Devices", "Networks", "Cable"],
}
REGIONS = ["North America", "EMEA", "APAC", "LATAM"]
CATEGORIES = ["how_to", "defect", "outage", "access", "billing", "feature_request"]

# Archetypes give the synthetic portfolio realistic stories to find.
ARCHETYPES = [
    ("healthy", 0.56),
    ("escalation_hit", 0.08),
    ("low_adoption", 0.08),
    ("unhappy_voice", 0.07),
    ("drifting", 0.07),
    ("expansion_ready", 0.14),
]

TEXT = {
    "positive": [
        "Thanks for the quick fix, the team really appreciate it.",
        "Resolved, great help from the engineer on the call.",
        "Helpful walkthrough, we are all set now.",
    ],
    "neutral": [
        "Need guidance on how to configure this for our regional teams.",
        "Please share steps to set this up for a new business unit.",
        "Requesting access for two new users.",
        "Question about the invoice line items this month.",
    ],
    "negative": [
        "This is broken again and the team is frustrated.",
        "Still waiting on a fix, this delay is unacceptable.",
        "Third time this issue came back, very disappointed.",
        "Please escalate, the workaround is not acceptable for our launch.",
    ],
    "churn": [
        "Leadership is reviewing alternatives before the renewal.",
        "If this is not fixed we will have to look at a competitor.",
        "We are questioning the contract value given these issues.",
    ],
}


def _weighted(rng, pairs):
    r = rng.random() * sum(w for _, w in pairs)
    for item, w in pairs:
        r -= w
        if r <= 0:
            return item
    return pairs[-1][0]


def _clip(x, lo, hi):
    return max(lo, min(hi, x))


def build_accounts(cfg, rng):
    accounts = []
    used_names = set()
    for client_id, c in cfg["clients"].items():
        n = c["accounts"]
        raw = [math.exp(rng.gauss(0, 0.55)) for _ in range(n)]
        scale = c["avg_account_arr_usd"] / (sum(raw) / n)
        for i in range(n):
            while True:
                name = f"{rng.choice(PREFIXES)} {rng.choice(SUFFIXES[client_id])}"
                if name not in used_names:
                    used_names.add(name)
                    break
            arch = _weighted(rng, ARCHETYPES)
            arr = int(round(raw[i] * scale, -3))
            seat_unit = 2500 if client_id == "lumora" else 6000
            seats = max(20, int(arr / seat_unit))
            util = {
                "healthy": rng.uniform(0.62, 0.84),
                "escalation_hit": rng.uniform(0.55, 0.80),
                "low_adoption": rng.uniform(0.22, 0.45),
                "unhappy_voice": rng.uniform(0.50, 0.75),
                "drifting": rng.uniform(0.40, 0.62),
                "expansion_ready": rng.uniform(0.86, 0.98),
            }[arch]
            n_mod = len(c["modules"])
            breadth = {
                "low_adoption": rng.randint(1, 2),
                "expansion_ready": n_mod,
                "drifting": rng.randint(2, 4),
            }.get(arch, rng.randint(3, n_mod))
            addons_licensed = rng.sample(c["addons"], rng.choice([0, 0, 1, 1, 2]))
            accounts.append({
                "id": f"{client_id[:2].upper()}-{i + 1:03d}",
                "client": client_id,
                "name": name,
                "segment": rng.choice(c["segments"]),
                "region": rng.choice(REGIONS),
                "archetype": arch,  # ground truth label, kept for model evaluation only
                "arr": arr,
                "seats_licensed": seats,
                "seats_active": int(seats * util),
                "modules_licensed": list(c["modules"]),
                "modules_used": rng.sample(c["modules"], breadth),
                "addons_licensed": addons_licensed,
                "ticket_weight": (arr ** 0.7) * rng.uniform(0.7, 1.3),
            })
    return accounts


def build_telemetry(accounts, rng):
    tele = {}
    for a in accounts:
        arch = a["archetype"]
        trend = {
            "healthy": rng.uniform(-0.05, 0.10),
            "escalation_hit": rng.uniform(-0.12, 0.02),
            "low_adoption": rng.uniform(-0.15, 0.03),
            "unhappy_voice": rng.uniform(-0.12, 0.0),
            "drifting": rng.uniform(-0.45, -0.20),
            "expansion_ready": rng.uniform(0.05, 0.22),
        }[arch]
        days = {
            "drifting": rng.randint(90, 180),
            "unhappy_voice": rng.randint(40, 110),
        }.get(arch, rng.randint(10, 75))
        champ = rng.random() < (0.55 if arch == "drifting" else 0.06)
        tele[a["id"]] = {
            "usage_trend": round(trend, 3),
            "days_since_exec_touch": days,
            "champion_left": champ,
        }
    return tele


def build_tickets(cfg, accounts, rng):
    months = cfg["months"]
    tickets = []
    tid = 0
    for client_id, c in cfg["clients"].items():
        accs = [a for a in accounts if a["client"] == client_id]
        total_w = sum(a["ticket_weight"] for a in accs)
        surge_uc = c["client_surge_use_case"]
        for mi, month in enumerate(months):
            recent = mi >= len(months) - 3
            last = mi == len(months) - 1
            for a in accs:
                arch = a["archetype"]
                base = c["tickets_per_month"] * a["ticket_weight"] / total_w
                if arch == "drifting":
                    base *= 1.0 - 0.12 * mi  # tickets go quiet as the account drifts away
                if arch == "escalation_hit" and recent:
                    base *= 1.35
                count = max(0, int(round(rng.gauss(base, base * 0.08))))
                unlicensed = [x for x in c["addons"] if x not in a["addons_licensed"]]
                surge_target = unlicensed[0] if unlicensed else None
                for _ in range(count):
                    tid += 1
                    use_case, category = _pick_use_case(rng, c, a, arch, recent, last, surge_uc, surge_target)
                    tickets.append(_make_ticket(rng, tid, client_id, a, month, use_case, category, arch, recent))
    return tickets


def _pick_use_case(rng, c, a, arch, recent, last, surge_uc, surge_target):
    # client-wide surge on one add-on in the most recent month (market event or new release)
    if last and surge_uc not in a["addons_licensed"] and rng.random() < 0.025:
        return surge_uc, "how_to"
    if arch == "expansion_ready" and surge_target and rng.random() < (0.16 if last else 0.04):
        return surge_target, "how_to"
    if rng.random() < 0.02:
        return rng.choice(c["addons"]), "how_to"
    pool = a["modules_used"] if rng.random() < 0.9 else a["modules_licensed"]
    use_case = rng.choice(pool)
    if arch == "escalation_hit" and recent:
        mix = [("how_to", 0.25), ("defect", 0.45), ("outage", 0.12), ("access", 0.08), ("billing", 0.04), ("feature_request", 0.06)]
    else:
        mix = [("how_to", 0.42), ("defect", 0.25), ("outage", 0.03), ("access", 0.15), ("billing", 0.06), ("feature_request", 0.09)]
    return use_case, _weighted(rng, mix)


def _make_ticket(rng, tid, client_id, a, month, use_case, category, arch, recent):
    if category == "outage":
        sev = _weighted(rng, [("S1", 0.5), ("S2", 0.5)])
    elif category == "defect":
        sev = _weighted(rng, [("S1", 0.04), ("S2", 0.26), ("S3", 0.5), ("S4", 0.2)])
    else:
        sev = _weighted(rng, [("S3", 0.55), ("S4", 0.45)])
    esc_p = {"S1": 0.85, "S2": 0.35, "S3": 0.06, "S4": 0.01}[sev]
    if arch == "escalation_hit" and recent:
        esc_p = min(1.0, esc_p * 1.6)
    escalated = rng.random() < esc_p
    reopen_p = 0.22 if (arch == "escalation_hit" and recent) else 0.06
    reopened = category in ("defect", "outage") and rng.random() < reopen_p * 2

    unhappy = arch == "unhappy_voice" or (arch == "escalation_hit" and recent)
    tone = _weighted(rng, [("positive", 0.10), ("neutral", 0.45), ("negative", 0.38), ("churn", 0.07)] if unhappy
                     else [("positive", 0.35), ("neutral", 0.55), ("negative", 0.10), ("churn", 0.0)])
    if arch == "drifting" and recent and rng.random() < 0.05:
        tone = "churn"
    csat = None
    if rng.random() < 0.35:  # survey response rate
        mean = {"positive": 4.8, "neutral": 4.3, "negative": 2.6, "churn": 1.8}[tone]
        csat = int(_clip(round(rng.gauss(mean, 0.6)), 1, 5))
    return {
        "ticket_id": f"T{tid:06d}",
        "client": client_id,
        "account_id": a["id"],
        "month": month,
        "use_case": use_case,
        "category": category,
        "severity": sev,
        "escalated": escalated,
        "reopened": reopened,
        "csat": csat,
        "text": rng.choice(TEXT[tone]),
    }


def generate(cfg):
    rng = random.Random(cfg.get("seed", 42))
    accounts = build_accounts(cfg, rng)
    telemetry = build_telemetry(accounts, rng)
    tickets = build_tickets(cfg, accounts, rng)
    for a in accounts:
        a.pop("ticket_weight")
    return accounts, telemetry, tickets
