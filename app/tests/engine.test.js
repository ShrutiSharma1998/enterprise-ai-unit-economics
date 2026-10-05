// SPDX-License-Identifier: Apache-2.0
// Run: node --test app/tests/engine.test.js
// Compares the browser engine with (1) the independent Python reference model and (2) the workbook's own recalculated values.
const test = require("node:test");
const assert = require("node:assert/strict");
const path = require("node:path");
const Engine = require("../js/engine.js");
const DATA = require("../js/data.js");
const FX = require(path.join(__dirname, "fixtures.json"));

const close = (got, want, what) => {
  assert.ok(got !== null && got !== undefined && Number.isFinite(got), `${what}: got ${got}`);
  const tol = 1e-9 * Math.max(1, Math.abs(want));
  assert.ok(Math.abs(got - want) <= tol, `${what}: got ${got}, want ${want}`);
};

function paramsFor(over) {
  const params = JSON.parse(JSON.stringify(DATA.params));
  for (const [k, v] of Object.entries(over || {})) params[k].vals = [v, v, v];
  return params;
}

function runCase(c) {
  return Engine.run({ k: c.k, valueK: c.valueK, org: c.org, teams: c.teams, params: paramsFor(c.paramsOverride), pricebook: DATA.pricebook });
}

for (const c of FX.cases) {
  test(`engine matches the reference model: ${c.name}`, () => {
    const r = runCase(c), e = c.expected;
    let n = 0;
    const cmp = (got, want, what) => { close(got, want, `${c.name} ${what}`); n++; };
    cmp(r.total_cost, e.total_cost, "total cost");
    cmp(r.comp.benefit, e.benefit, "benefit");
    cmp(r.net, e.net, "net");
    cmp(r.unalloc, e.unalloc, "unallocated");
    cmp(r.cpa_ent, e.cpa_ent, "cost per active user");
    cmp(r.hub_raw_total, e.hub_raw_total, "hub total");
    cmp(r.eff_hub, e.eff_hub, "effective hub");
    for (const i of ["1", "2", "3", "4", "5"]) cmp(r.layers[i], e.layers[i], `layer ${i}`);
    for (const t of ["A", "S", "R", "E"]) cmp(r.by_tag[t], e.by_tag[t], `evidence tag ${t}`);
    for (const key of Object.keys(e.comp)) cmp(r.comp[key], e.comp[key], `comp ${key}`);
    e.cpo.forEach((v, i) => cmp(r.cpo[i], v, `team ${i} cost per outcome (tokens)`));
    e.teams.forEach((t, i) => {
      for (const key of ["direct_total", "alloc", "benefit", "outcomes", "active_months", "net"]) cmp(r.teams[i][key], t[key], `team ${i} ${key}`);
      if (t.cost_per_outcome === null) assert.equal(r.teams[i].cost_per_outcome, null); else cmp(r.teams[i].cost_per_outcome, t.cost_per_outcome, `team ${i} cost per outcome`);
      if (t.cpa_month === null) assert.equal(r.teams[i].cpa_month, null); else cmp(r.teams[i].cpa_month, t.cpa_month, `team ${i} cpa`);
      assert.equal(r.teams[i].payback, t.payback, `${c.name} team ${i} payback`);
    });
    assert.equal(r.payback, e.payback, `${c.name} payback`);
    assert.ok(n >= 30, "compared enough values");
  });
}

test("engine matches the workbook's recalculated base case", () => {
  const w = FX.workbookBase, r = runCase(FX.cases.find((c) => c.name === "base"));
  assert.equal(w.tests, "ALL 12 PASS");
  close(r.total_cost, w.total_cost, "total cost");
  close(r.comp.benefit, w.benefit, "benefit");
  close(r.net, w.net, "net");
  assert.equal(r.payback, w.payback);
  close(r.cpa_ent, w.cpa_ent, "cost per active user");
  close(r.run_rate_last, w.run_rate_last, "run-rate at the last horizon month");
  const outcomes = r.teams.reduce((a, t) => a + t.outcomes, 0);
  close(r.total_cost / outcomes, w.cost_per_outcome, "cost per outcome");
  close(r.comp.benefit / outcomes, w.benefit_per_outcome, "benefit per outcome");
  for (const i of ["1", "2", "3", "4", "5"]) close(r.layers[i], w.layers[i], `layer ${i}`);
  for (const t of ["A", "R", "S", "E"]) close(r.by_tag[t] / r.total_cost, w.shares[t], `share ${t}`);
});

test("cumulative net curve ends at net value and crosses zero at the payback month", () => {
  for (const c of FX.cases) {
    const r = runCase(c);
    close(r.cum_series[r.cum_series.length - 1], r.net, `${c.name} cumulative net at the horizon`);
    assert.equal(r.cum_series.length, c.org.horizon + 1);
    if (r.payback !== null) assert.ok(r.cum_series[r.payback] >= 0 && r.cum_series.slice(1, r.payback).every((v) => v < 0));
  }
});

test("scenario order: low-cost <= base <= high-cost for every layer", () => {
  const base = FX.cases.find((c) => c.name === "base");
  const [lo, ba, hi] = [0, 1, 2].map((k) => runCase({ ...base, k }));
  for (const i of ["1", "2", "3", "4", "5"]) {
    assert.ok(lo.layers[i] <= ba.layers[i] + 1e-6 && ba.layers[i] <= hi.layers[i] + 1e-6, `layer ${i}`);
  }
});

test("a mistyped price ID stops the run instead of pricing at zero", () => {
  const c = JSON.parse(JSON.stringify(FX.cases.find((x) => x.name === "base")));
  c.teams[0].model = "M_SONET5";
  assert.throws(() => runCase(c), /Unknown price ID/);
  const d = JSON.parse(JSON.stringify(FX.cases.find((x) => x.name === "base")));
  d.teams[0].seat_std = "SEAT_TEAM_STDD";
  assert.throws(() => runCase(d), /Unknown price ID/);
});

test("a duplicated price ID stops the run", () => {
  const c = FX.cases.find((x) => x.name === "base");
  const pb = DATA.pricebook.concat([DATA.pricebook[0]]);
  assert.throws(() => Engine.run({ k: 1, valueK: 1, org: c.org, teams: c.teams, params: paramsFor(), pricebook: pb }), /Duplicate price ID/);
});

test("zero outcomes gives zero variable cost while fixed cost remains", () => {
  const c = JSON.parse(JSON.stringify(FX.cases.find((x) => x.name === "base")));
  for (const t of c.teams) { t.o_user = 0; t.direct = 0; }
  const r = runCase(c);
  for (const t of r.teams) { assert.equal(t.direct.tokens, 0); assert.equal(t.direct.vendor, 0); assert.equal(t.outcomes, 0); }
  assert.ok(r.total_cost > 0);
  assert.ok(Number.isFinite(r.net));
});

test("every team switched off leaves hub costs only and no crash", () => {
  const c = JSON.parse(JSON.stringify(FX.cases.find((x) => x.name === "base")));
  for (const t of c.teams) t.active = 0;
  const r = runCase(c);
  assert.equal(r.comp.benefit, 0);
  assert.ok(Number.isFinite(r.total_cost));
});
