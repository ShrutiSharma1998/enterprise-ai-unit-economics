# AI unit economics: a planning workbook and calculator for enterprise AI programs

**What it is:** an Excel workbook, and a browser calculator built on the same model, that show an enterprise what an AI program will cost across its teams before it builds: setup, data readiness, inference, run and people costs, with break-even and sensitivity.
**Headline finding:** only 11 of the 35 cost lines an enterprise faces can be defaulted from dated public prices; the rest need its own numbers. In the fictional worked example, one assumption decides whether a seat tool pays: the share of claimed time savings that is actually realised. The same product nets -$3.3M or +$2.0M depending only on minutes saved per use.
**Try the calculator now:** https://shrutisharma1998.github.io/enterprise-ai-unit-economics/app/ (runs entirely in your browser; nothing you enter is sent anywhere).
**How to open it:** for the workbook, open `model/ai-unit-economics-v0.1.xlsx` in Excel, start at the README sheet, then Summary. For the calculator, serve the folder (`python -m http.server 8000`) and browse to `http://localhost:8000/app/`; it runs entirely in your browser and can export and re-import a pre-filled Excel template for detailed input. Everything in the example is fictional.

Status: workbook version 0.1; browser calculator preview 0.2. A fictional worked example, not validated against a real enterprise.

## What is in this repo

| Folder | What it holds |
|---|---|
| `model/` | The workbook (17 sheets, about 24,000 formulas, no macros), its build scripts, and an independent reference model used to verify it |
| `app/` | The browser calculator: quick estimate on screen, detailed input through a pre-filled Excel template. Plain HTML, CSS and JavaScript, no server, no network requests |
| `evidence/` | 49 sources and 66 graded, dated benchmarks, with where they conflict and what no source answers |
| `research/` | How enterprises are structured and use AI, and the cost taxonomy (5 layers, 35 lines) |
| `spec/` | The requirements spec, input schema and starter values the workbook was built to |
| `validation/` | What checking the workbook found, including a bug in its own first numbers |
| `adoption/` | Onboarding, price-book refresh, ownership, and what security, finance and data-residency reviews will ask |

## How far to trust it

- **Evidence first.** Every benchmark is graded A to D (dated primary price, named survey, blog or vendor claim, our assumption) and conflicts are shown, not averaged.
- **Checked against an independent implementation.** The workbook is recalculated in Excel and compared with a separate Python model across nine variants, and 12 acceptance tests run inside the file. Deliberate breakages each fail exactly their matching test.
- **The calculator is checked against the same references.** Its JavaScript engine is compared with the Python model and with the workbook's own recalculated values (34 tests), and deliberate breakages of the engine are each caught.
- **Reproduces a provider's published example.** Anthropic's own worked pricing example matches to the cent.
- **Not validated against a real enterprise.** No public case publishes both its inputs and its realised costs. The value side has no external check, and most of the cost lines rest on starter values (grade D) or inputs the enterprise must supply.

## Known limits

Five teams in the file (a per-team switch ignores unused ones); one team per business unit; price dates are recorded but not applied; net value is undiscounted USD; committed capacity is a fixed cost; four cost lines are off until entered. Verified in Windows Excel only. The calculator has been driven in one browser only, saves nothing between visits (use the Excel template to carry work over), and no real user has tried it. Details in `model/README.md`, `app/README.md` and `validation/phase5-validation.md`.

## How this was made

Built with AI assistance (Claude, Anthropic) under the project owner's direction; see [docs/how-this-was-built.md](docs/how-this-was-built.md). Every number is labeled with its source and evidence grade.

## Licence

- `model/` (the workbook and its build scripts) and `app/` (the browser calculator): Apache License 2.0. See [LICENSE](LICENSE) and [NOTICE](NOTICE). `app/js/vendor/` holds the SheetJS library, unmodified, under its own Apache 2.0 licence.
- Written material (this README, `adoption/`, `docs/`, `evidence/`, `research/`, `spec/`, `validation/`): CC BY 4.0. See [LICENSE-docs.md](LICENSE-docs.md).
- Prices, figures and short quotations from providers and publishers belong to them; confirm at the source. Company and product names are their owners' trademarks, and no provider endorses or is affiliated with this work. Provided as is, without warranty.

Copyright 2026 Shruti Sharma.
