# -*- coding: utf-8 -*-
"""Q4-R11（精确主路线）：扩域差分 CSP / CP-SAT，词典序四层逐级固定再优化。
选项域 = {恒等} ∪ {df ±1..±10} ∪ {dt ±1..±5} ∪ {C 类 dg ±1..±10, g'>=1} ∪ {撤销}
（越界选项按 R3 剔除，见 q4common.build_domains）。
边 = 全势边（含因 dg 扩大的可达邻域）上的成对不相容子句（CH-05 警示#2a：禁止只约束原冲突边）。
--allow-gap false 时逐字退回 Q2 差分模型（域不含 dg ⇒ 势边表退化为 G*_Q2）。
输出：r11_layers.json（各层 status/LB/UB/撤销阶梯证书）+ solution_actions.json。
用法：python solve_r11.py --out-dir <dir> [--allow-gap true|false] [--hint actions.json]
      [--layer-caps L1,L2,L3,L4 秒] [--workers N] [--seed S]
"""
import argparse, io, json, os, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import q4common as Q
from ortools.sat.python import cp_model

LAYER_NAMES = ["revoke", "adjusted", "priority_loss", "magnitude"]


def build_model(plans, doms, edges, forb, hint_actions=None, workers=8, seed=7):
    m = cp_model.CpModel()
    x = {}
    for pid, opts in sorted(doms.items()):
        xs = [m.NewBoolVar(f"x_{pid}_{o}") for o in range(len(opts))]
        m.AddExactlyOne(xs)
        x[pid] = xs
    # 词典序四级线性式（与 evaluator.objective_tuple 同式）
    rev = sum(x[pid][o] * opt["rev"] for pid, opts in doms.items() for o, opt in enumerate(opts))
    adj = sum(x[pid][o] * opt["adj"] for pid, opts in doms.items() for o, opt in enumerate(opts))
    plo = sum(x[pid][o] * opt["ploss"] for pid, opts in doms.items() for o, opt in enumerate(opts))
    mag = sum(x[pid][o] * opt["mag"] for pid, opts in doms.items() for o, opt in enumerate(opts))
    n_clauses = 0
    for (i, j) in edges:
        f_map, _g_map = forb[(i, j)]
        xi, xj = x[i], x[j]
        for o1, o2s in f_map.items():
            for o2 in o2s:
                m.AddBoolOr((xi[o1].Not(), xj[o2].Not()))
                n_clauses += 1
    if hint_actions:
        idx = {pid: {json.dumps(opt["act"], sort_keys=True): o
                     for o, opt in enumerate(doms[pid]) if opt["act"]} for pid in doms}
        for pid, opts in doms.items():
            a = hint_actions.get(pid)
            key = json.dumps(a, sort_keys=True) if a else None
            if key and key in idx[pid]:
                m.AddHint(x[pid][idx[pid][key]], 1)
            else:
                m.AddHint(x[pid][0], 1)  # 恒等
    solver = cp_model.CpSolver()
    solver.parameters.num_workers = workers
    solver.parameters.random_seed = seed
    return m, solver, x, [rev, adj, plo, mag], n_clauses


def solve_lex(m, solver, x, doms, exprs, caps, trace, log=print):
    """逐层最小化；OPTIMAL 固定等式，FEASIBLE 固定 <= incumbent（界不闭合如实登记）。
    UNKNOWN 不阻断：不新增约束，继续下一层（深层无解则回退用最近一次成功层的解快照）。
    返回最终可行解 actions（或 None）。"""
    best_sol = None
    for k, (name, e) in enumerate(zip(LAYER_NAMES, exprs)):
        m.Minimize(e)
        solver.parameters.max_time_in_seconds = float(caps[k])
        t0 = time.time()
        st = solver.Solve(m)
        el = time.time() - t0
        sname = solver.StatusName(st)
        rec = {"layer": name, "cap_seconds": caps[k], "wall_seconds": round(el, 1), "status": sname}
        if sname in ("OPTIMAL", "FEASIBLE"):
            ub = int(round(solver.ObjectiveValue()))     # 当前层目标 = e 的解值
            lb = int(round(solver.BestObjectiveBound())) # 当前层目标的对偶界
            rec.update({"ub": ub, "lb": lb, "closed": sname == "OPTIMAL"})
            if sname == "OPTIMAL":
                m.Add(e == ub)   # 该层闭合：固定等式
            else:
                m.Add(e <= ub)   # 未闭合：只固定 incumbent 上界，如实登记 [lb,ub]
            best_sol = state_to_actions(doms, x, solver)  # 解快照（本层 incumbent）
        elif sname == "INFEASIBLE":
            trace.append(rec)
            log(f"[r11] layer {name}: INFEASIBLE —— 模型口径矛盾，须报告")
            return None
        trace.append(rec)
        log(f"[r11] layer {name}: {sname} lb={rec.get('lb')} ub={rec.get('ub')} {el:.1f}s")
    return best_sol


