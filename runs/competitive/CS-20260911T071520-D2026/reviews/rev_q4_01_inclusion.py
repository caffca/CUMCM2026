# -*- coding: utf-8 -*-
"""REV-Q4-01 附件脚本 B：
 (A) 用候选自带的构建器（只读 import，禁写字节码）独立复算 G*_Q2 ⊆ G*_Q4 与选项域逐字包含；
 (B) 更简基线对照：纯「按度撤销」greedy 顶点覆盖，看撤销数能不能低于三候选；
 (C) 冲突图最大匹配 ⇒ 「只撤销」口径的撤销数下界；
 (D) R22 最终解中 dg 动作存活情况 / 阶段 I 指派被阶段 II 覆盖的比例；
 (E) R11 的 hint 选择后果：把 Q2-R51 解（6 撤销）当 UB 锚的可达性复算。
"""
import io, json, os, sys

RUN = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.dont_write_bytecode = True          # 禁止向被审目录写 __pycache__
os.environ["PYTHONDONTWRITEBYTECODE"] = "1"
sys.stdout.reconfigure(encoding="utf-8")
sys.path.insert(0, os.path.join(RUN, "scouts", "Q4-R11", "code"))
import q4common as Q                    # noqa: E402  只读复用候选构建器

out = {}
plans = Q.CE.load_plans()

# ---------- (A) 域与势边集的包含关系 ----------
d2 = Q.build_domains(plans, allow_gap=False)
d4 = Q.build_domains(plans, allow_gap=True)
e2, f2 = Q.build_edges(plans, d2)
e4, f4 = Q.build_edges(plans, d4)


def sig(doms):
    return {pid: tuple((o["kind"], o["v"], o["mask"], o["ploss"], o["mag"], o["rev"], o["adj"],
                        json.dumps(o["act"], sort_keys=True) if o["act"] else None)
                       for o in opts) for pid, opts in doms.items()}


s2, s4 = sig(d2), sig(d4)
dom_subset, dom_order_ok, bad = True, True, []
for pid in sorted(s2):
    a, b = list(s2[pid]), list(s4[pid])
    if not set(a).issubset(set(b)):
        dom_subset = False
        bad.append(pid)
    # 逐字前缀：Q2 序列 = Q4 序列删去 dg 项
    b_no_dg = [x for x in b if x[0] != "dg"]
    if a != b_no_dg:
        dom_order_ok = False
out["A_domains"] = dict(vars_q2=sum(len(v) for v in d2.values()),
                        vars_q4=sum(len(v) for v in d4.values()),
                        set_subset=dom_subset, verbatim_prefix=dom_order_ok,
                        bad_examples=bad[:5])
E2, E4 = set(map(tuple, e2)), set(map(tuple, e4))
out["A_edges"] = dict(n_q2=len(E2), n_q4=len(E4), subset=E2.issubset(E4),
                      missing_in_q4=sorted(E2 - E4)[:10],
                      new_in_q4=len(E4 - E2),
                      claimed=dict(q2=1693, q4=2117),
                      claim_matches_recount=(len(E2) == 1693 and len(E4) == 2117))
# 禁元组（子句）集合包含：以 (i,kind,v)_o1 -> (j,kind,v)_o2 规范化
def clause_set(doms, edges, forb):
    S = set()
    for (i, j) in edges:
        fmap, _ = forb[(i, j)]
        for o1, o2s in fmap.items():
            k1 = (doms[i][o1]["kind"], doms[i][o1]["v"])
            for o2 in o2s:
                k2 = (doms[j][o2]["kind"], doms[j][o2]["v"])
                S.add((i, k1, j, k2))
    return S


C2 = clause_set(d2, e2, f2)
C4 = clause_set(d4, e4, f4)
out["A_clauses"] = dict(n_q2=len(C2), n_q4=len(C4), subset=C2.issubset(C4),
                        missing=sorted(list(C2 - C4))[:5],
                        claimed_q2=270626, claimed_q4=437962,
                        recount_matches_claim=(len(C2) == 270626 and len(C4) == 437962))

# ---------- (B) 更简基线：按度撤销的贪心顶点覆盖 ----------
def masks_of(actions):
    ms = {}
    for pid, p in plans.items():
        a = actions.get(pid, {})
        if a.get("revoke"):
            continue
        m = Q.mask_int(p, df=int(a.get("df", 0)), dt=int(a.get("dt", 0)), dg=int(a.get("dg", 0)))
        if m is None:
            return None
        ms[pid] = m
    return ms


def conflict_edges(ms):
    ids = sorted(ms)
    E = []
    for x in range(len(ids)):
        for y in range(x + 1, len(ids)):
            if ms[ids[x]] & ms[ids[y]]:
                E.append((ids[x], ids[y]))
    return E


base_ms = masks_of({})
baseE = conflict_edges(base_ms)
out["B_base"] = dict(n_conflict_edges=len(baseE))
deg = {}
for i, j in baseE:
    deg[i] = deg.get(i, 0) + 1
    deg[j] = deg.get(j, 0) + 1
