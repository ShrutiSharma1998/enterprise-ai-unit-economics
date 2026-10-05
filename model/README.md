# model/

`ai-unit-economics-v0.1.xlsx`: the thin workbook (v0.1), built from the approved spec in `spec/`. Open it in Excel. Formulas are visible, there are no macros, and nothing leaves your machine.

**It is a fictional worked example.** The organization, teams and usage are assumptions (grade D). Only the dated prices in the PriceBook sheet are grade A. It is not a forecast for any real organization.

## Start here

Open the README sheet, then Summary. Change settings on Org, replace the fictional teams on Teams, review every starter value on Params, and check every price on PriceBook. The Tests sheet should say ALL 12 PASS (the ten tests in `spec/requirements-spec.md` plus two added in Phases 5 and 6). The validation report is `validation/phase5-validation.md`.

## How it was verified

- `build/reference_model.py` is an independent Python re-implementation of the calculation rules (plain loops, no shared code with the workbook builder).
- `build/verify.py` recalculates the workbook with Excel and compares every total with the reference model for the base build and nine variants (org shape, allocation rule, scenario, value case, horizon, and teams switched off).
- It also breaks inputs on purpose (a blank price status, a blank evidence label, a wrong fixture, a low-cost value above base, a total that counts all 60 months, a mistyped price ID, a duplicate price ID) and checks that exactly the matching acceptance test fails.
- `build/validate.py` runs the Phase 5 checks: envelope ranges, scenario bands, and a full-recalculation test of each sensitivity driver.

## Rebuild and re-verify

Needs Python 3 with `openpyxl`, and Microsoft Excel on Windows (the recalculation step drives Excel; `build/recalc_excel.ps1`).

```bash
cd model/build
python build.py
python verify.py base <scratch-dir>
python verify.py variants <scratch-dir>
python verify.py mutations <scratch-dir>
```

## Known limits of v0.1 (also on the README sheet)

Five teams in the file (a per-team switch ignores unused ones; more needs a rebuild); one team per business unit; price dates are recorded but not applied in calculations; lines owned by both hub and team are modelled at team level; sensitivity is one-at-a-time with linear scaling, not a full recalculation; committed capacity is a fixed monthly cost with no utilization calculation; four lines have no starter and are off until entered (CL-14, CL-15, CL-31, CL-32).

## Adoption

See `../adoption/` for the onboarding one-pager, the price-book refresh procedure, ownership and cadence, and what security, finance and data-residency reviews will ask.
