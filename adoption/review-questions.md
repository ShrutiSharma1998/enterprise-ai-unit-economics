# What security, finance and data-residency reviews will ask

Built 2026-09-20. The questions are our judgement (D), informed by the cited evidence. The answers about the workbook are facts from inspecting the file on that date. IDs (PRC-01, G5) point to `evidence/`.

## What the file contains (checked 2026-09-20)

The package of `model/ai-unit-economics-v0.1.xlsx` was inspected directly:

| Feature | Present? |
|---|---|
| Macros (VBA) | No. The file is `.xlsx` and has no macro project |
| External links | No |
| Data connections or query tables | No |
| Embedded objects, ActiveX, images | No |
| Hidden sheets, defined names | No |
| Sheet or workbook protection | No |
| Author name and local file path in the metadata | Removed from the delivered file. Excel adds the saving user's name again when someone saves |

To check it yourself, rename the file to `.zip` and list the parts.

## Security

| Question | Answer |
|---|---|
| Does it send data anywhere? | No. It is a file with formulas. It has no macros, links or connections, so it makes no network calls |
| What can it run? | Excel formulas only |
| What data does it hold? | In the delivered file, fictional data only. Once real inputs go in, it holds team headcounts, planned usage, vendor quotes and staffing assumptions: commercially sensitive planning data. Classify and store it under your own policy. The workbook does not encrypt or redact anything |
| Can numbers be changed without a trace? | Yes. No protection is applied, and Excel keeps no change history unless your storage does. Use dated file versions (`adoption/ownership-and-cadence.md`) |
| What is needed to use it? | Microsoft Excel. It was recalculated and verified in Windows Excel only; other spreadsheet programs are untested |
| What is needed to rebuild it? | Python with `openpyxl`, and Excel (`model/README.md`). The build scripts are in `model/build/` and are readable |
| Does it depend on any service at run time? | No. Prices are typed into the PriceBook. There is no automatic price fetching |

## Finance

| Question | Answer |
|---|---|
| Can I trace any number? | Yes. Formulas are visible, every input has a label, source, date and grade in the Evidence sheet, and 12 tests run on the file |
| How much of the cost is evidence-based? | Summary shows the share resting on dated primary prices, ranges, starter values and enterprise-entered values. In the worked example: 41%, 25%, 34% and 0% |
| How are one-time costs treated? | Straight-line over the horizon for cost totals (36 months by default). Payback uses cash timing, with one-time costs at month 0 |
| How are shared costs allocated? | Four rules: usage-proportional, headcount proxy, even split, or a central budget (ORG-01). Federated shape duplicates the platform per unit instead |
| Showback or chargeback? | Showback: the Allocation sheet is a cost-center table ready to export. Chargeback needs a cost-center hierarchy and general-ledger support (ORG-08); the workbook is the manual, spreadsheet-based level |
| Is there a discount rate or NPV? | No. Net value is benefit minus cost, undiscounted, in USD, before tax. Add discounting yourself if your gate needs it |
| How should I read the benefit? | As a scenario. Benefit is self-reported time saved, times a loaded rate, times a realisation share (default 50%, our assumption). No source converts self-reported time saved into realised savings (G5) |
| How accurate is it? | Unknown, and published AI cost forecasts miss often: 85% miss by more than 10% in one vendor-sponsored survey (FCS-01, grade C). The high-cost case is a stress test, not a likely outcome |
| How do I reconcile to actuals? | Set a revisit at go-live and compare against a variance threshold you define (ORG-11) |

## Data residency and compliance

| Question | Answer |
|---|---|
| Does it enforce residency? | No. It prices it. Each team has a residency multiplier |
| What does residency cost? | Published premiums: 1.1x on all token categories for US-only inference on the Claude API for models from 4.6 (PRC-01), a 10% uplift on OpenAI models released on or after 2026-03-05 (PRC-02), and regional or multi-region endpoints 10% above global for Claude 4.5 and later on partner clouds (BUY-05). Confirm each on the provider's page |
| Where does inference data go? | Out of scope. It is a cost model. Review each provider's terms and regions separately |
| Does it assess regulation (for example the EU AI Act or sector rules)? | No. It does not classify risk or check compliance |
| Is the cost of compliance included? | The compliance audit line (CL-31) has no starter and is OFF until you enter it. It appears on Summary as an off line |
| What does regulated work cost? | People, not models, in the worked example: reviewing every output cost about 19 times the model spend for the regulated team (validation report). That rests on our review-minute assumption |
| What about data readiness for sensitive data? | The effort lines exist (CL-01 to CL-04) with starter values. No public benchmark exists (G1) |

## What the tool cannot answer

- Whether time saved becomes cash saved (G5).
- What a real organization's costs will be. The example is fictional.
- Regulatory classification, provider data handling, or where data is processed.
- Costs of self-hosted models beyond a single fixed-cost line.
- Multi-year price changes: dates are recorded but not applied.
- Discounted value, tax, or currency other than USD.
