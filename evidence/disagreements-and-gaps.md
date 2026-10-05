# Where sources disagree, and what none of them answer

Accessed 2026-09-20. IDs refer to benchmarks.md and source-register.md.

## Disagreements, explained through definitions

| # | What conflicts | Why (definitions) | What the tool must do |
|---|---|---|---|
| D1 | Copilot adoption is quoted as "67% daily", "20 to 30% of licensed seats weekly" and "35.8% of employees with access" (all from blog aggregators, S28, grade C). Gallup reports 13% daily, 28% a few times a week, 50% at least a few times a year (ADO-04) | Population: licensed seats in enterprises vs all employed US adults. Window: daily vs weekly vs any active day per period. Numerator: "active" is a setting (ADO-01). Denominator: licensed vs total staff (ADO-03) | Ask for denominator, window and threshold as three explicit parameters. Never store one "adoption %" |
| D2 | Time saved per day: 26 minutes (UK trial, per press), 19 (one department, per press), 40 to 60 (vendor survey), 5.4% of hours among users, 2.2% of all hours (VAL-01 to VAL-05) | Different populations (trial participants, all workers, users only), different denominators (minutes vs percent of hours), all self-reported, two from vendors or press | Benefit per outcome = time saved x loaded cost x a realisation haircut. The haircut is a labeled assumption (D). Show ranges. Never present minutes as savings |
| D3 | Forecast miss rates: 85% miss by more than 10%, 80% by more than 25%, 15% within 10% (FCS-01) vs a blog restatement of "56% miss by 11 to 25%" | The two cannot describe one distribution: if 85% miss by more than 10% and 80% by more than 25%, at most 5% miss by 10 to 25%. Unresolved; the original report was not found | Treat as directional. Use wide scenario bands as our own assumption (D), not a cited figure |
| D4 | Cost mix: "inference is 80 to 90% of spend" (CST-05), Menlo's applications 51% / infrastructure 49% (BUD-03), data preparation 15 to 75% of project cost (CST-07) | Different denominators: AI compute spend, enterprise market spend excluding inference and serving, per-project budget | Report every layer in currency with its denominator stated. Import no share as a default |
| D5 | Self-hosting is "up to 17x" cheaper (CST-09) while 76% of use cases are bought (ADO-06) | Different scenarios: the 17x assumes sustained near-continuous utilization and comes from a hardware seller; the purchase share is a survey of buyers from a sector investor | Make utilization the explicit input for any self-hosted line. Show the crossover, not the multiple |
| D6 | Org names differ: "advisory" (Microsoft), "federated" and "hub-and-spoke" (vendor and blog usage) | Sources define shapes by different attributes and rarely say who pays | Define the three shapes in the tool by who owns platform cost and who owns use-case cost, not by name |
| D7 | Forecast vintage: Gartner's 2026 spending forecast moved from $2.5T to $2.59T to $2.7T in eight months (BUD-04) | Forecasts are revised; a figure without a date is meaningless | Every figure carries its date. Old vintages are kept, not overwritten |
| D8 | Announced prices reverse or expire: Sonnet 5's planned rise was cancelled; Microsoft's seat promotion, Gemini's introductory Flash price and one OpenAI promotion all end on set dates (PRC-01 to PRC-05) | Providers change pricing on schedule and sometimes reverse announcements | The price book carries effective-from, effective-to and a status (standard, promotional, announced) for every price |
| D9 | Output-to-input price ratio: FinOps says output tokens typically cost 3 to 5 times input (CST-11). The price snapshots show 5.0 to 6.25 times at standard context and 3.75 to 4.5 times on long-context tiers (derived from PRC-04) | The FinOps range matches only the long-context tiers; standard-context list prices sit above it | Compute cost from the actual price book. Never apply a rule-of-thumb ratio |
| D10 | Caching savings: 20 to 40% (CST-06) versus 80 to 90% (CST-11) | Different denominators: the first is savings on total spend, the second is savings on the cached portion of input tokens. Both hold if cacheable input is roughly 22 to 50% of the bill (derived: 20/90 to 40/80) | Model caching as cached share of input times the read discount, not as a flat percentage of the bill |

