# Enterprise structure and usage (Phase 1)

Built 2026-09-20. Status: approved by the project owner on 2026-09-20 (six archetypes, org shapes as proposed, four calculators, 36-month horizon). Nothing here is built into a model yet.

How to read: IDs (ORG-06, BUY-03, ...) point to `evidence/benchmarks.md`, where each claim has its source, date and grade. **(D)** marks a design proposal of ours. It is not evidence. The proposals were approved by the project owner on 2026-09-20. A\*/B\* means the original was not opened.

## 1. What the evidence supports, and what is design

- **Evidence supports:** AI ownership splits by function (governance central, delivery distributed), funding comes from both central IT and business-unit budgets, buying models are diverse and often hybrid, "adoption" is a definition before it is a number, and cost governance sits mostly in technology, not finance.
- **Evidence does not supply:** who pays shared platform costs under each org shape, any per-team usage numbers, an enterprise seat-activation ramp, or a measured heavy-user distribution (gaps G1 to G4, G10).
- **So the design rule is:** the tool ships templates that decide which fields matter and which cost layers dominate for a kind of team. It ships no default usage numbers, and every number an enterprise enters is theirs.

## 2. Org models and who pays

### What the evidence says

- **Governance is centralized, delivery is distributed.** Fully centralized: risk and compliance 57%, data governance 46%, AI strategy 36%, tech talent 29%, adoption 23%. Talent and adoption are most often hybrid (ORG-06, B\*).
- **Maturity path.** Start with a central center of excellence, then move to an advisory model where platform teams embed governance and frontline teams own delivery. Signals to move: approval delays, knowledge bottlenecks (ORG-04, A).
- **Funding is mixed.** AI is funded from "centralized IT and business unit budgets", and the innovation-budget share fell from 25% to 7% (BUD-02, B).
- **Cost governance lives in technology.** 78% of FinOps teams report to the CTO or CIO, 8% to the CFO, and 98% now manage AI spend (ORG-07, B; respondents are FinOps practitioners, so self-selected).
- **Allocation methods.** Proportional, fixed, even split, or explicitly central (ORG-01, A). Showback reports costs to teams; chargeback moves them to each P&L owner's books and needs a cost-center hierarchy and general-ledger support. The lowest maturity level is manual and spreadsheet-based (ORG-08, A).
- **Attribution is hard.** The same model serves many interfaces, so the consumer of an output is hard to identify (ORG-02, A).

### Proposed org shapes, defined by who owns which cost (D)

| Shape | Platform, data and governance cost | Use-case build and run cost | Default shared-cost rule | Cost effect beyond allocation |
|---|---|---|---|---|
| Centralized | Hub | Mostly hub; business units consume | Central budget, showback only | Hub team is the largest fixed cost; bottleneck risk |
| Federated | Each business unit | Each business unit | Nothing shared | Platform and data-readiness work is duplicated per business unit |
| Hub-and-spoke | Hub (platform, standards, shared data, governance) | Spokes | Usage-proportional, or headcount proxy where usage is unmetered | Both a hub team and spoke teams are paid |

- The shape changes **what is bought and how often**, not just who is billed. The switch must therefore change duplication and hub-team lines, not only an allocation column.
- Shapes are a path, not a fixed choice. The tool takes "current shape", "target shape" and "month of transition" (D).
- No primary source says which shared-cost rule fits which shape (G4). The defaults above are assumptions (D), which the enterprise overrides.

**The tool asks:** current and target shape, business units and cost centers, who funds the platform, the allocation rule, and showback or chargeback. **It defaults:** the allocation rule per shape (D). Hub-team size has no benchmark, so it is an enterprise input. The only staffing benchmark found covers cost-governance teams alone: 8 to 10 practitioners and 3 to 10 contractors where $100M+ of cloud spend is managed (ORG-07).

## 3. Team archetypes (D)

Defined by **cost shape**, not department, because department names do not predict what drives cost. Evidence that use is broad: IT, marketing and sales, and knowledge management lead reported function-level use (ADO-05, B\*); spending splits into departmental tools such as coding, horizontal copilots and vertical solutions (BUD-03, B); and more than 90% of surveyed CIOs were testing third-party customer-support applications (a16z, S14).

| Archetype | Unit of outcome | Usual buying model | Layer that dominates | Heavy-tail risk | Watch for |
|---|---|---|---|---|---|
| A1 Knowledge-worker assistant | Active user per month | Seat | Licences, change and training | Low: a flat seat caps it | Paying for licensed but inactive seats |
| A2 Developer productivity and agents | Developer per month, or task | Seat plus usage allowance | Inference | Very high: agent loops multiply tokens | Overage; seat allowances that hide the tail |
| A3 High-volume service operations | Resolved conversation or ticket | Outcome-based or per-unit API | Inference plus human fallback | Volume spikes | Vendor definition of "resolved"; escalation cost |
| A4 Regulated document and decision work | Document or case processed | Cloud-managed API, regional endpoints | Data readiness, review, governance | Long documents | Data-residency premiums; 100% human review |
| A5 Embedded product feature | End-user transaction | API or committed capacity | Inference and capacity | Customer growth, not headcount | Gross margin; utilization of committed capacity |
| A6 Data and analytics assistant (added at approval) | Query or analysis completed | Seat or per-unit API | Data readiness (semantic layer, permissions) and review | Ad hoc large queries and agentic analysis | Access controls on the data; validating answers before they are used |

- Each archetype is a **template**: it picks a default buying model and unit of outcome and highlights the dominant layers. It carries **no default numbers**. Evidence exists for none of them (G2, G3).
- Enterprises define their own teams. Archetypes are starting points, and a team can mix two.

