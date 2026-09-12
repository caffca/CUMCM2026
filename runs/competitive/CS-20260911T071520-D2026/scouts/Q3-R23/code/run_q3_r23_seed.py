# -*- coding: utf-8 -*-
"""Q3-R23 重复实验 runner（评审闭环追加任务）：协议 seed_set=[11,29,47]，stochastic 候选 3 重复。
用法: python run_q3_r23_seed.py <seed>
与 seed=11 已跑流水线完全同参数（贪心构造 + LNS：KS=(5,10,20,40)、预算 240s、patience 400000、
条带访问序随机化重填、中性移动接受、周期回锚 best）。
输出（本目录）：solution_newc_seed{S}.json / eval_q3_seed{S}.json / run_report_seed{S}.json。
失败也写盘（status=failed + traceback 摘要），不删除任何记录。"""
import json
import os
import random
import subprocess
import sys
import time
import traceback

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import common_q3 as C

SEED = int(sys.argv[1])
assert SEED in (29, 47), "seed11 已有运行记录，本 runner 只补跑 29/47"
LNS_BUDGET_S = 240.0
NO_IMPROVE_STOP = 400000
KS = (5, 10, 20, 40)
T_START = time.time()

report_path = os.path.join(C.SCOUT_DIR, f"run_report_seed{SEED}.json")

try:
    base = C.build_base()
    tm = C.make_tmask_table()
    cands, by_f0 = C.gen_candidates(base["occ"], tm)

    g1 = C.greedy_scan(base["occ"], tm, by_f0)
    assert len(g1) == 133, f"greedy changed: {len(g1)}"

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
        rng.shuffle(order)
        new = C.greedy_scan(base["occ"], tm, by_f0, fixed=keep, order=order)
        if len(new) > len(best):
            best = list(new)
            no_improve = 0
            cur = new
            accepted += 1
        elif len(new) == len(cur):
            cur = new
            no_improve += 1
        else:
            no_improve += 1
        if iters % 50000 == 0 and len(cur) < len(best):
            cur = list(best)
    best.sort()
    solve_elapsed = time.time() - T_START

    ok, msg = C.verify_solution(best, base["occ"], tm)
    sol_path = os.path.join(C.SCOUT_DIR, f"solution_newc_seed{SEED}.json")
    json.dump([[f, t] for f, t in best], open(sol_path, "w", encoding="utf-8"))
    eval_out = os.path.join(C.SCOUT_DIR, f"eval_q3_seed{SEED}.json")
    cmd = [sys.executable, os.path.join(C.CS_DIR, "canonical_evaluator.py"),
           "--question", "Q3", "--solution", sol_path,
           "--base-actions", C.Q2_ACTIONS_PATH, "--out", eval_out]
    subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", check=True)
    ev = json.load(open(eval_out, encoding="utf-8"))

    report = {
        "idea_id": "Q3-R23", "question_id": "Q3", "status": "completed",
        "seed": SEED, "greedy_count": 133, "best_count": len(best),
        "external_verify": {"ok": bool(ok), "msg": msg},
        "evaluator": {"feasible": ev["feasible"], "objective": ev["objective"],
                      "n_violations": ev["n_violations"]},
        "lns": {"iterations": iters, "accepted": accepted,
                "no_improve_streak_at_stop": no_improve,
                "budget_s": LNS_BUDGET_S,
                "stopped_by": ("budget" if solve_elapsed >= LNS_BUDGET_S else "no_improve")},
        "solve_wall_seconds": round(solve_elapsed, 2),
        "solution_path": sol_path,
        "protocol_wall_limit_s": 600,
    }
    assert ok and ev["feasible"] and ev["objective"][0] == len(best)
except Exception:
    report = {
        "idea_id": "Q3-R23", "question_id": "Q3", "status": "failed",
        "seed": SEED, "failure_mode": "replicate_crash",
        "traceback": traceback.format_exc(limit=12),
        "solve_wall_seconds": round(time.time() - T_START, 2),
    }
json.dump(report, open(report_path, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
print(json.dumps({k: v for k, v in report.items() if k != "solution_path"}, ensure_ascii=False))
if report["status"] != "completed":
    sys.exit(1)
