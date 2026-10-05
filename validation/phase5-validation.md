# Phase 5: validation

Built 2026-09-20. Status: complete. Both findings were decided and applied the same day (section 11). Sections 1 to 10 record what validation found on the four-team build; section 11 gives the five-team results after the changes. IDs (ENV-01, S09, G5) point to `evidence/`.

## What "validated" can mean here

No public enterprise case publishes both its inputs and its realised costs (gaps G5 and G11). So the workbook cannot be validated by reproducing a real organization's actuals, and this report does not claim that. What it does:

1. Checks the computation against an independent implementation.
2. Reproduces a provider's own published worked example.
3. Range-checks outputs against published and derived envelopes.
4. Tests the sensitivity shortcuts by changing each driver for real and recalculating.
5. Compares the scenario bands with published forecast-miss data.
6. Tests the tests, by breaking inputs on purpose.

The value side (benefit per outcome, realisation share) has no external check at all.

## 1. Results at a glance

| # | Check | Result |
|---|---|---|
| 1 | Workbook recalculated in Excel vs an independent Python reference model: base build and six variants (shape, rule, scenario, value case, horizon), 34 values each | 0 mismatches |
| 2 | Team totals recomputed by closed form | **Found a bug** (section 2): outcome and active-user totals summed all 60 grid months, not the horizon. Fixed; test 11 added |
| 3 | Anthropic's published worked example (Opus 5, 50,000 input and 15,000 output tokens), reproduced through the lever logic | Exact match: $0.625 and $0.445 token-only (published $0.705 and $0.525 less $0.08 of session runtime) |
| 4 | Envelope checks (section 3) | Seat line inside the seat range; API cost per user about 1.15x Gartner's 2024 ceiling; initial cost inside the range once training is counted separately |
| 5 | Sensitivity shortcuts vs full recalculation (section 4) | Six drivers exact; adoption and volume approximate (7.5% of its swing) |
| 6 | Scenario bands vs published forecast-miss rates (section 5) | High-cost is far wider than published miss rates. Decided: see section 11 |
| 7 | Reproduce a published enterprise case (section 6) | Not possible. One illustration, and a calibration finding on Team 1 |
| 8 | Six deliberate input breakages (section 7) | Each turns exactly its matching test red |

## 2. The bug: totals over the wrong window

**How it was found:** Team 2's outcomes read 7,488,000. By hand, 320 active users x 400 tasks x a 4-month ramp over 36 months is 4,416,000. The 7,488,000 is 128,000 x 58.5, meaning all 60 months of the grid.

**Why the reference model missed it:** the workbook and the reference model were written from the same design, so both had the flaw. This is the limit of check 1: it verifies the implementation, not the design.

**What was wrong and what was not:** the outcome and active-user rows are state rows that the horizon mask does not touch, and their totals summed everything. Costs, benefits, payback, net value and the kill number were unaffected, because those rows are masked. Cost per outcome, benefit per outcome, cost per active user and the usage-proportional allocation shares were affected.

| Metric (base scenario) | Before (wrong) | After |
|---|---|---|
| Outcomes: Team 1 / 2 / 3 / 4 | 6,210,000 / 7,488,000 / 2,260,000 / 705,600 | 3,618,000 / 4,416,000 / 1,300,000 / 403,200 |
| Enterprise cost per outcome | $0.90 | $1.55 |
| Enterprise benefit per outcome | $1.21 | $2.06 |
| Enterprise cost per active user per month (per-user teams) | $99.36 | $170.50 |
| Total cost, benefit, net value, payback | $15.05M, $20.10M, $5.04M, month 12 | unchanged |

The $99.36 figure appeared in an earlier interim report. It was wrong.

**Fix:** totals of the two state rows now use the in-horizon months only. Test 11 checks each team's totals against the sum of its in-horizon months, and a mutation that restores the old formula fails it.

## 3. Envelope checks (base scenario, per licensed user per year)

