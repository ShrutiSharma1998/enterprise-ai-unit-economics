# SPDX-License-Identifier: Apache-2.0
"""Independent reference model. Plain loops, no spreadsheet logic. Used only to verify the workbook.

Mirrors the rules in research/cost-taxonomy.md and spec/requirements-spec.md. k = 0 low-cost, 1 base, 2 high-cost.
"""
import copy
from spec_data import ORG, PARAMS, PRICEBOOK, TEAMS, LANGFUSE_INCLUDED

MONTHS = 60
PB = {r["id"]: r for r in PRICEBOOK}


def P(key, k):
    return PARAMS[key][2 + k]


def price(pid, field="p_in"):
    return PB[pid][field] if pid else 0.0


def cost_per_outcome(t, k):
    steps = P("steps", k) if t["agentic"] == "Yes" else 1
    scale = (1 - t["ctx"]) * P("tok_mult", k) * P("retry", k) * steps
    tin, tout = t["tok_in"] * scale, t["tok_out"] * scale
    m, c = PB[t["model"]], PB[t["cheap"]]
    pin = (1 - t["route"]) * m["p_in"] + t["route"] * c["p_in"]
    pout = (1 - t["route"]) * m["p_out"] + t["route"] * c["p_out"]
    fc = (1 - t["cached"] - t["cwrite"]) + t["cached"] * m["c_read"] + t["cwrite"] * m["c_write"]
    fb = 1 - t["async_"] * (1 - m["batch"])
    return (tin * pin * fc + tout * pout) / 1e6 * fb * t["resid"]


def ramp(t, m):
    if m < t["start"]:
        return 0.0
    x = min(1.0, max(0.0, (m - t["start"] + 1) / t["ramp"]))
    return x * x * (3 - 2 * x) if t["curve"] == "S" else x


