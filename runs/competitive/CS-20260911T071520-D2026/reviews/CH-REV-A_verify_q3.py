# -*- coding: utf-8 -*-
"""CH-REV-A 独立复核 Q3 三候选（只读被审工件，报告写 reviews/）。

腿a: 用我自己的实现（数据源=common_input.compact；不 import evaluator/common_q3）
     重算 base(Q2-R51) 占用 → 全枚举 f0∈0..97 × t0∈0..531 与 base 零冲突的候选放置集合，
     核对 2123 与内部数字（覆盖格 14969?、singleton?、rows=13822、nnz=151709、edges=62071、
     n_checked=131254、解析判据全量对拍）。
腿b: CP-SAT 模型 B（逐格容量）以我的候选集独立重建 → 复核 OPTIMAL=139 + bound=139；
     冻结 evaluator 原样复跑（stdout）核对三个 eval_q3.json。
腿c: scipy HiGHS LP（我的行集）→ 复现 lp_bound=139.0；核对 lp_crosscheck_hiGHS.json 内部一致性。
界复核: 相位×块双计数 tot=997 → UB=332、密度界=676；phantom-block 变异（剔除越界块）重算；
        /3 论证实证：用 R11 的 139 解验证每个 (b,r) 的块区间两两不交且 count(b,r) ≤ C(b,r)。
其余: R23 贪心 133 独立复现；解文件成员资格/内部零冲突；621 口径扫描。
"""
import hashlib
import io
import json
import os
import re
import subprocess
import sys
import time
from collections import defaultdict

ROOT = r"F:\2026 数模\D题重跑\D题\runs\competitive\CS-20260911T071520-D2026"
WS = os.path.abspath(os.path.join(ROOT, "..", "..", ".."))
T_MAX, B_MAX = 643, 100            # ADJ R1（独立硬编码，不 import evaluator）
W, D, G, N = 3, 2, 8, 12           # ADJ R5 / F-013/F-018
PERIOD = G + D                      # 10
SPAN = (N - 1) * PERIOD + D         # 112
F0_MAX, T0_MAX = B_MAX - W, T_MAX - SPAN   # 97, 531
OUT = []


def log(s=""):
    OUT.append(str(s))


def J(x):
    return json.dumps(x, ensure_ascii=False, sort_keys=True)


# ---------- 数据 ----------
ci = json.loads(io.open(os.path.join(ROOT, "common_input.json"), encoding="utf-8").read())
plans = {}
for r in ci["plans_table_compact"]:
    pid = r[0]
    plans[pid] = dict(id=pid, cls=pid[0], f0=r[1], f1=r[2], t0=r[3], t1=r[4], g=r[5], n=r[6],
                      d=r[4] - r[3])
assert len(plans) == 150
sol_q2 = json.loads(io.open(os.path.join(ROOT, "scouts", "Q2-R51", "solution_actions.json"),
                            encoding="utf-8").read())


def slots(p, dt=0):
    P = p["g"] + p["d"]
    return [(p["t0"] + dt + k * P, p["t0"] + dt + k * P + p["d"]) for k in range(p["n"])]


occ = [0] * B_MAX
n_kept = n_revoke = 0
incidence = 0
for pid in sorted(plans):
    a = sol_q2.get(pid) or {}
    if a.get("revoke"):
        n_revoke += 1
        continue
    p = plans[pid]
    df, dt = int(a.get("df", 0)), int(a.get("dt", 0))
    f0, f1 = p["f0"] + df, p["f1"] + df
    assert 0 <= f0 and f1 <= B_MAX and f0 < f1
    n_kept += 1
    incidence += p["n"] * p["d"] * (f1 - f0)
    for (s, e) in slots(p, dt):
        for t in range(s, e):
            for f in range(f0, f1):
                occ[f] |= 1 << t
distinct = sum(x.bit_count() for x in occ)
log("base(Q2-R51): kept=%d revoked=%d incidence=%d distinct=%d equal=%s free_cells=%d"
    % (n_kept, n_revoke, incidence, distinct, incidence == distinct, B_MAX * T_MAX - distinct))

