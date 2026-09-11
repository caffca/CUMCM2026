#!/usr/bin/env python3
"""Q2 exact candidate-action solver using OR-Tools CP-SAT.

The model keeps one candidate action for every original plan and enforces
at-most-one ownership for every occupied discrete time-frequency cell.  The
cell-clique formulation is equivalent to the pairwise conflict formulation
for the integer candidate variables, while usually giving the solver a
stronger resource constraint.

This script is intentionally separate from the historical SciPy incumbent
solver.  It records solver status and bounds explicitly, so a time-limited
incumbent is never presented as a proof of optimality.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
import json
from pathlib import Path
from typing import Iterable

from ortools.sat.python import cp_model

from scripts.solve_q1 import read_plans
from scripts.solve_q2 import Candidate, build_candidates, summarize_selected


SCHEMES: dict[str, list[str]] = {
    # Closest to the order in the statement: revoke, adjust, preserve classes,
    # then reduce the movement amplitude.
    "wording": ["revoke", "adjust", "modified_A", "modified_B", "modified_C", "shift"],
    # Priority-first sensitivity: after the number of revocations, protect
    # A/B/C plans before minimizing the total number of adjusted plans.
    "priority_first": ["revoke", "modified_A", "modified_B", "modified_C", "adjust", "shift"],
    # A deliberately disclosed weighted compromise, not an official rule.
    # It allows a small amount of A/B/C trade-off instead of treating the
    # class order as a strict lexicographic chain.
    "weighted_compromise": ["revoke", "adjust", "weighted_class_damage", "shift"],
    # Main interpretation for the repaired Q2 milestone. Class protection is
    # applied separately to revocations and parameter adjustments.
    "priority_protected": [
        "revoke",
        "revoke_A",
        "revoke_B",
        "adjust",
        "adjust_A",
        "adjust_B",
        "normalized_shift",
    ],
}


def feature_vectors(candidates: list[Candidate]) -> dict[str, list[int]]:
    return {
        "revoke": [int(c.action == "revoke") for c in candidates],
        "adjust": [int(c.action in {"freq", "time"}) for c in candidates],
        "modified_A": [int(c.category == "A" and c.action != "keep") for c in candidates],
        "modified_B": [int(c.category == "B" and c.action != "keep") for c in candidates],
        "modified_C": [int(c.category == "C" and c.action != "keep") for c in candidates],
        "shift": [abs(c.df) + abs(c.dt) for c in candidates],
        # Ten times the dimensionless cost |df|/10 + |dt|/5.
        "normalized_shift": [abs(c.df) + 2 * abs(c.dt) for c in candidates],
        "revoke_A": [int(c.category == "A" and c.action == "revoke") for c in candidates],
        "revoke_B": [int(c.category == "B" and c.action == "revoke") for c in candidates],
        "adjust_A": [int(c.category == "A" and c.action in {"freq", "time"}) for c in candidates],
        "adjust_B": [int(c.category == "B" and c.action in {"freq", "time"}) for c in candidates],
        # Sensitivity-only compromise.  The weights are intentionally much
        # closer than lexicographic big-M weights.
        "weighted_class_damage": [
            100 * int(c.category == "A" and c.action != "keep")
            + 10 * int(c.category == "B" and c.action != "keep")
            + int(c.category == "C" and c.action != "keep")
            for c in candidates
        ],
    }


def build_model(
    candidates: list[Candidate],
    fixed: Iterable[tuple[str, int]],
    max_revocations: int | None = None,
) -> tuple[cp_model.CpModel, list[cp_model.IntVar], dict[str, list[int]], int]:
    model = cp_model.CpModel()
    variables = [model.new_bool_var(f"x_{i}") for i in range(len(candidates))]
    features = feature_vectors(candidates)

    by_plan: defaultdict[str, list[int]] = defaultdict(list)
    by_cell: defaultdict[tuple[int, int], list[int]] = defaultdict(list)
    for index, candidate in enumerate(candidates):
        by_plan[candidate.plan_id].append(index)
        for cell in candidate.cells:
            by_cell[cell].append(index)

    for indexes in by_plan.values():
        model.add(sum(variables[index] for index in indexes) == 1)

    resource_row_count = 0
    for indexes in by_cell.values():
        # A cell occupied by only one candidate produces no useful constraint.
        if len(indexes) >= 2:
            model.add(sum(variables[index] for index in indexes) <= 1)
            resource_row_count += 1

    for feature_name, value in fixed:
        model.add(sum(features[feature_name][i] * variables[i] for i in range(len(variables))) == value)

    if max_revocations is not None:
        model.add(sum(features["revoke"][i] * variables[i] for i in range(len(variables))) <= max_revocations)

    return model, variables, features, resource_row_count


def solver_status_name(status: cp_model.CpSolverStatus) -> str:
    if isinstance(status, str):
        return status
    return {
        cp_model.OPTIMAL: "OPTIMAL",
        cp_model.FEASIBLE: "FEASIBLE",
        cp_model.INFEASIBLE: "INFEASIBLE",
        cp_model.MODEL_INVALID: "MODEL_INVALID",
        cp_model.UNKNOWN: "UNKNOWN",
    }.get(status, str(status))


def solve_once(
    candidates: list[Candidate],
    fixed: list[tuple[str, int]],
    objective_name: str | None,
    time_limit: float,
    workers: int,
    seed: int,
    max_revocations: int | None = None,
    hint: list[int] | None = None,
) -> tuple[cp_model.CpSolver, cp_model.CpModel, list[cp_model.IntVar], dict[str, list[int]], int, object]:
    model, variables, features, resource_rows = build_model(candidates, fixed, max_revocations)
    if objective_name is not None:
        model.minimize(sum(features[objective_name][i] * variables[i] for i in range(len(variables))))
    if hint is not None:
        for variable, value in zip(variables, hint):
            model.add_hint(variable, int(value))

    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = time_limit
    solver.parameters.num_search_workers = workers
    solver.parameters.random_seed = seed
    solver.parameters.log_search_progress = False
    solver.parameters.cp_model_presolve = True
    solver.parameters.linearization_level = 2
    solver.parameters.symmetry_level = 2
    cp_status = solver.solve(model)
    return solver, model, variables, features, resource_rows, cp_status


def selected_values(solver: cp_model.CpSolver, variables: list[cp_model.IntVar], cp_status: object) -> list[int] | None:
    status = solver.status_name(cp_status)
    if status not in {"OPTIMAL", "FEASIBLE"}:
        return None
    return [int(solver.value(variable)) for variable in variables]


def cp_result_as_scipy_like(candidates: list[Candidate], values: list[int]):
    """Small adapter for the existing summary serializer."""

    class Result:
        x = values

    return Result()


def hint_from_result(
    candidates: list[Candidate],
    result_path: Path | None,
    boundary_repair: bool = False,
) -> list[int] | None:
    """Convert a serialized selected-action result into candidate hints."""
    if result_path is None:
        return None
    payload = json.loads(result_path.read_text(encoding="utf-8"))
    actions = {row["装备编号"]: row for row in payload.get("summary", {}).get("actions", [])}
    if boundary_repair:
        # C083 and C088 are the only raw plans with terminal events at or
        # beyond H=638.  A time shift of -5 is legal and repairs the hint
        # without changing the model's one-action rule.
        for identifier in ("C083", "C088"):
            row = actions.get(identifier)
            if row is not None and row.get("动作") != "revoke":
                actions[identifier] = {"动作": "time", "频移": 0, "时移": -5}
    values: list[int] = []
    for candidate in candidates:
        row = actions.get(candidate.plan_id)
        if row is None:
            values.append(int(candidate.action == "keep"))
            continue
        action = row.get("动作")
        values.append(
            int(
                (action == "revoke" and candidate.action == "revoke")
                or (
                    action in {"freq", "time"}
                    and candidate.action == action
                    and candidate.df == int(row.get("频移", 0))
                    and candidate.dt == int(row.get("时移", 0))
                )
            )
        )
    return values


def summarize_solver(
    solver: cp_model.CpSolver,
    objective_name: str | None,
    status: str,
    cp_status: object,
    time_limit: float,
) -> dict:
    record = {
        "status": status,
        "solver_status": solver.status_name(cp_status),
        "solver_message": status,
        "time_limit_seconds": time_limit,
        "wall_time_seconds": solver.wall_time,
        "user_time_seconds": solver.user_time,
        "objective": objective_name,
        "objective_value": float(solver.objective_value) if objective_name is not None and status in {"OPTIMAL", "FEASIBLE"} else None,
        "best_objective_bound": float(solver.best_objective_bound) if objective_name is not None else None,
        "num_conflicts": solver.num_conflicts,
        "num_branches": solver.num_branches,
        "num_booleans": solver.num_booleans,
    }
    if objective_name is not None and status == "OPTIMAL":
        record["optimality"] = "PROVED"
    elif status == "FEASIBLE":
        record["optimality"] = "NOT_PROVED"
    else:
        record["optimality"] = "NOT_APPLICABLE"
    return record


def run_chain(
    plans: list[dict],
    candidates: list[Candidate],
    scheme: str,
    time_limit: float,
    workers: int,
    seed: int,
    known_revocations_record: dict | None = None,
    initial_hint: list[int] | None = None,
    allow_conditional_chain: bool = False,
) -> dict:
    fixed: list[tuple[str, int]] = []
    stages: list[dict] = []
    hint: list[int] | None = initial_hint
    final_values: list[int] | None = None
    resource_rows = None
    objective_order = SCHEMES[scheme]
    if known_revocations_record is not None:
        known_revocations = int(known_revocations_record["value"])
        fixed.append(("revoke", known_revocations))
        stages.append({
            "status": "PROVED_BY_REFERENCED_RUN",
            "solver_status": "OPTIMAL",
            "solver_message": "A validated CP-SAT run established matching lower and upper bounds.",
            "time_limit_seconds": 0.0,
            "wall_time_seconds": 0.0,
            "user_time_seconds": 0.0,
            "objective": "revoke",
            "objective_value": float(known_revocations),
            "best_objective_bound": float(known_revocations),
            "incumbent_value": known_revocations,
            "optimality": "PROVED",
            "evidence": known_revocations_record["path"],
        })
        objective_order = objective_order[1:]
    for stage_index, objective_name in enumerate(objective_order):
        solver, _, variables, features, resource_rows, cp_status = solve_once(
            candidates,
            fixed,
            objective_name,
            time_limit,
            workers,
            seed + stage_index,
            hint=hint,
        )
        status = solver_status_name(cp_status)
        values = selected_values(solver, variables, cp_status)
        record = summarize_solver(solver, objective_name, status, cp_status, time_limit)
        if values is None:
            stages.append(record)
            break
        value = int(sum(features[objective_name][i] * values[i] for i in range(len(values))))
        record["incumbent_value"] = value
        stages.append(record)
        hint = values
        final_values = values
        if record["optimality"] != "PROVED" and not allow_conditional_chain:
            # Milestone gate: do not optimize later objectives on top of an
            # unproved incumbent for an earlier lexicographic layer.
            break
        fixed.append((objective_name, value))

    if final_values is None:
        raise RuntimeError(f"Q2 CP-SAT chain produced no feasible incumbent for scheme={scheme}")
    summary = summarize_selected(plans, candidates, cp_result_as_scipy_like(candidates, final_values))
    values_by_feature = feature_vectors(candidates)
    objective_values = {
        name: int(sum(values_by_feature[name][i] * final_values[i] for i in range(len(final_values))))
        for name in [
            "revoke", "revoke_A", "revoke_B", "adjust", "adjust_A", "adjust_B",
            "modified_A", "modified_B", "modified_C", "shift", "normalized_shift",
            "weighted_class_damage",
        ]
    }
    return {
        "question": "D-Q2",
        "status": "OPTIMAL" if all(stage["optimality"] == "PROVED" for stage in stages) else "FEASIBLE_INCUMBENT",
        "optimality": "PROVED" if all(stage["optimality"] == "PROVED" for stage in stages) else "NOT_PROVED",
        "method": "OR-Tools CP-SAT + candidate-action enumeration + resource-cell clique constraints",
        "scheme": scheme,
        "objective_order": SCHEMES[scheme],
        "objective_interpretation": {
            "wording": "按题面语序：撤销数、参数调整计划数、A/B/C 类未保持计划数、总平移幅度。",
            "priority_first": "撤销数固定后，先保护 A、B、C 类，再最小化参数调整计划数和总平移幅度。",
            "priority_protected": "精炼方案 B：先最少撤销，再依次最少 A/B 类撤销；随后最少参数调整，再依次最少 A/B 类调整；最后最小化归一化平移幅度 |df|/10+|dt|/5。",
            "weighted_compromise": "撤销数和调整计划数固定后，以 100:10:1 的 A:B:C 未保持计划损失作敏感性折中；权重为分析者设定，不是题面原生权重。",
        }[scheme],
        "time_domain": [0, max((0, max((c.time[1] + (0 if c.time is None else 0)) if c.time else 0 for c in candidates)), default=0)],
        "frequency_domain": [0, 100],
        "rules": {
            "frequency_shift_limit": 10,
            "time_shift_limit": 5,
            "one_action_per_plan": True,
            "keep_duration_gap_and_uses": True,
            "half_open_intervals": True,
        },
        "candidate_count": len(candidates),
        "resource_cell_constraint_count": resource_rows,
        "plan_count": summary["plans"],
        "optimization": {
            "stages": stages,
            "fixed_values": [{"feature": name, "value": value} for name, value in fixed],
            "objective_values": objective_values,
            "workers": workers,
            "seed": seed,
            "stage_time_limit_seconds": time_limit,
        },
        "summary": summary,
    }


def run_feasibility(
    plans: list[dict],
    candidates: list[Candidate],
    max_revocations: int,
    time_limit: float,
    workers: int,
    seed: int,
    initial_hint: list[int] | None = None,
) -> dict:
    solver, _, variables, features, resource_rows, cp_status = solve_once(
        candidates,
        [],
        "revoke",
        time_limit,
        workers,
        seed,
        max_revocations=max_revocations,
        hint=initial_hint,
    )
    status = solver_status_name(cp_status)
    values = selected_values(solver, variables, cp_status)
    payload = {
        "question": "D-Q2",
        "mode": "feasibility",
        "max_revocations": max_revocations,
        "status": status,
        "optimality": "PROVED_INFEASIBLE" if status == "INFEASIBLE" else ("PROVED" if status == "OPTIMAL" else "NOT_PROVED"),
        "method": "OR-Tools CP-SAT + resource-cell clique constraints",
        "candidate_count": len(candidates),
        "resource_cell_constraint_count": resource_rows,
        "time_domain": None,
        "frequency_domain": [0, 100],
        "optimization": summarize_solver(solver, "revoke", status, cp_status, time_limit),
    }
    if values is not None:
        summary = summarize_selected(plans, candidates, cp_result_as_scipy_like(candidates, values))
        payload["summary"] = summary
        payload["found_revocations"] = int(sum(features["revoke"][i] * values[i] for i in range(len(values))))
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=Path("data/raw/D题/附件/附件1.xlsx"))
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--horizon", type=int, default=643)
    parser.add_argument("--scheme", choices=sorted(SCHEMES), default="wording")
    parser.add_argument("--mode", choices=["chain", "feasibility"], default="chain")
    parser.add_argument("--max-revocations", type=int, default=6)
    parser.add_argument("--stage-time-limit", type=float, default=120.0)
    parser.add_argument("--time-limit", type=float, default=300.0)
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--seed", type=int, default=20260911)
    parser.add_argument("--known-revocations", type=int)
    parser.add_argument("--known-revocations-evidence", type=Path)
    parser.add_argument("--allow-conditional-chain", action="store_true")
    parser.add_argument("--hint-result", type=Path)
    parser.add_argument("--boundary-repair-hint", action="store_true")
    args = parser.parse_args()

    plans = read_plans(args.input)
    candidates = build_candidates(plans, args.horizon)
    if args.mode == "feasibility":
        payload = run_feasibility(
            plans,
            candidates,
            args.max_revocations,
            args.time_limit,
            args.workers,
            args.seed,
            initial_hint=hint_from_result(candidates, args.hint_result, args.boundary_repair_hint),
        )
        payload["time_domain"] = [0, args.horizon]
    else:
        known_revocations_record = None
        if args.known_revocations is not None:
            if args.known_revocations_evidence is None:
                parser.error("--known-revocations requires --known-revocations-evidence")
            evidence = json.loads(args.known_revocations_evidence.read_text(encoding="utf-8"))
            optimization = evidence.get("optimization", {})
            expected_domain = [0, args.horizon]
            valid_evidence = (
                evidence.get("status") == "OPTIMAL"
                and evidence.get("optimality") == "PROVED"
                and evidence.get("candidate_count") == len(candidates)
                and evidence.get("time_domain") == expected_domain
                and evidence.get("found_revocations") == args.known_revocations
                and optimization.get("objective") == "revoke"
                and optimization.get("objective_value") == args.known_revocations
                and optimization.get("best_objective_bound") == args.known_revocations
            )
            if not valid_evidence:
                raise ValueError("known-revocations evidence does not certify the requested value for this model")
            known_revocations_record = {
                "value": args.known_revocations,
                "path": str(args.known_revocations_evidence),
            }
        payload = run_chain(
            plans,
            candidates,
            args.scheme,
            args.stage_time_limit,
            args.workers,
            args.seed,
            known_revocations_record=known_revocations_record,
            initial_hint=hint_from_result(candidates, args.hint_result, args.boundary_repair_hint),
            allow_conditional_chain=args.allow_conditional_chain,
        )
        payload["time_domain"] = [0, args.horizon]
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({
        "status": payload["status"],
        "optimality": payload["optimality"],
        "mode": args.mode,
        "scheme": args.scheme if args.mode == "chain" else None,
        "horizon": args.horizon,
        "output": str(args.output),
        "objective_values": payload.get("optimization", {}).get("objective_values"),
        "found_revocations": payload.get("found_revocations"),
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
