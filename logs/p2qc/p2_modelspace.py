# -*- coding: utf-8 -*-
"""P2-4b：Q2/Q4 模型空间（选项数、G* 星形冲突边数）与 T_MAX 截断口径的独立复算。

本脚本自行用“合法域解析判定 + 格集（set of cells）”复算，不使用生产的大整数位图。
"""
import json
import os
import sys
import collections

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import p2_common as P  # noqa

DFM, DTM, DGM = P.DF_MAX, P.DT_MAX, P.DG_MAX


def option_ok_band(p, df):
    return 0 <= p["f0"] + df and p["f1"] + df <= P.B_MAX


def option_ok_time(p, dt=0, dg=0):
    q = P.shift(p, dt=dt, dg=dg)
    if q["g"] < 1:
        return False, "gap<=0"
    ss = P.slot_list(q)
    lo = min(s for s, e in ss)
    hi = max(e for s, e in ss)
    if lo < 0:
        return False, "start<0"
    if hi > P.T_MAX:
        return False, f"end>{P.T_MAX}"
    return True, ""


def build_opts(p, allow_dg):
    """返回该计划的合法动作选项集合（含 identity 与 revoke）。"""
    opts = [("id", 0)]
    for d in range(-DFM, DFM + 1):
        if d and option_ok_band(p, d):
            opts.append(("df", d))
    for d in range(-DTM, DTM + 1):
        if d:
            ok, _ = option_ok_time(p, dt=d)
            if ok:
                opts.append(("dt", d))
    dg_drop = {"gap": 0, "horizon": 0}
    if allow_dg:
        for d in range(-DGM, DGM + 1):
            if not d:
                continue
            ok, why = option_ok_time(p, dg=d)
            if ok:
                opts.append(("dg", d))
            elif why.startswith("gap"):
                dg_drop["gap"] += 1
            elif why.startswith("end"):
                dg_drop["horizon"] += 1
    opts.append(("rv", 0))
    return opts, dg_drop


def cells_for(p, kind, v):
    df = v if kind == "df" else 0
    dt = v if kind == "dt" else 0
    dg = v if kind == "dg" else 0
    q = P.shift(p, df=df, dt=dt, dg=dg)
    out = set()
    for (s, e) in P.slot_list(q):
        for t in range(s, e):
            for f in range(q["f0"], q["f1"]):
                out.add(t * 100 + f)
    return out


def union_cells(p, opts):
    u = set()
    for (k, v) in opts:
        if k == "rv":
            continue
        if k == "id":
            cs = cells_for(p, "id", 0)
        else:
            cs = cells_for(p, k, v)
        u |= cs
    return u


def main():
    plans = P.load_plans()
    res = {}
    for tag, allow_dg, auth in (("Q2", False, P.rj(os.path.join("results", "Q2_solution.json"))),
                                ("Q4", True, P.rj(os.path.join("results", "Q4_solution.json")))):
        total_opts = 0
        unions, ids = {}, []
        drop_gap = drop_hz = 0
        for p in plans:
            opts, dd = build_opts(p, allow_dg and p["cls"] == "C")
            total_opts += len(opts)
            drop_gap += dd["gap"]
            drop_hz += dd["horizon"]
            unions[p["id"]] = union_cells(p, opts)
            ids.append(p["id"])
        ids.sort()
        gstar = 0
        forced = 0
        for i in range(len(ids)):
            a = ids[i]
            ua = unions[a]
            if not ua:
                continue
            for j in range(i + 1, len(ids)):
                b = ids[j]
                if ua & unions[b]:
                    gstar += 1
        res[tag] = {
            "options_total_mine": total_opts, "options_total_auth": auth.get("options_total"),
            "options_equal": total_opts == auth.get("options_total"),
            "gstar_mine": gstar, "gstar_auth": auth.get("gstar_edges"),
            "gstar_equal": gstar == auth.get("gstar_edges"),
            "forced_edges_auth": auth.get("forced_edges"),
            "dg_dropped_gap_mine": drop_gap, "dg_dropped_horizon_mine": drop_hz,
            "dg_dropped_total_mine": drop_gap + drop_hz,
            "dg_dropped_auth_label_field": auth.get("dg_options_dropped_by_horizon"),
        }

    # T_MAX 截断口径专项：给出 3 个"确因末周期越出 643 被丢弃"的手工算式
    hz_examples = []
    for p in plans:
        if p["cls"] != "C":
            continue
        for d in range(-DGM, DGM + 1):
            if not d:
                continue
            gp = p["g"] + d
            if gp < 1:
                continue
            le = p["t0"] + (p["n"] - 1) * (gp + p["d"]) + p["d"]
            if le > P.T_MAX:
                hz_examples.append({"id": p["id"], "dg": d, "g": p["g"], "g_prime": gp, "t0": p["t0"],
                                    "n": p["n"], "d": p["d"], "last_slot": [le - p["d"], le],
                                    "formula": f"{p['t0']} + {p['n']-1}*({gp}+{p['d']}) + {p['d']} = {le} > 643"})
    gap_examples = []
    for p in plans:
        if p["cls"] != "C":
            continue
        for d in range(-DGM, DGM + 1):
            if d and p["g"] + d < 1:
                gap_examples.append({"id": p["id"], "dg": d, "g_prime": p["g"] + d})
    res["horizon_truncation_examples_first3"] = hz_examples[:3]
    res["horizon_truncation_examples_last3"] = hz_examples[-3:]
    res["n_horizon_examples"] = len(hz_examples)
    res["n_gap_examples"] = len(gap_examples)
    res["note"] = ("生产字段 dg_options_dropped_by_horizon 同时计入了 g+dg<=0 的非法间隔选项，"
                   "字段名与实际口径不符（数值可复算，语义命名瑕疵）。")
    res["verdict"] = P.verdict(
        res["Q2"]["options_equal"] and res["Q2"]["gstar_equal"]
        and res["Q4"]["options_equal"] and res["Q4"]["gstar_equal"]
        and res["Q4"]["dg_dropped_total_mine"] == res["Q4"]["dg_dropped_auth_label_field"]
        and len(hz_examples) == res["Q4"]["dg_dropped_horizon_mine"]
    )
    P.wr("p2_modelspace_report.json", res)
    print(json.dumps(res, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
