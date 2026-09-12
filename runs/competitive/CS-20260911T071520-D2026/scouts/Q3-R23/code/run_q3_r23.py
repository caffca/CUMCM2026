# -*- coding: utf-8 -*-
"""Q3-R23（baseline, CH-02）：全条带扫描贪心 + 轻量 LNS 改进。
- 贪心：按 f0 分组、t0 递增，可放置即放置（位图占用判定，与 evaluator 同逻辑）。
- LNS：随机移除 k∈{5,10,20} 个已放置 → 重填（同扫描序）；严格改善接受；
  无改进轮数上限 或 LNS 预算（240s）耗尽即停。确定性：seed=11（协议 seed_set 首元），replicates=1。
- 输出：solution_newc.json（[[f0,t0],...]）→ canonical_evaluator CLI 复验 → run_report.json。
"""
import json
import os
import random
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common_q3 as C

SEED = 11
LNS_BUDGET_S = 240.0
NO_IMPROVE_STOP = 400000      # 预算（240s）主导停止；patience 仅防死循环
KS = (5, 10, 20, 40)          # 移除规模循环
T_START = time.time()

base = C.build_base()
tm = C.make_tmask_table()
cands, by_f0 = C.gen_candidates(base["occ"], tm)

# --- 贪心（确定性自检：跑两遍逐位一致） ---
g1 = C.greedy_scan(base["occ"], tm, by_f0)
g2 = C.greedy_scan(base["occ"], tm, by_f0)
assert g1 == g2, "greedy not deterministic"
greedy_count = len(g1)

# --- LNS ---
rng = random.Random(SEED)
cur = list(g1)
best = list(g1)
iters = accepted = 0
no_improve = 0
strips = sorted(f for f in by_f0 if by_f0[f])
while time.time() - T_START < LNS_BUDGET_S:
    k = KS[iters % len(KS)]
    iters += 1
    rem = set(rng.sample(range(len(cur)), min(k, len(cur))))
    keep = [p for i, p in enumerate(cur) if i not in rem]
    order = strips[:]
    rng.shuffle(order)                     # 重填条带序随机化（否则规范重填为吸收态）
    new = C.greedy_scan(base["occ"], tm, by_f0, fixed=keep, order=order)
    if len(new) > len(best):
        best = list(new)
        no_improve = 0
        cur = new
        accepted += 1
    elif len(new) == len(cur):
        cur = new                          # 中性移动接受：解随机漂移，助逃出同分谷
        no_improve += 1
    else:
        no_improve += 1
    if iters % 50000 == 0 and len(cur) < len(best):
        cur = list(best)                   # 周期性回锚 best
        if no_improve >= NO_IMPROVE_STOP:
            break
best.sort()
solve_elapsed = time.time() - T_START

ok, msg = C.verify_solution(best, base["occ"], tm)
assert ok, f"external verify failed: {msg}"

sol_path = os.path.join(C.SCOUT_DIR, "solution_newc.json")
json.dump([[f, t] for f, t in best], open(sol_path, "w", encoding="utf-8"))

# --- canonical evaluator CLI（冻结件逐字调用） ---
eval_out = os.path.join(C.SCOUT_DIR, "eval_q3.json")
cmd = [sys.executable, os.path.join(C.CS_DIR, "canonical_evaluator.py"),
       "--question", "Q3", "--solution", sol_path,
       "--base-actions", C.Q2_ACTIONS_PATH, "--out", eval_out]
r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
ev = json.load(open(eval_out, encoding="utf-8"))

report = {
    "idea_id": "Q3-R23", "question_id": "Q3",
    "base": {"n_kept": base["n_kept"], "n_revoked": base["n_revoked"],
             "distinct_used": base["distinct"], "mult_used": base["used"],
             "T_MAX": C.T_MAX, "B_MAX": C.B_MAX},
    "n_candidates_base_free": len(cands),
    "nonempty_strips": sum(1 for v in by_f0.values() if v),
    "greedy_count": greedy_count,
    "lns": {"seed": SEED, "iterations": iters, "accepted": accepted,
            "removal_sizes_k": list(KS), "refill": "同扫描贪心、条带访问序随机化",
            "no_improve_streak_at_stop": no_improve,
            "budget_s": LNS_BUDGET_S, "stopped_by": ("budget" if time.time() - T_START >= LNS_BUDGET_S else "no_improve")},
    "best_count": len(best),
    "external_verify": {"ok": ok, "msg": msg},
    "evaluator": {"feasible": ev["feasible"], "objective": ev["objective"],
                  "n_violations": ev["n_violations"]},
    "solve_wall_seconds": round(solve_elapsed, 2),
    "protocol_wall_limit_s": 600, "replicates": 1,
}
json.dump(report, open(os.path.join(C.SCOUT_DIR, "run_report.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print(json.dumps(report, ensure_ascii=False))
