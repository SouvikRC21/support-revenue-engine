"""Run the full pipeline: generate (or load) data, build signals, score, route actions, roll up.

    python -m sre.cli                # writes output/ and refreshes dashboard data
    python -m sre.cli --no-dashboard
"""
import argparse
import csv
import json
from pathlib import Path

from . import config, generate, signals, scoring, playbook, revenue

ROOT = config.ROOT
MARK_START = "/*__PORTFOLIO_DATA_START__*/"
MARK_END = "/*__PORTFOLIO_DATA_END__*/"


def run(cfg):
    accounts, telemetry, tickets = generate.generate(cfg)
    sigs = signals.build_signals(cfg, accounts, telemetry, tickets)
    scored, actions = [], []
    for s in sigs:
        res = scoring.score_account(s, cfg)
        scored.append({**s, "result": res})
        a = playbook.churn_action(s, res)
        if a:
            actions.append(a)
        actions.extend(playbook.expansion_actions(s, res))
    actions.sort(key=lambda x: (x["type"] != "churn", x["start_within_days"], -x["value_usd"]))
    summary = revenue.rollup(cfg, scored)
    summary["glide"] = revenue.glide_path(cfg, scored)
    return tickets, scored, actions, summary


def evaluate(scored):
    """How well do the bands line up with the hidden archetypes? A sanity check, not a claim of accuracy."""
    risky = {"escalation_hit", "low_adoption", "unhappy_voice", "drifting"}
    tp = sum(1 for r in scored if r["result"]["band"] != "green" and r["archetype"] in risky)
    fp = sum(1 for r in scored if r["result"]["band"] != "green" and r["archetype"] not in risky)
    fn = sum(1 for r in scored if r["result"]["band"] == "green" and r["archetype"] in risky)
    precision = tp / (tp + fp) if tp + fp else 0
    recall = tp / (tp + fn) if tp + fn else 0
    return {"precision": round(precision, 2), "recall": round(recall, 2), "flagged": tp + fp}


def write_outputs(cfg, tickets, scored, actions, summary, refresh_dashboard=True):
    out = ROOT / "output"
    out.mkdir(exist_ok=True)
    with open(out / "tickets.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(tickets[0].keys()))
        w.writeheader()
        w.writerows(tickets)
    with open(out / "actions.csv", "w", newline="") as fh:
        w = csv.DictWriter(fh, fieldnames=list(actions[0].keys()))
        w.writeheader()
        w.writerows(actions)
    (out / "scored_accounts.json").write_text(json.dumps(scored, indent=1))
    (out / "summary.json").write_text(json.dumps(summary, indent=1))

    if refresh_dashboard:
        portfolio = [{k: v for k, v in r.items() if k != "result"} for r in scored]
        payload = json.dumps({"assumptions": cfg, "accounts": portfolio}, separators=(",", ":"))
        html_path = ROOT / "dashboard" / "index.html"
        html = html_path.read_text()
        a, b = html.index(MARK_START) + len(MARK_START), html.index(MARK_END)
        html_path.write_text(html[:a] + payload + html[b:])


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--config", help="path to an assumptions JSON")
    ap.add_argument("--no-dashboard", action="store_true")
    args = ap.parse_args()
    cfg = config.load(args.config)
    tickets, scored, actions, summary = run(cfg)
    write_outputs(cfg, tickets, scored, actions, summary, not args.no_dashboard)
    t = summary["total"]
    print(f"Tickets processed      {len(tickets):,}")
    print(f"Accounts scored        {t['accounts']}  (red {t['red']}, amber {t['amber']})")
    print(f"ARR under watch        ${t['arr']:,}")
    print(f"ARR at risk (expected) ${t['arr_at_risk']:,}")
    print(f"ARR saveable           ${t['arr_saveable']:,}")
    print(f"Expansion pipeline     ${t['expansion_pipeline']:,}  (weighted ${t['expansion_weighted']:,})")
    print(f"Support cost           ${t['support_cost']:,}")
    print(f"Revenue influenced     ${t['revenue_influenced']:,}  -> {t['multiplier']}x support cost")
    print(f"Programme cost         ${t['program_cost']:,}  -> {t['program_roi']}x return")
    gl = summary["glide"]
    print(f"Day-90 minimum gain    ${gl['day90_minimum']:,}")
    print(f"Year-1 glide path      floor ${gl['year1_floor']:,} / expected ${gl['year1_expected']:,}")
    for q in gl["quarters"]:
        print(f"  Q{q['quarter']}  floor ${q['total_floor']:>9,}  expected ${q['total_expected']:>9,}  "
              f"AHT {q['aht_hours']}h  esc/100 {q['escalations_per_100']}  complaints/mo {q['complaints_per_month']}")
    print(f"Actions queued         {len(actions)}")
    print(f"Band check vs labels   {evaluate(scored)}")


if __name__ == "__main__":
    main()
