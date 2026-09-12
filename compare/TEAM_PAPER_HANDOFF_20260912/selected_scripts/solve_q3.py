#!/usr/bin/env python3
"""Solve D-Q3 with Q2 fixed and complete C-class templates."""
from __future__ import annotations

import argparse
from dataclasses import dataclass
import json
from pathlib import Path

import numpy as np
from scipy.optimize import Bounds, LinearConstraint, milp
from scipy.sparse import coo_matrix

from scripts.solve_q1 import read_plans
from scripts.validate_q2 import apply_actions, check_conflicts, expanded, occupied_cells


C_WIDTH = 3
C_DURATION = 2
C_GAP = 8
C_USES = 12
C_STEP = C_DURATION + C_GAP


@dataclass(frozen=True)
class Candidate:
    frequency_start: int
    time_start: int
    cells: frozenset[tuple[int, int]]


def c_events(frequency_start: int, time_start: int) -> list[tuple[int, int, int, int]]:
    return [
        (
            frequency_start,
            frequency_start + C_WIDTH,
            time_start + k * C_STEP,
            time_start + k * C_STEP + C_DURATION,
        )
        for k in range(C_USES)
    ]


def build_q2_occupancy(input_path: Path, q2_result_path: Path, horizon: int) -> tuple[set[tuple[int, int]], dict]:
    plans = read_plans(input_path)
    result = json.loads(q2_result_path.read_text(encoding="utf-8"))
    adjusted, action_errors = apply_actions(plans, result.get("summary", {}).get("actions", []))
    if action_errors:
        raise ValueError(f"Q2 actions cannot be applied: {action_errors}")
    q2_checks = check_conflicts(adjusted, horizon)
    if (
        q2_checks["boundary_errors"]
        or q2_checks["continuous_conflict_pairs"]
        or q2_checks["discrete_conflict_pairs"]
    ):
        raise ValueError(f"fixed Q2 result is not a valid background: {q2_checks}")
    occupied: set[tuple[int, int]] = set()
    for plan in adjusted:
        if not plan.get("revoked", False):
            occupied.update(occupied_cells(expanded(plan)))
    return occupied, {
        "q2_result": str(q2_result_path),
        "q2_source_workbook": result.get("source_workbook"),
        "q2_interface_status": "APPROVED_BY_USER",
        "q2_objective_values": result.get("objective_values", {}),
        "q2_proof_reference": "outputs\\q2\\results.json",
        "q2_status": result.get("status"),
        "q2_optimality": result.get("optimality", "UNSPECIFIED"),
        "q2_active_plan_count": q2_checks["active_plan_count"],
        "q2_occupied_cell_count": len(occupied),
        "q2_validation": q2_checks,
    }


def enumerate_candidates(occupied: set[tuple[int, int]], horizon: int) -> tuple[list[Candidate], int]:
    latest_start = horizon - ((C_USES - 1) * C_STEP + C_DURATION)
    if latest_start < 0:
        return [], 0
    candidates: list[Candidate] = []
    total = 0
    for frequency_start in range(0, 100 - C_WIDTH + 1):
        for time_start in range(0, latest_start + 1):
            total += 1
            cells = frozenset(
                (time_start + C_STEP * k + time_offset, frequency_start + frequency_offset)
                for k in range(C_USES)
                for time_offset in range(C_DURATION)
                for frequency_offset in range(C_WIDTH)
            )
            if not cells & occupied:
                candidates.append(Candidate(frequency_start, time_start, cells))
    return candidates, total


def build_resource_matrix(candidates: list[Candidate]):
    row_by_cell: dict[tuple[int, int], int] = {}
    rows: list[int] = []
    cols: list[int] = []
    values: list[float] = []
    for column, candidate in enumerate(candidates):
        for cell in candidate.cells:
            row = row_by_cell.setdefault(cell, len(row_by_cell))
            rows.append(row)
            cols.append(column)
            values.append(1.0)
    matrix = coo_matrix(
        (values, (rows, cols)),
        shape=(len(row_by_cell), len(candidates)),
    ).tocsr()
    return matrix, row_by_cell


def solve(candidates: list[Candidate], time_limit: float):
    if not candidates:
        return None, None
    matrix, row_by_cell = build_resource_matrix(candidates)
    result = milp(
        c=-np.ones(len(candidates), dtype=float),
        integrality=np.ones(len(candidates), dtype=int),
        bounds=Bounds(np.zeros(len(candidates)), np.ones(len(candidates))),
        constraints=LinearConstraint(matrix, -np.inf, np.ones(matrix.shape[0])),
        options={"time_limit": time_limit, "presolve": True, "mip_rel_gap": 0.0},
    )
    return result, {"resource_cell_rows": len(row_by_cell), "matrix_nonzeros": int(matrix.nnz)}


