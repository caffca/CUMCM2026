# -*- coding: utf-8 -*-
"""Q4-R41（baseline）：周期重定时模拟退火。
状态 = 每计划恰一个动作选项（{恒等, df, dt, C 类 dg, 撤销}，与 q4common 域一致）。
能量 = 词典序标量化（TOURNAMENT_PROTOCOL.objective_scalar：1e12·rev + 1e8·adj + 1e4·ploss + mag）
       + 可行性前置层：1e15 × 残留冲突对数（不可行状态在协议单位下无定义目标，先压冲突）。
移动邻域 = 破坏-修复：90% 从当前违例涉及计划中随机抽一个（冲突加权），10% 全域均匀；均匀换动作。
冷却 = 几何编码（T0=4e14 → T1=5e7，按墙钟进度降温），末尾确定性 1-opt 抛光。
收尾 = 撤销修复投影（route 冻结设计）：若仍未零冲突，逐边撤销低优先端点直至零冲突（如实登记）。
任意时刻保持 incumbent（按 (viol, scalar) 词典序）。
用法：python solve_sa.py --seed 11 --wall 585 --out-dir <dir>
"""
import argparse, io, json, math, os, random, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import q4common as Q

W_PEN = 10 ** 15


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seed", type=int, required=True)
    ap.add_argument("--wall", type=float, default=585.0)
    ap.add_argument("--out-dir", required=True)
    a = ap.parse_args()
    os.makedirs(a.out_dir, exist_ok=True)
    t_start = time.time()
    plans = Q.CE.load_plans()
    doms = Q.build_domains(plans, allow_gap=True)
    edges, forb = Q.build_edges(plans, doms)
    ids = sorted(doms)
    pid2i = {p: k for k, p in enumerate(ids)}
    n = len(ids)
    # 每计划域：非撤销选项在前（选项 0=恒等）
    dom_opts = {pid: doms[pid] for pid in ids}
    deg = {pid: 0 for pid in ids}
    inc = {pid: [] for pid in ids}  # (other_pid, map_this->forbidden_other)
    for (i, j) in edges:
        f_map, g_map = forb[(i, j)]
        inc[i].append((j, f_map))
        inc[j].append((i, g_map))
        deg[i] += 1
        deg[j] += 1
    # 初始态：全恒等
    opt = {pid: 0 for pid in ids}
    def contrib(pid):
        c = 0
        op = opt[pid]
        for (q, fmap) in inc[pid]:
            if opt[q] in fmap.get(op, ()):
                c += 1
        return c
    V = 0
    for pid in ids:
        V += contrib(pid)
    V //= 2  # 每边两端各计一次
    def obj_counts(opt):
        r = ad = pl = mg = 0
        for pid in ids:
            o = dom_opts[pid][opt[pid]]
            r += o["rev"]; ad += o["adj"]; pl += o["ploss"]; mg += o["mag"]
        return r, ad, pl, mg
    R, A, P, M = obj_counts(opt)
    def energy(V, R, A, P, M):
        return V * W_PEN + R * 10**12 + A * 10**8 + P * 10**4 + M
    E = energy(V, R, A, P, M)
    best = (V, energy(V, R, A, P, M), dict(opt))
    rng = random.Random(a.seed)
    # 温度编码（步长谱：违例=1e15, rev=1e12, adj=1e8, ploss=1e4, mag=1）
    T0, T1 = 4e14, 5e7
    t_now = T0
    moves = 0
    first_zero_move = None
    CHECK_EVERY = 4096
    def active_plans():
        return [p for p in ids if contrib(p) > 0]
    active = active_plans()
    deadline = t_start + a.wall - 18.0  # 预留抛光与写盘
    while time.time() < deadline:
        # 几何降温：按墙钟进度
        frac = min(1.0, (time.time() - t_start) / max(1.0, deadline - t_start))
        t_now = T0 * (T1 / T0) ** frac
        for _ in range(CHECK_EVERY):
            # 破坏：90% 概率从当前违例涉及计划中抽（冲突加权），否则均匀
            if active and rng.random() < 0.9:
                pid = active[rng.randrange(len(active))]
            else:
                pid = ids[rng.randrange(n)]
            d = dom_opts[pid]
            new_o = rng.randrange(len(d))
            if new_o == opt[pid]:
                continue
            # delta 冲突（逐边端点条件变化之和）
            old_o = opt[pid]
            dV = 0
            for (q, fmap) in inc[pid]:
                oq = opt[q]
                dV += (oq in fmap.get(new_o, ())) - (oq in fmap.get(old_o, ()))  # 有符号
            o_old, o_new = d[old_o], d[new_o]
            dR = o_new["rev"] - o_old["rev"]
            dA = o_new["adj"] - o_old["adj"]
            dP = o_new["ploss"] - o_old["ploss"]
            dM = o_new["mag"] - o_old["mag"]
            dE = dV * W_PEN + dR * 10**12 + dA * 10**8 + dP * 10**4 + dM
            acc = False
            if dE <= 0:
                acc = True
            else:
                z = dE / t_now
                if z < 40.0 and rng.random() < math.exp(-z):
                    acc = True
            if acc:
                opt[pid] = new_o
                V += dV
                R += dR; A += dA; P += dP; M += dM
                E += dE
                moves += 1
                if V < best[0] or (V == best[0] and E < best[1]):
                    best = (V, E, dict(opt))
                    if V == 0 and first_zero_move is None:
                        first_zero_move = moves
            else:
                moves += 1
        # 周期一致性核对（防增量漏判；不一致则整点重算）+ 刷新冲突加权提案集
        s_all = sum(contrib(p) for p in ids)
        if s_all != V * 2:
            V = s_all // 2
            R, A, P, M = obj_counts(opt)
            E = energy(V, R, A, P, M)
        active = active_plans()
    # 确定性 1-opt 抛光：从 SA 的最优态出发，按 (V, E) 词典序改进
    opt = dict(best[2])
    V = sum(contrib(p) for p in ids) // 2
    R, A, P, M = obj_counts(opt)
    E = energy(V, R, A, P, M)
    improved = True
    polish_rounds = 0
    while improved and time.time() < t_start + a.wall:
        improved = False
        polish_rounds += 1
        for pid in ids:
            cur = opt[pid]
            bestd = (V, E, None)
            for cand in range(len(dom_opts[pid])):
                if cand == cur:
                    continue
                dV = 0
                for (q, fmap) in inc[pid]:
                    oq = opt[q]
                    dV += (oq in fmap.get(cand, ())) - (oq in fmap.get(cur, ()))  # 有符号
                o_old, o_new = dom_opts[pid][cur], dom_opts[pid][cand]
                dE = (dV * W_PEN + (o_new["rev"] - o_old["rev"]) * 10**12
                      + (o_new["adj"] - o_old["adj"]) * 10**8
                      + (o_new["ploss"] - o_old["ploss"]) * 10**4
                      + (o_new["mag"] - o_old["mag"]))
                if (V + dV, E + dE) < bestd[:2]:
                    bestd = (V + dV, E + dE, cand)
            if bestd[2] is not None:
                V, E, opt[pid] = bestd[0], bestd[1], bestd[2]
                improved = True
        if V < best[0] or (V == best[0] and E < best[1]):
            best = (V, E, dict(opt))
    wall_pre_proj = time.time() - t_start
    # 撤销修复投影（CH-04 路线冻结设计：收尾“撤销修复投影保证零冲突”；仅撤销，不做重调度）
    proj_info = {"applied": False}
    if best[0] > 0:
        state = dict(best[2])
        n_rev_added = 0
        guard = 0
        while True:
            guard += 1
            assert guard < 400
            res = Q.residual_conflicts(doms, state)
            if not res:
                break
            i, j = min(res)
            pi, pj = Q.PRIO[plans[i]["cls"]], Q.PRIO[plans[j]["cls"]]
            p = i if pi < pj else (j if pj < pi else max(i, j))
            ro = len(dom_opts[p]) - 1
            assert dom_opts[p][ro]["kind"] == "revoke"
            if state[p] == ro:  # 已撤销仍冲突（不应发生）→ 撤另一端
                p = j if p == i else i
                ro = len(dom_opts[p]) - 1
            state[p] = ro
            n_rev_added += 1
        V2 = len(Q.residual_conflicts(doms, state))
        R2, A2, P2, M2 = obj_counts(state)
        E2 = energy(V2, R2, A2, P2, M2)
        proj_info = {"applied": True, "revokes_added": n_rev_added,
                     "pre_projection_violations": best[0]}
        best = (V2, E2, state)  # 投影解强制替换（route 设计如此，即使词典序变差也如实登记）
    wall = time.time() - t_start
    # 独立复核：整点重算冲突
    V_chk = len(Q.residual_conflicts(doms, best[2]))
    sol = Q.actions_from_state(doms, best[2])
    obj, scalar = Q.opt_scalar(plans, sol)
    tag = f"seed{a.seed}"
    out = {"idea_id": "Q4-R41", "seed": a.seed, "wall_seconds": round(wall, 1),
           "moves_evaluated": moves, "polish_rounds": polish_rounds,
           "best_violations": best[0], "independent_recount_violations": V_chk,
           "first_zero_violation_move": first_zero_move,
           "projection": proj_info,
           "wall_seconds_pre_projection": round(wall_pre_proj, 1),
           "actions": sol, "objective_tuple_internal": obj, "objective_scalar": scalar,
           "final_V_after_polish": V, "T0": T0, "T1": T1,
           "energy_formula": "V*1e15 + 1e12*rev + 1e8*adj + 1e4*ploss + mag"}
    io.open(os.path.join(a.out_dir, f"sa_record_{tag}.json"), "w", encoding="utf-8").write(
        json.dumps(out, ensure_ascii=False, indent=1))
    io.open(os.path.join(a.out_dir, f"solution_{tag}.json"), "w", encoding="utf-8").write(
        json.dumps(sol, ensure_ascii=False, indent=1))
    print(f"[r41/{tag}] wall={wall:.0f}s moves={moves} viol={best[0]}/{V_chk} "
          f"tuple={obj} first_zero={first_zero_move}", flush=True)


if __name__ == "__main__":
    main()
