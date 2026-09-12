# -*- coding: utf-8 -*-
"""Q4-R22（解析构造，全程确定性）：同余重定时消元 + 最小修补。
阶段 I（C-C 同余结构闭式消元）：
  C 类 p=10 完整梳（d=2,n=12）间冲突 ⇔ 频段交叠且 (Δt1 mod 10)∈{0,±1}（等周期条带）；
  改间隔 g'∈[1,18] 即改模基 p'=g'+2 ⇒ 在 (t1,g') 平面给出每条 CC 边的可行 g' 条带矩阵，
  对 CC 冲突图连通分量做极小化枚举（最小化 [改 g' 数, Σ|dg|, id 字典序]），闭式清零 19 条 CC 边。
阶段 II（A/B 相关边保持不动的最小修补）：
  重算全部残留冲突（含阶段 I 新引入者）；对每对 (lex 序)：端点按类权 C<B<A 排序
  （优先级低的先动），候选动作 = {df,dt,dg}（|v|升序，同幅负先，类型 df<dt<dg），
  要求 (1)消解该边且 (2)不与他方新冲突；无解 → 撤销低优先端点（C 先于 B 先于 A）。
  贪心循环至零冲突（撤销步严格递减，必然终止）。
用法：python solve_r22.py --out-dir <dir>
"""
import io, json, os, sys, time
from itertools import combinations

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import q4common as Q


def mod10_rule_check(plans, doms):
    """特殊检查：等周期完整梳规则 冲突 ⇔ 频段交叠 ∧ Δmod10∈{0,1,9} ∧ |Δ|≤(n-1)p+1 的实测符合率。"""
    cids = sorted(p for p in plans if plans[p]["cls"] == "C")
    m0 = {pid: doms[pid][0]["mask"] for pid in cids}
    n_rule = n_true = mism = 0
    mism_examples = []
    for i, j in combinations(cids, 2):
        a, b = plans[i], plans[j]
        band = min(a["f1"], b["f1"]) - max(a["f0"], b["f0"])
        d = (a["t0"] - b["t0"]) % 10
        reach = abs(a["t0"] - b["t0"]) <= 11 * 10 + 1
        pred = band > 0 and (d in (0, 1, 9)) and reach
        truth = bool(m0[i] & m0[j])
        n_rule += 1
        if truth:
            n_true += 1
        if pred != truth:
            mism += 1
            if len(mism_examples) < 5:
                mism_examples.append([i, j, "pred" if pred else "truth"])
    return {"pairs_checked": n_rule, "true_conflicts": n_true,
            "rule_mismatches": mism, "examples": mism_examples}


def strip_matrix(doms, edges_cc, plans):
    """(t1,g') 平面可行条带：每条 CC 边的 {none,dg} 选项可行性矩阵。"""
    strips = {}
    for (i, j) in edges_cc:
        si = [(o, opt) for o, opt in enumerate(doms[i]) if opt["kind"] in ("none", "dg")]
        sj = [(o, opt) for o, opt in enumerate(doms[j]) if opt["kind"] in ("none", "dg")]
        feas = []
        for oi, opi in si:
            for oj, opj in sj:
                if not (opi["mask"] & opj["mask"]):
                    feas.append([opi["v"], opj["v"]])
        strips[f"{i}|{j}"] = {
            "n_pairs_total": len(si) * len(sj), "n_pairs_feasible": len(feas),
            "gi_feasible_if_gj_none": sorted({opi["v"] for oi, opi in si
                                              for oj, opj in sj
                                              if opj["kind"] == "none" and not (opi["mask"] & opj["mask"])}),
            "gj_feasible_if_gi_none": sorted({opj["v"] for oi, opi in si
                                              for oj, opj in sj
                                              if opi["kind"] == "none" and not (opi["mask"] & opj["mask"])}),
            "sample_feas": feas[:12]}
    return strips


