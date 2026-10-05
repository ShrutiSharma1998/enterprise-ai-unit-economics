# Requirements spec: enterprise AI unit economics planning tool (v1)

Built 2026-09-20. Status: approved by the project owner on 2026-09-20 (spec and schema as drafted; CL-14 and CL-31 set to zero until entered; thin workbook build approved). This spec, `input-schema.md` and `starter-values.md` are the build contract.
Builds on the approved Phase 1 and Phase 2 decisions and on `evidence/`. IDs point to `evidence/benchmarks.md`.

## Purpose and users

An enterprise runs this before it builds AI. It enters its org structure, teams, users and use cases, and gets cost by layer, by team and for the whole organization, plus break-even and sensitivity.

| User | Needs |
|---|---|
| AI program lead or center of excellence (owner) | Enter org, choose org shape, keep the price book fresh |
| Finance or FinOps partner (auditor) | Trace any output to its inputs, evidence grade and date |
| Team product owner | Enter one team's users, usage and benefit in under 30 minutes |
| Executive | One-page summary and the number that would kill the case |

## What it takes in

Full detail in `input-schema.md`.
- **Organization:** org shape now, target shape, transition month, business units and cost centers, allocation rule, showback or chargeback, horizon (36 months default).
- **Teams:** archetype template (six), buying model (four calculators), users (licensed, active definition, ramp, top-10% segment), usage per outcome, review rate, data sources, benefit per outcome.
- **Cost lines:** the 35 lines. Effort lines start from labeled starter values (D).
- **Price book:** dated prices with effective dates and status.

## What it returns

1. Per team and for the enterprise: total cost over the horizon by layer, monthly run-rate at plateau, cost per outcome, cost per active user per month.
2. Value: benefit per outcome, net value, payback month, break-even volume.
3. Owner view: hub cost vs team cost under the chosen org shape, plus a cost-center table (showback or chargeback), exportable as CSV.
4. Three scenarios (low-cost, base, high-cost), a ranked sensitivity table of the top 3 drivers, and **the one number that would kill the case**: the input whose break-even threshold sits closest to its base value.
5. **Evidence transparency:** the share of total cost resting on primary-price defaults, ranges, starter values (D) and enterprise-entered values, plus the full assumptions register.

## How it calculates

- Five layers, 35 lines (`research/cost-taxonomy.md`). One-time costs are amortised straight-line over the horizon.
- Four calculators: seat, seat plus usage, per-unit, committed capacity.
- Levers in a fixed order: context, routing, caching, batch, residency premium, then capacity utilization. Never summed as percentages.
- Org shape changes owner columns and duplication and hub-team lines, not the variable inference cost.
- Four allocation rules: usage-proportional, headcount proxy, even split, central budget.
- Adoption is three parameters (denominator, window, threshold), never one percentage.

## Evidence rules inside the tool

- Every input carries a label (measured, quoted, assumed or benchmark), a source, a date and a grade.
- Only grade A and B values become defaults. C values appear as ranges with a warning. D values are marked "starter" until the enterprise confirms them.
- The price book has no price without an effective date and a status (standard, promotional, announced).
- Conflicting benchmarks are shown side by side, never averaged.

## Adoptability requirements

- A workbook with visible formulas and no macros (macros commonly trigger security review, D). Runs offline, and no organization data leaves the machine.
- A first estimate in under 30 minutes for someone who knows their teams.
- Version stamp, an assumptions register with an owner and a last-reviewed date per input, and a written price-book refresh procedure.
- The output speaks the FinOps vocabulary: showback, chargeback, cost per workflow completion and per business transaction (CST-10, ORG-08).

## Out of scope for v1

Live billing or FOCUS-format import; automatic price fetching; GPU sizing beyond one committed-capacity line; a web front end; PDF export (the workbook has a print view); any real company data.

## Acceptance tests

The workbook is not done until all pass, and the results sit on a Tests sheet.

1. For each allocation rule and org shape, team allocations sum to the enterprise total.
2. Monthly amortisation of one-time costs sums to the one-time total over the horizon.
3. Lines sum to layers, and layers sum to the total.
4. Zero outcomes gives zero variable cost while fixed costs remain.
5. A hand-calculated lever fixture matches the workbook to the cent.
6. Switching federated to centralized changes duplication and owner lines but not variable inference cost.
7. Every input has a label, source, date and grade, and the evidence shares sum to 100%.
8. No price lacks an effective date and a status.
9. Effective cost per active user equals seat price divided by active share on a fixture.
10. For every layer, low-cost is at most base, which is at most high-cost.
11. Outcome and active-user totals cover only the horizon. (Added in Phase 5, after validation found totals summing all 60 grid months.)
12. Every price ID used by a team or the hub exists exactly once in the PriceBook. (Added in Phase 6: a mistyped ID would otherwise price silently at zero.)

## Decisions (approved 2026-09-20)

1. Spec and schema approved as drafted.
2. Starter values approved, except CL-14 (environments) and CL-31 (compliance audit), which are set to zero until the enterprise enters them. Four lines are now off by default: CL-14, CL-15, CL-31, CL-32.
3. Build the thin workbook next, using a clearly fictional organization for the worked example.
4. (2026-09-21) On the project owner's instruction, a browser calculator is added as a preview (0.2), which reverses the "web front end" exclusion above for that preview. The workbook remains the v1 deliverable. See `prototype-spec.md`.
