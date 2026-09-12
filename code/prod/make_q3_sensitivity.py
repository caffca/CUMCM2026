# -*- coding: utf-8 -*-
"""Q3_sensitivity 诊断件：本基座 Φ + 侦察期备查口径（alt bases / 2B 重排）真实历史数据，标诊断。"""
import io, json, os, subprocess, sys

WRITER = r"C:\Users\Administrator\.dsh\.agent-presets\mathmodel-v7\skills\3coding-visual\scripts\result_writer.py"
d3 = json.load(io.open("results/Q3_solution.json", encoding="utf-8"))
srows = []
scout_dir = "runs/competitive/CS-20260911T071520-D2026/scouts/Q3-R11"
if os.path.isdir(scout_dir):
    for f in sorted(os.listdir(scout_dir)):
        if f.endswith("result.json"):
            try:
                r = json.load(io.open(os.path.join(scout_dir, f), encoding="utf-8"))
                srows.append({"file": f, "note": "侦察期历史运行（非权威链）",
                              "keys": {k: r.get(k) for k in ("N_star", "phi", "ub_phase", "base_tag") if k in r}})
            except Exception:
                pass
payload = {"question_id": "Q3", "variant": "sensitivity_diag",
           "alt2B_ran": 1, "main_phi_production_base": d3.get("phi"),
           "scout_alt_bases": srows,
           "statement": ("生产权威口径=问题二交付解冻结基座（result3 三列模板语义）；"
                         "备查口径（可重排基座/2B）在侦察链实测存在，数值层级为历史诊断，不并入权威。")}
tmp = "runs/checks/Q3_sensitivity.src.json"
json.dump(payload, io.open(tmp, "w", encoding="utf-8"), ensure_ascii=False)
cmd = [sys.executable, WRITER, "--workspace", ".", "--payload", tmp,
       "--output", "results/Q3_sensitivity.json", "--problem-id", "Q3", "--role", "support",
       "--diagnostic", "--generator", "code/prod/make_q3_sensitivity.py",
       "--input-file", "results/Q3_solution.json"]
if os.path.exists("results/Q3_sensitivity.json"):
    cmd.append("--replace")
r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
print("writer rc", r.returncode, (r.stdout or r.stderr)[-200:])
