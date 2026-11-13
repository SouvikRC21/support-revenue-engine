"""Route every flagged account to a named play, an owner and a deadline.

The plays match section 6 of docs/SOP.md. A signal without an owner and a date is
just a report, so every row here carries both.
"""

CHURN_PLAYS = {
    "escalation": ("Stability swarm", "Support Lead + Engineering Manager",
                   "Open a war-room for the top recurring defect, publish an RCA to the customer within 5 working days, and review fix ETA weekly until closed."),
    "adoption": ("Adoption clinic", "Technical Account Manager + CSM",
                 "Run two enablement sessions on unused modules, switch on in-app guides, and agree a 60-day seat activation target with the customer admin."),
    "voice": ("Closed-loop recovery", "Support Director + Account Executive",
              "Call the customer sponsor within 48 hours, take the top three complaints to product triage, and report back on each in writing."),
    "disengagement": ("Re-engagement", "CSM + Account Executive",
                      "Book an executive QBR within 30 days, map a new champion if the old one left, and refresh the success plan."),
    "service_strain": ("Service recovery", "Support Lead + Queue Manager",
                       "Ring-fence a named pod for the account, clear the complaint backlog within 5 working days, cut hand-offs by routing straight to L2, and send the customer a weekly service note until complaint volume and handling time are back to baseline."),
}
SLA_DAYS = {"red": 2, "amber": 7}


def churn_action(acc, res):
    if res["band"] == "green":
        return None
    play, owner, steps = CHURN_PLAYS[res["primary_driver"]]
    return {
        "account_id": acc["id"], "account": acc["name"], "client": acc["client"], "type": "churn",
        "band": res["band"], "trigger": res["primary_driver"], "play": play, "owner": owner,
        "start_within_days": SLA_DAYS[res["band"]], "arr": acc["arr"], "value_usd": res["arr_at_risk"], "steps": steps,
    }


def expansion_actions(acc, res):
    out = []
    exp = res["expansion"]
    if exp["blocked_by_risk"]:
        return out
    if exp["seat_trigger"]:
        out.append({
            "account_id": acc["id"], "account": acc["name"], "client": acc["client"], "type": "expansion",
            "band": res["band"], "trigger": "high_adoption", "play": "Seat expansion brief", "owner": "TAM -> Account Executive",
            "start_within_days": 10, "arr": acc["arr"], "value_usd": round(acc["arr"] * 0.15),
            "steps": "Share seat utilisation and the teams queueing for access with the AE; AE proposes a seat block at renewal or mid-term.",
        })
    for s in exp["surges"][:1]:
        out.append({
            "account_id": acc["id"], "account": acc["name"], "client": acc["client"], "type": "expansion",
            "band": res["band"], "trigger": "query_surge", "play": f"Use-case surge: {s['use_case']}", "owner": "Support Analyst -> AE + Solutions Engineer",
            "start_within_days": 10, "arr": acc["arr"], "value_usd": round(acc["arr"] * 0.20),
            "steps": f"How-to queries on {s['use_case']} rose {s['ratio']}x against the 3-month baseline. Send the ticket themes to the AE and offer a scoped demo or pilot.",
        })
    return out
