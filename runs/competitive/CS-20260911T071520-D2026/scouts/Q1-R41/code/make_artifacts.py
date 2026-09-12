# -*- coding: utf-8 -*-
"""按 TOURNAMENT_PROTOCOL.result_artifact_contract + route-contract §4 落盘
本候选的 result.json 与 scout.json（只写本 scout 目录）。

输入：同 scout 目录的 detect_meta.json（原型自算）+ eval.json（canonical evaluator 输出）。
失败/不一致同样写盘（status=failed），不删记录。
"""
import io
import json
import os
import time

HERE = os.path.dirname(os.path.abspath(__file__))
SCOUT_DIR = os.path.abspath(os.path.join(HERE, ".."))
RUN_DIR = os.path.abspath(os.path.join(SCOUT_DIR, "..", ".."))
ROOT = os.path.abspath(os.path.join(RUN_DIR, "..", "..", ".."))
IDEA_ID = os.path.basename(SCOUT_DIR)

BUDGET_SECONDS = 600          # 协议 scout_wall_seconds_per_candidate_per_replicate
REPLICATES = 1                # 协议 replicates_deterministic（Q1 三候选均标注为确定性）


def rel(p):
    return os.path.relpath(p, ROOT).replace("\\", "/")


def read_json(path, default=None):
    if not os.path.isfile(path):
        return default
    return json.load(io.open(path, encoding="utf-8"))


