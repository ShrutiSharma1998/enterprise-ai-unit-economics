# SPDX-License-Identifier: Apache-2.0
"""Input sheets: Org, Params, PriceBook, Teams. Registers addresses in ADDR for the later builders."""
from datetime import date
from openpyxl.worksheet.datavalidation import DataValidation
from spec_data import ORG, PARAMS, PRICEBOOK, TEAMS, TEAM_FIELDS, FICTION, LANGFUSE_INCLUDED
from xl_helpers import put, widths, title, USD, USD2, USD4, NUM, NUM2, PCT, L

ADDR = {"org": {}, "param_row": {}, "team_row": {}, "team_cols": [], "derived_row": {}}
PB_FIRST, PB_LAST = 4, 3 + max(len(PRICEBOOK), 200)     # lookups cover 200 rows, so refresh rows added at the bottom are found
NT = len(TEAMS)
ADDR["team_cols"] = [L(3 + i) for i in range(NT)]
DKEYS = ["d_seat", "d_usage", "d_ptok", "d_vendor", "d_cap", "d_api", "v_seat", "v_unit", "p_in", "p_out", "f_cache", "f_batch",
         "o_rest", "o_top", "u_other", "v_parse", "v_emb", "v_plan", "v_store", "v_readp", "d_start", "d_lic"]


def pbv(idref, col):
    """Formula text: price-book lookup by ID. idref is a cell ref or a quoted literal."""
    return (f'IFERROR(INDEX(PriceBook!${col}${PB_FIRST}:${col}${PB_LAST},'
            f'MATCH({idref},PriceBook!$A${PB_FIRST}:$A${PB_LAST},0)),0)')


def org(key):
    return ADDR["org"][key]


def param(key, k):
    """Absolute address of a parameter for scenario k (0 low-cost, 1 base, 2 high-cost)."""
    return f"Params!${'DEF'[k]}${ADDR['param_row'][key]}"


def team(key, t):
    return f"Teams!${ADDR['team_cols'][t]}${ADDR['team_row'][key]}"


def derived(key, t):
    return f"Teams!${ADDR['team_cols'][t]}${ADDR['derived_row'][key]}"


def build_org(wb):
    ws = wb.create_sheet("Org")
    title(ws, "Organization inputs", "Blue text on pale yellow = input. Everything here is a fictional assumption (grade D) unless stated.")
    for i, h in enumerate(["Field", "Value", "Unit / options", "Label", "Source", "Grade"]):
        put(ws, f"{L(i + 1)}3", h, "head")
    r = 4
    for key, (lab, val, unit, label, src, grade) in ORG.items():
        put(ws, f"A{r}", lab)
        put(ws, f"B{r}", val, "input", NUM if isinstance(val, (int, float)) else None)
        put(ws, f"C{r}", unit, "note")
        put(ws, f"D{r}", label)
        put(ws, f"E{r}", src, "note")
        put(ws, f"F{r}", grade)
        ADDR["org"][key] = f"Org!$B${r}"
        r += 1
    r += 1
    put(ws, f"A{r}", "Derived", "sub")
    r += 1
    scen, valc = ADDR["org"]["scenario"].split("!")[1], ADDR["org"]["value_case"].split("!")[1]
    rows = [
        ("scen_idx", "Scenario index (1 low-cost, 2 base, 3 high-cost)", f'=MATCH({scen},{{"Low-cost","Base","High-cost"}},0)', NUM),
        ("val_idx", "Value-case index (1 low, 2 base, 3 high)", f'=MATCH({valc},{{"Low","Base","High"}},0)', NUM),
        ("nT", "Number of active teams", f"=SUM(Teams!{ADDR['team_cols'][0]}{4 + [k for k, _l, _u in TEAM_FIELDS].index('active')}:{ADDR['team_cols'][-1]}{4 + [k for k, _l, _u in TEAM_FIELDS].index('active')})", NUM),
        ("nBU", "Number of business units (v0.1: one team per unit)", "=B{nT}", NUM),
    ]
    for key, lab, f, fmt in rows:
        put(ws, f"A{r}", lab)
        ADDR["org"][key] = f"Org!$B${r}"
        if key == "nBU":
            f = f"=B{r - 1}"
        put(ws, f"B{r}", f, "calc", fmt)
        r += 1
    for key, opts in [("scenario", '"Low-cost,Base,High-cost"'), ("value_case", '"Low,Base,High"'),
                      ("shape", '"Centralized,Federated,Hub-and-spoke"'),
                      ("alloc", '"Usage-proportional,Headcount proxy,Even split,Central budget"')]:
        dv = DataValidation(type="list", formula1=opts, allow_blank=False)
        ws.add_data_validation(dv)
        dv.add(ADDR["org"][key].split("!")[1].replace("$", ""))
    widths(ws, {"A": 46, "B": 34, "C": 52, "D": 12, "E": 62, "F": 8})


