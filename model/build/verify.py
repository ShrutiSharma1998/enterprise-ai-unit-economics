# SPDX-License-Identifier: Apache-2.0
"""Verify the workbook against the independent reference model, and check that the acceptance tests can fail.

  python verify.py base <tmpdir>        compare the base build
  python verify.py variants <tmpdir>    flip shape, rule, scenario, value case, horizon; compare each with the reference
  python verify.py mutations <tmpdir>   break inputs on purpose; the matching test must turn FAIL
"""
import os
import sys
import openpyxl
import build as B
import build_inputs as bi
import build_out_a as oa
import build_out_b as ob
import build_out_c as oc
import reference_model as ref
from xl_run import save_and_recalc, cell, errors

SCEN = ["Low-cost", "Base", "High-cost"]
VALUE = ["Low", "Base", "High"]


def apply_org(wb, over):
    for key, val in over.items():
        wb["Org"][cell(bi.ADDR["org"][key])].value = val


def compare(v, k, org_over, value_k, team_over=None):
    r = ref.run(k, org_over={x: y for x, y in org_over.items() if x in ("shape", "alloc", "horizon")}, team_over=team_over, value_k=value_k)
    res, RES = v["Results"], oa.RES
    chk = [("total cost", res[f"{oa.ENTC}{RES['total_row']}"].value, r["total_cost"]),
           ("benefit", res[f"{oa.ENTC}{RES['m']['benefit']}"].value, r["comp"]["benefit"]),
           ("net", res[f"{oa.ENTC}{RES['m']['net']}"].value, r["net"]),
           ("unallocated", res[f"{oa.ENTC}{RES['m']['unalloc']}"].value, r["unalloc"])]
    for n in range(1, 6):
        chk.append((f"layer {n}", res[f"{oa.ENTC}{RES['layer_row'][n]}"].value, r["layers"][n]))
    for tag in "ASRE":
        chk.append((f"tag {tag}", res[f"D{RES['tag_row'][tag]}"].value, r["by_tag"][tag]))
    for t in range(bi.NT):
        chk.append((f"team{t} total", res[f"{oa.TCOL[t]}{RES['m']['total']}"].value, r["teams"][t]["direct_total"] + r["teams"][t]["alloc"]))
        chk.append((f"team{t} net", res[f"{oa.TCOL[t]}{RES['m']['net']}"].value, r["teams"][t]["net"]))
    sen = v["Sensitivity"]
    c = r["comp"]
    n0 = c["benefit"] - c["cost"]
    chk.append(("sensitivity N0", sen["B6"].value, n0))
    for i, e in enumerate([c["benefit"], c["benefit"], c["benefit"], c["benefit"] - c["vol"], -c["tokens"], -c["review"], -c["effort"]]):
        chk.append((f"sensitivity effect {i}", sen[f"B{ob.SENS['r0'] + i}"].value, e))
    chk.append(("cost per active user (enterprise)", res[f"{oa.ENTC}{RES['m']['cpa']}"].value, r["cpa_ent"]))
    for t in range(bi.NT):
        got = res[f"{oa.TCOL[t]}{RES['m']['cpa']}"].value
        exp = r["teams"][t]["cpa_month"]
        if exp is None:
            if got != "n/a":
                chk.append((f"team{t} cpa should be n/a", 0.0 if got != "n/a" else 0.0, 1.0))
        else:
            chk.append((f"team{t} cost per active user", got, exp))
    pb = res[f"{oa.ENTC}{RES['m']['payback']}"].value
    exp_pb = r["payback"] if r["payback"] is not None else "None"
    bad = [(n, g, e) for n, g, e in chk if g is None or abs(g - e) > 1e-6 * max(1, abs(e))]
    if pb != exp_pb:
        bad.append(("payback", pb, exp_pb))
    return len(chk) + 1, bad


def run_variant(tmp, name, over, k, value_k, team_over=None):
    wb = B.build()
    apply_org(wb, over)
    for t, ov in (team_over or {}).items():
        for key, val in ov.items():
            wb["Teams"][f"{bi.ADDR['team_cols'][t]}{bi.ADDR['team_row'][key]}"].value = val
    path = os.path.join(tmp, f"variant_{name}.xlsx")
    v = save_and_recalc(wb, path)
    n, bad = compare(v, k, over, value_k, team_over)
    tests = v["Tests"]["C16"].value
    errs = errors(v)
    ok = not bad and not errs and tests == "ALL 12 PASS"
    print(f"{'OK ' if ok else 'BAD'} {name:38s} compared {n:2d} values, mismatches {len(bad)}, errors {len(errs)}, tests: {tests}")
    for b in bad[:6]:
        print("     ", b)
    return ok