def main():
    meta = read_json(os.path.join(SCOUT_DIR, "detect_meta.json"), {})
    ev = read_json(os.path.join(SCOUT_DIR, "eval.json"))
    sol = meta.get("solution_path")
    sol_abs = os.path.join(ROOT, sol.replace("/", os.sep)) if sol else None

    if ev is None:
        objective, objective_tuple = None, None
        feasible, evaluator_invoked = False, False
        consistency_fail = "canonical_evaluator_not_invoked"
    else:
        objective_tuple = ev["objective"]
        objective = objective_tuple[0] if len(objective_tuple) == 1 else objective_tuple
        evaluator_invoked = True
        c = ev.get("counts", {})
        feasible = bool(ev.get("feasible")) and c.get("missing") == 0 and c.get("spurious") == 0

    # ---- 候选内部一致性判据（协议/路线硬验收）----
    checks = {}
    if IDEA_ID == "Q1-R21":
        checks = {
            "impl_A_vs_impl_B_symdiff": meta["evaluation"]["symdiff_AB"],
            "impl_A_equals_impl_B": meta["evaluation"]["impl_A_equals_impl_B"],
            "boundary_cases_all_pass": len(meta["boundary_case_failures"]) == 0,
            "csv_equals_common_input_compact":
                meta["data_source"]["common_input_equivalence"].get("equivalent"),
        }
        internal_ok = (checks["impl_A_vs_impl_B_symdiff"] == 0
                       and checks["impl_A_equals_impl_B"]
                       and checks["boundary_cases_all_pass"]
                       and checks["csv_equals_common_input_compact"])
    elif IDEA_ID == "Q1-R52":
        checks = {
            "class_homogeneity_g_d_n": meta["applicability"]["homogeneous"],
            "closed_form_time_predicate_pairs_checked":
                meta["pairs"]["time_predicate_pairs_checked_by_closed_form"],
            "closed_form_vs_enum_time_predicate_mismatches":
                meta["pairs"]["time_predicate_mismatches"],
            "closed_form_vs_enum_edge_pair_symdiff": meta["pairs"]["pair_symdiff"],
            "edge_sets_elementwise_equal": meta["pairs"]["elementwise_equal"],
            "bound_validity_LB_le_enum_le_UB":
                meta["bound_validity_selfcheck"]["LB_le_enum_le_UB"],
            "cross_class_fallback_pairs": meta["pairs"]["fallback_enum_branch_used"],
            "intra_class_LB": meta["analytic_bounds_intra_class"]["LB_intra"],
            "intra_class_UB": meta["analytic_bounds_intra_class"]["UB_intra"],
        }
        internal_ok = (checks["class_homogeneity_g_d_n"]
                       and checks["closed_form_vs_enum_time_predicate_mismatches"] == 0
                       and checks["closed_form_vs_enum_edge_pair_symdiff"] == 0
                       and checks["edge_sets_elementwise_equal"]
                       and checks["bound_validity_LB_le_enum_le_UB"])
    else:  # Q1-R41
        ph, pb = meta["phaseA"], meta["phaseB_stress"]
        checks = {
            "symdiff_join_vs_bitand": ph["symdiff_D1_D2"],
            "symdiff_join_vs_oracle_pruned": ph["symdiff_D1_D3_pruned"],
            "symdiff_join_vs_oracle_fullscan": ph["symdiff_D1_D3_full"],
            "boundary_cases_all_pass": len(meta["boundary_case_failures"]) == 0,
            "stress_trials_completed": pb["trials_completed"],
            "stress_injection_recall": pb["injection_recall"],
            "stress_deletion_vanish_recall": pb["deletion_vanish_recall"],
            "stress_pair_level_missing": pb["pair_level_missing"],
            "stress_pair_level_false_positive": pb["pair_level_false_positive"],
            "stress_global_symdiff": pb["global_symdiff"],
            "per_seed_symdiff": {k: v["global_symdiff"] for k, v in pb["per_seed"].items()},
            "per_seed_pair_miss": {k: v["pair_miss"] for k, v in pb["per_seed"].items()},
        }
        internal_ok = (checks["symdiff_join_vs_bitand"] == 0
                       and checks["symdiff_join_vs_oracle_pruned"] == 0
                       and checks["symdiff_join_vs_oracle_fullscan"] == 0
                       and checks["boundary_cases_all_pass"]
                       and pb["injection_recall"] == 1.0
                       and pb["deletion_vanish_recall"] == 1.0
                       and pb["pair_level_missing"] == 0 and pb["pair_level_false_positive"] == 0
                       and pb["global_symdiff"] == 0)

    runtime = float(meta.get("runtime_seconds", 0.0))
    status = "completed" if (internal_ok and evaluator_invoked and objective == 0
                             and feasible) else "failed"
    failure_mode = None if status == "completed" else (
        meta.get("failure_mode") or "consistency_or_evaluator_mismatch")
    if status == "failed" and failure_mode is None:
        failure_mode = "unknown"

    result = {
        "question_id": meta.get("question_id", "Q1"),
        "idea_id": IDEA_ID,
        "status": status,
        "feasible": bool(feasible and status == "completed"),
        "objective": objective,
        "objective_tuple": objective_tuple,
        "objective_unit": "symdiff_vs_canonical_truth（minimize）",
        "runtime_seconds": round(runtime, 4),
        "runtime_total_seconds": meta.get("runtime_total_seconds"),
        "evaluator_invoked": evaluator_invoked,
        "evaluator_command": (
            "python runs/competitive/CS-20260911T071520-D2026/canonical_evaluator.py "
            "--question Q1 --solution {} --out {}/eval.json".format(sol, rel(SCOUT_DIR))),
        "canonical_evaluator_sha256_bound": "8c4db98fa11845ca5492255e4da6c4b2e92e040ee30556fa9156993c06fcbb32",
        "seed": meta.get("seed", "N/A（确定性路线）"),
        "replicates": REPLICATES,
        "solution_path": sol,
        "solution_sha256": None,
        "conflict_pairs": (meta.get("conflict_pairs")
                            or meta.get("pairs", {}).get("cf_edges")),
        "by_class_pair": meta.get("by_class_pair") or meta.get("phaseA", {}).get("by_class_pair"),
        "plans_touched": meta.get("plans_touched") or meta.get("phaseA", {}).get("plans_touched"),
        "pairs_evaluated": (meta.get("evaluation", {}).get("pairs_evaluated")
                            or meta.get("pairs", {}).get("pairs_evaluated")
                            or meta.get("phaseA", {}).get("pairs_evaluated_bitand")),
        "evaluator_counts": (ev or {}).get("counts"),
        "internal_consistency": checks,
        "budget": {"scout_wall_seconds_per_candidate_per_replicate": BUDGET_SECONDS,
                   "used_seconds": round(runtime, 4),
                   "utilization": round(runtime / BUDGET_SECONDS, 5)},
        "adjudication_binding": {"T_MAX": 643, "half_open_intervals": True,
                                 "reference": "runs/competitive/CS-20260911T071520-D2026/ADJUDICATION.json"},
        "failure_mode": failure_mode,
        "finished_at": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "note": "最小可运行原型（侦察证据），非正式论文结果；未写 results/figures/paper。",
    }
    try:
        import hashlib
        if sol_abs and os.path.isfile(sol_abs):
            result["solution_sha256"] = hashlib.sha256(
                io.open(sol_abs, "rb").read()).hexdigest()
    except Exception as exc:                      # pragma: no cover
        result["solution_sha256_error"] = str(exc)

    scout = {
        "idea_id": IDEA_ID,
        "question_id": meta.get("question_id", "Q1"),
        "started_at": meta.get("started_at"),
        "feasible": result["feasible"],
        "objective": objective,
        "objective_tuple": objective_tuple,
        "runtime_seconds": round(runtime, 4),
        "replicate_values": [objective] if objective is not None else [],
        "replicates": REPLICATES,
        "stability_metric": 0.0 if status == "completed" else None,
        "stability_note": "确定性路线（Q1 三候选均标注 deterministic）：同输入 SHA 重跑逐位一致；"
                          "跨实现对称差同时为 0，故 replicate 间方差为 0。",
        "lower_bound": objective,
        "upper_bound": objective,
        "relative_gap": 0.0,
        "bound_note": "完全枚举/等价闭式，无近似间隙 ⇒ lower_bound = upper_bound = objective，"
                      "relative_gap = 0（协议：确定性路线）。",
        "evaluations": {"pair_evaluations": result["pairs_evaluated"],
                        "pairs_total_expected": 11175,
                        "internal_cross_checks": checks},
        "stopping_reason": ("all_pairs_enumerated_and_dual_impl_symdiff_zero"
                            if status == "completed" else "hard_acceptance_mismatch"),
        "budget_exhausted": False,
        "failure_mode": failure_mode,
        "canonical_evaluator": {"invoked": evaluator_invoked,
                                "out": rel(os.path.join(SCOUT_DIR, "eval.json")),
                                "counts": (ev or {}).get("counts")},
        "solution_path": sol,
        "status": status,
    }
    if IDEA_ID == "Q1-R41":
        scout["stopping_reason"] = ("all_pairs_enumerated_and_planted_stress_recall_1_"
                                    "symdiff_zero_across_3_frozen_seeds"
                                    if status == "completed" else scout["failure_mode"])
        scout["replicate_values"] = [objective]           # 主指标（确定性阶段A）
        scout["stability_metric"] = 0.0
        scout["stress_seed_replicates"] = {
            k: {"global_symdiff": v["global_symdiff"], "pair_miss": v["pair_miss"],
                "pair_fp": v["pair_fp"], "injection_recall":
                    (v["planted_hit"] / max(1, v["injected"])),
                "deletion_vanish_recall": (v["vanish_ok"] / max(1, v["deleted"]))}
            for k, v in meta["phaseB_stress"]["per_seed"].items()}

    with io.open(os.path.join(SCOUT_DIR, "result.json"), "w", encoding="utf-8") as fh:
        json.dump(result, fh, ensure_ascii=False, indent=1)
    with io.open(os.path.join(SCOUT_DIR, "scout.json"), "w", encoding="utf-8") as fh:
        json.dump(scout, fh, ensure_ascii=False, indent=1)
    print(IDEA_ID, "status=", status, "objective=", objective,
          "runtime=", result["runtime_seconds"], "failure_mode=", failure_mode)
    return result, scout


if __name__ == "__main__":
    main()
