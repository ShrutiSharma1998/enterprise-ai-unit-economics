# SPDX-License-Identifier: Apache-2.0
"""Write app/js/data.js from the workbook's single source of inputs (model/build/spec_data.py).

    python app/build/export_data.py

The calculator and the workbook therefore start from the same parameters, price book and fictional example.
Run this again whenever spec_data.py changes; the engine test fails if the two drift apart.
"""
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "model" / "build"))
import spec_data as sd  # noqa: E402

PRICE_DATE = "2026-09-20"   # the date the price book was fetched (spec_data.py)

# Org fields carried by the Excel template, in template row order. "scenario" and "value_case" are left out: the
# calculator picks those from the on-screen toggle, not from a stored default, to keep the template shorter.
TEMPLATE_ORG_FIELDS = ["name", "shape", "alloc", "horizon", "pd_rate", "hours_day", "work_days", "obs_per_out"]
TEMPLATE_ENTERPRISE_FIELDS = ["env_month", "comp_year", "lic_year"]
# Fields a team column must have a valid value for; every other field falls back to the chosen archetype's
# starter value (with a warning) if the cell is missing or blank.
TEMPLATE_REQUIRED_TEAM_FIELDS = ["archetype", "buy", "licensed", "plateau", "basis", "min_saved"]

ARCHETYPES = [
    # code, name, buying model default, review share (spec/starter-values.md, CL-34), worked-example team index or None, note
    ("A1", "Knowledge-worker assistant", "Seat", 0.05, 0,
     "Minutes saved: the worked example uses 2 per outcome (conservative) and, for a second team, 7 (calibrated to the low published self-reported figure, grade C*, evidence VAL-04)."),
    ("A2", "Developer productivity and agents", "Seat + usage", 0.20, 1, ""),
    ("A3", "High-volume service operations", "Per-unit", 0.10, 2, ""),
    ("A4", "Regulated document and decision work", "Per-unit", 1.00, 3, ""),
    ("A5", "Embedded product feature", "Per-unit", 0.02, None,
     "No worked example yet: usage values are copied from A1 as placeholders. Replace them. This model values time saved, so revenue from an embedded feature is not captured."),
    ("A6", "Data and analytics assistant", "Seat", 0.25, None,
     "No worked example yet: usage values are copied from A1 as placeholders. Replace them."),
]

MODEL_KINDS = {"model": "Model", "cheap": "Model", "seat_std": "Seat", "seat_prem": "Seat", "unit_price": "Outcome",
               "tool_price": "Unit", "guard_price": "Unit", "parse_price": "Unit", "emb_price": "Unit",
               "store_price": "Unit", "read_price": "Unit", "plan_price": "Plan"}
SELECTS = {"buy": ["Seat", "Seat + usage", "Per-unit", "Committed capacity"], "curve": ["Linear", "S"],
           "basis": ["per user", "direct volume"], "agentic": ["No", "Yes"]}
TOGGLES = {"own_index"}   # 1 / 0 flags shown as Yes / No
EXCLUDE = {"cap_outcomes"}   # informational only: no calculation reads this field (would confuse the template)


def price_label(r):
    tag = ""
    if r["status"] != "standard":
        tag = f" ({r['status']}" + (f" until {r['to']}" if r["to"] else "") + ")"
    return f"{r['provider']} {r['product']}{tag}"


def field_meta():
    meta = {}
    for key, label, unit in sd.TEAM_FIELDS:
        if key in EXCLUDE:
            continue
        m = {"label": label, "unit": unit, "kind": "number"}
        if key in MODEL_KINDS:
            m["kind"] = "price"
            m["priceKind"] = MODEL_KINDS[key]
            m["allowNone"] = key == "unit_price"
        elif key in SELECTS:
            m["kind"] = "select"
            m["options"] = SELECTS[key]
        elif key in TOGGLES:
            m["kind"] = "toggle"
        elif key in ("name", "archetype", "bu"):
            m["kind"] = "text"
        elif unit == "share":
            m["kind"] = "percent"
        meta[key] = m
    return meta


def main():
    ex = [dict(t) for t in sd.TEAMS]
    archetypes = {}
    a1 = {k: v for k, v in sd.TEAMS[0].items() if k not in ("name", "bu", "archetype", "active", "licensed")}
    for code, name, buy, review, idx, note in ARCHETYPES:
        base = dict(sd.TEAMS[idx]) if idx is not None else dict(a1)
        preset = {k: v for k, v in base.items() if k not in ("name", "bu", "archetype", "active", "licensed")}
        if idx is None:
            preset.update(buy=buy, review=review)
            if code == "A5":
                preset.update(basis="direct volume", direct=40000, o_user=0)
        archetypes[code] = {"code": code, "name": name, "label": f"{code} {name}", "preset": preset, "note": note,
                            "placeholder": idx is None}
    data = {
        "meta": {"priceDate": PRICE_DATE, "version": "0.2 preview", "horizonMax": 60,
                 "org": {k: v[1] for k, v in sd.ORG.items()}},
        "orgFields": {k: {"label": v[0], "unit": v[2], "source": v[4], "grade": v[5]} for k, v in sd.ORG.items()},
        "params": {k: {"desc": v[0], "unit": v[1], "vals": [v[2], v[3], v[4]], "line": v[5], "why": v[6], "grade": v[7]}
                   for k, v in sd.PARAMS.items()},
        "pricebook": sd.PRICEBOOK,
        "priceLabels": {r["id"]: price_label(r) for r in sd.PRICEBOOK},
        "fields": field_meta(),
        "archetypes": archetypes,
        "exampleTeams": ex,
        "template": {"orgFields": TEMPLATE_ORG_FIELDS, "enterpriseFields": TEMPLATE_ENTERPRISE_FIELDS,
                     "requiredTeamFields": TEMPLATE_REQUIRED_TEAM_FIELDS, "teamFieldOrder": list(field_meta().keys())},
    }
    body = json.dumps(data, indent=1, ensure_ascii=False)
    out = ROOT / "app" / "js" / "data.js"
    out.write_text(
        "// SPDX-License-Identifier: Apache-2.0\n"
        "// Generated by app/build/export_data.py from model/build/spec_data.py. Do not edit by hand.\n"
        "(function (root) {\n  var DATA = " + body.replace("\n", "\n  ") + ";\n"
        "  if (typeof module === \"object\" && module.exports) module.exports = DATA;\n  else root.DATA = DATA;\n"
        "}(typeof self !== \"undefined\" ? self : this));\n", encoding="utf-8", newline="\n")
    print("wrote", out, len(body), "characters;", len(data["pricebook"]), "prices;", len(data["params"]), "parameters;",
          len(archetypes), "archetypes")


if __name__ == "__main__":
    main()
