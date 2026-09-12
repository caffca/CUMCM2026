# -*- coding: utf-8 -*-
"""Q4 独立 checker（第二实现）：重算合规/零冲突/元组。支持 @Q4MAIN。"""
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cli import std_args, Timer, emit, load_plans_local, resolve_base  # noqa

T_MAX, B_MAX = 643, 100
WP = {"A": 100, "B": 10, "C": 1}


def main():
    a, param = std_args("q4 checker")
    tm = Timer()
    sol_path, _ = resolve_base(param.get("solution", "results/Q4_solution.json"), a.run_id,
                               want_variant="cpsat_lex", want_workers="main", qprefix="q4")
    src = json.load(open(sol_path, encoding="utf-8"))
    r = src.get("result", src)
    acts = r.get("actions") or {}
    plans = {p["id"]: p for p in load_plans_local()}
    viol = []
    occm = {}
    for pid, p in plans.items():
        o = acts.get(pid, {})
        if o.get("revoke"):
            occm[pid] = None
            continue
        ks = [k for k in o if k != "revoke"]
        if len(ks) > 1:
            viol.append(f"multi:{pid}")
        for k, lim in (("df", 10), ("dt", 5), ("dg", 10)):
            if k in o:
                if abs(int(o[k])) > lim:
                    viol.append(f"{k}mag:{pid}")
                if k == "dg" and p["cls"] != "C":
                    viol.append(f"dg_nonC:{pid}")
                if k == "dg" and p["g"] + int(o[k]) < 1:
                    viol.append(f"gprime:{pid}")
        g = p["g"] + int(o.get("dg", 0))
        m = 0
        ok = True
        for kk in range(p["n"]):
            s = p["t0"] + int(o.get("dt", 0)) + kk * (g + p["d"])
            if s < 0 or s + p["d"] > T_MAX:
                ok = False
                break
            for t in range(s, s + p["d"]):
                for f in range(p["f0"] + int(o.get("df", 0)), p["f1"] + int(o.get("df", 0))):
                    if f < 0 or f >= B_MAX:
                        ok = False
                        break
                    m |= 1 << (t * B_MAX + f)
                if not ok:
                    break
            if not ok:
                break
        occm[pid] = None if not ok else m
        if not ok:
            viol.append(f"outofbox:{pid}")
    ids = sorted(plans)
    residual = 0
    for i in range(len(ids)):
        x = occm.get(ids[i])
        if not x:
            continue
        for j in range(i + 1, len(ids)):
            y = occm.get(ids[j])
            if y and (x & y):
                residual += 1
    rev = adj = pl = mg = 0
    for pid, o in acts.items():
        c = pid[0]
        if o.get("revoke"):
            rev += 1
            pl += 2 * WP[c]
        elif o:
            adj += 1
            pl += WP[c]
            mg += sum(abs(int(v)) for k, v in o.items() if k != "revoke")
    tup2 = [rev, adj, pl, mg]
    emit(a.output_dir, {"question_id": "Q4", "variant": "check", "checker": True,
                        "residual_pairs_second_impl": residual, "residual_pairs": residual,
                        "compliance_violations": len(viol), "violations": residual + len(viol),
                        "violation_detail": viol[:50], "objective_tuple_second_impl": tup2,
                        "objective_tuple": tup2,
                        "tuple_matches_solver": 1 if tup2 == r.get("objective_tuple") else 0,
                        "scalar_second_impl": 10**12 * tup2[0] + 10**8 * tup2[1] + 10**4 * tup2[2] + tup2[3],
                        "objective_scalar": 10**12 * tup2[0] + 10**8 * tup2[1] + 10**4 * tup2[2] + tup2[3],
                        "revocations": rev, "adjusteds": adj,
                        "by_class": _byclass(acts, ids, plans)},
         {"elapsed_seconds": tm.el(), "status": "completed", "stopping_reason": "full_recheck",
          "evaluator_calls": 0, "budget_class": a.budget_class, "seed": a.seed,
          "scenario": a.scenario, "parameter": param})
    print("q4 check:", residual, len(viol), tup2)


def _byclass(acts, ids, plans):
    stat = {}
    for pid in ids:
        c = pid[0]
        st = stat.setdefault(c, {"kept": 150 and 0, "adjusted": 0, "revoked": 0})
        o = acts.get(pid, {})
        if o.get("revoke"):
            st["revoked"] += 1
        elif o:
            st["adjusted"] += 1
        else:
            st["kept"] += 1
    return stat


if __name__ == "__main__":
    main()
