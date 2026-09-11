#!/usr/bin/env python3
"""Solve D-Q2 with a finite-action exact 0-1 conflict-elimination model."""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from dataclasses import dataclass
from itertools import combinations
import json
from pathlib import Path

import numpy as np
from scipy.optimize import Bounds, LinearConstraint, milp
from scipy.sparse import coo_matrix, csr_matrix, vstack

from scripts.solve_q1 import expanded_events, read_plans


@dataclass(frozen=True)
class Candidate:
    plan_id: str
    category: str
    action: str
    df: int
    dt: int
    frequency: tuple[int, int] | None
    time: tuple[int, int] | None
    cells: frozenset[tuple[int, int]]


def build_candidates(plans: list[dict], horizon: int) -> list[Candidate]:
    candidates: list[Candidate] = []
    for plan in plans:
        plan_id = plan["id"]
        category = plan["category"]
        f0, f1 = plan["frequency"]
        t0, t1 = plan["time"]
        duration = t1 - t0
        events = expanded_events(plan)
        full_end = t1 + (plan["uses"] - 1) * (duration + plan["gap"])
        actions = []
        if t0 >= 0 and full_end <= horizon:
            actions.append(("keep", 0, 0))
        actions.extend(
            ("freq", df, 0)
            for df in range(-10, 11)
            if df != 0 and f0 + df >= 0 and f1 + df <= 100
            and full_end <= horizon
        )
        actions.extend(
            ("time", 0, dt)
            for dt in range(-5, 6)
            if dt != 0
            and t0 + dt >= 0
            and t1 + dt + (plan["uses"] - 1) * (duration + plan["gap"]) <= horizon
        )
        actions.append(("revoke", 0, 0))
        for action, df, dt in actions:
            if action == "revoke":
                candidates.append(Candidate(plan_id, category, action, df, dt, None, None, frozenset()))
                continue
            frequency = (f0 + df, f1 + df)
            time = (t0 + dt, t1 + dt)
            cells = frozenset(
                (time_index, frequency_index)
                for event_f0, event_f1, event_t0, event_t1 in events
                for time_index in range(event_t0 + dt, event_t1 + dt)
                for frequency_index in range(event_f0 + df, event_f1 + df)
            )
            candidates.append(Candidate(plan_id, category, action, df, dt, frequency, time, cells))
    return candidates


def build_choice_matrix(candidates: list[Candidate]) -> tuple[csr_matrix, np.ndarray, np.ndarray]:
    rows = []
    cols = []
    values = []
    lower = []
    upper = []
    plan_indexes: defaultdict[str, list[int]] = defaultdict(list)
    for index, candidate in enumerate(candidates):
        plan_indexes[candidate.plan_id].append(index)
    for row_index, indexes in enumerate(plan_indexes.values()):
        rows.extend([row_index] * len(indexes))
        cols.extend(indexes)
        values.extend([1.0] * len(indexes))
        lower.append(1.0)
        upper.append(1.0)
    choice_row_count = len(plan_indexes)
    matrix = coo_matrix(
        (values, (rows, cols)),
        shape=(choice_row_count, len(candidates)),
    ).tocsr()
    return matrix, np.asarray(lower), np.asarray(upper)


def find_selected_conflicts(candidates: list[Candidate], selected_indexes: list[int]) -> set[tuple[int, int]]:
    cell_candidates: defaultdict[tuple[int, int], list[int]] = defaultdict(list)
    for index in selected_indexes:
        for cell in candidates[index].cells:
            cell_candidates[cell].append(index)
    conflicts: set[tuple[int, int]] = set()
    for indexes in cell_candidates.values():
        for left, right in combinations(indexes, 2):
            if candidates[left].plan_id == candidates[right].plan_id:
                continue
            conflicts.add((min(left, right), max(left, right)))
    return conflicts


def feature_vectors(candidates: list[Candidate]) -> dict[str, np.ndarray]:
    return {
        "revoke": np.asarray([candidate.action == "revoke" for candidate in candidates], dtype=float),
        "adjust": np.asarray([candidate.action in {"freq", "time"} for candidate in candidates], dtype=float),
        "modified_A": np.asarray(
            [candidate.category == "A" and candidate.action != "keep" for candidate in candidates], dtype=float
        ),
        "modified_B": np.asarray(
            [candidate.category == "B" and candidate.action != "keep" for candidate in candidates], dtype=float
        ),
        "modified_C": np.asarray(
            [candidate.category == "C" and candidate.action != "keep" for candidate in candidates], dtype=float
        ),
        "shift": np.asarray([abs(candidate.df) + abs(candidate.dt) for candidate in candidates], dtype=float),
    }


