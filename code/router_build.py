# -*- coding: utf-8 -*-
"""V7-P3-02 Reviewer Router 决策投影构建器（methodology_review 产物，解释性路由，非模型 authority）。"""
import hashlib, io, json, os, datetime

def sha(p): return hashlib.sha256(open(p, "rb").read()).hexdigest()

PRESET = r"C:\Users\Administrator\.dsh\.agent-presets\mathmodel-v7"
MAN = json.load(io.open(os.path.join(PRESET, "PRESET_BUILD_MANIFEST.json"), encoding="utf-8"))
FMS = json.load(io.open("reports/FINAL_MODEL_SPEC.json", encoding="utf-8"))
FORM_SHA = {p["problem_id"]: p["formulation_sha256"] for p in FMS["problems"]}

FMS_PATH = "reports/FINAL_MODEL_SPEC.json"
OPP_PATH = "reports/discovery/MODEL_OPPORTUNITIES.json"
QC_PATH = "reports/contracts/QUESTION_CONTRACT.json"
DEC_PATH = "reports/contracts/IDEA_DECISION.json"
MAN_PATH = os.path.join(PRESET, "PRESET_BUILD_MANIFEST.json").replace("\\", "/")

def ref(path, role, qids=None):
    e = {"path": path, "sha256": sha(path), "role": role}
    if qids: e["question_ids"] = qids
    return e

def basis(path, fpath, signal, prec, spec, reason, qids=None):
    return {"source_ref": ref(path, "authority_input", qids), "field_path": fpath,
            "structural_signal": signal, "precedence_level": prec, "specialist": spec, "reason": reason}

routes = {
 "Q1": {
  "question_id": "Q1", "route_status": "routed", "reviewer_slot": "B",
  "classification": "primary_only", "primary_specialist": "operations_research",
  "secondary_checklist": None,
  "basis": [basis(FMS_PATH, "/problems[Q1].formulation_kind", "analytical/exhaustive_enum", "fms",
                  "operations_research", "完全枚举判定与组合计数属 OR/枚举专长", ["Q1"]),
           basis(OPP_PATH, "/opportunities[Q1-OP-special_boundary]", "resource_box_boundary", "discovery",
                 "operations_research", "边界资源盒与周期窗集合结构", ["Q1"])],
  "authority_conflicts": [], "fallback_action": "none",
  "reason": "FMS kind=analytical 的枚举完备性审查：B 席主判 = operations_research（区间交/组合枚举），无歧义。",
  "input_snapshot_sha256": FORM_SHA["Q1"]},
 "Q2": {
  "question_id": "Q2", "route_status": "routed", "reviewer_slot": "B",
  "classification": "ambiguous", "primary_specialist": "operations_research",
  "secondary_checklist": {"specialist": "multiobjective_optimization", "checklist_id": "Q2-LEX-CHECK",
    "checks": ["词典序四级锁定顺序与题面层级链一致", "标量化权重不串层（max ploss<步长）",
               "撤销阶梯证书方向正确（INFEASIBLE 只增 LB）", "incumbent 与 bound 分列不冒领"]},
  "basis": [basis(FMS_PATH, "/problems[Q2].formulation_kind", "optimization/lexicographic_csp", "fms",
                  "operations_research", "多选择 CSP/约束规划求解属 OR", ["Q2"]),
            basis(QC_PATH, "/questions[Q2].evaluation_target", "multi_level_objective", "claim_type",
                  "multiobjective_optimization", "四级目标链的达成性属多目标优化审查", ["Q2"])],
  "authority_conflicts": [], "fallback_action": "one_primary_plus_one_narrow_secondary",
  "reason": "FMS=optimization 主判 OR；claim_type 含多目标层级 ⇒ 附一条窄域多目标审查清单。",
  "input_snapshot_sha256": FORM_SHA["Q2"]},
 "Q3": {
  "question_id": "Q3", "route_status": "routed", "reviewer_slot": "B",
  "classification": "primary_only", "primary_specialist": "operations_research",
  "secondary_checklist": None,
  "basis": [basis(FMS_PATH, "/problems[Q3].formulation_kind", "optimization/set_packing", "fms",
                  "operations_research", "集包装/装箱与上下界会合证明属 OR", ["Q3"])],
  "authority_conflicts": [], "fallback_action": "none",
  "reason": "认证最优三腿（CP-SAT/LP/穷举完备）均由 OR 专长覆盖。",
  "input_snapshot_sha256": FORM_SHA["Q3"]},
 "Q4": {
  "question_id": "Q4", "route_status": "routed", "reviewer_slot": "B",
  "classification": "ambiguous", "primary_specialist": "operations_research",
  "secondary_checklist": {"specialist": "multiobjective_optimization", "checklist_id": "Q4-DOM-CHECK",
    "checks": ["支配界（域包含⇒不劣）表述与工件一致", "热启动解过 evaluator 复验", "收益判定未闭合前不宣称改善"]},
  "basis": [basis(FMS_PATH, "/problems[Q4].formulation_kind", "optimization/retiming_extension", "fms",
                  "operations_research", "扩域 CSP+支配界属 OR", ["Q4"]),
            basis(QC_PATH, "/questions[Q4].evaluation_target", "dominance_vs_q2", "claim_type",
                  "multiobjective_optimization", "不劣于 Q2 的目标链比较属多目标审查", ["Q4"])],
  "authority_conflicts": [], "fallback_action": "one_primary_plus_one_narrow_secondary",
  "reason": "同 Q2 结构加支配界审查窄清单。",
  "input_snapshot_sha256": FORM_SHA["Q4"]}
}

