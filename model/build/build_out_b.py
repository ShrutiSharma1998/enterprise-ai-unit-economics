# SPDX-License-Identifier: Apache-2.0
"""Scenarios (low-cost, base, high-cost side by side) and Sensitivity (drivers, break-even margins, kill number)."""
from xl_helpers import put, widths, title, USD, USD2, NUM, PCT, L
import build_calc as bc
from build_calc import ROWS, NAMES, NT
from build_inputs import ADDR, org
from build_out_a import RES, TCOL, LAYER_NAMES, R, ENTC
from reference_model import LAYER, HUB_LAYER

SCN = {}
SENS = {}


def layer_formula(name, n):
    terms = []
    for t in range(NT):
        for key in bc.COST_KEYS:
            if LAYER[key] == n:
                terms.append(f"{name}!$C${ROWS['team'](t, key)}")
    hub = [f"{name}!$C${ROWS['hub'](key)}" for key in bc.HUB_COST_KEYS if HUB_LAYER[key] == n]
    f = "=" + "+".join(terms) if terms else "=0"
    if hub:
        f += f"+{name}!$B${ROWS['alloc']('factor')}*(" + "+".join(hub) + ")"
    return f


def build_scenarios(wb):
    ws = wb.create_sheet("Scenarios")
    title(ws, "Scenarios side by side", "Low-cost, Base and High-cost, each from its own Calc sheet. Value case follows the Org selection.")
    for i, h in enumerate(["Enterprise, over the horizon", "Low-cost", "Base", "High-cost", "Low <= Base <= High"]):
        put(ws, f"{L(i + 1)}3", h, "head")
    put(ws, "D3", "High-cost (stress case)", "head")
    r = 4
    SCN["layer_row"] = {}
    for n, lab in LAYER_NAMES.items():
        put(ws, f"A{r}", lab)
        for k in range(3):
            put(ws, f"{'BCD'[k]}{r}", layer_formula(NAMES[k], n), "calc", USD)
        put(ws, f"E{r}", f'=IF(AND(B{r}<=C{r},C{r}<=D{r}),"OK","CHECK")', "calc")
        SCN["layer_row"][n] = r
        r += 1
    put(ws, f"A{r}", "Total cost", bold=True)
    for k in range(3):
        c = "BCD"[k]
        put(ws, f"{c}{r}", f"=SUM({c}4:{c}{r - 1})", "calc", USD, bold=True)
    put(ws, f"E{r}", f'=IF(AND(B{r}<=C{r},C{r}<=D{r}),"OK","CHECK")', "calc")
    SCN["total"] = r
    r += 1
    put(ws, f"A{r}", "Benefit")
    for k in range(3):
        put(ws, f"{'BCD'[k]}{r}", f"={NAMES[k]}!$C${ROWS['ent']('benefit')}", "link", USD)
    SCN["benefit"] = r
    r += 1
    put(ws, f"A{r}", "Net value")
    for k in range(3):
        c = "BCD"[k]
        put(ws, f"{c}{r}", f"={c}{SCN['benefit']}-{c}{SCN['total']}", "calc", USD)
    SCN["net"] = r
    r += 1
    put(ws, f"A{r}", "Payback month")
    for k in range(3):
        put(ws, f"{'BCD'[k]}{r}", f"={NAMES[k]}!$C${ROWS['ent']('pb')}", "link", NUM)
    r += 1
    put(ws, f"A{r}", "Cost per outcome")
    for k in range(3):
        c = "BCD"[k]
        outs = "+".join(f"{NAMES[k]}!$C${ROWS['team'](t, 'out')}" for t in range(NT))
        put(ws, f"{c}{r}", f"=IF(({outs})=0,0,{c}{SCN['total']}/({outs}))", "calc", USD2)
    put(ws, f"A{r + 2}", "High-cost is a stress case: every parameter at its high value at once. It is not a likely outcome. Published forecast-miss rates (FCS-01, grade C) are much narrower.", "note")
    widths(ws, {"A": 34, "B": 18, "C": 18, "D": 24, "E": 22})
    return ws


DRIVERS = [
    ("Realisation share of self-reported time saved", "=$B$4", 0.5, 1.5, "benefit"),
    ("Minutes saved per outcome", "=$B$4", 0.5, 1.5, "benefit"),
    ("Quality or acceptance rate", "=$B$4", 0.8, 1.1, "benefit"),
    ("Adoption and volume (active share, outcomes)", "=$B$4-$B$9", 0.7, 1.3, "volume"),
    ("Tokens per outcome", "=-$B$7", 0.7, 1.5, "cost"),
    ("Human review minutes", "=-$B$8", 2 / 3, 2.0, "cost"),
    ("Effort (person-day-rate-driven lines)", "=-$B$10", 0.5, 2.0, "cost"),
]