# ---------- 腿a：候选放置全枚举（我的位运算实现） ----------
t0_ = time.time()
TM = []
for t0 in range(T0_MAX + 1):
    m = 0
    for k in range(N):
        m |= 0b11 << (t0 + k * PERIOD)
    TM.append(m)

cands = []
by_f0 = {}
for f0 in range(F0_MAX + 1):
    o3 = occ[f0] | occ[f0 + 1] | occ[f0 + 2]
    lst = []
    for t0 in range(T0_MAX + 1):
        if (TM[t0] & o3) == 0:
            cands.append((f0, t0))
            lst.append(t0)
    by_f0[f0] = lst
P = len(cands)
log("candidates: N=%d (claim 2123) match=%s  (%.2fs)" % (P, P == 2123, time.time() - t0_))
idx = {p: i for i, p in enumerate(cands)}

cell2c = defaultdict(list)
for i, (f0, t0) in enumerate(cands):
    for k in range(N):
        for t in range(t0 + k * PERIOD, t0 + k * PERIOD + D):
            for f in range(f0, f0 + W):
                cell2c[t * B_MAX + f].append(i)
covered = len(cell2c)
cov_cells_sum = sum(len(v) for v in cell2c.values())
singletons = sum(1 for v in cell2c.values() if len(v) == 1)
rows_ge2 = sum(1 for v in cell2c.values() if len(v) >= 2)
nnz_ge2 = sum(len(v) for v in cell2c.values() if len(v) >= 2)
log("coverage: distinct_cells=%d sum_cells=%d (=72*%d=%d) singleton_cells=%d rows>=2=%d nnz_rows>=2=%d"
    % (covered, cov_cells_sum, P, 72 * P, singletons, rows_ge2, nnz_ge2))
log("  vs lp_crosscheck_hiGHS.json claims: rows=13822 nnz=151709 vars=2123 -> match=%s"
    % (rows_ge2 == 13822 and nnz_ge2 == 151709 and P == 2123))

edges = set()
for cell, lst in cell2c.items():
    if len(lst) >= 2:
        for a in range(len(lst)):
            for b in range(a + 1, len(lst)):
                i, j = sorted((lst[a], lst[b]))
                edges.add((i, j))
log("edges (inverted-index): %d (claim 62071) match=%s" % (len(edges), len(edges) == 62071))


def analytic(p, q):
    if abs(p[0] - q[0]) >= W:
        return False
    dtv = p[1] - q[1]
    if abs(dtv) > SPAN - 1:
        return False
    return dtv % PERIOD in (0, 1, PERIOD - 1)


t0_ = time.time()
n_checked = 0
bad = 0
for f0 in range(F0_MAX + 1):
    L0 = by_f0[f0]
    if not L0:
        continue
    for f1 in range(f0, min(f0 + W, F0_MAX + 1)):
        L1 = by_f0[f1]
        if not L1:
            continue
        for t0x in L0:
            for t1x in L1:
                i, j = idx[(f0, t0x)], idx[(f1, t1x)]
                if i >= j:
                    continue
                if abs(t0x - t1x) > SPAN - 1:
                    continue
                n_checked += 1
                in_bitmap = (TM[t0x] & TM[t1x]) != 0
                if in_bitmap != analytic((f0, t0x), (f1, t1x)):
                    bad += 1
                if in_bitmap != ((i, j) in edges):
                    bad += 1
log("edge audit (full, band-dist<=2, |dt|<=111): checked=%d (claim 131254) mismatches=%d  (%.1fs)"
    % (n_checked, bad, time.time() - t0_))

# ---------- 腿b：CP-SAT 模型 B 独立重建 ----------
try:
    from ortools.sat.python import cp_model
    t0_ = time.time()
    m = cp_model.CpModel()
    x = [m.NewBoolVar("x%d" % i) for i in range(P)]
    for cell, lst in cell2c.items():
        if len(lst) >= 2:
            m.Add(sum(x[i] for i in lst) <= 1)
    m.Maximize(sum(x))
    s = cp_model.CpSolver()
    s.parameters.max_time_in_seconds = 240.0
    s.parameters.num_search_workers = 8
    s.parameters.random_seed = 7
    st = s.Solve(m)
    recB = {"status": s.StatusName(st), "value": int(round(s.ObjectiveValue())) if s.StatusName(st) in ("OPTIMAL", "FEASIBLE") else None,
            "best_bound": int(s.BestObjectiveBound()), "wall_s": round(time.time() - t0_, 1)}
    mineB = [cands[i] for i in range(P) if s.Value(x[i])]
    log("CP-SAT(B, seed=7, my build): %s incumbent=%d -> claim OPTIMAL=139 confirmed=%s"
        % (J(recB), len(mineB), recB["status"] == "OPTIMAL" and recB["value"] == 139 and recB["best_bound"] == 139))
