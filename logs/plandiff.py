# -*- coding: utf-8 -*-
"""诊断 production 源计划 重算差异：备份现有→触发重算→逐 key diff。"""
import json, io, subprocess, sys, os, shutil, glob

SR = r"C:\Users\Administrator\.dsh\.agent-presets\mathmodel-v7\skills\3coding-visual\scripts\sharded_run.py"
SRC = "reports/execution/SHARD_PLAN.json"
BAK = "logs/SHARD_PLAN.stored.json"

shutil.copy(SRC, BAK)
# 触发 --production --check 重算（它会把重算结果写回 SRC 吗？先备份）
r = subprocess.run([sys.executable, SR, "--workspace", ".", "--production", "--run-id", "FULL-D2026-PROD-C",
                    "--budget-class", "full", "--check"], capture_output=True, text=True, encoding="utf-8",
                   env=dict(os.environ, PYTHONIOENCODING="utf-8"))
print("check rc", r.returncode)
print((r.stdout or "")[-600:], (r.stderr or "")[-600:])
try:
    new = json.load(io.open(SRC, encoding="utf-8"))
except Exception as e:
    print("SRC not rewritten:", e)
    new = None
old = json.load(io.open(BAK, encoding="utf-8"))
if new:
    ks = sorted(set(old) | set(new))
    for k in ks:
        if json.dumps(old.get(k), sort_keys=True) != json.dumps(new.get(k), sort_keys=True):
            ov, nv = old.get(k), new.get(k)
            print("DIFF top-level key:", k)
            if isinstance(ov, list) and isinstance(nv, list) and ov and isinstance(ov[0], dict):
                for a, b in zip(ov, nv):
                    if json.dumps(a, sort_keys=True) != json.dumps(b, sort_keys=True):
                        for kk in sorted(set(a) | set(b)):
                            if json.dumps(a.get(kk), sort_keys=True) != json.dumps(b.get(kk), sort_keys=True):
                                print("   task", a.get("task_id"), "->", kk, "|", str(a.get(kk))[:80], "!=", str(b.get(kk))[:80])
            else:
                print("   ", str(ov)[:120], "!=", str(nv)[:120])
