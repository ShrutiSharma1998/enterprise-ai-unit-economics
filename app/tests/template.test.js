// SPDX-License-Identifier: Apache-2.0
// Run: node --test app/tests/template.test.js
// Checks the Excel template builder and parser: a round trip through real .xlsx bytes should reproduce the
// original teams (once run through the calculation engine), and malformed uploads should fail with a clear
// message instead of silently producing wrong numbers.
const test = require("node:test");
const assert = require("node:assert/strict");
const XLSX = require("../js/vendor/xlsx.full.min.js");
global.XLSX = XLSX;   // Template's browser-only functions read the library off the global object
const Template = require("../js/xlsx-template.js");
const Engine = require("../js/engine.js");
const D = require("../js/data.js");

function baseState() {
  return {
    orgName: D.meta.org.name,
    org: { shape: D.meta.org.shape, alloc: D.meta.org.alloc, horizon: D.meta.org.horizon, pd_rate: D.meta.org.pd_rate,
      hours_day: D.meta.org.hours_day, work_days: D.meta.org.work_days, obs_per_out: D.meta.org.obs_per_out },
    entered: { env_month: 0, comp_year: 0, lic_year: 0 },
    teams: JSON.parse(JSON.stringify(D.exampleTeams)),
  };
}

function toWorkbookBytes(state) {
  const sheets = Template.buildAOA(state, D);
  const wb = XLSX.utils.book_new();
  for (const key of Template.SHEET_ORDER) XLSX.utils.book_append_sheet(wb, XLSX.utils.aoa_to_sheet(sheets[key]), Template.SHEET_NAMES[key]);
  return XLSX.write(wb, { type: "buffer", bookType: "xlsx" });
}

function readWorkbookBytes(buf) {
  const wb = XLSX.read(buf, { type: "buffer" });
  const sheets = {};
  for (const key of Template.SHEET_ORDER) {
    const name = Template.SHEET_NAMES[key];
    if (wb.Sheets[name]) sheets[key] = XLSX.utils.sheet_to_json(wb.Sheets[name], { header: 1, defval: "", raw: true });
  }
  return sheets;
}

function runEngine(state) {
  return Engine.run({ k: 1, valueK: 1, org: state.org, teams: state.teams, params: D.params, pricebook: D.pricebook });
}

test("a round trip through real .xlsx bytes reproduces the fictional example's result", () => {
  const state = baseState();
  const buf = toWorkbookBytes(state);
  const sheets = readWorkbookBytes(buf);
  const parsed = Template.parseAOA(sheets, D);
  assert.deepEqual(parsed.errors, []);
  assert.deepEqual(parsed.warnings, []);
  assert.equal(parsed.orgName, state.orgName);
  assert.deepEqual(parsed.org, state.org);
  assert.deepEqual(parsed.entered, state.entered);
  assert.equal(parsed.teams.length, state.teams.length);
  const rebuilt = { org: parsed.org, teams: parsed.teams.map((t) => t.team) };
  const before = runEngine(state), after = runEngine(rebuilt);
  assert.ok(Math.abs(before.total_cost - after.total_cost) < 1e-6, "total cost");
  assert.ok(Math.abs(before.net - after.net) < 1e-6, "net value");
  assert.equal(before.payback, after.payback);
  parsed.teams.forEach((t, i) => {
    assert.ok(Math.abs(t.team.min_saved - state.teams[i].min_saved) < 1e-9, "min_saved carried through for team " + i);
  });
});

test("the blank 'add a team here' column is ignored", () => {
  const state = baseState();
  const sheets = readWorkbookBytes(toWorkbookBytes(state));
  assert.equal(sheets.teams[0][sheets.teams[0].length - 1].includes("Add a team here"), true);
  const parsed = Template.parseAOA(sheets, D);
  assert.equal(parsed.teams.length, state.teams.length, "the unused guide column is not read as a team");
});

test("a filled-in extra column becomes a new team", () => {
  const state = baseState();
  const sheets = readWorkbookBytes(toWorkbookBytes(state));
  const lastCol = sheets.teams[0].length - 1;
  const set = (key, val) => { sheets.teams.find((r) => r[0] === key)[lastCol] = val; };
  set("name", "New AI helper");
  set("archetype", "A1 Knowledge-worker assistant");
  set("buy", "Seat");
  set("licensed", 250);
  set("plateau", 60);
  set("basis", "per user");
  set("min_saved", 3);
  const parsed = Template.parseAOA(sheets, D);
  assert.deepEqual(parsed.errors, []);
  assert.equal(parsed.teams.length, state.teams.length + 1);
  const added = parsed.teams[parsed.teams.length - 1];
  assert.equal(added.team.name, "New AI helper");
  assert.equal(added.team.licensed, 250);
  assert.equal(added.edited.licensed, true);
  assert.ok(!added.edited.tok_in, "an untouched field is not marked as entered");
});

test("leaving a vendor price ID blank is a valid choice, not a starter-value warning", () => {
  const state = baseState();
  const sheets = readWorkbookBytes(toWorkbookBytes(state));
  const parsed = Template.parseAOA(sheets, D);
  assert.deepEqual(parsed.errors, []);
  assert.ok(!parsed.warnings.some((w) => w.includes("Vendor per-outcome price")), "no warning for a field whose blank state is itself meaningful");
  assert.equal(parsed.teams[0].team.unit_price, "");
});

