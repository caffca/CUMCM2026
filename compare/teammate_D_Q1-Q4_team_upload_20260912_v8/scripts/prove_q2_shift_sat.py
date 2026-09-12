#!/usr/bin/env python3
"""Independent SAT threshold proof for the Q2 terminal shift layer.

The query is the adjacent threshold

    R=6, R_A=0, R_B=4, M=126, M_A=16, M_B=34, S10 <= 774,

under the same finite candidate-action semantics used by the approved Q2
workbook.  This is a feasibility checker, not an optimizer: SAT is a
witness, UNSAT is a closed lower-bound certificate, and an interrupted solve
is recorded as UNKNOWN.

The optional dominance reduction is proof-preserving for this particular
query.  Within one original plan, candidate ``a`` may be removed only when a
candidate ``b`` has (i) a subset of ``a``'s external conflict set, (ii) the
same six fixed feature values, and (iii) no larger S10 cost.  Replacing a by
b then preserves all equalities, cannot increase the threshold cost, and
cannot create a resource conflict.
"""
from __future__ import annotations

import argparse
from collections import defaultdict
import json
from pathlib import Path
import threading
from time import perf_counter

from pysat.card import CardEnc, EncType
from pysat.formula import CNF
from pysat.solvers import Solver

from scripts.solve_q1 import read_plans
from scripts.solve_q2 import Candidate, build_candidates


FIXED_FEATURES = [
    ("revoke", 6),
    ("revoke_A", 0),
    ("revoke_B", 4),
    ("adjust", 126),
    ("adjust_A", 16),
    ("adjust_B", 34),
]
THRESHOLD_FEATURE = "normalized_shift"
THRESHOLD = 774


def feature_value(candidate: Candidate, name: str) -> int:
    if name == "revoke":
        return int(candidate.action == "revoke")
    if name == "revoke_A":
        return int(candidate.category == "A" and candidate.action == "revoke")
    if name == "revoke_B":
        return int(candidate.category == "B" and candidate.action == "revoke")
    if name == "revoke_C":
        return int(candidate.category == "C" and candidate.action == "revoke")
    if name == "adjust":
        return int(candidate.action in {"freq", "time"})
    if name == "adjust_A":
        return int(candidate.category == "A" and candidate.action in {"freq", "time"})
    if name == "adjust_B":
        return int(candidate.category == "B" and candidate.action in {"freq", "time"})
    if name == "keep_A":
        return int(candidate.category == "A" and candidate.action == "keep")
    if name == "keep_B":
        return int(candidate.category == "B" and candidate.action == "keep")
    if name == "keep_C":
        return int(candidate.category == "C" and candidate.action == "keep")
    if name == THRESHOLD_FEATURE:
        return abs(candidate.df) + 2 * abs(candidate.dt)
    raise ValueError(f"unknown feature {name!r}")


def add_atmost(
    cnf: CNF,
    literals: list[int],
    bound: int,
    top_id: int,
    encoding: int = EncType.seqcounter,
) -> int:
    if bound < 0 or bound >= len(literals):
        if bound < 0:
            cnf.append([])
        return top_id
    if bound == 1 and len(literals) == 2:
        cnf.append([-literals[0], -literals[1]])
        return top_id
    encoded = CardEnc.atmost(
        lits=literals,
        bound=bound,
        top_id=top_id,
        encoding=encoding,
    )
    cnf.extend(encoded.clauses)
    return max(top_id, encoded.nv)


def add_equals(cnf: CNF, literals: list[int], value: int, top_id: int) -> int:
    if value < 0 or value > len(literals):
        cnf.append([])
        return top_id
    if value == 0:
        for literal in literals:
            cnf.append([-literal])
        return top_id
    encoded = CardEnc.equals(
        lits=literals,
        bound=value,
        top_id=top_id,
        encoding=EncType.totalizer,
    )
    cnf.extend(encoded.clauses)
    return max(top_id, encoded.nv)