def cc_assign(plans, doms, edges_cc):
    """CC 冲突图连通分量上的极小化枚举。返回 (opt_idx 局部指派, 日志)。"""
    import collections
    adj = collections.defaultdict(set)
    for (i, j) in edges_cc:
        adj[i].add(j)
        adj[j].add(i)
    verts = sorted(adj)
    seen, comps = set(), []
    for v in verts:
        if v in seen:
            continue
        st, comp = [v], []
        seen.add(v)
        while st:
            u = st.pop()
            comp.append(u)
            for w in sorted(adj[u]):
                if w not in seen:
                    seen.add(w)
                    st.append(w)
        comps.append(sorted(comp))
    assign, log = {}, []
    for comp in comps:
        strip = {}
        for pid in comp:
            strip[pid] = [(o, opt) for o, opt in enumerate(doms[pid]) if opt["kind"] in ("none", "dg")]
        best = None
        import itertools
        keys = sorted(strip)
        total = 1
        for k in keys:
            total *= len(strip[k])
        mode = "brute_force"
        if total <= 400000:
            for combo in itertools.product(*[strip[k] for k in keys]):
                asg = {k: combo[t] for t, k in enumerate(keys)}
                ok = True
                for (i, j) in edges_cc:
                    if i in asg and j in asg and (asg[i][1]["mask"] & asg[j][1]["mask"]):
                        ok = False
                        break
                if ok:
                    cost = (sum(1 for k in keys if asg[k][1]["kind"] != "none"),
                            sum(asg[k][1]["mag"] for k in keys),
                            [asg[k][0] for k in keys])
                    if best is None or cost < best[0]:
                        best = (cost, asg)
        else:
            # DFS + 前向剪枝（分量过大时；顺序固定）
            mode = "dfs_pruned"
            order = keys
            def dfs(t, asg, nch, smag):
                nonlocal best
                if best is not None and (nch, smag) > best[0][:2]:
                    return
                if t == len(order):
                    cost = (nch, smag, [asg[k][0] for k in order])
                    if best is None or cost < best[0]:
                        best = (cost, dict(asg))
                    return
                pid = order[t]
                for o, opt in strip[pid]:
                    conflict = False
                    for (u, w) in edges_cc:
                        other = None
                        if u == pid and w in asg:
                            other = w
                        elif w == pid and u in asg:
                            other = u
                        if other is not None and (asg[other][1]["mask"] & opt["mask"]):
                            conflict = True
                            break
                    if conflict:
                        continue
                    asg[pid] = (o, opt)
                    dfs(t + 1, asg, nch + (opt["kind"] != "none"), smag + opt["mag"])
                    del asg[pid]
            dfs(0, {}, 0, 0)
        if best:
            for k, (o, opt) in best[1].items():
                assign[k] = o
            log.append({"component": comp, "mode": mode, "combos": total,
                        "cost": list(best[0][:2]) if best else None})
        else:
            log.append({"component": comp, "mode": mode, "combos": total, "cost": None,
                        "note": "分量内无法全消解，交由阶段 II"})
    return assign, log


