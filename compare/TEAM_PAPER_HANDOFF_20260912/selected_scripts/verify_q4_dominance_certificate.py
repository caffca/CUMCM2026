#!/usr/bin/env python3
"""Verify the candidate-dominance reduction used by the Q4 R<=2 proof.

The global Q4 proof removes only active actions.  This checker independently
rebuilds the active-action conflict graph and records, for every removed
action, a retained action of the same plan whose external conflict set is a
subset.  It also checks that every original plan retains at least one active
action, so category-based revoke partitions are unchanged by the reduction.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
import json
from pathlib import Path

from scripts.solve_q1 import read_plans
from scripts.solve_q4_cp_sat import build_candidates


def candidate_key(candidate) -> list[object]:
    return [
        candidate.plan_id,
        candidate.action,
        candidate.df,
        candidate.dt,
        candidate.dg,
    ]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input", type=Path, default=Path("data/raw/D题/附件/附件1.xlsx")
    )
    parser.add_argument("--horizon", type=int, default=643)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    plans = read_plans(args.input)
    all_candidates = build_candidates(plans, args.horizon)
    active = [candidate for candidate in all_candidates if candidate.action != "revoke"]
    by_cell: defaultdict[tuple[int, int], list[int]] = defaultdict(list)
    by_plan: defaultdict[str, list[int]] = defaultdict(list)
    for index, candidate in enumerate(active):
        by_plan[candidate.plan_id].append(index)
        for cell in candidate.cells:
            by_cell[cell].append(index)

    neighbors = [set() for _ in active]
    for indexes in by_cell.values():
        for position, left in enumerate(indexes):
            for right in indexes[position + 1 :]:
                if active[left].plan_id == active[right].plan_id:
                    continue
                neighbors[left].add(right)
                neighbors[right].add(left)

    removed: set[int] = set()
    removal_reasons: dict[int, bool] = {}
    for indexes in by_plan.values():
        for left in indexes:
            if left in removed:
                continue
            for right in indexes:
                if left == right:
                    continue
                if neighbors[right] <= neighbors[left] and (
                    neighbors[right] != neighbors[left] or right < left
                ):
                    removed.add(left)
                    removal_reasons[left] = neighbors[right] == neighbors[left]
                    break

    kept = set(range(len(active))) - removed
    retained_keys = {tuple(candidate_key(active[index])) for index in kept}
    witnesses = []
    missing = []
    for left in sorted(removed):
        options = [
            right
            for right in by_plan[active[left].plan_id]
            if right in kept and neighbors[right] <= neighbors[left]
        ]
        if not options:
            missing.append(candidate_key(active[left]))
            continue
        right = min(options, key=lambda index: (len(neighbors[index]), index))
        witnesses.append(
            {
                "removed": candidate_key(active[left]),
                "dominator": candidate_key(active[right]),
                "removed_external_conflict_degree": len(neighbors[left]),
                "dominator_external_conflict_degree": len(neighbors[right]),
                "strict_subset": neighbors[right] < neighbors[left],
            }
        )

    plans_without_kept_action = [
        plan["id"]
        for plan in plans
        if not any(index in kept for index in by_plan[plan["id"]])
    ]
    category_counts = {
        category: sum(plan["category"] == category for plan in plans)
        for category in "ABC"
    }
    errors = []
    if missing:
        errors.append(f"removed actions without a retained dominator: {len(missing)}")
    if plans_without_kept_action:
        errors.append(f"plans without retained active action: {plans_without_kept_action}")
    if len(witnesses) != len(removed):
        errors.append("witness count does not equal removed-action count")

    payload = {
        "question": "D-Q4",
        "mode": "dominance_reduction_certificate_validation",
        "status": "PASS" if not errors else "FAIL",
        "proof": "DOMINANCE_REPLACEMENT_COVERAGE_CONFIRMED" if not errors else "NOT_CONFIRMED",
        "time_domain": [0, args.horizon],
        "frequency_domain": [0, 100],
        "input_candidate_count": len(all_candidates),
        "input_active_candidate_count": len(active),
        "removed_active_candidate_count": len(removed),
        "kept_active_candidate_count": len(kept),
        "plan_count": len(plans),
        "category_plan_counts": category_counts,
        "checks": {
            "every_removed_action_has_retained_same_plan_dominator": not missing,
            "every_plan_retains_active_action": not plans_without_kept_action,
            "all_dominators_are_retained": all(
                tuple(item["dominator"]) in retained_keys
                for item in witnesses
            ),
            "category_revoke_partition_is_unchanged": not plans_without_kept_action,
        },
        "witness_summary": {
            "witness_count": len(witnesses),
            "final_witness_strict_subset_count": sum(
                item["strict_subset"] for item in witnesses
            ),
            "final_witness_equal_set_count": sum(
                not item["strict_subset"] for item in witnesses
            ),
            "direct_equal_set_representative_removals": sum(
                removal_reasons.values()
            ),
            "missing_count": len(missing),
        },
        "witnesses": witnesses,
        "missing": missing,
        "plans_without_kept_action": plans_without_kept_action,
        "logic": {
            "replacement_rule": "N(b) subseteq N(a) within the same plan",
            "category_reason": "reduction removes active actions only; revoke category is a property of the original plan",
        },
        "errors": errors,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(
        json.dumps(
            {
                "status": payload["status"],
                "proof": payload["proof"],
                "removed": len(removed),
                "witnesses": len(witnesses),
                "output": str(args.output),
            },
            ensure_ascii=False,
        )
    )
    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