except ImportError as e:
    log("ortools unavailable: %s" % e)

# ---------- 腿c：HiGHS LP 独立重跑 ----------
try:
    import numpy as np
    from scipy import sparse
    from scipy.optimize import linprog
    rows_l, cols_l = [], []
    r = 0
    for cell, lst in cell2c.items():
        if len(lst) >= 2:
            for i in lst:
                rows_l.append(r)
                cols_l.append(i)
            r += 1
    A = sparse.csr_matrix((np.ones(len(rows_l)), (rows_l, cols_l)), shape=(r, P))
    t0_ = time.time()
    res = linprog(c=-np.ones(P), A_ub=A, b_ub=np.ones(r),
                  bounds=[(0, 1)] * P, method="highs")
    v = -res.fun
    log("HiGHS LP (my build): status=%s bound=%.6f floor=%d confirms_no_140=%s  (%.1fs)"
        % (res.status, v, int(np.floor(v + 1e-9)), v < 140, time.time() - t0_))
except Exception as e:
    log("LP re-run failed: %r" % e)

# ---------- 三候选解的独立复验 ----------
def check_sol(sol):
    s = set(map(tuple, sol))
    ok_sub = s <= set(cands)
    cols = [0] * B_MAX
    internal = 0
    for (f0, t0) in s:
        b = TM[t0]
        for f in range(f0, f0 + W):
            if cols[f] & b:
                internal += 1
            cols[f] |= b
    return ok_sub, internal, len(s)


for idea in ("Q3-R11", "Q3-R23", "Q3-R51"):
    p = os.path.join(ROOT, "scouts", idea, "solution_newc.json")
    sol = json.loads(io.open(p, encoding="utf-8").read())
    ok_sub, internal, n = check_sol(sol)
    sha = hashlib.sha256(io.open(p, "rb").read()).hexdigest()
    ev = json.loads(io.open(os.path.join(ROOT, "scouts", idea, "eval_q3.json"), encoding="utf-8").read())
    log("%s sol: n=%d unique=%d subset_of_my_cands=%s internal_cell_reuse_violations=%d sha=%s eval_obj=%s"
        % (idea, len(sol), n, ok_sub, internal, sha[:16] + "...", J(ev["objective"])))

# ---------- evaluator 原样复跑（stdout） ----------
for idea in ("Q3-R11", "Q3-R23", "Q3-R51"):
    cp = subprocess.run([sys.executable, os.path.join(ROOT, "canonical_evaluator.py"),
                         "--question", "Q3",
                         "--solution", os.path.join(ROOT, "scouts", idea, "solution_newc.json"),
                         "--base-actions", os.path.join(ROOT, "scouts", "Q2-R51", "solution_actions.json")],
                        capture_output=True, text=True, encoding="utf-8")
    try:
        o = json.loads(cp.stdout)
        log("evaluator re-run %s: feasible=%s objective=%s n_viol=%s" %
            (idea, o["feasible"], J(o["objective"]), o["n_violations"]))
    except Exception:
        log("evaluator re-run %s: FAIL rc=%s %s" % (idea, cp.returncode, cp.stdout[:150]))

# ---------- R51 相位×块界独立重算（含 phantom 变异） ----------
tot = 0
tot_noph = 0
detail = {}
for b in range(B_MAX):
    for rr in range(PERIOD):
        Jm = (T_MAX - 1 - rr) // PERIOD
        cur = run = 0
        curn = 0
        for j in range(Jm + 1):
            free = (occ[b] & (0b11 << (PERIOD * j + rr))) == 0
            if free:
                run += 1
            else:
                cur += run // N
                run = 0
            # no-phantom variant: block must fit fully in [0,643)
            if 10 * j + rr + 1 <= T_MAX - 1:
                pass
            else:
                curn = 1  # phantom block flag
        cur += run // N
        tot += cur
        detail["%d,%d" % (b, rr)] = cur
