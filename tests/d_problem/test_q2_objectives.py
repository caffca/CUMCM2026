from __future__ import annotations

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from d_problem.candidates import generate_all_candidates  # noqa: E402
from d_problem.io import load_plans  # noqa: E402
from d_problem.objectives import (  # noqa: E402
    candidate_coefficients,
    objective_names,
    objective_value_from_selection,
)


class Q2ObjectiveTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        plans = load_plans(Path(__file__).resolve().parents[2] / "D题/附件/附件1.xlsx")
        cls.grouped, _ = generate_all_candidates(plans, horizon=643)

    def test_keep_cancel_adjust_coefficients(self) -> None:
        group = self.grouped[0]
        keep = next(candidate for candidate in group if candidate.action == "keep")
        frequency = next(candidate for candidate in group if candidate.action == "frequency")
        cancel = next(candidate for candidate in group if candidate.action == "cancel")
        self.assertEqual(candidate_coefficients(keep)["C"], 0)
        self.assertEqual(candidate_coefficients(keep)["M"], 0)
        self.assertEqual(candidate_coefficients(frequency)["M"], 1)
        self.assertEqual(candidate_coefficients(frequency)["P_A"], 1)
        self.assertEqual(candidate_coefficients(cancel)["C"], 1)
        self.assertEqual(candidate_coefficients(cancel)["P_A"], 1)

    def test_smax_is_max_not_sum(self) -> None:
        group = self.grouped[0]
        adjusted = [candidate for candidate in group if candidate.action == "frequency"][:2]
        metrics = objective_value_from_selection(adjusted, policy="T")
        self.assertEqual(metrics["S_max"], max(c.displacement_cost for c in adjusted))
        self.assertEqual(metrics["S_sum"], sum(c.displacement_cost for c in adjusted))

    def test_policy_orders(self) -> None:
        self.assertEqual(objective_names("T")[:2], ("C", "M"))
        self.assertEqual(objective_names("P")[:2], ("P_A", "C_A"))


if __name__ == "__main__":
    unittest.main()