def build_neighbors(candidates: list[Candidate]) -> list[set[int]]:
    by_cell: defaultdict[tuple[int, int], list[int]] = defaultdict(list)
    for index, candidate in enumerate(candidates):
        for cell in candidate.cells:
            by_cell[cell].append(index)
    neighbors = [set() for _ in candidates]
    for indexes in by_cell.values():
        if len(indexes) < 2:
            continue
        for left_position, left in enumerate(indexes):
            for right in indexes[left_position + 1 :]:
                if candidates[left].plan_id == candidates[right].plan_id:
                    continue
                neighbors[left].add(right)
                neighbors[right].add(left)
    return neighbors


def add_full_adder(
    cnf: CNF,
    left: int,
    right: int,
    carry_in: int,
    sum_bit: int,
    carry_out: int,
) -> None:
    """Encode a one-bit full adder by its finite truth table.

    The five literals are ordinary positive variable identifiers.  Truth-table
    clauses are intentionally verbose but transparent and do not rely on an
    optional native pseudo-Boolean library.
    """
    variables = [left, right, carry_in, sum_bit, carry_out]
    for assignment in range(32):
        left_value = (assignment >> 0) & 1
        right_value = (assignment >> 1) & 1
        carry_value = (assignment >> 2) & 1
        observed_sum = (assignment >> 3) & 1
        observed_carry = (assignment >> 4) & 1
        expected_sum = left_value ^ right_value ^ carry_value
        expected_carry = int(left_value + right_value + carry_value >= 2)
        if observed_sum == expected_sum and observed_carry == expected_carry:
            continue
        # Block this complete input/output assignment.
        cnf.append([
            -variable if ((assignment >> position) & 1) else variable
            for position, variable in enumerate(variables)
        ])


def add_binary_weight_upper_bound(
    cnf: CNF,
    candidate_literals: list[int],
    weights: list[int],
    bound: int,
    top_id: int,
    maximum_sum: int | None = None,
) -> tuple[int, dict]:
    """Add ``sum(weights[i] * x_i) <= bound`` using a ripple-adder circuit.

    Every positive-weight candidate is added as a binary constant controlled by
    its selection literal.  The accumulator width is chosen above the maximum
    possible sum, so the construction is exact rather than a relaxation.  A
    binary comparator then forbids values lexicographically larger than the
    bound.  This provides a compact, dependency-free alternative to PyPBLib.
    """
    positive_weights = [weight for weight in weights if weight > 0]
    if maximum_sum is None:
        maximum_sum = sum(positive_weights)
    width = max(1, maximum_sum.bit_length(), max(0, bound).bit_length())

    top_id += 1
    false_var = top_id
    cnf.append([-false_var])

    accumulator = [false_var] * width
    added_candidates = 0
    for literal, weight in zip(candidate_literals, weights):
        if weight <= 0:
            continue
        added_candidates += 1
        carry = false_var
        next_accumulator: list[int] = []
        for bit in range(width):
            top_id += 1
            sum_bit = top_id
            top_id += 1
            carry_out = top_id
            right = literal if (weight >> bit) & 1 else false_var
            add_full_adder(cnf, accumulator[bit], right, carry, sum_bit, carry_out)
            next_accumulator.append(sum_bit)
            carry = carry_out
        # width was selected to contain the maximum possible sum; making this
        # explicit catches implementation mistakes instead of silently
        # allowing modular arithmetic.
        cnf.append([-carry])
        accumulator = next_accumulator

    if bound < 0:
        cnf.append([])
    else:
        # Equality prefix state, scanned from the most significant bit.  If
        # the corresponding bound bit is zero, an equal prefix may not choose
        # one at that position.
        top_id += 1
        equal_prefix = top_id
        cnf.append([equal_prefix])
        for bit in range(width - 1, -1, -1):
            bound_bit = (bound >> bit) & 1
            if bound_bit == 0:
                cnf.append([-equal_prefix, -accumulator[bit]])
            top_id += 1
            next_equal = top_id
            cnf.append([-next_equal, equal_prefix])
            if bound_bit:
                cnf.append([-next_equal, accumulator[bit]])
                cnf.append([-equal_prefix, -accumulator[bit], next_equal])
            else:
                cnf.append([-next_equal, -accumulator[bit]])
                cnf.append([-equal_prefix, accumulator[bit], next_equal])
            equal_prefix = next_equal

    return top_id, {
        "encoding": "binary-ripple-adder+lexicographic-comparator",
        "width_bits": width,
        "maximum_unconditional_weight_sum": maximum_sum,
        "positive_weight_candidate_count": added_candidates,
        "bound": bound,
    }


