# SPDX-License-Identifier: Apache-2.0
"""Lines (taxonomy index), Evidence (assumptions register) and Levers (step-by-step with fixtures) sheets."""
from datetime import date
from spec_data import ORG, PARAMS, PRICEBOOK, TEAM_FIELDS, FICTION
from spec_lines import LINES
from xl_helpers import put, widths, title, USD, USD4, NUM, PCT, L, F_WARN
import build_calc as bc
from build_calc import ROWS
from build_inputs import ADDR, org, team, derived, param, NT

EVID, LEV, LINEREG = {}, {}, {}
D0 = date(2026, 9, 20)


def build_lines(wb):
    ws = wb.create_sheet("Lines")
    title(ws, "The 35 cost lines (taxonomy index)", "Source: research/cost-taxonomy.md. Policy: P dated primary price, R range with warning, E enterprise-entered (starter value unless off).")
    for i, h in enumerate(["ID", "Line", "Layer", "Type", "Owner (hub-and-spoke)", "Policy", "Evidence", "Status", "Where it is computed"]):
        put(ws, f"{L(i + 1)}3", h, "head")
    pr = ADDR["param_row"]
    status = {
        "CL-14": f'=IF(Params!$E${pr["env_month"]}=0,"OFF","ON")',
        "CL-15": f'=IF(SUM(Teams!${ADDR["team_cols"][0]}${ADDR["team_row"]["cap_cost"]}:${ADDR["team_cols"][-1]}${ADDR["team_row"]["cap_cost"]})=0,"OFF","ON")',
        "CL-31": f'=IF(Params!$E${pr["comp_year"]}=0,"OFF","ON")',
        "CL-32": f'=IF(Params!$E${pr["lic_year"]}=0,"OFF","ON")',
        "CL-20": "n/a (not used in this example)",
    }
    r = 4
    off = []
    for lid, name, layer, typ, owner, pol, ev, where in LINES:
        for i, v in enumerate([lid, name, layer, typ, owner, pol, ev, status.get(lid, "ON"), where]):
            put(ws, f"{L(i + 1)}{r}", v, "calc" if (i == 7 and str(v).startswith("=")) else "text")
        if lid in ("CL-14", "CL-15", "CL-31", "CL-32"):
            off.append({"id": f"Lines!$A${r}", "name": f"Lines!$B${r}", "status": f"Lines!$H${r}"})
        r += 1
    last = r - 1
    r += 1
    put(ws, f"A{r}", "Tally by policy", "sub")
    for i, p in enumerate("PRE"):
        put(ws, f"A{r + 1 + i}", p)
        put(ws, f"B{r + 1 + i}", f'=COUNTIF($F$4:$F${last},A{r + 1 + i})', "calc", NUM)
    put(ws, f"A{r + 4}", "Lines with no starter value are OFF and understate cost until the enterprise enters a value (CL-14, CL-15, CL-31, CL-32).", "note")
    LINEREG["tally_row"] = r + 1
    widths(ws, {"A": 8, "B": 56, "C": 7, "D": 30, "E": 20, "F": 8, "G": 30, "H": 34, "I": 58})
    ws.freeze_panes = "C4"
    return off


def build_evidence(wb):
    ws = wb.create_sheet("Evidence")
    title(ws, "Assumptions register", "Every input with its label, source, date, grade, owner and review date. Values link to the input cells.")
    heads = ["Input ID", "Name", "Value (base)", "Unit", "Label", "Source", "Date", "Grade", "Owner", "Last reviewed"]
    for i, h in enumerate(heads):
        put(ws, f"{L(i + 1)}3", h, "head")
    r = 4
    first = r

    def row(iid, name, value, unit, label, src, grade, owner, fmt=None):
        nonlocal r
        put(ws, f"A{r}", iid, "note")
        put(ws, f"B{r}", name)
        put(ws, f"C{r}", value, "link" if isinstance(value, str) and value.startswith("=") else "text", fmt)
        put(ws, f"D{r}", unit, "note")
        put(ws, f"E{r}", label)
        put(ws, f"F{r}", src, "note")
        put(ws, f"G{r}", D0, "text", "yyyy-mm-dd")
        put(ws, f"H{r}", grade)
        put(ws, f"I{r}", owner)
        put(ws, f"J{r}", D0, "text", "yyyy-mm-dd")
        r += 1

    for key, (lab, val, unit, label, src, grade) in ORG.items():
        row(f"ORG.{key}", lab, f"={ADDR['org'][key]}", unit, label, src, grade, "AI program lead (fictional)")
    for key, (desc, unit, lo, ba, hi, line, why, grade) in PARAMS.items():
        row(f"PARAM.{key}", desc, f"=Params!$E${ADDR['param_row'][key]}", unit, "assumed", f"spec/starter-values.md ({line}); {why}"[:180], grade, "AI program lead (fictional)")
    for key, lab, unit in TEAM_FIELDS:
        row(f"TEAM.{key}", lab, "see Teams sheet (one value per team)", unit, "assumed", FICTION, "D", "Team product owner (fictional)")
    for i, p in enumerate(PRICEBOOK):
        row(f"PB.{p['id']}", p["product"], f"=PriceBook!$E${4 + i}", p["unit"], "quoted", f"{p['src']} in evidence/source-register.md; {p['provider']} pricing page, fetched 2026-09-20", "A", "AI program lead (fictional)")
    EVID["first"], EVID["last"] = first, r - 1
    r += 1
    put(ws, f"A{r}", "Share of cost by evidence category (selected scenario)", "sub")
    r += 1
    from build_out_a import RES, TAG_NAMES
    for tag, name in TAG_NAMES.items():
        put(ws, f"A{r}", name)
        put(ws, f"C{r}", f"=Results!$E${RES['tag_row'][tag]}", "link", PCT)
        r += 1
    widths(ws, {"A": 26, "B": 60, "C": 26, "D": 34, "E": 10, "F": 70, "G": 12, "H": 7, "I": 30, "J": 13})
    ws.freeze_panes = "C4"


