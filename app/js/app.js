// SPDX-License-Identifier: Apache-2.0
// Quick-estimate screen. Everything runs in the browser; nothing is sent anywhere.
(function () {
  "use strict";
  const D = window.DATA, Eng = window.Engine;

  // ---------- small helpers
  const clone = (o) => JSON.parse(JSON.stringify(o));
  function el(tag, attrs, kids) {
    const n = document.createElement(tag);
    let value;
    for (const k in (attrs || {})) {
      const v = attrs[k];
      if (v === null || v === undefined || v === false) continue;
      if (k === "class") n.className = v;
      else if (k === "text") n.textContent = v;
      else if (k === "value") value = v;
      else if (k.slice(0, 2) === "on") n.addEventListener(k.slice(2), v);
      else n.setAttribute(k, v === true ? "" : v);
    }
    (kids || []).forEach((c) => {
      if (c === null || c === undefined || c === false) return;
      n.appendChild(typeof c === "string" ? document.createTextNode(c) : c);
    });
    if (value !== undefined) n.value = value;
    return n;
  }
  const svgEl = (tag, attrs) => {
    const n = document.createElementNS("http://www.w3.org/2000/svg", tag);
    for (const k in attrs) n.setAttribute(k, attrs[k]);
    return n;
  };
  function usd(v) {
    if (v === null || v === undefined || !isFinite(v)) return "n/a";
    const a = Math.abs(v), sign = v < 0 ? "−" : "";
    if (a >= 1e6) return sign + "$" + (a / 1e6).toFixed(2) + "M";
    if (a >= 1e3) return sign + "$" + (a / 1e3).toFixed(1) + "K";
    return sign + "$" + a.toFixed(a < 10 ? 2 : 0);
  }
  const signedUsd = (v) => (v > 0 ? "+" : "") + usd(v);
  const pct = (v) => Math.round(v * 100) + "%";
  const num = (v) => (typeof v === "number" ? (Math.round(v * 1e4) / 1e4).toLocaleString("en-US") : String(v));
  const teamName = (t, i) => (t.name && t.name.trim()) || "Team " + (i + 1);
  const paybackText = (pb, hz) => (pb === null ? "Not within " + hz + " months" : "Month " + pb);

  // ---------- state
  let uid = 0;
  const state = { orgName: "", org: {}, entered: {}, teams: [], k: 1, valueK: 1, message: "", uploadReport: null };
  const MINS = { ramp: 1, start: 1, horizon: 1, hours_day: 1, work_days: 1 };
  const PRIMARY = new Set(["buy", "model", "licensed", "plateau", "basis", "o_user", "direct", "min_saved"]);
  const GROUPS = [
    ["Seats, vendor prices and capacity", ["seat_std", "seat_prem", "prem_share", "allow", "top_share", "top_mult", "unit_price", "cap_cost"]],
    ["Adoption ramp", ["start", "ramp", "curve"]],
    ["Models and tokens", ["cheap", "route", "tok_in", "tok_out", "ctx", "cached", "cwrite", "async_", "resid", "agentic", "tool_calls", "tool_price", "guard_units", "guard_price"]],
    ["Human review", ["review", "rev_rate"]],
    ["Data readiness", ["nsrc", "ndocs", "pages", "parse_price", "emb_tok", "emb_price", "own_index", "gb", "read_units", "plan_price", "store_price", "read_price"]],
    ["Value", ["b_rate", "accept"]],
    ["Team", ["bu"]],
  ];
  const SHAPE_ALLOC = { "Centralized": "Central budget", "Federated": "Usage-proportional", "Hub-and-spoke": "Usage-proportional" };

  function decorate(t) {
    t._id = ++uid;
    t._edited = t._edited || {};
    t._open = !!t._open;
    return t;
  }
  const archCode = (t) => String(t.archetype || "A1").split(" ")[0];
  function newTeam(code) {
    const a = D.archetypes[code];
    return decorate(Object.assign(clone(a.preset), { name: "", bu: "", archetype: a.label, active: 1, licensed: 500 }));
  }
  function applyArchetype(t, code) {
    const a = D.archetypes[code];
    Object.assign(t, clone(a.preset), { archetype: a.label });
    t._edited = {};
  }
  function loadExample() {
    state.orgName = D.meta.org.name;
    state.org = {};
    ["shape", "alloc", "horizon", "pd_rate", "hours_day", "work_days", "obs_per_out"].forEach((k) => { state.org[k] = D.meta.org[k]; });
    state.entered = { env_month: 0, comp_year: 0, lic_year: 0 };
    state.teams = D.exampleTeams.map((t) => decorate(clone(t)));
    state.message = "The fictional example is loaded. Its numbers match the Excel workbook in the model folder.";
    state.uploadReport = null;
  }
  function startBlank() {
    loadExample();
    state.orgName = "Your organization";
    state.teams = [newTeam("A1")];
    state.message = "Blank start: one team with starter values. Replace the ones you know.";
  }

  // ---------- Excel template: download and upload
  const slug = (s) => (s || "organization").toLowerCase().replace(/[^a-z0-9]+/g, "-").replace(/^-+|-+$/g, "").slice(0, 60) || "organization";

  function downloadTemplate() {
    try {
      window.Template.download(state, D, slug(state.orgName) + "-ai-unit-economics-template.xlsx");
    } catch (e) {
      state.uploadReport = { errors: ["Could not build the template: " + e.message], warnings: [], applied: false };
      render();
    }
  }

  function mergeUpload(result) {
    state.orgName = result.orgName;
    state.org = result.org;
    state.entered = result.entered;
    state.teams = result.teams.map(({ team, edited }) => decorate(Object.assign(team, { _edited: edited })));
    state.message = "Loaded from an uploaded workbook: " + state.teams.length + " team" + (state.teams.length === 1 ? "" : "s") + ".";
  }

  function handleUploadedFile(file) {
    state.uploadReport = { errors: [], warnings: [], applied: false, loading: true };
    render();
    const fail = (e) => {
      state.uploadReport = { errors: ["Could not read this file: " + e.message + ". Make sure it is the .xlsx template downloaded from this calculator."], warnings: [], applied: false };
      render();
    };
    try {
      window.Template.readFile(file).then((sheets) => {
        const result = window.Template.parseAOA(sheets, D);
        if (result.errors.length) {
          state.uploadReport = { errors: result.errors, warnings: result.warnings, applied: false };
        } else {
          mergeUpload(result);
          state.uploadReport = { errors: [], warnings: result.warnings, applied: true, count: state.teams.length };
        }
        render();
      }).catch(fail);
    } catch (e) {
      fail(e);
    }
  }

  // ---------- engine input and results
  function engineInput(k, valueK) {
    const params = clone(D.params);
    for (const key of ["env_month", "comp_year", "lic_year"]) {
      const v = state.entered[key] || 0;
      params[key].vals = [v, v, v];
    }
    const teams = state.teams.map((t) => {
      const c = {};
      for (const key in t) if (key.charAt(0) !== "_") c[key] = t[key];
      return c;
    });
    return { k, valueK, org: Object.assign({}, state.org), teams, params, pricebook: D.pricebook };
  }

  // ---------- input controls
  function parseValue(key, m, raw) {
    let v = parseFloat(raw);
    if (!isFinite(v)) v = 0;
    if (m && m.kind === "percent") return Math.min(100, Math.max(0, v)) / 100;
    return Math.max(MINS[key] === undefined ? 0 : MINS[key], v);
  }
  const displayNumber = (m, v) => (m.kind === "percent" ? Math.round(v * 10000) / 100 : v);

  function priceHint(id) {
    const r = D.pricebook.find((x) => x.id === id);
    if (!r) return "";
    const price = r.kind === "Model" ? "$" + r.p_in + " in, $" + r.p_out + " out per million tokens" : "$" + r.p_in + " " + r.unit.replace(/^USD /, "");
    return price + ". Source " + r.src + ", dated " + D.meta.priceDate + ", grade A" + (r.status !== "standard" ? ", " + r.status + (r.to ? " until " + r.to : "") : "") + ".";
  }

  function teamControl(team, key, labelOverride) {
    const m = D.fields[key];
    const id = "t" + team._id + "-" + key;
    const structural = key === "buy" || key === "basis";
    const dot = el("span", { class: "dot" + (team._edited[key] ? " entered" : ""), title: team._edited[key] ? "You entered this value" : "Starter value (grade D) until you change it" });
    const unit = m.kind === "percent" ? "%" : (m.unit && m.kind === "number" ? m.unit : "");
    const label = el("label", { class: "f", for: id }, [el("span", { class: "name" }, [dot, labelOverride || m.label.replace(/ \(price book ID[^)]*\)/, "")])]);
    let input;
    const changed = (raw, live) => {
      let v;
      if (m.kind === "select" || m.kind === "price" || m.kind === "text") v = raw;
      else if (m.kind === "toggle") v = raw === "1" ? 1 : 0;
      else v = parseValue(key, m, raw);
      team[key] = v;
      team._edited[key] = true;
      dot.className = "dot entered";
      dot.title = "You entered this value";
      if (structural && !live) render();
      else update();
    };
    if (m.kind === "select") {
      input = el("select", { id, value: team[key], onchange: (e) => changed(e.target.value) }, m.options.map((o) => el("option", { value: o, text: o })));
    } else if (m.kind === "price") {
      const opts = D.pricebook.filter((r) => r.kind === m.priceKind).map((r) => el("option", { value: r.id, text: D.priceLabels[r.id] }));
      if (m.allowNone) opts.unshift(el("option", { value: "", text: "None: priced per token" }));
      input = el("select", { id, value: team[key], onchange: (e) => { changed(e.target.value); hint.textContent = priceHint(e.target.value); } }, opts);
    } else if (m.kind === "toggle") {
      input = el("select", { id, value: String(team[key]), onchange: (e) => changed(e.target.value) }, [el("option", { value: "1", text: "Yes" }), el("option", { value: "0", text: "No" })]);
    } else if (m.kind === "text") {
      input = el("input", { id, type: "text", value: team[key] === undefined ? "" : team[key], oninput: (e) => changed(e.target.value, true) });
    } else {
      input = el("input", { id, type: "number", step: "any", min: MINS[key] === undefined ? 0 : MINS[key], inputmode: "decimal", value: displayNumber(m, team[key]),
        oninput: (e) => changed(e.target.value, true) });
    }
    label.appendChild(input);
    if (unit) label.appendChild(el("span", { class: "unit", text: unit }));
    const hint = el("span", { class: "hint", text: m.kind === "price" ? priceHint(team[key]) : "" });
    if (m.kind === "price") label.appendChild(hint);
    return label;
  }

  function teamNotes(t) {
    const notes = [];
    const a = D.archetypes[archCode(t)];
    if (a && a.note) notes.push(["note", a.note]);
    if (t.cached + t.cwrite > 1) notes.push(["warn", "Cached share plus cache-write share is above 100% of input."]);
    if (t.buy === "Committed capacity" && !(t.cap_cost > 0)) notes.push(["warn", "Committed capacity needs a monthly cost. Until you enter one, the capacity line (CL-15) stays off and cost is understated."]);
    if (t.basis === "per user" && !(t.o_user > 0)) notes.push(["warn", "No usage yet: enter outcomes per active user per month."]);
    if (t.basis === "direct volume" && !(t.direct > 0)) notes.push(["warn", "No usage yet: enter outcomes per month at plateau."]);
    if (t.buy === "Seat + usage" && t.basis === "direct volume") notes.push(["warn", "Seat plus usage prices usage from outcomes per active user. Count usage per user for this buying model."]);
    if (t.start > state.org.horizon) notes.push(["warn", "This team launches after the horizon ends, so it adds no cost or benefit."]);
    return notes;
  }

  function teamCard(t, i) {
    const head = el("div", { class: "team-head" }, [
      el("label", { class: "f", for: "t" + t._id + "-name" }, [el("span", { class: "name", text: "Team name" }),
        el("input", { id: "t" + t._id + "-name", type: "text", value: t.name, placeholder: "Team " + (i + 1), oninput: (e) => { t.name = e.target.value; update(); } })]),
      el("label", { class: "f", for: "t" + t._id + "-arch" }, [el("span", { class: "name", text: "Team type" }),
        el("select", { id: "t" + t._id + "-arch", value: archCode(t), onchange: (e) => { applyArchetype(t, e.target.value); render(); } },
          Object.keys(D.archetypes).map((c) => el("option", { value: c, text: D.archetypes[c].label + (D.archetypes[c].placeholder ? " (placeholder usage)" : "") })))]),
      el("label", { class: "check" }, [el("input", { type: "checkbox", checked: t.active === 1 ? true : null, onchange: (e) => { t.active = e.target.checked ? 1 : 0; render(); } }), "Counted"]),
      state.teams.length > 1 ? el("button", { type: "button", onclick: () => { state.teams.splice(i, 1); render(); } }, ["Remove"]) : el("span"),
    ]);
    const keys = ["buy", "model", "licensed", "plateau", "basis", t.basis === "per user" ? "o_user" : "direct", "min_saved"];
    if (t.buy === "Committed capacity") keys.push("cap_cost");
    const primary = el("div", { class: "grid" }, keys.map((k) => teamControl(t, k, k === "direct" ? "Outcomes per month at plateau" : null)));
    const card = el("article", { class: "team" + (t.active === 1 ? "" : " off") }, [head]);
    const notesEl = el("div");
    const fillNotes = () => notesEl.replaceChildren(...teamNotes(t).map(([cls, text]) => el("p", { class: cls }, [text])));
    fillNotes();
    noteRefreshers.push(fillNotes);
    card.appendChild(notesEl);
    card.appendChild(primary);
    const more = el("div", { class: "more" });
    if (t._open) {
      const seen = new Set();
      GROUPS.forEach(([title, fields]) => {
        const shown = fields.filter((f) => D.fields[f] && !PRIMARY.has(f) && !(f === "cap_cost" && t.buy === "Committed capacity"));
        shown.forEach((f) => seen.add(f));
        if (!shown.length) return;
        more.appendChild(el("h3", { text: title }));
        more.appendChild(el("div", { class: "grid" }, shown.map((f) => teamControl(t, f))));
      });
    }
    card.appendChild(el("div", { class: "actions" }, [el("button", { type: "button", "aria-expanded": t._open ? "true" : "false", onclick: () => { t._open = !t._open; render(); } }, [t._open ? "Hide more inputs" : "More inputs for this team"])]));
    card.appendChild(more);
    return card;
  }

  function orgControl(key, opts) {
    const meta = D.orgFields[key];
    const id = "org-" + key;
    let input;
    if (opts && opts.options) {
      input = el("select", { id, value: state.org[key], onchange: (e) => { state.org[key] = e.target.value; if (key === "shape") state.org.alloc = SHAPE_ALLOC[e.target.value]; render(); } },
        opts.options.map((o) => el("option", { value: o, text: o })));
    } else {
      input = el("input", { id, type: "number", step: "any", min: MINS[key] === undefined ? 0 : MINS[key], max: key === "horizon" ? D.meta.horizonMax : null, value: state.org[key],
        oninput: (e) => { let v = parseValue(key, null, e.target.value); if (key === "horizon") v = Math.min(D.meta.horizonMax, Math.round(v)); state.org[key] = v; update(); } });
    }
    return el("label", { class: "f", for: id }, [el("span", { class: "name", text: opts && opts.label ? opts.label : meta.label }), input,
      opts && opts.unit ? el("span", { class: "unit", text: opts.unit }) : null]);
  }

  let noteRefreshers = [];
  function renderInputs() {
    const root = document.getElementById("inputs");
    root.replaceChildren();
    noteRefreshers = [];
    const org = el("div", { class: "panel" }, [
      el("h2", { text: "Your organization" }),
      el("p", { class: "sub", text: "Shape and horizon change who pays for shared costs and how far ahead the estimate looks." }),
      el("div", { class: "row" }, [
        el("label", { class: "f", for: "orgname" }, [el("span", { class: "name", text: "Organization name" }), el("input", { id: "orgname", type: "text", value: state.orgName, oninput: (e) => { state.orgName = e.target.value; update(); } })]),
        orgControl("shape", { options: ["Centralized", "Federated", "Hub-and-spoke"], label: "Org shape" }),
        state.org.shape === "Federated" ? null : orgControl("alloc", { options: ["Usage-proportional", "Headcount proxy", "Even split", "Central budget"], label: "Shared cost allocation" }),
        orgControl("horizon", { label: "Horizon", unit: "months, up to " + D.meta.horizonMax }),
      ]),
      state.org.shape === "Federated" ? el("p", { class: "hint", text: "Federated: each unit runs its own platform, so shared costs are not split by a rule. Duplication is a scenario parameter." }) : null,
      el("div", { class: "actions" }, [
        el("button", { type: "button", onclick: () => { loadExample(); render(); } }, ["Load the fictional example"]),
        el("button", { type: "button", onclick: () => { startBlank(); render(); } }, ["Start blank"]),
      ]),
      state.message ? el("p", { class: "note", text: state.message }) : null,
    ]);
    root.appendChild(org);

    const teams = el("div", { class: "panel" }, [
      el("h2", { text: "Your teams" }),
      el("p", { class: "sub", text: "One team per business unit. Pick a team type and every other input starts from its starter value. A hollow dot means the value is still a starter (grade D); a filled dot means you entered it." }),
    ]);
    state.teams.forEach((t, i) => teams.appendChild(teamCard(t, i)));
    const addSel = el("select", { id: "add-arch", "aria-label": "Team type for the new team" }, Object.keys(D.archetypes).map((c) => el("option", { value: c, text: D.archetypes[c].label })));
    teams.appendChild(el("div", { class: "actions" }, [addSel, el("button", { type: "button", onclick: () => { state.teams.push(newTeam(addSel.value)); render(); } }, ["Add team"])]));
    root.appendChild(teams);

    const costs = el("div", { class: "panel" }, [
      el("h2", { text: "Organization-wide costs you may already know" }),
      el("p", { class: "sub", text: "These four costs have no starter value, so they are off until you enter them and the estimate is understated without them. Committed capacity is entered on a team." }),
      el("div", { class: "row" }, ["env_month", "comp_year", "lic_year"].map((key) => el("label", { class: "f", for: "ent-" + key }, [
        el("span", { class: "name", text: D.params[key].desc + " (" + D.params[key].line + ")" }),
        el("input", { id: "ent-" + key, type: "number", min: 0, step: "any", inputmode: "decimal", value: state.entered[key] || 0, oninput: (e) => { state.entered[key] = parseValue(key, null, e.target.value); update(); } }),
        el("span", { class: "unit", text: D.params[key].unit }),
      ]))),
      el("details", { class: "more" }, [el("summary", { class: "small muted", text: "Rates used for people costs" }),
        el("div", { class: "grid" }, ["pd_rate", "hours_day", "work_days", "obs_per_out"].map((k) => orgControl(k, { unit: D.orgFields[k].unit }))),
        el("p", { class: "hint", text: "Starter values, grade D. The person-day rate has a public cross-check (evidence LAB-02)." })]),
    ]);
    root.appendChild(costs);
  }

  // ---------- results
  function seg(options, current, onpick, label) {
    return el("div", { class: "seg", role: "group", "aria-label": label }, options.map(([v, text]) => el("button", { type: "button", "aria-pressed": String(v === current), onclick: () => onpick(v) }, [text])));
  }

  function lineChart(series, payback) {
    const W = 600, H = 190, L = 56, R = 10, T = 10, B = 24;
    const min = Math.min(0, ...series), max = Math.max(0, ...series), span = max - min || 1;
    const x = (i) => L + (W - L - R) * i / Math.max(1, series.length - 1);
    const y = (v) => T + (H - T - B) * (1 - (v - min) / span);
    const svg = svgEl("svg", { viewBox: "0 0 " + W + " " + H, class: "chart", role: "img", "aria-label": "Cumulative net value by month. " + (payback === null ? "It does not turn positive within the horizon." : "It turns positive in month " + payback + ".") });
    svg.appendChild(svgEl("line", { x1: L, x2: W - R, y1: y(0), y2: y(0), stroke: "currentColor", "stroke-opacity": "0.4", "stroke-dasharray": "4 3" }));
    svg.appendChild(svgEl("polyline", { points: series.map((v, i) => x(i).toFixed(1) + "," + y(v).toFixed(1)).join(" "), fill: "none", stroke: "var(--accent)", "stroke-width": "2" }));
    [[max, T + 4], [min, H - B]].forEach(([v, yy]) => { const t = svgEl("text", { x: L - 6, y: yy, "text-anchor": "end" }); t.textContent = usd(v); svg.appendChild(t); });
    const z = svgEl("text", { x: L - 6, y: y(0) + 4, "text-anchor": "end" }); z.textContent = "$0"; if (min < 0 && max > 0) svg.appendChild(z);
    [0, Math.round((series.length - 1) / 2), series.length - 1].forEach((m) => { const t = svgEl("text", { x: x(m), y: H - 6, "text-anchor": m === 0 ? "start" : m === series.length - 1 ? "end" : "middle" }); t.textContent = "Month " + m; svg.appendChild(t); });
    if (payback !== null) {
      svg.appendChild(svgEl("circle", { cx: x(payback), cy: y(series[payback]), r: 4, fill: "var(--good)" }));
      const t = svgEl("text", { x: x(payback) + 6, y: y(series[payback]) - 6 }); t.textContent = "Payback: month " + payback; svg.appendChild(t);
    }
    return svg;
  }

  function offLines() {
    const off = [];
    if (!(state.entered.env_month > 0)) off.push(["CL-14", "Environments and base cloud infrastructure", "Enter it under organization-wide costs."]);
    if (!state.teams.some((t) => t.active === 1 && t.buy === "Committed capacity" && t.cap_cost > 0)) off.push(["CL-15", "Committed capacity", "Choose Committed capacity for a team and enter its monthly cost."]);
    if (!(state.entered.comp_year > 0)) off.push(["CL-31", "Compliance audit and governance", "Enter it under organization-wide costs."]);
    if (!(state.entered.lic_year > 0)) off.push(["CL-32", "Platform and vendor licences", "Enter it under organization-wide costs."]);
    return off;
  }

  const LAYER_NAMES = { 1: "Data readiness", 2: "Setup and infrastructure", 3: "Inference and usage", 4: "Run and maintenance", 5: "People and change" };

  function renderResults(res) {
    const root = document.getElementById("results");
    root.replaceChildren();
    const { runs, r } = res;
    const hz = state.org.horizon;
    const active = state.teams.map((t, i) => i).filter((i) => state.teams[i].active === 1);
    const outcomes = active.reduce((a, i) => a + r.teams[i].outcomes, 0);
    const realise = D.params.realise.vals;

    // controls
    root.appendChild(el("div", { class: "panel" }, [
      el("h2", { text: "Scenario" }),
      el("div", { class: "row", style: "margin-top:8px" }, [
        el("div", {}, [el("p", { class: "small muted", text: "Cost scenario" }), seg([[0, "Low-cost"], [1, "Base"], [2, "High-cost (stress)"]], state.k, (v) => { state.k = v; update(); }, "Cost scenario")]),
        el("div", {}, [el("p", { class: "small muted", text: "Realisation share of time saved" }), seg([[0, pct(realise[0])], [1, pct(realise[1])], [2, pct(realise[2])]], state.valueK, (v) => { state.valueK = v; update(); }, "Realisation share")]),
      ]),
      el("p", { class: "hint", style: "margin-top:8px", text: "High-cost sets every parameter to its high value at once, so it is a stress case, not a forecast. Realisation share is how much self-reported time saved counts as value. No evidence converts one to the other (gap G5), so it is an assumption (grade D)." }),
    ]));

    // headline detail cards
    const cpa = r.cpa_ent;
    root.appendChild(el("div", { class: "panel" }, [
      el("h2", { text: "Result over " + hz + " months" }),
      el("div", { class: "cards", style: "margin-top:10px" }, [
        card("Cost per outcome", outcomes ? usd(r.total_cost / outcomes) : "n/a"),
        card("Benefit per outcome", outcomes ? usd(r.comp.benefit / outcomes) : "n/a"),
        card("Cost per active user per month", cpa ? usd(cpa) : "n/a"),
        card("Monthly run cost at month " + hz, usd(r.run_rate_last)),
        card("Shared costs (platform, governance, monitoring)", usd(r.eff_hub) + " (" + pct(r.eff_hub / (r.total_cost || 1)) + ")"),
      ]),
      r.eff_hub / (r.total_cost || 1) > 0.4 ? el("p", { class: "note", style: "margin-top:8px", text: "Shared costs are a large part of this total. They stay roughly fixed however many teams or users there are, so a small program carries them on few users." }) : null,
      el("p", { class: "hint", style: "margin-top:8px", text: "Cost per active user counts per-user teams only. Time saved is valued in USD and is not discounted. Effective dates on prices are recorded but not applied." }),
      r.unalloc > 0 ? el("p", { class: "note", text: "Shared cost not allocated to teams (central budget): " + usd(r.unalloc) + ". It is included in the total." }) : null,
    ]));

    // scenario range
    root.appendChild(el("div", { class: "panel" }, [
      el("h2", { text: "Range across cost scenarios" }),
      el("div", { class: "scroll" }, [el("table", {}, [
        el("thead", {}, [el("tr", {}, ["", "Low-cost", "Base", "High-cost (stress)"].map((h, i) => el("th", { class: i ? "num" : "", text: h })))]),
        el("tbody", {}, [
          el("tr", {}, [el("td", { text: "Total cost" })].concat(runs.map((x) => el("td", { class: "num", text: usd(x.total_cost) })))),
          el("tr", {}, [el("td", { text: "Net value" })].concat(runs.map((x) => el("td", { class: "num " + (x.net >= 0 ? "pos" : "neg"), text: signedUsd(x.net) })))),
          el("tr", {}, [el("td", { text: "Payback" })].concat(runs.map((x) => el("td", { class: "num", text: x.payback === null ? "none" : "Month " + x.payback })))),
        ]),
      ])]),
      el("p", { class: "hint", style: "margin-top:6px", text: "At realisation share " + pct(realise[state.valueK]) + "." }),
    ]));

    // cost by layer
    const maxLayer = Math.max(...[1, 2, 3, 4, 5].map((n) => r.layers[n]), 1);
    const layerPanel = el("div", { class: "panel bars" }, [el("h2", { text: "Cost by layer" })]);
    [1, 2, 3, 4, 5].forEach((n) => layerPanel.appendChild(el("div", { class: "b" }, [
      el("span", { class: "n", text: LAYER_NAMES[n] }),
      el("span", { class: "t" }, [el("i", { style: "left:0;width:" + (r.layers[n] / maxLayer * 100).toFixed(1) + "%;background:var(--layer)" })]),
      el("span", { class: "x", text: usd(r.layers[n]) }),
    ])));
    layerPanel.appendChild(el("p", { class: "hint", text: "Shared platform, governance and review costs sit in the layers they belong to. Teams see their allocated share in the team view." }));
    root.appendChild(layerPanel);

    // by team
    const nets = active.map((i) => r.teams[i].net);
    const maxNeg = Math.max(0, ...nets.map((v) => -v)), maxPos = Math.max(0, ...nets), range = (maxNeg + maxPos) || 1;
    const zero = maxNeg / range * 100;
    const teamPanel = el("div", { class: "panel bars" }, [el("h2", { text: "Net value by team" }),
      el("p", { class: "sub", text: "Cost includes the team's allocated share of shared costs." })]);
    active.forEach((i) => {
      const t = r.teams[i], v = t.net, w = Math.abs(v) / range * 100;
      teamPanel.appendChild(el("div", { class: "b" }, [
        el("span", { class: "n" }, [teamName(state.teams[i], i), el("small", { text: usd(t.direct_total + t.alloc) + " cost" + (t.cost_per_outcome !== null ? ", " + usd(t.cost_per_outcome) + " per outcome" : "") + ". Payback: " + (t.payback === null ? "none" : "month " + t.payback) })]),
        el("span", { class: "t" }, [el("u", { style: "left:" + zero.toFixed(1) + "%" }),
          el("i", { style: "left:" + (v >= 0 ? zero : zero - w).toFixed(1) + "%;width:" + w.toFixed(1) + "%;background:" + (v >= 0 ? "var(--a)" : "var(--bad)") })]),
        el("span", { class: "x " + (v >= 0 ? "pos" : "neg"), text: signedUsd(v) }),
      ]));
    });
    root.appendChild(teamPanel);

    // cumulative chart
    root.appendChild(el("div", { class: "panel" }, [el("h2", { text: "Cumulative net value" }),
      el("p", { class: "sub", text: "Month 0 holds the one-time costs. The line turns positive at payback." }), lineChart(r.cum_series, r.payback)]));

    // evidence
    const tags = [["A", "Dated provider prices", "var(--a)"], ["R", "Ranges with a warning", "var(--r)"], ["S", "Starter values (grade D)", "var(--s)"], ["E", "Enterprise-entered", "var(--e)"]];
    const total = r.total_cost || 1;
    root.appendChild(el("div", { class: "panel" }, [
      el("h2", { text: "What the cost rests on" }),
      el("div", { class: "stack", style: "margin-top:10px", role: "img", "aria-label": tags.map(([k, n]) => n + " " + pct(r.by_tag[k] / total)).join(", ") },
        tags.map(([k, , c]) => el("span", { style: "width:" + (r.by_tag[k] / total * 100).toFixed(2) + "%;background:" + c }))),
      el("div", { class: "legend" }, tags.map(([k, n, c]) => el("span", {}, [el("i", { style: "background:" + c }), n + " " + pct(r.by_tag[k] / total)]))),
      el("p", { class: "hint", style: "margin-top:8px", text: "Counted by cost line. A line is a dated price when its unit price comes from a provider's page (fetched " + D.meta.priceDate + "); the volumes multiplied by that price, such as users and tokens per outcome, are still your assumptions." }),
    ]));

    // kill number
    const b = r.comp.benefit;
    let kill;
    if (b <= 0) kill = "No benefit yet. Enter minutes saved per outcome to see how much margin the case has.";
    else if (r.net >= 0) kill = "Benefit can fall " + pct(1 - r.total_cost / b) + " before net value reaches zero. Realisation share of time saved and minutes saved per outcome both move benefit one for one, and both are assumptions (grade D).";
    else kill = "Net value is negative. Benefit would have to rise " + pct(r.total_cost / b - 1) + " to break even.";
    root.appendChild(el("div", { class: "panel" }, [el("h2", { text: "What would break the case" }), el("p", { class: "warn", style: "margin-top:8px", text: kill })]));

    // firm up
    const off = offLines();
    const firm = el("div", { class: "panel" }, [
      el("h2", { text: "Firm up this estimate" }),
      el("p", { class: "sub", text: pct(r.by_tag.S / total) + " of the cost still rests on starter values." }),
      off.length ? el("p", { class: "small", text: off.length + " cost line" + (off.length > 1 ? "s are" : " is") + " off until you enter " + (off.length > 1 ? "them" : "it") + ", so cost is understated:" }) : el("p", { class: "small", text: "All four enterprise-entered lines have a value." }),
      off.length ? el("ul", { class: "small", style: "margin:6px 0 0;padding-left:18px" }, off.map(([id, name, how]) => el("li", { text: name + " (" + id + "). " + how }))) : null,
    ]);
    const fileInput = el("input", { type: "file", accept: ".xlsx", class: "sr-only", "aria-label": "Upload a filled-in template",
      onchange: (e) => { if (e.target.files[0]) handleUploadedFile(e.target.files[0]); e.target.value = ""; } });
    firm.appendChild(el("div", { class: "actions" }, [
      el("button", { type: "button", onclick: downloadTemplate }, ["Download template, pre-filled"]),
      el("button", { type: "button", onclick: () => fileInput.click() }, ["Upload filled workbook"]),
      fileInput,
      el("a", { class: "btn", href: "../model/ai-unit-economics-v0.1.xlsx", download: "" }, ["Open the detailed workbook"]),
    ]));
    firm.appendChild(el("p", { class: "hint", style: "margin-top:6px", text: "The template is an .xlsx file with your current teams already filled in, plus a Read me sheet and a price book to copy IDs from. Nothing is sent anywhere: the file is built and read in your browser." }));
    const rep = state.uploadReport;
    if (rep) {
      if (rep.loading) {
        firm.appendChild(el("p", { class: "note", text: "Reading the file…" }));
      } else if (rep.errors.length) {
        firm.appendChild(el("div", { class: "err", style: "margin-top:10px" }, [
          el("p", { text: "Could not use this file. Nothing was changed. Fix these and upload it again:" }),
          el("ul", { style: "margin:6px 0 0;padding-left:18px" }, rep.errors.map((m) => el("li", { text: m }))),
        ]));
      } else {
        firm.appendChild(el("div", { class: "note", style: "margin-top:10px" }, [
          el("p", { text: "Loaded " + rep.count + " team" + (rep.count === 1 ? "" : "s") + " from the uploaded file." + (rep.warnings.length ? " " + rep.warnings.length + " note" + (rep.warnings.length === 1 ? "" : "s") + ":" : "") }),
          rep.warnings.length ? el("ul", { style: "margin:6px 0 0;padding-left:18px" }, rep.warnings.map((m) => el("li", { text: m }))) : null,
        ]));
      }
    }
    root.appendChild(firm);
  }

  function card(label, value) {
    return el("div", { class: "card" }, [el("div", { class: "l", text: label }), el("div", { class: "v", text: value })]);
  }

  function renderKpis(r) {
    const k = document.getElementById("kpis");
    k.replaceChildren();
    const hz = state.org.horizon;
    [["Total cost, " + hz + " months", usd(r.total_cost), ""], ["Benefit", usd(r.comp.benefit), ""], ["Net value", signedUsd(r.net), r.net >= 0 ? "pos" : "neg"], ["Payback", r.payback === null ? "None" : "Month " + r.payback, ""]]
      .forEach(([l, v, c]) => k.appendChild(el("div", { class: "kpi" }, [el("div", { class: "l", text: l }), el("div", { class: "v " + c, text: v })])));
    document.getElementById("live").textContent = "Total cost " + usd(r.total_cost) + ", net value " + signedUsd(r.net) + ", payback " + paybackText(r.payback, hz) + ".";
  }

  function renderEvidence() {
    const root = document.getElementById("evidence");
    root.replaceChildren();
    const price = (r) => (r.kind === "Model" ? "$" + r.p_in + " in / $" + r.p_out + " out" : "$" + r.p_in);
    const pbTable = el("table", {}, [
      el("thead", {}, [el("tr", {}, ["Product", "Price", "Unit", "Status", "Source", "Fetched"].map((h) => el("th", { text: h })))]),
      el("tbody", {}, D.pricebook.map((r) => el("tr", {}, [r.provider + " " + r.product, price(r), r.unit, r.status + (r.to ? " until " + r.to : ""), r.src, D.meta.priceDate].map((c) => el("td", { text: c }))))),
    ]);
    const parTable = el("table", {}, [
      el("thead", {}, [el("tr", {}, ["Parameter", "Unit", "Low", "Base", "High", "Grade", "Line", "Basis"].map((h, i) => el("th", { class: i > 1 && i < 5 ? "num" : "", text: h })))]),
      el("tbody", {}, Object.keys(D.params).map((k) => { const p = D.params[k]; return el("tr", {}, [p.desc, p.unit, num(p.vals[0]), num(p.vals[1]), num(p.vals[2]), p.grade, p.line, p.why].map((c, i) => el("td", { class: i > 1 && i < 5 ? "num" : "", text: c }))); })),
    ]);
    root.appendChild(el("div", { style: "grid-column: 1 / -1" }, [
      el("details", { class: "panel" }, [el("summary", { text: "Price book, dated " + D.meta.priceDate + " (grade A)" }),
        el("p", { class: "sub", style: "margin-top:8px", text: "Prices come from each provider's own page. Source IDs point to evidence/source-register.md in the repository. Prices change: re-check them before you rely on a number." }),
        el("div", { class: "scroll" }, [pbTable])]),
      el("details", { class: "panel" }, [el("summary", { text: "Scenario parameters and starter values" }),
        el("p", { class: "sub", style: "margin-top:8px", text: "Grade D means an assumption chosen to make the model run, not evidence. Low, base and high are the low-cost, base and high-cost scenario values." }),
        el("div", { class: "scroll" }, [parTable])]),
    ]));
  }

  // ---------- render loop
  let scheduled = false;
  function update() {
    if (scheduled) return;
    scheduled = true;
    setTimeout(() => { scheduled = false; recalc(); }, 0);
  }
  function recalc() {
    document.getElementById("orgline").textContent = (state.orgName || "Your organization") + ". Preview " + D.meta.version.split(" ")[0] + ". Prices dated " + D.meta.priceDate + ".";
    noteRefreshers.forEach((f) => f());
    try {
      const runs = [0, 1, 2].map((k) => Eng.run(engineInput(k, state.valueK)));
      renderKpis(runs[state.k]);
      renderResults({ runs, r: runs[state.k] });
    } catch (e) {
      document.getElementById("results").replaceChildren(el("div", { class: "err" }, ["Can't calculate yet: " + e.message]));
      document.getElementById("kpis").replaceChildren();
    }
  }
  function render() {
    const focusId = document.activeElement && document.activeElement.id;
    renderInputs();
    if (focusId) { const f = document.getElementById(focusId); if (f) f.focus(); }
    recalc();
  }

  loadExample();
  renderEvidence();
  render();
})();
