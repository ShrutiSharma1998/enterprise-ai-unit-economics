# SPDX-License-Identifier: Apache-2.0
"""Calc sheets: one per scenario (k = 0 low-cost, 1 base, 2 high-cost). Monthly grid, months 0..60."""
from spec_data import TEAMS
from xl_helpers import put, widths, title, mc, USD, NUM, NUM2, PCT, C0, C1, CN, L
from build_inputs import ADDR, org, param, team, derived, pbv, NT

NAMES = ["Calc_Low", "Calc_Base", "Calc_High"]
SCEN_LABEL = ["Low-cost", "Base", "High-cost"]

TEAM_START, TEAM_H = 8, 27
# (key, label, tag, format). Row offset = index within the block (0 is the header row).
TEAM_ROWS = [
    ("hdr", "", "", None), ("ramp", "Ramp factor", "", "0.000"), ("lic", "Licensed users", "", NUM), ("act", "Active users", "", NUM),
    ("out", "Outcomes", "", NUM),
    ("seat", "Seats (CL-21)", "A", USD), ("tokens", "Model tokens incl. retries and agent steps (CL-16, CL-17)", "A", USD),
    ("vendor", "Vendor per-outcome price (CL-22)", "A", USD), ("tools", "Tool and guardrail calls (CL-18, CL-19)", "A", USD),
    ("cap", "Committed capacity (CL-15)", "E", USD), ("data_price", "Parsing, embeddings, index, retrieval (CL-05 to CL-08)", "A", USD),
    ("data_effort", "Connector upkeep (CL-03)", "S", USD), ("run_effort", "Quality review, maintenance, support (CL-25, CL-27, CL-28)", "S", USD),
    ("migration", "Model migration events (CL-26)", "R", USD), ("review", "Human review of output (CL-34)", "R", USD),
    ("cm", "Change champions (CL-35)", "S", USD), ("ot_data_effort", "One-time: assess, clean, connect (CL-01 to CL-03)", "S", USD),
    ("ot_data_load", "One-time: initial parse and embed (CL-05, CL-06)", "A", USD), ("ot_l2", "One-time: integrate, evaluation harness (CL-10, CL-12)", "S", USD),
    ("ot_train", "One-time: training (CL-33)", "S", USD), ("benefit", "Benefit", "", USD),
    ("direct", "Direct cost", "", USD), ("hub_alloc", "Allocated hub cost", "", USD), ("net", "Net cash", "", USD),
    ("cum", "Cumulative net cash", "", USD), ("pb", "Payback flag (month)", "", NUM),
]
TOFF = {k: i for i, (k, *_r) in enumerate(TEAM_ROWS)}
COST_KEYS = [k for k, _l, tag, _f in TEAM_ROWS if tag]
HUB_START = TEAM_START + NT * TEAM_H
HUB_ROWS = [
    ("hdr", "", "", None), ("all_out", "All-team outcomes", "", NUM),
    ("plat_ot", "One-time: platform or gateway (CL-09)", "S", USD), ("perm_ot", "One-time: permission mapping (CL-04)", "S", USD),
    ("rev_ot", "One-time: security, privacy, legal review (CL-11)", "S", USD), ("rt_ot", "One-time: red-teaming (CL-13)", "S", USD),
    ("plat_run", "Platform run (CL-09)", "S", USD), ("perm_up", "Permission upkeep (CL-04)", "S", USD), ("rt_rep", "Red-team repeat (CL-13)", "S", USD),
    ("env", "Environments (CL-14)", "E", USD), ("mon", "Monitoring and observability (CL-24)", "A", USD),
    ("plat_team", "Platform team (CL-29)", "S", USD), ("gov", "Cost governance (CL-30)", "R", USD),
    ("comp", "Compliance audit (CL-31)", "E", USD), ("lic", "Platform and vendor licences (CL-32)", "E", USD), ("raw", "Hub cost, raw", "", USD),
]
HOFF = {k: i for i, (k, *_r) in enumerate(HUB_ROWS)}
HUB_COST_KEYS = [k for k, _l, tag, _f in HUB_ROWS if tag]
ALLOC_START = HUB_START + len(HUB_ROWS) + 2
ENT_START = ALLOC_START + 12
ENT_ROWS = ["hdr", "benefit", "direct", "hub_eff", "net", "cum", "pb", "runrate"]
EOFF = {k: i for i, k in enumerate(ENT_ROWS)}
AOFF = {"hdr": 0, "out": 1, "lic": 2, "share": 3, "hub_raw": 4, "fed": 5, "alloc": 6, "eff": 7, "f": 8, "factor": 9}