def solve_stage(
    matrix: csr_matrix,
    lower: np.ndarray,
    upper: np.ndarray,
    objective: np.ndarray,
    fixed: list[tuple[np.ndarray, float]],
    cut_edges: set[tuple[int, int]],
    time_limit: float,
):
    cut_rows = []
    for left, right in sorted(cut_edges):
        row = np.zeros(objective.shape[0])
        row[left] = 1.0
        row[right] = 1.0
        cut_rows.append(row)
    if cut_rows:
        extra = csr_matrix(np.vstack(cut_rows))
        matrix = vstack([matrix, extra], format="csr")
        lower = np.concatenate([lower, np.full(len(cut_rows), -np.inf)])
        upper = np.concatenate([upper, np.ones(len(cut_rows))])
    if fixed:
        extra = csr_matrix(np.vstack([row for row, _ in fixed]))
        matrix = vstack([matrix, extra], format="csr")
        lower = np.concatenate([lower, np.asarray([value for _, value in fixed])])
        upper = np.concatenate([upper, np.asarray([value for _, value in fixed])])
    result = milp(
        c=objective,
        integrality=np.ones(objective.shape[0]),
        bounds=Bounds(np.zeros(objective.shape[0]), np.ones(objective.shape[0])),
        constraints=LinearConstraint(matrix, lower, upper),
        options={"time_limit": time_limit, "presolve": True},
    )
    return result


def metric_value(result, feature: np.ndarray) -> int:
    if result.x is None:
        raise RuntimeError(f"MILP returned no incumbent: status={result.status}, message={result.message}")
    return int(round(float(feature @ result.x)))


def run_lexicographic(
    candidates: list[Candidate],
    matrix: csr_matrix,
    lower: np.ndarray,
    upper: np.ndarray,
    objective_order: str,
    time_limit: float,
) -> tuple[object, dict, list[tuple[np.ndarray, float]], set[tuple[int, int]]]:
    features = feature_vectors(candidates)
    fixed: list[tuple[np.ndarray, float]] = []
    cut_edges: set[tuple[int, int]] = set()
    stages: list[dict] = []

    def solve_valid_stage(name: str, feature_name: str):
        nonlocal cut_edges
        iteration_count = 0
        added_cut_count = 0
        while True:
            result = solve_stage(matrix, lower, upper, features[feature_name], fixed, cut_edges, time_limit)
            iteration_count += 1
            if result.status != 0:
                raise RuntimeError(
                    f"Q2 stage {name} did not prove optimality: "
                    f"status={result.status}, message={result.message}"
                )
            selected_indexes = [index for index, value in enumerate(result.x) if value > 0.5]
            new_conflicts = find_selected_conflicts(candidates, selected_indexes) - cut_edges
            if not new_conflicts:
                break
            cut_edges.update(new_conflicts)
            added_cut_count += len(new_conflicts)
        record = {
            "name": name,
            "feature": feature_name,
            "status": int(result.status),
            "message": str(result.message),
            "objective": float(result.fun) if result.fun is not None else None,
            "mip_gap": float(getattr(result, "mip_gap", np.nan)),
            "constraint_generation_iterations": iteration_count,
            "new_conflict_cuts": added_cut_count,
        }
        return result, record

    def run(name: str, feature_name: str) -> int:
        nonlocal fixed
        result, record = solve_valid_stage(name, feature_name)
        stages.append(record)
        value = metric_value(result, features[feature_name])
        fixed.append((features[feature_name], value))
        record["optimal_value"] = value
        return value

    def run_final(name: str, feature_name: str):
        result, record = solve_valid_stage(name, feature_name)
        stages.append(record)
        record["optimal_value"] = metric_value(result, features[feature_name])
        return result

    revoke = run("minimum revocations", "revoke")
    if objective_order == "primary":
        adjusted = run("minimum adjusted plans", "adjust")
        modified_a = run("preserve A plans", "modified_A")
        modified_b = run("preserve B plans", "modified_B")
        final = run_final("minimum total absolute shift", "shift")
        values = {
            "revocations": revoke,
            "adjusted_plans": adjusted,
            "modified_A": modified_a,
            "modified_B": modified_b,
            "modified_C": metric_value(final, features["modified_C"]),
            "total_shift": metric_value(final, features["shift"]),
        }
        return final, {"stages": stages, "objective_values": values, "conflict_cut_count": len(cut_edges)}, fixed, cut_edges

    if objective_order == "priority_first":
        modified_a = run("preserve A plans", "modified_A")
        modified_b = run("preserve B plans", "modified_B")
        modified_c = run("preserve C plans", "modified_C")
        adjusted = run("minimum adjusted plans", "adjust")
        final = run_final("minimum total absolute shift", "shift")
        values = {
            "revocations": revoke,
            "adjusted_plans": adjusted,
            "modified_A": modified_a,
            "modified_B": modified_b,
            "modified_C": modified_c,
            "total_shift": metric_value(final, features["shift"]),
        }
        return final, {"stages": stages, "objective_values": values, "conflict_cut_count": len(cut_edges)}, fixed, cut_edges

    raise ValueError(f"unknown objective order: {objective_order}")


