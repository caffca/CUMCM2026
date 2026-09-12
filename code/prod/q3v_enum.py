# -*- coding: utf-8 -*-
"""Q3 生产模块集：候选枚举（主/独立二实现）、CP-SAT set-packing（A/B）、HiGHS LP、初等双计数界。
基座 = results/Q2_solution.json 的 actions 应用后占用集。"""
import os, sys, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from cli import std_args, Timer, emit, load_plans_local  # noqa

T_MAX, B_MAX = 643, 100
CW, CD, CG, CN = 3, 2, 8, 12
F0MAX, T0MAX = B_MAX - CW, T_MAX - ((CN - 1) * (CG + CD) + CD)  # 97, 531


def cells_c(f0, t0):
    m = 0
    for k in range(CN):
        s = t0 + k * (CG + CD)
        for t in range(s, s + CD):
            for f in range(f0, f0 + CW):
                m |= 1 << (t * B_MAX + f)
    return m


def base_mask(param, run_id=None):
    """应用 Q2 生产解 actions 得基座占用位图（撤销释放、平移生效）。支持 @Q2MAIN。"""
    from cli import resolve_base
    pth, src_desc = resolve_base(param.get("base", "results/Q2_solution.json"), run_id or "", 
                                  want_variant="cpsat_lex", want_workers="main", qprefix="q2")
    param["base_resolved"] = pth
    src = json.load(open(pth, encoding="utf-8"))
    acts = src.get("actions") or (src.get("result") or {}).get("actions") or {}
    meta_src = src
    plans = {p["id"]: p for p in load_plans_local()}
    used = 0
    for pid, p in plans.items():
        o = acts.get(pid, {})
        if o.get("revoke"):
            continue
        df = int(o.get("df", 0)); dt = int(o.get("dt", 0))
        m = 0
        for k in range(p["n"]):
            s = p["t0"] + dt + k * (p["g"] + p["d"])
            for t in range(s, s + p["d"]):
                for f in range(p["f0"] + df, p["f1"] + df):
                    m |= 1 << (t * B_MAX + f)
        used |= m
    n_used = bin(used).count("1")
    return used, n_used, (src.get("objective_tuple") or (src.get("result") or {}).get("objective_tuple"))


def enumerate_candidates(used, method, param):
    """两种独立实现：主=位图零交；二=解析占用集差。返回 [(f0,t0,mask)] 与遍历计数。"""
    cands = []
    total = (F0MAX + 1) * (T0MAX + 1)
    if method == "bitmap":
        for f0 in range(F0MAX + 1):
            for t0 in range(T0MAX + 1):
                m = cells_c(f0, t0)
                if not (m & used):
                    cands.append((f0, t0, m))
    else:  # analytic second impl: 直接按计划重建占用格集合（不经位图）
        src = json.load(open(param.get("base_resolved") or param.get("base", "results/Q2_solution.json"), encoding="utf-8"))
        acts = src.get("actions") or (src.get("result") or {}).get("actions") or {}
        pls = {p["id"]: p for p in load_plans_local()}
        used_cells = set()
        for pid, p in pls.items():
            o = acts.get(pid, {})
            if o.get("revoke"):
                continue
            df = int(o.get("df", 0)); dt = int(o.get("dt", 0))
            for k in range(p["n"]):
                s = p["t0"] + dt + k * (p["g"] + p["d"])
                for t in range(s, s + p["d"]):
                    for f in range(p["f0"] + df, p["f1"] + df):
                        used_cells.add(t * B_MAX + f)
        for f0 in range(F0MAX + 1):
            for t0 in range(T0MAX + 1):
                s = set()
                for k in range(CN):
                    st = t0 + k * (CG + CD)
                    for t in range(st, st + CD):
                        for f in range(f0, f0 + CW):
                            s.add(t * B_MAX + f)
                if s.isdisjoint(used_cells):
                    cands.append((f0, t0, cells_c(f0, t0)))
    return cands, total


def interf_edges(cands):
    """干扰边三路之一：解析判据 |Δf0|≤CW-1 ∧ 存在 k,k' 窗交 ⟺ |Δf0|<3 且相位/跨度条件。"""
    n = len(cands)
    idmap = {(c[0], c[1]): i for i, c in enumerate(cands)}
    edges = []
    for i in range(n):
        f0, t0, _ = cands[i]
        for j in range(i + 1, n):
            g0, s0, _ = cands[j]
            if abs(f0 - g0) >= CW:
                continue
            dt = t0 - s0
            if abs(dt) > (CN - 1) * (CG + CD) + CD - 1:
                continue
            r = dt % (CG + CD)
            if min(r, (CG + CD) - r) < CD:
                edges.append((i, j))
    return edges


def interf_edges_bitmap(cands):
    n = len(cands)
    edges = []
    for i in range(n):
        mi = cands[i][2]
        for j in range(i + 1, n):
            if mi & cands[j][2]:
                edges.append((i, j))
    return edges


def main():
    a, param = std_args("q3 module")
    tm = Timer()
    variant = param.get("variant", "all")
    used, n_used, base_tuple = base_mask(param, a.run_id)
    cands, total = enumerate_candidates(used, "bitmap", param)
    cands2, _ = enumerate_candidates(used, "analytic", param)
    agree = 1 if [(c[0], c[1]) for c in cands] == [(c[0], c[1]) for c in cands2] else 0
    e_an = interf_edges(cands)
    e_bm = interf_edges_bitmap(cands)
    edge_agree = 1 if set(e_an) == set(e_bm) else 0
    free_cells = T_MAX * B_MAX - n_used
    res = {"question_id": "Q3", "variant": variant,
           "base_tuple": base_tuple, "base_cells": n_used, "free_cells": free_cells,
           "cand_universe": total, "cand_feasible": len(cands),
           "cand_agreement_second_impl": agree, "edge_agreement": edge_agree,
           "interf_edges": len(e_bm),
           "cand_list": [[c[0], c[1]] for c in cands],
           "edge_list": [[i, j] for i, j in e_bm]}
    emit(a.output_dir, res, {"elapsed_seconds": tm.el(), "status": "completed",
                             "stopping_reason": "enumerated", "evaluator_calls": 0,
                             "budget_class": a.budget_class, "seed": a.seed,
                             "scenario": a.scenario, "parameter": param})
    print("q3 enum:", len(cands), "edges:", len(e_bm), "agree:", agree, edge_agree, "rt", tm.el())


if __name__ == "__main__":
    main()
