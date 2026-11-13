# Support Revenue Engine: Standard Operating Procedure

Owner: Head of Product Support. Version 1.0, November 2026. The live, editable copy of this SOP is kept as a shared document; this file is the version that ships with the code.

## 1. Purpose and scope

This SOP governs the Support Revenue Engine, a programme run by Cognizant Product Support under the General Manager, Product Support, across a 100-engineer team serving two enterprise client accounts. Support already sees every escalation, every complaint, every frustrated comment and every new question a customer asks. The programme reads those signals every day, predicts which accounts are drifting toward churn and which are ready to buy more, and routes each one to a named owner with a deadline.

The model covers two B2B client accounts. Both names are fictional and stand in for the real support model of each platform.

| Client | Platform model | Accounts covered | Avg account ARR (assumed) | Tickets per month | Engineers |
| --- | --- | --- | --- | --- | --- |
| Lumora CX | Social media and customer experience management SaaS (listening, publishing, care console, AI bots) | 60 enterprise brands | $350K | 2,000 | 35 |
| Streamhaus | Streaming media platform, B2B side (advertisers, telco bundle partners, device makers, content partners) | 40 partners | $600K | 4,000 | 65 |

At these assumptions the portfolio carries $45M of ARR, the support org costs $3.0M a year at a $30K loaded cost per engineer, and the support contracts are worth $3.6M a year. The model predicts $9.6M of expected ARR at risk across 17 red and 10 amber accounts, $2.8M of it saveable, and $2.6M of expansion pipeline. At full run rate, revenue influenced comes to $3.5M a year, 1.17x the cost of the whole support org and 14.6x the $240K cost of the revenue pod. The first 90 days carry a minimum gain of $302K, and the four-quarter glide path in section 6 reaches $1.60M in the floor case and $2.89M expected.

The SOP does not replace Customer Success or Sales. Support finds and evidences the signal; Customer Success and Sales own the commercial conversation. What changes is that support stops handing over tickets and starts handing over revenue cases.

## 2. Roles and RACI

A six-person revenue pod is carved out of the existing 100 engineers. No new headcount is needed. The pod has four support analysts (two per client) and two technical account managers (one per client), and it reports to the Head of Product Support.

| Role | Who | What they do in this SOP |
| --- | --- | --- |
| Head of Product Support | Service delivery leader | Owns the SOP, chairs the weekly revenue review, signs off model changes and reports results to the client and to leadership |
| Support analyst (revenue pod) | 4 engineers from the existing team | Runs the daily scoring, validates flags, writes the evidence pack for each flagged account |
| Technical account manager | 2 senior engineers | Runs adoption clinics and seat expansion briefs, owns the customer conversation on product use |
| Support lead per queue | Existing team leads | Triggers the stability swarm for escalation-led risk and tags tickets correctly at closure |
| Engineering manager (client product team) | Client side | Commits fix dates for defects behind red accounts |
| Customer Success Manager | Client side | Owns re-engagement and the success plan |
| Account Executive | Client side | Owns the commercial outcome of every expansion play and every renewal save |

| Activity | Support analyst | TAM | Support lead | Head of Support | CSM | AE | Eng manager |
| --- | --- | --- | --- | --- | --- | --- | --- |
| Ticket tagging and data quality | A | I | R | I | | | |
| Daily scoring and flag validation | R | C | I | A | | | |
| Stability swarm (escalation) | C | I | R | A | I | I | R |
| Adoption clinic | C | R | I | A | R | I | |
| Closed-loop recovery (voice) | C | C | R | A | R | R | C |
| Re-engagement (disengagement) | C | C | I | A | R | R | |
| Seat expansion brief | R | R | I | A | C | R | |
| Use-case surge brief | R | C | I | A | C | R | |
| Model calibration | R | C | I | A | C | C | |

R is responsible, A is accountable, C is consulted and I is informed.

## 3. Signals, data sources and scoring rules

Every account is scored on five churn indicators and two expansion signals. Each churn indicator runs from 0 (healthy) to 1 (severe), and all inputs come from systems support already has access to.