## 4. Users: licensed, active, and the heavy tail

- **Adoption is three parameters, not a percentage:** the denominator (licensed seats or total staff), the window (day, week, four weeks, period) and the activity threshold (ADO-01, ADO-03, A).
- **Population priors, not enterprise numbers.** 50% of US employed adults use AI at work at least a few times a year, 28% a few times a week, 13% daily (ADO-04, B). The share who ever use AI rose from 21% in Q2 2023 to 46% in Q4 2025 and 50% in Q1 2026, about 2.6 points a quarter on average (ADO-08, B\*; derived). This is a workforce trend, not seat activation inside one company.
- **Enterprise ramp: no benchmark (G10).** The tool takes start month, months to plateau and plateau share as inputs, with linear and S-shaped curves as selectable shapes (D).
- **Seat waste is arithmetic.** Effective price per active user = seat price divided by the active share of licensed users (illustrative shares, D):

  | Seat price (per user per month) | 100% active | 50% active | 25% active |
  |---|---|---|---|
  | $18 (BUY-02, promotional) | $18 | $36 | $72 |
  | $30 (BUY-02) | $30 | $60 | $120 |

- **Segments by intensity.** Use two segments, the top 10% of users and everyone else, each with its own intensity (D). A measured distribution does not exist (G2), and the consultancy claim that under 10% of users drive most of the bill is grade C (HVY-01). Existing usage-level definitions (ADO-02) show how a vendor segments users.
- **Seats cap the tail; usage exposes it.** A premium seat is priced at 5 times a standard seat for "5x more usage" (BUY-02). Usage-priced plans scale with tokens instead.
- **Seat versus usage crossover (illustrative, D).** If an interaction is 2,000 input and 500 output tokens at $2 and $10 per million (PRC-04 snapshot), it costs $0.009. An $18 seat then equals about 2,000 such interactions a month, or about 95 per working day. Real seat products bundle more than model calls, so this is a comparison of shape, not a like-for-like price.
- Joiners, leavers and growth by business unit and month are enterprise inputs.

## 5. Buying models

| Model | How it charges | Utilization risk sits with | Dated examples (2026-09-20 snapshot, BUY-02 to BUY-06) |
|---|---|---|---|
| Seat | Flat per user per month | Buyer, for inactive seats | Microsoft 365 Copilot $30; Claude Team $20 |
| Seat plus usage (hybrid) | Seat plus variable usage or an allowance | Both | Claude Enterprise $20 plus API-rate usage; GitHub Copilot $19 and $39 with allowances |
| Per-unit consumption | Per token, credit or action | Provider | Direct APIs (PRC-01 to PRC-03); Copilot Studio $200 per 25,000 credits; Salesforce Flex Credits $500 per 100,000 |
| Committed capacity | Hourly per unit, used or not | Buyer | Bedrock Provisioned Throughput (none, 1 or 6 months); self-hosted GPUs |
| Outcome-based | Per resolved outcome or conversation | Vendor, subject to its outcome definition | Intercom $0.99 per outcome; Agentforce $2 per conversation |

- Cloud-managed access sits across these rows: partner clouds set their own prices, and regional endpoints carry a 10% premium over global endpoints for Claude 4.5 and later (BUY-05, A).
- **Four calculators cover all of it (D):** seat, seat plus usage, per-unit, and committed capacity (used for provisioned cloud capacity and for self-hosted GPUs, with utilization as an input). Self-hosted stays a simple line in v1 (CST-09).
- **Outcome definitions differ by vendor.** Intercom counts an outcome when a customer confirms resolution, asks for no further help, or a workflow completes. The tool records the vendor's own definition beside every per-outcome price.
- **Outcome pricing is not assumed acceptable.** CIOs say they prefer usage-based pricing (BUY-07, B).
- The price book needs effective dates and a status (standard, promotional, announced) because prices expire and reverse (D8).

## 6. What varies by team: seeds for the input schema (Phase 3)

Each team's profile will carry these fields. Evidence exists that each one changes cost or risk.

- **Buying model and unit of outcome** (section 5).
- **Data sensitivity and residency:** premiums of 1.1x on the Claude API for US-only inference and 10% for OpenAI models released after 2026-03-05, plus regional endpoints (PRC-01, PRC-02, BUY-05).
- **Human review rate:** 27% of respondents review all gen-AI content, and a similar share reviews 20% or less (ORG-06 source, B\*). This drives the people-and-change layer.
- **Model tier and routing:** the small-to-flagship price gap is 10x, 50x or about 2.7x depending on provider (PRC-04).
- **Volume shape:** peak and average, which matters for committed capacity.
- **Data readiness:** sources, effort and refresh cadence. No default (G1).
- **Cost center and business unit:** for allocation (ORG-03).
- **Users:** licensed, active parameters, ramp, and the top-10% segment.

## 7. Decisions (approved 2026-09-20)

1. Archetypes: the five proposed plus a sixth, the data and analytics assistant.
2. Org-shape definitions and default shared-cost rules: approved as proposed (section 2). All are labeled assumptions.
3. Four calculators (seat, seat plus usage, per-unit, committed capacity), with self-hosted as a simple committed-capacity line.
4. Default horizon for amortising one-time costs: 36 months, configurable.

## 8. Gaps carried forward

No A or B source for: shared-cost rules by org shape (G4), per-team usage numbers (G2, G3), enterprise seat activation and ramp (G10), data-readiness cost (G1). ChatGPT plan prices could not be read (blocked), and Gemini Enterprise prices are known only from blogs. Details in `evidence/disagreements-and-gaps.md`.
