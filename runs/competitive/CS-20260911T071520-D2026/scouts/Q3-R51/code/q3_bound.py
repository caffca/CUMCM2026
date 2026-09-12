# -*- coding: utf-8 -*-
"""Q3-R51（界路线, CH-05）：相位×连续块双计数上界 + 密度界对照 + 构造下界（复用 Q3-R23 结果，任务明示）。

上界推导（初等、全整数、可手核）：
  固定频段列 b 与相位 r = t0 mod 10。把该列时间轴按 (10j+r, 10j+r+1) 分块，j=0..J(r)，
  J(r)=(T_MAX-1-r)//10（块完全落于 [0,643)）。任一放置 p=(f0,t0)（相位 r、覆盖列 b）在列 b
  上占用 12 个连续块 [j0, j0+11]，j0=(t0-r)/10，且要求这 12 块对 base 全自由。
  同一 (b,r) 下被选中的若干放置互不冲突 ⇒ 其块区间两两不重叠（同相位时 |Δt0|≤111 即块区间
  相交 ⇔ 单元相交；不冲突 ⇒ 块区间不交），故对 base 自由块极长连续段 run_s 有
  count(b,r) ≤ Σ_s ⌊run_s/12⌋ =: C(b,r)。
  双计数：每个被选放置恰好为 3 个 (b,r) 对贡献 1（其相位 r 与其覆盖的 3 列），
  故 3N = Σ_b Σ_r count(b,r) ≤ Σ_b Σ_r C(b,r) ⇒ UB_pb = ⌊ΣΣ C / 3⌋。
  密度界（独立对照）：UB_dens = ⌊(100·643 − base distinct 占用)/72⌋（每放置耗 3×24=72 格）。
  报告 UB = min(UB_pb, UB_dens)（两者皆合法 ⇒ 逐点取小仍合法）。
强制自检门（CH-05 警示#3）：UB ≥ 已知可行解数（R23/R11 计数）；违反 ⇒ 界代码有 bug，如实写盘。
"""
import json
import os
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common_q3 as C

T_START = time.time()
base = C.build_base()
tm = C.make_tmask_table()

# ---- 构造下界：复用 Q3-R23 结果（任务明示；同工作区本组产物） ----
r23_sol_path = os.path.join(C.SCOUTS, "Q3-R23", "solution_newc.json")
sol = [tuple(map(int, x)) for x in json.load(open(r23_sol_path, encoding="utf-8"))]
ok, msg = C.verify_solution(sol, base["occ"], tm)
lb_count = len(sol) if ok else -1

# 本候选自己的 solution（=构造解）→ evaluator 复验
sol_path = os.path.join(C.SCOUT_DIR, "solution_newc.json")
json.dump([[f, t] for f, t in sorted(sol)], open(sol_path, "w", encoding="utf-8"))
eval_out = os.path.join(C.SCOUT_DIR, "eval_q3.json")
cmd = [sys.executable, os.path.join(C.CS_DIR, "canonical_evaluator.py"),
       "--question", "Q3", "--solution", sol_path,
       "--base-actions", C.Q2_ACTIONS_PATH, "--out", eval_out]
r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
ev = json.load(open(eval_out, encoding="utf-8"))
assert r.returncode == 0

# ---- 相位×块双计数上界 ----
occ = base["occ"]
detail = {}
tot = 0
for b in range(C.B_MAX):
    for rr in range(C.PERIOD):
        J = (C.T_MAX - 1 - rr) // C.PERIOD          # 块 j=0..J，块=(10j+r,10j+r+1)
        # 自由块位图
        runs = []
        cur = 0
        for j in range(J + 1):
            blk_free = (occ[b] & (0b11 << (C.PERIOD * j + rr))) == 0
            if blk_free:
                cur += 1
            else:
                if cur:
                    runs.append(cur)
                cur = 0
        if cur:
            runs.append(cur)
        cbr = sum(x // C.N for x in runs)           # Σ⌊run/12⌋
        tot += cbr
        detail[f"{b},{rr}"] = cbr
UB_pb = tot // 3

# ---- 密度界对照（ADJ R2：distinct 口径） ----
free_cells = C.B_MAX * C.T_MAX - base["distinct"]
UB_dens = free_cells // (C.W * C.D * C.N)           # /72

UB = min(UB_pb, UB_dens)

# ---- 强制自检门 ----
known = [lb_count]
known_detail = {"Q3-R23": lb_count}
r11_sol = os.path.join(C.SCOUTS, "Q3-R11", "solution_newc.json")
if os.path.isfile(r11_sol):
    s11 = [tuple(map(int, v)) for v in json.load(open(r11_sol, encoding="utf-8"))]
    ok11, _ = C.verify_solution(s11, base["occ"], tm)
    if ok11:
        known.append(len(s11))
        known_detail["Q3-R11"] = len(s11)
required_min = max(known)
gate_ok = (lb_count >= 0) and (UB >= required_min)
result = {
    "idea_id": "Q3-R51", "question_id": "Q3",
    "base": {"n_kept": base["n_kept"], "n_revoked": base["n_revoked"],
             "distinct_used": base["distinct"], "T_MAX": C.T_MAX, "B_MAX": C.B_MAX},
    "constructive_lb": {"source": "Q3-R23 solution (任务明示复用)", "count": lb_count,
                        "verified_zero_conflict": bool(ok), "verify_msg": msg,
                        "evaluator_feasible": ev["feasible"], "evaluator_objective": ev["objective"]},
    "ub_phase_block": UB_pb, "ub_sum_cells": tot,
    "ub_density": UB_dens, "free_cells": free_cells,
    "ub_reported": UB,
    "gate_ub_ge_lb": {"known_feasible_counts": known_detail, "required_min": required_min,
                      "passed": bool(gate_ok),
                      "note": "CH-05 警示#3：UB<已知可行解 ⇒ 界代码 bug"},
    "runtime_seconds": round(time.time() - T_START, 2),
}
json.dump(result, open(os.path.join(C.SCOUT_DIR, "bound_r51.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print(json.dumps({k: v for k, v in result.items() if k != "constructive_lb"}, ensure_ascii=False))
print("LB:", lb_count, "verify:", ok, "eval feasible:", ev["feasible"])