ROWS = {"team": lambda t, k: TEAM_START + t * TEAM_H + TOFF[k], "hub": lambda k: HUB_START + HOFF[k],
        "alloc": lambda k: ALLOC_START + AOFF[k], "ent": lambda k: ENT_START + EOFF[k]}
ALLOC_COLS = [L(2 + i) for i in range(NT)]     # teams in the allocation table
ALLOC_UNALLOC, ALLOC_TOTAL = L(2 + NT), L(3 + NT)


def build_calc(wb, k):
    ws = wb.create_sheet(NAMES[k])
    title(ws, f"Calc: {SCEN_LABEL[k]} scenario" + (" (stress case: every parameter at its high value at once)" if k == 2 else ""), "Monthly grid. Month 0 holds one-time costs; months 1 to 60 are masked by the horizon. All values are formulas.")
    PD, HRS, WD = org("pd_rate"), org("hours_day"), org("work_days")
    hourly = f"({PD}/{HRS})"
    HZ = org("horizon")
    put(ws, "A4", "Month", "head")
    put(ws, "B4", "Tag", "head")
    put(ws, "C4", "Total", "head")
    put(ws, f"{mc(0)}4", 0, "head")
    put(ws, "A5", "In horizon (1/0)")
    for m in range(1, 61):
        c = mc(m)
        put(ws, f"{c}4", f"={mc(m - 1)}4+1", "head")
        put(ws, f"{c}5", f"=IF({c}$4<={HZ},1,0)", "calc", NUM)
    # ---------------- teams
    for t in range(NT):
        R = lambda key: ROWS["team"](t, key)
        T = lambda key: team(key, t)
        Dv = lambda key: derived(key, t)
        r0 = R("hdr")
        put(ws, f"A{r0}", f"={T('name')}", "link", bold=True)
        put(ws, f"B{r0}", "Token cost per outcome:", "note")
        scale = f"(1-{T('ctx')})*{param('tok_mult', k)}*{param('retry', k)}*IF({T('agentic')}=\"Yes\",{param('steps', k)},1)"
        put(ws, f"C{r0}", f"=({T('tok_in')}*{scale}*{Dv('p_in')}*{Dv('f_cache')}+{T('tok_out')}*{scale}*{Dv('p_out')})/1000000*{Dv('f_batch')}*{T('resid')}",
            "calc", '$#,##0.0000')
        cpo = f"$C${r0}"
        for key, label, tag, fmt in TEAM_ROWS[1:]:
            r = R(key)
            put(ws, f"A{r}", label)
            if tag:
                put(ws, f"B{r}", tag, "note")
        hh = lambda c: f"{c}$5"
        mm = lambda c: f"{c}$4"
        for m in range(1, 61):
            c = mc(m)
            rr = lambda key: f"{c}{R(key)}"
            st = f"{mm(c)}>={Dv('d_start')}"
            x = f"MIN(1,({mm(c)}-{Dv('d_start')}+1)/{T('ramp')})"
            f = {
                "ramp": f"=IF({mm(c)}<{Dv('d_start')},0,IF({T('curve')}=\"S\",{x}^2*(3-2*{x}),{x}))",
                "lic": f"=IF({st},{T('licensed')},0)",
                "act": f"={rr('lic')}*{T('plateau')}*{rr('ramp')}",
                "out": f"=IF({T('basis')}=\"per user\",{rr('act')}*{T('o_user')},{T('direct')}*{rr('ramp')})",
                "seat": f"={hh(c)}*{Dv('d_seat')}*{rr('lic')}*{Dv('v_seat')}",
                "tokens": (f"={hh(c)}*IF({Dv('d_usage')}=1,{rr('act')}*((1-{T('top_share')})*MAX(0,{Dv('o_rest')}*{cpo}-{T('allow')})"
                           f"+{T('top_share')}*MAX(0,{Dv('o_top')}*{cpo}-{T('allow')})),IF({Dv('d_ptok')}=1,{rr('out')}*{cpo},0))"),
                "vendor": f"={hh(c)}*{Dv('d_vendor')}*{rr('out')}*{Dv('v_unit')}",
                "tools": f"={hh(c)}*{Dv('d_api')}*{rr('out')}*{Dv('u_other')}",
                "cap": f"={hh(c)}*{Dv('d_cap')}*{T('cap_cost')}*IF({st},1,0)",
                "data_price": (f"={hh(c)}*IF(AND({st},{T('own_index')}=1),{T('ndocs')}*{param('change_rate', k)}*{T('pages')}*{Dv('v_parse')}"
                               f"+{T('ndocs')}*{param('change_rate', k)}*{T('emb_tok')}*{Dv('v_emb')}/1000000+{Dv('v_plan')}+{T('gb')}*{Dv('v_store')}"
                               f"+{rr('out')}*{T('read_units')}*{Dv('v_readp')}/1000000,0)"),
                "data_effort": f"={hh(c)}*IF({st},{T('nsrc')}*{param('conn_pd', k)}*{PD}*{param('conn_up', k)}/12,0)",
                "run_effort": (f"={hh(c)}*IF({st},{param('evalcases', k)}*{param('eval_min', k)}/60*{hourly}+{param('maint', k)}/12*{param('int_pd', k)}*{PD}"
                               f"+{rr('act')}/1000*{param('tickets', k)}*{param('tkt_hours', k)}*{hourly},0)"),
                "migration": (f"={hh(c)}*IF(AND({mm(c)}>{Dv('d_start')},MOD({mm(c)}-{Dv('d_start')},MAX(1,ROUND({param('mig_int', k)},0)))=0),"
                              f"({param('mig_pd', k)}+{param('eval_rerun', k)}*{param('eval_pd', k)})*{PD},0)"),
                "review": f"={hh(c)}*{rr('out')}*MIN(1,{T('review')}*{param('rev_mult', k)})*{param('rev_min', k)}/60*{T('rev_rate')}",
                "cm": (f"={hh(c)}*IF({st},{rr('lic')}/1000*IF({mm(c)}-{Dv('d_start')}<6,{param('cm_ramp', k)},{param('cm_after', k)})*{PD}*{WD}/12,0)"),
                "benefit": (f"={hh(c)}*{rr('out')}*{T('min_saved')}/60*{T('b_rate')}*INDEX(Params!$D${ADDR['param_row']['realise']}:$F${ADDR['param_row']['realise']},{org('val_idx')})*{T('accept')}"),
            }
            for key, formula in f.items():
                fmt = dict((a, d) for a, _l, _t, d in TEAM_ROWS)[key]
                put(ws, f"{c}{R(key)}", formula, "calc", fmt)
        # month 0: one-time rows
        d0 = mc(0)
        ot = {
            "ot_data_effort": f"={T('active')}*(({T('nsrc')}*{param('src_pd', k)}+{T('ndocs')}/100000*{param('clean_pd', k)}+{T('nsrc')}*{param('conn_pd', k)})*{PD})",
            "ot_data_load": f"={T('active')}*({T('own_index')}*({T('ndocs')}*{T('pages')}*{Dv('v_parse')}+{T('ndocs')}*{T('emb_tok')}*{Dv('v_emb')}/1000000))",
            "ot_l2": f"={T('active')}*(({param('int_pd', k)}+{param('eval_pd', k)})*{PD})",
            "ot_train": f"={T('active')}*({T('licensed')}*{T('plateau')}*{param('train_hours', k)}*{hourly})",
        }
        for key, formula in ot.items():
            put(ws, f"{d0}{R(key)}", formula, "calc", USD)
        # direct, allocation, net, cumulative, payback across month 0..60
        f_i = f"${ALLOC_COLS[t]}${ROWS['alloc']('f')}"
        for m in range(0, 61):
            c = mc(m)
            put(ws, f"{c}{R('direct')}", f"=SUM({c}{R('seat')}:{c}{R('ot_train')})", "calc", USD)
            put(ws, f"{c}{R('hub_alloc')}", f"={f_i}*{c}{ROWS['hub']('raw')}", "calc", USD)
            put(ws, f"{c}{R('net')}", f"={c}{R('benefit')}-{c}{R('direct')}-{c}{R('hub_alloc')}", "calc", USD)
            put(ws, f"{c}{R('cum')}", f"={c}{R('net')}" if m == 0 else f"={mc(m - 1)}{R('cum')}+{c}{R('net')}", "calc", USD)
            if m >= 1:
                put(ws, f"{c}{R('pb')}", f"=IF(AND({c}$4<={HZ},{c}{R('cum')}>=0),{c}$4,\"\")", "calc", NUM)
        for key in ["benefit", "direct", "hub_alloc", "net"] + COST_KEYS:
            put(ws, f"C{R(key)}", f"=SUM({mc(0)}{R(key)}:{mc(60)}{R(key)})", "calc", dict((a, d) for a, _l, _t, d in TEAM_ROWS)[key])
        # state rows (not masked by the horizon flag): total only the in-horizon months
        for key in ["act", "out"]:
            put(ws, f"C{R(key)}", f"=SUMPRODUCT({mc(1)}{R(key)}:{mc(60)}{R(key)},{mc(1)}$5:{mc(60)}$5)", "calc", NUM)
        put(ws, f"C{R('pb')}", f"=IF(COUNT({mc(1)}{R('pb')}:{mc(60)}{R('pb')})=0,\"None\",MIN({mc(1)}{R('pb')}:{mc(60)}{R('pb')}))", "calc", NUM)
    # ---------------- hub
    Hr = lambda key: ROWS["hub"](key)
    put(ws, f"A{Hr('hdr')}", "Hub (shared platform, data and governance costs)", "sub")
    for key, label, tag, fmt in HUB_ROWS[1:]:
        put(ws, f"A{Hr(key)}", label)
        if tag:
            put(ws, f"B{Hr(key)}", tag, "note")
    nsrc_rng = f"SUMPRODUCT(Teams!${ADDR['team_cols'][0]}${ADDR['team_row']['active']}:${ADDR['team_cols'][-1]}${ADDR['team_row']['active']},Teams!${ADDR['team_cols'][0]}${ADDR['team_row']['nsrc']}:${ADDR['team_cols'][-1]}${ADDR['team_row']['nsrc']})"
    nT = org("nT")
    d0 = mc(0)
    put(ws, f"{d0}{Hr('plat_ot')}", f"={param('plat_pd', k)}*{PD}", "calc", USD)
    put(ws, f"{d0}{Hr('perm_ot')}", f"={nsrc_rng}*{param('perm_pd', k)}*{PD}", "calc", USD)
    put(ws, f"{d0}{Hr('rev_ot')}", f"=({nT}*{param('rev_uc_pd', k)}+{param('rev_once_pd', k)})*{PD}", "calc", USD)
    put(ws, f"{d0}{Hr('rt_ot')}", f"={nT}*{param('rt_pd', k)}*{PD}", "calc", USD)
    plan, over = pbv('"PL_LANGFUSE_PRO"', "E"), pbv('"U_LANGFUSE_OVER"', "E")
    incl = pbv('"PL_LANGFUSE_PRO"', "R")
    for m in range(1, 61):
        c = mc(m)
        h = f"{c}$5"
        put(ws, f"{c}{Hr('all_out')}", "=" + "+".join(f"{c}{ROWS['team'](t, 'out')}" for t in range(NT)), "calc", NUM)
        put(ws, f"{c}{Hr('plat_run')}", f"={h}*${d0}${Hr('plat_ot')}*{param('plat_run', k)}/12", "calc", USD)
        put(ws, f"{c}{Hr('perm_up')}", f"={h}*${d0}${Hr('perm_ot')}*{param('perm_up', k)}/12", "calc", USD)
        put(ws, f"{c}{Hr('rt_rep')}", f"={h}*${d0}${Hr('rt_ot')}*{param('rt_rep', k)}/12", "calc", USD)
        put(ws, f"{c}{Hr('env')}", f"={h}*{param('env_month', k)}", "calc", USD)
        put(ws, f"{c}{Hr('mon')}", f"={h}*({plan}+MAX(0,{c}{Hr('all_out')}*{org('obs_per_out')}-{incl})/100000*{over})", "calc", USD)
        put(ws, f"{c}{Hr('plat_team')}", f"={h}*{param('plat_fte', k)}*{PD}*{WD}/12", "calc", USD)
        put(ws, f"{c}{Hr('gov')}", f"={h}*{param('gov_fte', k)}*{PD}*{WD}/12", "calc", USD)
        put(ws, f"{c}{Hr('comp')}", f"={h}*{param('comp_year', k)}/12", "calc", USD)
        put(ws, f"{c}{Hr('lic')}", f"={h}*{param('lic_year', k)}/12", "calc", USD)
    for m in range(0, 61):
        c = mc(m)
        put(ws, f"{c}{Hr('raw')}", f"=SUM({c}{Hr('plat_ot')}:{c}{Hr('lic')})", "calc", USD)
    for key in HUB_COST_KEYS + ["raw"]:
        put(ws, f"C{Hr(key)}", f"=SUM({mc(0)}{Hr(key)}:{mc(60)}{Hr(key)})", "calc", USD)
    put(ws, f"C{Hr('all_out')}", f"=SUMPRODUCT({mc(1)}{Hr('all_out')}:{mc(60)}{Hr('all_out')},{mc(1)}$5:{mc(60)}$5)", "calc", NUM)
    # ---------------- allocation table
    Ar = lambda key: ROWS["alloc"](key)
    put(ws, f"A{Ar('hdr')}", "Allocation of hub cost (selected shape and rule)", "sub")
    labels = {"out": "Outcomes over horizon", "lic": "Licensed users", "share": "Share under the selected rule", "hub_raw": "Hub raw total",
              "fed": "Federated platform share (per unit)", "alloc": "Allocated hub cost (teams, unallocated, total)", "eff": "Effective hub cost (after shape)",
              "f": "Team share of raw hub cost", "factor": "Shape factor on raw hub cost"}
    for key, lab in labels.items():
        put(ws, f"A{Ar(key)}", lab)
    fed, shape, rule = param("fed_dup", k), org("shape"), org("alloc")
    raw_total = f"$B${Ar('hub_raw')}"
    put(ws, f"B{Ar('hub_raw')}", f"=C{Hr('raw')}", "calc", USD)
    put(ws, f"B{Ar('fed')}", f"={fed}", "calc", PCT)
    put(ws, f"B{Ar('factor')}", f"=IF({shape}=\"Federated\",{nT}*{fed},1)", "calc", "0.00")
    put(ws, f"B{Ar('eff')}", f"={raw_total}*B{Ar('factor')}", "calc", USD)
    for t in range(NT):
        c = ALLOC_COLS[t]
        put(ws, f"{c}{Ar('out')}", f"=C{ROWS['team'](t, 'out')}", "calc", NUM)
        put(ws, f"{c}{Ar('lic')}", f"={derived('d_lic', t)}", "link", NUM)
        put(ws, f"{c}{Ar('share')}", (f"=IF({rule}=\"Usage-proportional\",{c}{Ar('out')}/SUM(${ALLOC_COLS[0]}{Ar('out')}:${ALLOC_COLS[-1]}{Ar('out')}),"
                                    f"IF({rule}=\"Headcount proxy\",{c}{Ar('lic')}/SUM(${ALLOC_COLS[0]}{Ar('lic')}:${ALLOC_COLS[-1]}{Ar('lic')}),"
                                    f"IF({rule}=\"Even split\",IF({nT}=0,0,{team('active', t)}/{nT}),0)))"), "calc", PCT)
        put(ws, f"{c}{Ar('alloc')}", f"=IF({shape}=\"Federated\",{raw_total}*$B{Ar('fed')}*{team('active', t)},{raw_total}*{c}{Ar('share')})", "calc", USD)
        put(ws, f"{c}{Ar('f')}", f"=IF({raw_total}=0,0,{c}{Ar('alloc')}/{raw_total})", "calc", "0.0000")
    put(ws, f"{ALLOC_UNALLOC}{Ar('alloc')}", f"=IF(AND({shape}<>\"Federated\",{rule}=\"Central budget\"),{raw_total},0)", "calc", USD)
    put(ws, f"{ALLOC_TOTAL}{Ar('alloc')}", f"=SUM(B{Ar('alloc')}:{ALLOC_UNALLOC}{Ar('alloc')})", "calc", USD)
    put(ws, f"{ALLOC_UNALLOC}{Ar('f')}", f"=IF({raw_total}=0,0,{ALLOC_UNALLOC}{Ar('alloc')}/{raw_total})", "calc", "0.0000")
    put(ws, f"{ALLOC_UNALLOC}{Ar('hdr')}", "Unallocated", "note")
    put(ws, f"{ALLOC_TOTAL}{Ar('hdr')}", "Total", "note")
    # ---------------- enterprise
    Er = lambda key: ROWS["ent"](key)
    put(ws, f"A{Er('hdr')}", "Enterprise", "sub")
    lab = {"benefit": "Benefit", "direct": "Team direct cost", "hub_eff": "Hub cost after shape", "net": "Net cash", "cum": "Cumulative net cash",
           "pb": "Payback flag (month)", "runrate": "Run-rate at the last horizon month (team direct + hub)"}
    for key, text in lab.items():
        put(ws, f"A{Er(key)}", text)
    for m in range(0, 61):
        c = mc(m)
        put(ws, f"{c}{Er('benefit')}", "=" + "+".join(f"{c}{ROWS['team'](t, 'benefit')}" for t in range(NT)), "calc", USD)
        put(ws, f"{c}{Er('direct')}", "=" + "+".join(f"{c}{ROWS['team'](t, 'direct')}" for t in range(NT)), "calc", USD)
        put(ws, f"{c}{Er('hub_eff')}", f"={c}{Hr('raw')}*$B${Ar('factor')}", "calc", USD)
        put(ws, f"{c}{Er('net')}", f"={c}{Er('benefit')}-{c}{Er('direct')}-{c}{Er('hub_eff')}", "calc", USD)
        put(ws, f"{c}{Er('cum')}", f"={c}{Er('net')}" if m == 0 else f"={mc(m - 1)}{Er('cum')}+{c}{Er('net')}", "calc", USD)
        if m >= 1:
            put(ws, f"{c}{Er('pb')}", f"=IF(AND({c}$4<={HZ},{c}{Er('cum')}>=0),{c}$4,\"\")", "calc", NUM)
    for key in ["benefit", "direct", "hub_eff", "net"]:
        put(ws, f"C{Er(key)}", f"=SUM({mc(0)}{Er(key)}:{mc(60)}{Er(key)})", "calc", USD)
    put(ws, f"C{Er('pb')}", f"=IF(COUNT({mc(1)}{Er('pb')}:{mc(60)}{Er('pb')})=0,\"None\",MIN({mc(1)}{Er('pb')}:{mc(60)}{Er('pb')}))", "calc", NUM)
    put(ws, f"C{Er('runrate')}",
        f"=INDEX({mc(1)}{Er('direct')}:{mc(60)}{Er('direct')},{HZ})+INDEX({mc(1)}{Er('hub_eff')}:{mc(60)}{Er('hub_eff')},{HZ})", "calc", USD)
    widths(ws, {"A": 58, "B": 22, "C": 16})
    ws.column_dimensions.group(mc(1), mc(60), hidden=False)
    ws.freeze_panes = f"{mc(0)}6"
    return ws