| Team | Seats | Model tokens, vendor, tools | Human review | Other run and setup | Total incl. hub share |
|---|---|---|---|---|---|
| Corporate knowledge assistant (seat) | $336 | $0 | $47 | $294 | $677 |
| Engineering assistant (seat + usage) | $240 | $630 | $1,726 | $1,669 | $4,265 |
| Customer service agent (per outcome) | n/a | $7,150 | $1,693 | $4,035 | $12,878 |
| Regulated document review (token API) | n/a | $111 | $2,101 | $1,180 | $3,392 |

| Envelope | Comparison | Reading |
|---|---|---|
| Seat list, $228 to $468 a year; premium seat $1,200 (ENV-02, arithmetic on grade A prices) | Team 1's blended seat line is $336: 90% standard at $240 plus 10% premium at $1,200 | Inside the range. This is arithmetic on the same price book, so it checks wiring, not realism |
| Gartner 2024, API-based coding assistant: up to $550 per user per year (ENV-01, B\*) | Team 2's model cost is $630 a year; with the seat, $870 | 1.15x the ceiling on tokens alone, 1.6x with the seat. Same order of magnitude, from heavy assumed usage (400 agentic tasks a month, 6 steps) against 2024 prices. Not a contradiction |
| Gartner 2024, initial cost $100,000 to $200,000 (ENV-01) | Team 2: $205,000 own one-time plus $98,000 hub share = $303,000. Excluding the $128,000 of training: $175,000 | Inside the range if training is counted as a people cost; 1.5x above its top if counted in |
| Gartner 2024, custom-model cost $8,000 to $21,000 per user per year | None of the four teams builds a custom model | Not applicable. Team 3's $12,878 falls in the band by coincidence: its 60 "users" are agents, not what drives cost |
| Human review vs inference (cost-taxonomy section 4) | Team 4: $2,101 review against $111 inference | 19x. Directionally what the taxonomy illustrated, and it depends on the review-minute assumption |

Caveats: Gartner's figures are two years old, from an excerpt (B\*), and from before recent price changes. They were only ever sanity checks.

## 4. Sensitivity shortcuts vs full recalculation

Each driver was changed in the workbook, recalculated by Excel, and compared with the Sensitivity sheet's linear prediction.

| Driver | Change | Predicted net | Recalculated net | Error (share of swing) |
|---|---|---|---|---|
| Realisation share | x1.5 | $15,089,867 | $15,089,867 | 0.0% |
| Minutes saved per outcome | x1.5 | $15,089,867 | $15,089,867 | 0.0% |
| Acceptance rate | x0.8 | $1,022,684 | $1,022,684 | 0.0% |
| Tokens per outcome | x1.5 | $4,642,724 | $4,642,724 | 0.0% |
| Human review minutes | x3.33 | -$3,696,150 | -$3,696,150 | 0.0% |
| Effort (person-day rate) | x2 | -$792,088 | -$792,088 | 0.0% after the fix below |
| Adoption and volume | x0.7 | $764,427 | $1,084,690 | 7.5% |

- **Effort was wrong at first.** The first run was $579,000 (11%) off, because the person-day rate also drives model-migration events and cost governance, which the driver had left out. The driver now covers all person-day-rate-driven lines and is exact.
- **Adoption and volume stays approximate.** With fewer users, support tickets, training and retrieval reads also fall, and the shortcut does not include them. It over-penalises by about 7.5% of that driver's swing at x0.7. The Sensitivity sheet now says so.
- **Consequence for the kill number:** it depends on the realisation share (exact), so it is not affected.

## 5. Scenario bands

| Enterprise, over the horizon | Low-cost | Base | High-cost |
|---|---|---|---|
| Total cost | $8.4M (0.56x) | $15.1M | $51.2M (3.40x) |
| Net value | +$11.7M | +$5.0M | -$31.1M |
| L5 people and change | $1.2M | $5.0M | $25.2M (5.06x) |

- **The high-cost scenario puts every parameter at its high value at once.** That is a stress corner, not a likely outcome, yet the scenario is labeled as if it were a plausible range.
- **Published context (FCS-01, grade C):** 24% of firms miss AI cost forecasts by more than 50%, and 80% miss infrastructure forecasts by more than 25%. The model's band is roughly -44% to +240%, far wider.
- **The largest driver is human review:** L5 is 56% of the high-cost increase. That comes from the review-minute range (1, 3 or 10 minutes) and a doubled review share. Both are grade D.

