#!/usr/bin/env python3
"""Independently re-encode D-Q3 and verify the 141-plan optimum.

This checker intentionally uses a pairwise-conflict formulation instead of the
resource-cell formulation used by ``solve_q3.py``.  The two formulations are
equivalent for binary candidate variables, but the independent encoding gives
the paper a second optimality audit and a direct infeasibility test for 142
plans.  It never changes the Q3 input, candidate set, or selected workbook.
"""
from __future__ import annotations

import argparse
from itertools import combinations
import json
from pathlib import Path

import numpy as np
from scipy.optimize import Bounds, LinearConstraint, milp
from scipy.sparse import coo_matrix, vstack

from scripts.solve_q3 import build_q2_occupancy, enumerate_candidates


def build_pairwise_matrix(candidates):
    owners_by_cell: dict[tuple[int, int], list[int]] = {}
    for index, candidate in enumerate(candidates):
        for cell in candidate.cells:
            owners_by_cell.setdefault(cell, []).append(index)

    edges: set[tuple[int, int]] = set()
    for owners in owners_by_cell.values():
        edges.update(combinations(owners, 2))

    rows: list[int] = []
    cols: list[int] = []
    values: list[float] = []
    for row, (left, right) in enumerate(sorted(edges)):
        rows.extend([row, row])
        cols.extend([left, right])
        values.extend([1.0, 1.0])
    matrix = coo_matrix(
        (values, (rows, cols)),
        shape=(len(edges), len(candidates)),
    ).tocsr()
    return matrix, len(edges), len(owners_by_cell)


def solve_maximum(candidates, matrix, time_limit: float):
    result = milp(
        c=-np.ones(len(candidates), dtype=float),
        integrality=np.ones(len(candidates), dtype=int),
        bounds=Bounds(np.zeros(len(candidates)), np.ones(len(candidates))),
        constraints=LinearConstraint(matrix, -np.inf, np.ones(matrix.shape[0])),
        options={"time_limit": time_limit, "presolve": True, "mip_rel_gap": 0.0},
    )
    selected_count = None
    if result.x is not None:
        selected_count = int(np.sum(result.x > 0.5))
    dual_bound = getattr(result, "mip_dual_bound", None)
    upper_bound = None
    if dual_bound is not None and np.isfinite(dual_bound):
        upper_bound = int(np.ceil(-float(dual_bound) - 1e-7))
    if result.status == 0 and selected_count is not None:
        upper_bound = selected_count
    return result, selected_count, upper_bound


def test_threshold(candidates, matrix, threshold: int, time_limit: float):
    threshold_row = coo_matrix(np.ones((1, len(candidates)), dtype=float)).tocsr()
    combined = vstack([matrix, threshold_row], format="csr")
    lower = np.concatenate([np.full(matrix.shape[0], -np.inf), [threshold]])
    upper = np.concatenate([np.ones(matrix.shape[0]), [np.inf]])
    result = milp(
        c=np.zeros(len(candidates), dtype=float),
        integrality=np.ones(len(candidates), dtype=int),
        bounds=Bounds(np.zeros(len(candidates)), np.ones(len(candidates))),
        constraints=LinearConstraint(combined, lower, upper),
        options={"time_limit": time_limit, "presolve": True, "mip_rel_gap": 0.0},
    )
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=Path("data/raw/D题/附件/附件1.xlsx"))
    parser.add_argument("--q2-result", type=Path, default=Path("outputs/q3/q2_input_from_result2.json"))
    parser.add_argument("--q3-result", type=Path, default=Path("outputs/q3/results.json"))
    parser.add_argument("--output", type=Path, default=Path("outputs/q3/q3_optimality_audit.json"))
    parser.add_argument("--horizon", type=int, default=643)
    parser.add_argument("--threshold", type=int, default=142)
    parser.add_argument("--time-limit", type=float, default=180.0)
    args = parser.parse_args()

    occupied, fixed = build_q2_occupancy(args.input, args.q2_result, args.horizon)
    candidates, total_candidates = enumerate_candidates(occupied, args.horizon)
    matrix, conflict_edge_count, cell_count = build_pairwise_matrix(candidates)
    maximum, selected_count, upper_bound = solve_maximum(candidates, matrix, args.time_limit)
    threshold = test_threshold(candidates, matrix, args.threshold, args.time_limit)
    q3_result = json.loads(args.q3_result.read_text(encoding="utf-8"))

    payload = {
        "question": "D-Q3",
        "scope": {
            "q2_input": str(args.q2_result),
            "q2_source_workbook": fixed.get("q2_source_workbook"),
            "horizon": args.horizon,
            "frequency_domain": [0, 100],
            "q2_interface_status": fixed.get("q2_interface_status"),
        },
        "candidate_enumeration": {
            "total_integer_starts": total_candidates,
            "q2_compatible_starts": len(candidates),
            "fixed_q2_occupied_cells": fixed.get("q2_occupied_cell_count"),
        },
        "independent_pairwise_model": {
            "formulation": "max sum(y_p), y_p+y_q<=1 for every pair with overlapping resource cells",
            "candidate_variables": len(candidates),
            "pairwise_conflict_constraints": conflict_edge_count,
            "resource_cells_indexed": cell_count,
            "status_code": int(maximum.status),
            "message": str(maximum.message),
            "selected_count": selected_count,
            "upper_bound": upper_bound,
            "mip_gap": float(getattr(maximum, "mip_gap", np.nan)),
            "mip_node_count": int(getattr(maximum, "mip_node_count", -1)),
        },
        "independent_threshold_test": {
            "constraint": f"sum(y_p) >= {args.threshold}",
            "status_code": int(threshold.status),
            "message": str(threshold.message),
            "infeasible_proved": threshold.status == 2,
        },
        "comparison_with_formal_q3": {
            "formal_selected_count": len(q3_result.get("selected_plans", [])),
            "formal_status": q3_result.get("status"),
            "formal_upper_bound": q3_result.get("solver", {}).get("upper_bound_from_solver"),
            "counts_match": selected_count == len(q3_result.get("selected_plans", [])),
            "both_bounds_close": selected_count is not None and upper_bound == selected_count,
        },
        "claim": (
            f"在固定批准 Q2 和当前资源域下，独立成对冲突模型得到上下界均为 {selected_count}，"
            f"且 {args.threshold} 台阈值不可行；因此最大新增数量为 {selected_count}。"
            if maximum.status == 0 and threshold.status == 2 and selected_count == upper_bound
            else "独立最优性核验未闭合，不能升级 Q3 最优性表述。"
        ),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({
        "status": "PASS" if payload["claim"].startswith("在固定") else "INCOMPLETE",
        "selected_count": selected_count,
        "upper_bound": upper_bound,
        "threshold_status": int(threshold.status),
        "output": str(args.output),
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