def build_params(wb):
    ws = wb.create_sheet("Params")
    title(ws, "Scenario parameters (starter values)",
          "Grade D unless stated. Low, Base and High are the low-cost, base and high-cost values. Source: spec/starter-values.md. Every value is editable.")
    heads = ["Key", "Parameter", "Unit", "Low-cost", "Base", "High-cost (stress)", "Taxonomy line", "How it was built", "Label", "Source", "Grade"]
    for i, h in enumerate(heads):
        put(ws, f"{L(i + 1)}3", h, "head")
    r = 4
    for key, (desc, unit, lo, ba, hi, line, why, grade) in PARAMS.items():
        put(ws, f"A{r}", key, "note")
        put(ws, f"B{r}", desc)
        put(ws, f"C{r}", unit, "note")
        fmt = PCT if "share" in unit else (USD if unit.startswith("USD") else NUM2)
        for j, v in enumerate((lo, ba, hi)):
            put(ws, f"{'DEF'[j]}{r}", v, "input", fmt)
        put(ws, f"G{r}", line)
        put(ws, f"H{r}", why, "note")
        put(ws, f"I{r}", "assumed")
        put(ws, f"J{r}", "spec/starter-values.md (Claude, 2026-09-20)", "note")
        put(ws, f"K{r}", grade)
        ADDR["param_row"][key] = r
        r += 1
    widths(ws, {"A": 12, "B": 52, "C": 26, "D": 11, "E": 11, "F": 11, "G": 12, "H": 70, "I": 10, "J": 38, "K": 7})
    ws.freeze_panes = "D4"


def build_pricebook(wb):
    ws = wb.create_sheet("PriceBook")
    title(ws, "Price book (dated primary prices, grade A)",
          "Fetched 2026-09-20 from each provider's own page (see evidence/source-register.md). 'Effective from' is the first date the price was seen. Confirm on the page before use. Model names are as extracted. Refresh: add a new row with a NEW unique ID, keep the old row, never overwrite (adoption/price-book-refresh.md). Dates and status are recorded, not applied in calculations.")
    heads = ["ID", "Provider", "Product", "Kind", "Price / input", "Output", "Cache read x", "Cache write x", "Batch factor", "Unit",
             "Effective from", "Effective to", "Status", "Source", "Date fetched", "Grade", "Label", "Included units"]
    for i, h in enumerate(heads):
        put(ws, f"{L(i + 1)}3", h, "head")
    r = PB_FIRST
    for row in PRICEBOOK:
        vals = [row["id"], row["provider"], row["product"], row["kind"], row["p_in"], row.get("p_out"), row.get("c_read"),
                row.get("c_write"), row.get("batch"), row["unit"], date(2026, 9, 20),
                date.fromisoformat(row["to"]) if row["to"] else None, row["status"], row["src"], date(2026, 9, 20), "A", "quoted",
                LANGFUSE_INCLUDED if row["id"] == "PL_LANGFUSE_PRO" else None]
        for i, v in enumerate(vals):
            col = L(i + 1)
            kind = "input" if i in (4, 5, 6, 7, 8, 11, 12, 17) else "text"
            fmt = None
            if i in (4, 5):
                fmt = USD4 if (row["kind"] in ("Unit",) and (row["p_in"] or 0) < 1) else USD2
            if i in (6, 7, 8):
                fmt = "0.00"
            if i in (10, 11, 14):
                fmt = "yyyy-mm-dd"
            if v is not None or kind == "input":
                put(ws, f"{col}{r}", v, kind, fmt)
        r += 1
    widths(ws, {"A": 18, "B": 16, "C": 54, "D": 9, "E": 13, "F": 9, "G": 11, "H": 12, "I": 11, "J": 30, "K": 13, "L": 12, "M": 12,
                "N": 8, "O": 12, "P": 7, "Q": 8, "R": 14})
    ws.freeze_panes = "D4"


