# -*- coding: utf-8 -*-
"""Q3 组共享模块（Prototype Engineer, CS-20260911T071520-D2026 / Q3）
- base 占用栅格：对 Q2-R51 冻结方案应用 actions（6 个撤销资源释放=ADJ R8、df/dt 平移），
  占用位图逐字节复用 canonical_evaluator.mask_of / load_plans（只读 import，保证与 evaluator 完全一致）。
- 候选放置 p=(f0,t0)：新C模板固定 宽3/时长2/间隔8/次数12 ⇒ 占用窗 [t0+10k, t0+10k+2), k=0..11；
  f0∈0..97；末窗 t0+110+2 ≤ 643 ⇒ t0∈0..531。
- 与 evaluator 同资源常数：T_MAX=643, B_MAX=100（ADJ R1 / pending P1）。
"""
import importlib.util
import io
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
SCOUT_DIR = os.path.dirname(HERE)                          # .../scouts/Q3-Rxx
SCOUTS = os.path.dirname(SCOUT_DIR)                        # .../scouts
CS_DIR = os.path.dirname(SCOUTS)                           # .../CS-20260911T071520-D2026

# C 类模板常量（与 evaluator.eval_q3 内部写死的 w,d,g,n 一致）
W, D, G, N = 3, 2, 8, 12
PERIOD = G + D                 # 10
SPAN = (N - 1) * PERIOD + D    # 112


