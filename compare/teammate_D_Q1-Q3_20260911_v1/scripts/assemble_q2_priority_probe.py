#!/usr/bin/env python3
"""Assemble a same-revocation A-priority probe for Q2 comparison."""
from __future__ import annotations

import argparse
import json
from pathlib import Path


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--candidate", type=Path, required=True)
    parser.add_argument("--validation", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    candidate = load(args.candidate)
    validation = load(args.validation)
    counts = candidate["summary"]["counts_by_category"]
    values = {
        "revocations": sum(counts[c]["撤销数量"] for c in "ABC"),
        "adjusted_plans": sum(counts[c]["调整数量"] for c in "ABC"),
        "modified_A": counts["A"]["调整数量"] + counts["A"]["撤销数量"],
        "modified_B": counts["B"]["调整数量"] + counts["B"]["撤销数量"],
        "modified_C": counts["C"]["调整数量"] + counts["C"]["撤销数量"],
        "total_absolute_shift": sum(abs(row["频移"]) + abs(row["时移"]) for row in candidate["summary"]["actions"]),
    }
    payload = {
        "question": "D-Q2",
        "status": "FEASIBLE_INCUMBENT",
        "optimality": "NOT_PROVED",
        "method": "same-19-revocation A-priority probe",
        "objective_order": ["minimum revocations", "minimum modified A plans"],
        "objective_interpretation": "仅作为与当前 19 撤销主 incumbent 同口径的 A 类优先级探测，不是完整 priority-first 最优链。",
        "time_domain": [0, 643],
        "frequency_domain": [0, 100],
        "candidate_count": candidate["candidate_count"],
        "candidate_conflict_edge_count": candidate["candidate_conflict_edge_count"],
        "plan_count": candidate["summary"]["plans"],
        "objective_values": values,
        "summary": candidate["summary"],
        "optimization": candidate["optimization"],
        "validation": validation,
        "claim_boundary": {
            "feasibility": validation["status"] == "PASS",
            "global_minimum_revocations_proved": False,
            "probe_optimality_proved": False,
            "paper_wording": "只用于说明同一 19 撤销 incumbent 下 A 类优先探测的代价，不作为最终 result2.xlsx 的优化证明。",
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"status": payload["status"], "objective_values": values, "output": str(args.output)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
