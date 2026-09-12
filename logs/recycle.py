# -*- coding: utf-8 -*-
"""router_request 刷新（重算 authority SHA）+ 重建 router + 校验 + vp 刷新。"""
import hashlib, io, json, os, subprocess, sys
from datetime import datetime

V = r"C:\Users\Administrator\.dsh\.agent-presets\mathmodel-v7\skills\6verity\scripts"
R7 = r"C:\Users\Administrator\.dsh\.agent-presets\mathmodel-v7\skills\7methodology-review\scripts\review_router.py"


def sha(p): return hashlib.sha256(open(p, "rb").read()).hexdigest()


def ref(p, role, qs=None):
    e = {"path": p.replace("\\", "/"), "sha256": sha(p), "role": role}
    if qs:
        e["question_ids"] = qs
    return e


Q = ["Q1", "Q2", "Q3", "Q4"]
ENVELO = dict(os.environ, PYTHONIOENCODING="utf-8")
PRESET = r"C:\Users\Administrator\.dsh\.agent-presets\mathmodel-v7"
man = json.load(io.open(os.path.join(PRESET, "PRESET_BUILD_MANIFEST.json"), encoding="utf-8"))
req = {"schema_version": 1, "problem_id": "D2026", "question_ids": Q,
       "inputs": {
           "discovery": [ref("reports/discovery/MODEL_OPPORTUNITIES.json", "problem_structure", Q),
                          ref("reports/discovery/PROBLEM_STRUCTURE.json", "structure", Q)],
           "fms": [ref("reports/FINAL_MODEL_SPEC.json", "formulation_authority", Q)],
           "validation_claims": [ref("reports/contracts/QUESTION_CONTRACT.json", "claim_type_source", Q)]},
       "provenance": {"run_id": "CS-20260911T071520Z-1A9D30", "model": "qwen3.8-flash",
                       "resource_profile": "standard", "producer": "methodology_review",
                       "source_commit": man["source_commit"], "preset_bundle_sha256": man["bundle_sha256"],
                       "preset_manifest_ref": ref("PRESET_BUILD_MANIFEST.json", "preset_provenance"),
                       "prompt_model_resource": {"model": "qwen3.8-flash", "resource_profile": "standard"},
                       "generated_at": datetime.now().astimezone().isoformat(timespec="seconds")}}
io.open("logs/router_request.json", "w", encoding="utf-8").write(json.dumps(req, ensure_ascii=False, indent=1))

r = subprocess.run([sys.executable, R7, "--workspace", ".", "--request", "logs/router_request.json"],
                   capture_output=True, text=True, encoding="utf-8", env=ENVELO)
print("router build:", r.returncode, (r.stdout or "").strip()[-160:])
g = subprocess.run([sys.executable, V + r"\review_router_gate.py", "--workspace", ".", "--strict"],
                   capture_output=True, text=True, encoding="utf-8", env=ENVELO)
print("router gate:", (g.stdout or "").strip()[-160:])
v = subprocess.run([sys.executable, "code/vp_build.py"], capture_output=True, text=True, encoding="utf-8", env=ENVELO)
print("vp:", (v.stdout or v.stderr).strip()[-160:])
for st in ("methodology_review", "validation_plan"):
    c = subprocess.run([sys.executable, V + r"\stage_close.py", "--workspace", ".", "--stage", st],
                       capture_output=True, text=True, encoding="utf-8", env=ENVELO)
    print("close", st, ":", (c.stdout or c.stderr).strip()[-120:])
pl = subprocess.run([sys.executable, "code/prod/run_prod.py", "plan"], capture_output=True,
                    text=True, encoding="utf-8")
print("plan:", (pl.stdout or pl.stderr).strip()[-300:])
