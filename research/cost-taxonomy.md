# Cost taxonomy (Phase 2)

Built 2026-09-20. Status: approved by the project owner on 2026-09-20 (35 lines, lever order, and labeled starter values for effort lines). Nothing here is built into a model yet.

How to read: IDs (COMP-01, BUY-03, ...) point to `evidence/benchmarks.md`. **(D)** marks a design proposal of ours. A\* means the original was not opened. This builds on the approved Phase 1 decisions: six team archetypes, three org shapes, four calculators (seat, seat plus usage, per-unit, committed capacity), and a 36-month horizon.

## 1. Rules (D)

- **Type.** Every line is one-time (amortised straight-line over the horizon, 36 months by default), recurring fixed (per month) or variable (units times price).
- **Owner.** Each line gets a typical owner under hub-and-spoke: H (hub), S (spoke or team) or H+S. Centralized moves S lines to the hub. Federated moves H lines to every business unit and duplicates them (approved in Phase 1).
- **Default policy.** Each line has exactly one:
  - **P** = default from a dated primary price (grade A).
  - **R** = a range shown with a warning (grade B\* or C).
  - **E** = enterprise-entered, because no benchmark exists. Each E line ships with a labeled starter value (grade D, approved at Phase 2), marked "starter" until the enterprise confirms or replaces it. Starter values and their rationale are set in Phase 3 (`spec/starter-values.md`).
- **Effort lines** are quantity times a loaded rate. The enterprise enters both. BLS figures are only a cross-check (LAB-01, LAB-02).
- **Reporting.** Each layer is reported in currency with its denominator stated (disagreement D4).

## 2. The lines

Evidence column: benchmark IDs. "none" means no A or B source exists (gap in brackets).

### L1 Data readiness

| ID | Line | Type | Driver | Owner | Evidence | Policy |
|---|---|---|---|---|---|---|
| CL-01 | Source inventory and assessment | One-time | Sources x person-days x rate | H+S | none (G1) | E |
| CL-02 | Cleaning, deduplication, labelling | One-time, then refresh | Volume x effort per unit x rate | S | CST-07 (C, sources conflict), CST-08 | E |
| CL-03 | Connectors to source systems | One-time plus upkeep | Systems x build effort; upkeep as a share of build | H+S | none (G1) | E |
| CL-04 | Permission and access mapping | One-time, then on org change | Sources x groups; change rate | H | ORG-03 | E |
| CL-05 | Document parsing and OCR | Variable | Pages x price per page | S | COMP-01 | P |
| CL-06 | Embeddings | Variable; re-run when the embedding model changes | Tokens x price | S | COMP-02 | P |
| CL-07 | Index and retrieval infrastructure | Recurring fixed plus variable | Plan minimum + GB x price + read and write units | H+S | COMP-03 | P |
| CL-08 | Refresh and sync | Recurring | Change rate x (CL-05 + CL-06) | S | none for change rates | E |

### L2 Setup and infrastructure

| ID | Line | Type | Driver | Owner | Evidence | Policy |
|---|---|---|---|---|---|---|
| CL-09 | Platform or gateway, build or buy | One-time plus recurring | Enterprise-entered | H | ENV-01 envelope only (G11) | E |
| CL-10 | Workflow and application integration | One-time | Per use case: effort x rate | S | none (G11) | E |
| CL-11 | Security, privacy and legal review | One-time, and on material change | Reviews x effort | H | none (G11) | E |
| CL-12 | Evaluation harness and test sets | One-time, and per model change | Cases x effort | H+S | none (G11) | E |
| CL-13 | Red-teaming and adversarial testing | One-time, then periodic | Effort or vendor fee | H | none (G11) | E |
| CL-14 | Environments and base cloud infrastructure | Recurring fixed | Enterprise-entered | H | none | E |
| CL-15 | Committed capacity (provisioned cloud or self-hosted GPUs) | Recurring fixed | Hourly price x hours, commitment term | H or S | BUY-05, CST-09 (C). Per-unit prices are quoted by the vendor | E |

### L3 Inference and usage

| ID | Line | Type | Driver | Owner | Evidence | Policy |
|---|---|---|---|---|---|---|
| CL-16 | Model tokens | Variable | Outcomes x (input, output, cached, cache-write tokens) x price | S | PRC-01 to PRC-04 | P |
| CL-17 | Retries, failed calls, agent steps | Variable | Multiplier on CL-16 | S | none for rates (G8) | E |
| CL-18 | Tool and retrieval calls | Variable | Calls x price | S | COMP-03, COMP-04 | P |
| CL-19 | Guardrails and moderation | Variable | Text units x price | H+S | COMP-05, COMP-02 | P |
| CL-20 | Voice and image | Variable | Minutes, characters, images x price | S | COMP-04 | P |
| CL-21 | Seats | Recurring fixed | Licensed seats x price | S | BUY-02, BUY-03 | P |
| CL-22 | Credits and outcomes | Variable | Units x price, with the vendor's own definition recorded | S | BUY-04, BUY-06 | P |
| CL-23 | Residency and regional premium | Multiplier | 1.1x (Claude API), +10% (OpenAI, partner regional endpoints) | S | PRC-01, PRC-02, BUY-05 | P |

### L4 Run and maintenance

