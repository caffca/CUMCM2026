# -*- coding: utf-8 -*-
import hashlib, io, json

def sha(p): return hashlib.sha256(open(p, "rb").read()).hexdigest()

Q1 = "results/Q1_detect.json"
Q2 = "results/Q2_solution.json"
Q3 = "results/Q3_solution.json"
Q4 = "results/Q4_solution.json"
req = {
    "schema_version": 1,
    "run_id": "FULL-D2026-PROD-H",
    "problem_id": "D2026",
    "question_ids": ["Q1", "Q2", "Q3", "Q4"],
    "inputs": {
        "result_registry": {"path": "results/RESULT_REGISTRY.json", "sha256": sha("results/RESULT_REGISTRY.json")},
    },
    "shared_states": [
        {"state_id": "T_MAX", "question_ids": ["Q1", "Q2", "Q3", "Q4"],
         "value_ref": {"path": Q1, "sha256": sha(Q1), "value_path": "T_MAX"}},
        {"state_id": "evaluator_frozen_sha", "question_ids": ["Q1", "Q2", "Q3", "Q4"],
         "value_ref": {"path": Q1, "sha256": sha(Q1), "value_path": "evaluator_frozen_sha256"}},
        {"state_id": "q2_authority_tuple", "question_ids": ["Q2"],
         "value_ref": {"path": Q2, "sha256": sha(Q2), "value_path": "objective_tuple"}},
        {"state_id": "q3_base_tuple", "question_ids": ["Q3"],
         "value_ref": {"path": Q3, "sha256": sha(Q3), "value_path": "base_tuple"}},
        {"state_id": "q4_anchor_tuple", "question_ids": ["Q4"],
         "value_ref": {"path": Q4, "sha256": sha(Q4), "value_path": "planted_q2_tuple"}},
    ],
}
io.open("logs/wp_req.json", "w", encoding="utf-8").write(json.dumps(req, ensure_ascii=False, indent=1))
print("req v3 written")