def add_binary_numbers_upper_bound(
    cnf: CNF,
    numbers: list[list[int]],
    bound: int,
    top_id: int,
    maximum_sum: int,
) -> tuple[int, dict]:
    """Add an upper bound for a sum of encoded binary plan costs."""
    width = max(1, maximum_sum.bit_length(), max(0, bound).bit_length())
    top_id += 1
    false_var = top_id
    cnf.append([-false_var])
    accumulator = [false_var] * width
    adder_count = 0
    for number in numbers:
        carry = false_var
        next_accumulator: list[int] = []
        for bit in range(width):
            top_id += 1
            sum_bit = top_id
            top_id += 1
            carry_out = top_id
            right = number[bit] if bit < len(number) else false_var
            add_full_adder(cnf, accumulator[bit], right, carry, sum_bit, carry_out)
            next_accumulator.append(sum_bit)
            carry = carry_out
            adder_count += 1
        cnf.append([-carry])
        accumulator = next_accumulator

    if bound < 0:
        cnf.append([])
    else:
        top_id += 1
        equal_prefix = top_id
        cnf.append([equal_prefix])
        for bit in range(width - 1, -1, -1):
            bound_bit = (bound >> bit) & 1
            if bound_bit == 0:
                cnf.append([-equal_prefix, -accumulator[bit]])
            top_id += 1
            next_equal = top_id
            cnf.append([-next_equal, equal_prefix])
            if bound_bit:
                cnf.append([-next_equal, accumulator[bit]])
                cnf.append([-equal_prefix, -accumulator[bit], next_equal])
            else:
                cnf.append([-next_equal, -accumulator[bit]])
                cnf.append([-equal_prefix, accumulator[bit], next_equal])
            equal_prefix = next_equal
    return top_id, {
        "encoding": "plan-cost-bits+ripple-adder+lexicographic-comparator",
        "width_bits": width,
        "plan_count": len(numbers),
        "adder_count": adder_count,
        "maximum_feasible_weight_sum": maximum_sum,
        "bound": bound,
    }


def dominance_reduce(candidates: list[Candidate]) -> tuple[list[Candidate], dict]:
    neighbors = build_neighbors(candidates)
    by_plan: defaultdict[str, list[int]] = defaultdict(list)
    for index, candidate in enumerate(candidates):
        by_plan[candidate.plan_id].append(index)

    signature_names = [name for name, _ in FIXED_FEATURES]
    signatures = {
        index: tuple(feature_value(candidate, name) for name in signature_names)
        for index, candidate in enumerate(candidates)
    }
    removed: set[int] = set()
    for indexes in by_plan.values():
        for left in indexes:
            for right in indexes:
                if left == right or signatures[left] != signatures[right]:
                    continue
                left_cost = feature_value(candidates[left], THRESHOLD_FEATURE)
                right_cost = feature_value(candidates[right], THRESHOLD_FEATURE)
                if right_cost > left_cost:
                    continue
                if not neighbors[right] <= neighbors[left]:
                    continue
                if neighbors[right] == neighbors[left] and right > left:
                    continue
                removed.add(left)
                break

    kept = [candidate for index, candidate in enumerate(candidates) if index not in removed]
    details = {
        "enabled": True,
        "input_candidate_count": len(candidates),
        "removed_candidate_count": len(removed),
        "kept_candidate_count": len(kept),
        "plans_with_removed_actions": sum(
            any(index in removed for index in indexes) for indexes in by_plan.values()
        ),
        "fixed_feature_signature": [name for name, _ in FIXED_FEATURES],
        "threshold_feature": THRESHOLD_FEATURE,
        "rule": "same-plan b replaces a when N_ext(b) subseteq N_ext(a), fixed signatures equal, and S10(b) <= S10(a)",
    }
    return kept, details