## 6. Published cases

**Not reproducible end to end.** Checked and why:
- UK Government Digital Service Copilot trial (S22): design read; the time-saved figure is from press; no cost data.
- DWP trial and OpenAI survey: press or search summaries only, no cost data.
- FinOps unit-metric examples (S01): arithmetic illustrations such as $5,000 / 100,000 = $0.05, not enterprise cases.
- Gartner (ENV-01): ranges, not cases.
- Menlo, a16z, Gartner spending: market-level.
- Lenovo TCO (S18): a self-hosted cost comparison, and self-hosting is not modelled in v0.1.
- Intercom and Salesforce (S37, S38): price sheets, no realised cost.

**Illustration only (not validation):** a trial-like design of 20,000 users on a $30 seat over 3 months costs $90 a user. If each user saves 26 minutes over about 63 working days (assumptions: today's list price S35, the press figure C\*, 63 days D), the time is worth about $1,280 at the $46.89 average hourly employer cost (LAB-01). Break-even needs only about 7% of the claimed time to be realised, against the tool's 50% default.

**A calibration finding on Team 1:** the example assumes 5.5 minutes saved per active user per working day (2 minutes on each of 60 interactions a month). Published self-reported figures are 19 to 26 minutes a day (C\*). At 26 minutes a day with the same haircuts, Team 1's benefit is about $198 per active user-month against a cost of about $101. Its negative net value is an artefact of a conservative assumption, not a finding about seat-based assistants.

## 7. Testing the tests

Each mutation was applied to a fresh build, and only its matching test failed (overall: 1 failing).

| Deliberate breakage | Test that failed |
|---|---|
| Outcome total restored to sum all 60 months | 11 |
| Provider example's expected value set to the published total including runtime | 5 |
| A lever fixture's expected value set wrong | 5 |
| A price with no status | 8 |
| An input with no label in the register | 7 |
| A low-cost value above base | 10 |

## 8. Decisions (both decided and applied: see section 11)

1. **High-cost scenario.** Options: keep it and add a plain label ("every parameter at its high value at once: a stress case"), or also narrow the review-minute range so the band is closer to published miss rates.
2. **Team 1's minutes saved.** Options: keep the conservative 2 minutes and label it, or recalibrate to the published range so the worked example is not read as "seats do not pay".

## 9. What remains unvalidated

- Any real enterprise's actuals, and the value side entirely (G5).
- The starter values (grade D), the federated duplication share (G4), and the migration cadence (one provider).
- The reference model shares the authors' understanding of the rules, so it checks the implementation, not the rules. The bug in section 2 is what that limit looks like.
- Recalculation was verified in Windows Excel only.

## 10. Reproduce

```bash
cd model/build
python build.py
python verify.py base <scratch-dir>
python verify.py variants <scratch-dir>
python verify.py mutations <scratch-dir>
python validate.py envelopes
python validate.py bands
python validate.py sensitivity <scratch-dir>
```

## 11. Follow-up: decisions applied (2026-09-20)

**Decisions:** label the high-cost scenario as a stress case and narrow the review-minute range; and keep Team 1 as it is while adding a second, recalibrated seat team.

**What changed**
- **Review minutes** narrowed from 1, 3 and 10 to 2, 3 and 6 (Params sheet and `spec/starter-values.md`). The Sensitivity multipliers follow (0.67 to 2.0).
- **Stress-case label** on Org, Params, Scenarios and Calc_High, and on the Summary whenever High-cost is selected: "every parameter at its high value at once. Not a likely outcome."
- **Team 5 added:** "Sales assistant (published-range calibration)": 2,000 seats and 7 minutes saved per interaction, about 19 minutes per working day, the low published self-reported figure (grade C\*). Team 1 is renamed "(conservative calibration)" and is otherwise unchanged. The example now has five business units.
- **Builder generalised** from four teams to any number. Regression check before adding Team 5: with the same four teams, every figure was identical to the run before the change.

**Results (base scenario, five teams)**

| Enterprise, 36 months | Value |
|---|---|
| Total cost / benefit / net value | $18.34M / $26.03M / $7.69M |
| Payback month | 12 |
| Cost per outcome / benefit per outcome | $1.51 / $2.14 |
| Cost per active user per month (per-user teams) | $140.26 |
| Cost by evidence category | 41% dated prices, 25% ranges, 34% starter values |
| Kill number | Realisation share can fall 30% (from 50% to 35%) before net value reaches zero |

| Team | Net value | Payback |
|---|---|---|
| Team 1, conservative seat assistant | -$3.30M | none |
| Team 5, published-range seat assistant | +$1.98M | month 13 |
| Engineering assistant | +$8.95M | month 3 |
| Customer service agent | +$0.36M | month 14 |
| Regulated document review | -$0.30M | none |

Teams 1 and 5 are the same product at the same price. The only difference is minutes saved (2 against 7 per interaction). That difference alone moves net value by $5.3M, so the example shows that the value assumption, not the seat price, decides whether a seat tool pays.

**The band after narrowing:** high-cost is now 2.71x base (was 3.40x) and low-cost 0.63x. Net value in the high-cost case is -$23.6M. Human review is 43% of the increase (was 56%). The widest layer is now L4, run and maintenance, at 3.85x, driven by the platform team (3 to 12 FTE), migration cadence (every 25 or every 12 months) and effort ranges up to 300 person-days. That is still far wider than published forecast-miss rates (grade C). Narrowing it further means changing the L4 starters. This has not been done.

**Envelope update (per licensed user per year):** Team 1 $649, engineering $4,012, customer service $12,382, regulated review $3,330, Team 5 $660. Team 2's initial cost is $205,000 own plus $86,000 hub share, $291,000 in total, or $163,000 without training, inside Gartner's $100,000 to $200,000 range. The hub one-time cost of $236,800 is now shared by five teams, which lowers each team's share.

**Re-verification on the five-team build:** base case and six variants, 37 values each, 0 mismatches; 11 of 11 tests pass; six mutations each fail exactly their test; sensitivity by full recalculation is exact for six drivers, and adoption and volume is 8.2% off, matching the sheet's stated "about 8%".

## 12. Follow-up: changes made while writing the adoption pack (Phase 6, 2026-09-20)

Writing the onboarding steps and the review answers exposed four problems in the workbook. All four were fixed, and the full check was re-run.

| Found | Why it mattered | Fix |
|---|---|---|
| The file held exactly five teams, hard-wired into its formulas | A pilot with three teams would have broken the allocation checks | A "Team is active" switch (1 or 0) per team; a team set to 0 is ignored everywhere. More than five teams still needs a rebuild |
| The price lookup covered only rows 4 to 24 | A price row added at the bottom during a refresh would have been silently ignored | The lookup now covers 200 rows |
| A mistyped or duplicated price ID priced silently at zero | The refresh procedure asks people to add rows | New test 12: every price ID used exists exactly once. Test 8 was rewritten to ignore blank capacity rows |
| Excel had stored a personal name and a local file path in the delivered file's metadata | Not safe to publish | The build now scrubs both. Excel re-adds the saving user's name when someone saves |

Also confirmed by inspecting the package: no macros, external links, data connections, embedded objects, hidden sheets, defined names or sheet protection. Price dates and status are recorded but not applied in calculations; the adoption pack says so.

**Re-verification of the final build:** the base case and nine variants (the six earlier ones plus two teams switched off under two different shapes and rules, and a single-team pilot), 37 values each, 0 mismatches; 12 of 12 tests pass in every variant; eight deliberate breakages (the six earlier ones, a mistyped price ID and a duplicated price ID) each fail exactly their matching test; sensitivity by full recalculation is unchanged (six drivers exact, adoption and volume 8.2% off). Headline results are unchanged: total cost $18.34M, net value $7.69M, payback month 12.