FIXTURES = [
    # in, out, ctx, tok_mult, retry, steps, main_in, main_out, cheap_in, cheap_out, route, cached, cwrite, read, write, async, batch, resid
    (10000, 1000, 0.0, 1.0, 1.0, 1, 2.0, 10.0, 1.0, 5.0, 0.0, 0.5, 0.0, 0.1, 1.25, 0.0, 0.5, 1.0),
    (20000, 2000, 0.2, 1.0, 1.2, 2, 5.0, 25.0, 1.0, 5.0, 0.5, 0.4, 0.1, 0.1, 1.25, 0.3, 0.5, 1.1),
    # Fixtures 3 and 4: the worked example on Anthropic's pricing page (S09, read 2026-09-20): Opus 5, 50,000 input and 15,000 output tokens.
    (50000, 15000, 0.0, 1.0, 1.0, 1, 5.0, 25.0, 1.0, 5.0, 0.0, 0.0, 0.0, 0.1, 1.25, 0.0, 0.5, 1.0),
    (50000, 15000, 0.0, 1.0, 1.0, 1, 5.0, 25.0, 1.0, 5.0, 0.0, 0.8, 0.0, 0.1, 1.25, 0.0, 0.5, 1.0),
]
FIX_NAMES = ["Fixture 1", "Fixture 2", "Fixture 3 (provider example, no cache)", "Fixture 4 (provider example, 80% cached)"]
# Hand calculation, written out (independent of the workbook formulas):
#   fixture 1: (10,000 x 2 x (0.5 + 0.5 x 0.1) + 1,000 x 10) / 1e6 = (11,000 + 10,000) / 1e6 = 0.021
#   fixture 2: scale 0.8 x 1.2 x 2 = 1.92 -> tokens in 38,400, out 3,840; blended prices 3 and 15;
#              cache factor 0.5 + 0.04 + 0.125 = 0.665; batch factor 0.85; (38,400 x 3 x 0.665 + 3,840 x 15) / 1e6 x 0.85 x 1.1 = 0.12548448
#   fixtures 3 and 4: the provider's published totals are $0.705 (no cache) and $0.525 (40,000 of 50,000 input tokens read from cache); each includes
#              $0.08 of session runtime, which is not a token cost, so the token-only expected values are 0.705 - 0.08 = 0.625 and 0.525 - 0.08 = 0.445.
EXPECTED = [0.021, 0.12548448, 0.625, 0.445]
FIX_LABELS = ["Input tokens per outcome", "Output tokens per outcome", "Context-management reduction", "Tokens scenario multiplier", "Retry multiplier",
              "Agent steps", "Main model input price", "Main model output price", "Cheaper model input price", "Cheaper model output price",
              "Share routed to cheaper model", "Cached share of input", "Cache-write share of input", "Cache read multiplier", "Cache write multiplier",
              "Asynchronous (batch) share", "Batch price factor", "Residency multiplier"]


