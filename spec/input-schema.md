# Input schema (v1)

Built 2026-09-20. Status: draft for approval. Companion to `requirements-spec.md`.

Every input has: value, unit, **label** (measured, quoted, assumed or benchmark), source, date, grade (A, B, C, D) and, where relevant, owner. "Default" says where an initial value comes from: P = dated primary price (A), R = range with warning, S = starter value (D, see `starter-values.md`), E = enterprise must enter. Low, base and high values exist for every input that feeds a scenario.

## 1. Organization (one row)

| Field | Unit | Default | Note |
|---|---|---|---|
| Organization name | text | E | Fictional in the worked example |
| Currency, horizon | USD; months | USD; 36 (approved) | One-time costs amortised over the horizon |
| Org shape now, target, transition month | centralized, federated or hub-and-spoke; month | E | Shapes are defined by who owns which cost (Phase 1, section 2) |
| Allocation rule | usage-proportional, headcount proxy, even split, central budget | By shape (D) | Centralized: central budget. Federated: none shared. Hub-and-spoke: usage-proportional |
| Reporting mode | showback or chargeback | showback | Chargeback needs a cost-center hierarchy (ORG-08) |
| Business units | name, cost center | E | Keys for allocation (ORG-03) |

## 2. Teams (one row per use case)

| Field | Unit | Default | Note |
|---|---|---|---|
| Name, business unit, cost center | text | E | |
| Archetype | one of six | E | Sets the defaults below (Phase 1, section 3) |
| Unit of outcome | text, plus the vendor's own definition if bought | Archetype | Outcome definitions differ by vendor (BUY-06) |
| Buying model | seat, seat plus usage, per-unit, committed capacity | Archetype | Picks the calculator |
| Data sensitivity and residency | none, regional, US-only, and similar | E | Triggers the premium in CL-23 |
| Model tier mix | share of traffic per tier | E | Routing lever |

## 3. Users (per team)

| Field | Unit | Default | Note |
|---|---|---|---|
| Licensed users, by month | count | E | Joiners and leavers are month-by-month inputs |
| Adoption denominator | licensed seats or total staff | E | ADO-03 |
| Adoption window and threshold | day, week, four weeks, period; at least one action | E | ADO-01 |
| Ramp | start month, months to plateau, plateau share, curve (linear or S) | E; curve S | No benchmark (G10) |
| Top-10% segment | share of users (10%), intensity multiple | S | Model separately; no measured distribution (G2) |

## 4. Usage (per team)

| Field | Unit | Default | Note |
|---|---|---|---|
| Outcomes per active user per month, or direct monthly volume | count | E | Service operations use direct volume |
| Tokens per outcome: input, output, cached share | tokens; share | E | Derived, and labeled derived (G3) |
| Retry and failure multiplier; agent steps per outcome | multiplier; count | S | G8 |
| Human review: share of outputs, minutes each | share; minutes | S by archetype | ORG-06 (B\*) |
| Tool, retrieval, guardrail, voice and image volumes | calls, text units, minutes, images | E | Priced from the price book |
| Asynchronous share (batch eligible) | share | E | Batch lever |

## 5. Data readiness (per team or shared)

| Field | Unit | Default | Note |
|---|---|---|---|
| Source systems | count | E | CL-01, CL-03, CL-04 |
| Documents and pages | count | E | CL-02, CL-05, CL-06 |
| Change rate per month | share | S | CL-08 |

## 6. Cost lines (35 rows)

One row per CL line: quantity, unit, rate, type (one-time, recurring, variable), owner (H, S or H+S) overridable, policy (P, R, S or E), evidence IDs. Effort lines are quantity times the loaded rate. Loaded rates are entered per role, with a starter of $800 per person-day and a BLS cross-check (LAB-02).

## 7. Price book (dated)

| Field | Note |
|---|---|
| Provider, product, tier | e.g. model, seat plan, credit pack |
| Input, output, cache read, cache write (5 minute, 1 hour), batch factor | Per million tokens, or per unit |
| Regional or residency multiplier | PRC-01, PRC-02, BUY-05 |
| Effective from, effective to, status | standard, promotional or announced (D8) |
| Source URL, date fetched, grade | A for provider pages |

Refresh procedure (written in Phase 6): fetch from each provider's own page, record the date, keep old rows with their effective-to date, never overwrite.

## 8. Value (per team)

| Field | Unit | Default | Note |
|---|---|---|---|
| Benefit basis | minutes saved per outcome, or direct currency per outcome | E | |
| Loaded hourly rate of the time saved | currency per hour | $46.89 (A: LAB-01, private-industry average, June 2026) | Enterprise overrides per team |
| Realisation share of time saved | share | S: 25% / 50% / 75% | No evidence converts self-reported time saved to cash (G5). A kill-number candidate |
| Quality or acceptance rate | share | E | Failed outputs earn no benefit |

## 9. Scenarios and sensitivity

- Low-cost, base and high-cost values for every input that has a range (the starter table gives them).
- One-at-a-time swing on net value for each such input, ranked; the top 3 are reported.
- Break-even threshold for each key input (realisation share, active share, cost per outcome, tokens per outcome, review minutes). The one with the smallest margin of safety is the kill number.

## 10. Workbook layout

README and version stamp; Org; Teams; Users; Usage; Lines; Levers; PriceBook; Value; Scenarios; Summary; Allocation (with CSV-ready table); Evidence (assumptions register, evidence shares); Tests.
