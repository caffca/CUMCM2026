#!/usr/bin/env python3
"""Independent SAT proof probes for Q2 threshold infeasibility.

The candidate-action model is encoded as Boolean variables.  Every plan has
exactly one selected action, every occupied resource cell has at most one
selected candidate, and the requested cardinality threshold is encoded with
sequential/totalizer counters.  SAT is used only as a proof probe: UNSAT is a
closed infeasibility result; SAT is a witness; an interrupted run is not a
bound.
"""
from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path
from time import perf_counter

from pysat.card import CardEnc, EncType
from pysat.formula import CNF
from pysat.solvers import Solver

from scripts.solve_q1 import read_plans
from scripts.solve_q2 import build_candidates


def add_atmost(cnf: CNF, literals: list[int], bound: int, top_id: int) -> int:
    if bound < 0:
        cnf.append([])
        return top_id
    if bound >= len(literals):
        return top_id
    if bound == 1 and len(literals) == 2:
        cnf.append([-literals[0], -literals[1]])
        return top_id
    encoded = CardEnc.atmost(lits=literals, bound=bound, top_id=top_id, encoding=EncType.seqcounter)
    cnf.extend(encoded.clauses)
    return max(top_id, encoded.nv)


def add_atleast(cnf: CNF, literals: list[int], bound: int, top_id: int) -> int:
    if bound <= 0:
        return top_id
    if bound > len(literals):
        cnf.append([])
        return top_id
    encoded = CardEnc.atleast(lits=literals, bound=bound, top_id=top_id, encoding=EncType.totalizer)
    cnf.extend(encoded.clauses)
    return max(top_id, encoded.nv)


def add_equals(cnf: CNF, literals: list[int], value: int, top_id: int) -> int:
    if value == 0:
        for literal in literals:
            cnf.append([-literal])
        return top_id
    encoded = CardEnc.equals(lits=literals, bound=value, top_id=top_id, encoding=EncType.totalizer)
    cnf.extend(encoded.clauses)
    return max(top_id, encoded.nv)


