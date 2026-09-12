# -*- coding: utf-8 -*-
import json, io, os, sys
sys.path.insert(0, r"C:\Users\Administrator\.dsh\.agent-presets\mathmodel-v7\skills\3coding-visual\scripts")
sys.stdout.reconfigure(encoding="utf-8")
import sharded_run as sr
from pathlib import Path

SRC = "reports/execution/SHARD_PLAN.json"
old = json.load(io.open("logs/SHARD_PLAN.stored.json", encoding="utf-8"))
os.rename(SRC, "logs/SHARD_PLAN.tmpmove")
plan, errs = sr.build_production_plan(Path(".").resolve(), "FULL-D2026-PROD-C", "full")
os.rename("logs/SHARD_PLAN.tmpmove", SRC)
if errs:
    print("errs", errs[:2]); sys.exit(1)
for k in sorted(set(old) | set(plan)):
    a = json.dumps(old.get(k), sort_keys=True, ensure_ascii=False)
    b = json.dumps(plan.get(k), sort_keys=True, ensure_ascii=False)
    if a != b:
        print("== DIFF:", k)
        if k == "tasks":
            for x, y in zip(old["tasks"], plan["tasks"]):
                ax, by = json.dumps(x, sort_keys=True), json.dumps(y, sort_keys=True)
                if ax != by:
                    for kk in sorted(set(x) | set(y)):
                        if json.dumps(x.get(kk), sort_keys=True) != json.dumps(y.get(kk), sort_keys=True):
                            print("   ", x.get("task_id"), "|", kk)
                            print("      old:", str(x.get(kk))[:180])
                            print("      new:", str(y.get(kk))[:180])
        else:
            print("   old:", str(old.get(k))[:220])
            print("   new:", str(plan.get(k))[:220])
print("diff scan done")
