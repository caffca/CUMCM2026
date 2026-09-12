# -*- coding: utf-8 -*-
"""Q3 求解模块：CP-SAT set-packing（A pairwise / B 逐格容量）、HiGHS LP 上界。
自含：无 enum_payload 时内部执行枚举（base 支持 @Q2MAIN）。"""
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cli import std_args, Timer, emit, resolve_base  # noqa

T_MAX, B_MAX = 643, 100
CW, CD, CG, CN = 3, 2, 8, 12


def get_enum(param, run_id, tm):
    if param.get("enum_payload"):
        d = json.load(open(param["enum_payload"], encoding="utf-8"))
        return d.get("result", d)
    import q3v_enum
    used, n_used, base_tuple = q3v_enum.base_mask(param, run_id)
    cands, total = q3v_enum.enumerate_candidates(used, "bitmap", param)
    cands2, _ = q3v_enum.enumerate_candidates(used, "analytic", param)
    agree = 1 if [(c[0], c[1]) for c in cands] == [(c[0], c[1]) for c in cands2] else 0
    e_bm = q3v_enum.interf_edges_bitmap(cands)
    return {"cand_list": [[c[0], c[1]] for c in cands], "edge_list": [list(e) for e in e_bm],
            "cand_agreement_second_impl": agree, "base_cells": n_used, "base_tuple": base_tuple,
            "free_cells": T_MAX * B_MAX - n_used}


def main():
    a, param = std_args("q3 solve")
    tm = Timer()
    variant = param.get("variant", "cpsat_a")
    limit = float(param.get("limit", 900))
    workers = int(param.get("workers", 4))
    enum = get_enum(param, a.run_id, tm)
    cands = [tuple(c) for c in enum["cand_list"]]
    edges = [tuple(e) for e in enum["edge_list"]]
    n = len(cands)
    out = {"question_id": "Q3", "variant": variant, "n_cand": n, "n_edges": len(edges),
           "cand_agreement_second_impl": enum.get("cand_agreement_second_impl"),
           "base_tuple": enum.get("base_tuple")}
    if variant in ("cpsat_a", "cpsat_b"):
        from ortools.sat.python import cp_model
        m = cp_model.CpModel()
        x = [m.NewBoolVar(f"x{i}") for i in range(n)]
        if variant == "cpsat_a":
            for i, j in edges:
                m.Add(x[i] + x[j] <= 1)
        else:
            cellmap = {}
            for i, (f0, t0) in enumerate(cands):
                for k in range(CN):
                    s = t0 + k * (CG + CD)
                    for t in range(s, s + CD):
                        for f in range(f0, f0 + CW):
                            cellmap.setdefault(t * B_MAX + f, []).append(i)
            for c, lst in cellmap.items():
                m.Add(sum(x[i] for i in lst) <= 1)
            out["cells_with_cands"] = len(cellmap)
        m.Maximize(sum(x))
        sv = cp_model.CpSolver()
        sv.parameters.max_time_in_seconds = limit
        sv.parameters.num_search_workers = workers
        st = sv.Solve(m)
        name = sv.StatusName(st)
        sel = [i for i in range(n) if sv.Value(x[i])] if name in ("OPTIMAL", "FEASIBLE") else []
        out.update({"status": name, "phi": len(sel),
                    "best_bound": sv.BestObjectiveBound() if sel else None,
                    "selected": [list(cands[i]) for i in sel],
                    "proven_optimal": name == "OPTIMAL"})
    elif variant == "lp_hiGHS":
        from scipy.optimize import linprog
        from scipy.sparse import lil_matrix, csr_matrix
        A = lil_matrix((len(edges), n), dtype=int)
        for r, (i, j) in enumerate(edges):
            A[r, i] = 1
            A[r, j] = 1
        res = linprog(c=[-1] * n, A_ub=csr_matrix(A), b_ub=[1] * len(edges),
                      bounds=[(0, 1)] * n, method="highs")
        out.update({"lp_status": int(res.status), "lp_bound": (-res.fun) if res.success else None,
                    "lp_message": str(res.message)})
    emit(a.output_dir, out, {"elapsed_seconds": tm.el(), "status": "completed",
                             "stopping_reason": "solved", "evaluator_calls": 1,
                             "budget_class": a.budget_class, "seed": a.seed,
                             "scenario": a.scenario, "parameter": param})
    print(variant, out.get("phi"), out.get("status"), out.get("best_bound"), out.get("lp_bound"), "rt", tm.el())


if __name__ == "__main__":
    main()
