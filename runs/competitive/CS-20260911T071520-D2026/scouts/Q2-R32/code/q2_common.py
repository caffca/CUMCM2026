# -*- coding: utf-8 -*-
"""Q2 侦察共享内核（Prototype 组，只读消费 canonical_evaluator 的口径）

口径唯一来源：
  runs/competitive/CS-20260911T071520-D2026/ADJUDICATION.json（T_MAX=643、半开区间、
  词典序四级、单参数/撤销语义、F-006 冲突判据）
  数据 = data/canonical_plans.csv（与 canonical_evaluator.load_plans 同一文件、同一列序）

本模块只做"结构事实"：动作枚举、占用掩码、全势冲突边 G*（含动作级不相容组合表）、
目标元组复刻（内部打分用；最终一律经 canonical_evaluator 复算）。
"""
import io
import os
import sys

T_MAX = 643
B_MAX = 100
DF_LIM = 10
DT_LIM = 5
PRIO = {"A": 100, "B": 10, "C": 1}

# 本 scout 的 code/ 目录 -> run 目录
HERE = os.path.dirname(os.path.abspath(__file__))
RUN_DIR = os.path.abspath(os.path.join(HERE, "..", "..", ".."))
WORKSPACE = os.path.abspath(os.path.join(RUN_DIR, "..", "..", ".."))
CSV_CANDIDATES = [
    os.path.join(WORKSPACE, "data", "canonical_plans.csv"),
    os.path.abspath(os.path.join(RUN_DIR, "..", "..", "..", "data", "canonical_plans.csv")),
    "data/canonical_plans.csv",
]


def csv_path():
    for p in CSV_CANDIDATES:
        if os.path.isfile(p):
            return p
    raise FileNotFoundError("canonical_plans.csv not found")


def load_plans(path=None):
    """列序与 canonical_evaluator.load_plans 完全一致（不得自作主张重排列）。"""
    path = path or csv_path()
    plans = {}
    rd = io.open(path, encoding="utf-8").read().splitlines()
    for line in rd[1:]:
        a = line.split(",")
        plans[a[0]] = dict(id=a[0], cls=a[0][0], f0=int(a[2]), f1=int(a[3]),
                           t0=int(a[4]), t1=int(a[5]), g=int(a[6]), n=int(a[7]),
                           d=int(a[5]) - int(a[4]))
    assert len(plans) == 150, len(plans)
    return plans


def raw_slots(p, dt=0):
    g = p["g"]
    return [(p["t0"] + dt + k * (g + p["d"]), p["t0"] + dt + k * (g + p["d"]) + p["d"])
            for k in range(p["n"])]


def mask_of(p, df=0, dt=0):
    """占用单元集合；越界（R3_shift_boundary）返回 None。与 evaluator.mask_of 同语义。"""
    f0, f1 = p["f0"] + df, p["f1"] + df
    if f0 < 0 or f1 > B_MAX:
        return None
    m = set()
    for (s, e) in raw_slots(p, dt):
        if s < 0 or e > T_MAX:
            return None
        for t in range(s, e):
            base = t * B_MAX
            for f in range(f0, f1):
                m.add(base + f)
    return frozenset(m)


# ---- 动作枚举 ---------------------------------------------------------------
# 动作编码：('keep',0,0) / ('df',v,0) / ('dt',0,v) / ('revoke',0,0)
ACTION_KINDS = ("keep", "df", "dt", "revoke")


def enumerate_actions(p):
    """每计划动作选项 = {恒等} ∪ {df∈±1..±10 且平移后频段在 0..99 且全部占用窗在 [0,643)}
                        ∪ {dt∈±1..±5  同理}                    ∪ {撤销}
    恒等动作本身若越界（原始数据已越界）则不可用——由 identity_ok 决定。"""
    acts = []
    ident_ok = mask_of(p, 0, 0) is not None
    if ident_ok:
        acts.append(("keep", 0, 0))
    for v in list(range(-DF_LIM, 0)) + list(range(1, DF_LIM + 1)):
        if mask_of(p, df=v) is not None:
            acts.append(("df", v, 0))
    for v in list(range(-DT_LIM, 0)) + list(range(1, DT_LIM + 1)):
        if mask_of(p, dt=v) is not None:
            acts.append(("dt", 0, v))
    acts.append(("revoke", 0, 0))
    return acts


def build_action_tables(plans):
    ids = sorted(plans)
    acts = {i: enumerate_actions(plans[i]) for i in ids}
    masks = {}
    for i in ids:
        p = plans[i]
        for (k, df, dt) in acts[i]:
            if k == "revoke":
                continue
            masks[(i, k, df, dt)] = mask_of(p, df, dt)
    return ids, acts, masks


