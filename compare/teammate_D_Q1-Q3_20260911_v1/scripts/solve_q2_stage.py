#!/usr/bin/env python3
"""Run one full-conflict Q2 MILP stage with explicit fixed metric values."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
from scipy.optimize import Bounds, LinearConstraint, milp
from scipy.sparse import coo_matrix, vstack

from scripts.solve_q1 import read_plans
from scripts.solve_q2 import build_candidates, build_choice_matrix, feature_vectors, summarize_selected
from scripts.solve_q2_incumbent import build_conflict_edges, build_constraints


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=Path("data/raw/D题/附件/附件1.xlsx"))
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--horizon", type=int, default=643)
    parser.add_argument("--time-limit", type=float, default=180.0)
    parser.add_argument("--objective", choices=["revoke", "adjust", "modified_A", "modified_B", "modified_C", "shift"], required=True)
    parser.add_argument("--fixed-revocations", type=int)
    parser.add_argument("--fixed-adjusted", type=int)
    parser.add_argument("--fixed-modified-a", type=int)
    parser.add_argument("--fixed-modified-b", type=int)
    parser.add_argument("--fixed-modified-c", type=int)
    args = parser.parse_args()

    plans = read_plans(args.input)
    candidates = build_candidates(plans, args.horizon)
    choice_matrix, choice_lower, choice_upper = build_choice_matrix(candidates)
    edges = build_conflict_edges(candidates)
    matrix, lower, upper = build_constraints(choice_matrix, choice_lower, choice_upper, edges)
    features = feature_vectors(candidates)
    fixed_rows = []
    fixed_values = []
    requested = {
        "revoke": args.fixed_revocations,
        "adjust": args.fixed_adjusted,
        "modified_A": args.fixed_modified_a,
        "modified_B": args.fixed_modified_b,
        "modified_C": args.fixed_modified_c,
    }
    for name, value in requested.items():
        if value is not None:
            fixed_rows.append(features[name])
            fixed_values.append(value)
    if fixed_rows:
        matrix = vstack([matrix, coo_matrix(np.vstack(fixed_rows))], format="csr")
        lower = np.concatenate([lower, np.asarray(fixed_values, dtype=float)])
        upper = np.concatenate([upper, np.asarray(fixed_values, dtype=float)])

    result = milp(
        c=features[args.objective],
        integrality=np.ones(len(candidates)),
        bounds=Bounds(np.zeros(len(candidates)), np.ones(len(candidates))),
        constraints=LinearConstraint(matrix, lower, upper),
        options={"time_limit": args.time_limit, "presolve": True},
    )
    if result.x is None:
        raise RuntimeError(f"Q2 stage returned no incumbent: status={result.status}, message={result.message}")
    summary = summarize_selected(plans, candidates, result)
    payload = {
        "question": "D-Q2",
        "status": "OPTIMAL" if result.status == 0 else "FEASIBLE_INCUMBENT",
        "optimality": "PROVED" if result.status == 0 else "NOT_PROVED",
        "method": "full candidate-conflict MILP, single lexicographic stage",
        "objective": args.objective,
        "fixed_values": {name: value for name, value in requested.items() if value is not None},
        "time_domain": [0, args.horizon],
        "frequency_domain": [0, 100],
        "candidate_count": len(candidates),
        "candidate_conflict_edge_count": len(edges),
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
        "status": payload["status"],
        "objective": args.objective,
        "objective_value": payload["optimization"]["objective_value"],
        "mip_gap": payload["optimization"]["mip_gap"],
        "output": str(args.output),
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