def make_formula(candidates: list[Candidate]) -> tuple[CNF, dict]:
    cnf = CNF()
    top_id = len(candidates)
    by_plan: defaultdict[str, list[int]] = defaultdict(list)
    by_cell: defaultdict[tuple[int, int], list[int]] = defaultdict(list)
    for index, candidate in enumerate(candidates, start=1):
        by_plan[candidate.plan_id].append(index)
        for cell in candidate.cells:
            by_cell[cell].append(index)

    # Exactly one action per original plan.
    for literals in by_plan.values():
        cnf.append(list(literals))
        for position, left in enumerate(literals):
            for right in literals[position + 1 :]:
                cnf.append([-left, -right])

    # Deduplicated binary conflicts are equivalent to cell at-most-one rows
    # for 0-1 variables, because candidates from the same plan are already
    # mutually exclusive above.
    conflict_edges = {
        (left, right)
        for literals in by_cell.values()
        if len(literals) >= 2
        for position, left in enumerate(literals)
        for right in literals[position + 1 :]
        if candidates[left - 1].plan_id != candidates[right - 1].plan_id
    }
    for left, right in conflict_edges:
        cnf.append([-left, -right])

    # The six Q2 prefix equalities have an equivalent compact form because
    # every plan selects exactly one action and the category totals are fixed:
    # R=6, R_A=0, R_B=4, M=126, M_A=16, M_B=34
    # <=> R_A=0, R_B=4, R_C=2, K_A=4, K_B=2, K_C=12.
    # The latter uses only plan-level keep/revoke literals, avoiding large
    # totalizers over thousands of adjusted-action literals.
    compact_constraints = [
        ("revoke_A", 0),
        ("revoke_B", 4),
        ("revoke_C", 2),
        ("keep_A", 4),
        ("keep_B", 2),
        ("keep_C", 12),
    ]
    feature_literals = {
        name: [
            index
            for index, candidate in enumerate(candidates, start=1)
            if feature_value(candidate, name)
        ]
        for name, _ in compact_constraints
    }
    # Since exactly one candidate is selected per plan, write its integer cost
    # as a sum of threshold indicators:
    #
    #     cost_p = 1[cost_p >= 1] + ... + 1[cost_p >= K].
    #
    # The indicators are equivalent to the corresponding disjunctions of the
    # plan's action literals.  Thus S10 is an ordinary cardinality sum over at
    # most 10 indicators per plan; this is much smaller than adding every
    # candidate literal separately and is exact under the one-action rule.
    candidate_literals_by_plan: defaultdict[str, list[int]] = defaultdict(list)
    for literal, candidate in enumerate(candidates, start=1):
        candidate_literals_by_plan[candidate.plan_id].append(literal)
    maximum_cost = 0
    maximum_sum = 0
    level_literals: list[int] = []
    level_indicator_count = 0
    for plan_literals in candidate_literals_by_plan.values():
        costs = [feature_value(candidates[literal - 1], THRESHOLD_FEATURE) for literal in plan_literals]
        plan_maximum = max(costs, default=0)
        maximum_cost = max(maximum_cost, plan_maximum)
        maximum_sum += plan_maximum
        for level in range(1, plan_maximum + 1):
            positive = [
                literal
                for literal, cost in zip(plan_literals, costs)
                if cost >= level
            ]
            top_id += 1
            level_literal = top_id
            if positive:
                for literal in positive:
                    cnf.append([-literal, level_literal])
                cnf.append([-level_literal, *positive])
            else:
                cnf.append([-level_literal])
            level_literals.append(level_literal)
            level_indicator_count += 1
    top_id = add_atmost(
        cnf,
        level_literals,
        THRESHOLD,
        top_id,
        encoding=EncType.kmtotalizer,
    )
    weighted_encoding = {
        "encoding": "plan-cost-threshold-indicators+kmtotalizer",
        "maximum_cost_per_plan": maximum_cost,
        "maximum_feasible_weight_sum": maximum_sum,
        "level_indicator_count": level_indicator_count,
        "bound": THRESHOLD,
    }

    for name, value in compact_constraints:
        top_id = add_equals(cnf, feature_literals[name], value, top_id)

    return cnf, {
        "plan_count": len(by_plan),
        "candidate_count": len(candidates),
        "resource_cell_count": len(by_cell),
        "resource_cell_constraint_count": sum(len(items) >= 2 for items in by_cell.values()),
        "conflict_edge_count": len(conflict_edges),
        "base_variable_count": len(candidates),
        "encoded_variable_count": top_id,
        "clause_count": len(cnf.clauses),
        "weighted_encoding": weighted_encoding,
        "level_indicator_count": level_indicator_count,
        "fixed_features": [{"feature": name, "value": value} for name, value in FIXED_FEATURES],
        "compact_equivalent_constraints": [
            {"feature": name, "value": value} for name, value in compact_constraints
        ],
        "threshold": {"feature": THRESHOLD_FEATURE, "value": THRESHOLD},
    }


