from __future__ import annotations

import random
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from d_problem.candidates import (  # noqa: E402
    candidates_conflict,
    generate_all_candidates,
    generate_cell_cliques,
    generate_conflict_edges,
    verify_mask_sample,
)
from d_problem.conflicts import states_conflict  # noqa: E402
from d_problem.io import load_plans  # noqa: E402


class Q2CandidateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.plans = load_plans(
            Path(__file__).resolve().parents[2] / "D题/附件/附件1.xlsx"
        )
        cls.grouped, cls.flat = generate_all_candidates(cls.plans, horizon=643)

    def test_candidate_count_and_boundaries(self) -> None:
        self.assertEqual(len(self.flat), 4582)
        self.assertEqual(min(map(len, self.grouped)), 22)
        self.assertEqual(max(map(len, self.grouped)), 32)
        for candidate in self.flat:
            if candidate.cancelled:
                continue
            self.assertGreaterEqual(candidate.f_start, 0)
            self.assertLessEqual(candidate.f_end, 100)
            self.assertTrue(candidate.time_masks)
            for mask in candidate.time_masks:
                if mask:
                    self.assertLessEqual(mask.bit_length(), 643)

    def test_mask_matches_canonical_on_deterministic_sample(self) -> None:
        pairs = list(zip(range(0, 1000), range(1000, 2000)))
        checked = verify_mask_sample(self.flat, pairs)
        self.assertEqual(checked, 1000)

    def test_cell_cliques_cover_every_edge(self) -> None:
        edges = set(generate_conflict_edges(self.grouped))
        cliques = generate_cell_cliques(self.flat)
        candidate_plan = {candidate.index: candidate.plan.plan_id for candidate in self.flat}
        clique_edges = {
            tuple(sorted((left, right)))
            for clique in cliques
            for pos, left in enumerate(clique)
            for right in clique[pos + 1 :]
            if candidate_plan[left] != candidate_plan[right]
        }
        self.assertEqual(edges, clique_edges)

    def test_keep_and_cancel_have_expected_semantics(self) -> None:
        for group in self.grouped:
            keep = next(candidate for candidate in group if candidate.action == "keep")
            cancel = next(candidate for candidate in group if candidate.action == "cancel")
            self.assertFalse(cancel.time_masks)
            self.assertFalse(candidates_conflict(keep, cancel))


if __name__ == "__main__":
    unittest.main()
