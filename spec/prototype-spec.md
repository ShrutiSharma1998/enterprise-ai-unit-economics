# Browser calculator: prototype spec (preview 0.2)

Built 2026-09-21 on the project owner's instruction; Excel upload added 2026-09-22, also on the project owner's instruction. Status: both the quick-estimate screen and the Excel download/upload are built and verified. This adds a front end that `requirements-spec.md` listed as out of scope for v1. The Excel workbook in `model/` stays the v1 deliverable and the version a finance reviewer can audit; the template here is a separate, simpler file the calculator itself reads and writes.

## Why

Enterprise users want a calculator they can use without knowing the model: pick team types, buying models and approximate usage, and see what the cost looks like. Anyone who needs more precision then supplies detail in Excel. One tool, two levels.

## The two levels

1. **Quick estimate (built).** The user enters the organization (shape, allocation rule, horizon) and one card per team. A team card asks for team type, buying model, main model, licensed users, active share, usage per active user (or direct volume), and minutes saved per outcome. Every other input, about 40 more, starts from the team type's starter value (grade D) and can be opened and changed under "More inputs". Four costs with no starter value (environments, compliance audit, platform licences, committed capacity) stay off until entered, and the screen says so.
2. **Firm it up with Excel (built).** "Download template, pre-filled" writes an `.xlsx` file with the user's current organization and teams already filled in, plus a Read me sheet and a Price book sheet to copy price IDs from. The user edits it in Excel (or any spreadsheet program that can save `.xlsx`) and uploads it back with "Upload filled workbook". The file is validated before anything changes: missing or invalid values in the six required team fields (archetype, buying model, licensed users, active share, outcome basis, minutes saved) make the whole upload fail with a list of every problem, so the calculator's state never ends up half-updated. Every other blank field falls back to the chosen team type's starter value, with a warning naming the field, mirroring the same "starter until entered" idea as the quick-estimate screen's dots. There is no fixed limit on the number of teams: the user copies an existing column to add one.

## What the screen shows

Total cost, benefit, net value and payback in a header that stays in view while inputs change. Cost per outcome, benefit per outcome, cost per active user, the monthly run cost and the shared (hub) share of cost. The low-cost, base and high-cost range. Cost by layer. Net value and payback by team. The cumulative net value curve. What the cost rests on: dated prices, ranges, starter values and enterprise-entered values. The margin by which benefit can fall before net value reaches zero. The cost lines that are still off. A price book and a parameter table with grades and dates.

## Rules it follows

- The calculation is a port of `model/build/reference_model.py`, and it reads the same parameters, price book and worked example (`app/build/export_data.py` writes them from `model/build/spec_data.py`).
- Every displayed number comes from the engine. Prices carry their source and the date fetched. A price ID that does not exist stops the calculation with a message instead of pricing at zero.
- Nothing is sent anywhere, including the uploaded workbook: it is read locally by a vendored spreadsheet library (SheetJS, Apache-2.0), never over the network.
- A hollow dot beside an input means the value is still a starter (grade D); a filled dot means the user entered it, whether by typing on the screen or by an uploaded cell that differs from the starter.
- Team types A5 and A6 have no worked example, so their usage values are placeholders copied from A1 and are labeled that way. The model values time saved, so revenue from an embedded feature (A5) is not captured.
- The Excel template's column A on every data sheet is a machine-readable key; the parser reads by key regardless of row order, so a user reordering rows does not break the upload. Rows with an unrecognised key are ignored with a warning, not applied. Uploading a file that is not a template from this calculator, or whose header rows were altered, is refused with a plain message rather than parsed as if it were one.

## Verification

`node --test app/tests/engine.test.js` compares the engine with the Python reference model on the base case, the nine variants used to verify the workbook, a committed-capacity case and an enterprise-entered-cost case. It also compares the base case with the workbook's own recalculated Summary values. `python app/build/mutation_check.py` breaks the engine nine ways and confirms the suite fails each time. `node --test app/tests/template.test.js` (15 tests) builds a template as real `.xlsx` bytes with the vendored library, reads them back, and confirms the result reproduces the original teams through the engine; nine of the fifteen check malformed or edge-case uploads (a missing required field, an unknown price ID, an out-of-range percentage, an invalid select value, reordered rows, an unrecognised row, a file missing the Read me sheet, an invalid org shape, a horizon above the maximum) each fail with the right message or recover with the right warning. The screen was driven in a browser to confirm that what it shows equals the engine's output; that editing inputs, switching shape and horizon, and adding, removing and switching off teams all recompute correctly; and, separately, a full download-edit-upload cycle through the real vendored library, including two deliberately broken uploads, each correctly refused without changing the displayed numbers.

## Not built, and open

- Saving a session in the browser, CSV export of the team table, the ranked sensitivity table, and per-input evidence tracking (the evidence bar counts by cost line).
- The Excel template does not carry which scenario or realisation share to open with; that stays a screen toggle.
- No real user has tried it. The 30-minute first-estimate target is untested. Other browsers, opening the page as a local file, and screen readers are untested.
- Hosting is publishing and needs the project owner's explicit yes. The design assumes static hosting with no server.