def team_rows(t, k, org, value_k):
    hz, pd = org["horizon"], org["pd_rate"]
    hourly = pd / org["hours_day"]
    cpo = cost_per_outcome(t, k)
    buy = t["buy"]
    seat_flag = buy in ("Seat", "Seat + usage")
    vendor = buy == "Per-unit" and t["unit_price"] != ""
    api = buy == "Seat + usage" or (buy == "Per-unit" and t["unit_price"] == "") or buy == "Committed capacity"
    std, prem = price(t["seat_std"]), price(t["seat_prem"])
    rows = {n: [0.0] * (MONTHS + 1) for n in [
        "ramp", "lic", "act", "out", "seat", "tokens", "vendor", "tools", "cap", "data_price", "data_effort", "run_effort",
        "migration", "review", "cm", "ot_data_effort", "ot_data_load", "ot_l2", "ot_train", "benefit"]}
    interval = max(1, round(P("mig_int", k)))
    if t.get("active", 1) != 1:
        return rows, cpo
    for m in range(1, MONTHS + 1):
        h = 1 if m <= hz else 0
        st = m >= t["start"]
        x = ramp(t, m)
        lic = t["licensed"] if st else 0
        act = lic * t["plateau"] * x
        out = act * t["o_user"] if t["basis"] == "per user" else t["direct"] * x
        rows["ramp"][m], rows["lic"][m], rows["act"][m], rows["out"][m] = x, lic, act, out
        rows["seat"][m] = h * seat_flag * lic * ((1 - t["prem_share"]) * std + t["prem_share"] * prem)
        if buy == "Seat + usage":
            o_rest = t["o_user"] / ((1 - t["top_share"]) + t["top_share"] * t["top_mult"])
            o_top = t["top_mult"] * o_rest
            tok = act * ((1 - t["top_share"]) * max(0, o_rest * cpo - t["allow"]) + t["top_share"] * max(0, o_top * cpo - t["allow"]))
        elif buy == "Per-unit" and not vendor:
            tok = out * cpo
        else:
            tok = 0.0
        rows["tokens"][m] = h * tok
        rows["vendor"][m] = h * (out * price(t["unit_price"]) if vendor else 0)
        rows["tools"][m] = h * (out * (t["tool_calls"] * price(t["tool_price"]) / 1000 + t["guard_units"] * price(t["guard_price"]) / 1000) if api else 0)
        rows["cap"][m] = h * (t["cap_cost"] if (buy == "Committed capacity" and st) else 0)
        if st and t["own_index"]:
            dp = (t["ndocs"] * P("change_rate", k) * t["pages"] * price(t["parse_price"])
                  + t["ndocs"] * P("change_rate", k) * t["emb_tok"] * price(t["emb_price"]) / 1e6
                  + price(t["plan_price"]) + t["gb"] * price(t["store_price"]) + out * t["read_units"] * price(t["read_price"]) / 1e6)
        else:
            dp = 0.0
        rows["data_price"][m] = h * dp
        rows["data_effort"][m] = h * (t["nsrc"] * P("conn_pd", k) * pd * P("conn_up", k) / 12 if st else 0)
        rows["run_effort"][m] = h * ((P("evalcases", k) * P("eval_min", k) / 60 * hourly + P("maint", k) / 12 * P("int_pd", k) * pd
                                      + act / 1000 * P("tickets", k) * P("tkt_hours", k) * hourly) if st else 0)
        ev = 1 if (m > t["start"] and (m - t["start"]) % interval == 0) else 0
        rows["migration"][m] = h * ev * (P("mig_pd", k) + P("eval_rerun", k) * P("eval_pd", k)) * pd
        rows["review"][m] = h * out * min(1.0, t["review"] * P("rev_mult", k)) * P("rev_min", k) / 60 * t["rev_rate"]
        fte = P("cm_ramp", k) if (m - t["start"]) < 6 else P("cm_after", k)
        rows["cm"][m] = h * ((lic / 1000) * fte * pd * org["work_days"] / 12 if st else 0)
        rows["benefit"][m] = h * out * t["min_saved"] / 60 * t["b_rate"] * P("realise", value_k) * t["accept"]
    rows["ot_data_effort"][0] = (t["nsrc"] * P("src_pd", k) + t["ndocs"] / 100000 * P("clean_pd", k) + t["nsrc"] * P("conn_pd", k)) * pd
    rows["ot_data_load"][0] = t["own_index"] * (t["ndocs"] * t["pages"] * price(t["parse_price"]) + t["ndocs"] * t["emb_tok"] * price(t["emb_price"]) / 1e6)
    rows["ot_l2"][0] = (P("int_pd", k) + P("eval_pd", k)) * pd
    rows["ot_train"][0] = t["licensed"] * t["plateau"] * P("train_hours", k) * hourly
    return rows, cpo


def hub_rows(teams_rows, teams, k, org):
    hz, pd, wd = org["horizon"], org["pd_rate"], org["work_days"]
    nT = sum(1 for t in teams if t.get("active", 1) == 1)
    srcs = sum(t["nsrc"] for t in teams if t.get("active", 1) == 1)
    ot = {"plat_ot": P("plat_pd", k) * pd, "perm_ot": srcs * P("perm_pd", k) * pd,
          "rev_ot": (nT * P("rev_uc_pd", k) + P("rev_once_pd", k)) * pd, "rt_ot": nT * P("rt_pd", k) * pd}
    rows = {n: [0.0] * (MONTHS + 1) for n in ["plat_run", "perm_up", "rt_rep", "env", "mon", "plat_team", "gov", "comp", "lic"]}
    for m in range(1, MONTHS + 1):
        h = 1 if m <= hz else 0
        sumo = sum(r["out"][m] for r in teams_rows)
        rows["plat_run"][m] = h * ot["plat_ot"] * P("plat_run", k) / 12
        rows["perm_up"][m] = h * ot["perm_ot"] * P("perm_up", k) / 12
        rows["rt_rep"][m] = h * ot["rt_ot"] * P("rt_rep", k) / 12
        rows["env"][m] = h * P("env_month", k)
        rows["mon"][m] = h * (price("PL_LANGFUSE_PRO") + max(0, sumo * org["obs_per_out"] - LANGFUSE_INCLUDED) / 100000 * price("U_LANGFUSE_OVER"))
        rows["plat_team"][m] = h * P("plat_fte", k) * pd * wd / 12
        rows["gov"][m] = h * P("gov_fte", k) * pd * wd / 12
        rows["comp"][m] = h * P("comp_year", k) / 12
        rows["lic"][m] = h * P("lic_year", k) / 12
    return ot, rows