def act_cost(cls, act):
    """内部打分用的词典序四级贡献（撤销=rev+1,ploss+2w；调整=adj+1,ploss+w,mag+|δ|）。"""
    k = act[0]
    if k == "revoke":
        return (1, 0, PRIO[cls] * 2, 0)
    if k == "keep":
        return (0, 0, 0, 0)
    return (0, 1, PRIO[cls], abs(act[1]) + abs(act[2]))


def objective_tuple(plans, actions):
    """复刻 evaluator.objective_tuple（仅供内部打分；最终结论一律用 canonical_evaluator）。"""
    rev = adj = ploss = mag = 0
    for pid, act in actions.items():
        c = plans[pid]["cls"]
        if act.get("revoke"):
            rev += 1
            ploss += PRIO[c] * 2
        else:
            ks = [k for k in ("df", "dt") if act.get(k)]
            if ks:
                adj += 1
                ploss += PRIO[c]
                mag += sum(abs(int(act[k])) for k in ks)
    return [rev, adj, ploss, mag]


def scalarize(t):
    """TOURNAMENT_PROTOCOL.objective_scalar_formula"""
    return 1e12 * t[0] + 1e8 * t[1] + 1e4 * t[2] + t[3]


# ---- 冲突谓词的解析式（成对 clause 生成用，不用掩码暴力） --------------------
def band_delta_range(pi, pj):
    """使频段半开区间交叠的 δf = dfi - dfj 的整数闭区间 [lo,hi]（可能为空）。
    推导：交叠 ⇔ f0i+dfi < f1j+dfj  ∧  f0j+dfj < f1i+dfi
         ⇔ δf <= f1j-f0i-1  ∧  δf >= f0j-f1i+1
    """
    lo = pj["f0"] - pi["f1"] + 1
    hi = pj["f1"] - pi["f0"] - 1
    if lo > hi:
        return None
    return (lo, hi)


def time_delta_overlap_set(pi, pj):
    """使存在某对占用窗半开交叠的 δt = dti - dtj 的整数集合（限定 |δt|<=10）。
    单对窗交叠 ⇔ c-di < δt < c+dj，c = (t0j+l*Pj) - (t0i+k*Pi)。
    """
    di, dj = pi["d"], pj["d"]
    Pi = pi["g"] + di
    Pj = pj["g"] + dj
    out = set()
    for k in range(pi["n"]):
        A = pi["t0"] + k * Pi
        for l in range(pj["n"]):
            B = pj["t0"] + l * Pj
            c = B - A
            lo = max(-10, c - di + 1)
            hi = min(10, c + dj - 1)
            for v in range(lo, hi + 1):
                out.add(v)
    return out


def build_star_edges(plans, acts, masks=None, verify=False):
    """全势冲突边 G*：对每对计划，枚举其动作邻域内所有可能同格共占的动作组合。
    返回 { (i,j): [ (ai_index, aj_index), ... ] }（索引对 = 该组合下仍冲突），
    以及每个计划的动作数统计。剪枝必须可证完备：先做包络预筛（频段包络 ∧ 时间包络），
    再对通过预筛的对做逐组合精确判定。
    """
    ids = sorted(plans)
    nact0 = {i: [a for a in acts[i] if a[0] != "revoke"] for i in ids}
    # 包络
    env_b = {}
    env_t = {}
    for i in ids:
        f0 = min(plans[i]["f0"] + a[1] for a in nact0[i])
        f1 = max(plans[i]["f1"] + a[1] for a in nact0[i])
        smin = min(plans[i]["t0"] + a[2] for a in nact0[i])
        smax = max(plans[i]["t0"] + a[2] + (plans[i]["n"] - 1) * (plans[i]["g"] + plans[i]["d"])
                   + plans[i]["d"] for a in nact0[i])
        env_b[i] = (f0, f1)
        env_t[i] = (smin, smax)
    idx_of = {i: {a: x for x, a in enumerate(acts[i])} for i in ids}
    edges = {}
    checked = 0
    for x in range(len(ids)):
        i = ids[x]
        bi0, bi1 = env_b[i]
        ti0, ti1 = env_t[i]
        di = plans[i]["d"]
        for y in range(x + 1, len(ids)):
            j = ids[y]
            bj0, bj1 = env_b[j]
            if not (max(bi0, bj0) < min(bi1, bj1)):
                continue
            tj0, tj1 = env_t[j]
            if not (max(ti0, tj0) < min(ti1, tj1)):
                continue
            checked += 1
            br = band_delta_range(plans[i], plans[j])
            if br is None:
                continue
            tset = time_delta_overlap_set(plans[i], plans[j])
            if not tset:
                continue
            lo_f, hi_f = br
            combos = []
            for ai, a in enumerate(nact0[i]):
                dfa, dta = a[1], a[2]
                for b_idx, b in enumerate(nact0[j]):
                    d = dfa - b[1]
                    if d < lo_f or d > hi_f:
                        continue
                    if (dta - b[2]) in tset:
                        combos.append((idx_of[i][a], idx_of[j][b]))
            if combos:
                edges[(i, j)] = combos
    if verify:
        _verify_edges(plans, acts, masks, edges)
    return edges, {"pairs_envelope_checked": checked, "star_edges": len(edges),
                   "infeasible_combos": sum(len(v) for v in edges.values())}