def selected_feature_values(candidates: list[Candidate], positive: set[int]) -> dict[str, int]:
    names = [name for name, _ in FIXED_FEATURES] + [THRESHOLD_FEATURE]
    return {
        name: sum(
            feature_value(candidate, name)
            for index, candidate in enumerate(candidates, start=1)
            if index in positive
        )
        for name in names
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=Path("data/raw/D题/附件/附件1.xlsx"))
    parser.add_argument("--horizon", type=int, default=643)
    parser.add_argument("--solver", default="cadical195")
    parser.add_argument("--time-limit", type=float, default=900.0)
    parser.add_argument("--no-dominance", action="store_true")
    parser.add_argument("--build-only", action="store_true", help="Build and record the formula without invoking a SAT solver.")
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    build_started = perf_counter()
    plans = read_plans(args.input)
    original_candidates = build_candidates(plans, args.horizon)
    if args.no_dominance:
        candidates = original_candidates
        dominance = {"enabled": False, "input_candidate_count": len(candidates), "kept_candidate_count": len(candidates), "removed_candidate_count": 0}
    else:
        candidates, dominance = dominance_reduce(original_candidates)
    cnf, formula = make_formula(candidates)
    build_seconds = perf_counter() - build_started

    if args.build_only:
        payload = {
            "question": "D-Q2",
            "mode": "independent_sat_shift_threshold",
            "description": "R=6, R_A=0, R_B=4, M=126, M_A=16, M_B=34, S10<=774",
            "status": "BUILD_ONLY",
            "proof": "NOT_PROVED",
            "horizon": args.horizon,
            "solver": args.solver,
            "time_limit_seconds": args.time_limit,
            "build_seconds": build_seconds,
            "dominance": dominance,
            "formula": formula,
        }
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        print(json.dumps({"status": payload["status"], "candidate_count": len(candidates), "clauses": formula["clause_count"], "output": str(args.output)}, ensure_ascii=False))
        return

    solve_started = perf_counter()
    with Solver(name=args.solver, bootstrap_with=cnf.clauses) as solver:
        timer = None
        if args.time_limit > 0:
            timer = threading.Timer(args.time_limit, solver.interrupt)
            timer.daemon = True
            timer.start()
        try:
            result = solver.solve_limited(expect_interrupt=args.time_limit > 0)
        finally:
            if timer is not None:
                timer.cancel()
        solve_seconds = perf_counter() - solve_started
        status = "SAT" if result is True else "UNSAT" if result is False else "UNKNOWN"
        payload = {
            "question": "D-Q2",
            "mode": "independent_sat_shift_threshold",
            "description": "R=6, R_A=0, R_B=4, M=126, M_A=16, M_B=34, S10<=774",
            "status": status,
            "proof": "FEASIBLE_WITNESS" if result is True else "PROVED_INFEASIBLE" if result is False else "NOT_PROVED",
            "horizon": args.horizon,
            "solver": args.solver,
            "time_limit_seconds": args.time_limit,
            "build_seconds": build_seconds,
            "solve_seconds": solve_seconds,
            "dominance": dominance,
            "formula": formula,
            "solver_stats": solver.accum_stats(),
        }
        if result is True:
            positive = {literal for literal in solver.get_model() if literal > 0}
            selected = [candidate for index, candidate in enumerate(candidates, start=1) if index in positive]
            payload["selected_feature_values"] = selected_feature_values(candidates, positive)
            payload["selected_action_count"] = sum(candidate.action != "keep" for candidate in selected)
            payload["selected_plan_count"] = len(selected)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"status": status, "proof": payload["proof"], "candidate_count": len(candidates), "clauses": formula["clause_count"], "output": str(args.output)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
