# Support Revenue Engine

Product support teams see churn and buying intent before anyone else in the company. This repository turns that into a working system: a pipeline that reads support tickets and product telemetry, predicts which accounts are drifting toward churn and which are ready to buy more, routes each one to an owner and a play, and reports how much revenue support influenced.

It is built around a 100-engineer product support organisation serving two B2B clients and 6,000 tickets a month. Both clients are fictional. **Lumora CX** is modelled on a social media and customer experience SaaS platform (2,000 tickets a month, 60 enterprise accounts). **Streamhaus** is modelled on the B2B side of a streaming media platform (4,000 tickets a month, 40 advertisers and partners). All company names, accounts and tickets are synthetic.

## What it shows

At the default assumptions the model scores 100 accounts carrying $45M of ARR. It finds $8.1M of expected ARR at risk (17 red and 16 amber accounts), $2.5M of it saveable at a 35% save rate, and $2.8M of expansion pipeline. Revenue influenced comes to $3.3M a year, which is 1.1x the $3.0M cost of the whole support org and 13.7x the $240K cost of the six-person revenue pod that runs the process. Every one of those numbers comes from `config/assumptions.json` and changes when you change it.

## Signals

Churn risk is scored from four indicators, each from 0 (healthy) to 1 (severe).

| Indicator | Inputs, last 90 days | Weight |
| --- | --- | --- |
| Product escalation | escalations and Sev1s per 100 tickets against a healthy baseline, defect reopen rate | 0.30 |
| Low adoption | active seats against licensed seats, modules used against modules licensed | 0.25 |
| Customer voice | ticket comment sentiment, CSAT, mentions of renewal, contract, competitor or cancel | 0.25 |
| Disengagement | 30-day usage trend, days since last exec touchpoint, champion left | 0.20 |

The weighted score passes through a logistic curve to give a churn probability. Expansion is flagged by **high adoption** (seat use at or above 85%) and by a **query surge** (how-to tickets about an add-on the account does not own reaching 1.8x the previous three-month average). Red accounts are never pitched an upsell.

## Run it

Python 3.10+ with the standard library only. Node is used only for the dashboard parity test.

```bash
python -m sre.cli              # generate data, score, write output/, refresh the dashboard
python -m unittest discover -s tests -t .
```

The run prints a summary and writes `output/tickets.csv` (about 36,000 synthetic tickets), `output/scored_accounts.json`, `output/actions.csv` (the routed action queue) and `output/summary.json`. It also injects the scored portfolio into `dashboard/index.html`, which you can open straight from disk.

To use your own numbers, copy `config/assumptions.json`, edit it, and run `python -m sre.cli --config my.json`.

## Layout

| Path | What it does |
| --- | --- |
| `sre/generate.py` | Synthetic tickets, accounts and telemetry. Swap for connectors to your ticketing tool, product analytics and CRM. |
| `sre/signals.py` | Turns tickets and telemetry into per-account signals, including a transparent sentiment lexicon. |
| `sre/scoring.py` | Churn indicators, churn probability, bands, expansion triggers. |
| `sre/playbook.py` | Maps each flagged account to a play, owner and start-by SLA. |
| `sre/revenue.py` | Rolls up ARR at risk, saveable ARR, pipeline and return on cost. |
| `sre/cli.py` | Runs the pipeline end to end and checks bands against the hidden archetype labels. |
| `dashboard/index.html` | Interactive dashboard. Re-scores live in the browser when assumptions change. |
| `docs/SOP.md` | The operating procedure: roles, RACI, rhythm, plays, KPIs and a 90-day rollout. |
| `tests/` | Unit tests for scoring and a parity test that the dashboard's JavaScript matches the Python engine. |

## Moving to real data

Replace `generate.generate()` with loaders that return the same three structures (accounts, telemetry, tickets). Run in shadow mode for a month, then calibrate weights and thresholds monthly against actual renewals. After two quarters of outcomes, fit the weights with a logistic regression and drop them into the assumptions file.

## Licence

MIT