| Indicator | Inputs (last 90 days) | Source system | Starts to score when | Default weight |
| --- | --- | --- | --- | --- |
| Product escalation | Escalations to engineering per 100 tickets, Sev1 tickets per 100, defect reopen rate | Ticketing tool (JSM, Zendesk or ServiceNow) | More than 9 escalations or 3 Sev1s per 100 tickets, or reopen rate above 12% | 0.25 |
| Complaint surge and handling time | Complaint tickets last month against the previous 3-month average, complaint share of all tickets, growth in average handling time per ticket against the prior quarter | Ticketing tool (category and time-tracking fields) | Complaints at 1.2x their baseline with at least 4 in the month, complaints above 4% of tickets, or handling time up more than 5% | 0.20 |
| Low adoption | Active seats against licensed seats, modules in use against modules licensed | Product analytics | Seat use below 75% or module breadth below 60% | 0.20 |
| Customer voice | Ticket comment sentiment, average CSAT, mentions of renewal, contract, competitor or cancel | Ticketing tool and CSAT survey | Sentiment below 0.2, CSAT below 4.4, any renewal or competitor mention | 0.20 |
| Customer disengagement | 30-day usage trend, days since last executive touchpoint, champion left | Product analytics and CRM | Usage falling, no exec contact for 120 days, champion change | 0.15 |

Complaint surge and handling time is scored separately from escalations because it measures the customer's experience of the service rather than the product. In the model, Streamhaus complaint tickets rise from 118 a month to 240 over three months, a 2x jump, while Lumora CX rises from 67 to 101. At client level, average handling time moves only from about 2.6 to 2.7 hours, which hides the pain. At account level it is stark: the worst accounts went from about 2.3 hours to over 4 hours per ticket, a rise of 65% to 100%. Each extra hour is a customer waiting longer and an engineer hour not spent elsewhere.

| Expansion signal | Rule | What it means |
| --- | --- | --- |
| High adoption of a feature | Seat use at or above 85% of licence | Teams are queuing for access; a seat block is likely |
| Query surge on a use case | How-to tickets on an add-on the account does not own reach 1.8x the previous three-month average, with at least 6 queries in the month | Buying intent is showing in support before it shows in the CRM |

The weighted indicator score passes through a logistic curve, p = 1 / (1 + e^(-12 (score - 0.30))), to give a churn probability for the next renewal. Expected ARR at risk is p times account ARR. Accounts at 40% or above are red, 15% to 40% are amber, and the rest are green. The account's main driver is the indicator that contributes most to its weighted score, and it decides which play the account gets.

Three guard rails apply. A red account is never pitched an expansion until it returns to amber or green. Expansion value is weighted by win rate (30% by default) and by the chance the account stays. Sentiment uses a plain word list so any score can be explained line by line to an account team; an LLM classifier can replace it later without changing anything downstream.

Ticket tagging is the foundation. Every ticket must close with a use case (module or add-on), a category (how-to, defect, outage, access, billing, feature request), a severity and an escalation flag. Support leads audit 20 closed tickets per engineer per month for tagging accuracy, with a target of 95%.

## 4. Operating rhythm

The engine runs every night, an analyst validates every new flag by 11:00 the next morning, and the account has an owner the same day. Outcomes go back into the CRM so the model can be checked against real renewals each month.

```mermaid
flowchart LR
  A[Nightly data pull] --> B[Signals built] --> C[Scored and banded] --> D[Analyst validates by 11:00]
  D --> E[Routed to owner, SLA 2 to 10 days] --> F[Owner runs play] --> G[Outcome in CRM] --> H[Monthly calibration]
  H -. new weights and thresholds .-> C
```

