#!/usr/bin/env python3
"""Assemble the priority-first Q2 sensitivity result."""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--minimum-revocations", type=Path, required=True)
    parser.add_argument("--preserve-a", type=Path, required=True)
    parser.add_argument("--preserve-b", type=Path, required=True)
    parser.add_argument("--preserve-c", type=Path, required=True)
    parser.add_argument("--minimum-adjusted", type=Path, required=True)
    parser.add_argument("--minimum-shift", type=Path, required=True)
    parser.add_argument("--validation", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    stage_paths = {
        "minimum_revocations": args.minimum_revocations,
        "preserve_A": args.preserve_a,
        "preserve_B": args.preserve_b,
        "preserve_C": args.preserve_c,
        "minimum_adjusted": args.minimum_adjusted,
        "minimum_shift": args.minimum_shift,
    }
    stages = {name: load(path) for name, path in stage_paths.items()}
    final = stages["minimum_shift"]
    validation = load(args.validation)
    counts = final["summary"]["counts_by_category"]
    objective_values = {
        "revocations": stages["minimum_revocations"]["optimization"]["objective_value"],
        "modified_A": stages["preserve_A"]["optimization"]["objective_value"],
        "modified_B": stages["preserve_B"]["optimization"]["objective_value"],
        "modified_C": stages["preserve_C"]["optimization"]["objective_value"],
        "adjusted_plans": stages["minimum_adjusted"]["optimization"]["objective_value"],
        "total_absolute_shift": stages["minimum_shift"]["optimization"]["objective_value"],
    }
    all_stages_optimal = all(stage["optimality"] == "PROVED" for stage in stages.values())
    first_stage_proved = stages["minimum_revocations"]["optimality"] == "PROVED"
    payload = {
        "question": "D-Q2",
        "status": "OPTIMAL" if all_stages_optimal else "FEASIBLE_INCUMBENT",
        "optimality": "PROVED" if all_stages_optimal else "NOT_PROVED",
        "method": "候选动作枚举 + 完整候选冲突约束 MILP + 独立连续/离散复核",
        "objective_order": [
            "minimum revocations",
            "minimum modified A plans",
            "minimum modified B plans",
            "minimum modified C plans",
            "minimum adjusted plans",
            "minimum total absolute shift",
        ],
        "objective_interpretation": "作为主模型字典序的优先级敏感性：在撤销数固定后，先最大化 A、B、C 计划保持，再比较调整总数和位移幅度。",
        "time_domain": [0, 643],
        "frequency_domain": [0, 100],
        "rules": {
            "frequency_shift_limit": 10,
            "time_shift_limit": 5,
            "one_action_per_plan": True,
            "keep_duration_gap_and_uses": True,
            "half_open_intervals": True,
        },
        "candidate_count": final["candidate_count"],
        "candidate_conflict_edge_count": final["candidate_conflict_edge_count"],
        "plan_count": final["summary"]["plans"],
        "objective_values": objective_values,
        "summary": final["summary"],
        "stage_chain": {
            name: {
                "status": stage["status"],
                "optimality": stage["optimality"],
                "objective": stage.get("objective", "revoke"),
                "fixed_values": stage.get("fixed_values", {}),
                "optimization": stage["optimization"],
            }
            for name, stage in stages.items()
        },
        "validation": validation,
        "claim_boundary": {
            "feasibility": validation["status"] == "PASS",
            "conditional_stages_proved": all(stage["optimality"] == "PROVED" for name, stage in stages.items() if name != "minimum_revocations"),
            "global_minimum_revocations_proved": first_stage_proved,
            "paper_wording": "当前可写为‘在限时 MILP 得到的 61 撤销 incumbent 条件下，优先级敏感性方案的后续阶段条件最优；全局最小撤销数尚未证明’，不可写成全局最优。" if not first_stage_proved else "各阶段均已证明最优。",
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({
        "status": payload["status"],
        "optimality": payload["optimality"],
        "objective_values": objective_values,
        "output": str(args.output),
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
