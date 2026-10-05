# Ownership and cadence

Built 2026-09-20. IDs (ORG-04, ORG-10) point to `evidence/`. **(D)** marks our judgement, not evidence. Nothing here has been tried in a real organization.

## Roles

| Role | Owns | Evidence for the role |
|---|---|---|
| **AI program lead** (or a center-of-excellence owner) | The workbook, the org settings, the price-book cadence, the gate rule below | An AI center of excellence measures and reports outcomes, sets standards, and runs intake and prioritization (ORG-04) |
| **Finance or FinOps partner** | The allocation rule, the cost-center keys, the Allocation table, sign-off before a gate | Finance and FinOps are named personas of estimating (ORG-10). 78% of FinOps teams report to the CTO or CIO and only 8% to the CFO, so finance has to be brought in on purpose (ORG-07, B; self-selected respondents) |
| **Team product owners** | Their team's column on Teams: users, usage, buying model, benefit basis | Product is a named persona of estimating (ORG-10) |
| **Platform or hub team** | Hub cost inputs on Params: platform team size, monitoring, permission mapping | The hub owns platform, standards and shared data under the hub-and-spoke shape (research/enterprise-structure.md, D) |
| **Security and data owners** | Sign-off on residency and sensitivity inputs before real data is entered; the data-readiness effort lines | Risk and compliance is the function most often fully centralized, at 57% (ORG-06, B\*) |
| **Sponsor** | The decision at the gate | |

## Who owns the workbook under each org shape (D)

| Shape | Owner | Team inputs | Watch for |
|---|---|---|---|
| Centralized | The hub owns the workbook and most inputs | Hub staff, with team input | A bottleneck if every team waits on the hub |
| Federated | Each business unit runs its own copy | Each unit | Divergent price books. Keep one shared price book, or the units will price the same model differently |
| Hub-and-spoke | The hub owns the workbook, org settings and price book | Each spoke owns its team column | Spokes overwriting the hub's starters without recording it |

## Cadence (D)

| When | Who | What |
|---|---|---|
| Before every funding gate | Program lead, finance partner | Refresh prices, replace starters where possible, review the OFF lines and the kill number, run the tests |
| At least quarterly | Price-book owner | Full price refresh (`adoption/price-book-refresh.md`) |
| A model retirement or price notice | Price-book owner | Repoint the affected teams, re-run, record the change |
| Org change (new team, merger, new shape) | Program lead | Update Org and Teams; re-check the allocation rule |
| At go-live and at agreed review points | Finance partner, product owners | Compare the estimate with actual spend against a variance threshold the organization sets, and update the starters (ORG-11) |
| Yearly | Program lead | Review the assumptions register: owners and last-reviewed dates |

## Change control

- Save every version under a dated name (for example `ai-unit-economics-2026-Q4-gate.xlsx`) and keep the previous ones.
- One line per change: date, what changed, and the effect on total cost and net value on Summary.
- The workbook applies no sheet protection. To reduce accidental edits, protect the Calc, Results and Scenarios sheets in your own copy; formulas stay visible and the input sheets stay open.
- Starter values have an owner: whoever replaces one records who, when and the source, in the Evidence sheet.

## Gate rule (D)

Do not take a number to a funding gate until all of these are true:

1. All 12 tests pass.
2. The share of cost resting on starter values is shown, and each starter that carries a material share is either replaced or accepted in writing by the finance partner. The acceptable share is the organization's choice; no source gives one.
3. The OFF lines are reviewed and entered, or explicitly accepted as zero.
4. The kill number has been discussed with the sponsor.
5. The price book was refreshed within the last quarter, and any promotion ending within the horizon has been noted.
6. The finance partner has signed off the change line.

## Maturity path

- **Now: Walk** (ORG-10). A common template, an assumptions register, views for several roles.
- **Toward Run** (ORG-10). Carry one estimate through prioritization, commercial and architecture gates, and connect it to accounting so chargeback can run. This is out of scope for v1.
- **Forecasting loop** (ORG-11). Compare estimate with actual at go-live, and let the variance threshold be your own.

## Adoption measures (D)

Time to a first estimate (target under 30 minutes, untested); share of teams with confirmed inputs; share of cost on starter values, falling over time; age of the price book; number of gate decisions that used a workbook that passed all tests.