| ID | Line | Type | Driver | Owner | Evidence | Policy |
|---|---|---|---|---|---|---|
| CL-24 | Monitoring and observability | Recurring fixed plus variable | Plan + units x overage; or self-host | H | COMP-06 | P |
| CL-25 | Ongoing evaluation and quality review | Recurring | Cases a month x effort | H+S | none | E |
| CL-26 | Model migration events | Recurring event | Workflows to re-evaluate x effort; every 12 to 25 months per model, with a window as short as 60 days | S (H if shared) | PRC-06 (cadence, one provider); effort G12 | R |
| CL-27 | Prompt and workflow maintenance | Recurring | Workflows x maintenance effort | S | none | E |
| CL-28 | Support and incident response | Recurring | Users x ticket rate x effort | H+S | none | E |
| CL-29 | Platform team | Recurring fixed | FTE x loaded rate | H | LAB-01, LAB-02 (cross-check) | E |
| CL-30 | Cost governance (FinOps) | Recurring fixed | FTE x loaded rate | H | ORG-07: 8 to 10 practitioners plus 3 to 10 contractors at $100M+ of cloud spend (B) | R |
| CL-31 | Compliance audit and governance | Recurring | Enterprise-entered | H | none (G7) | E |
| CL-32 | Platform and vendor licences | Recurring fixed | Quoted | H | none | E |

### L5 People and change

| ID | Line | Type | Driver | Owner | Evidence | Policy |
|---|---|---|---|---|---|---|
| CL-33 | Training and enablement | One-time, plus new joiners | Headcount x hours x rate | S (H builds the material) | none | E |
| CL-34 | Human review of output | Variable | Outputs x review rate x minutes x rate | S | ORG-06 (review rate, B\*), LAB-01 | R |
| CL-35 | Change management and champions | Recurring | Effort | H+S | none | E |

**Tally:** 35 lines. 11 can default from dated primary prices (P), 3 show a range (R), and 21 are enterprise-entered (E). The tool's value on most lines is the structure and the questions it asks, not defaults, and it should say so plainly.

## 3. Levers, applied in a fixed order (D)

Levers change tokens per outcome or price per token. They are modelled from mechanics, never as flat percentages of the bill (D10), and they compound, so the order matters.

| Order | Lever | Mechanics (A) | Quoted ranges (C) | Acts on |
|---|---|---|---|---|
| 1 | Context management and token optimization | Fewer tokens per outcome | 20 to 60% (CST-11) | CL-16 |
| 2 | Model routing | Share of traffic per tier x tier price; small-to-flagship input ratio 10x, 50x or about 2.7x by provider (PRC-04) | 40 to 70%, and 60 to 90% (CST-06, CST-11) | CL-16 |
| 3 | Prompt caching | Effective input price = list x [(1 - c) + c x read multiplier], c = cached share of input; write premium 1.25x (5 minutes) or 2x (1 hour) (PRC-01 to PRC-03) | 80 to 90% of the cached portion (CST-11) | CL-16 |
| 4 | Batch for the asynchronous share | 50% off (PRC-01 to PRC-03) | none | CL-16 |
| 5 | Residency premium | Multiplier last (PRC-01, PRC-02) | none | CL-16 |
| 6 | Utilization of committed capacity | Hourly cost spread over the units actually used (BUY-05, CST-09) | none | CL-15 |

## 4. Sanity envelopes (used in Phase 5, never as defaults)

- **Seat products:** $228 to $468 per user per year at list, and $1,200 for a premium seat (ENV-02).
- **Gartner, 2024 vintage (B\*):** API-based coding assistant $100,000 to $200,000 initial plus up to $550 per user per year; fine-tuned or custom models $5 million to $20 million plus $8,000 to $21,000 per user per year (ENV-01).
- **How they are used:** a modelled team on seats should land near the seat envelope. A team on API pricing far above about $550 per user per year should send us to the heavy tail and agent-step assumptions first.
- **Illustrative, why the people layer matters (D):** reviewing one output for 3 minutes at $46.89 an hour (LAB-01, all private-industry workers) costs $2.34. One interaction of 2,000 input and 500 output tokens at $2 and $10 per million costs $0.009. The review costs about 260 times more. Where review is near 100%, the people layer dominates. The minutes and token counts are assumptions.

## 5. What the tool asks and what it defaults

- **Defaults:** the 11 P lines, from a dated price book. Levers use provider mechanics.
- **Starts with:** a labeled starter value (D) on every E and R effort line, so the model runs on day one. The tool asks the enterprise to confirm or replace each one, and every output shows the share of total cost that still rests on starter values.
- **Asks:** quantities and rates for every effort line, the cost-center owner of each line, and a loaded rate per role. BLS figures appear only as a cross-check beside the enterprise's own rate.
- **Warns:** every R line shows its range and grade, and the migration cadence names its single provider.

## 6. Decisions (approved 2026-09-20)

1. The five layers and 35 lines, as drafted.
2. The fixed lever order and the rule that levers are never summed as percentages, as drafted.
3. Changed at approval: effort lines are not left blank. They carry labeled starter values (grade D), and the tool shows the share of cost resting on them.

## 7. Gaps carried into Phase 3

No A or B source for setup and governance effort (G11), data-readiness effort (G1), migration effort (G12), run-staffing (G7), retry and agent-step rates (G8), or committed-capacity prices (quoted by vendors). Details in `evidence/disagreements-and-gaps.md`. The value side (benefit per outcome, realisation haircut, payback) belongs to the Phase 3 spec.
