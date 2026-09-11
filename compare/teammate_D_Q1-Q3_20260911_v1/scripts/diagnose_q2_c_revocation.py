#!/usr/bin/env python3
"""Diagnose whether Q2's zero C-class revocations are forced by the model.

This is an evidence probe only.  It does not change the Q2 incumbent and does
not read or optimize any Q3 quantity.  By default it fixes the total number of
revocations to the current incumbent value and asks for at least one revoked C
class plan, then minimizes the number of adjusted plans among those solutions.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import numpy as np
from scipy.optimize import Bounds, LinearConstraint, milp
from scipy.sparse import coo_matrix, vstack

from scripts.solve_q1 import read_plans
from scripts.solve_q2 import (
    build_candidates,
    build_choice_matrix,
    feature_vectors,
    summarize_selected,
)
from scripts.solve_q2_incumbent import build_conflict_edges, build_constraints


def append_rows(matrix, lower, upper, rows, row_lower, row_upper):
    if not rows:
        return matrix, lower, upper
    extra = coo_matrix(np.vstack(rows))
    return (
        vstack([matrix, extra], format="csr"),
        np.concatenate([lower, np.asarray(row_lower, dtype=float)]),
        np.concatenate([upper, np.asarray(row_upper, dtype=float)]),
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=Path("data/raw/D题/附件/附件1.xlsx"))
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--horizon", type=int, default=643)
    parser.add_argument("--fixed-total-revocations", type=int, default=19)
    parser.add_argument("--minimum-c-revocations", type=int, default=1)
    parser.add_argument("--time-limit", type=float, default=180.0)
    args = parser.parse_args()

    plans = read_plans(args.input)
    candidates = build_candidates(plans, args.horizon)
    choice_matrix, choice_lower, choice_upper = build_choice_matrix(candidates)
    edges = build_conflict_edges(candidates)
    matrix, lower, upper = build_constraints(
        choice_matrix, choice_lower, choice_upper, edges
    )
    features = feature_vectors(candidates)
    c_revoke = np.asarray(
        [candidate.category == "C" and candidate.action == "revoke" for candidate in candidates],
        dtype=float,
    )
    matrix, lower, upper = append_rows(
        matrix,
        lower,
        upper,
        [features["revoke"], c_revoke],
        [args.fixed_total_revocations, args.minimum_c_revocations],
        [args.fixed_total_revocations, np.inf],
    )

    result = milp(
        c=features["adjust"],
        integrality=np.ones(len(candidates)),
        bounds=Bounds(np.zeros(len(candidates)), np.ones(len(candidates))),
        constraints=LinearConstraint(matrix, lower, upper),
        options={"time_limit": args.time_limit, "presolve": True},
    )
    if result.x is None:
        payload = {
            "question": "D-Q2",
            "diagnostic": "C-class revocation probe",
            "status": "NO_INCUMBENT",
            "optimality": "NOT_APPLICABLE",
            "interpretation": "No feasible incumbent was returned under the probe constraints; this does not prove infeasibility.",
            "q3_inputs_used": False,
            "fixed_total_revocations": args.fixed_total_revocations,
            "minimum_c_revocations": args.minimum_c_revocations,
            "optimization": {
                "solver_status": int(result.status),
                "solver_message": str(result.message),
                "time_limit_seconds": args.time_limit,
            },
        }
    else:
        summary = summarize_selected(plans, candidates, result)
        payload = {
            "question": "D-Q2",
            "diagnostic": "C-class revocation probe",
            "status": "OPTIMAL" if result.status == 0 else "FEASIBLE_INCUMBENT",
            "optimality": "PROVED" if result.status == 0 else "NOT_PROVED",
            "method": "full candidate-conflict MILP with fixed total revocations and a C-class revocation lower bound",
            "interpretation": "A feasible result shows that C-class revocation is not forced to zero by the Q2 feasibility constraints at this revocation count; it is not a replacement for the selected Q2 incumbent.",
            "q3_inputs_used": False,
            "time_domain": [0, args.horizon],
            "frequency_domain": [0, 100],
            "fixed_total_revocations": args.fixed_total_revocations,
            "minimum_c_revocations": args.minimum_c_revocations,
            "candidate_count": len(candidates),
            "candidate_conflict_edge_count": len(edges),
            "plan_count": len(plans),
            "optimization": {
                "solver_status": int(result.status),
                "solver_message": str(result.message),
                "objective": "adjusted plans",
                "objective_value": float(result.fun) if result.fun is not None else None,
                "mip_gap": float(getattr(result, "mip_gap", np.nan)),
                "time_limit_seconds": args.time_limit,
            },
            "summary": summary,
        }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(
        json.dumps(
            {
                "status": payload["status"],
                "fixed_total_revocations": args.fixed_total_revocations,
                "minimum_c_revocations": args.minimum_c_revocations,
                "objective_value": payload.get("optimization", {}).get("objective_value"),
                "output": str(args.output),
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
