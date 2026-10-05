# Browser calculator (preview 0.2)

A quick-estimate calculator that runs in the browser. Pick team types, buying models and approximate usage, and see cost by layer, net value, payback and how much of the cost rests on starter values. It can also export a detailed Excel template pre-filled with the current inputs, and read a filled-in one back for the full ~50-field-per-team detail. The Excel workbook in `../model/` stays the auditable version a finance reviewer would check formulas in. The design is in `../spec/prototype-spec.md`.

Everything shown is a fictional worked example (Northwind Example Co) unless you replace it. Nothing you type leaves your browser, including uploaded files: they are read locally by the vendored spreadsheet library, never sent anywhere.

## Open it

Serve the repository folder and open the page:

```
python -m http.server 8000
```

Then browse to `http://localhost:8000/app/`. The page uses plain scripts and makes no network requests, so opening `app/index.html` directly should also work, but that has not been tested. The "Open the detailed workbook" link expects the repository layout (`../model/`).

If you edit `app/js/xlsx-template.js` or `app/js/app.js` while testing in a browser, hard-reload (or fetch with `cache: "no-store"`) — plain HTTP servers like `python -m http.server` let browsers cache `<script src>` files aggressively, so a stale copy can keep running after a save.

## What is built

The quick-estimate screen, and the Excel template download and upload.

## Files

| File | What it is |
|---|---|
| `index.html`, `style.css`, `js/app.js` | The screen |
| `js/engine.js` | The calculation, ported from `model/build/reference_model.py` |
| `js/data.js` | Parameters, price book, field schema and the worked example. Generated: `python app/build/export_data.py` |
| `js/xlsx-template.js` | Builds the pre-filled Excel template and parses an uploaded one back, with validation |
| `js/vendor/xlsx.full.min.js` | Third-party (SheetJS, Apache-2.0); see `js/vendor/README.md` |
| `tests/engine.test.js`, `tests/fixtures.json` | Checks against the Python reference model and the workbook |
| `tests/template.test.js` | Checks the Excel template: a real-bytes round trip, and each validation rule |
| `build/make_fixtures.py` | Rebuilds `fixtures.json` from the reference model and the workbook |
| `build/mutation_check.py` | Breaks the engine on purpose and confirms the tests fail |

## Check it

```
python app/build/export_data.py
python app/build/make_fixtures.py
node --test app/tests/*.test.js
python app/build/mutation_check.py
```

Needs Node (tested with 24) and Python 3 with `openpyxl` (tested with 3.14). `make_fixtures.py` reads the recalculated workbook, so it needs no Excel.

## The Excel template

Five sheets: **Read me** (instructions, not read by the parser), **Org**, **Teams**, **Enterprise costs** and **Price book** (reference only, for copying price IDs). Column A on every data sheet is a machine-readable key; the parser reads by key regardless of row order, so reordering rows is safe. There is no fixed limit on the number of teams: copy an existing team's column into a new one to add another.

Six fields are required on every team column (archetype, buying model, licensed users, active share, outcome basis, minutes saved per outcome); a missing or invalid value there is an upload error, and the file is rejected with a list of every problem found rather than applied partially. Every other blank field falls back to the chosen team type's starter value, with a warning naming the field. A blank vendor-price cell is a valid choice (priced per token instead) where the field allows "none", not a warning. Uploading a file that isn't a template from this calculator, or one whose header rows were altered, is refused with a plain-language message.

## Known limits

- Session data is not saved between visits: reloading returns to the fictional example. Downloading, editing and re-uploading the template is today's way to carry work between sessions.
- The evidence bar counts by cost line. A line counts as a dated price when its unit price comes from a provider's page; volumes such as users and tokens per outcome remain assumptions.
- Team types A5 and A6 use placeholder usage values copied from A1.
- Price effective dates are shown but not applied, and net value is undiscounted USD, as in the workbook.
- The template does not let you choose which scenario (low/base/high-cost) or realisation share the calculator opens with; that stays a screen toggle.
- Checked by driving it in one browser (the Claude desktop app's built-in browser) at desktop and phone width, including a real .xlsx download/edit/upload cycle via the vendored library. Other browsers, opening it as a local file, and screen readers are untested. No real user has tried it.