def _verify_edges(plans, acts, masks, edges, sample=400, seed=12345):
    """随机抽样用掩码暴力复核解析式（哨兵：解析式 vs 掩码必须逐位一致）。"""
    import random
    ids = sorted(plans)
    rng = random.Random(seed)
    lookup = {(i, j): set(v) for (i, j), v in edges.items()}
    bad = 0
    for _ in range(sample):
        i, j = rng.choice(ids), rng.choice(ids)
        if i == j:
            continue
        if i > j:
            i, j = j, i
        key = (i, j)
        got = lookup.get(key, set())
        brute = set()
        A = [a for a in acts[i] if a[0] != "revoke"]
        B = [a for a in acts[j] if a[0] != "revoke"]
        idx_i = {a: x for x, a in enumerate(acts[i])}
        idx_j = {a: x for x, a in enumerate(acts[j])}
        for a in A:
            ma = masks[(i, a[0], a[1], a[2])]
            for b in B:
                mb = masks[(j, b[0], b[1], b[2])]
                if not ma.isdisjoint(mb):
                    brute.add((idx_i[a], idx_j[b]))
        if got != brute:
            bad += 1
    assert bad == 0, "解析式与掩码复核不一致: %d 例" % bad
    return True


def solution_from_choice(plans, acts, choice):
    """choice: {pid: action_index}；输出 canonical_evaluator 可吃的 actions json（只列被改/撤销者）"""
    sol = {}
    for pid, ai in choice.items():
        k, df, dt = acts[pid][ai]
        if k == "keep":
            continue
        if k == "revoke":
            sol[pid] = {"revoke": True}
        elif k == "df":
            sol[pid] = {"df": int(df)}
        elif k == "dt":
            sol[pid] = {"dt": int(dt)}
    return sol


def residual_pairs(plans, acts, masks, choice):
    """给定选择，返回残留冲突对（掩码法，与 evaluator 同语义）。"""
    ms = {}
    for i in sorted(acts):
        a = acts[i][choice[i]]
        if a[0] == "revoke":
            continue
        ms[i] = masks[(i, a[0], a[1], a[2])]
    out = []
    ks = sorted(ms)
    for x in range(len(ks)):
        for y in range(x + 1, len(ks)):
            if not ms[ks[x]].isdisjoint(ms[ks[y]]):
                out.append((ks[x], ks[y]))
    return out


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    plans = load_plans()
    ids, acts, masks = build_action_tables(plans)
    global_masks = masks
    nclass = {}
    for i in ids:
        nclass[plans[i]["cls"]] = nclass.get(plans[i]["cls"], 0) + 1
    na = [len(acts[i]) for i in ids]
    # 原始冲突对（掩码法）
    base = [(i, j) for x, i in enumerate(ids) for j in ids[x + 1:]
            if not masks[(i, "keep", 0, 0)].isdisjoint(masks[(j, "keep", 0, 0)])]
    edges, stats = build_star_edges(plans, acts, masks, verify=True)
    print("csv:", csv_path())
    print("class counts:", nclass)
    print("|A_i| min/max/sum:", min(na), max(na), sum(na))
    print("identity_ok_all:", all(acts[i][0][0] == "keep" for i in ids))
    print("base conflicts:", len(base))
    print("star stats:", stats)
    deg = {}
    for (i, j) in edges:
        deg[i] = deg.get(i, 0) + 1
        deg[j] = deg.get(j, 0) + 1
    print("G* nodes:", len(deg), "maxdeg:", max(deg.values()))
    import collections
    cc = collections.Counter(len(v) for v in edges.values())
    print("combo-count histogram(top10):", cc.most_common(10))
    full = sum(1 for (i, j), v in edges.items()
               if len(v) == len([a for a in acts[i] if a[0] != 'revoke']) * len([a for a in acts[j] if a[0] != 'revoke']))
    print("pairs where ALL non-revoke combos conflict:", full)