## Gaps: nothing found at grade A or B

| # | Gap | Consequence for the tool |
|---|---|---|
| G1 | Data-readiness cost, as a share of budget or per source system | Data readiness is an explicit layer with enterprise-entered effort. No default share |
| G2 | Measured distribution of usage across users inside an enterprise (heavy tail) | The distribution is an enterprise input, with the top decile modelled separately. Any default is a labeled assumption (D) |
| G3 | Tokens per user per day | Derive it as interactions per day x tokens per interaction, and label it derived |
| G4 | Who pays shared platform costs under each org model | Allocation defaults per org shape are assumptions (D), informed by ORG-01 and BUD-02 |
| G5 | Realised savings, as opposed to self-reported time saved | Value side is scenario-based with a haircut assumption, and says so |
| G6 | Seat prices: partly closed in Phase 1 (Microsoft 365 Copilot, Claude Team and Enterprise, GitHub Copilot; BUY-02, BUY-03). Still missing: ChatGPT plans (blocked) and Gemini Enterprise (blogs only) | The seat option takes the enterprise's quoted price as an input |
| G7 | Run-and-maintenance staffing (people per production AI system) and governance or compliance cost. Only cost-governance team size was found (ORG-07) | Enterprise-entered, labeled assumption |
| G8 | Agentic workloads' token multiple versus chat (only a search snippet, "agents use 5x more tokens", grade C\*) | Steps per outcome is an explicit input; no default multiple |
| G9 | Originals not opened: OpenAI State of Enterprise AI (S23), Gartner releases (S21), McKinsey (S20), the UK trial report PDF (S22), OpenAI Enterprise signals (S24) | Figures from these carry an asterisk or grade C. Open them before they become defaults |
| G10 | Enterprise seat activation and the ramp to a plateau (weeks or months). Only a workforce-level trend exists (ADO-08) | Ramp is an enterprise input with selectable curve shapes (D) |
| G11 | Setup and governance effort: platform or gateway, workflow integration, security and legal review, evaluation harness, red-teaming. Only a two-year-old Gartner envelope exists (ENV-01) | Enterprise-entered effort times the enterprise's loaded rate. The envelope is used only in validation |
| G12 | Effort to migrate a workflow when a model is retired (only the cadence is known, PRC-06) | Effort per workflow is enterprise-entered |

## What this means for Phases 1 to 3

1. Adoption is parameterised: denominator, window, threshold. Not a single percentage.
2. Costs are shown by layer in currency, with each denominator stated. No imported shares.
3. Allocation has four options (usage-proportional, headcount proxy, even split, central budget), and the org switch changes the defaults.
4. The price book has effective dates and a price status, and keeps history.
5. The value side uses a labeled realisation haircut and shows ranges.
6. The top decile of users is modelled separately, because the distribution is unknown and the evidence says it is skewed.
7. Run costs include a model-migration event roughly every one to two years, with a window as short as 60 days.
8. Self-hosted options depend on utilization, so it is an input.
9. Scenario bands are wide by design, since AI cost forecasts are widely missed.
10. Buying models use four calculators (seat, seat plus usage, per-unit, committed capacity), and each vendor's own outcome definition is recorded beside its per-outcome price.
11. The org shape changes duplication and hub-team lines, not just who is billed.
12. Caching and other levers are modelled from mechanics (cached share times discount), never as flat percentages of the bill.

## Sources that would improve the grading

Text or excerpts from these would upgrade several entries from provisional to graded: OpenAI State of Enterprise AI 2025, the Gartner press releases, McKinsey State of AI 2025, and the UK trial findings report. Paste only the method and the specific figures, not the marketing text.
