from __future__ import annotations

import sys
import unittest
from pathlib import Path
import re

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from d_problem.conflicts import (
    expand_occurrences,
    find_conflict_pairs,
    interval_overlap,
    states_conflict,
)
from d_problem.domain import Plan, PlanState
from d_problem.io import load_plans


class ConflictTests(unittest.TestCase):
    def make_plan(
        self,
        plan_id: str,
        f: tuple[int, int],
        t: tuple[int, int],
        gap: int = 0,
        count: int = 1,
    ) -> Plan:
        return Plan(plan_id, plan_id[0], f[0], f[1], t[0], t[1], gap, count)

    def test_touching_intervals_do_not_overlap(self) -> None:
        self.assertIsNone(interval_overlap(0, 2, 2, 4))
        self.assertIsNone(interval_overlap(0, 3, 3, 6))

    def test_both_dimensions_need_overlap(self) -> None:
        a = PlanState(self.make_plan("A001", (0, 2), (0, 2)))
        b = PlanState(self.make_plan("B001", (2, 4), (1, 3)))
        c = PlanState(self.make_plan("C001", (1, 3), (2, 4)))
        self.assertFalse(states_conflict(a, b)[0])
        self.assertFalse(states_conflict(a, c)[0])

    def test_periodic_later_window_is_detected(self) -> None:
        a = PlanState(self.make_plan("A001", (0, 3), (0, 2), gap=8, count=2))
        b = PlanState(self.make_plan("B001", (1, 2), (10, 12)))
        conflict, witness = states_conflict(a, b)
        self.assertTrue(conflict)
        self.assertIsNotNone(witness)
        self.assertEqual(witness.occurrence_i, 1)

    def test_sorted_pair_keeps_witness_orientation(self) -> None:
        a = PlanState(self.make_plan("A001", (0, 3), (0, 2)))
        b = PlanState(self.make_plan("B001", (1, 2), (1, 3)))
        pair = next(iter(find_conflict_pairs([b, a])))
        self.assertEqual((pair.plan_i, pair.plan_j), ("A001", "B001"))
        self.assertEqual((pair.witness.plan_i, pair.witness.plan_j), ("A001", "B001"))

    def test_c083_expands_to_final_boundary(self) -> None:
        plans = load_plans(Path(__file__).resolve().parents[2] / "D题/附件/附件1.xlsx")
        c083 = next(plan for plan in plans if plan.plan_id == "C083")
        occurrences = expand_occurrences(PlanState(c083))
        self.assertEqual(len(occurrences), 12)
        self.assertEqual((occurrences[-1].t_start, occurrences[-1].t_end), (641, 643))

    def test_full_attachment_matches_independent_grid_crosscheck(self) -> None:
        """Use cell sets, not the interval implementation, as a second Q1 check."""

        root = Path(__file__).resolve().parents[2]
        frame = pd.read_excel(root / "D题/附件/附件1.xlsx", dtype={"用频装备编号": str})
        interval = re.compile(r"\[\s*(\d+)\s*,\s*(\d+)\s*\)")
        cells: dict[str, set[tuple[int, int]]] = {}
        for _, row in frame.iterrows():
            plan_id = str(row["用频装备编号"])
            f_start, f_end = (int(x) for x in interval.fullmatch(str(row["频段区间"])).groups())
            t_start, t_end = (int(x) for x in interval.fullmatch(str(row["时间区间"])).groups())
            gap = int(row["间隔时长"])
            count = int(row["使用次数"])
            cells[plan_id] = {
                (f, t)
                for k in range(count)
                for f in range(f_start, f_end)
                for t in range(t_start + k * (t_end - t_start + gap), t_end + k * (t_end - t_start + gap))
            }

        grid_pairs = {
            tuple(sorted((left, right)))
            for left, left_cells in cells.items()
            for right, right_cells in cells.items()
            if left < right and left_cells.intersection(right_cells)
        }
        interval_pairs = {
            (pair.plan_i, pair.plan_j)
            for pair in find_conflict_pairs(
                [PlanState(plan) for plan in load_plans(root / "D题/附件/附件1.xlsx")]
            )
        }
        self.assertEqual(grid_pairs, interval_pairs)
        self.assertEqual(len(grid_pairs), 297)


if __name__ == "__main__":
    unittest.main()
