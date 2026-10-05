# SPDX-License-Identifier: Apache-2.0
"""Results (selected scenario), Summary and Allocation sheets."""
from spec_data import TEAMS
from xl_helpers import put, widths, title, USD, USD2, NUM, NUM2, PCT, F_WARN, L
import build_calc as bc
from build_calc import ROWS, NAMES
from build_inputs import ADDR, org, team, derived, NT
from reference_model import LAYER, HUB_LAYER

LAYER_NAMES = {1: "L1 Data readiness", 2: "L2 Setup and infrastructure", 3: "L3 Inference and usage", 4: "L4 Run and maintenance", 5: "L5 People and change"}
TAG_NAMES = {"A": "Dated primary prices (A)", "R": "Ranges with a warning (B*/C)", "S": "Starter values (D)", "E": "Enterprise-entered, off until entered"}
TCOL = [L(4 + i) for i in range(NT)]          # team columns on Results
HUBC, ENTC = L(4 + NT), L(5 + NT)          # hub and enterprise columns
RES = {}                              # registry of Results addresses


def ch(fn):
    return f"CHOOSE({org('scen_idx')}," + ",".join(fn(n) for n in NAMES) + ")"


def build_results(wb):
    ws = wb.create_sheet("Results")
    title(ws, "Results for the selected scenario", "Every cell picks the Low-cost, Base or High-cost Calc sheet using the scenario chosen on Org.")
    put(ws, "A3", "Shape factor on raw hub cost")
    put(ws, "D3", "=" + ch(lambda n: f"{n}!$B${ROWS['alloc']('factor')}"), "calc", "0.00")
    RES["factor"] = "Results!$D$3"
    heads = ["Cost group", "Evidence", "Layer"] + [f"=Teams!{c}$4" for c in ADDR["team_cols"]] + ["Hub (raw)", "Enterprise"]
    for i, h in enumerate(heads):
        put(ws, f"{L(i + 1)}4", h, "head")
    r = 5
    first = r
    RES["cost_row"] = {}
    for key, label, tag, fmt in bc.TEAM_ROWS:
        if not tag:
            continue
        put(ws, f"A{r}", label)
        put(ws, f"B{r}", tag)
        put(ws, f"C{r}", LAYER[key])
        for t in range(NT):
            put(ws, f"{TCOL[t]}{r}", "=" + ch(lambda n, t=t, key=key: f"{n}!$C${ROWS['team'](t, key)}"), "calc", USD)
        put(ws, f"{ENTC}{r}", f"=SUM({TCOL[0]}{r}:{TCOL[-1]}{r})", "calc", USD)
        RES["cost_row"][key] = r
        r += 1
    RES["hub_row"] = {}
    for key, label, tag, fmt in bc.HUB_ROWS:
        if not tag:
            continue
        put(ws, f"A{r}", "Hub: " + label)
        put(ws, f"B{r}", tag)
        put(ws, f"C{r}", HUB_LAYER[key])
        put(ws, f"{HUBC}{r}", "=" + ch(lambda n, key=key: f"{n}!$C${ROWS['hub'](key)}"), "calc", USD)
        put(ws, f"{ENTC}{r}", f"={HUBC}{r}*$D$3", "calc", USD)
        RES["hub_row"][key] = r
        r += 1
    last = r - 1
    put(ws, f"A{r}", "Total cost over the horizon", bold=True)
    for c in TCOL + [HUBC, ENTC]:
        put(ws, f"{c}{r}", f"=SUM({c}{first}:{c}{last})", "calc", USD, bold=True)
    RES["total_row"] = r
    r += 2
    put(ws, f"A{r}", "By layer", "sub")
    r += 1
    RES["layer_row"] = {}
    for n, name in LAYER_NAMES.items():
        put(ws, f"A{r}", name)
        for c in TCOL + [HUBC, ENTC]:
            put(ws, f"{c}{r}", f"=SUMIF($C${first}:$C${last},{n},{c}${first}:{c}${last})", "calc", USD)
        RES["layer_row"][n] = r
        r += 1
    r += 1
    put(ws, f"A{r}", "By evidence category", "sub")
    put(ws, f"D{r}", "Cost", "note")
    put(ws, f"E{r}", "Share", "note")
    r += 1
    RES["tag_row"] = {}
    for tag, name in TAG_NAMES.items():
        put(ws, f"A{r}", name)
        put(ws, f"B{r}", tag)
        put(ws, f"D{r}", f"=SUMIF($B${first}:$B${last},B{r},${ENTC}${first}:${ENTC}${last})", "calc", USD)
        put(ws, f"E{r}", f"=IF(${ENTC}${RES['total_row']}=0,0,D{r}/${ENTC}${RES['total_row']})", "calc", PCT)
        RES["tag_row"][tag] = r
        r += 1
    put(ws, f"A{r}", "Sum of shares")
    put(ws, f"E{r}", f"=SUM(E{r - 4}:E{r - 1})", "calc", PCT)
    RES["tag_sum"] = f"Results!$E${r}"
    r += 2
    put(ws, f"A{r}", "Team and enterprise metrics", "sub")
    r += 1
    RES["m"] = {}

    def metric(key, label, team_f, ent_f, fmt):
        nonlocal r
        put(ws, f"A{r}", label)
        for t in range(NT):
            put(ws, f"{TCOL[t]}{r}", team_f(t), "calc", fmt)
        if ent_f:
            put(ws, f"{ENTC}{r}", ent_f, "calc", fmt)
        RES["m"][key] = r
        r += 1

    tr = lambda key: (lambda t: "=" + ch(lambda n: f"{n}!$C${ROWS['team'](t, key)}"))
    metric("buy", "Buying model", lambda t: f"={team('buy', t)}", None, None)
    metric("licensed", "Licensed users (active teams)", lambda t: f"={derived('d_lic', t)}", f"=SUM({TCOL[0]}{r}:{TCOL[-1]}{r})", NUM)
    metric("outcomes", "Outcomes over the horizon", tr("out"), f"=SUM({TCOL[0]}{r}:{TCOL[-1]}{r})", NUM)
    metric("active", "Active user-months", tr("act"), f"=SUM({TCOL[0]}{r}:{TCOL[-1]}{r})", NUM)
    metric("benefit", "Benefit", tr("benefit"), f"=SUM({TCOL[0]}{r}:{TCOL[-1]}{r})", USD)
    metric("direct", "Direct cost", lambda t: f"={TCOL[t]}{RES['total_row']}", None, USD)
    metric("alloc", "Allocated hub cost", lambda t: "=" + ch(lambda n: f"{n}!${bc.ALLOC_COLS[t]}${ROWS['alloc']('alloc')}"), None, USD)
    ws[f"{ENTC}{RES['m']['alloc']}"] = "=" + ch(lambda n: f"{n}!${bc.ALLOC_TOTAL}${ROWS['alloc']('alloc')}")
    ws[f"{ENTC}{RES['m']['alloc']}"].number_format = USD
    metric("total", "Total cost including allocation", lambda t: f"={TCOL[t]}{RES['m']['direct']}+{TCOL[t]}{RES['m']['alloc']}", f"={ENTC}{RES['total_row']}", USD)
    metric("net", "Net value (benefit minus cost)", lambda t: f"={TCOL[t]}{RES['m']['benefit']}-{TCOL[t]}{RES['m']['total']}",
           f"={ENTC}{RES['m']['benefit']}-{ENTC}{RES['m']['total']}", USD)
    metric("payback", "Payback month", lambda t: f'=IF({team("active", t)}=0,"n/a",' + tr("pb")(t)[1:] + ")", "=" + ch(lambda n: f"{n}!$C${ROWS['ent']('pb')}"), NUM)
    metric("cpo", "Cost per outcome", lambda t: f"=IF({TCOL[t]}{RES['m']['outcomes']}=0,0,{TCOL[t]}{RES['m']['total']}/{TCOL[t]}{RES['m']['outcomes']})",
           f"=IF({ENTC}{RES['m']['outcomes']}=0,0,{ENTC}{RES['m']['total']}/{ENTC}{RES['m']['outcomes']})", USD2)
    bas = f"Teams!${ADDR['team_cols'][0]}${ADDR['team_row']['basis']}:${ADDR['team_cols'][-1]}${ADDR['team_row']['basis']}"
    act, tot_r = RES["m"]["active"], RES["m"]["total"]
    pu_act = f'SUMPRODUCT(({bas}="per user")*{TCOL[0]}{act}:{TCOL[-1]}{act})'
    pu_tot = f'SUMPRODUCT(({bas}="per user")*{TCOL[0]}{tot_r}:{TCOL[-1]}{tot_r})'
    metric("cpa", "Cost per active user per month (teams with per-user outcomes; n/a for direct-volume teams)",
           lambda t: (f'=IF({team("basis", t)}="direct volume","n/a",IF({TCOL[t]}{act}=0,0,{TCOL[t]}{tot_r}/{TCOL[t]}{act}))'),
           f"=IF({pu_act}=0,0,{pu_tot}/{pu_act})", USD2)
    metric("bpo", "Benefit per outcome", lambda t: f"=IF({TCOL[t]}{RES['m']['outcomes']}=0,0,{TCOL[t]}{RES['m']['benefit']}/{TCOL[t]}{RES['m']['outcomes']})",
           f"=IF({ENTC}{RES['m']['outcomes']}=0,0,{ENTC}{RES['m']['benefit']}/{ENTC}{RES['m']['outcomes']})", USD2)
    put(ws, f"A{r}", "Run-rate at the last horizon month (team direct + hub)")
    put(ws, f"{ENTC}{r}", "=" + ch(lambda n: f"{n}!$C${ROWS['ent']('runrate')}"), "calc", USD)
    RES["m"]["runrate"] = r
    r += 1
    put(ws, f"A{r}", "Unallocated hub cost (central budget)")
    put(ws, f"{ENTC}{r}", "=" + ch(lambda n: f"{n}!${bc.ALLOC_UNALLOC}${ROWS['alloc']('alloc')}"), "calc", USD)
    RES["m"]["unalloc"] = r
    widths(ws, {"A": 60, "B": 10, "C": 8, **{c: 16 for c in TCOL + [HUBC, ENTC]}})
    ws.freeze_panes = "D5"
    return ws


