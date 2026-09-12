# -*- coding: utf-8 -*-
"""compute budget 诊断件（bundle remaining_budget 的合法数值源）。"""
import io, json, os, subprocess, sys

WRITER = r"C:\Users\Administrator\.dsh\.agent-presets\mathmodel-v7\skills\3coding-visual\scripts\result_writer.py"
import datetime
now = datetime.datetime.now()
close = now.replace(hour=18, minute=0, second=0, microsecond=0) + datetime.timedelta(days=1)
remaining = max(0.0, round((close - now).total_seconds() / 3600.0, 2))
payload = {"artifact": "compute_budget", "remaining_budget_hours": remaining,
           "question_ids": ["__budget__"],
           "basis": "竞赛窗口保守估计（至次日 18:00 提交截止）；供 whole-problem bundle 预算契约使用",
           "generated_at": now.astimezone().isoformat(timespec="seconds")}
tmp = "runs/checks/compute_budget.src.json"
json.dump(payload, io.open(tmp, "w", encoding="utf-8"), ensure_ascii=False)
cmd = [sys.executable, WRITER, "--workspace", ".", "--payload", tmp,
       "--output", "results/compute_budget.json", "--problem-id", "Q2", "--role", "support",
       "--diagnostic", "--generator", "code/prod/make_compute_budget.py",
       "--input-file", "data/canonical_plans.csv"]
if os.path.exists("results/compute_budget.json"):
    cmd.append("--replace")
r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace",
                   env=dict(os.environ, PYTHONIOENCODING="utf-8"))
print("rc", r.returncode, (r.stdout or r.stderr)[-120:])
sys.exit(r.returncode)
