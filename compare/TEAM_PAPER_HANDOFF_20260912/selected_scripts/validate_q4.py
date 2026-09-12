#!/usr/bin/env python3
"""Independently reconstruct and validate a D-Q4 candidate solution."""
from __future__ import annotations

import argparse
from collections import defaultdict
import json
from pathlib import Path

from scripts.solve_q1 import read_plans


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


def apply_actions(plans: list[dict], actions: list[dict]) -> tuple[list[dict], list[str]]:
    raw = {plan["id"]: dict(plan) for plan in plans}
    action_map = {row.get("装备编号"): row for row in actions}
    errors = []
    if len(action_map) != len(actions):
        errors.append("duplicate equipment identifiers in actions")
    unknown = sorted(set(action_map) - set(raw))
    if unknown:
        errors.append(f"unknown equipment identifiers: {unknown}")

    adjusted = []
    for identifier, plan in raw.items():
        row = action_map.get(identifier)
        if row is None:
            adjusted.append({**plan, "action": "keep", "revoked": False})
            continue
        action = row.get("动作")
        df = row.get("频移", 0)
        dt = row.get("时移", 0)
        dg = row.get("间隔变化", 0)
        if action not in {"freq", "time", "gap", "revoke"}:
            errors.append(f"unsupported action for {identifier}: {action}")
            continue
        if not all(isinstance(value, int) for value in (df, dt, dg)):
            errors.append(f"non-integer action delta for {identifier}")
            continue
        changed = sum(value != 0 for value in (df, dt, dg))
        if action == "revoke":
            if changed:
                errors.append(f"revoked plan has nonzero delta: {identifier}")
            adjusted.append({**plan, "action": action, "revoked": True})
            continue
        if changed != 1:
            errors.append(f"adjustment must change exactly one parameter: {identifier}")
        if action == "freq" and not (df != 0 and dt == 0 and dg == 0 and abs(df) <= 10):
            errors.append(f"invalid frequency action: {identifier}")
        if action == "time" and not (dt != 0 and df == 0 and dg == 0 and abs(dt) <= 5):
            errors.append(f"invalid time action: {identifier}")
        if action == "gap" and not (
            plan["category"] == "C" and dg != 0 and df == 0 and dt == 0 and abs(dg) <= 10
        ):
            errors.append(f"invalid gap action: {identifier}")

        new_plan = {
            **plan,
            "frequency": (plan["frequency"][0] + df, plan["frequency"][1] + df),
            "time": (plan["time"][0] + dt, plan["time"][1] + dt),
            "gap": plan["gap"] + dg,
            "action": action,
            "revoked": False,
        }
        if new_plan["gap"] < 0:
            errors.append(f"negative gap: {identifier}")
        if row.get("调整后间隔") != new_plan["gap"]:
            errors.append(f"serialized gap mismatch: {identifier}")
        adjusted.append(new_plan)
    return adjusted, errors


def validate_events(plans: list[dict], horizon: int) -> dict:
    active = [plan for plan in plans if not plan["revoked"]]
    events = {plan["id"]: expanded(plan) for plan in active}
    boundary_errors = []
    for plan in active:
        for event in events[plan["id"]]:
            f0, f1, t0, t1 = event
            if not (0 <= f0 < f1 <= 100 and 0 <= t0 < t1 <= horizon):
                boundary_errors.append({"id": plan["id"], "event": list(event)})

    continuous_pairs = set()
    for left_index, left in enumerate(active):
        for right in active[left_index + 1 :]:
            if any(
                overlaps((a[0], a[1]), (b[0], b[1]))
                and overlaps((a[2], a[3]), (b[2], b[3]))
                for a in events[left["id"]]
                for b in events[right["id"]]
            ):
                continuous_pairs.add(tuple(sorted((left["id"], right["id"]))))

    owners: defaultdict[tuple[int, int], list[str]] = defaultdict(list)
    weighted_cells = 0
    for plan in active:
        plan_cells = {
            (time_index, frequency_index)
            for f0, f1, t0, t1 in events[plan["id"]]
            for time_index in range(t0, t1)
            for frequency_index in range(f0, f1)
        }
        weighted_cells += len(plan_cells)
        for cell in plan_cells:
            owners[cell].append(plan["id"])
    discrete_pairs = {
        tuple(sorted((ids[i], ids[j])))
        for ids in owners.values()
        for i in range(len(ids))
        for j in range(i + 1, len(ids))
    }
    return {
        "active_plan_count": len(active),
        "boundary_errors": boundary_errors,
        "continuous_conflict_pairs": sorted(continuous_pairs),
        "discrete_conflict_pairs": sorted(discrete_pairs),
        "unique_occupied_cell_count": len(owners),
        "weighted_occupied_cell_count": weighted_cells,
        "duplicate_occupied_cell_count": sum(len(ids) > 1 for ids in owners.values()),
        "max_cell_occupancy": max((len(ids) for ids in owners.values()), default=0),
    }