doc = {
 "schema_version": 1, "artifact_id": "review_router_decision",
 "router_decision_id": "RRD-D2026-01",
 "problem_id": "D2026", "question_ids": ["Q1", "Q2", "Q3", "Q4"],
 "authority_inputs": {
   "discovery_refs": [ref(OPP_PATH, "problem_structure", ["Q1", "Q2", "Q3", "Q4"])],
   "fms_refs": [ref(FMS_PATH, "formulation_kind_authority", ["Q1", "Q2", "Q3", "Q4"])],
   "validation_claim_refs": [ref(QC_PATH, "claim_type_source", ["Q1", "Q2", "Q3", "Q4"])]},
 "authority_precedence": ["fms_formulation_kind_domain", "discovery_structure", "validation_claim_type"],
 "routes_by_question": routes,
 "reviewer_roster": [
   {"seat_id": "A", "identity": "Competition Modeling Generalist", "count": 1, "fixed": True},
   {"seat_id": "B", "identity": "Dynamic Specialist", "count": 1, "primary_per_question": 1,
    "secondary_max_per_question": 1, "finite_seat": True},
   {"seat_id": "C", "identity": "Scientific Paper & Visual Editor", "count": 1, "fixed": True}],
 "fallback": {"ambiguous": "one_primary_plus_one_narrow_secondary",
   "missing_or_invalid_structured_input": "fail_closed_return_to_methodology_review",
   "unknown_domain": "reject_without_fanout", "invalid_provenance": "fail_closed",
   "max_reviewer_seats": 3, "all_specialist_fanout": False},
 "failure_routes": {"figure_data_render_error": "figure_editorial", "figure_type_selection": "editorial_plan",
   "figure_text_order_explanation": "writing", "float_pagination_whitespace": "compile_package",
   "claim_without_evidence": "result_review", "model_structure_error": "methodology_review",
   "statistical_protocol_error": "validation_plan", "coding_visual_error": "coding_visual", "unknown": "compile_package"},
 "review_policy": {"finding_only": True, "self_repair": False, "self_close": False,
   "repair_owner": "existing_final_review_repair_editorial", "same_reviewer_re_review": True,
   "new_trip_required": True, "original_verdict_immutable": True, "verification_read_only": True,
   "verification_dispatches_reviewer": False, "verification_closes_finding": False,
   "independence_basis": "role_and_context_isolation_only",
   "same_model_is_not_statistical_independence": True,
   "forbidden_route_inputs": ["paper_wording", "gate_status", "other_reviewer_score",
                               "other_reviewer_conclusion", "review_order", "repair_result"]},
 "provenance": {"source_commit": MAN["source_commit"], "preset_bundle_sha256": MAN["bundle_sha256"],
   "producer": "methodology_review", "run_id": "CS-20260911T071520Z-1A9D30",
   "input_refs": [ref(FMS_PATH, "fms"), ref(OPP_PATH, "discovery"), ref(QC_PATH, "claims"), ref(DEC_PATH, "route_winner")],
   "preset_manifest_ref": {"path": MAN_PATH, "sha256": sha(MAN_PATH), "role": "preset_provenance"},
   "prompt_model_resource": {"prompt_sha256": sha("code/router_build.py"), "model": "qwen3.8-flash",
                              "resource_profile": "standard"},
   "generated_at": datetime.datetime.now().astimezone().isoformat(timespec="seconds")},
 "invalidation": {"changed_input_refs": [], "invalidated_question_ids": [],
   "invalidated_artifacts": [], "invalidated_stages": []},
 "authority_boundary": {"explanatory_routing_only": True, "can_modify_idea": False, "can_modify_fms": False,
   "can_modify_solver": False, "can_modify_result_registry": False, "can_close_own_finding": False}}
os.makedirs("reports/review", exist_ok=True)
io.open("reports/review/REVIEW_ROUTER_DECISION.json", "w", encoding="utf-8").write(json.dumps(doc, ensure_ascii=False, indent=1))
print("router decision written; commit", MAN["source_commit"][:8], "bundle", MAN["bundle_sha256"][:8])
