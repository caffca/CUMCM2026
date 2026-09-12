# -*- coding: utf-8 -*-
import json, io, os, sys
sys.stdout.reconfigure(encoding="utf-8")
new = json.load(io.open("reports/execution/SHARD_PLAN.json", encoding="utf-8"))
old = json.load(io.open("logs/SHARD_PLAN.tmpmove", encoding="utf-8"))
for k in sorted(set(old) | set(new)):
    a = json.dumps(old.get(k), sort_keys=True, ensure_ascii=False)
    b = json.dumps(new.get(k), sort_keys=True, ensure_ascii=False)
    if a != b:
        print("== DIFF:", k)
        if k == "tasks":
            for x, y in zip(old["tasks"], new["tasks"]):
                if json.dumps(x, sort_keys=True) != json.dumps(y, sort_keys=True):
                    for kk in sorted(set(x) | set(y)):
                        if json.dumps(x.get(kk), sort_keys=True) != json.dumps(y.get(kk), sort_keys=True):
                            print("   ", x.get("task_id"), "|", kk)
                            print("      old:", str(x.get(kk))[:200])
                            print("      new:", str(y.get(kk))[:200])
        else:
            print("   old:", str(old.get(k))[:240])
            print("   new:", str(new.get(k))[:240])
print("scan complete")
