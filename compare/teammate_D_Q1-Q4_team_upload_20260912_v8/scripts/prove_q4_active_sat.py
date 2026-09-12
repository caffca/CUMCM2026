#!/usr/bin/env python3
"""Independent SAT threshold check using only non-revoke Q4 actions."""
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

from scripts.cutgen_q4_active import make_full_values
from scripts.solve_q1 import read_plans
from scripts.solve_q4_cp_sat import build_candidates, summarize


def key(candidate) -> tuple:
    return (candidate.plan_id, candidate.action, candidate.df, candidate.dt, candidate.dg)


def add_equals(cnf: CNF, literals: list[int], bound: int, top_id: int) -> int:
    """Add an exact cardinality constraint and return the updated variable bound."""
    if bound < 0 or bound > len(literals):
        cnf.append([])
        return top_id
    if bound == 0:
        for literal in literals:
            cnf.append([-literal])
        return top_id
    encoded = CardEnc.equals(
        lits=literals,
        bound=bound,
        top_id=top_id,
        encoding=EncType.totalizer,
    )
    cnf.extend(encoded.clauses)
    return max(top_id, encoded.nv)


def add_atmost(
    cnf: CNF,
    literals: list[int],
    bound: int,
    top_id: int,
    encoding: int = EncType.seqcounter,
) -> int:
    """Add an at-most cardinality constraint and return the new variable bound."""
    if bound < 0:
        cnf.append([])
        return top_id
    if bound >= len(literals):
        return top_id
    if bound == 0:
        for literal in literals:
            cnf.append([-literal])
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


def add_atleast(
    cnf: CNF,
    literals: list[int],
    bound: int,
    top_id: int,
    encoding: int = EncType.seqcounter,
) -> int:
    """Add an at-least cardinality constraint and return the new variable bound."""
    if bound <= 0:
        return top_id
    if bound > len(literals):
        cnf.append([])
        return top_id
    if bound == len(literals):
        for literal in literals:
            cnf.append([literal])
        return top_id
    encoded = CardEnc.atleast(
        lits=literals,
        bound=bound,
        top_id=top_id,
        encoding=encoding,
    )
    cnf.extend(encoded.clauses)
    return max(top_id, encoded.nv)


def add_exact_compact(cnf: CNF, literals: list[int], bound: int, top_id: int) -> int:
    """Add a small exact-cardinality constraint with a compact 0/1 encoding."""
    if bound < 0 or bound > len(literals):
        cnf.append([])
        return top_id
    if bound == 0:
        for literal in literals:
            cnf.append([-literal])
        return top_id
    if bound == 1:
        cnf.append(list(literals))
        encoded = CardEnc.atmost(
            lits=literals,
            bound=1,
            top_id=top_id,
            encoding=EncType.seqcounter,
        )
        cnf.extend(encoded.clauses)
        return max(top_id, encoded.nv)
    return add_equals(cnf, literals, bound, top_id)


