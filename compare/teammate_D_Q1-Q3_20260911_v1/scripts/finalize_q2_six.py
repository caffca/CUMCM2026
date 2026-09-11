#!/usr/bin/env python3
"""Freeze the validated six-revocation incumbent with explicit bound evidence."""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def read_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--validation", type=Path, required=True)
    parser.add_argument("--revocation-proof", type=Path, required=True)
    parser.add_argument("--priority-run", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=Path("outputs/q2/results.json"))
    args = parser.parse_args()

    candidate = read_json(args.candidate)
    validation = read_json(args.validation)
    proof = read_json(args.revocation_proof)
    priority = read_json(args.priority_run)
    objective = candidate["objective_values"]
    if validation.get("status") != "PASS":
        raise ValueError("six-revocation incumbent did not pass independent validation")
    if not (
        proof.get("status") == "OPTIMAL"
        and proof.get("optimality") == "PROVED"
        and proof.get("found_revocations") == 6
        and proof.get("optimization", {}).get("objective_value") == 6
        and proof.get("optimization", {}).get("best_objective_bound") == 6
    ):
        raise ValueError("revocation proof does not establish LB=UB=6")
    stages = priority.get("optimization", {}).get("stages", [])
    if len(stages) < 3 or stages[0].get("optimality") != "PROVED" or stages[1].get("optimality") != "PROVED":
        raise ValueError("priority run did not prove the expected objective prefix")
    if objective["revocations"] != 6 or objective["revoke_A"] != 0 or objective["revoke_B"] != 4:
        raise ValueError("candidate objective values do not match the certified/incumbent prefix")

    payload = {
        "question": "D-Q2",
        "status": "PRIMARY_OPTIMAL_SECONDARY_INCUMBENT",
        "optimality": "PRIMARY_OBJECTIVE_PROVED",
        "method": "CP-SAT 资源格团约束证明主目标 + 外部六撤销方案规范化 + 独立连续/离散冲突复核",
        "scheme": "priority_protected",
        "objective_order": [
            "minimum revocations",
            "minimum A revocations",
            "minimum B revocations",
            "minimum adjusted plans",
            "minimum A adjustments",
            "minimum B adjustments",
            "minimum normalized shift |df|/10+|dt|/5",
        ],
        "objective_interpretation": "精炼方案 B。撤销优先于调整，类别优先分别作用于撤销和调整；后续层只有在所有更高层已经证明后才允许宣称条件最优。",
        "time_domain": [0, 643],
        "frequency_domain": [0, 100],
        "rules": {
            "frequency_shift_limit": 10,
            "time_shift_limit": 5,
            "one_action_per_plan": True,
            "keep_duration_gap_and_uses": True,
            "half_open_intervals": True,
        },
        "plan_count": candidate["plan_count"],
        "candidate_count": proof["candidate_count"],
        "resource_cell_constraint_count": proof["resource_cell_constraint_count"],
        "objective_values": objective,
        "bounds": {
            "revocations": {"lower_bound": 6, "upper_bound": 6, "status": "PROVED_OPTIMAL"},
            "revoke_A_given_R6": {"lower_bound": 0, "upper_bound": 0, "status": "PROVED_OPTIMAL"},
            "revoke_B_given_R6_RA0": {
                "lower_bound": int(stages[2]["best_objective_bound"]),
                "upper_bound": objective["revoke_B"],
                "status": "NOT_PROVED",
            },
            "adjusted_plans": {"upper_bound": objective["adjusted_plans"], "status": "INCUMBENT_ONLY"},
        },
        "proof_chain": stages,
        "evidence": {
            "revocation_proof": str(args.revocation_proof),
            "priority_prefix_run": str(args.priority_run),
            "normalized_candidate": str(args.candidate),
            "independent_validation": str(args.validation),
            "source_workbook": candidate["source_workbook"],
        },
        "summary": candidate["summary"],
        "validation_snapshot": {
            "status": validation["status"],
            "counts_by_category": validation["counts_by_category"],
            "checks": validation["checks"],
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({
        "output": str(args.output),
        "status": payload["status"],
        "bounds": payload["bounds"],
        "objective_values": objective,
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
