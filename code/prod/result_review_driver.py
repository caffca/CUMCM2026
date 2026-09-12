# -*- coding: utf-8 -*-
"""result_review 装配驱动：完全复用官方 build_result_interpretation 的函数与结构，
仅对每条 must claim 应用 builder 自带的唯一兜底命名 claim:{vid}（builder 缺 claim_id 时即此规则），
以解决本 plan 多条 validation 归同一语义 claim_id 导致的“duplicate”——不改 plan、不改 verdict/route。"""
import importlib.util, json, sys
from pathlib import Path

SPEC = r"C:\Users\Administrator\.dsh\.agent-presets\mathmodel-v7\skills\9result-review\scripts\build_result_interpretation.py"
spec = importlib.util.spec_from_file_location("bri", SPEC)
bri = importlib.util.module_from_spec(spec)
spec.loader.exec_module(bri)

ws = Path(".").resolve()
plan_path = ws / "reports" / "VALIDATION_PLAN.json"
eval_path = ws / "reports" / "VALIDATION_EVAL.json"
plan = bri.read_json(plan_path, "VALIDATION_PLAN")
evaluation = bri.read_json(eval_path, "VALIDATION_EVAL")
for key in ("evidence_integrity", "execution_metadata", "result_evidence", "independent_reproduction"):
    d = evaluation.get(key)
    assert isinstance(d, dict) and d.get("status") == "PASS", f"{key} not PASS"
plan_map = {str(x.get("validation_id")): x for x in plan.get("validations", []) if isinstance(x, dict)}
evals = evaluation["evaluations"]
must = [x for x in evals if isinstance(x, dict) and x.get("priority") == "must"]
rec = [x for x in evals if isinstance(x, dict) and x.get("priority") != "must"]
claims = []
for item in must:
    c = bri.build_claim(plan_map, evaluation, item)
    c["claim_id"] = f"claim:{c['validation_ids'][0]}"  # builder 自带唯一兜底命名
    claims.append(c)
assert len({c["claim_id"] for c in claims}) == len(claims)
eval_sha = bri.sha256_file(eval_path)
plan_sha = bri.sha256_file(plan_path)
revisions = bri.collect_revisions(ws, plan, evaluation)
interp = {
    "schema_version": 2, "review_revision": 1,
    "generated_at": str(evaluation.get("ran_at") or "result-review-generated"),
    "validation_eval_ref": "reports/VALIDATION_EVAL.json",
    "validation_eval_sha256": eval_sha, "validation_plan_sha256": plan_sha,
    "source_artifact_revisions": revisions,
    "model_decision_binding": evaluation.get("model_decision_binding"),
    "result_registry_ref": evaluation.get("result_registry_ref"),
    "claims": claims,
    "recommended_evaluations": [
        {k: item.get(k) for k in ("validation_id", "claim_id", "question_id", "priority", "verdict", "evidence_refs")}
        for item in rec],
    "producer": "skills/9result-review/scripts/build_result_interpretation.py",
    "producer_sha256": bri.sha256_file(Path(SPEC)),
}
bri.write_json_atomic(ws / "reports" / "RESULT_INTERPRETATION.json", interp)
(ws / "reports").mkdir(exist_ok=True)
(ws / "reports" / "RESULT_REVIEW.md").write_text(bri.build_markdown(ws, evaluation, claims, eval_sha), encoding="utf-8")
from collections import Counter
print("claims:", len(claims), dict(Counter(c["claim_status"] for c in claims)),
      "| recommended:", len(rec), dict(Counter(x.get("verdict") for x in rec)))