TAG = {"seat": "A", "tokens": "A", "vendor": "A", "tools": "A", "cap": "E", "data_price": "A", "data_effort": "S", "run_effort": "S",
       "migration": "R", "review": "R", "cm": "S", "ot_data_effort": "S", "ot_data_load": "A", "ot_l2": "S", "ot_train": "S"}
LAYER = {"seat": 3, "tokens": 3, "vendor": 3, "tools": 3, "cap": 2, "data_price": 1, "data_effort": 1, "run_effort": 4, "migration": 4,
         "review": 5, "cm": 5, "ot_data_effort": 1, "ot_data_load": 1, "ot_l2": 2, "ot_train": 5}
HUB_TAG = {"plat_ot": "S", "perm_ot": "S", "rev_ot": "S", "rt_ot": "S", "plat_run": "S", "perm_up": "S", "rt_rep": "S", "env": "E",
           "mon": "A", "plat_team": "S", "gov": "R", "comp": "E", "lic": "E"}
HUB_LAYER = {"plat_ot": 2, "perm_ot": 1, "rev_ot": 2, "rt_ot": 2, "plat_run": 2, "perm_up": 1, "rt_rep": 2, "env": 2,
             "mon": 4, "plat_team": 4, "gov": 4, "comp": 4, "lic": 4}