| Cadence | When | What happens | Owner | Output |
| --- | --- | --- | --- | --- |
| Daily | 06:00 | Pipeline pulls the previous day's tickets, product usage and CRM fields, rebuilds signals and re-scores all 100 accounts | Automated | Refreshed dashboard and action queue |
| Daily | By 11:00 | Analyst reviews every account that changed band or newly triggered an expansion signal, reads the underlying tickets and confirms or rejects the flag | Support analyst | Validated flags with a one-page evidence pack |
| Daily | By 17:00 | Confirmed plays are assigned in the CRM with owner and start date | Support analyst | CRM task per play |
| Weekly | Monday, 45 minutes | Revenue review: new red accounts, plays past their start date, expansion briefs sent and their status | Head of Support with CSM and AE leads | Decisions and escalations log |
| Weekly | Thursday | Top recurring defects behind red accounts reviewed with engineering | Support lead and Eng manager | Fix dates committed |
| Monthly | First week | Calibration: compare last month's predictions with renewals, downgrades and expansions; adjust weights and thresholds if precision or recall drop below target | Support analyst, approved by Head of Support | Change note and updated assumptions file |
| Quarterly | QBR | Support-influenced revenue report shared with each client: ARR saved, expansion won, product fixes driven | Head of Support | QBR revenue slide |

## 5. Plays and SLAs

Each flagged account gets exactly one retention play, chosen by its main churn driver, and up to two expansion plays. Red accounts start within 2 working days, amber within 7, and expansion briefs within 10.

| Play | Trigger | Owner | Start within | Steps | Done when |
| --- | --- | --- | --- | --- | --- |
| Stability swarm | Product escalation is the main driver | Support lead with Engineering manager | Red 2 days, amber 7 days | 1. Open a war-room on the top recurring defect. 2. Publish an RCA to the customer within 5 working days. 3. Review fix ETA weekly with the customer until closed. 4. Pre-empt related tickets with a proactive status note. | Escalations per 100 tickets back under 9 for 30 days |
| Service recovery | Complaint surge and handling time is the main driver | Support lead with Queue manager | Red 2 days, amber 7 days | 1. Ring-fence a named pod of engineers for the account. 2. Clear the complaint backlog within 5 working days. 3. Route the account straight to L2 to cut hand-offs. 4. Send the customer a weekly service note with complaint count and handling time. | Complaints back to their 3-month baseline and handling time within 10% of the prior quarter |
| Adoption clinic | Low adoption is the main driver | TAM with CSM | Red 2 days, amber 7 days | 1. Map unused modules and inactive seats. 2. Run two enablement sessions for admins and power users. 3. Switch on in-app guides for the weakest module. 4. Agree a 60-day seat activation target. | Seat use above 75% or the agreed target met |
| Closed-loop recovery | Customer voice is the main driver | Support Director with AE | Red 2 days, amber 7 days | 1. Call the customer sponsor within 48 hours. 2. Take the top three complaints to product triage. 3. Reply in writing on each complaint with a date. 4. Re-survey CSAT after 30 days. | CSAT above 4.4 and no renewal or competitor mentions for 60 days |
| Re-engagement | Disengagement is the main driver | CSM with AE | Red 2 days, amber 7 days | 1. Book an executive QBR within 30 days. 2. Map a new champion if the old one left. 3. Refresh the success plan with two measurable goals. 4. Set a monthly exec touchpoint. | Usage flat or rising for 60 days and a named champion |
| Seat expansion brief | Seat use at or above 85% | TAM, handed to AE | 10 days | 1. Pull seat utilisation and the teams waiting for access. 2. Write a one-page brief with the evidence. 3. Hand to the AE, who proposes a seat block mid-term or at renewal. | AE logs the opportunity in the CRM |
| Use-case surge brief | How-to queries on an unowned add-on at 1.8x baseline or more | Support analyst, handed to AE and Solutions Engineer | 10 days | 1. Group the surge tickets into themes with quotes. 2. Write a brief on what the customer is trying to do. 3. AE and SE offer a scoped demo or a 30-day pilot. | Demo or pilot booked, or the AE records why not |

A client-wide surge (the same add-on surging across many accounts, as the model shows for Conversational AI Bots at Lumora CX and Live Events at Streamhaus) also goes to the client's product marketing team as one brief, since it usually means a release or a market event is driving demand.

Support engineers keep solving the ticket in front of them. The plays run alongside normal ticket work and never delay a fix.