def recompute_objectives(adjusted: list[dict], raw: list[dict]) -> dict:
    raw_by_id = {plan["id"]: plan for plan in raw}
    return {
        "revoke": sum(plan["revoked"] for plan in adjusted),
        "revoke_A": sum(plan["revoked"] and plan["category"] == "A" for plan in adjusted),
        "revoke_B": sum(plan["revoked"] and plan["category"] == "B" for plan in adjusted),
        "adjust": sum(plan["action"] in {"freq", "time", "gap"} for plan in adjusted),
        "adjust_A": sum(plan["action"] in {"freq", "time", "gap"} and plan["category"] == "A" for plan in adjusted),
        "adjust_B": sum(plan["action"] in {"freq", "time", "gap"} and plan["category"] == "B" for plan in adjusted),
        "normalized_shift": sum(
            abs(plan["frequency"][0] - raw_by_id[plan["id"]]["frequency"][0])
            + 2 * abs(plan["time"][0] - raw_by_id[plan["id"]]["time"][0])
            + abs(plan["gap"] - raw_by_id[plan["id"]]["gap"])
            for plan in adjusted
            if not plan["revoked"]
        ),
    }


def category_counts(adjusted: list[dict]) -> dict:
    counts = {}
    for category in "ABC":
        rows = [plan for plan in adjusted if plan["category"] == category]
        counts[category] = {
            "保留数量": sum(plan["action"] == "keep" for plan in rows),
            "调整数量": sum(plan["action"] in {"freq", "time", "gap"} for plan in rows),
            "撤销数量": sum(plan["revoked"] for plan in rows),
        }
    return counts


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=Path("data/raw/D题/附件/附件1.xlsx"))
    parser.add_argument("--result", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--horizon", type=int, default=643)
    args = parser.parse_args()

    raw = read_plans(args.input)
    result = json.loads(args.result.read_text(encoding="utf-8"))
    if not result.get("summary"):
        payload = {
            "question": "D-Q4",
            "status": "NOT_APPLICABLE",
            "horizon": args.horizon,
            "reason": "The solver result has no candidate summary, so there is no solution to reconstruct.",
            "solver_status": result.get("status"),
            "errors": [],
        }
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        print(json.dumps({"status": payload["status"], "errors": [], "output": str(args.output)}, ensure_ascii=False))
        return
    actions = (result.get("summary") or {}).get("actions", [])
    adjusted, errors = apply_actions(raw, actions)
    checks = validate_events(adjusted, args.horizon) if len(adjusted) == len(raw) else {}
    objectives = recompute_objectives(adjusted, raw) if len(adjusted) == len(raw) else {}
    reported = result.get("optimization", {}).get("objective_values") or {}
    counts = category_counts(adjusted) if len(adjusted) == len(raw) else {}
    objective_match = (
        all(reported.get(name) == value for name, value in objectives.items())
        if reported
        else None
    )
    passed = (
        not errors
        and len(adjusted) == 150
        and not checks["boundary_errors"]
        and not checks["continuous_conflict_pairs"]
        and checks["continuous_conflict_pairs"] == checks["discrete_conflict_pairs"]
        and objective_match is not False
        and counts == result.get("summary", {}).get("counts_by_category")
    )
    payload = {
        "question": "D-Q4",
        "status": "PASS" if passed else "FAIL",
        "horizon": args.horizon,
        "errors": errors,
        "recomputed_objectives": objectives,
        "reported_objectives": reported,
        "objective_values_match": objective_match,
        "counts_by_category": counts,
        "checks": checks,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"status": payload["status"], "errors": errors, "output": str(args.output)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
