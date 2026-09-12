#!/usr/bin/env python3
"""Independently validate a Q2 plan-adjustment result."""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
import json
from pathlib import Path
import re

from scripts.solve_q1 import read_plans


INTERVAL_RE = re.compile(r"\s*\[\s*(-?\d+)\s*,\s*(-?\d+)\s*\)\s*")


def parse_interval(value: str, field: str) -> tuple[int, int]:
    match = INTERVAL_RE.fullmatch(value or "")
    if not match:
        raise ValueError(f"invalid {field} interval: {value!r}")
    left, right = map(int, match.groups())
    if right <= left:
        raise ValueError(f"non-positive {field} interval: {value!r}")
    return left, right


def overlaps(left: tuple[int, int], right: tuple[int, int]) -> bool:
    return max(left[0], right[0]) < min(left[1], right[1])


def expanded(plan: dict) -> list[tuple[int, int, int, int]]:
    f0, f1 = plan["frequency"]
    t0, t1 = plan["time"]
    duration = t1 - t0
    step = duration + plan["gap"]
    return [
        (f0, f1, t0 + k * step, t1 + k * step)
        for k in range(plan["uses"])
    ]


def occupied_cells(events: list[tuple[int, int, int, int]]) -> set[tuple[int, int]]:
    return {
        (time, frequency)
        for f0, f1, t0, t1 in events
        for time in range(t0, t1)
        for frequency in range(f0, f1)
    }


def apply_actions(plans: list[dict], actions: list[dict]) -> tuple[list[dict], list[str]]:
    by_id = {plan["id"]: dict(plan) for plan in plans}
    errors: list[str] = []
    seen: set[str] = set()
    adjusted: list[dict] = []
    for row in actions:
        identifier = row.get("装备编号")
        if identifier in seen:
            errors.append(f"duplicate action for {identifier}")
            continue
        seen.add(identifier)
        if identifier not in by_id:
            errors.append(f"unknown equipment id {identifier}")
            continue
        plan = by_id[identifier]
        action = row.get("动作")
        if action not in {"freq", "time", "revoke"}:
            errors.append(f"unsupported action {action!r} for {identifier}")
            continue
        df = row.get("频移")
        dt = row.get("时移")
        if not isinstance(df, int) or not isinstance(dt, int):
            errors.append(f"non-integer shift for {identifier}")
            continue
        if action == "revoke":
            adjusted.append({**plan, "revoked": True})
            continue
        if action == "freq":
            if df == 0 or dt != 0:
                errors.append(f"frequency action must have df!=0 and dt=0 for {identifier}")
            if abs(df) > 10:
                errors.append(f"frequency shift exceeds 10 for {identifier}")
            frequency = parse_interval(row.get("频段区间"), "frequency")
            if frequency[1] - frequency[0] != plan["frequency"][1] - plan["frequency"][0]:
                errors.append(f"frequency width changed for {identifier}")
            if frequency != (plan["frequency"][0] + df, plan["frequency"][1] + df):
                errors.append(f"frequency interval does not match df for {identifier}")
            adjusted.append({**plan, "frequency": frequency, "revoked": False})
        else:
            if dt == 0 or df != 0:
                errors.append(f"time action must have dt!=0 and df=0 for {identifier}")
            if abs(dt) > 5:
                errors.append(f"time shift exceeds 5 for {identifier}")
            time = parse_interval(row.get("时间区间"), "time")
            if time[1] - time[0] != plan["time"][1] - plan["time"][0]:
                errors.append(f"time duration changed for {identifier}")
            if time != (plan["time"][0] + dt, plan["time"][1] + dt):
                errors.append(f"time interval does not match dt for {identifier}")
            adjusted.append({**plan, "time": time, "revoked": False})

    for identifier, plan in by_id.items():
        if identifier not in seen:
            adjusted.append({**plan, "revoked": False})
    return adjusted, errors


