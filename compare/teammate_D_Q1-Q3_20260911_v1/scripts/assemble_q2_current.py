#!/usr/bin/env python3
"""Assemble the best currently validated Q2 incumbent without overclaiming."""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def metric_counts(summary: dict) -> dict:
    counts = summary["counts_by_category"]
    modified = {category: counts[category]["调整数量"] + counts[category]["撤销数量"] for category in "ABC"}
    total_shift = sum(abs(action["频移"]) + abs(action["时移"]) for action in summary["actions"])
    return {
        "revocations": sum(counts[category]["撤销数量"] for category in "ABC"),
        "adjusted_plans": sum(counts[category]["调整数量"] for category in "ABC"),
        "modified_A": modified["A"],
        "modified_B": modified["B"],
        "modified_C": modified["C"],
        "total_absolute_shift": total_shift,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--minimum-revocations", type=Path, required=True)
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--validation", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    minimum_revocations = load(args.minimum_revocations)
    candidate = load(args.candidate)
    validation = load(args.validation)
    values = metric_counts(candidate["summary"])
    payload = {
        "question": "D-Q2",
        "status": "FEASIBLE_INCUMBENT",
        "optimality": "NOT_PROVED",
        "method": "候选动作枚举 + 完整候选冲突约束 MILP + 独立连续/离散复核",
        "objective_order": [
            "minimum revocations",
            "minimum adjusted plans",
            "minimum modified A plans",
            "minimum modified B plans",
            "minimum total absolute shift",
        ],
        "objective_interpretation": "将题面‘尽量’层级解释为字典序目标；当前仅报告限时 MILP 找到的可行 incumbent，不把未证实的阶段值写成全局最优。",
        "time_domain": [0, 643],
        "frequency_domain": [0, 100],
        "rules": {
            "frequency_shift_limit": 10,
            "time_shift_limit": 5,
            "one_action_per_plan": True,
            "keep_duration_gap_and_uses": True,
            "half_open_intervals": True,
        },
        "candidate_count": candidate["candidate_count"],
        "candidate_conflict_edge_count": candidate["candidate_conflict_edge_count"],
        "plan_count": candidate["summary"]["plans"],
        "objective_values": values,
        "summary": candidate["summary"],
        "stage_chain": {
            "minimum_revocations_incumbent": {
                "status": minimum_revocations["status"],
                "optimality": minimum_revocations.get("optimality", "NOT_PROVED"),
                "objective": "revoke",
                "optimization": minimum_revocations["optimization"],
                "note": "该 19 撤销方案由 H=638 正确边界筛选模型得到，并在 H=643 域中再次独立验证可行。",
            },
            "minimum_adjusted_given_19_revocations": {
                "status": candidate["status"],
                "optimality": candidate.get("optimality", "NOT_PROVED"),
                "objective": "adjust",
                "fixed_values": candidate.get("fixed_values", {"revoke": 19}),
                "optimization": candidate["optimization"],
            },
        },
        "validation": validation,
        "claim_boundary": {
            "feasibility": validation["status"] == "PASS",
            "global_minimum_revocations_proved": False,
            "minimum_adjusted_given_19_proved": candidate.get("optimality") == "PROVED",
            "paper_wording": "可写为‘在 H=643 域内找到 19 个撤销、113 个调整的无冲突可行方案’，不可写成‘最少撤销 19 个’或‘最优方案’。",
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"status": payload["status"], "objective_values": values, "output": str(args.output)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
