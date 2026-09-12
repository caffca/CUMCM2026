#!/usr/bin/env python3
"""Probe exact Q2 threshold feasibility under the central action model.

This script is deliberately a feasibility checker, not an optimizer.  A
threshold is reported as proved only when CP-SAT returns INFEASIBLE.  A
time-limited UNKNOWN result is preserved as unresolved rather than promoted
to a lower bound.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from ortools.sat.python import cp_model

from scripts.solve_q1 import read_plans
from scripts.solve_q2 import build_candidates
from scripts.solve_q2_cp_sat import (
    build_model,
    hint_from_result,
    selected_values,
    solver_status_name,
)


PROBES = {
    "b_le_3": {
        "description": "R=6, A类撤销=0, B类撤销<=3",
        "fixed": [("revoke", 6), ("revoke_A", 0)],
        "upper": ("revoke_B", 3),
    },
    "adjust_le_125": {
        "description": "R=6, A类撤销=0, B类撤销=4, 调整计划数<=125",
        "fixed": [("revoke", 6), ("revoke_A", 0), ("revoke_B", 4)],
        "upper": ("adjust", 125),
    },
    "shift_le_774": {
        "description": "R=6, A类撤销=0, B类撤销=4, M=126, M_A=16, M_B=34, S10<=774",
        "fixed": [
            ("revoke", 6),
            ("revoke_A", 0),
            ("revoke_B", 4),
            ("adjust", 126),
            ("adjust_A", 16),
            ("adjust_B", 34),
        ],
        "upper": ("normalized_shift", 774),
    },
}


def run_probe(
    plans: list[dict],
    horizon: int,
    probe_name: str,
    time_limit: float,
    workers: int,
    seed: int,
    hint_result: Path | None,
) -> dict:
    if probe_name not in PROBES:
        raise ValueError(f"unknown probe {probe_name!r}")
    candidates = build_candidates(plans, horizon)
    spec = PROBES[probe_name]
    model, variables, features, resource_rows = build_model(candidates, spec["fixed"])
    feature_name, upper_value = spec["upper"]
    model.add(sum(features[feature_name][i] * variables[i] for i in range(len(variables))) <= upper_value)

    hint = hint_from_result(candidates, hint_result) if hint_result else None
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
    status = solver.solve(model)
    status_name = solver_status_name(status)
    payload = {
        "question": "D-Q2",
        "probe": probe_name,
        "description": spec["description"],
        "horizon": horizon,
        "candidate_count": len(candidates),
        "resource_cell_constraint_count": resource_rows,
        "fixed_equalities": [{"feature": name, "value": value} for name, value in spec["fixed"]],
        "upper_bound": {"feature": feature_name, "value": upper_value},
        "status": status_name,
        "optimality": "PROVED_INFEASIBLE" if status_name == "INFEASIBLE" else (
            "FEASIBLE_WITNESS" if status_name in {"FEASIBLE", "OPTIMAL"} else "NOT_PROVED"
        ),
        "solver": {
            "time_limit_seconds": time_limit,
            "wall_time_seconds": solver.wall_time,
            "best_objective_bound": solver.best_objective_bound,
            "num_conflicts": solver.num_conflicts,
            "num_branches": solver.num_branches,
            "num_booleans": solver.num_booleans,
            "workers": workers,
            "seed": seed,
        },
    }
    values = selected_values(solver, variables, status)
    if values is not None:
        for name in ("revoke", "revoke_A", "revoke_B", "adjust", "adjust_A", "adjust_B", "modified_A", "modified_B", "modified_C"):
            payload.setdefault("incumbent", {})[name] = int(
                sum(features[name][i] * values[i] for i in range(len(values)))
            )
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=Path("data/raw/D题/附件/附件1.xlsx"))
    parser.add_argument("--probe", choices=sorted(PROBES), required=True)
    parser.add_argument("--horizon", type=int, default=643)
    parser.add_argument("--time-limit", type=float, default=600.0)
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--seed", type=int, default=20260923)
    parser.add_argument("--hint-result", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    plans = read_plans(args.input)
    payload = run_probe(plans, args.horizon, args.probe, args.time_limit, args.workers, args.seed, args.hint_result)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"probe": args.probe, "status": payload["status"], "optimality": payload["optimality"], "output": str(args.output)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
