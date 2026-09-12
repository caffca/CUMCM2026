# -*- coding: utf-8 -*-
"""Q2-R32 异范式路线（Prototype Engineer 侦察实现）
连续重叠体积罚场（归一化次梯度 + 回溯下降检验） → 确定性取整 → 冲突分量局部精确修复（小 CP-SAT）

口径：ADJUDICATION.json（T_MAX=643 资源盒、半开区间、词典序四级、单参数/撤销语义）。
结构事实：code/q2_common.py（与 canonical_evaluator 同一掩码语义）+ code/star_edges.json（G* 全势边
及其动作级不相容组合表）。可行性一律用 G* 子句谓词判定，末尾再做掩码全量复核，
最终数字交 canonical_evaluator --question Q2 复算（连续罚值绝不作为目标值上报）。

阶段 A（连续引导，确定性）
  每计划两个连续变量：δf_i ∈ [max(-10,-f0_i), min(10,100-f1_i)]、
  δt_i ∈ [max(-5,-t0_i), min(5,643-末窗结束)]（= F-012 平移盒 ∩ R3 边界，逐计划收紧的盒）
  对 G* 每条边 (i,j)：P^F_ij = 频段重叠长度（仿射 max/min ⇒ 凸分段线性）；
  P^T_ij = Σ_{k,l} 时间窗重叠长度（F-005 端点对 δt 仿射 ⇒ 同型）；
  Φ(δ) = Σ_{G*} P^F·P^T + λ Σ_i w_i(|δf_i|+|δt_i|)，w={A:1,B:0.1,C:0.01}，λ 冻结=2
  乘积项破坏整体凸性 ⇒ 归一化次梯度 + "仅当 Φ_λ 不升才接受、否则步长折半"的回溯检验
  ⇒ Φ_λ 轨迹单调不升（route 指定的实现正确性哨兵；纯 Φ 的上升次数另行计数报告）。
阶段 B（确定性取整）
  按 |δ-round δ| 降序处理计划；单参数互斥 ⇒ 只保留 |值| 较大的那一维；结果必落在合法动作集内。
阶段 C（冲突分量局部精确修复）
  取整后残留冲突边 → 连通分量（大小降序、编号破平）；分量自由集 = 分量顶点 ∪ 一跳 G* 邻居，
  其余固定当前动作；子问题 = 每自由计划选一动作（含撤销）+ 成对不相容子句
  （自由-自由全量；自由-固定投影为一元禁止；固定-固定边本轮忽略，交后续轮次）；
  目标大权重标量化 W=(1e15,1e10,1e4,1)（现场断言 W1>(|F|+1)W2、W2>400(|F|+1)W3、W3>15(|F|+1)W4
  ⇒ 与词典序四级严格等价）；子问题恒有"撤销全部自由计划"解 ⇒ 不会卡死；
  逐轮直到残留=0；若某轮无进展 ⇒ 一次全局修复；再失败 ⇒ 撤销全部涉事顶点（可行兜底）。
  最后做"去撤销阶梯"：自由集 = 被撤销计划 ∪ 一跳邻居，加约束 全局撤销数 ≤ k-1 求可行，
  直到 INFEASIBLE 或预算耗尽（这是分量级证书，不是全局证书）。
"""
import argparse
import io
import json
import os
import sys
import time

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.stdout.reconfigure(encoding="utf-8")

import q2_common as Q  # noqa: E402
from ortools.sat.python import cp_model  # noqa: E402

LAM = 2.0                                   # 幅度正则权重（跑实验前冻结）
WREL = {"A": 1.0, "B": 0.1, "C": 0.01}      # 连续层的优先级倾向（非词典序承诺）
ITERS = 2000
STEP0 = 2.0
BIG_W = (1e15, 1e10, 1e4, 1.0)