def main():
    ap_path = sys.argv
    out_dir = "."
    if "--out-dir" in ap_path:
        out_dir = ap_path[ap_path.index("--out-dir") + 1]
    os.makedirs(out_dir, exist_ok=True)
    t0 = time.time()
    plans = Q.CE.load_plans()
    doms = Q.build_domains(plans, allow_gap=True)
    edges_all, forb = Q.build_edges(plans, doms)
    base = set(map(tuple, Q.base_conflict_set(plans)))
    edges_cc = [e for e in base if plans[e[0]]["cls"] == "C" and plans[e[1]]["cls"] == "C"]
    modchk = mod10_rule_check(plans, doms)
    strips = strip_matrix(doms, edges_cc, plans)
    # 阶段 I
    assign, cclog = cc_assign(plans, doms, edges_cc)
    opt_idx = {pid: 0 for pid in plans}
    for pid, o in assign.items():
        opt_idx[pid] = o
    # 阶段 II：贪心最小修补
    prio = Q.PRIO
    kind_rank = {"df": 0, "dt": 1, "dg": 2}
    def cand_options(pid):
        # 允许回到 none（撤销已动作），及 df/dt/dg；不允许在修补中用 revoke（单独分支）
        out = []
        for o, opt in enumerate(doms[pid]):
            if opt["kind"] == "none" or opt["kind"] in ("df", "dt", "dg"):
                out.append((o, opt))
        out.sort(key=lambda t: (0 if t[1]["kind"] == "none" else kind_rank[t[1]["kind"]],
                                t[1]["mag"], t[1]["v"]))
        return out
    repair_log = []
    guard = 0
    while True:
        guard += 1
        assert guard < 1000, "修补不收敛"
        res = Q.residual_conflicts(doms, opt_idx)
        if not res:
            break
        i, j = min(res)
        masks = Q.state_masks(doms, opt_idx)
        endpoints = sorted([i, j], key=lambda p: (prio[plans[p]["cls"]], p))
        applied = None
        for p in endpoints:  # 低优先（C→B→A）先动
            for o, opt in cand_options(p):
                if o == opt_idx[p]:
                    continue
                nm = opt["mask"]
                if p == i and (nm & masks[j]):
                    continue
                if p == j and (nm & masks[i]):
                    continue
                clash = False
                for q in opt_idx:
                    if q == p or not masks[q]:
                        continue
                    if nm & masks[q]:
                        clash = True
                        break
                if not clash:
                    applied = ("adjust", p, o, opt)
                    break
            if applied:
                break
        if applied:
            _, p, o, opt = applied
            opt_idx[p] = o
            repair_log.append({"edge": [i, j], "fix": "adjust", "plan": p,
                               "action": opt["act"], "kind": opt["kind"]})
        else:
            # 撤销：优先撤销低优先类（C 先于 B 先于 A）；同类取 id 大者
            if prio[plans[i]["cls"]] != prio[plans[j]["cls"]]:
                p = i if prio[plans[i]["cls"]] < prio[plans[j]["cls"]] else j
            else:
                p = max(i, j)
            ro = next(o for o, opt in enumerate(doms[p]) if opt["kind"] == "revoke")
            opt_idx[p] = ro
            repair_log.append({"edge": [i, j], "fix": "revoke", "plan": p})
    # 事后收缩（确定性）：能不动则不动、幅度能小则小；保持零冲突
    def zero_ok(idx):
        return not Q.residual_conflicts(doms, idx)
    changed = True
    shrink_steps = 0
    while changed:
        changed = False
        for p in sorted(plans):
            cur = opt_idx[p]
            if cur == 0:
                continue
            optc = doms[p][cur]
            if optc["kind"] == "revoke":
                continue
            trial = dict(opt_idx)
            trial[p] = 0
            if zero_ok(trial):  # 该动作冗余（边已被他处消解）
                opt_idx[p] = 0
                shrink_steps += 1
                changed = True
                continue
            cur_rank = kind_rank[optc["kind"]]
            better = sorted(((o, opt) for o, opt in enumerate(doms[p])
                             if opt["kind"] in ("df", "dt", "dg")
                             and (kind_rank[opt["kind"]], opt["mag"]) < (cur_rank, optc["mag"])),
                            key=lambda t: (kind_rank[t[1]["kind"]], t[1]["mag"], t[1]["v"]))
            for o, opt in better:
                trial = dict(opt_idx)
                trial[p] = o
                if zero_ok(trial):
                    opt_idx[p] = o
                    shrink_steps += 1
                    changed = True
                    break
    wall_build = time.time() - t0
    # 复核
    final_res = Q.residual_conflicts(doms, opt_idx)
    sol = Q.actions_from_state(doms, opt_idx)
    obj, scalar = Q.opt_scalar(plans, sol)
    out = {"idea_id": "Q4-R22", "deterministic": True,
           "wall_seconds_total": round(wall_build, 1),
           "mod10_rule_check": modchk,
           "cc_edges": len(edges_cc),
           "cc_strip_matrix": strips,
           "cc_components": cclog,
           "repair_steps": len(repair_log),
           "repair_log_head": repair_log[:40],
           "n_adjust_repairs": sum(1 for r in repair_log if r["fix"] == "adjust"),
           "n_revoke_repairs": sum(1 for r in repair_log if r["fix"] == "revoke"),
           "final_residual_internal": len(final_res),
           "objective_tuple_internal": obj, "objective_scalar": scalar,
           "endpoint_order_rule": "类权 C(1)<B(10)<A(100) 先动；候选按 (类型 df<dt<dg, |v|升, 负先)；"
                                  "修不动撤销 C 优先、同权撤销 id 大者"}
    io.open(os.path.join(out_dir, "r22_log.json"), "w", encoding="utf-8").write(
        json.dumps(out, ensure_ascii=False, indent=1))
    io.open(os.path.join(out_dir, "solution_actions.json"), "w", encoding="utf-8").write(
        json.dumps(sol, ensure_ascii=False, indent=1))
    print(f"[r22] wall={wall_build:.1f}s residual={len(final_res)} tuple={obj} "
          f"steps={len(repair_log)} (adj {out['n_adjust_repairs']} / rev {out['n_revoke_repairs']})",
          flush=True)


if __name__ == "__main__":
    main()
