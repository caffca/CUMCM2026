# -*- coding: utf-8 -*-
"""优化退化三角场景执行（方法学审计件，数值只进 reports/methodology/，不进 results/）。
Q2/Q4：constraint_only=全撤销端点 rev=150（合法可行端）；objective_only=无目标可行性搜索
（CP-SAT find any feasible，记录其词典序读数）；full=锦标赛植入锚（evaluator 已认证）。
Q3：constraint_only=空集 Φ=0 平凡端；objective_only=首个可行放置 Φ=1；full=认证 139（侦察基座）。"""
import io, json, os, sys, time
os.environ.setdefault("PYTHONPATH", r"F:\dsh_envlibs\mathmodel")
sys.path.insert(0, r"F:\dsh_envlibs\mathmodel")
sys.path.insert(0, r"runs\competitive\CS-20260911T071520-D2026")
from ortools.sat.python import cp_model  # noqa
import canonical_evaluator as ce  # noqa

sys.stdout.reconfigure(encoding="utf-8")
plans = ce.load_plans()

def build(q, allow_dg=False):
    """域生成（与 R51/R11 同语义），返回 plan→actions 列表与边禁元组表。"""
    acts = {}
    for pid, p in plans.items():
        lst = [("id", 0)]
        for d in range(-10, 11):
            if d and ce.mask_of(p, df=d) is not None:
                lst.append(("df", d))
        for d in (-5, 5):
            pass
        for d in range(-5, 6):
            if d and ce.mask_of(p, dt=d) is not None:
                lst.append(("dt", d))
        if allow_dg and p["cls"] == "C":
            for d in range(-10, 11):
                if d and p["g"] + d >= 1:
                    # 间隔改变后需检查全部窗在盒内（重算 slots）
                    g2 = p["g"] + d
                    ok = all(0 <= p["t0"] + k * (g2 + p["d"]) and p["t0"] + k * (g2 + p["d"]) + p["d"] <= ce.T_MAX for k in range(p["n"]))
                    if ok:
                        lst.append(("dg", d))
        lst.append(("rv", None))
        acts[pid] = [i for i in range(len(lst))]
    amap = {pid: [(k[0], k[1]) for k in acts_l] for pid, acts_l in ((p, [a[1:] for a in v]) for p, v in ((pid, plans[pid]) for pid in plans))}
    # 简化：直接构造 (kind,val) 与 masks
    kinds = {}
    masks = {}
    for pid, p in plans.items():
        kl = [("id", 0)]
        for d in range(-10, 11):
            if d and ce.mask_of(p, df=d) is not None: kl.append(("df", d))
        for d in range(-5, 6):
            if d and ce.mask_of(p, dt=d) is not None: kl.append(("dt", d))
        if allow_dg and p["cls"] == "C":
            for d in range(-10, 11):
                if d and p["g"] + d >= 1:
                    g2 = p["g"] + d
                    if all(p["t0"] + k * (g2 + p["d"]) + p["d"] <= ce.T_MAX for k in range(p["n"])):
                        kl.append(("dg", d))
        kl.append(("rv", 0))
        kinds[pid] = kl
        masks[pid] = [None if k == "rv" else (set() if k == "id" and False else ce.mask_of(p, df=v if k == "df" else 0, dt=v if k == "dt" else 0, dg=v if k == "dg" else 0)) for k, v in kl]
    ids = sorted(plans)
    edges = []
    for x in range(150):
        for y in range(x + 1, 150):
            i, j = ids[x], ids[y]
            pairs = []
            for a in range(len(kinds[i])):
                for b in range(len(kinds[j])):
                    mi, mj = masks[i][a], masks[j][b]
                    if mi is None or mj is None:
                        continue
                    if not mi.isdisjoint(mj):
                        pairs.append((a, b))
            full = len(kinds[i]) * len(kinds[j])
            if len(pairs) == full:
                edges.append((i, j))  # 恒冲突对（必须撤销一端）——强制撤销核
            elif pairs:
                edges.append((i, j, pairs))
    return ids, kinds, masks, edges

def run_objective_only(q, allow_dg=False):
    ids, kinds, masks, edges = build(allow_dg=allow_dg)
    m = cp_model.CpModel()
    X = {i: [m.NewBoolVar(f"x_{i}_{a}") for a in range(len(kinds[i]))] for i in ids}
    for i in ids:
        m.AddExactlyOne(X[i])
    for e in edges:
        if len(e) == 2:
            i, j = e
            m.Add(sum(X[i]) + sum(X[j]) <= 1 + len(kinds[i]) + len(kinds[j]) - 2)  # 占位，见下
    # 上面恒冲突边处理：i,j 所有动作对都冲突 ⇒ 至少撤销一端
    m2 = cp_model.CpModel()
    X2 = {i: [m2.NewBoolVar(f"y_{i}_{a}") for a in range(len(kinds[i]))] for i in ids}
    for i in ids:
        m2.AddExactlyOne(X2[i])
    forced = 0
    for e in edges:
        i, j = (e[0], e[1])
        if len(e) == 2:
            forced += 1
            ri = kinds[i].index(("rv", 0)); rj = kinds[j].index(("rv", 0))
            m2.Add(X2[i][ri] + X2[j][rj] >= 1)
        else:
            for a, b in e[2]:
                m2.AddBoolOr([X2[i][a], X2[j][b]]).OnlyEnforceIf([])  # placeholder never used
    for e in edges:
        if len(e) == 3:
            i, j = e[0], e[1]
            for a, b in e[2]:
                # NOT(x_i=a AND x_j=b)
                m2.AddBoolOr([X2[i][a].Not(), X2[j][b].Not()])
    # 纯可行性（无目标）
    sv = cp_model.CpSolver()
    sv.parameters.max_time_in_seconds = 60
    sv.parameters.num_search_workers = 8
    t0 = time.time()
    st = sv.Solve(m2)
    wall = time.time() - t0
    if st not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        return None, wall, forced
    acts = {}
    for i in ids:
        for a, v in enumerate(kinds[i]):
            if sv.Value(X2[i][a]):
                if v[0] != "id":
                    acts[i] = ({"rv": "revoke"}.get(v[0], v[0]), v[1]) if v[0] != "rv" else {"revoke": True}
                break
    sol = {i: ({"revoke": True} if k == "rv" else ({k: v} if not isinstance(v, dict) else v)) for i, (k, v) in ((i, (a[0], a[1])) for i, a in acts.items())}
    plain = {}
    for i, (k, v) in acts.items():
        plain[i] = {"revoke": True} if k == "rv" else {k: v}
    stats, viol = ce.apply_actions(plans, plain, allow_gap=allow_dg)
    tup = ce.objective_tuple(plans, plain, allow_gap)
    residual = sum(1 for x in viol if x.startswith("residual"))
    scalar = 1e12 * tup[0] + 1e8 * tup[1] + 1e4 * tup[2] + tup[3]
    return {"scalar": scalar, "tuple": tup, "feasible": residual == 0, "wall": round(wall, 1)}, wall, forced

res = {}
t, w, f = run_objective_only("Q2")
res["Q2"] = {"objective_only": t and t["scalar"], "objective_only_tuple": t and t["tuple"], "forced_edges": f, "wall": w}
t4, w4, f4 = run_objective_only("Q4", allow_dg=True)
res["Q4"] = {"objective_only": t4 and t4["scalar"], "objective_only_tuple": t4 and t4["tuple"], "forced_edges": f4, "wall": w4}
io.open("logs/degeneracy_run.json", "w", encoding="utf-8").write(json.dumps(res, ensure_ascii=False, indent=1))
print(json.dumps(res, ensure_ascii=False))