# ------------------------------------------------------------------ 场
def build_field(edge_cache):
    plans = Q.load_plans()
    ids, acts, masks = Q.build_action_tables(plans)
    raw = json.load(io.open(edge_cache, encoding="utf-8"))
    edges = {tuple(k.split("|")): [tuple(v) for v in vv] for k, vv in raw["edges"].items()}
    idx = {p: n for n, p in enumerate(ids)}
    keys = sorted(edges)
    # 编码集合：元素 = ai*64+aj（与 choice 的编码一致），避免"元组∈整数集合"恒 False 的陷阱
    csets = {k: set(ai * 64 + aj for (ai, aj) in v) for k, v in edges.items()}
    lo = np.array([idx[i] for (i, j) in keys], dtype=np.int64)
    hi = np.array([idx[j] for (i, j) in keys], dtype=np.int64)
    plo, phi_, si, di_, sj, dj_, eix = [], [], [], [], [], [], []
    for e, (a, b) in enumerate(zip(lo, hi)):
        pa, pb = plans[ids[a]], plans[ids[b]]
        sa = [pa["t0"] + k * (pa["g"] + pa["d"]) for k in range(pa["n"])]
        sb = [pb["t0"] + k * (pb["g"] + pb["d"]) for k in range(pb["n"])]
        for x in sa:
            for y in sb:
                plo.append(a); phi_.append(b)
                si.append(x); di_.append(pa["d"])
                sj.append(y); dj_.append(pb["d"])
                eix.append(e)
    f0 = np.array([plans[p]["f0"] for p in ids], dtype=float)
    f1 = np.array([plans[p]["f1"] for p in ids], dtype=float)
    t0a = np.array([plans[p]["t0"] for p in ids], dtype=float)
    last_end = np.array([plans[p]["t0"] + (plans[p]["n"] - 1) * (plans[p]["g"] + plans[p]["d"])
                         + plans[p]["d"] for p in ids], dtype=float)
    adjacency = {i: set() for i in ids}
    for (i, j) in keys:
        adjacency[i].add(j)
        adjacency[j].add(i)
    return dict(plans=plans, ids=ids, acts=acts, masks=masks, edges=edges, csets=csets,
                keys=keys, idx=idx, nP=len(ids), nE=len(keys), f0=f0, f1=f1, lo=lo, hi=hi,
                plo=np.array(plo, np.int64), phi_=np.array(phi_, np.int64),
                si=np.array(si, float), sj=np.array(sj, float),
                di=np.array(di_, float), dj=np.array(dj_, float),
                eidx=np.array(eix, np.int64), adj=adjacency,
                w=np.array([WREL[plans[p]["cls"]] for p in ids], dtype=float),
                df_lo=np.maximum(-Q.DF_LIM, -f0), df_hi=np.minimum(Q.DF_LIM, Q.B_MAX - f1),
                dt_lo=np.maximum(-Q.DT_LIM, -t0a), dt_hi=np.minimum(Q.DT_LIM, Q.T_MAX - last_end))


def phi_and_grad(f, df, dt):
    """(Phi+λamp, Phi, amp, ∂/∂df, ∂/∂dt)。子梯度在折点取 0（严格不等式）。"""
    lo, hi, f0, f1 = f["lo"], f["hi"], f["f0"], f["f1"]
    a0, a1 = f0[lo] + df[lo], f1[lo] + df[lo]
    b0, b1 = f0[hi] + df[hi], f1[hi] + df[hi]
    ovb = np.maximum(0.0, np.minimum(a1, b1) - np.maximum(a0, b0))
    posb = ovb > 0.0
    g_lo = (posb & (a1 < b1)).astype(float) - (posb & (a0 > b0)).astype(float)
    g_hi = (posb & (b1 < a1)).astype(float) - (posb & (b0 > a0)).astype(float)
    si = f["si"] + dt[f["plo"]]
    sj = f["sj"] + dt[f["phi_"]]
    di, dj = f["di"], f["dj"]
    ovt = np.maximum(0.0, np.minimum(si + di, sj + dj) - np.maximum(si, sj))
    post = ovt > 0.0
    gt_i = (post & (si + di < sj + dj)).astype(float) - (post & (si > sj)).astype(float)
    gt_j = (post & (sj + dj < si + di)).astype(float) - (post & (sj > si)).astype(float)
    nE = f["nE"]
    T_edge = np.bincount(f["eidx"], weights=ovt, minlength=nE)
    GTi = np.bincount(f["eidx"], weights=gt_i, minlength=nE)
    GTj = np.bincount(f["eidx"], weights=gt_j, minlength=nE)
    Phi = float(np.dot(ovb, T_edge))
    nP = f["nP"]
    # 边级链式法则后按端点聚合（ovb/T_edge/GTi/GTj 均为 per-edge 数组 ⇒ 一次 bincount）
    Gdf = (np.bincount(lo, weights=g_lo * T_edge, minlength=nP)
           + np.bincount(hi, weights=g_hi * T_edge, minlength=nP))
    Gdt = (np.bincount(lo, weights=GTi * ovb, minlength=nP)
           + np.bincount(hi, weights=GTj * ovb, minlength=nP))
    amp = float(np.dot(f["w"], np.abs(df) + np.abs(dt)))
    Gdf = Gdf + LAM * f["w"] * np.sign(df)
    Gdt = Gdt + LAM * f["w"] * np.sign(dt)
    return Phi + LAM * amp, Phi, amp, Gdf, Gdt


