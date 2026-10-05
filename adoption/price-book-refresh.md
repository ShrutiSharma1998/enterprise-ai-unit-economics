# Price-book refresh procedure

Built 2026-09-20. For the PriceBook sheet of `model/ai-unit-economics-v0.1.xlsx`. IDs (PRC-01, S09) point to `evidence/`. **(D)** marks our judgement.

## Why it needs a procedure

Prices in the evidence base changed or carried end dates within a single day's reading:

- An announced Sonnet 5 price rise (to $3/$15 on 2026-09-01) was cancelled, so $2/$10 became the standard price (PRC-01).
- Microsoft's seat promotion ($18 against a $21 list) ends 2026-12-31 (S08).
- One Gemini Flash model's introductory price doubles from 2027-01-01 (S11).
- OpenAI lists a promotional price on one model at least through 2026-11-21 (S12).
- Anthropic gives at least 60 days' notice before retiring a model, and observed lifetimes ran 12 to 25 months from release (PRC-06).

A price you copied in September is not a price you can quote in December.

## What the workbook does and does not do with dates

- **Recorded, not applied.** Effective-from, effective-to and status are documentation. The model looks a price up by its ID and takes the first match. It never switches price on a date.
- **Test 8** checks that every price row has a price, an effective-from date and a status. **Test 12** checks that every price ID a team or the hub uses exists exactly once. A mistyped ID would otherwise price silently at zero.
- **A scheduled step inside your horizon is not modelled.** To see its effect, save a second copy with the new price and compare the two Summary sheets.

## When to refresh (D)

| Trigger | Action |
|---|---|
| Before every funding gate | Refresh every row that any team uses |
| At least once a quarter | Refresh the whole book |
| A provider announces a price change | Add the new price with status announced and its effective date |
| A model retirement notice arrives (at least 60 days' warning) | Repoint the teams that use it and re-run the tests |
| A row's effective-to date is within 90 days | Check what replaces it |
| A team changes its buying model or provider | Add the new plan's rows |

The cadence is our judgement; no source prescribes one.

## Known dated events, as of 2026-09-20

| Date | Event | Rows affected | Source |
|---|---|---|---|
| 2026-10-15 | Earliest tentative retirement date for Claude Haiku 4.5 | M_HAIKU45 (the cheaper routing tier on Teams 1, 2, 3 and 5) | S10 |
| 2026-12-31 | Microsoft 365 Copilot Business promotion ends | SEAT_M365_BUS | S08 |
| 2026-12-31 | Gemini 3.8 Flash introductory price ends; doubles from 2027-01-01 | M_GEM38FLASH | S11 |
| 2027-06-30 | Earliest tentative retirement date for Claude Sonnet 5 | M_SONNET5 | S10 |
| 2027-07-24 | Earliest tentative retirement date for Claude Opus 5 | M_OPUS5 | S10 |

Retirement dates are "not sooner than" dates and can move. Set a reminder 90 days ahead.

## Steps

1. **Pick the rows.** List the rows any active team uses, plus the two monitoring rows (PL_LANGFUSE_PRO, U_LANGFUSE_OVER).
2. **Open the provider's own page.** The Source column gives the ID; the URL is in `evidence/source-register.md`. Some pages block automated fetching (OpenAI and Gartner returned 403). Read them in a browser. Model names in the book are as extracted, so confirm each one.
3. **Compare.** If the price is unchanged, update **Date fetched** and stop.
4. **If it changed, add a row; never overwrite.**
   - Add the new row below the last one (the lookup covers rows 4 to 203), with a **new unique ID** such as `M_SONNET5_2026Q4`.
   - Fill price, unit, source, date fetched, grade A and label "quoted".
   - Set **Effective from** to the date the price takes effect, or the date you first saw it if unknown. Set **Status** to standard, promotional or announced.
   - On the old row, set **Effective to**. Keep it.
5. **Repoint.** On Teams, change the price ID fields of each team that should use the new row.
6. **Register.** Add a row for the new price to the **Evidence** sheet (ID, source, date, grade, owner, last reviewed). Test 7 only checks rows that are in the register.
7. **Re-check the fixtures.** Levers fixtures 3 and 4 reproduce the worked example on Anthropic's pricing page. If that page's example changes, update the fixtures and note the date.
8. **Run the tests.** All 12 must pass.
9. **Record the change.** Save the workbook under a dated name, keep the previous file, and write one line: date, rows changed, and the change in total cost and net value on Summary.

## Ownership

The price-book owner (a delegate of the AI program lead, or a FinOps practitioner) refreshes. The finance partner reviews the change line before the workbook is used at a gate. See `adoption/ownership-and-cadence.md`.