def prune_dominated_active_candidates(
    candidates: list,
    preserve_adjustment_feature: bool = False,
    preserve_normalized_shift: bool = False,
) -> tuple[list, dict]:
    """Remove active actions whose external conflict set is dominated.

    For one plan, if N(b) is a subset of N(a), replacing action a by b can
    never create a new resource conflict.  Same-plan candidates are never
    conflict edges, because exactly one action is selected for each plan.
    Equal conflict sets keep the first candidate as a deterministic
    representative.  This is an equivalence-preserving reduction for the
    active-plan threshold, not a heuristic.
    """
    active = [candidate for candidate in candidates if candidate.action != "revoke"]
    by_cell: defaultdict[tuple[int, int], list[int]] = defaultdict(list)
    by_plan: defaultdict[str, list[int]] = defaultdict(list)
    for index, candidate in enumerate(active):
        by_plan[candidate.plan_id].append(index)
        for cell in candidate.cells:
            by_cell[cell].append(index)

    neighbors = [set() for _ in active]
    for indexes in by_cell.values():
        if len(indexes) < 2:
            continue
        for position, left in enumerate(indexes):
            for right in indexes[position + 1 :]:
                if active[left].plan_id == active[right].plan_id:
                    continue
                neighbors[left].add(right)
                neighbors[right].add(left)

    feature_signature = {
        index: (
            candidate.category,
            candidate.action in {"freq", "time", "gap"},
        )
        for index, candidate in enumerate(active)
    }
    normalized_shift = {
        index: abs(candidate.df) + 2 * abs(candidate.dt) + abs(candidate.dg)
        for index, candidate in enumerate(active)
    }
    removed: set[int] = set()
    equal_representatives = 0
    for indexes in by_plan.values():
        for left in indexes:
            if left in removed:
                continue
            for right in indexes:
                if left == right:
                    continue
                if preserve_adjustment_feature and feature_signature[left] != feature_signature[right]:
                    continue
                if preserve_normalized_shift and normalized_shift[right] > normalized_shift[left]:
                    continue
                if neighbors[right] <= neighbors[left]:
                    if neighbors[right] != neighbors[left] or right < left:
                        removed.add(left)
                        if neighbors[right] == neighbors[left]:
                            equal_representatives += 1
                        break

    kept = [candidate for index, candidate in enumerate(active) if index not in removed]
    details = {
        "enabled": True,
        "input_active_candidate_count": len(active),
        "removed_active_candidate_count": len(removed),
        "kept_active_candidate_count": len(kept),
        "plans_with_removed_actions": sum(
            any(index in removed for index in indexes) for indexes in by_plan.values()
        ),
        "equal_conflict_set_representatives_removed": equal_representatives,
        "rule": "within one plan, remove a when external_conflicts(b) is a subset of external_conflicts(a)",
    }
    if preserve_adjustment_feature and preserve_normalized_shift:
        details["preserves_features"] = ["category", "is_adjusted", "normalized_shift_not_increased"]
        details["rule"] = (
            "within one plan, remove a when b has the same category/adjusted flag, "
            "N_ext(b) subseteq N_ext(a), and S10(b) <= S10(a)"
        )
    elif preserve_adjustment_feature:
        details["preserves_features"] = ["category", "is_adjusted"]
        details["rule"] = (
            "within one plan, remove a when b has the same category/adjusted flag, "
            "and N_ext(b) subseteq N_ext(a)"
        )
    elif preserve_normalized_shift:
        raise ValueError("preserve_normalized_shift requires preserve_adjustment_feature")
    return kept, details


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=Path("data/raw/D题/附件/附件1.xlsx"))
    parser.add_argument("--horizon", type=int, default=643)
    parser.add_argument("--target-active", type=int, default=148)
    parser.add_argument(
        "--exact-revokes",
        type=int,
        help="Use an equality for the number of inactive plans. For target-active=148, exact-revokes=2 is equivalent to R<=2.",
    )
    parser.add_argument(
        "--revoke-category-count",
        action="append",
        default=[],
        metavar="CATEGORY=COUNT",
        help="Optionally fix the exact number of revoked plans in category A, B, or C; repeat per category.",
    )
    parser.add_argument(
        "--no-dominance-pruning",
        action="store_true",
        help="Keep all active actions instead of the equivalence-preserving conflict-set reduction.",
    )
    parser.add_argument(
        "--feature-aware-dominance",
        action="store_true",
        help="Use dominance pruning that preserves category and adjusted/keep indicators; safe with adjustment and S10 thresholds.",
    )
    parser.add_argument(
        "--adjustment-aware-dominance",
        action="store_true",
        help="Use dominance pruning that preserves category and adjusted/keep indicators; safe for M thresholds without preserving S10.",
    )
    parser.add_argument(
        "--compact-category-cardinality",
        action="store_true",
        help="When all A/B/C exact revoke counts are supplied, encode their small cardinalities directly and omit the redundant total equality.",
    )
    parser.add_argument(
        "--exact-adjust",
        type=int,
        help="Fix the total number of active adjusted actions exactly; useful after a prior M layer is closed.",
    )
    parser.add_argument(
        "--max-adjust",
        type=int,
        help="Add an upper threshold for the total number of active adjusted actions.",
    )
    parser.add_argument(
        "--min-keeps",
        type=int,
        help="Add a lower threshold for kept active plans; for fixed 147 active plans, min-keeps=10 is equivalent to M<=137.",
    )
    parser.add_argument(
        "--max-adjust-category",
        action="append",
        default=[],
        metavar="CATEGORY=COUNT",
        help="Add an upper threshold for adjusted actions in category A, B, or C; repeat per category.",
    )
    parser.add_argument(
        "--max-normalized-shift",
        type=int,
        help="Add an upper threshold for S10=sum(|df|+2|dt|+|dg|) over the selected actions.",
    )
    parser.add_argument("--solver", default="cadical195")
    parser.add_argument("--time-limit", type=float, default=300.0)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    build_started = perf_counter()
    plans = read_plans(args.input)
    all_candidates = build_candidates(plans, args.horizon)
    if sum([args.no_dominance_pruning, args.feature_aware_dominance, args.adjustment_aware_dominance]) > 1:
        raise ValueError("dominance mode flags are mutually exclusive")
    if args.no_dominance_pruning:
        active_candidates = [candidate for candidate in all_candidates if candidate.action != "revoke"]
        dominance = {
            "enabled": False,
            "input_active_candidate_count": len(active_candidates),
            "removed_active_candidate_count": 0,
            "kept_active_candidate_count": len(active_candidates),
        }
    else:
        active_candidates, dominance = prune_dominated_active_candidates(
            all_candidates,
            preserve_adjustment_feature=(args.feature_aware_dominance or args.adjustment_aware_dominance),
            preserve_normalized_shift=args.feature_aware_dominance,
        )
    cnf = CNF()
    top_id = len(active_candidates) + len(plans)
    by_plan: defaultdict[str, list[int]] = defaultdict(list)
    by_cell: defaultdict[tuple[int, int], list[int]] = defaultdict(list)
    for index, candidate in enumerate(active_candidates, start=1):
        by_plan[candidate.plan_id].append(index)
        for cell in candidate.cells:
            by_cell[cell].append(index)
    plan_active_literals = []
    for plan_index, plan in enumerate(plans):
        literals = by_plan[plan["id"]]
        # Pairwise at-most-one is smaller than a sequential counter for these
        # domains (at most 50 actions per plan).
        for position, left in enumerate(literals):
            for right in literals[position + 1 :]:
                cnf.append([-left, -right])
        active_indicator = len(active_candidates) + plan_index + 1
        plan_active_literals.append(active_indicator)
        for literal in literals:
            cnf.append([-literal, active_indicator])
        cnf.append([-active_indicator, *literals])
    conflict_edges = {
        (left, right)
        for literals in by_cell.values()
        if len(literals) >= 2
        for position, left in enumerate(literals)
        for right in literals[position + 1 :]
        if active_candidates[left - 1].plan_id != active_candidates[right - 1].plan_id
    }
    for left, right in conflict_edges:
        cnf.append([-left, -right])
    inactive_indicators = [-literal for literal in plan_active_literals]
    inactive_bound = len(plans) - args.target_active
    exact_revokes = args.exact_revokes

    category_counts = {}
    for raw_count in args.revoke_category_count:
        category, raw_value = raw_count.split("=", 1)
        if category not in {"A", "B", "C"}:
            raise ValueError(f"unknown category: {category}")
        if category in category_counts:
            raise ValueError(f"duplicate category count: {category}")
        category_counts[category] = int(raw_value)
    compact_categories = args.compact_category_cardinality and set(category_counts) == {"A", "B", "C"}

    if compact_categories and exact_revokes is not None and sum(category_counts.values()) != exact_revokes:
        cnf.append([])
    if compact_categories and inactive_bound >= 0 and sum(category_counts.values()) != inactive_bound:
        cnf.append([])

    if compact_categories:
        # The three disjoint category counts already imply the total inactive
        # count, so the global exact/at-most constraint would be redundant.
        cardinality_mode = "compact_category_exact"
    elif exact_revokes is None and inactive_bound < 0:
        cnf.append([])
        cardinality_mode = "global_atmost"
    elif exact_revokes is not None:
        top_id = add_equals(cnf, inactive_indicators, exact_revokes, top_id)
        cardinality_mode = "global_exact_plus_category_exact" if category_counts else "global_exact"
    elif inactive_bound < len(inactive_indicators):
        encoded = CardEnc.atmost(
            lits=inactive_indicators,
            bound=inactive_bound,
            top_id=top_id,
            encoding=EncType.seqcounter,
        )
        cnf.extend(encoded.clauses)
        top_id = max(top_id, encoded.nv)
        cardinality_mode = "global_atmost"
    else:
        cardinality_mode = "none"
    for category, count in category_counts.items():
        category_literals = [
            -plan_active_literals[index]
            for index, plan in enumerate(plans)
            if plan["category"] == category
        ]
        top_id = (
            add_exact_compact(cnf, category_literals, count, top_id)
            if compact_categories
            else add_equals(cnf, category_literals, count, top_id)
        )

    adjust_literals = [
        index
        for index, candidate in enumerate(active_candidates, start=1)
        if candidate.action in {"freq", "time", "gap"}
    ]
    if args.exact_adjust is not None:
        top_id = add_equals(cnf, adjust_literals, args.exact_adjust, top_id)
    if args.max_adjust is not None:
        top_id = add_atmost(
            cnf,
            adjust_literals,
            args.max_adjust,
            top_id,
            encoding=EncType.kmtotalizer,
        )
    keep_literals = [
        index
        for index, candidate in enumerate(active_candidates, start=1)
        if candidate.action == "keep"
    ]
    if args.min_keeps is not None:
        top_id = add_atleast(
            cnf,
            keep_literals,
            args.min_keeps,
            top_id,
            encoding=EncType.seqcounter,
        )
    max_adjust_category = {}
    for raw_value in args.max_adjust_category:
        category, raw_count = raw_value.split("=", 1)
        if category not in {"A", "B", "C"}:
            raise ValueError(f"unknown adjusted category: {category}")
        if category in max_adjust_category:
            raise ValueError(f"duplicate adjusted category: {category}")
        max_adjust_category[category] = int(raw_count)
        category_adjust_literals = [
            index
            for index, candidate in enumerate(active_candidates, start=1)
            if candidate.category == category and candidate.action in {"freq", "time", "gap"}
        ]
        top_id = add_atmost(
            cnf,
            category_adjust_literals,
            max_adjust_category[category],
            top_id,
            encoding=EncType.kmtotalizer,
        )

    normalized_shift_encoding = None
    if args.max_normalized_shift is not None:
        # With exactly one candidate selected per plan, an integer candidate
        # cost can be represented exactly by threshold indicators:
        # cost_p = sum_k 1[cost_p >= k].  The global S10 threshold is then an
        # ordinary cardinality constraint.  This avoids using a weighted
        # pseudo-Boolean relaxation and keeps the terminal proof auditable.
        level_literals = []
        maximum_cost_per_plan = 0
        maximum_possible_sum = 0
        for plan in plans:
            plan_literals = by_plan[plan["id"]]
            costs = [
                abs(active_candidates[literal - 1].df)
                + 2 * abs(active_candidates[literal - 1].dt)
                + abs(active_candidates[literal - 1].dg)
                for literal in plan_literals
            ]
            plan_maximum = max(costs, default=0)
            maximum_cost_per_plan = max(maximum_cost_per_plan, plan_maximum)
            maximum_possible_sum += plan_maximum
            for level in range(1, plan_maximum + 1):
                positive = [
                    literal
                    for literal, cost in zip(plan_literals, costs)
                    if cost >= level
                ]
                top_id += 1
                indicator = top_id
                if positive:
                    for literal in positive:
                        cnf.append([-literal, indicator])
                    cnf.append([-indicator, *positive])
                else:
                    cnf.append([-indicator])
                level_literals.append(indicator)
        top_id = add_atmost(
            cnf,
            level_literals,
            args.max_normalized_shift,
            top_id,
            encoding=EncType.kmtotalizer,
        )
        normalized_shift_encoding = {
            "encoding": "plan-cost-threshold-indicators+kmtotalizer",
            "maximum_cost_per_plan": maximum_cost_per_plan,
            "maximum_possible_sum": maximum_possible_sum,
            "level_indicator_count": len(level_literals),
            "bound": args.max_normalized_shift,
        }

    build_seconds = perf_counter() - build_started
    with Solver(name=args.solver, bootstrap_with=cnf.clauses) as solver:
        solve_started = perf_counter()
        if args.time_limit > 0:
            timer = threading.Timer(args.time_limit, solver.interrupt)
            timer.daemon = True
            timer.start()
            try:
                result = solver.solve_limited(expect_interrupt=True)
            finally:
                timer.cancel()
        else:
            result = solver.solve()
        solve_seconds = perf_counter() - solve_started
        status = "SAT" if result is True else "UNSAT" if result is False else "UNKNOWN"
        payload = {
            "question": "D-Q4",
            "mode": "independent_active_sat_threshold",
            "method": "PySAT + deduplicated candidate conflict edges + plan at-most-one + active-cardinality lower bound",
            "status": status,
            "proof": "FEASIBLE_WITNESS" if result is True else "PROVED_INFEASIBLE" if result is False else "NOT_PROVED",
            "time_domain": [0, args.horizon],
            "frequency_domain": [0, 100],
            "target_active": args.target_active,
            "exact_revokes": exact_revokes,
            "revoke_category_counts": category_counts,
            "exact_adjust": args.exact_adjust,
            "max_adjust": args.max_adjust,
            "min_keeps": args.min_keeps,
            "max_adjust_category": max_adjust_category,
            "max_normalized_shift": args.max_normalized_shift,
            "normalized_shift_encoding": normalized_shift_encoding,
            "cardinality_mode": cardinality_mode,
            "dominance_pruning": dominance,
            "feature_aware_dominance": args.feature_aware_dominance,
            "adjustment_aware_dominance": args.adjustment_aware_dominance,
            "plan_count": len(plans),
            "candidate_count": len(active_candidates),
            "plan_activation_variable_count": len(plan_active_literals),
            "base_variable_count": len(active_candidates) + len(plan_active_literals),
            "resource_cell_count": len(by_cell),
            "conflict_edge_count": len(conflict_edges),
            "encoded_variable_count": top_id,
            "clause_count": len(cnf.clauses),
            "solver": args.solver,
            "build_seconds": build_seconds,
            "solve_seconds": solve_seconds,
            "solver_stats": solver.accum_stats(),
        }
        if result is True:
            positive = {literal for literal in solver.get_model() if literal > 0}
            selected = [
                candidate
                for index, candidate in enumerate(active_candidates, start=1)
                if index in positive
            ]
            selected_by_plan = {candidate.plan_id: candidate for candidate in selected}
            all_values = [0] * len(all_candidates)
            all_lookup = {key(candidate): index for index, candidate in enumerate(all_candidates)}
            for candidate in selected:
                all_values[all_lookup[key(candidate)]] = 1
            for plan in plans:
                if plan["id"] not in selected_by_plan:
                    all_values[all_lookup[(plan["id"], "revoke", 0, 0, 0)]] = 1
            payload["summary"] = summarize(plans, all_candidates, all_values)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"status": status, "proof": payload["proof"], "output": str(args.output)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