def subgradient(f, deadline, log):
    n = f["nP"]
    df = np.zeros(n)
    dt = np.zeros(n)
    F0, Phi0, amp0, _, _ = phi_and_grad(f, df, dt)
    Fc, Phic, ampc = F0, Phi0, amp0
    Phi_hist_max_rise = 0.0
    mono_viol = 0
    step, it, gn_max = STEP0, 0, 0.0
    traj = [{"it": 0, "F": round(Fc, 3), "Phi": round(Phic, 3), "amp": 0.0}]
    for it in range(1, ITERS + 1):
        if time.time() > deadline:
            break
        _, _, _, Gdf, Gdt = phi_and_grad(f, df, dt)
        gn = max(float(np.abs(Gdf).max()), float(np.abs(Gdt).max()), 1e-9)
        gn_max = max(gn_max, gn)
        s = step
        acc = False
        for _t in range(30):
            ndf = np.clip(df - s * Gdf / gn, f["df_lo"], f["df_hi"])
            ndt = np.clip(dt - s * Gdt / gn, f["dt_lo"], f["dt_hi"])
            Fn, Phn, amn, _, _ = phi_and_grad(f, ndf, ndt)
            if Fn <= Fc + 1e-12:
                if Phn > Phic + 1e-9:
                    mono_viol += 1
                    Phi_hist_max_rise = max(Phi_hist_max_rise, Phn - Phic)
                df, dt, Fc, Phic, ampc = ndf, ndt, Fn, Phn, amn
                acc = True
                break
            s *= 0.5
        if not acc:
            step = max(step * 0.5, 1e-4)
            if step <= 1e-4:
                break
        else:
            step = min(max(s * 1.2, 1e-3), STEP0)
        if it % 200 == 0:
            traj.append({"it": it, "F": round(Fc, 3), "Phi": round(Phic, 3),
                         "amp": round(ampc, 3), "step": round(step, 5)})
            log("subgrad it=%d Phi=%.2f amp=%.2f F=%.2f step=%.5f" % (it, Phic, ampc, Fc, step))
    stats = {"params": {"lambda": LAM, "iters_cap": ITERS, "step0": STEP0},
             "iterations_run": it - 1, "Phi_start": round(Phi0, 3), "Phi_final": round(Phic, 3),
             "F_final": round(Fc, 3), "amp_final": round(ampc, 3),
             "F_monotone_by_construction": True,
             "Phi_upward_steps": mono_viol, "Phi_max_upward_jump": round(Phi_hist_max_rise, 4),
             "stop_reason": ("step_tol" if step <= 1e-4 else
                             ("deadline" if time.time() > deadline else "iters_cap")),
             "grad_inf_norm_max": round(gn_max, 2),
             "fractional_df": int(np.sum(np.abs(df - np.round(df)) > 1e-9)),
             "fractional_dt": int(np.sum(np.abs(dt - np.round(dt)) > 1e-9)),
             "box_saturation_rate": round(float(np.mean(
                 (np.abs(df) >= np.maximum(np.abs(f["df_lo"]), np.abs(f["df_hi"])) - 1e-9) |
                 (np.abs(dt) >= np.maximum(np.abs(f["dt_lo"]), np.abs(f["dt_hi"])) - 1e-9))), 3),
             "trajectory": traj}
    return df, dt, stats


