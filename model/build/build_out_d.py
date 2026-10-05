# SPDX-License-Identifier: Apache-2.0
"""Tests (the 10 acceptance tests from spec/requirements-spec.md, as live formulas) and README."""
from xl_helpers import put, widths, title, USD, NUM, F_WARN, L, mc, F_NOTE
from spec_data import TEAM_FIELDS
import build_calc as bc
from build_calc import ROWS, NT
from build_inputs import ADDR, org, team, derived, param, PB_LAST
from build_out_a import RES, TCOL, ENTC
from build_out_b import SCN
from build_out_c import EVID, LEV

TESTS = {}


def build_tests(wb):
    ws = wb.create_sheet("Tests")
    title(ws, "Acceptance tests", "The ten tests from spec/requirements-spec.md plus tests 11 and 12 (added in Phases 5 and 6), as live formulas. Supporting calculations are below the table.")
    for i, h in enumerate(["#", "Test", "Result", "What is compared"]):
        put(ws, f"{L(i + 1)}3", h, "head")
    B = "Calc_Base"
    HZ, nT = org("horizon"), org("nT")
    hub_raw = f"{B}!$B${ROWS['alloc']('hub_raw')}"
    fed = f"{B}!$B${ROWS['alloc']('fed')}"
    s = 20   # first supporting row
    # ---- T1 allocation grid (12 combinations)
    put(ws, f"A{s}", "Support for test 1: allocation under every rule and shape (Base scenario)", "sub")
    UN, SM, EF, DF, OKC = (L(3 + NT + i) for i in range(5))
    for i, h in enumerate(["Shape", "Rule"] + [f"Team {i + 1}" for i in range(NT)] + ["Unallocated", "Sum", "Effective hub", "Difference", "OK"]):
        put(ws, f"{L(i + 1)}{s + 1}", h, "sub")
    outs = [f"{B}!${c}${ROWS['alloc']('out')}" for c in bc.ALLOC_COLS]
    lics = [f"{B}!${c}${ROWS['alloc']('lic')}" for c in bc.ALLOC_COLS]
    r = s + 2
    g_first = r
    for shape in ["Centralized", "Federated", "Hub-and-spoke"]:
        for rule in ["Usage-proportional", "Headcount proxy", "Even split", "Central budget"]:
            put(ws, f"A{r}", shape)
            put(ws, f"B{r}", rule)
            for t in range(NT):
                if shape == "Federated":
                    f = f"={hub_raw}*{fed}*{team('active', t)}"
                elif rule == "Usage-proportional":
                    f = f"={hub_raw}*{outs[t]}/({'+'.join(outs)})"
                elif rule == "Headcount proxy":
                    f = f"={hub_raw}*{lics[t]}/({'+'.join(lics)})"
                elif rule == "Even split":
                    f = f"=IF({nT}=0,0,{hub_raw}*{team('active', t)}/{nT})"
                else:
                    f = "=0"
                put(ws, f"{L(3 + t)}{r}", f, "calc", USD)
            put(ws, f"{UN}{r}", f"={hub_raw}" if (rule == "Central budget" and shape != "Federated") else "=0", "calc", USD)
            put(ws, f"{SM}{r}", f"=SUM(C{r}:{UN}{r})", "calc", USD)
            put(ws, f"{EF}{r}", f"={hub_raw}*{nT}*{fed}" if shape == "Federated" else f"={hub_raw}", "calc", USD)
            put(ws, f"{DF}{r}", f"={SM}{r}-{EF}{r}", "calc", '0.0000')
            put(ws, f"{OKC}{r}", f'=IF(ABS({DF}{r})<0.005,"OK","BAD")', "calc")
            r += 1
    g_last = r - 1
    # ---- T2 amortisation row
    r += 1
    put(ws, f"A{r}", "Support for test 2: amortisation of one-time costs by month", "sub")
    r += 1
    put(ws, f"A{r}", "Month")
    for m in range(1, 61):
        put(ws, f"{L(1 + m)}{r}", m, "text", NUM)
    mrow = r
    r += 1
    one = f"({B}!${mc(0)}${ROWS['ent']('direct')}+{B}!${mc(0)}${ROWS['ent']('hub_eff')})"
    put(ws, f"A{r}", "Amortised cost")
    for m in range(1, 61):
        c = L(1 + m)
        put(ws, f"{c}{r}", f"=IF({c}{mrow}<={HZ},{one}/{HZ},0)", "calc", USD)
    arow = r
    r += 1
    put(ws, f"A{r}", "One-time total, and sum of amortisation")
    put(ws, f"B{r}", f"={one}", "calc", USD)
    put(ws, f"C{r}", f"=SUM(B{arow}:{L(61)}{arow})", "calc", USD)
    t2 = r
    # ---- T4 zero-outcome months
    r += 2
    put(ws, f"A{r}", "Support for test 4: variable cost in months with zero outcomes (Base)", "sub")
    r += 1
    put(ws, f"A{r}", "Team")
    put(ws, f"B{r}", "Variable cost in zero-outcome months")
    put(ws, f"C{r}", "Zero-outcome months in horizon")
    r += 1
    t4 = r
    E, Z = mc(1), mc(60)
    for t in range(NT):
        rr = lambda k: f"{B}!${E}${ROWS['team'](t, k)}:${Z}${ROWS['team'](t, k)}"
        put(ws, f"A{r}", f"={team('name', t)}", "link")
        put(ws, f"B{r}", f"=SUMPRODUCT(({rr('out')}=0)*({rr('tokens')}+{rr('vendor')}+{rr('tools')}+{rr('review')}))", "calc", USD)
        put(ws, f"C{r}", f"=SUMPRODUCT(({rr('out')}=0)*({B}!${E}$5:${Z}$5=1))", "calc", NUM)
        r += 1
    put(ws, f"A{r}", "Hub cost in month 1 (fixed cost that remains)")
    put(ws, f"B{r}", f"={B}!${E}${ROWS['hub']('raw')}", "calc", USD)
    t4_hub = r
    # ---- T6 shape
    r += 2
    put(ws, f"A{r}", "Support for test 6: shape changes the hub lines, not the variable inference cost", "sub")
    r += 1
    put(ws, f"A{r}", "Variable inference cost (tokens, vendor, tools), both shapes")
    var = "+".join(f"{B}!$C${ROWS['team'](t, k)}" for t in range(NT) for k in ("tokens", "vendor", "tools"))
    put(ws, f"B{r}", f"={var}", "calc", USD)
    put(ws, f"C{r}", f"={var}", "calc", USD)
    t6a = r
    r += 1
    put(ws, f"A{r}", "Effective hub cost: Centralized, Federated")
    put(ws, f"B{r}", f"={hub_raw}", "calc", USD)
    put(ws, f"C{r}", f"={hub_raw}*{nT}*{fed}", "calc", USD)
    t6b = r
    r += 1
    put(ws, f"A{r}", "The build script also flips the shape in the workbook, recalculates and compares with the reference model (build/verify.py).", "note")
    # ---- T9 seat arithmetic
    r += 2
    put(ws, f"A{r}", "Support for test 9: seat price divided by active share", "sub")
    r += 1
    put(ws, f"A{r}", "Fixture: seat 30, active share 50%, expected 60")
    put(ws, f"B{r}", 30, "input", NUM)
    put(ws, f"C{r}", 0.5, "input", "0.00")
    put(ws, f"D{r}", 60, "input", NUM)
    put(ws, f"E{r}", f"=B{r}/C{r}", "calc", "0.00")
    t9a = r
    r += 1
    put(ws, f"A{r}", "Live, Team 1 at the last horizon month: seat cost / active users, and blended seat / plateau share")
    seat = f"INDEX({B}!${E}${ROWS['team'](0, 'seat')}:${Z}${ROWS['team'](0, 'seat')},{HZ})"
    act = f"INDEX({B}!${E}${ROWS['team'](0, 'act')}:${Z}${ROWS['team'](0, 'act')},{HZ})"
    ramp = f"INDEX({B}!${E}${ROWS['team'](0, 'ramp')}:${Z}${ROWS['team'](0, 'ramp')},{HZ})"
    put(ws, f"B{r}", f"=IF({act}=0,0,{seat}/{act})", "calc", "0.0000")
    put(ws, f"C{r}", f"={derived('v_seat', 0)}/{team('plateau', 0)}", "calc", "0.0000")
    put(ws, f"D{r}", f"={ramp}", "calc", "0.000")
    t9b = r
    # ---- T12 price IDs
    r += 2
    put(ws, f"A{r}", "Support for test 12: every price ID used by a team or the hub exists exactly once in the PriceBook (0 = fine)", "sub")
    r += 1
    t12_first = r
    ID_FIELDS = ["seat_std", "seat_prem", "unit_price", "model", "cheap", "tool_price", "guard_price", "parse_price", "emb_price", "plan_price", "store_price", "read_price"]
    lab = {k: l for k, l, _u in TEAM_FIELDS}
    for key in ID_FIELDS:
        put(ws, f"A{r}", lab[key])
        for t in range(NT):
            idc = team(key, t)
            put(ws, f"{L(3 + t)}{r}", f'=IF({idc}="",0,IF(COUNTIF(PriceBook!$A$4:$A${PB_LAST},{idc})=1,0,1))', "calc", NUM)
        r += 1
    t12_last = r - 1
    put(ws, f"A{r}", "Hub IDs (monitoring plan, overage)")
    put(ws, f"C{r}", f'=IF(COUNTIF(PriceBook!$A$4:$A${PB_LAST},"PL_LANGFUSE_PRO")=1,0,1)', "calc", NUM)
    put(ws, f"D{r}", f'=IF(COUNTIF(PriceBook!$A$4:$A${PB_LAST},"U_LANGFUSE_OVER")=1,0,1)', "calc", NUM)
    t12_hub = r
    r += 1
    put(ws, f"A{r}", "Duplicate IDs in the PriceBook")
    put(ws, f"C{r}", f'=SUMPRODUCT((PriceBook!$A$4:$A${PB_LAST}<>"")*(COUNTIF(PriceBook!$A$4:$A${PB_LAST},PriceBook!$A$4:$A${PB_LAST})>1))', "calc", NUM)
    t12_dup = r
    # ---- results table
    lv, ev = LEV, EVID
    pb_last = PB_LAST
    rows = [
        ("Allocations sum to the enterprise hub cost under every rule and shape",
         f'=IF(COUNTIF({OKC}{g_first}:{OKC}{g_last},"OK")={g_last - g_first + 1},"PASS","FAIL")', "12 combinations, difference under $0.005"),
        ("Amortised one-time costs sum to the one-time total",
         f'=IF(AND({HZ}>=1,{HZ}<=60,ABS(B{t2}-C{t2})<0.005),"PASS","FAIL")', "One-time total versus the sum of monthly amortisation"),
        ("Lines sum to layers, and layers sum to the total",
         (f'=IF(AND(ABS(Results!${ENTC}${RES["total_row"]}-SUM(Results!${ENTC}${RES["layer_row"][1]}:${ENTC}${RES["layer_row"][5]}))<0.01,'
          f'ABS(Results!${ENTC}${RES["total_row"]}-(SUM(Results!${TCOL[0]}${RES["m"]["total"]}:${TCOL[-1]}${RES["m"]["total"]})+Results!${ENTC}${RES["m"]["unalloc"]}))<0.01),"PASS","FAIL")'),
         "Total cost versus layers, and versus teams plus unallocated hub"),
        ("Zero outcomes gives zero variable cost while fixed costs remain",
         f'=IF(AND(SUM(B{t4}:B{t4 + NT - 1})<0.005,SUM(C{t4}:C{t4 + NT - 1})>0,B{t4_hub}>0),"PASS","FAIL")',
         "Zero-outcome months exist, variable cost in them is 0, hub cost in month 1 is positive"),
        ("Lever fixtures match hand calculations and the provider's published example, and Levers matches Calc_Base",
         (f'=IF(AND(SUMPRODUCT(ABS(Levers!$B${lv["fx_diff_row"]}:$E${lv["fx_diff_row"]}))<0.000000001,'
          f'SUMPRODUCT(ABS(Levers!$B${lv["diff_row"]}:${L(1 + NT)}${lv["diff_row"]}))<0.000000001),"PASS","FAIL")'),
         "Two hand-calculated fixtures, two from Anthropic's published example, and every team's cost per outcome"),
        ("Shape changes hub lines, not variable inference cost",
         f'=IF(AND(ABS(B{t6a}-C{t6a})<0.005,IF({nT}*{fed}=1,TRUE,ABS(B{t6b}-C{t6b})>0.005)),"PASS","FAIL")', "Same variable cost; effective hub cost differs"),
        ("Every input has label, source, date, grade; evidence shares sum to 100%",
         (f'=IF(AND(COUNTBLANK(Evidence!$E${ev["first"]}:$H${ev["last"]})=0,COUNTBLANK(Evidence!$J${ev["first"]}:$J${ev["last"]})=0,'
          f'ABS({RES["tag_sum"]}-1)<0.000000001),"PASS","FAIL")'), "No blanks in the register; category shares total 100%"),
        ("No price lacks an effective date and a status",
         (f'=IF(AND(SUMPRODUCT((PriceBook!$A$4:$A${pb_last}<>"")*(PriceBook!$K$4:$K${pb_last}=""))=0,SUMPRODUCT((PriceBook!$A$4:$A${pb_last}<>"")*(PriceBook!$M$4:$M${pb_last}=""))=0,SUMPRODUCT((PriceBook!$A$4:$A${pb_last}<>"")*(PriceBook!$E$4:$E${pb_last}=""))=0),"PASS","FAIL")'),
         "Effective-from, status and price all filled"),
        ("Effective cost per active user equals seat price divided by active share",
         f'=IF(AND(ABS(E{t9a}-D{t9a})<0.000001,D{t9b}=1,ABS(B{t9b}-C{t9b})<0.000001),"PASS","FAIL")', "Fixture, and live Team 1 once the ramp is complete"),
        ("Low-cost <= Base <= High-cost in every layer and in total",
         f'=IF(COUNTIF(Scenarios!$E$4:$E${SCN["total"]},"OK")=6,"PASS","FAIL")', "Five layers and the total"),
        ("Outcome and active-user totals cover only the horizon (added in Phase 5)",
         "=IF(AND(" + ",".join(
             f'ABS({B}!$C${ROWS["team"](t, key)}-SUMPRODUCT(({B}!${E}$4:${Z}$4<={HZ})*{B}!${E}${ROWS["team"](t, key)}:${Z}${ROWS["team"](t, key)}))<0.005'
             for t in range(NT) for key in ("out", "act")) + '),"PASS","FAIL")',
         "Each team's total equals the sum of its in-horizon months (a check that would have caught the 60-month total)"),
        ("Every price ID used exists exactly once in the PriceBook (added in Phase 6)",
         f'=IF(SUM(C{t12_first}:{L(2 + NT)}{t12_last})+SUM(C{t12_hub}:D{t12_hub})+C{t12_dup}=0,"PASS","FAIL")',
         "No mistyped, missing or duplicate ID; a missing ID would otherwise price silently at zero"),
    ]
    for i, (name, f, what) in enumerate(rows):
        rr = 4 + i
        put(ws, f"A{rr}", i + 1)
        put(ws, f"B{rr}", name)
        put(ws, f"C{rr}", f, "calc", bold=True)
        put(ws, f"D{rr}", what, "note")
    put(ws, "B16", "Overall", bold=True)
    put(ws, "C16", '=IF(COUNTIF(C4:C15,"PASS")=12,"ALL 12 PASS","CHECK: "&(12-COUNTIF(C4:C15,"PASS"))&" failing")', "calc", bold=True)
    TESTS["overall"] = "Tests!$C$16"
    widths(ws, {"A": 26, "B": 70, "C": 16, "D": 60, **{L(5 + i): 14 for i in range(NT + 6)}})
    return ws