def run(k=1, org_over=None, team_over=None, value_k=1):
    org = {key: v[1] for key, v in ORG.items()}
    org.update(org_over or {})
    teams = copy.deepcopy(TEAMS)
    for i, ov in (team_over or {}).items():
        teams[i].update(ov)
    tr, cpo = [], []
    for t in teams:
        r, c = team_rows(t, k, org, value_k)
        tr.append(r)
        cpo.append(c)
    hot, hrows = hub_rows(tr, teams, k, org)
    tot = lambda arr: sum(arr)
    res = {"cpo": cpo, "teams": [], "org": org}
    hub_raw_ot = sum(hot.values())
    hub_raw_m = [sum(hrows[n][m] for n in hrows) for m in range(MONTHS + 1)]
    hub_raw_total = hub_raw_ot + sum(hub_raw_m)
    flags = [1 if t.get("active", 1) == 1 else 0 for t in teams]
    nT = sum(flags)
    fedfac = nT * P("fed_dup", k)
    eff_hub = hub_raw_total * (fedfac if org["shape"] == "Federated" else 1)
    hs = lambda arr: sum(arr[1:org["horizon"] + 1])      # state rows are not masked: total only the horizon
    outs = [hs(r["out"]) for r in tr]
    lics = [t["licensed"] * f for t, f in zip(teams, flags)]
    rule = org["alloc"]
    share = {"Usage-proportional": [o / sum(outs) for o in outs], "Headcount proxy": [l / sum(lics) for l in lics],
             "Even split": [f / nT for f in flags], "Central budget": [0.0] * len(teams)}[rule]
    if org["shape"] == "Federated":
        alloc = [hub_raw_total * P("fed_dup", k) * f for f in flags]
        unalloc = 0.0
    else:
        alloc = [hub_raw_total * s for s in share]
        unalloc = hub_raw_total if rule == "Central budget" else 0.0
    layers = {i: 0.0 for i in range(1, 6)}
    by_tag = {"A": 0.0, "S": 0.0, "R": 0.0, "E": 0.0}
    comp = {"benefit": 0.0, "tokens": 0.0, "vol": 0.0, "review": 0.0, "effort": 0.0, "cost": 0.0}
    cum_e = [0.0] * (MONTHS + 1)
    for i, r in enumerate(tr):
        direct = {n: tot(r[n]) for n in TAG}
        d_tot = sum(direct.values())
        ben = tot(r["benefit"])
        f = alloc[i] / hub_raw_total if hub_raw_total else 0
        cum, pb = 0.0, None
        for m in range(0, MONTHS + 1):
            if m > org["horizon"]:
                break
            dm = sum(r[n][m] for n in TAG)
            net = r["benefit"][m] - dm - f * (hub_raw_ot if m == 0 else hub_raw_m[m])
            cum += net
            if m >= 1 and pb is None and cum >= 0:
                pb = m
        res["teams"].append({"direct": direct, "direct_total": d_tot, "alloc": alloc[i], "benefit": ben, "outcomes": outs[i],
                             "active_months": hs(r["act"]), "net": ben - d_tot - alloc[i], "payback": pb,
                             "cost_per_outcome": (d_tot + alloc[i]) / outs[i] if outs[i] else None,
                             "cpa_month": ((d_tot + alloc[i]) / hs(r["act"]) if hs(r["act"]) else 0.0) if teams[i]["basis"] == "per user" else None})
        for n in TAG:
            layers[LAYER[n]] += direct[n]
            by_tag[TAG[n]] += direct[n]
        comp["benefit"] += ben
        comp["tokens"] += direct["tokens"]
        comp["review"] += direct["review"]
        comp["vol"] += direct["tokens"] + direct["vendor"] + direct["tools"] + direct["review"]
        comp["effort"] += sum(direct[n] for n in TAG if TAG[n] == "S") + direct["migration"]   # all person-day-rate-driven team lines
    pu = [i for i, t in enumerate(teams) if t["basis"] == "per user"]
    pu_act = sum(res["teams"][i]["active_months"] for i in pu)
    res["cpa_ent"] = (sum(res["teams"][i]["direct_total"] + res["teams"][i]["alloc"] for i in pu) / pu_act) if pu_act else 0.0
    fm = fedfac if org["shape"] == "Federated" else 1
    hub_tot = {n: hot[n] for n in hot}
    hub_tot.update({n: tot(hrows[n]) for n in hrows})
    for n, v in hub_tot.items():
        layers[HUB_LAYER[n]] += v * fm
        by_tag[HUB_TAG[n]] += v * fm
        if HUB_TAG[n] == "S" or n == "gov":     # cost governance is FTE x person-day rate
            comp["effort"] += v * fm
    total_cost = sum(layers.values())
    comp["cost"] = total_cost
    res.update(dict(layers=layers, by_tag=by_tag, comp=comp, total_cost=total_cost, alloc=alloc, unalloc=unalloc,
                    hub_raw_total=hub_raw_total, eff_hub=eff_hub, net=comp["benefit"] - total_cost,
                    hub_rows=hrows, hub_ot=hot, team_rows=tr))
    # enterprise payback
    cum, pb = 0.0, None
    for m in range(0, org["horizon"] + 1):
        ben = sum(r["benefit"][m] for r in tr)
        dm = sum(r[n][m] for r in tr for n in TAG)
        hm = (hub_raw_ot if m == 0 else hub_raw_m[m]) * fm
        cum += ben - dm - hm
        if m >= 1 and pb is None and cum >= 0:
            pb = m
    res["payback"] = pb
    return res


if __name__ == "__main__":
    for k, name in enumerate(["Low-cost", "Base", "High-cost"]):
        r = run(k)
        print(f"{name:10s} total cost {r['total_cost']:>14,.0f}  benefit {r['comp']['benefit']:>14,.0f}  net {r['net']:>14,.0f}  payback {r['payback']}")
        print("   layers", {i: round(v) for i, v in r["layers"].items()}, "| by evidence", {k2: round(v) for k2, v in r["by_tag"].items()})
    r = run(1)
    for i, t in enumerate(r["teams"]):
        print(TEAMS[i]["name"][:28].ljust(28), "cost/outcome", round(t["cost_per_outcome"], 3), "net", round(t["net"]), "payback", t["payback"], "cpo(tokens)", round(r["cpo"][i], 4))