# ------------------------------------------------------------------ 取整
def round_to_actions(f, df, dt):
    ids, acts = f["ids"], f["acts"]
    dist = np.abs(df - np.round(df)) + np.abs(dt - np.round(dt))
    order = sorted(range(f["nP"]), key=lambda k: (-float(dist[k]), ids[k]))
    choice = {}
    hist = {"keep": 0, "df": 0, "dt": 0}
    for k in order:
        pid = ids[k]
        vb = int(np.clip(int(round(float(df[k]))), int(f["df_lo"][k]), int(f["df_hi"][k])))
        vt = int(np.clip(int(round(float(dt[k]))), int(f["dt_lo"][k]), int(f["dt_hi"][k])))
        if abs(vb) >= abs(vt):
            vt = 0
        else:
            vb = 0
        want = "keep" if (vb == 0 and vt == 0) else ("df" if vb else "dt")
        hist[want] += 1
        if want == "keep":
            choice[pid] = 0
        else:
            a = next(x for x, act in enumerate(acts[pid])
                     if act[0] == want and act[1] == vb and act[2] == vt)
            choice[pid] = a
    return choice, hist


# ------------------------------------------------------------------ 谓词 / 分量
def violated(f, choice):
    ch = choice
    return [key for key in f["keys"]
            if (ch[key[0]] * 64 + ch[key[1]]) in f["csets"][key]]


def components_of(nodes, edges):
    par = {x: x for x in nodes}

    def find(a):
        while par[a] != a:
            par[a] = par[par[a]]
            a = par[a]
        return a
    for (i, j) in edges:
        ri, rj = find(i), find(j)
        if ri != rj:
            par[ri] = rj
    g = {}
    for x in nodes:
        g.setdefault(find(x), []).append(x)
    return sorted([sorted(v) for v in g.values()], key=lambda c: (-len(c), c[0]))