def build_teams(wb):
    ws = wb.create_sheet("Teams")
    title(ws, "Teams (worked example: fictional)", "One team per business unit in v0.1. Blue text on pale yellow = input. IDs refer to the PriceBook.")
    put(ws, "A3", "Field", "head")
    put(ws, "B3", "Unit / options", "head")
    for t in range(NT):
        put(ws, f"{ADDR['team_cols'][t]}3", f"Team {t + 1}", "head")
    for i, h in enumerate(["Label", "Source", "Grade"]):
        put(ws, f"{L(3 + NT + i)}3", h, "head")
    # row 4 = team names (Org counts them with COUNTA on row 4)
    r = 4
    for key, lab, unit in TEAM_FIELDS:
        put(ws, f"A{r}", lab)
        put(ws, f"B{r}", unit, "note")
        for t, tm in enumerate(TEAMS):
            v = tm[key]
            fmt = PCT if unit == "share" else (USD2 if unit.startswith("USD") else (NUM if isinstance(v, (int, float)) else None))
            put(ws, f"{ADDR['team_cols'][t]}{r}", v if v != "" else None, "input", fmt)
        put(ws, f"{L(3 + NT)}{r}", "assumed")
        put(ws, f"{L(4 + NT)}{r}", "Fictional worked example (Claude, 2026-09-20); prices come from PriceBook (A)", "note")
        put(ws, f"{L(5 + NT)}{r}", "D")
        ADDR["team_row"][key] = r
        r += 1
    r += 1
    put(ws, f"A{r}", "Derived from inputs and the PriceBook (formulas)", "sub")
    r += 1
    T = ADDR["team_row"]

    def defn(c):
        f = lambda k: f"{c}{T[k]}"
        d = lambda k: f"{c}{ADDR['derived_row'][k]}"
        return [
            ("d_seat", "Seat billed (1/0)", f'=IF(OR({f("buy")}="Seat",{f("buy")}="Seat + usage"),1,0)', NUM),
            ("d_usage", "Seat + usage (1/0)", f'=IF({f("buy")}="Seat + usage",1,0)', NUM),
            ("d_ptok", "Per-unit, token-billed (1/0)", f'=IF(AND({f("buy")}="Per-unit",{f("unit_price")}=""),1,0)', NUM),
            ("d_vendor", "Per-unit, vendor outcome price (1/0)", f'=IF(AND({f("buy")}="Per-unit",{f("unit_price")}<>""),1,0)', NUM),
            ("d_cap", "Committed capacity (1/0)", f'=IF({f("buy")}="Committed capacity",1,0)', NUM),
            ("d_api", "API-billed extras apply (1/0)", f'=IF({d("d_usage")}+{d("d_ptok")}+{d("d_cap")}>0,1,0)', NUM),
            ("v_seat", "Blended seat price (USD per licensed user per month)",
             f'=(1-{f("prem_share")})*{pbv(f("seat_std"), "E")}+{f("prem_share")}*{pbv(f("seat_prem"), "E")}', USD2),
            ("v_unit", "Vendor per-outcome price (USD)", f'={pbv(f("unit_price"), "E")}', USD2),
            ("p_in", "Blended input price (USD per million tokens)",
             f'=(1-{f("route")})*{pbv(f("model"), "E")}+{f("route")}*{pbv(f("cheap"), "E")}', USD2),
            ("p_out", "Blended output price (USD per million tokens)",
             f'=(1-{f("route")})*{pbv(f("model"), "F")}+{f("route")}*{pbv(f("cheap"), "F")}', USD2),
            ("f_cache", "Input price factor after caching",
             f'=(1-{f("cached")}-{f("cwrite")})+{f("cached")}*{pbv(f("model"), "G")}+{f("cwrite")}*{pbv(f("model"), "H")}', "0.000"),
            ("f_batch", "Price factor after batch share", f'=1-{f("async_")}*(1-{pbv(f("model"), "I")})', "0.000"),
            ("o_rest", "Outcomes per user, non-top segment",
             f'=IF({f("basis")}="per user",{f("o_user")}/((1-{f("top_share")})+{f("top_share")}*{f("top_mult")}),0)', NUM2),
            ("o_top", "Outcomes per user, top segment", f'={f("top_mult")}*{d("o_rest")}', NUM2),
            ("u_other", "Tool and guardrail cost per outcome (USD)",
             f'={f("tool_calls")}*{pbv(f("tool_price"), "E")}/1000+{f("guard_units")}*{pbv(f("guard_price"), "E")}/1000', USD4),
            ("v_parse", "Parsing price (USD per page)", f'={pbv(f("parse_price"), "E")}', USD4),
            ("v_emb", "Embedding price (USD per million tokens)", f'={pbv(f("emb_price"), "E")}', USD4),
            ("v_plan", "Index plan minimum (USD per month)", f'={pbv(f("plan_price"), "E")}', USD2),
            ("v_store", "Storage price (USD per GB per month)", f'={pbv(f("store_price"), "E")}', USD4),
            ("v_readp", "Read price (USD per million read units)", f'={pbv(f("read_price"), "E")}', USD2),
            ("d_start", "Effective launch month (9999 when the team is not active)", f'=IF({f("active")}=1,{f("start")},9999)', NUM),
            ("d_lic", "Licensed users counted (0 when the team is not active)", f'={f("active")}*{f("licensed")}', NUM),
        ]
    for i, key in enumerate(DKEYS):
        ADDR["derived_row"][key] = r + i
    assert [x[0] for x in defn("C")] == DKEYS
    for i, (key, lab, _, fmt) in enumerate(defn("C")):
        put(ws, f"A{r + i}", lab)
    for t in range(NT):
        c = ADDR["team_cols"][t]
        for i, (key, lab, formula, fmt) in enumerate(defn(c)):
            put(ws, f"{c}{r + i}", formula, "calc", fmt)
    put(ws, f"A{r + len(DKEYS) + 1}", "Calibration note: Team 1 assumes 2 minutes saved per interaction, about 5.5 minutes per working day, far below published self-reported figures. "
                          "Team 5 is the same kind of team calibrated to the low published figure (7 minutes per interaction, about 19 minutes per working day, grade C*). Both are shown on purpose.", "note")
    dvs = {"buy": '"Seat,Seat + usage,Per-unit,Committed capacity"', "curve": '"Linear,S"', "basis": '"per user,direct volume"',
           "agentic": '"Yes,No"', "own_index": '"1,0"', "active": '"1,0"'}
    for key, opts in dvs.items():
        dv = DataValidation(type="list", formula1=opts, allow_blank=False)
        ws.add_data_validation(dv)
        dv.add(f"{ADDR['team_cols'][0]}{ADDR['team_row'][key]}:{ADDR['team_cols'][-1]}{ADDR['team_row'][key]}")
    widths(ws, {"A": 52, "B": 44, **{c: 30 for c in ADDR["team_cols"]}, L(3 + NT): 10, L(4 + NT): 60, L(5 + NT): 7})
    ws.freeze_panes = "C5"