def R(key, col=None):
    col = col or ENTC
    return f"Results!${col}${RES['m'][key]}"


def build_summary(wb, sens, off, tests_cell):
    ws = wb.create_sheet("Summary", 0)
    title(ws, "AI unit economics: summary")
    put(ws, "A2", "FICTIONAL WORKED EXAMPLE. Every input is an assumption (grade D) except dated primary prices (grade A). Not a forecast for any real organization.", fill=F_WARN, bold=True)
    r = 4
    put(ws, f"A{r}", "Settings (change them on the Org sheet)", "sub")
    r += 1
    for lab, key in [("Organization", "name"), ("Scenario", "scenario"), ("Value case", "value_case"), ("Org shape", "shape"), ("Allocation rule", "alloc"), ("Horizon (months)", "horizon")]:
        put(ws, f"A{r}", lab)
        put(ws, f"B{r}", f"={org(key)}", "link")
        r += 1
    put(ws, f"A{r}", f'=IF({org("scenario")}="High-cost","Stress case: every parameter is at its high value at once. Not a likely outcome.","")', fill=F_WARN, bold=True)
    r += 2
    put(ws, f"A{r}", "Headline (enterprise, over the horizon)", "sub")
    r += 1
    heads = [("Total cost", "total", USD), ("Benefit", "benefit", USD), ("Net value", "net", USD), ("Payback month", "payback", NUM),
             ("Cost per outcome", "cpo", USD2), ("Benefit per outcome", "bpo", USD2), ("Cost per active user per month", "cpa", USD2),
             ("Run-rate at the last horizon month (per month)", "runrate", USD)]
    for lab, key, fmt in heads:
        put(ws, f"A{r}", lab)
        put(ws, f"B{r}", f"={R(key)}", "link", fmt, bold=True)
        r += 1
    r += 1
    put(ws, f"A{r}", "Cost by layer", "sub")
    for j, c in enumerate([f"Team {i + 1}" for i in range(NT)] + ["Hub (after shape)", "Enterprise"]):
        put(ws, f"{L(2 + j)}{r}", f"=Teams!{ADDR['team_cols'][j]}$4" if j < NT else c, "sub")
    r += 1
    for n, name in LAYER_NAMES.items():
        put(ws, f"A{r}", name)
        for j in range(NT):
            put(ws, f"{L(2 + j)}{r}", f"=Results!{TCOL[j]}{RES['layer_row'][n]}", "link", USD)
        put(ws, f"{L(2 + NT)}{r}", f"=Results!{HUBC}{RES['layer_row'][n]}*{RES['factor']}", "link", USD)
        put(ws, f"{L(3 + NT)}{r}", f"=Results!{ENTC}{RES['layer_row'][n]}", "link", USD)
        r += 1
    r += 1
    put(ws, f"A{r}", "Teams (cost includes the allocated hub share)", "sub")
    for j, h in enumerate(["Buying model", "Outcomes", "Total cost", "Cost per outcome", "Cost per active user per month", "Benefit", "Net value", "Payback month"]):
        put(ws, f"{L(2 + j)}{r}", h, "sub", wrap=True)
    r += 1
    for t in range(NT):
        put(ws, f"A{r}", f"={team('name', t)}", "link")
        for j, (key, fmt) in enumerate([("buy", None), ("outcomes", NUM), ("total", USD), ("cpo", USD2), ("cpa", USD2), ("benefit", USD), ("net", USD), ("payback", NUM)]):
            put(ws, f"{L(2 + j)}{r}", f"=Results!{TCOL[t]}{RES['m'][key]}", "link", fmt)
        r += 1
    r += 1
    put(ws, f"A{r}", "How much of the cost rests on what evidence", "sub")
    put(ws, f"B{r}", "Cost", "sub")
    put(ws, f"C{r}", "Share", "sub")
    r += 1
    for tag, name in TAG_NAMES.items():
        put(ws, f"A{r}", name)
        put(ws, f"B{r}", f"=Results!D{RES['tag_row'][tag]}", "link", USD)
        put(ws, f"C{r}", f"=Results!E{RES['tag_row'][tag]}", "link", PCT)
        r += 1
    r += 1
    put(ws, f"A{r}", "Cost lines that are OFF (they understate cost until entered)", "sub")
    r += 1
    for o in off:
        put(ws, f"A{r}", f"={o['id']}&\" \"&{o['name']}&\": \"&{o['status']}", "link")
        r += 1
    r += 1
    put(ws, f"A{r}", "Acceptance tests (Tests sheet)")
    put(ws, f"B{r}", f"={tests_cell}", "link", bold=True)
    r += 2
    put(ws, f"A{r}", "The number that would kill the case", "sub")
    r += 1
    put(ws, f"A{r}", "Smallest margin of safety")
    put(ws, f"B{r}", f"={sens['kill_name']}", "link", bold=True)
    r += 1
    put(ws, f"A{r}", "How far it can move before net value reaches zero")
    put(ws, f"B{r}", f"={sens['kill_text']}", "link")
    r += 1
    put(ws, f"A{r}", "Top three drivers by swing in net value")
    for i in range(3):
        put(ws, f"{L(2 + i)}{r}", f"={sens['top'][i]}", "link")
    widths(ws, {"A": 62, "B": 26, "C": 20, "D": 20, "E": 22, "F": 22, "G": 20, "H": 18, "I": 16})
    return ws


