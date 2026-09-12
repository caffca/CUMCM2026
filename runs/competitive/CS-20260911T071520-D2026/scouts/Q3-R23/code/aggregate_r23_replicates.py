# -*- coding: utf-8 -*-
"""Q3-R23 三重复聚合（评审闭环追加任务）：
读取 seed=11（既有 run_report.json）+ seed=29/47（run_report_seed{S}.json），
聚合 = median over replicates（协议 aggregation_stochastic；平手按 tuple 再按更低 runtime，
tuple=[count,UB] 相同 ⇒ 平手取 runtime 更低者，seed=11 记录保持）；
stability_metric = 极差/中位数。若 median 由 seed29/47 的解取得（seed11 值 ≠ median），
把该解复制为 solution_newc.json 并重跑 evaluator → eval_q3.json。失败重复保留记录不删。"""
import json
import os
import shutil
import statistics
import subprocess
import sys
import io

D = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))   # .../scouts/Q3-R23
CS_DIR = os.path.dirname(os.path.dirname(os.path.dirname(D)))
SEEDS = (11, 29, 47)

reps = {}
per_rep_wall = {}
for s in SEEDS:
    fn = "run_report.json" if s == 11 else f"run_report_seed{s}.json"
    p = os.path.join(D, fn)
    if not os.path.isfile(p):
        reps[s] = {"status": "missing", "count": None}
        continue
    r = json.load(io.open(p, encoding="utf-8"))
    st = r.get("status")
    if st is None:  # seed=11 既有报告无 status 字段：由 evaluator 结果推断
        st = "completed" if (r.get("evaluator", {}).get("feasible") and r.get("best_count") is not None) else "failed"
    reps[s] = {"status": st, "count": r.get("best_count"),
               "wall_s": r.get("solve_wall_seconds"),
               "iterations": r.get("lns", {}).get("iterations"),
               "accepted": r.get("lns", {}).get("accepted"),
               "stopped_by": r.get("lns", {}).get("stopped_by"),
               "failure_mode": r.get("failure_mode"),
               "report_file": fn}
    if reps[s]["status"] == "completed":
        per_rep_wall[s] = reps[s]["wall_s"]

completed = {s: v["count"] for s, v in reps.items() if v["status"] == "completed" and v["count"] is not None}
assert len(completed) == 3, f"协议要求 3 重复齐全: {reps}"
values = [completed[11], completed[29], completed[47]]
med = int(statistics.median(values))
rng = max(values) - min(values)
stability = rng / med

# 选中重复：count==median；平手取 runtime 更低（seed11 优先保持既有 solution 记录）
cands_sel = [s for s in SEEDS if completed[s] == med]
sel = min(cands_sel, key=lambda s: (per_rep_wall[s], s))

changed = False
if sel != 11:
    src = os.path.join(D, f"solution_newc_seed{sel}.json")
    dst = os.path.join(D, "solution_newc.json")
    shutil.copyfile(src, dst)
    ev_out = os.path.join(D, "eval_q3.json")
    subprocess.run([sys.executable, os.path.join(CS_DIR, "canonical_evaluator.py"),
                    "--question", "Q3", "--solution", dst,
                    "--base-actions", os.path.join(CS_DIR, "scouts", "Q2-R51", "solution_actions.json"),
                    "--out", ev_out],
                   capture_output=True, text=True, encoding="utf-8", check=True)
    changed = True
    ev = json.load(io.open(ev_out, encoding="utf-8"))
    assert ev["feasible"] and ev["objective"][0] == med, ev
else:
    ev = json.load(io.open(os.path.join(D, "eval_q3.json"), encoding="utf-8"))

UB = 332  # R51 初等界（R23 三候选对照 UB，保持不变）

p = os.path.join(D, "result.json")
r = json.load(io.open(p, encoding="utf-8"))
r.update({
    "status": "completed", "feasible": bool(ev["feasible"]),
    "objective": med, "objective_tuple": [med, UB],
    "replicates": 3,
    "replicate_values": values,
    "aggregation": "median over replicates (协议 aggregation_stochastic；平手按 tuple 再按更低 runtime)",
    "selected_replicate_seed": sel,
    "stability_metric": {"kind": "极差/中位数", "range": rng, "median": med, "value": stability},
    "seed": "seed_set=[11,29,47]（协议冻结）；LNS 唯一随机源；三跑同一流水线同参数，各 ≤240s",
    "runtime_seconds": round(statistics.median([per_rep_wall[s] for s in SEEDS]), 2),
    "runtime_seconds_per_replicate": {str(s): reps[s]["wall_s"] for s in SEEDS},
    "evaluator_invoked": True,
    "failure_mode": None,
    "replicate_reports": {str(s): {"count": reps[s]["count"], "status": reps[s]["status"],
                                   "report_file": reps[s]["report_file"],
                                   "failure_mode": reps[s]["failure_mode"]} for s in SEEDS},
    "revision_note": "评审闭环修订 v2：补跑 seed=29/47 满 3 重复；solution 选择=median 规则（本例 selected_seed=%d%s）" % (sel, "，solution_newc.json/eval_q3.json 已随之更新" if changed else "，与 seed=11 既有记录一致，主文件未替换"),
})
json.dump(r, io.open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

p = os.path.join(D, "scout.json")
s = json.load(io.open(p, encoding="utf-8"))
s.update({
    "objective": med, "lower_bound": med, "upper_bound": UB,
    "relative_gap": (UB - med) / UB,
    "replicates": 3, "replicate_values": values, "median": med,
    "stability_metric": stability,
    "stability_kind": "极差/中位数（range/median）",
    "selected_replicate_seed": sel,
    "solution_replaced_from_replicate": bool(changed),
    "replicate_detail": {str(x): reps[x] for x in SEEDS},
    "stopping_reason": "3 重复（seed 11/29/47）各 240s LNS 预算耗尽；聚合=median；评审闭环要求 stochastic 候选 3 重复已补齐",
    "revision_note": "评审闭环修订 v2：由 1 重复补至 3 重复（seed=29/47 各 ≤240s 同流水线）；聚合与稳定性字段新增",
})
json.dump(s, io.open(p, "w", encoding="utf-8"), ensure_ascii=False, indent=1)

print(json.dumps({"values": values, "median": med, "range": rng,
                  "stability": round(stability, 4), "selected_seed": sel,
                  "solution_replaced": changed,
                  "per_seed": {str(x): {"count": reps[x]["count"], "wall": reps[x]["wall_s"],
                                         "iters": reps[x]["iterations"], "status": reps[x]["status"]}
                               for x in SEEDS}}, ensure_ascii=False, indent=1))