def serialize_selected(candidates: list[Candidate], result) -> list[dict]:
    if result is None or result.x is None:
        return []
    chosen = [
        candidates[index]
        for index, value in enumerate(result.x)
        if value > 0.5
    ]
    chosen.sort(key=lambda item: (item.time_start, item.frequency_start))
    return [
        {
            "新增用频装备序号": sequence,
            "频段区间": f"[{candidate.frequency_start},{candidate.frequency_start + C_WIDTH})",
            "时间区间": f"[{candidate.time_start},{candidate.time_start + C_DURATION})",
            "频段起点": candidate.frequency_start,
            "时间起点": candidate.time_start,
            "使用次数": C_USES,
            "单次时长": C_DURATION,
            "间隔时长": C_GAP,
            "相邻起点步长": C_STEP,
        }
        for sequence, candidate in enumerate(chosen, start=1)
    ]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=Path("data/raw/D题/附件/附件1.xlsx"))
    parser.add_argument("--q2-result", type=Path, default=Path("outputs/q2/results.json"))
    parser.add_argument("--output-dir", type=Path, default=Path("outputs/q3"))
    parser.add_argument("--horizon", type=int, default=643)
    parser.add_argument("--time-limit", type=float, default=180.0)
    args = parser.parse_args()

    occupied, fixed = build_q2_occupancy(args.input, args.q2_result, args.horizon)
    candidates, total_candidates = enumerate_candidates(occupied, args.horizon)
    result, matrix_info = solve(candidates, args.time_limit)
    output_dir = args.output_dir
    output_dir.mkdir(parents=True, exist_ok=True)

    if result is None or result.x is None:
        payload = {
            "question": "D-Q3",
            "status": "NO_INCUMBENT",
            "optimality": "NOT_APPLICABLE",
            "method": "fixed Q2 occupancy + complete C-class candidate enumeration + 0-1 set packing",
            "time_domain": [0, args.horizon],
            "frequency_domain": [0, 100],
            "c_class_template": {
                "frequency_width": C_WIDTH,
                "duration": C_DURATION,
                "gap": C_GAP,
                "uses": C_USES,
                "step": C_STEP,
            },
            "candidate_count": total_candidates,
            "feasible_candidate_count": len(candidates),
            "fixed_q2": fixed,
            "solver": {"time_limit_seconds": args.time_limit},
            "selected_plans": [],
            "claim_boundary": "没有返回可行 incumbent，不能报告新增数量。",
        }
    else:
        selected = serialize_selected(candidates, result)
        status = "OPTIMAL" if result.status == 0 else "FEASIBLE_INCUMBENT"
        optimality = "PROVED" if result.status == 0 else "NOT_PROVED"
        dual_bound = getattr(result, "mip_dual_bound", None)
        upper_bound = None
        if dual_bound is not None and np.isfinite(dual_bound):
            upper_bound = int(np.ceil(-float(dual_bound) - 1e-7))
        if result.status == 0:
            upper_bound = len(selected)
        payload = {
            "question": "D-Q3",
            "status": status,
            "optimality": optimality,
            "method": "fixed Q2 occupancy + complete C-class candidate enumeration + 0-1 set packing",
            "interpretation": "Q2 final active plans are fixed; Q3 only chooses new C-class complete templates inside the fixed resource domain.",
            "time_domain": [0, args.horizon],
            "frequency_domain": [0, 100],
            "c_class_template": {
                "frequency_width": C_WIDTH,
                "duration": C_DURATION,
                "gap": C_GAP,
                "uses": C_USES,
                "step": C_STEP,
                "resource_cells_per_plan": C_WIDTH * C_DURATION * C_USES,
            },
            "candidate_count": total_candidates,
            "feasible_candidate_count": len(candidates),
            "fixed_q2": fixed,
            "solver": {
                "status_code": int(result.status),
                "message": str(result.message),
                "objective_minimization_value": float(result.fun) if result.fun is not None else None,
                "selected_count": len(selected),
                "upper_bound_from_solver": upper_bound,
                "mip_gap": float(getattr(result, "mip_gap", np.nan)),
                "mip_node_count": int(getattr(result, "mip_node_count", -1)),
                "time_limit_seconds": args.time_limit,
                **(matrix_info or {}),
            },
            "selected_plans": selected,
            "claim_boundary": (
                f"在固定当前 Q2 主方案和 [0,{args.horizon})×[0,100) 资源域内，求解器已证明最大新增数量为 {len(selected)}。"
                if optimality == "PROVED"
                else f"在固定当前 Q2 主方案和 [0,{args.horizon})×[0,100) 资源域内，当前仅找到 {len(selected)} 个新增计划的可行 incumbent，最多数量尚未证明。"
            ),
        }

    (output_dir / "results.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "status": payload["status"],
                "optimality": payload["optimality"],
                "total_candidates": total_candidates,
                "feasible_candidates": len(candidates),
                "selected_count": len(payload["selected_plans"]),
                "solver_message": payload.get("solver", {}).get("message"),
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