CC = [f"CC-{1001 + i}" for i in range(NT)]


def build_allocation(wb):
    ws = wb.create_sheet("Allocation")
    title(ws, "Cost-center table (showback)", "CSV-ready: each row is one cost center. Direct cost plus the allocated hub share. Fictional cost centers.")
    for i, h in enumerate(["Cost center", "Business unit", "Team", "Direct cost", "Allocated hub cost", "Total cost", "Share of total"]):
        put(ws, f"{L(i + 1)}3", h, "head")
    r = 4
    for t in range(NT):
        put(ws, f"A{r}", CC[t], "input")
        put(ws, f"B{r}", f"={team('bu', t)}", "link")
        put(ws, f"C{r}", f"={team('name', t)}", "link")
        put(ws, f"D{r}", f"=Results!{TCOL[t]}{RES['m']['direct']}", "link", USD)
        put(ws, f"E{r}", f"=Results!{TCOL[t]}{RES['m']['alloc']}", "link", USD)
        put(ws, f"F{r}", f"=D{r}+E{r}", "calc", USD)
        put(ws, f"G{r}", f"=IF($F${4 + NT + 1}=0,0,F{r}/$F${4 + NT + 1})", "calc", PCT)
        r += 1
    put(ws, f"A{r}", "HUB-UNALLOC")
    put(ws, f"B{r}", "Hub (central budget)")
    put(ws, f"C{r}", "Unallocated shared cost")
    put(ws, f"D{r}", 0, "calc", USD)
    put(ws, f"E{r}", f"={R('unalloc')}", "link", USD)
    put(ws, f"F{r}", f"=D{r}+E{r}", "calc", USD)
    put(ws, f"G{r}", f"=IF($F${r + 1}=0,0,F{r}/$F${r + 1})", "calc", PCT)
    r += 1
    put(ws, f"A{r}", "Total", bold=True)
    for c in "DEF":
        put(ws, f"{c}{r}", f"=SUM({c}4:{c}{r - 1})", "calc", USD, bold=True)
    put(ws, f"G{r}", f"=SUM(G4:G{r - 1})", "calc", PCT, bold=True)
    ALLOC_TOTAL_ROW = r
    widths(ws, {"A": 16, "B": 24, "C": 34, "D": 16, "E": 18, "F": 16, "G": 14})
    return ws, ALLOC_TOTAL_ROW
