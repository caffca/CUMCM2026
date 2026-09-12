# -*- coding: utf-8 -*-
"""SMOKE 全链预演：构造假 run（SMOKE-R1），把各 variant 小预算 payload 摆进 tasks 目录，
再跑 check+synth，捕获路径/键名 bug。"""
import json, os, shutil, subprocess, sys

RUN = "SMOKE-R1"
root = os.path.join("runs", "fresh", RUN, "tasks")
shutil.rmtree(os.path.join("runs", "fresh", RUN), ignore_errors=True)


def put(qdir, task, payload_name, param, extra=None):
    d = os.path.join(root, task, "attempts", "1")
    os.makedirs(d, exist_ok=True)
    p = dict(param or {})
    if extra:
        p.update(extra)
    cmd = [sys.executable, os.path.join("code", "prod", payload_name),
           "--run-id", RUN, "--stage", "coding_visual", "--seed", "N/A", "--scenario", "main",
           "--parameter", json.dumps(p), "--output-dir", d, "--budget-class", "full"]
    r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8")
    print(task, "->", r.returncode, (r.stdout or "").strip()[-120:], (r.stderr or "").strip()[-200:] if r.returncode else "")
    return d


# Q2 main(w4)+w1+grasp×3+check+synth
put(root, "q2-Q2-R51-main-N-A-p0", "q2v_cpsat.py", {"workers": 4, "stage_budget": {"l1": 100, "ladder": 20, "l2": 20, "l3": 12, "l4": 12}})
put(root, "q2-Q2-R51-main-N-A-p1", "q2v_cpsat.py", {"workers": 1, "stage_budget": {"l1": 100, "ladder": 20, "l2": 20, "l3": 12, "l4": 12}})
for i, sd in enumerate((11, 29, 47)):
    put(root, f"q2-Q2-R51-main-N-A-p{2+i}", "q2v_grasp.py", {"grasp_seed": sd, "budget": 25})
put(root, "q2-Q2-R51-main-N-A-p5", "check_q2.py", {"solution": "@Q2MAIN"})
put(root, "q2-Q2-R51-main-N-A-p6", "q_synth.py", {"question": "Q2"})
# Q3
put(root, "q3-Q3-R11-main-N-A-p0", "q3v_enum.py", {"variant": "enum", "base": "@Q2MAIN"})
put(root, "q3-Q3-R11-main-N-A-p1", "q3v_cpsat.py", {"variant": "cpsat_a", "base": "@Q2MAIN", "limit": 90})
put(root, "q3-Q3-R11-main-N-A-p2", "q3v_cpsat.py", {"variant": "cpsat_b", "base": "@Q2MAIN", "limit": 90})
put(root, "q3-Q3-R11-main-N-A-p3", "q3v_cpsat.py", {"variant": "lp_hiGHS", "base": "@Q2MAIN"})
put(root, "q3-Q3-R11-main-N-A-p4", "q3v_bound.py", {"variant": "bound_elementary", "base": "@Q2MAIN"})
put(root, "q3-Q3-R11-main-N-A-p5", "q3v_check.py", {"solution": "@Q3MAIN", "base": "@Q2MAIN"})
put(root, "q3-Q3-R11-main-N-A-p6", "q_synth.py", {"question": "Q3"})
# Q4
put(root, "q4-Q4-R11-main-N-A-p0", "q4v_cpsat.py", {"workers": 4, "stage_budget": {"l1": 100, "ladder": 20, "l2": 20, "l3": 12, "l4": 12}, "q2_solution": "@Q2MAIN", "anchor": True})
put(root, "q4-Q4-R11-main-N-A-p1", "q4v_cpsat.py", {"workers": 1, "stage_budget": {"l1": 100, "ladder": 20, "l2": 20, "l3": 12, "l4": 12}, "q2_solution": "@Q2MAIN", "anchor": True})
put(root, "q4-Q4-R11-main-N-A-p2", "q4v_check.py", {"solution": "@Q4MAIN"})
put(root, "q4-Q4-R11-main-N-A-p3", "q_synth.py", {"question": "Q4"})
print("=== synth payloads ===")
for t in ("q2-Q2-R51-main-N-A-p6", "q3-Q3-R11-main-N-A-p6", "q4-Q4-R11-main-N-A-p3"):
    d = json.load(open(os.path.join(root, t, "attempts", "1", "payload.json"), encoding="utf-8"))
    keys = [k for k in ("objective_tuple", "phi", "revoke", "residual_pairs_second_impl",
                         "compliance_violations", "ladder_proven_revoke_lb", "gap_revoke", "degeneracy_ratio",
                         "repro_w1_eq_w8", "grasp_revoke_median", "cand_count_second_impl_minus_solver",
                         "ub_min", "gap_certified", "base_is_production_q2", "scalar", "scalar_q2_ref",
                         "planted_q2_feasible", "revoke_gain_vs_q2", "violations_second_impl")
            if k in d]
    print(t.split("-p")[-1], d.get("question_id"), {k: d[k] for k in keys if not isinstance(d[k], (list, dict))})