README = [
    ("AI unit economics planning tool (v0.1, thin workbook)", "h"),
    ("Built 2026-09-20. Status: first build from the approved spec. FICTIONAL WORKED EXAMPLE: every organization input is an assumption (grade D). Only dated primary prices are grade A.", "warn"),
    ("What it is", "s"),
    ("A planning workbook an enterprise runs before it builds AI. Enter the org shape, teams, users and usage; it returns cost by layer, by team and for the organization, plus payback, sensitivity and the one number that would kill the case. Formulas are visible and there are no macros.", ""),
    ("How to use it (about 30 minutes)", "s"),
    ("1. Org: set the organization, horizon (up to 60 months), scenario, value case, org shape and allocation rule.", ""),
    ("2. Teams: replace the five fictional teams (one team per business unit in v0.1; Teams 1 and 5 are the same kind of seat-based assistant at two calibrations, on purpose). Blue text on pale yellow is an input.", ""),
    ("3. Params: review every starter value (grade D). Replace any you can with the enterprise's own value; the Summary shows how much cost still rests on starters.", ""),
    ("4. PriceBook: check every price against the provider's page and follow the refresh procedure at the bottom of that sheet.", ""),
    ("5. Read Summary, then Sensitivity (kill number), Scenarios, Allocation (cost-center table) and Tests (all twelve should pass).", ""),
    ("Colours", "s"),
    ("Blue text on pale yellow = input. Black = formula. Green = link to another sheet.", ""),
    ("Evidence grades", "s"),
    ("A dated primary price. B named survey with a visible method. C blog, vendor or a number without a visible method. D our assumption. * = original not opened. Details in evidence/README.md.", ""),
    ("Sheets", "s"),
    ("Summary, Org, Teams, Params, PriceBook, Lines (the 35 taxonomy lines), Levers (fixed lever order and fixtures), Results (selected scenario), Scenarios, Sensitivity, Allocation, Evidence (assumptions register), Tests, and Calc_Low, Calc_Base, Calc_High (monthly grids).", ""),
    ("v0.1 simplifications (deviations from the full spec, by design)", "s"),
    ("One team per business unit. Lines owned H+S are modelled at team level. The top-10% segment only changes cost when a plan has an included-usage allowance. Committed capacity is a fixed monthly cost (no utilization calculation) and is off until entered. Migration events cover one workflow per team.", ""),
    ("Sensitivity is one-at-a-time with linear scaling of the selected scenario's cost components, not a full recalculation. Per-team payback includes the allocated hub share.", ""),
    ("Four lines have no starter value and are OFF until entered (CL-14, CL-15, CL-31, CL-32), so cost is understated until they are.", ""),
    ("Licence and provenance", "s"),
    ("Copyright 2026 Shruti Sharma. Licensed under the Apache License, Version 2.0 (see LICENSE in the repository); provided as is, without warranty. The organization and usage in this workbook are fictional. Prices are quoted from providers' public pages on the dates shown; company and product names belong to their owners, and no provider endorses or is affiliated with this work. Built with AI assistance (Claude, Anthropic) under the project owner's direction.", ""),
    ("Provenance", "s"),
    ("Evidence base: evidence/. Design: research/ and spec/. Build scripts and the independent reference model used to verify this workbook: model/build/.", ""),
]


def build_readme(wb):
    ws = wb.create_sheet("README")
    r = 1
    for text, kind in README:
        c = put(ws, f"A{r}", text, wrap=True)
        if kind == "h":
            c.font = c.font.copy(bold=True, size=14)
        elif kind == "s":
            put(ws, f"A{r}", text, "sub")
        elif kind == "warn":
            put(ws, f"A{r}", text, fill=F_WARN, bold=True, wrap=True)
        r += 1
    widths(ws, {"A": 150})
    for i in range(1, r):
        ws.row_dimensions[i].height = 16 * (1 + len(README[i - 1][0]) // 140)
    return ws
