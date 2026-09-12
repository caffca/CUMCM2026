"""Independent small-instance validation for the Q2 state model.

The full 150-plan instance is too large for exhaustive enumeration.  This script
selects three deterministic four-plan subsets, enumerates every conflict-free
state combination, and compares the exact lexicographic T vector with the edge,
cell-clique, and lazy CP-SAT formulations.  It is a model/implementation check,
not a proof of the full-instance optimum.
"""

from __future__ import annotations

import json
import math
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from d_problem.candidates import (  # noqa: E402
    CandidateState,
    candidates_conflict,
    generate_all_candidates,
    generate_cell_clique_map,
    generate_cell_cliques,
    generate_conflict_edges,
    verify_mask_sample,
)
from d_problem.conflicts import states_conflict  # noqa: E402
from d_problem.io import load_plans  # noqa: E402
from d_problem.objectives import objective_names, objective_value_from_selection  # noqa: E402
from d_problem.q2_model import SolverConfig, solve_lexicographic, validate_selected_pairwise  # noqa: E402
from d_problem.validation import validate_schedule  # noqa: E402


SUBSETS = (
    ("A001", "B001", "C001", "C002"),
    ("B009", "C028", "A003", "C018"),
    ("B016", "C051", "C031", "B021"),
)


def _vector(selected: tuple[CandidateState, ...]) -> list[int]:
    metrics = objective_value_from_selection(selected, policy="T")
    return [int(metrics[name]) for name in objective_names("T")]


def _brute_force(grouped: list[list[CandidateState]]) -> tuple[tuple[CandidateState, ...], list[int], int, int]:
    """Enumerate all conflict-free choices using the independent mask predicate."""

    group_count = len(grouped)
    pair_conflicts: dict[tuple[int, int], list[list[bool]]] = {}
    for left in range(group_count):
        for right in range(left + 1, group_count):
            pair_conflicts[(left, right)] = [
                [candidates_conflict(a, b) for b in grouped[right]]
                for a in grouped[left]
            ]

    best: tuple[tuple[int, ...], tuple[CandidateState, ...]] | None = None
    feasible_leaves = 0
    visited_nodes = 0

    def recurse(group_index: int, chosen: list[CandidateState]) -> None:
        nonlocal best, feasible_leaves, visited_nodes
        visited_nodes += 1
        if group_index == group_count:
            feasible_leaves += 1
            current = tuple(chosen)
            key = tuple(_vector(current))
            if best is None or key < best[0]:
                best = (key, current)
            return
        for candidate_position, candidate in enumerate(grouped[group_index]):
            compatible = True
            for previous_group, previous in enumerate(chosen):
                matrix = pair_conflicts[(previous_group, group_index)]
                previous_position = grouped[previous_group].index(previous)
                if matrix[previous_position][candidate_position]:
                    compatible = False
                    break
            if compatible:
                chosen.append(candidate)
                recurse(group_index + 1, chosen)
                chosen.pop()

    recurse(0, [])
    if best is None:
        raise RuntimeError("subset unexpectedly has no feasible state combination")
    return best[1], list(best[0]), feasible_leaves, visited_nodes


def main() -> None:
    all_plans = load_plans(ROOT / "D题/附件/附件1.xlsx")
    by_id = {plan.plan_id: plan for plan in all_plans}
    records: list[dict[str, object]] = []
    for subset in SUBSETS:
        plans = [by_id[plan_id] for plan_id in subset]
        started = time.perf_counter()
        grouped, flat = generate_all_candidates(plans, horizon=643)
        edges = generate_conflict_edges(grouped)
        cliques = generate_cell_cliques(flat)
        sampled = verify_mask_sample(flat, edges[: min(250, len(edges))] + edges[-min(250, len(edges)):]) if edges else 0
        brute_selected, brute_vector, leaves, nodes = _brute_force(grouped)
        brute_validation = validate_schedule([candidate.state for candidate in brute_selected], horizon=643)
        config = SolverConfig(time_limit_seconds=30.0, num_search_workers=8, random_seed=20260912)
        edge_result = solve_lexicographic(
            grouped, flat, policy="T", mode="full", edges=edges, cell_cliques=(),
            constraint_form="edges", config=config,
        )
        cell_result = solve_lexicographic(
            grouped, flat, policy="T", mode="full", edges=edges, cell_cliques=cliques,
            constraint_form="cells", config=config,
        )
        lazy_result = solve_lexicographic(
            grouped, flat, policy="T", mode="lazy", edges=(), cell_cliques=(),
            cell_clique_map=generate_cell_clique_map(flat), constraint_form="edges",
            config=config, max_lazy_iterations=100,
        )
        solver_records = {}
        for label, result in (("edge", edge_result), ("cell", cell_result), ("lazy", lazy_result)):
            selected = result.selected
            validation = validate_schedule([candidate.state for candidate in selected], horizon=643) if selected else None
            solver_records[label] = {
                "vector": _vector(selected) if selected else None,
                "proven_optimal": result.proven_optimal,
                "layers": result.layer_dicts(),
                "pairwise_conflicts": validate_selected_pairwise(selected) if selected else None,
                "canonical_conflicts": validation.conflict_count if validation else None,
                "canonical_ok": validation.ok if validation else False,
            }
        elapsed = time.perf_counter() - started
        records.append(
            {
                "plans": list(subset),
                "candidate_counts": [len(group) for group in grouped],
                "candidate_product": math.prod(len(group) for group in grouped),
                "state_conflict_edges": len(edges),
                "cell_cliques": len(cliques),
                "mask_sample_checked": sampled,
                "brute_force": {
                    "objective_vector": brute_vector,
                    "feasible_leaves": leaves,
                    "visited_nodes": nodes,
                    "canonical_conflicts": brute_validation.conflict_count,
                    "canonical_ok": brute_validation.ok,
                },
                "solvers": solver_records,
                "all_solver_vectors_match_brute": all(
                    record["vector"] == brute_vector for record in solver_records.values()
                ),
                "all_solver_valid": all(
                    record["canonical_ok"] and record["canonical_conflicts"] == 0
                    and record["pairwise_conflicts"] == 0
                    for record in solver_records.values()
                ),
                "seconds": elapsed,
            }
        )
    output = ROOT / "outputs/q2/subset_validation.json"
    output.write_text(
        json.dumps(
            {
                "purpose": "small-instance exhaustive cross-check; not full-instance optimality proof",
                "horizon": 643,
                "objective": list(objective_names("T")),
                "subsets": records,
                "all_subsets_pass": all(
                    item["all_solver_vectors_match_brute"] and item["all_solver_valid"]
                    for item in records
                ),
            },
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    print(json.dumps({"output": str(output), "all_subsets_pass": all(item["all_solver_vectors_match_brute"] and item["all_solver_valid"] for item in records)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
