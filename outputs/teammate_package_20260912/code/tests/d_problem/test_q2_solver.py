from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from d_problem.candidates import (  # noqa: E402
    generate_all_candidates,
    generate_cell_clique_map,
    generate_cell_cliques,
    generate_conflict_edges,
)
from d_problem.domain import Plan  # noqa: E402
from d_problem.q2_model import SolverConfig, solve_lexicographic  # noqa: E402


class Q2SolverTests(unittest.TestCase):
    def test_full_and_lazy_agree_on_tiny_instance(self) -> None:
        plans = [
            Plan("A001", "A", 0, 2, 0, 2, 2, 1),
            Plan("B001", "B", 0, 2, 0, 2, 2, 1),
        ]
        grouped, flat = generate_all_candidates(plans, horizon=20)
        edges = generate_conflict_edges(grouped)
        cells = generate_cell_cliques(flat)
        config = SolverConfig(time_limit_seconds=2, num_search_workers=1, random_seed=7)
        full = solve_lexicographic(
            grouped,
            flat,
            policy="T",
            mode="full",
            edges=edges,
            cell_cliques=cells,
            constraint_form="cells",
            config=config,
        )
        lazy = solve_lexicographic(
            grouped,
            flat,
            policy="T",
            mode="lazy",
            edges=[],
            cell_clique_map=generate_cell_clique_map(flat),
            constraint_form="edges",
            config=config,
            max_lazy_iterations=100,
        )
        self.assertTrue(full.proven_optimal)
        self.assertTrue(lazy.proven_optimal)
        self.assertEqual(dict(full.metrics), dict(lazy.metrics))
        self.assertEqual(full.metrics["C"], 0)

        # A certified prefix may be supplied when a separate boundary run
        # already proved the first lexicographic layer.  The remaining layers
        # must retain the same exact result on this tiny instance.
        fixed = solve_lexicographic(
            grouped,
            flat,
            policy="T",
            mode="full",
            edges=edges,
            cell_cliques=cells,
            constraint_form="cells",
            config=config,
            fixed_initial={"C": 0},
        )
        self.assertTrue(fixed.proven_optimal)
        self.assertEqual(dict(fixed.metrics), dict(full.metrics))


if __name__ == "__main__":
    unittest.main()
