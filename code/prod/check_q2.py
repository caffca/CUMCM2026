# -*- coding: utf-8 -*-
"""Q2 独立 checker（第二实现，不 import 任何求解代码）：
输入含 actions 的 payload/results JSON；独立重算域合法性、零冲突、四级元组。"""
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cli import std_args, Timer, emit, load_plans_local, resolve_base  # noqa

T_MAX, B_MAX = 643, 100
WP = {"A": 100, "B": 10, "C": 1}


def main():
    a, param = std_args("q2 checker")
    tm = Timer()
    sol_path, _ = resolve_base(param.get("solution", "results/Q2_solution.json"), a.run_id,
                               want_variant="cpsat_lex", want_workers="main")
    src = json.load(open(sol_path, encoding="utf-8"))
    acts = src.get("actions") or (src.get("result") or {}).get("actions") or {}
    plans = {p["id"]: p for p in load_plans_local()}
    viol = []
    cells_of = {}
    def cells(p, df=0, dt=0):
        m = 0
        for k in range(p["n"]):
            s = p["t0"] + dt + k * (p["g"] + p["d"])
            if s < 0 or s + p["d"] > T_MAX:
                return None
            for t in range(s, s + p["d"]):
                for f in range(p["f0"] + df, p["f1"] + df):
                    if f < 0 or f >= B_MAX:
                        return None
                    m |= 1 << (t * B_MAX + f)
        return m
    ids = sorted(plans)
    for pid, o in acts.items():
        if pid not in plans:
            viol.append(f"unknown:{pid}"); continue
        keys = [k for k in o if o[k]]
        if len(keys) > 1:
            viol.append(f"multiparam:{pid}")
        p = plans[pid]
        if "revoke" in keys:
            cells_of[pid] = None
            continue
        if "df" in keys and abs(int(o["df"])) > 10:
            viol.append(f"dfmag:{pid}")
        if "dt" in keys and abs(int(o["dt"])) > 5:
            viol.append(f"dtmag:{pid}")
        if "dg" in keys:
            viol.append(f"gap_in_q2:{pid}")
        m = cells(p, df=int(o.get("df", 0)), dt=int(o.get("dt", 0)))
        if m is None:
            viol.append(f"out_of_box:{pid}")
        else:
            cells_of[pid] = m
    for pid, p in plans.items():
        cells_of.setdefault(pid, cells(p))
    residual = 0
    for i in range(len(ids)):
        x = cells_of.get(ids[i])
        if not x:
            continue
        for j in range(i + 1, len(ids)):
            y = cells_of.get(ids[j])
            if y and (x & y):
                residual += 1
    rev = adj = pl = mg = 0
    for pid, o in acts.items():
        c = pid[0]
        if "revoke" in o:
            rev += 1; pl += 2 * WP[c]
        elif o:
            adj += 1; pl += WP[c]; mg += sum(abs(int(v)) for k, v in o.items() if k != "revoke")
    tuple_chk = [rev, adj, pl, mg]
    scalar = 10**12 * rev + 10**8 * adj + 10**4 * pl + mg
    src_tuple = src.get("objective_tuple") or (src.get("result") or {}).get("objective_tuple")
    match = 1 if src_tuple == tuple_chk else 0
    byc = {}
    for pid in plans:
        c = pid[0]
        st = byc.setdefault(c, {"kept": 0, "adjusted": 0, "revoked": 0})
        o = acts.get(pid, {})
        if o.get("revoke"):
            st["revoked"] += 1
        elif o:
            st["adjusted"] += 1
        else:
            st["kept"] += 1
    res = {"question_id": "Q2", "variant": "check", "checker": True, "by_class": byc,
           "objective_tuple": tuple_chk, "revoked": rev, "adjusted": adj, "residual_pairs": residual, "objective_scalar": scalar,
           "residual_pairs_second_impl": residual, "mirrors_for_ir_pairs": True,
           "residual_pairs": residual, "compliance_violations": len(viol),
           "violation_detail": viol[:50], "objective_tuple_second_impl": tuple_chk,
           "tuple_matches_solver": match}
    emit(a.output_dir, res, {"elapsed_seconds": tm.el(), "status": "completed",
                             "stopping_reason": "full_recheck", "evaluator_calls": 0,
                             "budget_class": a.budget_class, "seed": a.seed,
                             "scenario": a.scenario, "parameter": param})
    print(json.dumps(res, ensure_ascii=False)[:300])


if __name__ == "__main__":
    main()