## 6. Minimum gain in 90 days and the four-quarter glide path

The programme commits to a minimum gain of $302K in the first 90 days and $1.60M over four quarters, with an expected case of $534K and $2.89M. The minimum is the number to put in front of a client or a leadership review; the expected case is what the plan is built to deliver.

Gain has three parts. ARR saved is the expected ARR at risk on red and amber accounts, counted only in the quarter each account renews, times the save rate and a coverage ramp. Expansion won is the weighted pipeline, starting in Q2 because briefs begin on day 61. Capacity released is engineer hours freed by lower handling time, valued at the $30K loaded cost. The floor case uses a 20% save rate instead of 35%, a 15% win rate instead of 30%, and half the capacity gain.

| Measure | Baseline | Q1, days 1 to 90 | Q2, days 91 to 180 | Q3, days 181 to 270 | Q4, days 271 to 360 |
| --- | --- | --- | --- | --- | --- |
| Coverage | | Lumora CX pilot, then Streamhaus from day 61 | Both clients, all plays | Steady state | Steady state, weights refit |
| Coverage ramp | | 50% | 80% | 95% | 100% |
| Flagged accounts renewing | | 6 | 6 | 6 | 9 |
| ARR saved, floor / expected | | $282K / $494K | $339K / $594K | $197K / $344K | $394K / $690K |
| Expansion won, floor / expected | | $0 / $0 | $45K / $91K | $77K / $154K | $91K / $181K |
| Capacity released, floor / expected | | $20K / $40K | $40K / $81K | $52K / $105K | $60K / $121K |
| **Quarter gain, floor / expected** | | **$302K / $534K** | **$425K / $765K** | **$326K / $603K** | **$545K / $992K** |
| Cumulative, floor / expected | | $302K / $534K | $727K / $1.30M | $1.05M / $1.90M | $1.60M / $2.89M |
| Escalations per 100 tickets | 9.6 | 8.6 | 7.7 | 7.2 | 6.7 |
| Average handling time per ticket | 2.68 h | 2.55 h | 2.42 h | 2.33 h | 2.28 h |
| Engineer capacity released | | 5.4 FTE | 10.7 FTE | 14.0 FTE | 16.1 FTE |
| Complaint tickets per month | 341 | 290 | 239 | 205 | 188 |
| CSAT | 4.14 | 4.24 | 4.34 | 4.44 | 4.44 |

Q3 is lower than Q2 because fewer of the flagged accounts renew in that quarter, not because the programme slows. The cumulative line rises every quarter. If a quarter falls below its floor, the weekly revenue review treats it as a red item and the Head of Support reports the cause and the recovery plan at the next client QBR.

## 7. Case files

These four case files are drawn from the programme's model portfolio, with anonymised account names. Each shows a signal the engine raised, what the team did, and the outcome the play is measured against. Replace the outcome lines with recorded results as each case closes.

### Case 1: complaint surge and slower handling at a Streamhaus telco bundle partner

Silverline Devices carries $1.97M of ARR and renews in Q1. Complaint tickets rose from 8 a month in July to 21, 37 and then 48 in October, six times the summer level. Average handling time climbed from 2.3 to 4.1 hours per ticket, up 77%, and the account logged 158 escalations and 58 Sev1 tickets in 90 days. CSAT fell to 3.55 and 48 tickets mentioned the renewal, the contract or a competitor. The engine scored the account at 97% churn probability, with product escalation and service strain both above 0.85.

The team ran a stability swarm and a service recovery play together. A ring-fenced pod took every ticket from the account, the top recurring defect got a war-room and a customer-facing RCA within five working days, and the customer received a weekly note with complaint count and handling time. The outcome the play is measured against is complaints back under 15 a month and handling time under 2.6 hours before the renewal date. At a 35% save rate this one account is worth about $670K of ARR protected.

### Case 2: an escalation storm at a Lumora CX telecom brand

