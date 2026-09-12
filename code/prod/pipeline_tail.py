# -*- coding: utf-8 -*-
"""流水线尾部：write_results → xlsx → submission_checks → verify → report → figures"""
import subprocess, sys, os

env = dict(os.environ, PYTHONIOENCODING="utf-8")
steps = [
    ("write_results", [sys.executable, "code/prod/write_results.py", "--run-id", "FULL-D2026-PROD-C"]),
    ("make_xlsx", [sys.executable, "code/prod/make_xlsx.py"]),
    ("submission_checks", [sys.executable, "code/prod/submission_checks.py"]),
    ("sensitivity", [sys.executable, "code/prod/make_q3_sensitivity.py"]),
    ("verify", [sys.executable, "code/verify_all.py"]),
    ("report", [sys.executable, "code/prod/make_report.py"]),
    ("figures", [sys.executable, "code/prod/make_figures.py"]),
]
log = open("logs/pipeline_tail.log", "a", encoding="utf-8")
for name, cmd in steps:
    log.write(f"\n===== {name} =====\n"); log.flush()
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", env=env)
    log.write((r.stdout or "")[-5000:])
    if r.stderr:
        log.write("\nSTDERR:" + r.stderr[-2500:])
    log.write(f"\n[{name}] rc={r.returncode}\n"); log.flush()
    print(name, "rc=", r.returncode, flush=True)
    if r.returncode != 0:
        print("TAIL-STOP-AT", name, flush=True)
        sys.exit(r.returncode)
print("TAIL-OK", flush=True)