def _load_evaluator():
    path = os.path.join(CS_DIR, "canonical_evaluator.py")
    spec = importlib.util.spec_from_file_location("canonical_evaluator", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


EV = _load_evaluator()
T_MAX, B_MAX = EV.T_MAX, EV.B_MAX          # 643, 100（冻结）
T0_MAX = T_MAX - SPAN                      # 531
assert T0_MAX == 531, T0_MAX

Q2_ACTIONS_PATH = os.path.join(SCOUTS, "Q2-R51", "solution_actions.json")


def build_base():
    """返回 dict：plans/actions/occ(每频段列 int 位图)/used/distinct/n_kept/n_revoked。"""
    plans = EV.load_plans()
    actions = json.load(io.open(Q2_ACTIONS_PATH, encoding="utf-8"))
    occ = [0] * B_MAX
    used_total = 0
    n_kept = n_revoke = 0
    for pid in sorted(plans):
        p = plans[pid]
        a = actions.get(pid) or {}
        if a.get("revoke"):
            n_revoke += 1                    # ADJ R8：撤销计划资源释放
            continue
        m = EV.mask_of(p, df=int(a.get("df", 0)), dt=int(a.get("dt", 0)))
        if m is None:
            raise AssertionError(f"base plan out of resource: {pid}")
        n_kept += 1
        used_total += len(m)
        for c in m:
            t, f = divmod(c, 100)
            occ[f] |= 1 << t
    distinct = sum(x.bit_count() for x in occ)
    # 自检：Q2 冻结方案零冲突 ⇒ 重数=distinct（ADJ R2 口径分离）；evaluator 已复验 feasible=true
    assert distinct == used_total, f"base overlap: distinct={distinct} used={used_total}"
    return {"plans": plans, "actions": actions, "occ": occ,
            "used": used_total, "distinct": distinct,
            "n_kept": n_kept, "n_revoked": n_revoke}


def make_tmask_table():
    """tmask[t0] = 新C图案时间占用位（每窗 2 格 × 12 窗），t0∈0..531。"""
    tm = []
    for t0 in range(T0_MAX + 1):
        m = 0
        for k in range(N):
            m |= 0b11 << (t0 + k * PERIOD)
        tm.append(m)
    return tm


def gen_candidates(occ, tm):
    """全条带预筛：与 base 零冲突的 (f0,t0)。返回 (cands, cands_by_f0)。"""
    cands = []
    by_f0 = {}
    for f0 in range(B_MAX - W + 1):
        o3 = occ[f0] | occ[f0 + 1] | occ[f0 + 2]
        lst = []
        for t0 in range(T0_MAX + 1):
            if tm[t0] & o3 == 0:
                cands.append((f0, t0))
                lst.append(t0)
        by_f0[f0] = lst
    return cands, by_f0


def analytic_conflict(p, q):
    """两个新C放置冲突的解析判据（与位图占用语义等价，见 verify_analytic_vs_bitmap）。
    频轴：|Δf0| ≤ 2；时轴：|Δt0| ≤ 111 且 Δt0 mod 10 ∈ {0,1,9}（相位差 ±1/0）。"""
    if abs(p[0] - q[0]) >= W:
        return False
    dt = p[1] - q[1]
    if abs(dt) > SPAN - 1:
        return False
    return dt % PERIOD in (0, 1, PERIOD - 1)


def cells_of(f0, t0):
    """候选占用的 72 个单元 (t,f)。"""
    out = []
    b = f0 * 100
    for k in range(N):
        s = t0 + k * PERIOD
        for f in range(f0, f0 + W):
            for t in range(s, s + D):
                out.append(t * 100 + f)
    return out


def verify_analytic_vs_bitmap(tm, sample_pairs):
    """解析判据 vs 位图占用交集：抽样断言逐对一致。"""
    bad = 0
    for (p, q) in sample_pairs:
        mp = tm[p[1]]
        mq = tm[q[1]]
        band_ov = abs(p[0] - q[0]) < W
        bitmap_conflict = band_ov and (mp & mq) != 0
        if bitmap_conflict != analytic_conflict(p, q):
            bad += 1
    return bad


def verify_solution(sol, occ, tm):
    """外部复验：sol 与 base 零冲突 且 内部零冲突（与 evaluator 判据同位图逻辑）。"""
    colbits = [0] * B_MAX
    cover = [0] * B_MAX
    for (f0, t0) in sol:
        assert 0 <= f0 <= B_MAX - W and 0 <= t0 <= T0_MAX, (f0, t0)
        b = tm[t0]
        for f in range(f0, f0 + W):
            if b & occ[f]:
                return False, f"base_conflict:{f0},{t0}@col{f}"
            if colbits[f] & b:
                return False, f"internal_conflict:{f0},{t0}@col{f}"
            colbits[f] |= b
            cover[f] += 1
    return True, "ok"


def greedy_scan(occ, tm, by_f0, fixed=(), order=None):
    """全条带扫描贪心：按 f0 分组、t0 递增，可放置即放置。fixed 先行提交。
    order=None → f0 升序（规范贪心）；否则按给定条带序列扫描（LNS 重填多样化用）。"""
    cur = list(occ)
    placed = []
    for (f0, t0) in fixed:
        b = tm[t0]
        cur[f0] |= b
        cur[f0 + 1] |= b
        cur[f0 + 2] |= b
        placed.append((f0, t0))
    if order is None:
        order = sorted(by_f0)
    for f0 in order:
        for t0 in by_f0[f0]:
            b = tm[t0]
            if (b & cur[f0]) == 0 and (b & cur[f0 + 1]) == 0 and (b & cur[f0 + 2]) == 0:
                cur[f0] |= b
                cur[f0 + 1] |= b
                cur[f0 + 2] |= b
                placed.append((f0, t0))
    return placed


def eval_with_canonical(sol, sol_path=None):
    """逐字调用冻结 evaluator 的 eval_q3（同码；CLI 亦由脚本另行调用一次）。"""
    plans = EV.load_plans()
    base = json.load(io.open(Q2_ACTIONS_PATH, encoding="utf-8"))
    if sol_path is not None:
        sol = json.load(io.open(sol_path, encoding="utf-8"))
        sol = [(int(a), int(b)) for a, b in sol]
    r = EV.eval_q3(plans, [list(x) for x in sol], base)
    return r