def make_formula(plans: list[dict], horizon: int, probe: str) -> tuple[CNF, list, dict]:
    candidates = build_candidates(plans, horizon)
    cnf = CNF()
    top_id = len(candidates)
    by_plan: defaultdict[str, list[int]] = defaultdict(list)
    by_cell: defaultdict[tuple[int, int], list[int]] = defaultdict(list)
    for index, candidate in enumerate(candidates, start=1):
        by_plan[candidate.plan_id].append(index)
        for cell in candidate.cells:
            by_cell[cell].append(index)

    for literals in by_plan.values():
        cnf.append(list(literals))
        top_id = add_atmost(cnf, literals, 1, top_id)
    for literals in by_cell.values():
        if len(literals) >= 2:
            top_id = add_atmost(cnf, literals, 1, top_id)

    def feature(predicate):
        return [index for index, candidate in enumerate(candidates, start=1) if predicate(candidate)]

    revokes = feature(lambda c: c.action == "revoke")
    revoke_a = feature(lambda c: c.category == "A" and c.action == "revoke")
    revoke_b = feature(lambda c: c.category == "B" and c.action == "revoke")
    keeps = feature(lambda c: c.action == "keep")
    adjust_a = feature(lambda c: c.category == "A" and c.action in {"freq", "time"})
    adjust_b = feature(lambda c: c.category == "B" and c.action in {"freq", "time"})
    if probe == "b_le_3":
        top_id = add_equals(cnf, revokes, 6, top_id)
        top_id = add_equals(cnf, revoke_a, 0, top_id)
        top_id = add_atmost(cnf, revoke_b, 3, top_id)
        description = "R=6, A类撤销=0, B类撤销<=3"
    elif probe == "b_le_4":
        top_id = add_equals(cnf, revokes, 6, top_id)
        top_id = add_equals(cnf, revoke_a, 0, top_id)
        top_id = add_atmost(cnf, revoke_b, 4, top_id)
        description = "sanity check: R=6, A类撤销=0, B类撤销<=4"
    elif probe == "adjust_le_125":
        top_id = add_equals(cnf, revokes, 6, top_id)
        top_id = add_equals(cnf, revoke_a, 0, top_id)
        top_id = add_equals(cnf, revoke_b, 4, top_id)
        # With exactly one action per each of 150 plans and R=6, M<=125 is
        # equivalent to selecting at least 19 keep candidates.
        top_id = add_atleast(cnf, keeps, 19, top_id)
        description = "R=6, A类撤销=0, B类撤销=4, 调整计划数<=125（等价于保留数>=19）"
    elif probe == "adjust_le_126":
        top_id = add_equals(cnf, revokes, 6, top_id)
        top_id = add_equals(cnf, revoke_a, 0, top_id)
        top_id = add_equals(cnf, revoke_b, 4, top_id)
        top_id = add_atleast(cnf, keeps, 18, top_id)
        description = "sanity check: R=6, A类撤销=0, B类撤销=4, 调整计划数<=126（等价于保留数>=18）"
    elif probe == "adjust_a_le_15":
        top_id = add_equals(cnf, revokes, 6, top_id)
        top_id = add_equals(cnf, revoke_a, 0, top_id)
        top_id = add_equals(cnf, revoke_b, 4, top_id)
        top_id = add_atleast(cnf, keeps, 18, top_id)
        top_id = add_atmost(cnf, adjust_a, 15, top_id)
        description = "R=6, A类撤销=0, B类撤销=4, M<=126, A类调整<=15"
    elif probe == "adjust_b_le_33":
        top_id = add_equals(cnf, revokes, 6, top_id)
        top_id = add_equals(cnf, revoke_a, 0, top_id)
        top_id = add_equals(cnf, revoke_b, 4, top_id)
        top_id = add_atleast(cnf, keeps, 18, top_id)
        top_id = add_atmost(cnf, adjust_a, 16, top_id)
        top_id = add_atmost(cnf, adjust_b, 33, top_id)
        description = "R=6, A类撤销=0, B类撤销=4, M<=126, A类调整<=16, B类调整<=33"
    else:
        raise ValueError(f"unknown probe {probe!r}")

    metadata = {
        "description": description,
        "candidate_count": len(candidates),
        "plan_count": len(plans),
        "resource_cell_count": len(by_cell),
        "resource_cell_constraint_count": sum(len(literals) >= 2 for literals in by_cell.values()),
        "base_variable_count": len(candidates),
        "encoded_variable_count": top_id,
        "candidate_cells_nonzero_count": sum(len(candidate.cells) > 0 for candidate in candidates),
    }
    return cnf, candidates, metadata


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=Path("data/raw/D题/附件/附件1.xlsx"))
    parser.add_argument(
        "--probe",
        choices=["b_le_3", "b_le_4", "adjust_le_125", "adjust_le_126", "adjust_a_le_15", "adjust_b_le_33"],
        required=True,
    )
    parser.add_argument("--horizon", type=int, default=643)
    parser.add_argument("--solver", default="cadical195")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    plans = read_plans(args.input)
    started = perf_counter()
    cnf, candidates, metadata = make_formula(plans, args.horizon, args.probe)
    build_seconds = perf_counter() - started
    with Solver(name=args.solver, bootstrap_with=cnf.clauses) as solver:
        solve_started = perf_counter()
        sat = solver.solve()
        solve_seconds = perf_counter() - solve_started
        status = "SAT" if sat else "UNSAT"
        payload = {
            "question": "D-Q2",
            "probe": args.probe,
            "horizon": args.horizon,
            "solver": args.solver,
            "status": status,
            "optimality": "PROVED_INFEASIBLE" if status == "UNSAT" else "FEASIBLE_WITNESS",
            "build_seconds": build_seconds,
            "solve_seconds": solve_seconds,
            "formula": {**metadata, "clause_count": len(cnf.clauses)},
            "solver_stats": solver.accum_stats(),
        }
        if sat:
            model = set(literal for literal in solver.get_model() if literal > 0)
            selected = [candidates[index - 1] for index in range(1, len(candidates) + 1) if index in model]
            payload["incumbent"] = {
                "selected_candidates": len(selected),
                "revocations": sum(candidate.action == "revoke" for candidate in selected),
                "revoke_A": sum(candidate.category == "A" and candidate.action == "revoke" for candidate in selected),
                "revoke_B": sum(candidate.category == "B" and candidate.action == "revoke" for candidate in selected),
                "adjusted_plans": sum(candidate.action in {"freq", "time"} for candidate in selected),
                "kept_plans": sum(candidate.action == "keep" for candidate in selected),
            }

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"probe": args.probe, "solver": args.solver, "status": status, "optimality": payload["optimality"], "output": str(args.output)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
