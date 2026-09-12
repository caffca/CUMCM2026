# -*- coding: utf-8 -*-
"""组装 Whole-Problem Route Bundle 请求（每问胜者选项，引用真实可信件）。"""
import hashlib, importlib.util, io, json, sys
from pathlib import Path
sys.stdout.reconfigure(encoding="utf-8")
SPEC = r"C:\Users\Administrator\.dsh\.agent-presets\mathmodel-v7\skills\brainstorm-mathmodel\scripts\whole_problem_route_bundle.py"
spec = importlib.util.spec_from_file_location("wpb", SPEC)
wpb = importlib.util.module_from_spec(spec)
spec.loader.exec_module(wpb)
RUN = "FULL-D2026-PROD-H"
AGG = f"runs/fresh/{RUN}/SHARD_AGGREGATE.json"


def sha(p): return hashlib.sha256(open(p, "rb").read()).hexdigest()


def ref(p, **kw):
    d = {"path": p.replace("\\", "/"), "sha256": sha(p)}
    d.update(kw)
    return d


WIN = {"Q1": ("Q1-R21", "results/bundle_view_Q1.json", f"runs/fresh/{RUN}/tasks/Q1-Q1-R21-main-N-A-p0/attempts/001/execution_metrics.json"),
       "Q2": ("Q2-R51", "results/bundle_view_Q2.json", f"runs/fresh/{RUN}/tasks/Q2-Q2-R51-main-N-A-p0/attempts/001/execution_metrics.json"),
       "Q3": ("Q3-R11", "results/bundle_view_Q3.json", f"runs/fresh/{RUN}/tasks/Q3-Q3-R11-main-N-A-p1/attempts/001/execution_metrics.json"),
       "Q4": ("Q4-R11", "results/bundle_view_Q4.json", f"runs/fresh/{RUN}/tasks/Q4-Q4-R11-main-N-A-p0/attempts/001/execution_metrics.json")}
EVAL = "reports/VALIDATION_EVAL.json"
opts = {}
for q, (cid, res, met) in WIN.items():
    opts[q] = [{
        "candidate_id": cid,
        "result_ref": ref(res, question_ids=[q]),
        "cost_ref": ref(met, value_path="elapsed_seconds", unit="seconds", question_ids=[q]),
        "coverage_ref": ref(EVAL, question_ids=[q]),
        "evidence_refs": [ref(res, question_ids=[q]), ref(EVAL, question_ids=[q])],
        "shared_state_ids": [],
    }]
req = {
    "schema_version": 1, "run_id": RUN, "problem_id": "D2026",
    "question_ids": ["Q1", "Q2", "Q3", "Q4"],
    "inputs": {
        "idea_decision": ref("reports/contracts/IDEA_DECISION.json"),
        "fms": ref("reports/FINAL_MODEL_SPEC.json"),
        "result_registry": ref("results/RESULT_REGISTRY.json"),
    },
    "remaining_budget": {
        "source_ref": ref("results/compute_budget.json"),
        "value_path": "remaining_budget_hours", "unit": "hours",
    },
    "route_options_by_question": opts,
    "shared_states": [
        {"state_id": "T_MAX", "question_ids": ["Q1", "Q2", "Q3", "Q4"],
         "value_ref": ref("results/Q1_detect.json", value_path="T_MAX", question_ids=["Q1", "Q2", "Q3", "Q4"]),
         "evidence_refs": [ref("results/Q1_detect.json", question_ids=["Q1"])]},
    ],
    "consistency_constraints": [
        {"constraint_id": "CC-Q2Q3-BASE", "question_ids": ["Q2", "Q3"],
         "expression": "Q3.base_tuple == Q2.objective_tuple", "unit_contract": "typed shared state (4-level tuple)",
         "check_ref": ref("results/degeneracy_triangle.json", question_ids=["Q2", "Q3"])},
        {"constraint_id": "CC-Q2Q4-ANCHOR", "question_ids": ["Q4", "Q2"],
         "expression": "Q4.planted_q2_tuple == Q2.objective_tuple", "unit_contract": "typed shared state (4-level tuple)",
         "check_ref": ref("results/Q4_solution.json", question_ids=["Q2", "Q4"])},
    ],
    "dependency_dag": [
        {"from_artifact": "shared_state:T_MAX", "to_artifact": wpb.ARTIFACT_ID,
         "question_ids": ["Q1", "Q2", "Q3", "Q4"], "edge_scope": "shared"},
    ] + [{"from_artifact": f"idea:{q}", "to_artifact": wpb.ARTIFACT_ID,
          "question_ids": [q], "edge_scope": "question_local"} for q in ("Q1", "Q2", "Q3", "Q4")],
    "reuse": [], "narrative_cost": "low",
    "provenance": {
        "problem_statement_ref": ref("D题.pdf"),
        "data_snapshot_refs": [ref("reports/data/DATASET_SNAPSHOT.json"), ref("data/canonical_plans.csv")],
        "preset_manifest_ref": ref("PRESET_BUILD_MANIFEST.json"),
        "prompt_model_resource": {"prompt_sha256": sha("logs/wp_req.json"), "model": "qwen3.8-flash",
                                   "resource_profile": "standard"},
    },
}
io.open("logs/wp_req.json", "w", encoding="utf-8").write(json.dumps(req, ensure_ascii=False, indent=1))
print("req v4 written; ARTIFACT_ID=", wpb.ARTIFACT_ID)
