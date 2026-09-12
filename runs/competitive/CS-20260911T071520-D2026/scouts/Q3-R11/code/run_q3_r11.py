# -*- coding: utf-8 -*-
"""Q3-R11（集包装精确, CH-01）：预筛候选 → 干扰边（位图倒排）→ CP-SAT max Σx。
- 主模型 A：计划对冲突子句 x_i+x_j≤1（边由候选-单元倒排索引生成，并与解析判据穷举对拍）。
- 对照模型 B：逐时间-频格累计容量 Σ_{p∋cell} x_p ≤ 1。
  等价性：两模型的整数可行集相同（"无两放置共享单元" ⟺ "每条干扰边两端不同时选"）；
  LP 松弛不同（B 的每格行强制同格任意对 ⇒ B 多面体 ⊆ A 多面体，B 的分数界不劣于 A）。
  差异写入 scout.json（任务要求）。边数 ~6.2e4 未爆炸 ⇒ A 为主模型（协议），B 限时对照。
- 600s 报告 incumbent + bound（协议冻结；本脚本内预算：A 340s，B 170s，余量留给构建/复验）。
"""
import bisect
import json
import os
import random
import subprocess
import sys
import time
from collections import defaultdict

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common_q3 as C

from ortools.sat.python import cp_model

T_START = time.time()
BUDGET_A = 340.0
BUDGET_B = 170.0
NUM_WORKERS = 8
CP_SAT_SEED = 0

base = C.build_base()
tm = C.make_tmask_table()
cands, by_f0 = C.gen_candidates(base["occ"], tm)
P = len(cands)
idx = {p: i for i, p in enumerate(cands)}

# ---------- 边集：倒排索引（cell → candidates） ----------
cell2c = defaultdict(list)
for i, (f0, t0) in enumerate(cands):
    for cell in C.cells_of(f0, t0):
        cell2c[cell].append(i)
edges = set()
for cell, lst in cell2c.items():
    m = len(lst)
    if m >= 2:
        for a in range(m):
            for b in range(a + 1, m):
                i, j = lst[a], lst[b]
                edges.add((i, j) if i < j else (j, i))
n_edges = len(edges)

# ---------- 边集：解析判据穷举对拍（|Δf0|≤2 的全部候选对） ----------
rng = random.Random(13)
bad = 0
n_checked = 0
strip_ts = {f: by_f0[f] for f in by_f0}
for f0 in range(C.B_MAX - C.W + 1):
    L0 = strip_ts.get(f0, [])
    if not L0:
        continue
    for f1 in range(f0, min(f0 + C.W, C.B_MAX - C.W + 1)):
        L1 = strip_ts.get(f1, [])
        if not L1:
            continue
        for t0 in L0:
            lo = bisect.bisect_left(L1, t0 - (C.SPAN - 1))
            hi = bisect.bisect_right(L1, t0 + (C.SPAN - 1))
            for t1 in L1[lo:hi]:
                p, q = (f0, t0), (f1, t1)
                i, j = idx[p], idx[q]
                if i >= j:
                    continue
                n_checked += 1
                in_analytic = C.analytic_conflict(p, q)
                in_bitmap = (tm[t0] & tm[t1]) != 0   # 同带窗重叠已保证 |Δf0|≤2
                if in_analytic != in_bitmap:
                    bad += 1
                if in_bitmap != ((i, j) in edges):
                    bad += 1
assert bad == 0, f"analytic/bitmap/inverted edge mismatch: {bad}"
edges = sorted(edges)

# ---------- 模型求解器函数 ----------

