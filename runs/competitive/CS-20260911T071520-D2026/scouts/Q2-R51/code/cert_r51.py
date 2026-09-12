# -*- coding: utf-8 -*-
"""R51 阶段二：撤销层下界加强（relaxation 下界 + 边界 INFEASIBLE 证书攻坚）。

背景：阶段一（solve_r51.py，555s）已给出可行解与撤销层 incumbent UB=6，
但 min Σr 的 CP 分数界只有 LB=2 ⇒ gap_revoke=4。本脚本用两种可复核手段加强下界：

(1) relaxation 下界：只保留"原冲突边 297"的动作级不相容子句（G* 子句集的真子集 ⇒ 合法松弛），
    对该松弛求 min Σr；若返回 OPTIMAL=v，则真实撤销数 ≥ v（松弛最优 ≤ 原问题最优）。
    ——同时给出 adjusted 层的松弛分数界（LP 界，仅作诊断，不当作证书）。
(2) 边界深证明：在全势边 G* 完整模型上加 Σr ≤ k（k 从 UB-1=5 起，必要时继续下探），
    纯可行性判定；INFEASIBLE ⇒ "撤销数 ≥ k+1" 的机器可复核证书。

只读阶段一产物（solution_actions.json / star_edges.json），只写本目录新文件。
"""
import argparse
import io
import json
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.stdout.reconfigure(encoding="utf-8")