def build_levers(wb):
    ws = wb.create_sheet("Levers")
    title(ws, "Levers in their fixed order (Base scenario)", "Order: context and scenario scale, routing, caching, batch, residency. Below: two hand-calculated fixtures used by acceptance test 5.")
    put(ws, "A3", "Step", "head")
    for t in range(NT):
        put(ws, f"{L(2 + t)}3", f"={team('name', t)}", "head")
    steps = [
        ("Input tokens per outcome (entered)", lambda t: f"={team('tok_in', t)}", NUM),
        ("Output tokens per outcome (entered)", lambda t: f"={team('tok_out', t)}", NUM),
        ("Scale: (1 - context) x scenario x retries x steps",
         lambda t: f"=(1-{team('ctx', t)})*{param('tok_mult', 1)}*{param('retry', 1)}*IF({team('agentic', t)}=\"Yes\",{param('steps', 1)},1)", "0.000"),
        ("Input tokens after scale", lambda t: f"={L(2 + t)}4*{L(2 + t)}6", NUM),
        ("Output tokens after scale", lambda t: f"={L(2 + t)}5*{L(2 + t)}6", NUM),
        ("Blended input price after routing (USD per million)", lambda t: f"={derived('p_in', t)}", "$#,##0.00"),
        ("Blended output price after routing (USD per million)", lambda t: f"={derived('p_out', t)}", "$#,##0.00"),
        ("Input price factor after caching", lambda t: f"={derived('f_cache', t)}", "0.0000"),
        ("Price factor after batch share", lambda t: f"={derived('f_batch', t)}", "0.0000"),
        ("Residency multiplier", lambda t: f"={team('resid', t)}", "0.00"),
    ]
    r = 4
    for lab, fn, fmt in steps:
        put(ws, f"A{r}", lab)
        for t in range(NT):
            put(ws, f"{L(2 + t)}{r}", fn(t), "calc", fmt)
        r += 1
    put(ws, f"A{r}", "Token cost per outcome (this sheet)", bold=True)
    for t in range(NT):
        c = L(2 + t)
        put(ws, f"{c}{r}", f"=({c}7*{c}9*{c}11+{c}8*{c}10)/1000000*{c}12*{c}13", "calc", USD4, bold=True)
    LEV["cpo_row"] = r
    r += 1
    put(ws, f"A{r}", "Token cost per outcome (Calc_Base)")
    for t in range(NT):
        put(ws, f"{L(2 + t)}{r}", f"=Calc_Base!$C${ROWS['team'](t, 'hdr')}", "link", USD4)
    r += 1
    put(ws, f"A{r}", "Difference")
    for t in range(NT):
        c = L(2 + t)
        put(ws, f"{c}{r}", f"={c}{r - 2}-{c}{r - 1}", "calc", '0.000000000')
    LEV["diff_row"] = r
    r += 3
    put(ws, f"A{r}", "Fixtures (typed inputs; expected values hand-calculated, see build/build_out_c.py)", "sub")
    for j, nm in enumerate(FIX_NAMES):
        put(ws, f"{'BCDE'[j]}{r}", nm, "sub", wrap=True)
    r += 1
    f0 = r
    for i, lab in enumerate(FIX_LABELS):
        put(ws, f"A{r}", lab)
        for j, fx in enumerate(FIXTURES):
            put(ws, f"{'BCDE'[j]}{r}", fx[i], "input", "General")
        r += 1
    g = lambda c, i: f"{c}{f0 + i}"
    put(ws, f"A{r}", "Computed cost per outcome", bold=True)
    for j in range(len(FIXTURES)):
        c = "BCDE"[j]
        scale = f"((1-{g(c, 2)})*{g(c, 3)}*{g(c, 4)}*{g(c, 5)})"
        pin = f"((1-{g(c, 10)})*{g(c, 6)}+{g(c, 10)}*{g(c, 8)})"
        pout = f"((1-{g(c, 10)})*{g(c, 7)}+{g(c, 10)}*{g(c, 9)})"
        fc = f"((1-{g(c, 11)}-{g(c, 12)})+{g(c, 11)}*{g(c, 13)}+{g(c, 12)}*{g(c, 14)})"
        fb = f"(1-{g(c, 15)}*(1-{g(c, 16)}))"
        put(ws, f"{c}{r}", f"=({g(c, 0)}*{scale}*{pin}*{fc}+{g(c, 1)}*{scale}*{pout})/1000000*{fb}*{g(c, 17)}", "calc", '0.00000000', bold=True)
    LEV["fx_calc_row"] = r
    r += 1
    put(ws, f"A{r}", "Expected (fixtures 1 and 2 hand-calculated; 3 and 4 from the provider's published example)")
    for j in range(len(FIXTURES)):
        put(ws, f"{'BCDE'[j]}{r}", EXPECTED[j], "input", '0.00000000')
    LEV["fx_exp_row"] = r
    r += 1
    put(ws, f"A{r}", "Difference")
    for j in range(len(FIXTURES)):
        c = "BCDE"[j]
        put(ws, f"{c}{r}", f"={c}{r - 2}-{c}{r - 1}", "calc", '0.000000000')
    LEV["fx_diff_row"] = r
    r += 2
    put(ws, f"A{r}", "Fixtures 3 and 4 reproduce the worked example on Anthropic's pricing page (evidence S09, read 2026-09-20): Opus 5, 50,000 input and 15,000 output tokens. "
                     "The page's totals, $0.705 without caching and $0.525 with 40,000 tokens read from cache, include $0.08 of session runtime, which is not a token cost.", "note")
    widths(ws, {"A": 58, **{L(2 + i): 24 for i in range(max(NT, 4))}})