def build_sensitivity(wb):
    ws = wb.create_sheet("Sensitivity")
    title(ws, "Sensitivity and the kill number",
          "One-at-a-time, linear scaling of the selected scenario's components. Checked in Phase 5 by full recalculation: exact for realisation, minutes saved, acceptance, tokens, "
          "review minutes and effort; approximate for adoption and volume (about 8% of that driver's swing at x0.7). Multipliers are grade D inputs.")
    tok, vend, tools, rev = (RES["cost_row"][k] for k in ("tokens", "vendor", "tools", "review"))
    comp = [
        ("Benefit (B)", f"={R('benefit')}"),
        ("Total cost", f"={R('total')}"),
        ("Net value (N0 = B minus cost)", "=B4-B5"),
        ("Model token cost", f"=SUM(Results!{TCOL[0]}{tok}:{TCOL[-1]}{tok})"),
        ("Human review cost", f"=SUM(Results!{TCOL[0]}{rev}:{TCOL[-1]}{rev})"),
        ("Volume-driven cost (tokens, vendor, tools, review)", f"=SUM(Results!{TCOL[0]}{tok}:{TCOL[-1]}{tok})+SUM(Results!{TCOL[0]}{vend}:{TCOL[-1]}{vend})+SUM(Results!{TCOL[0]}{tools}:{TCOL[-1]}{tools})+SUM(Results!{TCOL[0]}{rev}:{TCOL[-1]}{rev})"),
        ("Person-day-rate-driven effort cost (starter effort lines, migration, cost governance; hub after shape)",
         f"=Results!D{RES['tag_row']['S']}+SUM(Results!{TCOL[0]}{RES['cost_row']['migration']}:{TCOL[-1]}{RES['cost_row']['migration']})+Results!{ENTC}{RES['hub_row']['gov']}"),
    ]
    for i, (lab, f) in enumerate(comp):
        put(ws, f"A{4 + i}", lab)
        put(ws, f"B{4 + i}", f, "calc" if not f.startswith("=Results") and "SUM(" not in f else "link", USD)
    heads = ["Driver", "Effect on net value per +100% (USD)", "Low multiplier", "High multiplier", "Net value at low", "Net value at high", "Swing",
             "Rank", "Break-even multiplier", "Margin of safety", "Direction", "Break-even value (where a single scalar exists)"]
    hr = 12
    for i, h in enumerate(heads):
        put(ws, f"{L(i + 1)}{hr}", h, "head", wrap=True)
    r0 = hr + 1
    rN = r0 + len(DRIVERS) - 1
    for i, (name, eff, lo, hi, _kind) in enumerate(DRIVERS):
        r = r0 + i
        put(ws, f"A{r}", name)
        put(ws, f"B{r}", eff, "calc", USD)
        put(ws, f"C{r}", lo, "input", "0.00")
        put(ws, f"D{r}", hi, "input", "0.00")
        put(ws, f"E{r}", f"=$B$6+(C{r}-1)*B{r}", "calc", USD)
        put(ws, f"F{r}", f"=$B$6+(D{r}-1)*B{r}", "calc", USD)
        put(ws, f"G{r}", f"=ABS(F{r}-E{r})", "calc", USD)
        put(ws, f"H{r}", f"=RANK(G{r},$G${r0}:$G${rN})+COUNTIF($G${r0}:G{r},G{r})-1", "calc", NUM)
        put(ws, f"I{r}", f'=IF(B{r}=0,"n/a",1-$B$6/B{r})', "calc", "0.00")
        put(ws, f"J{r}", f"=IF(B{r}=0,1E+9,$B$6/ABS(B{r}))", "calc", PCT)
        put(ws, f"K{r}", f'=IF(B{r}>0,"can fall by","can rise by")', "calc")
    rp = ADDR["param_row"]["realise"]
    put(ws, f"L{r0}", f"=I{r0}*INDEX(Params!$D${rp}:$F${rp},{org('val_idx')})", "calc", PCT)
    kr = rN + 3
    put(ws, f"A{kr}", "The number that would kill the case (smallest margin of safety)", "sub")
    m = f"MATCH(MIN($J${r0}:$J${rN}),$J${r0}:$J${rN},0)"
    put(ws, f"A{kr + 1}", "Driver")
    put(ws, f"B{kr + 1}", f'=IF($B$6<=0,"Net value is already zero or negative",INDEX($A${r0}:$A${rN},{m}))', "calc", bold=True)
    put(ws, f"A{kr + 2}", "How far it can move")
    put(ws, f"B{kr + 2}", (f'=IF($B$6<=0,"Nothing to erode in this scenario",INDEX($K${r0}:$K${rN},{m})&" "&TEXT(MIN($J${r0}:$J${rN}),"0%")'
                           f'&" before net value reaches zero (break-even multiplier "&TEXT(INDEX($I${r0}:$I${rN},{m}),"0.00")&"x)")'), "calc")
    put(ws, f"A{kr + 4}", "Top three drivers by swing", "sub")
    top = []
    for i in range(3):
        rr = kr + 5 + i
        mm = f"MATCH({i + 1},$H${r0}:$H${rN},0)"
        put(ws, f"A{rr}", f"Rank {i + 1}")
        put(ws, f"B{rr}", f'=INDEX($A${r0}:$A${rN},{mm})&" (swing "&TEXT(INDEX($G${r0}:$G${rN},{mm}),"$#,##0")&")"', "calc")
        top.append(f"Sensitivity!$B${rr}")
    SENS.update(dict(kill_name=f"Sensitivity!$B${kr + 1}", kill_text=f"Sensitivity!$B${kr + 2}", top=top, r0=r0, rN=rN, comp_row=4))
    widths(ws, {"A": 62, "B": 30, "C": 12, "D": 12, "E": 18, "F": 18, "G": 16, "H": 8, "I": 12, "J": 12, "K": 14, "L": 22})
    return ws, SENS