def make_subproblem(f, choice, free, plans, acts):
    mm = cp_model.CpModel()
    X = {}
    for v in free:
        X[v] = [mm.NewBoolVar("") for _ in acts[v]]
        mm.AddExactlyOne(X[v])
    fset = set(free)
    ncl = 0
    for key in f["keys"]:
        i, j = key
        fi, fj = i in fset, j in fset
        if not fi and not fj:
            continue
        combos = f["edges"][key]
        if fi and fj:
            Xi, Xj = X[i], X[j]
            for (ai, aj) in combos:
                mm.AddBoolOr([Xi[ai].Not(), Xj[aj].Not()])
                ncl += 1
        elif fi:
            au = choice[j]
            for (ai, aj) in combos:
                if aj == au:
                    mm.Add(X[i][ai] == 0)
                    ncl += 1
        else:
            au = choice[i]
            for (ai, aj) in combos:
                if ai == au:
                    mm.Add(X[j][aj] == 0)
                    ncl += 1
    rev = sum(X[v][len(acts[v]) - 1] for v in free)
    adjv = sum(1 - X[v][0] - X[v][len(acts[v]) - 1] for v in free)
    pri = sum(Q.PRIO[plans[v]["cls"]] * (1 - X[v][0] - X[v][len(acts[v]) - 1]
                                         + 2 * X[v][len(acts[v]) - 1]) for v in free)
    mag = sum((abs(a[1]) + abs(a[2])) * X[v][k] for v in free
              for k, a in enumerate(acts[v]) if a[0] in ("df", "dt"))
    nf = len(free)
    assert BIG_W[0] > (nf + 1) * BIG_W[1], "大权重 W1 合法性失败"
    assert BIG_W[1] > 400 * (nf + 1) * BIG_W[2], "大权重 W2 合法性失败"
    assert BIG_W[2] > 15 * (nf + 1) * BIG_W[3], "大权重 W3 合法性失败"
    mm.Minimize(BIG_W[0] * rev + BIG_W[1] * adjv + BIG_W[2] * pri + BIG_W[3] * mag)
    for v in free:
        for k, lit in enumerate(X[v]):
            mm.AddHint(lit, 1 if k == choice[v] else 0)
    return mm, X, rev, ncl


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--budget", type=float, default=430.0)
    ap.add_argument("--out-dir", default=os.path.abspath(os.path.join(HERE, "..")))
    a = ap.parse_args()
    os.makedirs(a.out_dir, exist_ok=True)
    logf = io.open(os.path.join(a.out_dir, "r32_log.txt"), "w", encoding="utf-8")
    t0 = time.time()

    def log(msg):
        line = "[%7.1fs] %s" % (time.time() - t0, msg)
        print(line, flush=True)
        logf.write(line + "\n")
        logf.flush()

    diag = {"idea": "Q2-R32", "paradigm": "continuous_overlap_penalty -> rounding -> "
                                        "component_local_exact_repair"}
    f = build_field(os.path.join(HERE, "star_edges.json"))
    plans, ids, acts, masks = f["plans"], f["ids"], f["acts"], f["masks"]
    log("field: |G*|=%d slot_pairs=%d" % (f["nE"], len(f["eidx"])))

    # 阶段 A
    dl_a = t0 + min(0.40 * a.budget, 170.0)
    df, dt, sstats = subgradient(f, dl_a, log)
    diag["field"] = sstats
    log("field: Phi %.2f -> %.2f  amp=%.2f  Phi_up_steps=%d  %s"
        % (sstats["Phi_start"], sstats["Phi_final"], sstats["amp_final"],
           sstats["Phi_upward_steps"], sstats["stop_reason"]))

    # 阶段 B
    choice, mode_hist = round_to_actions(f, df, dt)
    viol = violated(f, choice)
    allkeep = {i: 0 for i in ids}
    zviol = violated(f, allkeep)
    diag["rounding"] = {"mode_hist": mode_hist, "violated_after_round": len(viol),
                        "violated_at_all_keep": len(zviol),
                        "guide_reduction": len(zviol) - len(viol)}
    log("rounding: %s violated=%d (全恒等=%d)" % (json.dumps(mode_hist), len(viol), len(zviol)))

    # 阶段 C
    rep_log, rounds, touched = [], 0, set()
    rd = lambda: t0 + a.budget * 0.70          # noqa: E731
    while viol and time.time() < rd():
        rounds += 1
        if rounds > 25:
            break
        nodes = set()
        for (i, j) in viol:
            nodes.add(i); nodes.add(j)
        comps = components_of(nodes, viol)
        progress = False
        for c in comps:
            if time.time() > rd():
                break
            free = set(c)
            for v in c:
                free |= f["adj"][v]
            free = sorted(free)
            bud = max(3.0, min(30.0, (rd() - time.time()) / max(1, len(comps))))
            mm, X, rev, ncl = make_subproblem(f, choice, free, plans, acts)
            s = cp_model.CpSolver()
            s.parameters.max_time_in_seconds = max(2.0, bud)
            s.parameters.num_search_workers = 4
            s.parameters.random_seed = 0
            st = s.Solve(mm)
            nm = s.StatusName(st)
            rep_log.append({"round": rounds, "component": len(c), "free": len(free),
                            "clauses": ncl, "status": nm, "wall_s": round(s.WallTime(), 2),
                            "viol_before": len(viol)})
            ch = None
            if st in (cp_model.OPTIMAL, cp_model.FEASIBLE):
                ch = dict(choice)
                for v in free:
                    for k, lit in enumerate(X[v]):
                        if s.Value(lit):
                            ch[v] = k
                            break
            if ch is None:
                ch = dict(choice)
                for v in c:
                    ch[v] = len(acts[v]) - 1
                rep_log[-1]["fallback_revoke_component"] = True
            touched |= set(free)
            before = len(viol)
            choice = ch
            viol = violated(f, choice)
            progress = progress or (len(viol) < before)
        if not progress:
            nodes = set()
            for (i, j) in viol:
                nodes.add(i); nodes.add(j)
            free = set(nodes)
            for v in list(free):
                free |= f["adj"][v]
            free = sorted(free)
            mm, X, rev, ncl = make_subproblem(f, choice, free, plans, acts)
            s = cp_model.CpSolver()
            s.parameters.max_time_in_seconds = max(5.0, rd() - time.time())
            s.parameters.num_search_workers = 4
            st = s.Solve(mm)
            nm = s.StatusName(st)
            rep_log.append({"round": rounds, "global_repair": True, "free": len(free),
                            "status": nm, "wall_s": round(s.WallTime(), 2)})
            if st in (cp_model.OPTIMAL, cp_model.FEASIBLE):
                for v in free:
                    for k, lit in enumerate(X[v]):
                        if s.Value(lit):
                            choice[v] = k
                            break
                touched |= set(free)
            else:
                for v in nodes:
                    choice[v] = len(acts[v]) - 1
                rep_log[-1]["fallback_revoke_all_nodes"] = True
            viol = violated(f, choice)
            break
    diag["repair"] = {"rounds": rounds, "n_subproblems": len(rep_log),
                      "subproblems_last40": rep_log[-40:],
                      "plans_touched": len(touched), "touch_fraction": round(len(touched) / 150.0, 3),
                      "violated_after_repair": len(viol)}
    log("repair: rounds=%d subs=%d violated=%d touched=%d" % (rounds, len(rep_log), len(viol),
                                                               len(touched)))
    sol = Q.solution_from_choice(plans, acts, choice)
    tup = Q.objective_tuple(plans, sol)
    resid = Q.residual_pairs(plans, acts, masks, choice)
    diag["after_repair_internal_tuple"] = tup
    diag["mask_full_recheck_residual"] = len(resid)

    # 去撤销阶梯（分量级；口径=全局撤销数 ≤ k-1）
    ladder = []
    if not viol and tup[0] > 0:
        nodes = [pid for pid, ac in sol.items() if ac.get("revoke")]
        free = set(nodes)
        for v in list(free):
            free |= f["adj"][v]
        free = sorted(free)
        fset = set(free)
        fixed_rev = sum(1 for pid in ids if pid not in fset
                        and acts[pid][choice[pid]][0] == "revoke")
        k = tup[0]
        guard = 0
        while k - 1 - fixed_rev >= 0 and time.time() < t0 + a.budget - 20 and guard < 25:
            guard += 1
            mm, X, rev, ncl = make_subproblem(f, choice, free, plans, acts)
            mm.Add(rev <= k - 1 - fixed_rev)
            s = cp_model.CpSolver()
            s.parameters.max_time_in_seconds = max(5.0, min(60.0, (t0 + a.budget - 10) - time.time()))
            s.parameters.num_search_workers = 4
            s.parameters.random_seed = 0
            st = s.Solve(mm)
            nm = s.StatusName(st)
            ladder.append({"try_global_revoke_max": k - 1, "status": nm,
                           "wall_s": round(s.WallTime(), 2), "free": len(free),
                           "fixed_revokes": fixed_rev})
            log("derevoke ladder Σr<=%d -> %s (%.1fs)" % (k - 1, nm, s.WallTime()))
            if st not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
                break
            prev = dict(choice)
            for v in free:
                for kk, lit in enumerate(X[v]):
                    if s.Value(lit):
                        choice[v] = kk
                        break
            v2 = violated(f, choice)
            if v2:
                choice = prev
                ladder[-1]["note"] = "残留冲突非零，回退"
                break
            sol = Q.solution_from_choice(plans, acts, choice)
            tup = Q.objective_tuple(plans, sol)
            k = tup[0]
            if nm == "INFEASIBLE":
                break
    diag["derevoke_ladder"] = ladder
    resid = Q.residual_pairs(plans, acts, masks, choice)
    sol = Q.solution_from_choice(plans, acts, choice)
    tup = Q.objective_tuple(plans, sol)
    diag["final_internal_tuple"] = tup
    diag["final_internal_residual"] = len(resid)
    diag["wall_total_s"] = round(time.time() - t0, 2)
    json.dump(sol, io.open(os.path.join(a.out_dir, "solution_actions.json"), "w",
                           encoding="utf-8"), ensure_ascii=False, indent=1, sort_keys=True)
    json.dump(diag, io.open(os.path.join(a.out_dir, "r32_diagnostics.json"), "w",
                            encoding="utf-8"), ensure_ascii=False, indent=1)
    log("FINAL internal tuple=%s residual=%d listed=%d wall=%ss"
        % (tup, len(resid), len(sol), diag["wall_total_s"]))
    logf.close()
    return 0 if (not viol and not resid) else 2


if __name__ == "__main__":
    sys.exit(main())

