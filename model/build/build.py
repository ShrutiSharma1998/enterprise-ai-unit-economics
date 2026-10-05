# SPDX-License-Identifier: Apache-2.0
"""Build the workbook: python build.py  ->  model/ai-unit-economics-v0.1.xlsx (formulas recalculated by Excel)."""
import os
import openpyxl
import build_inputs as bi
import build_calc as bc
import build_out_a as oa
import build_out_b as ob
import build_out_c as oc
import build_out_d as od
from xl_run import save_and_recalc, errors, scrub_metadata

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "ai-unit-economics-v0.1.xlsx")
ORDER = ["README", "Summary", "Org", "Teams", "Params", "PriceBook", "Lines", "Levers", "Results", "Scenarios", "Sensitivity",
         "Allocation", "Evidence", "Tests", "Calc_Low", "Calc_Base", "Calc_High"]


def build():
    wb = openpyxl.Workbook()
    wb.remove(wb.active)
    bi.build_org(wb); bi.build_params(wb); bi.build_pricebook(wb); bi.build_teams(wb)
    for k in range(3):
        bc.build_calc(wb, k)
    oa.build_results(wb)
    ob.build_scenarios(wb)
    _ws, sens = ob.build_sensitivity(wb)
    off = oc.build_lines(wb)
    oc.build_levers(wb)
    oa.build_allocation(wb)
    oc.build_evidence(wb)
    od.build_tests(wb)
    oa.build_summary(wb, sens, off, od.TESTS["overall"])
    od.build_readme(wb)
    wb._sheets = [wb[n] for n in ORDER]
    for ws in wb.worksheets:
        ws.sheet_view.showGridLines = False if ws.title in ("README", "Summary") else True
    wb.active = 1
    return wb


if __name__ == "__main__":
    path = os.path.abspath(OUT)
    save_and_recalc(build(), path)
    scrub_metadata(path)                      # remove the author name and local path that Excel writes on save
    import openpyxl
    v = openpyxl.load_workbook(path, data_only=True)
    errs = errors(v)
    print("saved", path)
    print("formula errors:", errs[:10])
    t = v["Tests"]
    for r in range(4, 16):
        print(t[f"A{r}"].value, t[f"C{r}"].value, "|", t[f"B{r}"].value)
    print("overall:", t["C16"].value)