# phantom-only recount: exclude blocks j with 10j+r+1 > 642
for b in range(B_MAX):
    for rr in range(PERIOD):
        pass  # integrated below instead
# second pass, clean: only blocks fully inside horizon
tot_np = 0
maxj = {}
for b in range(B_MAX):
    for rr in range(PERIOD):
        Jm2 = (T_MAX - 2 - rr) // PERIOD  # block cells (10j+r, 10j+r+1) both ≤ 642
        run = cur = 0
        for j in range(Jm2 + 1):
            free = (occ[b] & (0b11 << (PERIOD * j + rr))) == 0
            if free:
                run += 1
            else:
                cur += run // N
                run = 0
        cur += run // N
        tot_np += cur
ub_pb = tot // 3
ub_pb_np = tot_np // 3
free_cells = B_MAX * T_MAX - distinct
ub_dens = free_cells // (W * D * N)
log("phase-block bound: my tot=%d (claim 997) UB_pb=floor(tot/3)=%d (claim 332) | no-phantom tot=%d UB=%d"
    % (tot, ub_pb, tot_np, ub_pb_np))
log("density bound: free=%d (claim 48700) UB_dens=%d (claim 676) ; min=%d (claim 332)"
    % (free_cells, ub_dens, min(ub_pb, ub_dens)))

# /3 论证实证：R11 的 139 解，每个 (b,r)：放置的块区间两两不交且 count ≤ C(b,r)
sol11 = set(map(tuple, json.loads(io.open(os.path.join(ROOT, "scouts", "Q3-R11", "solution_newc.json"),
                                          encoding="utf-8").read())))
cnt_br = defaultdict(list)
for (f0, t0) in sol11:
    r = t0 % PERIOD
    j0 = (t0 - r) // PERIOD
    for f in range(f0, f0 + W):
        cnt_br[(f, r)].append((j0, j0 + N - 1))
viol_disjoint = 0
viol_cap = 0
tot_count = 0
for (b, r), ivs in cnt_br.items():
    ivs.sort()
    for a, bb in zip(ivs, ivs[1:]):
        if bb[0] <= a[1]:
            viol_disjoint += 1
    tot_count += len(ivs)
    if len(ivs) > detail.get("%d,%d" % (b, r), 0):
        viol_cap += 1
log("/3 audit on R11 solution: Σ count(b,r)=%d (=3*139=%s) ; overlapping-interval violations=%d ; cap violations C(b,r)=%d"
    % (tot_count, 3 * 139, viol_disjoint, viol_cap))

# ---------- R23 贪心独立复现 ----------
cur_occ = list(occ)
placed = 0
for f0 in sorted(by_f0):
    for t0 in by_f0[f0]:
        b = TM[t0]
        if (b & cur_occ[f0]) == 0 and (b & cur_occ[f0 + 1]) == 0 and (b & cur_occ[f0 + 2]) == 0:
            cur_occ[f0] |= b
            cur_occ[f0 + 1] |= b
            cur_occ[f0 + 2] |= b
            placed += 1
log("greedy (f0 asc, t0 asc) independent recount = %d (claim 133)" % placed)

# ---------- 621 / 16680 / 15600 口径扫描 ----------
log("\nunit-basis scan Q3 artifacts:")
pat = re.compile(r"621|643|531|509|15600|48700|332")
for idea in ("Q3-R11", "Q3-R23", "Q3-R51"):
    d = os.path.join(ROOT, "scouts", idea)
    hits = {}
    for fn in os.listdir(d):
        if fn.endswith((".json", ".md", ".py", ".txt")):
            try:
                txt = io.open(os.path.join(d, fn), encoding="utf-8").read()
            except Exception:
                continue
            for mm in set(pat.findall(txt)):
                hits.setdefault(mm, []).append(fn)
    log("%s: %s" % (idea, J({k: sorted(v)[:8] for k, v in hits.items()})))

io.open(os.path.join(ROOT, "reviews", "CH-REV-A_verify_q3_report.txt"), "w",
        encoding="utf-8").write("\n".join(OUT))
print("\n".join(OUT))
