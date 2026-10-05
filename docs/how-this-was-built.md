# How this was built

A short account for readers deciding how far to trust the work.

## Approach

Evidence first. Every benchmark is graded A to D (dated primary price, named survey with a visible method, blog or vendor claim, our assumption) and logged with its definition, population, source and date. Where sources conflict the conflict is shown and explained through definitions, never averaged. Gaps are listed as gaps. Prices come from providers' own pages.

## Phases

| Phase | Question | Where |
|---|---|---|
| 0 Evidence base | What does the industry actually know, and how sure can we be? | `evidence/` |
| 1 Enterprise structure and usage | How are enterprises organised, who pays, how do teams use AI? | `research/enterprise-structure.md` |
| 2 Cost structure | What are the cost layers, drivers and owners? | `research/cost-taxonomy.md` |
| 3 Requirements | What must an enterprise enter, and what can the tool default? | `spec/` |
| 4 Workbook | Turn the spec into a working, auditable model | `model/` |
| 5 Validation | Does it hold up, and where does it not? | `validation/` |
| 6 Adoption | How does an enterprise start, keep it current, and get it through review? | `adoption/` |
| 7 Browser calculator (added afterwards) | Can users get a first estimate without Excel, and add detail through a structured template? | `app/`, `spec/prototype-spec.md` |

The project owner approved the design at the end of phases 1 to 3 and approved the workbook build before it started.

## Decisions taken by the project owner

- Free public sources only, graded A to D.
- Three org shapes as a switch, six team archetypes, four buying-model calculators, a 36-month default horizon.
- Effort lines carry labeled starter values (grade D). Four lines have no starter and are off until entered.
- After validation: the review-minute range was narrowed, the high-cost case was labeled a stress case, and Team 1 was kept in a conservative version with a second, published-range version added.

## How it was checked

A separate Python implementation of the calculation rules is compared with the workbook, recalculated in Excel, across nine variants. Twelve acceptance tests run inside the file. Inputs are deliberately broken to confirm the right test fails. A provider's own published worked example is reproduced. Each sensitivity driver is changed for real and recalculated. Details are in `validation/`. The browser calculator's engine is compared with that Python model and with the workbook's recalculated values, its Excel template is tested by a real file round trip and by malformed uploads, and deliberate breakages of the engine are each caught (`app/README.md`).

## What went wrong and was fixed

Validation found that outcome totals summed all 60 grid months instead of the horizon, that the price lookup ignored rows added at the bottom, that a mistyped price ID priced silently at zero, and that the delivered file carried a personal name and local path in its metadata. All were fixed and re-verified. See sections 2 and 12 of `validation/phase5-validation.md`.

## How AI was used

The work was done by Claude (Anthropic) under the project owner's direction: reading sources, drafting, building the workbook and scripts, and checking. Web pages were read through a tool that summarises them, so quotations are as extracted and should be confirmed at the source. Several original reports could not be opened and their figures are marked provisional (an asterisk). The work has not been independently audited, and no real organization has used it.

## What it is not

Not a forecast for any organization. Not financial or legal advice. Not validated against a real enterprise's actuals.
