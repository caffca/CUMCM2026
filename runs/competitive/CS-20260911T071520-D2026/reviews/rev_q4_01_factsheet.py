# -*- coding: utf-8 -*-
"""REV-Q4-01 附件脚本 J：把全部复算结果折叠成评审结论所需的『事实表』，并落盘
   reviews/_tmp/review_fact_sheet.json（人工核对用 + 附件 SHA 清单）。
"""
import io, json, os, sys

RUN = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TMP = os.path.join(RUN, "reviews", "_tmp")
A = json.load(io.open(os.path.join(TMP, "recheck_out.json"), encoding="utf-8"))["checks"]
B = json.load(io.open(os.path.join(TMP, "recheck_out_B.json"), encoding="utf-8"))
C = json.load(io.open(os.path.join(TMP, "recheck_out_C.json"), encoding="utf-8"))
D = json.load(io.open(os.path.join(TMP, "recheck_out_D.json"), encoding="utf-8"))
E = json.load(io.open(os.path.join(TMP, "recheck_out_E.json"), encoding="utf-8"))
F = json.load(io.open(os.path.join(TMP, "recheck_out_F.json"), encoding="utf-8"))
G = json.load(io.open(os.path.join(TMP, "recheck_out_G.json"), encoding="utf-8"))
H = json.load(io.open(os.path.join(TMP, "recheck_out_H.json"), encoding="utf-8"))
I = json.load(io.open(os.path.join(TMP, "recheck_out_I.json"), encoding="utf-8"))

facts = {
    "independent_recomputation": {
        "R11_tuple_indep_vs_claim": [A["R11"]["independent_tuple"], A["R11"]["claimed_result_tuple"]],
        "R11_residual_conflicts_indep": A["R11"]["independent_residual_conflicts"],
        "R11_sample20_pair_overlaps": A["R11"]["sample20_overlaps"],
        "R11_dg_actions": A["R11"]["n_dg_actions"],
        "R11_dg_max_last_end": max(d["last_end"] for d in A["R11"]["dg_detail"]),
        "R11_dg_all_rules_ok": all(d["within_643"] and d["gp_ge1"] and d["dg_le10"]
                                   for d in A["R11"]["dg_detail"]),
        "R11_evaluator_recheck": A["R11"]["evaluator_recheck_tuple"],
        "R41_median_seed": A["R41"]["median_seed_by_claimed"],
        "R41_result_tuple": A["R41"]["result_json_tuple"],
        "R41_median_is_seed29": A["R41"]["median_is_seed29"],
        "R41_per_seed_indep_eval_agree": {k: (v["indep_matches_claim"] and v["eval_matches_claim"])
                                          for k, v in A["R41"]["per_seed_independent"].items()},
        "R22_tuple_indep_vs_claim": [A["R22"]["independent_tuple"], A["R22"]["claimed_tuple"]],
        "R22_mod10_rule_recount": A["R22"]["mod10_rule"],
        "R22_empty_strip_edge": A["R22"]["empty_strip_claim"],
    },
    "inclusion_and_dominance": {
        "q2reduction_dual_eval": [A["inclusion"]["evaluator_as_Q2"], A["inclusion"]["evaluator_as_Q4"]],
        "q2reduction_has_dg": A["inclusion"]["q2reduction_contains_dg"],
        "objective_tuple_ignores_allow_gap": True,
        "domain_subset_B": B["A_domains"], "edge_subset_B": B["A_edges"], "clause_subset_B": B["A_clauses"],
        "edge_audit_independent_E": E["E_edge_table_audit"],
        "q2_official_incumbent_in_q4_E": C["R11_model_can_hold_6revoke"],
        "q2_official_incumbent_A": A["inclusion"]["q2_official_incumbent"],
    },
    "attack_evidence": {
        "R11_mag_polish_H": {k: H["R11"][k] for k in ("original_tuple", "polished_tuple",
                                                      "n_mag_reductions", "frozen_after", "saturated")},
        "R22_unrevoke_C": {k: C["R22_unrevoke_test"][k] for k in
                           ("n_restored", "tuple_after_restore", "frozen_evaluator_tuple",
                            "frozen_evaluator_feasible", "residual_after_restore")},
        "R22_cross_kind_mag_polish_G": {k: G["G2_shrink_kind_preference"][k] for k in
                                        ("n_improvable_same_pass", "tuple_before", "tuple_after")},
        "R22_stage1_survival_F": {k: F["F1_r22_stage1_survival"][k] for k in
                                  ("stage1_claim_resolved_edges", "edges_with_both_endpoints_kept",
                                   "edges_surviving_via_retiming")},
        "R22_empty_strip_cause_G": G["G1_empty_strip_attribution"],
        "R22_dg_domain_F2": F["F2_r11_dg_domain"],
        "R11_revoke_mix_F2": {k: F["F2_r11_revoke_mix"][k] for k in
                              ("revA", "revB", "revC", "revoke_ploss_actual", "revoke_ploss_if_all_C")},
        "simpler_baselines_B": dict(revoke_only_vertex_cover=B["B_greedy_revoke_only"]["revokes"],
                                    degree_aware_repair=B["B2_degree_aware_repair"],
                                    incremental_greedy_C=C["B2_frozen_evaluator"]["tuple"]),
        "R41_f3_consistency_F": F["F3_r41_internal_consistency"]["per_seed"],
    },
    "caliber": {
        "evaluator_sha_binding_D": D["evaluator_sha"],
        "q4common_identical_across_scouts": D["q4common_identical_across_scouts"],
        "scout_evaluator_binding": D["scout_evaluator_binding"],
        "horizon_fact_D": D["horizon_fact"],
        "scalar_literals_D": D["scalar_literals_in_code"],
        "tier_spacing_C": C["scalarization_safety"],
    },
    "negative_test_matrix_I": dict(cases=[{k: c.get(k) for k in ("case", "outcome", "feasible",
                                                                 "violation_kinds", "objective")}
                                        for c in I["cases"]],
                                   defects=I["defects"], notes=I["notes"]),
}
io.open(os.path.join(TMP, "review_fact_sheet.json"), "w", encoding="utf-8").write(
    json.dumps(facts, ensure_ascii=False, indent=1, default=str))
print(json.dumps(facts["attack_evidence"], ensure_ascii=False, indent=1, default=str)[:2500])