def state_to_actions(doms, x, solver):
    sol = {}
    for pid, opts in doms.items():
        for o, opt in enumerate(opts):
            if solver.Value(x[pid][o]):
                if opt["act"]:
                    sol[pid] = opt["act"]
                break
    return sol


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out-dir", required=True)
    ap.add_argument("--allow-gap", default="true")
    ap.add_argument("--hint", default=None)
    ap.add_argument("--layer-caps", default="180,120,90,90")
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--seed", type=int, default=7)
    ap.add_argument("--solution-name", default="solution_actions.json")
    a = ap.parse_args()
    allow_gap = a.allow_gap.lower() != "false"
    caps = [float(c) for c in a.layer_caps.split(",")]
    tag = "Q4" if allow_gap else "Q2reduction"
    t0 = time.time()
    os.makedirs(a.out_dir, exist_ok=True)

    def log(s):
        print(s, flush=True)

    plans = Q.CE.load_plans()
    doms = Q.build_domains(plans, allow_gap=allow_gap)
    edges, forb = Q.build_edges(plans, doms)
    t_build = time.time() - t0
    log(f"[{tag}] build: edges={len(edges)} vars={sum(len(d) for d in doms.values())} build={t_build:.1f}s")
    hint = json.load(io.open(a.hint, encoding="utf-8")) if a.hint and os.path.isfile(a.hint) else None
    m, solver, x, exprs, n_clauses = build_model(plans, doms, edges, forb, hint, a.workers, a.seed)
    log(f"[{tag}] clauses={n_clauses} modeltime={time.time()-t0:.1f}s")
    trace = []
    sol = solve_lex(m, solver, x, doms, exprs, caps, trace, log)
    wall = time.time() - t0
    ok = sol is not None
    out = {"tag": tag, "allow_gap": allow_gap, "edges": len(edges), "clause_pairs": n_clauses,
           "vars": sum(len(d) for d in doms.values()), "build_seconds": round(t_build, 1),
           "wall_seconds_total": round(wall, 1), "workers": a.workers, "seed": a.seed,
           "hint_used": bool(hint), "layers": trace,
           "solve_ok": ok}
    if ok:
        closed = [r["layer"] for r in trace if r.get("closed")]
        out["ladder_certificate"] = {
            "revoke_lb": trace[0].get("lb"), "revoke_ub": trace[0].get("ub"),
            "revoke_closed": trace[0].get("closed", False),
            "layers_closed": closed,
            "note": "OPTIMAL 层由 CP-SAT 对偶界证明该层在既定前缀下无更优解；"
                    "FEASIBLE 层报告 [lb,ub] 不闭合区间；UNKNOWN 层不固定目标继续下一层"}
        # 用 evaluator 自身口径复核模型解的元组（防止建模口径漂移）
        obj_ev = list(Q.CE.objective_tuple(plans, sol, allow_gap=allow_gap))
        out["objective_tuple_evaluator_recheck"] = obj_ev
        model_tuple = [r.get("ub") for r in trace]
        out["objective_tuple_model"] = model_tuple
        out["tuple_match"] = all(u is not None for u in model_tuple) and obj_ev == model_tuple
        # 内部零冲突断言（独立于 evaluator，基于 actions 重掩码）
        idx = {}
        for pid, opts in doms.items():
            want = sol.get(pid)
            idx[pid] = next(o for o, opt in enumerate(opts) if opt["act"] == want) if want else 0
        res = Q.residual_conflicts(doms, idx)
        out["internal_residual_conflicts"] = len(res)
        io.open(os.path.join(a.out_dir, a.solution_name), "w", encoding="utf-8").write(
            json.dumps(sol, ensure_ascii=False, indent=1))
    io.open(os.path.join(a.out_dir, "r11_layers.json"), "w", encoding="utf-8").write(
        json.dumps(out, ensure_ascii=False, indent=1))
    log(f"[{tag}] done wall={wall:.1f}s ok={ok}")


if __name__ == "__main__":
    main()