test("a missing required field is an error, not a silent default", () => {
  const state = baseState();
  const sheets = readWorkbookBytes(toWorkbookBytes(state));
  const buyRow = sheets.teams.find((r) => r[0] === "buy");
  buyRow[3] = "";
  const parsed = Template.parseAOA(sheets, D);
  assert.ok(parsed.errors.some((e) => e.includes("Buying model") && e.includes("required")));
  assert.equal(parsed.teams.length, state.teams.length - 1, "the broken team column is dropped, not guessed at");
});

test("a blank optional field falls back to the starter value, with a warning", () => {
  const state = baseState();
  const sheets = readWorkbookBytes(toWorkbookBytes(state));
  const tokRow = sheets.teams.find((r) => r[0] === "tok_in");
  tokRow[3] = "";
  const parsed = Template.parseAOA(sheets, D);
  assert.deepEqual(parsed.errors, []);
  assert.ok(parsed.warnings.some((w) => w.includes("Input tokens per outcome") && w.includes("starter value")));
  const archetype = D.archetypes[Object.keys(D.archetypes).find((c) => D.archetypes[c].label === parsed.teams[0].team.archetype)];
  assert.equal(parsed.teams[0].team.tok_in, archetype.preset.tok_in);
});

test("an unknown price ID is rejected with a message pointing at the price book", () => {
  const state = baseState();
  const sheets = readWorkbookBytes(toWorkbookBytes(state));
  const modelRow = sheets.teams.find((r) => r[0] === "model");
  modelRow[3] = "M_SONET5";
  const parsed = Template.parseAOA(sheets, D);
  assert.ok(parsed.errors.some((e) => e.includes("M_SONET5") && e.includes("Price book")));
});

test("a value outside a select's options is rejected and lists the valid ones", () => {
  const state = baseState();
  const sheets = readWorkbookBytes(toWorkbookBytes(state));
  const buyRow = sheets.teams.find((r) => r[0] === "buy");
  buyRow[3] = "Subscription";
  const parsed = Template.parseAOA(sheets, D);
  assert.ok(parsed.errors.some((e) => e.includes("Subscription") && e.includes("Seat")));
});

test("a percentage outside 0 to 100 is rejected", () => {
  const state = baseState();
  const sheets = readWorkbookBytes(toWorkbookBytes(state));
  const plateauRow = sheets.teams.find((r) => r[0] === "plateau");
  plateauRow[3] = 140;
  const parsed = Template.parseAOA(sheets, D);
  assert.ok(parsed.errors.some((e) => e.includes("140") && e.includes("between 0 and 100")));
});

test("an unrecognised row is ignored with a warning, not applied", () => {
  const state = baseState();
  const sheets = readWorkbookBytes(toWorkbookBytes(state));
  sheets.teams.push(["not_a_real_field", "Made up", "text", "hello", "", "", "", "", ""]);
  const parsed = Template.parseAOA(sheets, D);
  assert.ok(parsed.warnings.some((w) => w.includes("not_a_real_field") && w.includes("ignored")));
});

test("rows in a different order still parse correctly", () => {
  const state = baseState();
  const sheets = readWorkbookBytes(toWorkbookBytes(state));
  const header = sheets.teams[0];
  const body = sheets.teams.slice(1).reverse();
  sheets.teams = [header].concat(body);
  const parsed = Template.parseAOA(sheets, D);
  assert.deepEqual(parsed.errors, []);
  assert.equal(parsed.teams.length, state.teams.length);
});

test("a file without the calculator's Read me sheet is refused", () => {
  const sheets = readWorkbookBytes(toWorkbookBytes(baseState()));
  delete sheets.readme;
  const parsed = Template.parseAOA(sheets, D);
  assert.equal(parsed.teams.length, 0);
  assert.ok(parsed.errors[0].includes("Read me"));
});

test("an org shape outside the known list is rejected", () => {
  const sheets = readWorkbookBytes(toWorkbookBytes(baseState()));
  const shapeRow = sheets.org.find((r) => r[0] === "shape");
  shapeRow[2] = "Matrix";
  const parsed = Template.parseAOA(sheets, D);
  assert.ok(parsed.errors.some((e) => e.includes("Matrix") && e.includes("Centralized")));
});

test("a horizon above the maximum is rejected", () => {
  const sheets = readWorkbookBytes(toWorkbookBytes(baseState()));
  const hRow = sheets.org.find((r) => r[0] === "horizon");
  hRow[2] = 90;
  const parsed = Template.parseAOA(sheets, D);
  assert.ok(parsed.errors.some((e) => e.includes("90") && e.includes("maximum")));
});

test("enterprise-entered organization-wide costs round-trip", () => {
  const state = baseState();
  state.entered = { env_month: 9000, comp_year: 60000, lic_year: 120000 };
  const parsed = Template.parseAOA(readWorkbookBytes(toWorkbookBytes(state)), D);
  assert.deepEqual(parsed.entered, state.entered);
});
