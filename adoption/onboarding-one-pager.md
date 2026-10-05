# Onboarding: your first estimate

For an enterprise AI program lead and the people who will fill it in. Built 2026-09-20. IDs (ORG-10, PRC-01) point to `evidence/`. **(D)** marks our judgement, not evidence.

## When to use it

Before a funding gate for an AI program, to compare what each team's use case will cost and whether it pays back. In FinOps terms this is Planning & Estimating, and the workbook sits at the **Walk** level: a common template used at a gate, with a shared assumptions register and views for several roles (ORG-10). It does not connect to accounting (that is Run).

## Who needs to be in the room

| Role | Time | Does |
|---|---|---|
| AI program lead (owner) | 30 min | Sets the org shape, scenario and allocation rule on Org |
| One product owner per team | 15 min each | Fills in their team's column on Teams |
| Finance or FinOps partner | 20 min | Agrees the allocation rule and the cost-center keys; reads Summary and Allocation |
| Security or data contact | as needed | Confirms residency and data-sensitivity inputs before real data goes in |

The 30-minute target for a first estimate is a design target (D). It has not been timed with a real team.

## Gather first, per team

- Business unit and cost center; how many people will be licensed; launch month; how fast usage ramps.
- What one outcome is (a resolved ticket, a reviewed document, a merged change) and how many per user per month, or the monthly volume.
- The buying model and its quoted price: seat, seat plus usage, per-unit, or committed capacity.
- For token-billed work: tokens in and out per outcome, and the model tier.
- The share of output a person will review, and the minutes each review takes.
- Data: number of source systems, documents, and any residency or sensitivity limit.
- Benefit: minutes saved per outcome, the hourly cost of that time, and how often the output is accepted.

## The path

1. Open the **README** sheet, then **Org**. Set organization, horizon (up to 60 months), scenario, value case, org shape and allocation rule.
2. On **Teams**, overwrite the example columns. Set **Team is active** to 0 for any column you do not need; a team set to 0 is ignored everywhere. The file holds five teams. For more, edit `model/build/spec_data.py` and rebuild (needs Python and Excel).
3. On **Params**, read every starter value (grade D). Replace those you can with your own numbers. Values you leave stay marked as starters.
4. On **PriceBook**, check each price you use against the provider's page (`adoption/price-book-refresh.md`).
5. Read **Summary**, then **Sensitivity** (the kill number), **Scenarios**, **Allocation** (cost-center table) and **Tests**. All 12 tests should pass.

## Three warnings to read before you quote a number

1. **Share of cost resting on starter values** (Summary). Every point of it is our assumption, not yours.
2. **Lines that are OFF** (Summary). Environments, committed capacity, compliance audit and licences have no starter, so cost is understated until you enter them.
3. **The kill number** (Summary and Sensitivity). It is the input with the smallest margin before net value reaches zero. In the example it is the share of claimed time savings that is realised, an assumption no source can currently ground (G5).

## What to say out loud

- The example organization is fictional. Nothing in it is a forecast for yours.
- Net value is undiscounted, in USD, and before tax.
- Price dates and status are recorded, not applied: the model does not switch prices on a date.
- Published forecast-miss rates are large (FCS-01, grade C). Treat the base case as one point in a range, and the high-cost case as a stress test.
- The value side has no external check. Self-reported time saved is not realised savings.

## After the decision

Set a revisit at go-live, compare the estimate with actual spend against a variance threshold your organization defines, and update the starter values with what you learned (ORG-11).
