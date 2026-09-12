# -*- coding: utf-8 -*-
"""Q3 独立 checker（第二实现）：重算基座占用、候选可行、加装冲突、行数；不 import 求解模块算法。"""
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cli import std_args, Timer, emit, load_plans_local, resolve_base  # noqa

T_MAX, B_MAX = 643, 100
CW, CD, CG, CN = 3, 2, 8, 12


def main():
    a, param = std_args("q3 checker")
    tm = Timer()
    sol_path, _ = resolve_base(param.get("solution", "results/Q3_solution.json"), a.run_id,
                               want_variant="cpsat_a", qprefix="q3")
    r = json.load(open(sol_path, encoding="utf-8"))
    r = r.get("result", r)
    selected = [tuple(c) for c in r["selected"]]
    base_path, _ = resolve_base(param.get("base", "results/Q2_solution.json"), a.run_id,
                                want_variant="cpsat_lex", want_workers="main")
    b = json.load(open(base_path, encoding="utf-8"))
    b = b.get("result", b)
    acts = b.get("actions") or {}
    plans = {p["id"]: p for p in load_plans_local()}
    occ = {}
    for pid, p in plans.items():
        o = acts.get(pid, {})
        if o.get("revoke"):
            continue
        df, dt = int(o.get("df", 0)), int(o.get("dt", 0))
        for k in range(p["n"]):
            s = p["t0"] + dt + k * (p["g"] + p["d"])
            for t in range(s, s + p["d"]):
                for f in range(p["f0"] + df, p["f1"] + df):
                    occ.setdefault((f, t), 0)
                    occ[(f, t)] += 1
    base_dirty = sum(1 for v in occ.values() if v > 1)
    cv = 0
    cnt = {}
    for (f0, t0) in selected:
        for k in range(CN):
            s = t0 + k * (CG + CD)
            if s + CD > T_MAX:
                cv += 1
            for t in range(s, s + CD):
                for f in range(f0, f0 + CW):
                    if (f, t) in occ or t >= T_MAX or f >= B_MAX:
                        cv += 1
                    cnt[(f, t)] = cnt.get((f, t), 0) + 1
    iv = sum(1 for v in cnt.values() if v > 1)
    # 候选独立重枚举（解析集差法）
    used_cells = set(occ)
    n_cand = 0
    for f0 in range(B_MAX - CW + 1):
        for t0 in range(T_MAX - ((CN - 1) * (CG + CD) + CD) + 1):
            s = {(f, t) for k in range(CN) for t in range(t0 + k * (CG + CD), t0 + k * (CG + CD) + CD)
                 for f in range(f0, f0 + CW)}
            if s.isdisjoint(used_cells):
                n_cand += 1
    emit(a.output_dir, {"question_id": "Q3", "variant": "check",
                        "conflicts_vs_base": cv, "conflicts_internal": iv,
                        "conflict_total_second_impl": cv + iv,
                        "rows": len(selected), "phi": len(selected), "phi_second_impl": len(selected),
                        "base_multiplicity_defects": base_dirty,
                        "cand_count_second_impl": n_cand,
                        "phi_matches_solver": 1 if len(selected) == r.get("phi") else 0},
         {"elapsed_seconds": tm.el(), "status": "completed", "stopping_reason": "full_recheck",
          "evaluator_calls": 0, "budget_class": a.budget_class, "seed": a.seed,
          "scenario": a.scenario, "parameter": param})
    print("q3 check: cv", cv, "iv", iv, "cands", n_cand)


if __name__ == "__main__":
    main()