Willowmere Telecom carries $491K of ARR and renews in Q2. After a Care Console release, 28 of its 141 tickets in 90 days were escalated to engineering, 12 were Sev1, and half of fixed defects reopened. Complaints went from about 1 a month to 11, and handling time rose from 2.5 to 4.3 hours. The stability swarm put the defect on the client's engineering priority list with a committed fix date, and the support lead reviewed it with the customer every week. The measure is escalations under 9 per 100 tickets for 30 days before renewal.

### Case 3: a quiet complaint trend at a Lumora CX food brand

Oakridge Foods carries $684K of ARR and renews in Q1. Escalations were normal, which is why nobody had noticed. The signal came from voice and complaints: sentiment fell to -0.30, CSAT to 3.3, seven tickets mentioned the renewal, and complaints went from 0 in August to 6 and then 8. The closed-loop recovery play had the Support Director call the sponsor within 48 hours and answer the top three complaints in writing with dates. The measure is CSAT above 4.4 and no renewal mentions for 60 days.

### Case 4: a query surge that became pipeline at a Streamhaus advertiser

Kestrel Cable carries $1.22M of ARR and already uses 91% of its seats. In October it raised 29 how-to tickets about Ad Measurement Plus, an add-on it does not own, against a three-month average of 6. The support analyst grouped the tickets into themes and sent the AE a one-page brief. With seat expansion and the add-on together, the opportunity is worth $427K, about $128K weighted at a 30% win rate. Across Streamhaus, Live Events questions from accounts that do not own it rose more than fourfold in the same month, which went to the client's product marketing team as one brief.

## 8. Handoffs, governance, KPIs and rollout

### Handoff standard

Every handoff to Sales or Customer Success is a CRM task with a one-page evidence pack attached. The pack states the account, the trigger, the three to five tickets that prove it, the customer's own words where they help, the suggested play and the ARR involved. A handoff without evidence is sent back. Support gets credit for revenue influenced only when the AE or CSM logs the outcome against that task, which keeps the numbers honest and auditable.

### Governance

The Head of Product Support owns this SOP and reviews it every quarter. Model changes (weights, thresholds, plays) are proposed by the analysts, logged in a change note with before-and-after precision and recall, and approved by the Head of Support. Customer data stays inside the client's tenant and the support org's approved tooling. Ticket text used for sentiment is never shared outside the account team.

### KPIs

| KPI | Definition | Target after two quarters |
| --- | --- | --- |
| Flag precision | Share of red and amber flags the analyst confirms and the account team agrees with | 80% or more |
| Flag recall | Share of actual churns and downgrades flagged at least 60 days before renewal | 75% or more |
| Play SLA compliance | Plays started within their start-by window | 95% |
| Gross revenue retention | ARR kept from the accounts covered, before expansion | Up 3 points on the prior year |
| ARR saved | ARR on flagged accounts that renewed, as logged by the AE | $2.0M a year across both clients |
| Expansion influenced | Closed-won ARR on opportunities that started from a support brief | $0.8M a year |
| Revenue influenced per support dollar | (ARR saved + expansion influenced) divided by support org cost | 1.0x or more |
| Tagging accuracy | Closed tickets with correct use case, category and severity | 95% |

### Calibration

The default weights and thresholds are starting points. Each month the analysts compare last month's bands with what actually happened at renewal. If precision falls below 80% the thresholds go up; if recall falls below 75% they come down or the weight of the weakest indicator moves. After two quarters there is enough outcome data to fit the weights with a logistic regression.

### 90-day rollout

1. Days 1 to 30, foundation. Agree the ticket tagging standard with both clients, fix tagging gaps, connect the ticketing tool, product analytics and CRM exports, and form the revenue pod. Run the model in shadow mode with no plays.
2. Days 31 to 60, pilot. Turn on retention plays for Lumora CX only. Hold the first weekly revenue reviews and the first monthly calibration. Agree the handoff standard and credit rules with the client's CS and Sales leads.
3. Days 61 to 90, scale. Add Streamhaus and switch on expansion briefs for both clients. Present the first support-influenced revenue report at each client QBR.
4. After day 90, run as business as usual, refit weights after two quarters of outcomes, and propose an outcome-based element in the support contract (for example a share of ARR saved) at the next renewal.
