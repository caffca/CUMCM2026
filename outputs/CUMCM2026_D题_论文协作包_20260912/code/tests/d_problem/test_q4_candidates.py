from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))

from d_problem.candidates import generate_all_candidates as generate_q2
from d_problem.io import load_plans
from d_problem.q4_candidates import generate_all_candidates as generate_q4


ROOT = Path(__file__).resolve().parents[3]
ATTACHMENT = ROOT / "data" / "附件1.xlsx"


class Q4CandidateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.plans = load_plans(ATTACHMENT)
        cls.q2_groups, cls.q2_flat = generate_q2(cls.plans, horizon=643)
        cls.q4_groups, cls.q4_flat = generate_q4(cls.plans, horizon=643)

    def test_q4_extends_q2_state_ids_without_replacing_them(self):
        q2_ids = {candidate.state_id for candidate in self.q2_flat}
        q4_ids = {candidate.state_id for candidate in self.q4_flat}
        self.assertTrue(q2_ids <= q4_ids)
        self.assertEqual(len(self.q2_flat), 4582)
        self.assertEqual(len(self.q4_flat), 6103)
        self.assertEqual(
            sum(candidate.action == "gap" for candidate in self.q4_flat), 1521
        )

    def test_gap_states_are_c_only_and_within_horizon(self):
        gap_states = [candidate for candidate in self.q4_flat if candidate.action == "gap"]
        self.assertTrue(gap_states)
        self.assertTrue(all(candidate.category == "C" for candidate in gap_states))
        for candidate in gap_states:
            self.assertNotEqual(candidate.state.gap_shift, 0)
            self.assertEqual(candidate.state.f_shift, 0)
            self.assertEqual(candidate.state.t_shift, 0)
            plan = candidate.plan
            self.assertGreaterEqual(plan.gap + candidate.state.gap_shift, 0)
            last_end = plan.t_end + (plan.count - 1) * (
                plan.period + candidate.state.gap_shift
            )
            self.assertLessEqual(last_end, 643)

    def test_each_plan_has_exactly_one_keep_and_cancel(self):
        for group in self.q4_groups:
            self.assertEqual(sum(candidate.action == "keep" for candidate in group), 1)
            self.assertEqual(sum(candidate.action == "cancel" for candidate in group), 1)


if __name__ == "__main__":
    unittest.main()
