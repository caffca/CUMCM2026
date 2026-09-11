#!/usr/bin/env python3
"""Find and save a Q2 minimum-revocation incumbent without claiming optimality."""
from __future__ import annotations

import argparse
from collections import defaultdict
from itertools import combinations
import json
from pathlib import Path

import numpy as np
from scipy.optimize import Bounds, LinearConstraint, milp
from scipy.sparse import coo_matrix, vstack

from scripts.solve_q1 import read_plans
from scripts.solve_q2 import build_candidates, build_choice_matrix, summarize_selected


def build_conflict_edges(candidates):
    by_cell = defaultdict(list)
    for index, candidate in enumerate(candidates):
        for cell in candidate.cells:
            by_cell[cell].append(index)
    edges = set()
    for indexes in by_cell.values():
        for left, right in combinations(indexes, 2):
            if candidates[left].plan_id != candidates[right].plan_id:
                edges.add((min(left, right), max(left, right)))
    return sorted(edges)


def build_constraints(choice_matrix, choice_lower, choice_upper, edges):
    if not edges:
        return choice_matrix, choice_lower, choice_upper
    rows = np.repeat(np.arange(len(edges)), 2)
    cols = np.asarray(edges, dtype=int).reshape(-1)
    values = np.ones(len(cols), dtype=float)
    conflict_matrix = coo_matrix(
        (values, (rows, cols)), shape=(len(edges), choice_matrix.shape[1])
    ).tocsr()
    matrix = vstack([choice_matrix, conflict_matrix], format="csr")
    lower = np.concatenate([choice_lower, np.full(len(edges), -np.inf)])
    upper = np.concatenate([choice_upper, np.ones(len(edges))])
    return matrix, lower, upper


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=Path("data/raw/D题/附件/附件1.xlsx"))
    parser.add_argument("--output", type=Path, default=Path("tmp/q2_full_incumbent.json"))
    parser.add_argument("--horizon", type=int, default=643)
    parser.add_argument("--time-limit", type=float, default=180.0)
    args = parser.parse_args()

    plans = read_plans(args.input)
    candidates = build_candidates(plans, args.horizon)
    choice_matrix, choice_lower, choice_upper = build_choice_matrix(candidates)
    edges = build_conflict_edges(candidates)
    matrix, lower, upper = build_constraints(choice_matrix, choice_lower, choice_upper, edges)
    objective = np.asarray([candidate.action == "revoke" for candidate in candidates], dtype=float)
    result = milp(
        c=objective,
        integrality=np.ones(len(candidates)),
        bounds=Bounds(np.zeros(len(candidates)), np.ones(len(candidates))),
        constraints=LinearConstraint(matrix, lower, upper),
        options={"time_limit": args.time_limit, "presolve": True},
    )
    if result.x is None:
        raise RuntimeError(f"Q2 MILP returned no incumbent: status={result.status}, message={result.message}")
    summary = summarize_selected(plans, candidates, result)
    status = "OPTIMAL" if result.status == 0 else "FEASIBLE_INCUMBENT"
    payload = {
        "question": "D-Q2",
        "status": status,
        "optimality": "PROVED" if result.status == 0 else "NOT_PROVED",
        "method": "full candidate-conflict MILP, minimum revocations stage",
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
        "candidate_conflict_edge_count": len(edges),
        "plan_count": len(plans),
        "optimization": {
            "solver_status": int(result.status),
            "solver_message": str(result.message),
            "objective_value": float(result.fun) if result.fun is not None else None,
            "mip_gap": float(getattr(result, "mip_gap", np.nan)),
            "time_limit_seconds": args.time_limit,
        },
        "summary": summary,
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({
        "status": status,
        "solver_status": int(result.status),
        "objective_value": payload["optimization"]["objective_value"],
        "mip_gap": payload["optimization"]["mip_gap"],
        "candidate_count": len(candidates),
        "candidate_conflict_edges": len(edges),
        "actions": len(summary["actions"]),
        "output": str(args.output),
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