OFF = {3: {"active": 0}, 4: {"active": 0}}
SINGLE = {1: {"active": 0}, 2: {"active": 0}, 3: {"active": 0}, 4: {"active": 0}}


def active_variants(tmp):
    cases = [
        ("two_teams_off_hubspoke", dict(), 1, 1, OFF),
        ("two_teams_off_federated_even", dict(shape="Federated", alloc="Even split"), 1, 1, OFF),
        ("single_team_headcount", dict(alloc="Headcount proxy"), 1, 1, SINGLE),
    ]
    return all(run_variant(tmp, n, o, k, vk, to) for n, o, k, vk, to in cases)


def variants(tmp):
    cases = [
        ("federated_usage_base", dict(shape="Federated", alloc="Usage-proportional"), 1, 1),
        ("centralized_central_budget", dict(shape="Centralized", alloc="Central budget"), 1, 1),
        ("hubspoke_headcount_high", dict(shape="Hub-and-spoke", alloc="Headcount proxy", scenario="High-cost"), 2, 1),
        ("hubspoke_even_low_lowvalue", dict(shape="Hub-and-spoke", alloc="Even split", scenario="Low-cost", value_case="Low"), 0, 0),
        ("horizon24_federated_even", dict(horizon=24, shape="Federated", alloc="Even split"), 1, 1),
        ("horizon60_highvalue", dict(horizon=60, value_case="High"), 1, 2),
    ]
    return all(run_variant(tmp, n, o, k, vk) for n, o, k, vk in cases)


def mutation(tmp, name, mutate, test_row):
    wb = B.build()
    mutate(wb)
    path = os.path.join(tmp, f"mut_{name}.xlsx")
    v = save_and_recalc(wb, path)
    got = v["Tests"][f"C{test_row}"].value
    ok = got == "FAIL"
    print(f"{'OK ' if ok else 'BAD'} mutation {name:34s} test {test_row - 3} result: {got} (expected FAIL); overall: {v['Tests']['C16'].value}")
    return ok


def mutations(tmp):
    def blank_status(wb):
        wb["PriceBook"]["M6"].value = None

    def blank_label(wb):
        wb["Evidence"][f"E{oc.EVID['first'] + 3}"].value = None

    def wrong_fixture(wb):
        wb["Levers"][f"B{oc.LEV['fx_exp_row']}"].value = 0.5

    def break_scenario_order(wb):
        p = bi.ADDR["param_row"]["plat_pd"]
        wb["Params"][f"D{p}"].value = 5000   # low-cost platform effort above base: Low > Base

    def unmasked_total(wb):
        import build_calc as bc
        row = bc.ROWS["team"](1, "out")
        wb["Calc_Base"][f"C{row}"].value = f"=SUM(D{row}:BL{row})"   # the original bug: totals all 60 months

    def wrong_provider_example(wb):
        wb["Levers"][f"D{oc.LEV['fx_exp_row']}"].value = 0.705    # published total including the $0.08 runtime

    def mistyped_price_id(wb):
        wb["Teams"][f"{bi.ADDR['team_cols'][0]}{bi.ADDR['team_row']['model']}"].value = "M_SONET5"   # typo: would price at zero silently

    def duplicate_price_id(wb):
        wb["PriceBook"]["A7"].value = wb["PriceBook"]["A6"].value      # two rows, one ID

    return all([
        mutation(tmp, "mistyped_price_id", mistyped_price_id, 15),
        mutation(tmp, "duplicate_price_id", duplicate_price_id, 15),
        mutation(tmp, "outcomes_total_all_60_months", unmasked_total, 14),
        mutation(tmp, "provider_example_includes_runtime", wrong_provider_example, 8),
        mutation(tmp, "blank_price_status", blank_status, 11),
        mutation(tmp, "blank_evidence_label", blank_label, 10),
        mutation(tmp, "wrong_fixture_expected", wrong_fixture, 8),
        mutation(tmp, "low_scenario_above_base", break_scenario_order, 13),
    ])


if __name__ == "__main__":
    mode, tmp = sys.argv[1], sys.argv[2]
    os.makedirs(tmp, exist_ok=True)
    if mode == "base":
        wb = B.build()
        v = save_and_recalc(wb, os.path.join(tmp, "base.xlsx"))
        n, bad = compare(v, 1, {}, 1)
        print("base: compared", n, "mismatches", len(bad), "errors", len(errors(v)), "tests", v["Tests"]["C16"].value)
        ok = not bad
    elif mode == "variants":
        ok = variants(tmp) and active_variants(tmp)
    elif mode == "active":
        ok = active_variants(tmp)
    else:
        ok = mutations(tmp)
    sys.exit(0 if ok else 1)
