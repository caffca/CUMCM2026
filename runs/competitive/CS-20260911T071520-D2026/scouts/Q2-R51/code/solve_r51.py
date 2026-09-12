# -*- coding: utf-8 -*-
"""Q2-R51 精确主路线（Prototype Engineer 侦察实现，CP-SAT / 成对不相容子句 + 撤销阶梯证书）

口径：ADJUDICATION.json（T_MAX=643 资源盒、半开区间、词典序四级、单参数/撤销语义）。
数据：data/canonical_plans.csv（与 canonical_evaluator.load_plans 同一文件、同一列序）。

模型（列表着色型 CSP）：每计划 i 恰好选一个动作 a ∈ A_i
  A_i = {恒等} ∪ {Δf∈±1..±10 且平移后频段在 0..99 且全部占用窗在 [0,643)}
        ∪ {Δt∈±1..±5 同理} ∪ {撤销}
约束（CH-05 警示 2a）：一律加在 **全势冲突边 G*** 上——对每一对计划枚举其动作邻域内所有
"同格共占"的动作组合 (a,b)，生成成对不相容子句 ¬x[i,a] ∨ ¬x[j,b]。只约束 297 条原冲突边
会放松模型 ⇒ 假 OPTIMAL。三重防呆：
  (1) assert 原冲突边集合 ⊆ G*；
  (2) q2_common 解析式（δf 区间 ∧ δt 集合）与掩码暴力随机抽样逐组合一致（哨兵）；
  (3) 最终方案一律交 canonical_evaluator.py --question Q2 复算（权威 objective）。

词典序逐级求 min（层1 ≤ --stage1-budget，其余层共享剩余；到预算即用当前 incumbent + 界）：
  L1 min Σr  +  撤销阶梯证书：k=0 地板测试 → 下降测试（逐 k 求可行/不可行）→ contested k 深证明
     INFEASIBLE(Σr ≤ k) ⇒ "撤销数 ≥ k+1" 的机器可复核证书；gap_revoke = UB − LB
  L2 min Σadj | Σr 锁定 → L3 min Σw·被改 → L4 min Σ|δ| → solution_actions.json
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
from ortools.sat.python import cp_model  # noqa: E402

LAYERS = ["revoke", "adjusted", "priority_loss", "magnitude_sum"]
WORKERS = 8
STATE = {}           # 随时可 dumps 的最新 incumbent（硬超时也留得住解）


def save_state(plans, acts, choice, note):
    if not choice:
        return
    STATE["choice"] = dict(choice)
    STATE["solution"] = Q.solution_from_choice(plans, acts, choice)
    STATE["internal_tuple"] = Q.objective_tuple(plans, STATE["solution"])
    STATE["note"] = note


# --------------------------------------------------------------- 模型构造
def build_model(plans, ids, acts, edges):
    m = cp_model.CpModel()
    X, keep_lit, rev_lit = {}, {}, {}
    for i in ids:
        lits = [m.NewBoolVar("") for _ in acts[i]]
        X[i] = lits
        m.AddExactlyOne(lits)
        for ai, act in enumerate(acts[i]):
            if act[0] == "keep":
                keep_lit[i] = lits[ai]
            elif act[0] == "revoke":
                rev_lit[i] = lits[ai]
        assert i in keep_lit and i in rev_lit, i
    ncl = 0
    for (i, j), combos in edges.items():
        Xi, Xj = X[i], X[j]
        for (ai, aj) in combos:
            m.AddBoolOr([Xi[ai].Not(), Xj[aj].Not()])
            ncl += 1
    adj = {i: 1 - keep_lit[i] - rev_lit[i] for i in ids}
    L = {"revoke": sum(rev_lit[i] for i in ids),
         "adjusted": sum(adj[i] for i in ids),
         "priority_loss": sum(Q.PRIO[plans[i]["cls"]] * (adj[i] + 2 * rev_lit[i]) for i in ids),
         "magnitude_sum": sum((abs(a[1]) + abs(a[2])) * X[i][ai]
                              for i in ids for ai, a in enumerate(acts[i]) if a[0] in ("df", "dt"))}
    rep = {"n_bool": sum(len(acts[i]) for i in ids), "n_clauses": ncl,
           "n_star_edges": len(edges), "n_plans": len(ids)}
    return m, X, L, rep


def choice_of(acts, X, solver):
    ch = {}
    for i in acts:
        for ai, lit in enumerate(X[i]):
            if solver.Value(lit):
                ch[i] = ai
                break
    return ch


def set_hints(m, X, choice):
    try:
        m.ClearHints()
    except Exception:
        pass
    for i, ai in choice.items():
        for aj, lit in enumerate(X[i]):
            m.AddHint(lit, 1 if aj == ai else 0)


class Recorder(cp_model.CpSolverSolutionCallback):
    """记录搜索过程中的可行解轨迹（内部四级元组）；用于报告 LNS 改进曲线。"""

    def __init__(self, plans, acts, X, cap=600):
        super().__init__()
        self.plans, self.acts, self.X, self.cap = plans, acts, X, cap
        self.rows = []

    def OnSolutionCallback(self):
        if len(self.rows) >= self.cap:
            return
        try:
            ch = choice_of(self.acts, self.X, self)
            self.rows.append(Q.objective_tuple(self.plans,
                                               Q.solution_from_choice(self.plans, self.acts, ch)))
        except Exception:
            pass


def mk_solver(tlimit):
    s = cp_model.CpSolver()
    s.parameters.max_time_in_seconds = max(1.0, float(tlimit))
    s.parameters.num_search_workers = WORKERS
    s.parameters.random_seed = 0
    return s


def n_revoke(acts, ch):
    return sum(1 for i in acts if acts[i][ch[i]][0] == "revoke")


def tuple_of(acts, plans, ch):
    return Q.objective_tuple(plans, Q.solution_from_choice(plans, acts, ch))


class Capped:
    """撤销预算模型：Σr ≤ k 单调收紧（同一实例上累积）；需要放松时才重建（≈2-3s）。"""

    def __init__(self, plans, ids, acts, edges, minimize=False):
        self.args = (plans, ids, acts, edges)
        self.minimize = minimize
        self.k = None
        self.m = self.X = self.L = None
        self.rebuilds = 0

    def get(self, k):
        if self.m is not None and self.k is not None and k <= self.k:
            if k < self.k:
                self.m.Add(self.L["revoke"] <= k)
                self.k = k
            return self.m, self.X, self.L, 0.0
        t = time.time()
        plans, ids, acts, edges = self.args
        self.m, self.X, self.L, _ = build_model(plans, ids, acts, edges)
        self.m.Add(self.L["revoke"] <= k)
        self.k = k
        self.rebuilds += 1
        return self.m, self.X, self.L, round(time.time() - t, 2)


# --------------------------------------------------------------- 层 1
def layer1(plans, ids, acts, edges, m, X, L, budget_total, stage1_budget, t0, log):
    """层1：min Σr + 撤销阶梯 INFEASIBLE 证书。返回 (R_star|None, best, rec1, ladder, certs)。

    阶梯语义（每次判定都在**同一全势边模型**的收紧副本上做 ⇒ 结论作用于完整约束集）：
      INFEASIBLE(Σr ≤ k) ⇒ "任何消解方案至少要 k+1 个撤销"（机器可复核的下界证书）
      FEASIBLE(Σr ≤ k)   ⇒ 得到一个 r ≤ k 的可行方案（该层上界样本）
    经验事实（本实例实测）：可行性模式（不带目标）找到 cap 内解只需 4-30s，而带 min Σr
    目标的模式在同样预算内常连一个 cap 内解都找不到 ⇒ 下探一律用可行性模式；
    min Σr 只跑一次用于拿到初始 incumbent 与 CP 层界（LP 分数界，实测很松）。
    """
    certs, ladder = {}, []
    tail_reserve = 140.0                      # 留给 L2-L4 的最小秒数
    l1_deadline = t0 + max(60.0, min(stage1_budget, budget_total - tail_reserve))

    def rem1():
        return l1_deadline - time.time()

    cap = Capped(plans, ids, acts, edges)
    box = {"best": None, "best_tuple": None, "UB": None, "LB": 0}

    def test(k, tlimit, phase, with_obj=False):
        mm, XX, LL, build_s = cap.get(k)
        if box["best"]:
            set_hints(mm, XX, box["best"])
        if with_obj:
            mm.Minimize(LL["revoke"])
        s = mk_solver(max(1.0, tlimit - build_s))
        st = s.Solve(mm)
        nm = s.StatusName(st)
        row = {"k_max_revoke": k, "phase": phase, "status": nm, "budget_s": round(tlimit, 1),
               "model_build_s": build_s, "wall_s": round(build_s + s.WallTime(), 1),
               "objective_used": bool(with_obj)}
        ladder.append(row)
        r = None
        if st in (cp_model.OPTIMAL, cp_model.FEASIBLE):
            ch = choice_of(acts, XX, s)
            tup = tuple_of(acts, plans, ch)
            r = tup[0]
            row.update(found_revoke=r, found_tuple=tup)
            if with_obj and st == cp_model.OPTIMAL:
                box["LB"] = max(box["LB"], r)
            elif with_obj:
                box["LB"] = max(box["LB"], int(s.BestObjectiveBound()))
            if box["best_tuple"] is None or tup < box["best_tuple"]:
                box["best"], box["best_tuple"] = ch, tup
                box["UB"] = r if box["UB"] is None else min(box["UB"], r)
                save_state(plans, acts, ch, "ladder:%s:k=%d:tuple=%s" % (phase, k, tup))
        log("ladder[%s] Σr<=%d -> %s (%.1fs) found_r=%s" % (phase, k, nm, row["wall_s"], r))
        return nm, r

    # (0) min Σr：一次，拿初始 incumbent 与该层 CP 界
    tl = max(8.0, min(0.16 * (l1_deadline - t0), max(8.0, rem1() - 60.0)))
    m.Minimize(L["revoke"])
    s1 = mk_solver(tl)
    rc = Recorder(plans, acts, X)
    st1 = s1.Solve(m, rc)
    rec1 = {"stage": 1, "layer": LAYERS[0], "mode": "min_sum_revoke", "status": s1.StatusName(st1),
            "budget_s": round(tl, 1), "wall_s": round(s1.WallTime(), 1),
            "n_conflicts": s1.NumConflicts(), "n_branches": s1.NumBranches(),
            "n_solutions_logged": len(rc.rows)}
    if st1 in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        c1 = choice_of(acts, X, s1)
        t1 = tuple_of(acts, plans, c1)
        box["best"], box["best_tuple"] = c1, t1
        box["UB"] = min(int(round(s1.ObjectiveValue())), t1[0])
        box["LB"] = int(s1.BestObjectiveBound())
        rec1.update(value=box["UB"], best_bound=box["LB"], proven_optimal=(st1 == cp_model.OPTIMAL))
        save_state(plans, acts, c1, "L1:min_sum_revoke")
    else:
        rec1.update(value=None, best_bound=None, proven_optimal=False)
    rec1["trajectory_min_revoke"] = min([r[0] for r in rc.rows]) if rc.rows else None
    log("L1(min Σr) %s" % json.dumps(rec1))
    certs["L1_min_revoke_solve"] = {kk: rec1.get(kk) for kk in
                                    ("status", "value", "best_bound", "proven_optimal", "wall_s")}
    if box["UB"] is None:
        return None, None, rec1, ladder, certs

    # (a) 地板测试 k=0（CH-05 探针：该判定通常几秒内出 INFEASIBLE）⇒ 撤销数 ≥1
    if box["UB"] > 0 and rem1() > 60:
        nm, r = test(0, min(20.0, max(6.0, 0.05 * (l1_deadline - t0))), "floor")
        if nm == "INFEASIBLE":
            box["LB"] = max(box["LB"], 1)
            certs["revoke_LB_floor_certificate"] = 1
        elif r == 0:
            certs["floor_feasible_zero_revoke"] = True

    # (b) 阶梯下探：先大步（8→4→2→1）后逐格；UNKNOWN 时同一 k 预算翻倍重试（最多 3 次）
    contested = None
    jump, guard, attempts = 8, 0, {}
    deep_reserve = max(35.0, 0.28 * (l1_deadline - t0))
    while box["LB"] < box["UB"] and rem1() > deep_reserve and guard < 60:
        guard += 1
        k = box["UB"] - jump
        if k < box["LB"]:
            k = box["LB"]                      # 夹到已知下界（=UB-1 时的边界探针）
        if k >= box["UB"]:
            break
        attempts[k] = attempts.get(k, 0) + 1
        if attempts[k] > 3:                    # 同一 k 已加深 3 次仍无解 ⇒ 交给 (c) 深证明
            contested = k
            break
        base = min(max(8.0, 0.06 * (l1_deadline - t0)), 14.0)
        b = min(base * (2 ** (attempts[k] - 1)), max(12.0, 0.45 * rem1()))
        nm, r = test(k, b, "lapse%d_try%d" % (jump, attempts[k]))
        if nm == "INFEASIBLE":
            box["LB"] = max(box["LB"], k + 1)
            jump = max(1, jump // 2)
            attempts[k] = 99
            continue
        if r is not None:
            jump = max(1, jump // 2)
            attempts[k] = 0                    # k 变了就重新计尝试数
            continue
        # UNKNOWN：保持同一 k，下一轮预算翻倍
    
    # (c) 边界深证明：固定攻 k=UB-1（可行⇒UB 再降；INFEASIBLE⇒该层 LB=UB 闭合证书），
    #     押上层1剩余全部预算。contested 仅作诊断记录。
    k_target = box["UB"] - 1
    if k_target >= box["LB"] and box["UB"] > box["LB"] and rem1() > 20:
        nm, r = test(k_target, max(20.0, rem1()), "deep_certificate")
        if nm == "INFEASIBLE":
            box["LB"] = max(box["LB"], k_target + 1)
            certs["deep_certificate_outcome"] = "INFEASIBLE@k=%d ⇒ 撤销数≥%d" % (k_target, k_target + 1)
        elif r is not None:
            certs["deep_certificate_outcome"] = "FEASIBLE@k=%d (r=%d)" % (k_target, r)
        else:
            certs["deep_certificate_outcome"] = \
                "UNKNOWN@k=%d（层1预算耗尽，该层无 INFEASIBLE 证书）" % k_target
    certs["revoke_LB_after_ladder"] = box["LB"]
    certs["revoke_UB_incumbent"] = box["UB"]
    certs["revoke_gap"] = box["UB"] - box["LB"]
    certs["ladder_rebuilds"] = cap.rebuilds
    certs["contested_k"] = contested
    certified = (box["LB"] == box["UB"])
    certs["revoke_LB_certificate"] = box["LB"]
    certs["revoke_layer_certified_optimal"] = certified
    R_star = box["UB"]
    m.Add(L["revoke"] == R_star if certified else L["revoke"] <= R_star)
    log("revoke locked at %d (LB=%d, certified=%s)" % (R_star, box["LB"], certified))
    return R_star, box["best"], rec1, ladder, certs


# --------------------------------------------------------------- 层 2/3/4
def layer_tail(plans, ids, acts, m, X, L, R_star, choice, budget_total, t0, log, stages, certs):
    def rem():
        return budget_total - (time.time() - t0)

    locked = {"revoke": R_star}
    cur = choice
    shares = {2: 0.45, 3: 0.35, 4: 0.97}
    for stage, key in ((2, "adjusted"), (3, "priority_loss"), (4, "magnitude_sum")):
        if rem() <= 12:
            stages.append({"stage": stage, "layer": key, "mode": "min_" + key,
                           "status": "SKIPPED_no_budget", "budget_s": 0.0, "wall_s": 0.0,
                           "value": None, "best_bound": None, "proven_optimal": False})
            continue
        tl = min(max(10.0, rem() * shares[stage]), max(1.0, rem() - 8.0))
        m.Minimize(L[key])
        set_hints(m, X, cur)
        s3 = mk_solver(tl)
        rc3 = Recorder(plans, acts, X, cap=200)
        st3 = s3.Solve(m, rc3)
        rec = {"stage": stage, "layer": key, "mode": "min_" + key, "status": s3.StatusName(st3),
               "budget_s": round(tl, 1), "wall_s": round(s3.WallTime(), 1),
               "n_conflicts": s3.NumConflicts(), "n_branches": s3.NumBranches()}
        if st3 in (cp_model.OPTIMAL, cp_model.FEASIBLE):
            v = int(round(s3.ObjectiveValue()))
            ch3 = choice_of(acts, X, s3)
            r3 = n_revoke(acts, ch3)
            rec.update(value=v, best_bound=int(s3.BestObjectiveBound()),
                       proven_optimal=(st3 == cp_model.OPTIMAL),
                       tuple_of_solution=tuple_of(acts, plans, ch3))
            if r3 > R_star:
                rec["note"] = "revoke 层回退(%d>%d)：不采纳该解" % (r3, R_star)
            else:
                if r3 < R_star:
                    rec["note"] = "顺带发现更少撤销(%d<%d)，按词典序采纳并重锁层1" % (r3, R_star)
                    R_star = r3
                    m.Add(L["revoke"] == r3)
                    certs["revoke_UB_incumbent"] = r3
                cur = choice = ch3
                locked[key] = v
                save_state(plans, acts, ch3, "L%d:%s=%s" % (stage, key, v))
        else:
            rec.update(value=None, best_bound=None, proven_optimal=False)
        stages.append(rec)
        log("L%d %s" % (stage, json.dumps(rec, ensure_ascii=False)))
        if rec.get("value") is not None:
            m.Add(L[key] == rec["value"])
            if not rec["proven_optimal"]:
                certs.setdefault("layers_locked_unproven", []).append(key)
    return R_star, choice, locked


# --------------------------------------------------------------- 主流程
def run(budget_total, stage1_budget, log, verify_star=True, state=None):
    if state is None:
        state = {}
    t0 = time.time()
    plans = Q.load_plans()
    ids, acts, masks = Q.build_action_tables(plans)
    out_dir = os.path.dirname(HERE)
    cache = os.path.join(out_dir, "star_edges.json")
    if os.path.isfile(cache):
        raw = json.load(io.open(cache, encoding="utf-8"))
        edges = {tuple(k.split("|")): [tuple(v) for v in vv] for k, vv in raw["edges"].items()}
        stats = dict(raw["stats"], source="cache")
    else:
        t = time.time()
        edges, stats = Q.build_star_edges(plans, acts, masks, verify=False)
        stats["build_seconds"] = round(time.time() - t, 2)
        stats["source"] = "built"
        json.dump({"edges": {"%s|%s" % k: v for k, v in edges.items()}, "stats": stats},
                  io.open(cache, "w", encoding="utf-8"), ensure_ascii=False)
    tv = time.time()
    if verify_star:
        Q._verify_edges(plans, acts, masks, edges, sample=250)
        stats["mask_recheck"] = "PASS(sample=250)"
    else:
        stats["mask_recheck"] = "skipped"
    stats["mask_recheck_seconds"] = round(time.time() - tv, 1)
    base = [(i, j) for x, i in enumerate(ids) for j in ids[x + 1:]
            if not masks[(i, "keep", 0, 0)].isdisjoint(masks[(j, "keep", 0, 0)])]
    stats["base_conflicts"] = len(base)
    stats["star_covers_base"] = bool(set(base).issubset(set(edges)))
    log("G* %s" % json.dumps(stats, ensure_ascii=False))
    assert stats["star_covers_base"], "G* 剪枝不完备（原冲突边未被覆盖）——禁止继续"

    tb = time.time()
    m, X, L, rep = build_model(plans, ids, acts, edges)
    rep["build_seconds"] = round(time.time() - tb, 2)
    log("model %s" % json.dumps(rep))

    R_star, choice, rec1, ladder, certs = layer1(plans, ids, acts, edges, m, X, L,
                                                 budget_total, stage1_budget, t0, log)
    stages = [rec1] if rec1 else []
    if R_star is None or choice is None:
        return dict(stages=stages, ladder=ladder, certs=certs, model=rep, choice=None,
                    stats=stats, total_seconds=round(time.time() - t0, 1))
    R_star, choice, locked = layer_tail(plans, ids, acts, m, X, L, R_star, choice,
                                        budget_total, t0, log, stages, certs)
    sol = Q.solution_from_choice(plans, acts, choice)
    resid = Q.residual_pairs(plans, acts, masks, choice)
    certs["revoke_final_incumbent"] = n_revoke(acts, choice)
    return dict(stages=stages, ladder=ladder, certs=certs, model=rep, choice=choice,
                stats=stats, locked=locked, internal_tuple=Q.objective_tuple(plans, sol),
                internal_residual=len(resid), solution=sol,
                total_seconds=round(time.time() - t0, 1))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--budget", type=float, default=560.0)
    ap.add_argument("--stage1-budget", type=float, default=300.0)
    ap.add_argument("--out-dir", default=os.path.abspath(os.path.join(HERE, "..")))
    ap.add_argument("--tag", default="")
    ap.add_argument("--no-star-verify", action="store_true")
    a = ap.parse_args()
    os.makedirs(a.out_dir, exist_ok=True)
    logf = io.open(os.path.join(a.out_dir, "run_log%s.txt" % a.tag), "w", encoding="utf-8")
    t_start = time.time()

    def log(msg):
        line = "[%7.1fs] %s" % (time.time() - t_start, msg)
        print(line, flush=True)
        logf.write(line + "\n")
        logf.flush()

    try:
        res = run(a.budget, a.stage1_budget, log, verify_star=not a.no_star_verify)
    except Exception as e:
        import traceback
        log("EXCEPTION %s\n%s" % (e, traceback.format_exc()))
        json.dump({"error": str(e), "trace": traceback.format_exc()},
                  io.open(os.path.join(a.out_dir, "cpsat_report%s.json" % a.tag), "w",
                          encoding="utf-8"), ensure_ascii=False, indent=1)
        # 异常也要留住当前 incumbent（禁止丢解）
        if STATE.get("solution"):
            json.dump(STATE["solution"],
                      io.open(os.path.join(a.out_dir, "solution_actions_partial%s.json" % a.tag),
                              "w", encoding="utf-8"), ensure_ascii=False, indent=1, sort_keys=True)
            log("partial solution kept: %s (%s)" % (STATE.get("internal_tuple"), STATE.get("note")))
        logf.close()
        return 3
    rep = {k: v for k, v in res.items() if k not in ("choice", "solution")}
    rep["wall_total_s"] = round(time.time() - t_start, 1)
    rep["params"] = {"budget": a.budget, "stage1_budget": a.stage1_budget,
                     "num_search_workers": WORKERS, "random_seed": 0,
                     "encoding": "pairwise nogood clauses over full potential-conflict graph G*"}
    json.dump(rep, io.open(os.path.join(a.out_dir, "cpsat_report%s.json" % a.tag), "w",
                           encoding="utf-8"), ensure_ascii=False, indent=1)
    if not res.get("choice"):
        log("NO INCUMBENT -> status=failed")
        logf.close()
        return 2
    sol = res["solution"]
    json.dump(sol, io.open(os.path.join(a.out_dir, "solution_actions%s.json" % a.tag), "w",
                           encoding="utf-8"), ensure_ascii=False, indent=1, sort_keys=True)
    meta = {"internal_objective_tuple": res["internal_tuple"],
            "internal_residual_pairs": res["internal_residual"],
            "n_listed_actions": len(sol),
            "objective_scalar_internal": Q.scalarize(res["internal_tuple"]),
            "solve_seconds": res["total_seconds"]}
    json.dump(meta, io.open(os.path.join(a.out_dir, "solution_meta%s.json" % a.tag), "w",
                            encoding="utf-8"), ensure_ascii=False, indent=1)
    log("solution tuple(internal)=%s residual=%d listed=%d"
        % (res["internal_tuple"], res["internal_residual"], len(sol)))
    logf.close()
    return 0


if __name__ == "__main__":
    sys.exit(main())
