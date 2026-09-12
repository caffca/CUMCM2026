# -*- coding: utf-8 -*-
"""谁引用了旧版/现行 VALIDATION_PLAN 指纹（追溯链新鲜度取证）。"""
import datetime
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import p2_common as P  # noqa

OLD = "2166c4c85eb0eb9d"
CUR = "f00b19480a65631c"

cands = ["results/Q1_detect.json", "results/Q1_stats.json", "results/Q1_verify.json",
         "results/Q2_solution.json", "results/Q2_check.json", "results/Q2_table1.json", "results/Q2_main_w4.json",
         "results/Q3_solution.json", "results/Q3_check.json", "results/Q3_bound.json",
         "results/Q3_submission_check.json", "results/Q4_solution.json", "results/Q4_check.json",
         "results/Q4_table1.json", "results/Q4_submission_check.json", "results/RESULT_REGISTRY.json",
         "reports/FINAL_MODEL_SPEC.json", "reports/VALIDATION_EVAL.json", "reports/execution/SHARD_PLAN.json",
         "state/artifact_bindings.json", "runs/fresh/FULL-D2026-PROD-E/SHARD_PLAN.json",
         "runs/fresh/FULL-D2026-PROD-E/SHARD_AGGREGATE.json", "reports/VALIDATION_PLAN.json"]
rows = []
for c in cands:
    p = os.path.join(P.ROOT, c)
    if not os.path.exists(p):
        rows.append((c, "MISSING", 0, 0, "-"))
        continue
    t = open(p, encoding="utf-8", errors="ignore").read()
    mt = datetime.datetime.fromtimestamp(os.path.getmtime(p)).strftime("%m-%d %H:%M:%S")
    rows.append((c, "", t.count(OLD), t.count(CUR), mt))
print(f"{'file':52s} {'OLD':>4s} {'CUR':>4s}  mtime")
for c, _, o, u, mt in rows:
    print(f"{c:52s} {o:4d} {u:4d}  {mt}")
vp = json.load(open(os.path.join(P.ROOT, "reports", "VALIDATION_PLAN.json"), encoding="utf-8"))
print("\nplan rev", vp.get("plan_revision"), "frozen_at", vp.get("frozen_at"),
      "claim_frozen_before_production", vp.get("frozen_before_production_runs"))