def format_interval(interval: tuple[int, int] | None) -> str | None:
    return None if interval is None else f"[{interval[0]},{interval[1]})"


def serialize_actions(candidates: list[Candidate], result) -> list[dict]:
    selected = [candidates[index] for index, value in enumerate(result.x) if value > 0.5]
    actions = []
    for candidate in sorted(selected, key=lambda item: item.plan_id):
        if candidate.action == "keep":
            continue
        actions.append(
            {
                "装备编号": candidate.plan_id,
                "类别": candidate.category,
                "动作": candidate.action,
                "频段区间": format_interval(candidate.frequency),
                "时间区间": format_interval(candidate.time),
                "频移": candidate.df,
                "时移": candidate.dt,
                "撤销": candidate.action == "revoke",
            }
        )
    return actions


def summarize_selected(plans: list[dict], candidates: list[Candidate], result) -> dict:
    by_id = {plan["id"]: plan for plan in plans}
    selected = [candidates[index] for index, value in enumerate(result.x) if value > 0.5]
    counts = {}
    for category in "ABC":
        total = sum(plan["category"] == category for plan in plans)
        cat_selected = [candidate for candidate in selected if candidate.category == category]
        revoked = sum(candidate.action == "revoke" for candidate in cat_selected)
        adjusted = sum(candidate.action in {"freq", "time"} for candidate in cat_selected)
        counts[category] = {
            "保留数量": total - revoked - adjusted,
            "调整数量": adjusted,
            "撤销数量": revoked,
        }
    used_cells = set()
    for candidate in selected:
        used_cells.update(candidate.cells)
    return {
        "plans": len(by_id),
        "selected_candidates": len(selected),
        "actions": serialize_actions(candidates, result),
        "counts_by_category": counts,
        "selected_unique_occupied_cell_count": len(used_cells),
        "selected_weighted_occupied_cell_count": sum(len(candidate.cells) for candidate in selected),
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=Path("data/raw/D题/附件/附件1.xlsx"))
    parser.add_argument("--output-dir", type=Path, default=Path("outputs/q2"))
    parser.add_argument("--horizon", type=int, default=643)
    parser.add_argument("--objective-order", choices=["primary", "priority_first"], default="primary")
    parser.add_argument("--time-limit", type=float, default=180.0)
    args = parser.parse_args()

    plans = read_plans(args.input)
    candidates = build_candidates(plans, args.horizon)
    matrix, lower, upper = build_choice_matrix(candidates)
    result, optimization, fixed, cut_edges = run_lexicographic(
        candidates, matrix, lower, upper, args.objective_order, args.time_limit
    )
    summary = summarize_selected(plans, candidates, result)
    output_dir = args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)
    data = {
        "question": "D-Q2",
        "status": "OPTIMAL",
        "objective_order": args.objective_order,
        "time_domain": [0, args.horizon],
        "frequency_domain": [0, 100],
        "rules": {
            "frequency_shift_limit": 10,
            "time_shift_limit": 5,
            "one_action_per_plan": True,
            "keep_duration_gap_and_uses": True,
            "half_open_intervals": True,
        },
        "candidate_count": len(candidates),
        "candidate_conflict_cut_count": len(cut_edges),
        "plan_count": len(plans),
        "optimization": optimization,
        "summary": summary,
        "validation": {
            "solver_status_all_stages_optimal": all(stage["status"] == 0 for stage in optimization["stages"]),
            "selected_one_candidate_per_plan": summary["selected_candidates"] == len(plans),
        },
    }
    (output_dir / "results.json").write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(
        json.dumps(
            {
                "status": data["status"],
                "objective_order": args.objective_order,
                "candidate_count": len(candidates),
                "candidate_conflict_edges": len(cut_edges),
                **optimization["objective_values"],
                "actions": len(summary["actions"]),
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