def solve(var_rows, tag, budget_s, hints):
    model = cp_model.CpModel()
    x = [model.NewBoolVar(f"x{i}") for i in range(P)]
    if var_rows == "pair":
        for (i, j) in edges:
            model.Add(x[i] + x[j] <= 1)
    else:
        for cell, lst in cell2c.items():
            if len(lst) >= 2:
                model.Add(sum(x[i] for i in lst) <= 1)
    model.Maximize(sum(x))
    for p in hints:
        if p in idx:
            model.AddHint(x[idx[p]], 1)
    s = cp_model.CpSolver()
    s.parameters.max_time_in_seconds = budget_s
    s.parameters.num_search_workers = NUM_WORKERS
    s.parameters.random_seed = CP_SAT_SEED
    t0 = time.time()
    st = s.Solve(model)
    st_name = s.StatusName(st)
    has_sol = st_name in ("OPTIMAL", "FEASIBLE")
    rec = {
        "model": tag, "status": st_name,
        "wall_s": round(time.time() - t0, 1),
        "n_vars": P,
        "n_constraints": n_edges if var_rows == "pair" else sum(1 for l in cell2c.values() if len(l) >= 2),
        "has_incumbent": has_sol,
        "num_conflicts": int(s.NumConflicts()),
        "num_branches": int(s.NumBranches()),
        "cp_wall_s": round(s.WallTime(), 1),
    }
    sol = None
    if has_sol:
        rec["incumbent"] = int(round(s.ObjectiveValue()))
        sol = [cands[i] for i in range(P) if s.Value(x[i])]
        sol.sort()
    if st_name != "MODEL_INVALID":
        rec["best_bound"] = int(s.BestObjectiveBound())
    return rec, sol


r23_hint_path = os.path.join(C.SCOUTS, "Q3-R23", "solution_newc.json")
hints = [tuple(map(int, v)) for v in json.load(open(r23_hint_path, encoding="utf-8"))] if os.path.isfile(r23_hint_path) else []

# 主模型 A：pairwise 子句
recA, solA = solve("pair", "A_pairwise_clauses", BUDGET_A, hints)
# 对照模型 B：逐格容量
recB, solB = solve("cell", "B_cell_capacity", BUDGET_B, hints)

best_sol, best_rec = (solA, recA)
if solB is not None and (best_sol is None or len(solB) > len(best_sol)):
    best_sol, best_rec = (solB, recB)

assert best_sol is not None, "no incumbent from either model"
ok, msg = C.verify_solution(best_sol, base["occ"], tm)
assert ok, f"incumbent verify failed: {msg}"

sol_path = os.path.join(C.SCOUT_DIR, "solution_newc.json")
json.dump([[f, t] for f, t in best_sol], open(sol_path, "w", encoding="utf-8"))
eval_out = os.path.join(C.SCOUT_DIR, "eval_q3.json")
cmd = [sys.executable, os.path.join(C.CS_DIR, "canonical_evaluator.py"),
       "--question", "Q3", "--solution", sol_path,
       "--base-actions", C.Q2_ACTIONS_PATH, "--out", eval_out]
r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
ev = json.load(open(eval_out, encoding="utf-8"))

report = {
    "idea_id": "Q3-R11", "question_id": "Q3",
    "n_candidates_base_free": P, "n_edges": n_edges,
    "edge_equivalence_audit": {"pairs_with_band_overlap_checked": n_checked,
                                "analytic_vs_bitmap_vs_inverted_mismatches": bad},
    "model_A": recA, "model_B": recB,
    "incumbent_used": best_rec["model"],
    "final_count": len(best_sol),
    "external_verify": {"ok": ok, "msg": msg},
    "evaluator": {"feasible": ev["feasible"], "objective": ev["objective"],
                  "n_violations": ev["n_violations"]},
    "hint_from": r23_hint_path if hints else None,
    "solver_params": {"random_seed": CP_SAT_SEED, "num_search_workers": NUM_WORKERS,
                       "budget_A_s": BUDGET_A, "budget_B_s": BUDGET_B},
    "equivalence_note": ("整数可行集：A（干扰边 x_i+x_j≤1）≡ B（每格 Σx≤1），"
                          "因两者都精确表达『无两放置共享时频单元』；LP 松弛：B 的多面体 ⊆ A"
                          "（同格任意对被 B 的格行强制），故 B 的 CP-SAT best_bound ≥ A（界更紧）；"
                          "边数=6.2e4 未爆炸 ⇒ 按协议以 A 为主模型，B 为对照。"),
    "runtime_seconds_total": round(time.time() - T_START, 1),
    "protocol_wall_limit_s": 600, "replicates": 1,
}
json.dump(report, open(os.path.join(C.SCOUT_DIR, "cpsat_r11_report.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print(json.dumps(report, ensure_ascii=False))
