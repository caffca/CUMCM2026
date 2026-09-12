"""Solve CUMCM2026 D, Q1: enumerate periodic time-frequency conflicts."""

from __future__ import annotations

import argparse
from collections import Counter
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from d_problem.conflicts import find_conflict_pairs  # noqa: E402
from d_problem.domain import PlanState  # noqa: E402
from d_problem.io import load_plans, write_q1_result  # noqa: E402
from d_problem.validation import validate_schedule  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=ROOT / "D题/附件/附件1.xlsx")
    parser.add_argument("--template", type=Path, default=ROOT / "D题/附件/附件2/result1.xlsx")
    parser.add_argument("--output", type=Path, default=ROOT / "outputs/q1/result1.xlsx")
    parser.add_argument("--json", type=Path, default=ROOT / "outputs/q1/conflicts.json")
    parser.add_argument(
        "--plot-data",
        type=Path,
        default=ROOT / "outputs/q1/plot_data/q1_conflict_categories.json",
    )
    args = parser.parse_args()

    plans = load_plans(args.input)
    states = [PlanState(plan) for plan in plans]
    report = validate_schedule(states, horizon=643)
    conflicts = find_conflict_pairs(states)
    write_q1_result(args.output, conflicts, args.template)
    args.json.parent.mkdir(parents=True, exist_ok=True)
    args.json.write_text(
        json.dumps(
            {
                "plan_count": report.plan_count,
                "occurrence_count": report.occurrence_count,
                "conflict_count": report.conflict_count,
                "pairs": [
                    {
                        "plan_i": pair.plan_i,
                        "plan_j": pair.plan_j,
                        "occurrence_i": pair.witness.occurrence_i,
                        "occurrence_j": pair.witness.occurrence_j,
                        "f_overlap": pair.witness.f_overlap,
                        "t_overlap": pair.witness.t_overlap,
                    }
                    for pair in conflicts
                ],
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    category_pairs = Counter(
        "-".join(sorted((pair.plan_i[0], pair.plan_j[0]))) for pair in conflicts
    )
    category_order = ["A-A", "A-B", "A-C", "B-B", "B-C", "C-C"]
    args.plot_data.parent.mkdir(parents=True, exist_ok=True)
    args.plot_data.write_text(
        json.dumps(
            {
                "figure_id": "fig_q1_conflict_categories",
                "question": "Q1",
                "kind": "category_bar",
                "unit_and_population": "去重冲突计划对；150 个原始用频计划",
                "aggregation": "按类别组合统计冲突计划对",
                "uncertainty": "none",
                "categories": [
                    {"label": label, "value": category_pairs.get(label, 0)}
                    for label in category_order
                ],
                "total_conflicts": len(conflicts),
                "supported_claim": "B-C 是数量最多的原始冲突类别。",
                "forbidden_inference": "类别冲突数量不等于 Q2 的撤销或调整优先级。",
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    print(
        json.dumps(
            {
                "plans": report.plan_count,
                "occurrences": report.occurrence_count,
                "conflicts": report.conflict_count,
                "result": str(args.output),
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
