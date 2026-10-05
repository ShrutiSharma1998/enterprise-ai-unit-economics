// SPDX-License-Identifier: Apache-2.0
// Calculation engine for the browser calculator. A line-by-line port of model/build/reference_model.py,
// which is the independent check on the Excel workbook. app/tests/engine.test.js compares this engine with
// that reference model and with the workbook's own recalculated values.
// k = 0 low-cost, 1 base, 2 high-cost. valueK = 0, 1, 2 picks the realisation share (low, base, high).
(function (root, factory) {
  if (typeof module === "object" && module.exports) module.exports = factory();
  else root.Engine = factory();
}(typeof self !== "undefined" ? self : this, function () {
  "use strict";

  const MONTHS = 60;
  const LANGFUSE_INCLUDED = 100000;   // units included in the Pro plan (evidence source S44)

  // Evidence tag per cost line: A dated primary price, S starter value, R range with a warning, E enterprise-entered.
  const TAG = { seat: "A", tokens: "A", vendor: "A", tools: "A", cap: "E", data_price: "A", data_effort: "S", run_effort: "S",
    migration: "R", review: "R", cm: "S", ot_data_effort: "S", ot_data_load: "A", ot_l2: "S", ot_train: "S" };
  const LAYER = { seat: 3, tokens: 3, vendor: 3, tools: 3, cap: 2, data_price: 1, data_effort: 1, run_effort: 4, migration: 4,
    review: 5, cm: 5, ot_data_effort: 1, ot_data_load: 1, ot_l2: 2, ot_train: 5 };
  const HUB_TAG = { plat_ot: "S", perm_ot: "S", rev_ot: "S", rt_ot: "S", plat_run: "S", perm_up: "S", rt_rep: "S", env: "E",
    mon: "A", plat_team: "S", gov: "R", comp: "E", lic: "E" };
  const HUB_LAYER = { plat_ot: 2, perm_ot: 1, rev_ot: 2, rt_ot: 2, plat_run: 2, perm_up: 1, rt_rep: 2, env: 2,
    mon: 4, plat_team: 4, gov: 4, comp: 4, lic: 4 };
  const TEAM_ROWS = ["ramp", "lic", "act", "out", "seat", "tokens", "vendor", "tools", "cap", "data_price", "data_effort", "run_effort",
    "migration", "review", "cm", "ot_data_effort", "ot_data_load", "ot_l2", "ot_train", "benefit"];
  const HUB_ROWS = ["plat_run", "perm_up", "rt_rep", "env", "mon", "plat_team", "gov", "comp", "lic"];

  const zeros = () => new Array(MONTHS + 1).fill(0);
  const sum = (arr) => arr.reduce((a, b) => a + b, 0);
  const div = (a, b) => (b ? a / b : 0);
  const isActive = (t) => (t.active === undefined ? 1 : t.active) === 1;

  function buildPriceBook(rows) {
    const pb = {};
    for (const r of rows) {
      if (pb[r.id]) throw new Error("Duplicate price ID: " + r.id);
      pb[r.id] = r;
    }
    return pb;
  }

  function run(inp) {
    const k = inp.k === undefined ? 1 : inp.k;
    const valueK = inp.valueK === undefined ? 1 : inp.valueK;
    const org = inp.org, teams = inp.teams;
    const pb = buildPriceBook(inp.pricebook);

    const P = (key, kk) => {
      const p = inp.params[key];
      if (!p) throw new Error("Unknown parameter: " + key);
      return p.vals[kk === undefined ? k : kk];
    };
    const price = (pid, field) => {
      if (!pid) return 0;
      const r = pb[pid];
      if (!r) throw new Error("Unknown price ID: " + pid);   // never price a mistyped ID silently at zero
      return r[field || "p_in"];
    };

    function costPerOutcome(t) {
      const steps = t.agentic === "Yes" ? P("steps") : 1;
      const scale = (1 - t.ctx) * P("tok_mult") * P("retry") * steps;
      const tin = t.tok_in * scale, tout = t.tok_out * scale;
      const m = pb[t.model], c = pb[t.cheap];
      if (!m) throw new Error("Unknown price ID: " + t.model);
      if (!c) throw new Error("Unknown price ID: " + t.cheap);
      const pin = (1 - t.route) * m.p_in + t.route * c.p_in;
      const pout = (1 - t.route) * m.p_out + t.route * c.p_out;
      const fc = (1 - t.cached - t.cwrite) + t.cached * m.c_read + t.cwrite * m.c_write;
      const fb = 1 - t.async_ * (1 - m.batch);
      return (tin * pin * fc + tout * pout) / 1e6 * fb * t.resid;
    }

    function ramp(t, m) {
      if (m < t.start) return 0;
      const x = Math.min(1, Math.max(0, (m - t.start + 1) / t.ramp));
      return t.curve === "S" ? x * x * (3 - 2 * x) : x;
    }

    function teamRows(t) {
      const hz = org.horizon, pd = org.pd_rate;
      const hourly = pd / org.hours_day;
      const cpo = costPerOutcome(t);
      const buy = t.buy;
      const seatFlag = buy === "Seat" || buy === "Seat + usage";
      const hasVendorPrice = !!t.unit_price;
      const vendor = buy === "Per-unit" && hasVendorPrice;
      const api = buy === "Seat + usage" || (buy === "Per-unit" && !hasVendorPrice) || buy === "Committed capacity";
      const std = price(t.seat_std), prem = price(t.seat_prem);
      const rows = {};
      for (const n of TEAM_ROWS) rows[n] = zeros();
      const interval = Math.max(1, Math.round(P("mig_int")));
      if (!isActive(t)) return { rows, cpo };
      for (let m = 1; m <= MONTHS; m++) {
        const h = m <= hz ? 1 : 0;
        const st = m >= t.start;
        const x = ramp(t, m);
        const lic = st ? t.licensed : 0;
        const act = lic * t.plateau * x;
        const out = t.basis === "per user" ? act * t.o_user : t.direct * x;
        rows.ramp[m] = x; rows.lic[m] = lic; rows.act[m] = act; rows.out[m] = out;
        rows.seat[m] = h * (seatFlag ? 1 : 0) * lic * ((1 - t.prem_share) * std + t.prem_share * prem);
        let tok;
        if (buy === "Seat + usage") {
          const oRest = t.o_user / ((1 - t.top_share) + t.top_share * t.top_mult);
          const oTop = t.top_mult * oRest;
          tok = act * ((1 - t.top_share) * Math.max(0, oRest * cpo - t.allow) + t.top_share * Math.max(0, oTop * cpo - t.allow));
        } else if (buy === "Per-unit" && !vendor) {
          tok = out * cpo;
        } else {
          tok = 0;
        }
        rows.tokens[m] = h * tok;
        rows.vendor[m] = h * (vendor ? out * price(t.unit_price) : 0);
        rows.tools[m] = h * (api ? out * (t.tool_calls * price(t.tool_price) / 1000 + t.guard_units * price(t.guard_price) / 1000) : 0);
        rows.cap[m] = h * ((buy === "Committed capacity" && st) ? t.cap_cost : 0);
        let dp = 0;
        if (st && t.own_index) {
          dp = (t.ndocs * P("change_rate") * t.pages * price(t.parse_price)
            + t.ndocs * P("change_rate") * t.emb_tok * price(t.emb_price) / 1e6
            + price(t.plan_price) + t.gb * price(t.store_price) + out * t.read_units * price(t.read_price) / 1e6);
        }
        rows.data_price[m] = h * dp;
        rows.data_effort[m] = h * (st ? t.nsrc * P("conn_pd") * pd * P("conn_up") / 12 : 0);
        rows.run_effort[m] = h * (st ? (P("evalcases") * P("eval_min") / 60 * hourly + P("maint") / 12 * P("int_pd") * pd
          + act / 1000 * P("tickets") * P("tkt_hours") * hourly) : 0);
        const ev = (m > t.start && (m - t.start) % interval === 0) ? 1 : 0;
        rows.migration[m] = h * ev * (P("mig_pd") + P("eval_rerun") * P("eval_pd")) * pd;
        rows.review[m] = h * out * Math.min(1, t.review * P("rev_mult")) * P("rev_min") / 60 * t.rev_rate;
        const fte = (m - t.start) < 6 ? P("cm_ramp") : P("cm_after");
        rows.cm[m] = h * (st ? (lic / 1000) * fte * pd * org.work_days / 12 : 0);
        rows.benefit[m] = h * out * t.min_saved / 60 * t.b_rate * P("realise", valueK) * t.accept;
      }
      rows.ot_data_effort[0] = (t.nsrc * P("src_pd") + t.ndocs / 100000 * P("clean_pd") + t.nsrc * P("conn_pd")) * pd;
      rows.ot_data_load[0] = t.own_index * (t.ndocs * t.pages * price(t.parse_price) + t.ndocs * t.emb_tok * price(t.emb_price) / 1e6);
      rows.ot_l2[0] = (P("int_pd") + P("eval_pd")) * pd;
      rows.ot_train[0] = t.licensed * t.plateau * P("train_hours") * hourly;
      return { rows, cpo };
    }

    function hubRows(trows) {
      const hz = org.horizon, pd = org.pd_rate, wd = org.work_days;
      const nT = teams.filter(isActive).length;
      const srcs = sum(teams.filter(isActive).map((t) => t.nsrc));
      const ot = {
        plat_ot: P("plat_pd") * pd, perm_ot: srcs * P("perm_pd") * pd,
        rev_ot: (nT * P("rev_uc_pd") + P("rev_once_pd")) * pd, rt_ot: nT * P("rt_pd") * pd,
      };
      const rows = {};
      for (const n of HUB_ROWS) rows[n] = zeros();
      for (let m = 1; m <= MONTHS; m++) {
        const h = m <= hz ? 1 : 0;
        const sumo = sum(trows.map((r) => r.out[m]));
        rows.plat_run[m] = h * ot.plat_ot * P("plat_run") / 12;
        rows.perm_up[m] = h * ot.perm_ot * P("perm_up") / 12;
        rows.rt_rep[m] = h * ot.rt_ot * P("rt_rep") / 12;
        rows.env[m] = h * P("env_month");
        rows.mon[m] = h * (price("PL_LANGFUSE_PRO") + Math.max(0, sumo * org.obs_per_out - LANGFUSE_INCLUDED) / 100000 * price("U_LANGFUSE_OVER"));
        rows.plat_team[m] = h * P("plat_fte") * pd * wd / 12;
        rows.gov[m] = h * P("gov_fte") * pd * wd / 12;
        rows.comp[m] = h * P("comp_year") / 12;
        rows.lic[m] = h * P("lic_year") / 12;
      }
      return { ot, rows };
    }

    const tr = [], cpo = [];
    for (const t of teams) {
      const r = teamRows(t);
      tr.push(r.rows);
      cpo.push(r.cpo);
    }
    const hub = hubRows(tr);
    const hot = hub.ot, hrows = hub.rows;
    const res = { cpo, teams: [], org };
    const hubRawOt = sum(Object.values(hot));
    const hubRawM = [];
    for (let m = 0; m <= MONTHS; m++) hubRawM.push(sum(HUB_ROWS.map((n) => hrows[n][m])));
    const hubRawTotal = hubRawOt + sum(hubRawM);
    const flags = teams.map((t) => (isActive(t) ? 1 : 0));
    const nT = sum(flags);
    const fedfac = nT * P("fed_dup");
    const effHub = hubRawTotal * (org.shape === "Federated" ? fedfac : 1);
    const hs = (arr) => sum(arr.slice(1, org.horizon + 1));    // state rows are not masked: total only the horizon
    const outs = tr.map((r) => hs(r.out));
    const lics = teams.map((t, i) => t.licensed * flags[i]);
    const rule = org.alloc;
    const shares = {
      "Usage-proportional": outs.map((o) => div(o, sum(outs))),
      "Headcount proxy": lics.map((l) => div(l, sum(lics))),
      "Even split": flags.map((f) => div(f, nT)),
      "Central budget": teams.map(() => 0),
    };
    if (!shares[rule]) throw new Error("Unknown allocation rule: " + rule);
    const share = shares[rule];
    let alloc, unalloc;
    if (org.shape === "Federated") {
      alloc = flags.map((f) => hubRawTotal * P("fed_dup") * f);
      unalloc = 0;
    } else {
      alloc = share.map((s) => hubRawTotal * s);
      unalloc = rule === "Central budget" ? hubRawTotal : 0;
    }
    const layers = { 1: 0, 2: 0, 3: 0, 4: 0, 5: 0 };
    const byTag = { A: 0, S: 0, R: 0, E: 0 };
    const comp = { benefit: 0, tokens: 0, vol: 0, review: 0, effort: 0, cost: 0 };
    tr.forEach((r, i) => {
      const direct = {};
      for (const n of Object.keys(TAG)) direct[n] = sum(r[n]);
      const dTot = sum(Object.values(direct));
      const ben = sum(r.benefit);
      const f = div(alloc[i], hubRawTotal);
      let cum = 0, pb2 = null;
      for (let m = 0; m <= org.horizon; m++) {
        const dm = sum(Object.keys(TAG).map((n) => r[n][m]));
        const net = r.benefit[m] - dm - f * (m === 0 ? hubRawOt : hubRawM[m]);
        cum += net;
        if (m >= 1 && pb2 === null && cum >= 0) pb2 = m;
      }
      const act = hs(r.act);
      res.teams.push({
        direct, direct_total: dTot, alloc: alloc[i], benefit: ben, outcomes: outs[i], active_months: act,
        net: ben - dTot - alloc[i], payback: pb2,
        cost_per_outcome: outs[i] ? (dTot + alloc[i]) / outs[i] : null,
        cpa_month: teams[i].basis === "per user" ? (act ? (dTot + alloc[i]) / act : 0) : null,
      });
      for (const n of Object.keys(TAG)) {
        layers[LAYER[n]] += direct[n];
        byTag[TAG[n]] += direct[n];
      }
      comp.benefit += ben;
      comp.tokens += direct.tokens;
      comp.review += direct.review;
      comp.vol += direct.tokens + direct.vendor + direct.tools + direct.review;
      comp.effort += sum(Object.keys(TAG).filter((n) => TAG[n] === "S").map((n) => direct[n])) + direct.migration;
    });
    const pu = teams.map((t, i) => i).filter((i) => teams[i].basis === "per user");
    const puAct = sum(pu.map((i) => res.teams[i].active_months));
    res.cpa_ent = puAct ? sum(pu.map((i) => res.teams[i].direct_total + res.teams[i].alloc)) / puAct : 0;
    const fm = org.shape === "Federated" ? fedfac : 1;
    const hubTot = {};
    for (const n of Object.keys(hot)) hubTot[n] = hot[n];
    for (const n of Object.keys(hrows)) hubTot[n] = sum(hrows[n]);
    for (const [n, v] of Object.entries(hubTot)) {
      layers[HUB_LAYER[n]] += v * fm;
      byTag[HUB_TAG[n]] += v * fm;
      if (HUB_TAG[n] === "S" || n === "gov") comp.effort += v * fm;   // cost governance is FTE x person-day rate
    }
    const totalCost = sum(Object.values(layers));
    comp.cost = totalCost;
    Object.assign(res, { layers, by_tag: byTag, comp, total_cost: totalCost, alloc, unalloc, hub_raw_total: hubRawTotal,
      eff_hub: effHub, net: comp.benefit - totalCost, hub_rows: hrows, hub_ot: hot, team_rows: tr });
    // enterprise payback and the cumulative net curve (month 0 = one-time costs)
    let cum = 0, pb3 = null;
    const cumSeries = [];
    for (let m = 0; m <= org.horizon; m++) {
      const ben = sum(tr.map((r) => r.benefit[m]));
      const dm = sum(tr.map((r) => sum(Object.keys(TAG).map((n) => r[n][m]))));
      const hm = (m === 0 ? hubRawOt : hubRawM[m]) * fm;
      cum += ben - dm - hm;
      cumSeries.push(cum);
      if (m >= 1 && pb3 === null && cum >= 0) pb3 = m;
    }
    res.payback = pb3;
    res.cum_series = cumSeries;
    // monthly run cost in the last horizon month (recurring lines only; one-time costs sit in month 0)
    const last = org.horizon;
    res.run_rate_last = sum(tr.map((r) => sum(Object.keys(TAG).map((n) => r[n][last])))) + sum(HUB_ROWS.map((n) => hrows[n][last])) * fm;
    return res;
  }

  return { run, MONTHS, TAG, LAYER };
}));