E = set(baseE)
rev = []
while E:
    d = {}
    for (i, j) in E:
        d[i] = d.get(i, 0) + 1
        d[j] = d.get(j, 0) + 1
    v = max(d, key=lambda k: (d[k], [-ord(c) for c in k]))
    rev.append(v)
    E = {(i, j) for (i, j) in E if i != v and j != v}
out["B_greedy_revoke_only"] = dict(revokes=len(rev), plans=sorted(rev)[:20],
                                   note="仅撤销、不调整（无任何求解器）的度贪心顶点覆盖：撤销数上界")
# 更简基线 B2：先按 Q4 允许的单参数最小修补（对每条边试 df/dt/dg 单端点消解，失败才撤销）
# —— 与 R22 同族但用最大度端点先动，检验 R22 的 66 是否只是端点选择规则造成
E = set(baseE)
actions = {}
for _round in range(1000):
    if not E:
        break
    d = {}
    for (i, j) in E:
        d[i] = d.get(i, 0) + 1
        d[j] = d.get(j, 0) + 1
    i, j = min(E)                       # 确定性：字典序最小残余边（与 R22 同）
    # 端点顺序：类权低者优先（C<B<A），同权取度大者 —— 与 R22 的差异仅在是否用度信息
    ends = sorted({i, j}, key=lambda k: (Q.PRIO[plans[k]["cls"]], -d.get(k, 0), k))
    done = False
    for pid in ends:
        for o, opt in enumerate(d4[pid]):
            if opt["kind"] in ("none", "revoke") or not opt["act"]:
                continue
            trial = dict(actions)
            trial[pid] = opt["act"]
            ms = masks_of(trial)
            if ms is None:
                continue
            ne = conflict_edges(ms)
            if len(ne) < len(E):
                actions[pid] = opt["act"]
                E = set(ne)
                done = True
                break
        if done:
            break
    if not done:
        p = ends[0]
        actions[p] = {"revoke": True}
        E = {(a, b) for (a, b) in E if a != p and b != p}
ms = masks_of(actions)
t, sc = Q.opt_scalar(plans, actions)
out["B2_degree_aware_repair"] = dict(revokes=t[0], adjusted=t[1], ploss=t[2], mag=t[3],
                                     residual=len(conflict_edges(ms)) if ms else None,
                                     rule="与 R22 同（字典序最小残余边 + 类权低者优先），但端点同权时取度大者")

# ---------- (C) 只撤销口径的匹配下界（Gallai: tau >= nu） ----------
# 一般图极大匹配（简单增广路径近似，足够给下界）
adj = {p: set() for p in plans}
for (i, j) in baseE:
    adj[i].add(j)
    adj[j].add(i)
match = {}
for v in sorted(adj, key=lambda k: -len(adj[k])):
    if v in match:
        continue
    for w in sorted(adj[v], key=lambda k: -len(adj[k])):
        if w not in match:
            match[v] = w
            match[w] = v
            break
out["C_matching"] = dict(maximal_matching_size=len(match) // 2,
                         meaning="只撤销口径下顶点覆盖 >= 匹配数（撤销数 LB 的组合参照）")

# ---------- (D) R22 最终解中 dg 存活 ----------
r22 = json.load(io.open(os.path.join(RUN, "scouts", "Q4-R22", "run", "solution_actions.json"),
                        encoding="utf-8"))
log22 = json.load(io.open(os.path.join(RUN, "scouts", "Q4-R22", "run", "r22_log.json"),
                          encoding="utf-8"))
stageI_dg = {}
for comp in log22["cc_components"]:
    if comp.get("cost"):
        for pid in comp["component"]:
            pass
final_dg = {k: int(v["dg"]) for k, v in r22.items() if v.get("dg")}
out["D_r22"] = dict(final_dg_actions=len(final_dg), final_dg_detail=final_dg,
                   cc_edges=19, stage1_components_with_cost=sum(1 for c in log22["cc_components"] if c.get("cost")),
                   stage1_failed_components=[c["component"] for c in log22["cc_components"] if not c.get("cost")],
                   note_stage1_cc_resolved_claim="16/19")

# ---------- (E) R11 hint 后果：把 6 撤销解塞进 R11 模型口径检查是否合法 ----------
q2r51 = json.load(io.open(os.path.join(RUN, "scouts", "Q2-R51", "solution_actions.json"),
                          encoding="utf-8"))
ok_keys = all(list(a.keys()) == ["df"] or list(a.keys()) == ["dt"] or a.get("revoke")
              for a in q2r51.values())
ms = masks_of(q2r51)
out["E_q2r51_in_q4_model"] = dict(single_param_only=ok_keys,
                                  has_dg=bool([a for a in q2r51.values() if a.get("dg")]),
                                  residual_conflicts=len(conflict_edges(ms)) if ms else "invalid",
                                  tuple=Q.opt_scalar(plans, q2r51)[0],
                                  horizon_ok=ms is not None,
                                  meaning="Q2-R51 侦察解（6 撤销）在 Q4 口径下可行 ⇒ Q4 撤销层已知 UB 应为 6，不是 8")

io.open(os.path.join(RUN, "reviews", "_tmp", "recheck_out_B.json"), "w", encoding="utf-8").write(
    json.dumps(out, ensure_ascii=False, indent=1, default=str))
print(json.dumps(out, ensure_ascii=False, indent=1, default=str)[:4000])