def check_conflicts(plans: list[dict], horizon: int) -> dict:
    active = [plan for plan in plans if not plan.get("revoked", False)]
    events = {plan["id"]: expanded(plan) for plan in active}
    boundary_errors = []
    for plan in active:
        for f0, f1, t0, t1 in events[plan["id"]]:
            if f0 < 0 or f1 > 100 or t0 < 0 or t1 > horizon:
                boundary_errors.append({"id": plan["id"], "event": [f0, f1, t0, t1]})

    continuous_pairs: set[tuple[str, str]] = set()
    for left_index, left in enumerate(active):
        for right in active[left_index + 1 :]:
            if any(
                overlaps((left_event[0], left_event[1]), (right_event[0], right_event[1]))
                and overlaps((left_event[2], left_event[3]), (right_event[2], right_event[3]))
                for left_event in events[left["id"]]
                for right_event in events[right["id"]]
            ):
                continuous_pairs.add(tuple(sorted((left["id"], right["id"]))))

    cell_owners: defaultdict[tuple[int, int], list[str]] = defaultdict(list)
    for plan in active:
        for cell in occupied_cells(events[plan["id"]]):
            cell_owners[cell].append(plan["id"])
    discrete_pairs = {
        tuple(sorted((owners[0], owners[1])))
        for owners in cell_owners.values()
        if len(owners) >= 2
        for i in range(len(owners))
        for j in range(i + 1, len(owners))
    }
    duplicate_cells = sum(1 for owners in cell_owners.values() if len(owners) > 1)
    max_occupancy = max((len(owners) for owners in cell_owners.values()), default=0)
    return {
        "active_plan_count": len(active),
        "continuous_conflict_pairs": sorted(continuous_pairs),
        "discrete_conflict_pairs": sorted(discrete_pairs),
        "boundary_errors": boundary_errors,
        "occupied_cell_count": len(cell_owners),
        "duplicate_occupied_cell_count": duplicate_cells,
        "max_cell_occupancy": max_occupancy,
        "weighted_occupied_cell_count": sum(len(occupied_cells(events[plan["id"]])) for plan in active),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=Path("data/raw/D题/附件/附件1.xlsx"))
    parser.add_argument("--result", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--horizon", type=int, default=643)
    args = parser.parse_args()

    plans = read_plans(args.input)
    result = json.loads(args.result.read_text(encoding="utf-8"))
    actions = result.get("summary", {}).get("actions", [])
    errors: list[str] = []
    try:
        adjusted, action_errors = apply_actions(plans, actions)
        errors.extend(action_errors)
        checks = check_conflicts(adjusted, args.horizon)
    except Exception as exc:
        errors.append(f"validator exception: {exc}")
        adjusted = []
        checks = {}

    counts = {}
    for category in "ABC":
        category_plans = [plan for plan in adjusted if plan["category"] == category]
        revoked = sum(plan.get("revoked", False) for plan in category_plans)
        modified = sum(
            plan.get("revoked", False)
            or plan["frequency"] != next(raw["frequency"] for raw in plans if raw["id"] == plan["id"])
            or plan["time"] != next(raw["time"] for raw in plans if raw["id"] == plan["id"])
            for plan in category_plans
        )
        counts[category] = {
            "保留数量": len(category_plans) - modified,
            "调整数量": modified - revoked,
            "撤销数量": revoked,
        }

    passed = (
        not errors
        and len(adjusted) == len(plans)
        and not checks.get("boundary_errors")
        and not checks.get("continuous_conflict_pairs")
        and checks.get("continuous_conflict_pairs") == checks.get("discrete_conflict_pairs")
    )
    payload = {
        "question": "D-Q2",
        "status": "PASS" if passed else "FAIL",
        "result_status": result.get("status"),
        "result_optimality": result.get("optimality", "UNSPECIFIED"),
        "horizon": args.horizon,
        "errors": errors,
        "counts_by_category": counts,
        "checks": checks,
        "claims_supported": {
            "all_plans_have_one_action_or_keep": len(adjusted) == len(plans) and not errors,
            "all_active_events_in_resource_domain": not checks.get("boundary_errors"),
            "continuous_conflict_free": not checks.get("continuous_conflict_pairs"),
            "independent_discrete_check_matches": checks.get("continuous_conflict_pairs") == checks.get("discrete_conflict_pairs"),
            "primary_objective_optimality_proved": result.get("optimality") in {
                "PROVED",
                "PRIMARY_OBJECTIVE_PROVED",
                "LEXICOGRAPHIC_PREFIX_PROVED",
            },
            "full_lexicographic_optimality_proved": result.get("optimality") == "PROVED",
        },
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"status": payload["status"], "errors": len(errors), "output": str(args.output)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
