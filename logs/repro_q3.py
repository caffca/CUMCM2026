# -*- coding: utf-8 -*-
import json, os, subprocess, sys
RUN = "SMOKE-R1"
d = os.path.join("runs", "fresh", RUN, "tasks", "q3-Q3-R11-main-N-A-p0", "attempts", "1")
os.makedirs(d, exist_ok=True)
cmd = [sys.executable, "code/prod/q3v_enum.py", "--run-id", RUN,
       "--parameter", json.dumps({"base": "@Q2MAIN"}), "--output-dir", d, "--budget-class", "full"]
r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
print("rc", r.returncode)
print(r.stdout[-400:])
print(r.stderr[-800:])
