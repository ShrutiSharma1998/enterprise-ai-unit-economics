# SPDX-License-Identifier: Apache-2.0
"""Write app/tests/fixtures.json: the inputs and answers the browser engine must reproduce.

    python app/build/make_fixtures.py

Answers come from the independent Python reference model (model/build/reference_model.py), for the base case and the
same nine variants used to verify the workbook. The workbook's own recalculated Summary values are stored for the
base case, so the engine is compared with both. Run node app/tests/engine.test.js afterwards.
"""
import copy
import json
import pathlib
import sys

import openpyxl

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "model" / "build"))
import reference_model as ref  # noqa: E402
import spec_data as sd  # noqa: E402

OFF = {3: {"active": 0}, 4: {"active": 0}}
SINGLE = {1: {"active": 0}, 2: {"active": 0}, 3: {"active": 0}, 4: {"active": 0}}
# name, org overrides, k, value_k, team overrides
CASES = [
    ("base", {}, 1, 1, None),
    ("federated_usage_base", dict(shape="Federated", alloc="Usage-proportional"), 1, 1, None),
    ("centralized_central_budget", dict(shape="Centralized", alloc="Central budget"), 1, 1, None),
    ("hubspoke_headcount_high", dict(shape="Hub-and-spoke", alloc="Headcount proxy"), 2, 1, None),
    ("hubspoke_even_low_lowvalue", dict(shape="Hub-and-spoke", alloc="Even split"), 0, 0, None),
    ("horizon24_federated_even", dict(horizon=24, shape="Federated", alloc="Even split"), 1, 1, None),
    ("horizon60_highvalue", dict(horizon=60), 1, 2, None),
    ("two_teams_off_hubspoke", {}, 1, 1, OFF),
    ("two_teams_off_federated_even", dict(shape="Federated", alloc="Even split"), 1, 1, OFF),
    ("single_team_headcount", dict(alloc="Headcount proxy"), 1, 1, SINGLE),
    # extra cases that exercise the calculators the worked example does not use
    ("committed_capacity_team", {}, 1, 1, {0: {"buy": "Committed capacity", "cap_cost": 12000}}),
    ("enterprise_entered_costs", {}, 1, 1, None),
]


def expected(r):
    return {
        "total_cost": r["total_cost"], "benefit": r["comp"]["benefit"], "net": r["net"], "unalloc": r["unalloc"],
        "payback": r["payback"], "cpa_ent": r["cpa_ent"], "hub_raw_total": r["hub_raw_total"], "eff_hub": r["eff_hub"],
        "layers": {str(i): v for i, v in r["layers"].items()}, "by_tag": r["by_tag"], "comp": r["comp"],
        "cpo": r["cpo"],
        "teams": [{"direct_total": t["direct_total"], "alloc": t["alloc"], "benefit": t["benefit"], "outcomes": t["outcomes"],
                   "active_months": t["active_months"], "net": t["net"], "payback": t["payback"],
                   "cost_per_outcome": t["cost_per_outcome"], "cpa_month": t["cpa_month"]} for t in r["teams"]],
    }


def workbook_base():
    wb = openpyxl.load_workbook(ROOT / "model" / "ai-unit-economics-v0.1.xlsx", data_only=True)
    s = wb["Summary"]
    return {"total_cost": s["B14"].value, "benefit": s["B15"].value, "net": s["B16"].value, "payback": s["B17"].value,
            "cost_per_outcome": s["B18"].value, "benefit_per_outcome": s["B19"].value, "cpa_ent": s["B20"].value,
            "run_rate_last": s["B21"].value,
            "layers": {str(n): s[f"H{23 + n}"].value for n in range(1, 6)},
            "shares": {"A": s["C38"].value, "R": s["C39"].value, "S": s["C40"].value, "E": s["C41"].value},
            "tests": s["B49"].value}


def main():
    fixtures = []
    for name, org_over, k, vk, team_over in CASES:
        org = {key: v[1] for key, v in sd.ORG.items()}
        org.update(org_over)
        teams = copy.deepcopy(sd.TEAMS)
        for i, ov in (team_over or {}).items():
            teams[i].update(ov)
        params_over = None
        if name == "enterprise_entered_costs":
            params_over = {"env_month": 9000, "comp_year": 60000, "lic_year": 120000}
            saved = {key: list(sd.PARAMS[key]) for key in params_over}
            for key, val in params_over.items():
                p = list(sd.PARAMS[key])
                p[2] = p[3] = p[4] = val
                sd.PARAMS[key] = tuple(p)
        r = ref.run(k, org_over={x: y for x, y in org_over.items() if x in ("shape", "alloc", "horizon")}, team_over=team_over, value_k=vk)
        if params_over:
            for key, val in saved.items():
                sd.PARAMS[key] = tuple(val)
        fixtures.append({"name": name, "k": k, "valueK": vk, "org": org, "teams": teams, "paramsOverride": params_over,
                         "expected": expected(r)})
    out = ROOT / "app" / "tests" / "fixtures.json"
    out.write_text(json.dumps({"workbookBase": workbook_base(), "cases": fixtures}, indent=1), encoding="utf-8", newline="\n")
    print("wrote", out, "with", len(fixtures), "cases")


if __name__ == "__main__":
    main()