import q2_common as Q  # noqa: E402
import solve_r51 as S  # noqa: E402
from ortools.sat.python import cp_model  # noqa: E402


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--budget", type=float, default=250.0)
    ap.add_argument("--relax-frac", type=float, default=0.22)
    ap.add_argument("--out-dir", default=os.path.abspath(os.path.join(HERE, "..")))
    a = ap.parse_args()
    t0 = time.time()
    logf = io.open(os.path.join(a.out_dir, "r51_phase2_log.txt"), "w", encoding="utf-8")

    def log(msg):
        line = "[%7.1fs] %s" % (time.time() - t0, msg)
        print(line, flush=True)
        logf.write(line + "\n")
        logf.flush()

    plans = Q.load_plans()
    ids, acts, masks = Q.build_action_tables(plans)
    raw = json.load(io.open(os.path.join(a.out_dir, "star_edges.json"), encoding="utf-8"))
    edges = {tuple(k.split("|")): [tuple(v) for v in vv] for k, vv in raw["edges"].items()}
    rep = json.load(io.open(os.path.join(a.out_dir, "solution_meta.json"), encoding="utf-8")) \
        if os.path.isfile(os.path.join(a.out_dir, "solution_meta.json")) else {}
    sol = json.load(io.open(os.path.join(a.out_dir, "solution_actions.json"), encoding="utf-8"))
    UB = sum(1 for v in sol.values() if v.get("revoke"))
    a_idx = {i: {("keep", 0, 0): 0} for i in ids}
    for i in ids:
        for x, act in enumerate(acts[i]):
            a_idx[i][act] = x
    base_choice = {i: a_idx[i][("keep", 0, 0)] for i in ids}
    for pid, act in sol.items():
        if act.get("revoke"):
            base_choice[pid] = a_idx[pid][("revoke", 0, 0)]
        elif "df" in act:
            base_choice[pid] = a_idx[pid][("df", int(act["df"]), 0)]
        elif "dt" in act:
            base_choice[pid] = a_idx[pid][("dt", 0, int(act["dt"]))]
    base = [(i, j) for x, i in enumerate(ids) for j in ids[x + 1:]
            if not masks[(i, "keep", 0, 0)].isdisjoint(masks[(j, "keep", 0, 0)])]
    assert set(base).issubset(set(edges))
    log("stage1 UB=%d | base=%d subset of G*=%d" % (UB, len(base), len(edges)))

    out = {"stage1_UB_revoke": UB, "n_star_edges": len(edges), "n_base_edges": len(base)}

    # ---------- (1) relaxation 下界 ----------
    tl = max(8.0, a.budget * a.relax_frac)
    tb = time.time()
    edges_relax = {k: edges[k] for k in base}
    mr, Xr, Lr, repr_ = S.build_model(plans, ids, acts, edges_relax)
    mr.Minimize(Lr["revoke"])
    S.set_hints(mr, Xr, base_choice)
    sr = S.mk_solver(tl)
    st = sr.Solve(mr)
    rec = {"model": "relaxation(base_edges_only)", "status": sr.StatusName(st),
           "budget_s": round(tl, 1), "wall_s": round(time.time() - tb, 1),
           "clauses": repr_["n_clauses"]}
    if st in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        rec.update(value=int(round(sr.ObjectiveValue())),
                   best_bound=int(sr.BestObjectiveBound()), proven_optimal=(st == cp_model.OPTIMAL))
        if st == cp_model.OPTIMAL:
            out["revoke_LB_relaxation"] = rec["value"]
            out["revoke_LB_relaxation_valid"] = True
        else:
            out["revoke_LB_relaxation"] = rec["best_bound"]
            out["revoke_LB_relaxation_valid"] = True   # 松弛的界仍是原问题的界
    else:
        out["revoke_LB_relaxation"] = None
    log("relax %s" % json.dumps(rec))
    out["relaxation_record"] = rec

    def rem():
        return a.budget - (time.time() - t0)

    # ---------- (2) 边界 INFEASIBLE 深证明（全势边模型） ----------
    ladder = []
    k = UB - 1
    while k >= 0 and rem() > 15:
        tb = time.time()
        mm, Xm, Lm, _ = S.build_model(plans, ids, acts, edges)
        mm.Add(Lm["revoke"] <= k)
        S.set_hints(mm, Xm, base_choice)
        b = min(max(20.0, 0.45 * rem()), 130.0)
        s2 = S.mk_solver(b)
        st2 = s2.Solve(mm)
        nm = s2.StatusName(st2)
        row = {"k_max_revoke": k, "status": nm, "budget_s": round(b, 1),
               "wall_s": round(time.time() - tb, 1)}
        ladder.append(row)
        log("certificate Σr<=%d -> %s (%.1fs)" % (k, nm, row["wall_s"]))
        if st2 == cp_model.INFEASIBLE:
            out["revoke_LB_full_model_certificate"] = k + 1
            out["certificate_k"] = k
            break
        if st2 in (cp_model.OPTIMAL, cp_model.FEASIBLE):
            ch = S.choice_of(acts, Xm, s2)
            r = S.n_revoke(acts, ch)
            row["found_revoke"] = r
            if r < UB:
                UB = r
                out["stage1_UB_revoke_improved"] = r
                json.dump(Q.solution_from_choice(plans, acts, ch),
                          io.open(os.path.join(a.out_dir, "solution_actions_phase2.json"),
                                  "w", encoding="utf-8"), ensure_ascii=False, indent=1,
                          sort_keys=True)
                log("阶段二找到更少撤销解 r=%d（另存 solution_actions_phase2.json）" % r)
            k = r - 1
            continue
        out["certificate_stopped"] = "UNKNOWN@k=%d（预算耗尽）" % k
        break
    out["certificate_ladder"] = ladder
    if "revoke_LB_full_model_certificate" not in out:
        out["revoke_LB_full_model_certificate"] = None
    lbs = [v for v in (out.get("revoke_LB_relaxation"),
                       out.get("revoke_LB_full_model_certificate"), 0) if v is not None]
    lb = max(lbs)
    out["revoke_LB_best"] = lb
    out["revoke_gap_best"] = UB - lb
    out["certified"] = (lb == UB)
    out["wall_total_s"] = round(time.time() - t0, 1)
    json.dump(out, io.open(os.path.join(a.out_dir, "r51_certificates.json"), "w",
                           encoding="utf-8"), ensure_ascii=False, indent=1)
    log("SUMMARY %s" % json.dumps({k2: out[k2] for k2 in
                                   ("revoke_LB_best", "revoke_gap_best", "certified")}))
    logf.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
