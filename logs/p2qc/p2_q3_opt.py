# -*- coding: utf-8 -*-
"""P2-3b：Q3 最优性的独立第三实现。
自建候选集（P2-3 已独立复算 2270）+ 自建干扰边（格集倒排，非生产位图）+ 自写 CP-SAT 集包装，
独立复核 phi=140 与 proven_optimal 声明。
"""
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import p2_common as P  # noqa

sys.path.append(os.environ.get("DSH_ENVLIBS", r"F:\dsh_envlibs\mathmodel"))
from ortools.sat.python import cp_model  # noqa

CW, CD, CG, CN = P.C_W, P.C_D, P.C_G, P.C_N


def main():
    plans = P.load_plans()
    pmap = {p["id"]: p for p in plans}
    acts = P.rj(os.path.join("results", "Q2_solution.json"))["actions"]
    base = []
    for pid in sorted(pmap):
        o = acts.get(pid, {})
        if o.get("revoke"):
            continue
        base.append(P.shift(pmap[pid], df=int(o.get("df", 0)), dt=int(o.get("dt", 0))))
    occ = set()
    for bp in base:
        for (s, e) in P.slot_list(bp):
            for t in range(s, e):
                for f in range(bp["f0"], bp["f1"]):
                    occ.add((t, f))
    f0max, t0max = P.B_MAX - CW, P.T_MAX - ((CN - 1) * (CG + CD) + CD)
    cands, cells_of = [], []
    for f0 in range(f0max + 1):
        for t0 in range(t0max + 1):
            cs = frozenset((t, f) for k in range(CN) for t in range(t0 + k * (CG + CD), t0 + k * (CG + CD) + CD)
                           for f in range(f0, f0 + CW))
            if cs.isdisjoint(occ):
                cands.append((f0, t0))
                cells_of.append(cs)
    # 倒排建边
    inv = {}
    for i, cs in enumerate(cells_of):
        for c in cs:
            inv.setdefault(c, []).append(i)
    edges = set()
    for lst in inv.values():
        for a in range(len(lst)):
            for b in range(a + 1, len(lst)):
                edges.add((lst[a], lst[b]))
    n = len(cands)
    m = cp_model.CpModel()
    x = [m.NewBoolVar(f"x{i}") for i in range(n)]
    for (i, j) in edges:
        m.Add(x[i] + x[j] <= 1)
    m.Maximize(sum(x))
    sv = cp_model.CpSolver()
    sv.parameters.max_time_in_seconds = float(os.environ.get("P2_Q3_LIMIT", "420"))
    sv.parameters.num_search_workers = 8
    sv.parameters.log_search_progress = False
    st = sv.Solve(m)
    name = sv.StatusName(st)
    sel = [] if name not in ("OPTIMAL", "FEASIBLE") else [cands[i] for i in range(n) if sv.Value(x[i])]
    q3 = P.rj(os.path.join("results", "Q3_solution.json"))
    auth = {tuple(c) for c in q3["selected"]}
    res = {
        "check": "Q3 最优性独立第三实现（自建候选+自建边+自写 CP-SAT）",
        "n_cand_mine": n, "n_edges_mine": len(edges),
        "solver_status": name,
        "phi_mine": len(sel), "phi_auth": q3["phi"],
        "best_bound_mine": sv.BestObjectiveBound(),
        "bound_auth": q3.get("best_bound"),
        "proven_optimal_mine": name == "OPTIMAL",
        "proven_optimal_auth": q3.get("proven_optimal"),
        "mine_is_also_optimal_value": len(sel) == q3["phi"],
        "selected_set_equal_auth": set(sel) == auth,
        "selected_size_intersection": len(set(sel) & auth),
        "note": "解不要求唯一：只要独立实现同样证明上界=下界=140，即认证 phi 的最大性；多重解属正常简并。",
        "limit_seconds": float(os.environ.get("P2_Q3_LIMIT", "420")),
    }
    res["verdict"] = P.verdict(res["phi_mine"] == q3["phi"] and res["proven_optimal_mine"])
    P.wr("p2_q3_optimality.json", res)
    print(json.dumps(res, ensure_ascii=False, indent=1))


if __name__ == "__main__":
    main()
