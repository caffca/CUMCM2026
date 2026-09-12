"""Finite Q4 candidate states with optional C-class gap adjustment.

Q4 starts from the raw attachment-1 plans.  It reuses the Q2 keep/frequency/time/
cancel states and adds, for C plans only, a ``gap`` state whose interval gap is
changed by a non-zero integer amount with absolute value at most 10.  Every
candidate is a complete plan state; all repeated windows are represented by the
same integer time-mask interface used by the Q2 resource-cell model.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations, product
from typing import Sequence

from .conflicts import states_conflict
from .domain import Plan, PlanState


@dataclass(frozen=True, slots=True)
class Q4Candidate:
    """One legal Q4 state together with exact integer occupancy masks."""

    index: int
    state_id: str
    state: PlanState
    action: str
    shift: int
    f_start: int
    f_end: int
    time_masks: tuple[int, ...]

    @property
    def plan(self) -> Plan:
        return self.state.plan

    @property
    def category(self) -> str:
        return self.plan.category

    @property
    def cancelled(self) -> bool:
        return self.action == "cancel"

    @property
    def adjusted(self) -> bool:
        return self.action in {"frequency", "time", "gap"}

    @property
    def disturbed(self) -> bool:
        return self.action != "keep"

    @property
    def displacement_cost(self) -> int:
        """Integer-scaled Q4 displacement: |df| + 2|dt| + |dg|."""

        return (
            abs(self.state.f_shift)
            + 2 * abs(self.state.t_shift)
            + abs(self.state.gap_shift)
        )


def _time_masks(state: PlanState) -> tuple[int, int, tuple[int, ...]]:
    if state.action == "cancel":
        return 0, 0, ()
    plan = state.plan
    f_start = plan.f_start + state.f_shift
    f_end = plan.f_end + state.f_shift
    period = plan.duration + plan.gap + state.gap_shift
    base = (1 << plan.duration) - 1
    masks = [0] * (f_end - f_start)
    for k in range(plan.count):
        start = plan.t_start + state.t_shift + k * period
        occurrence_mask = base << start
        for offset in range(len(masks)):
            masks[offset] |= occurrence_mask
    return f_start, f_end, tuple(masks)


def _make_candidate(index: int, state: PlanState, action: str, shift: int) -> Q4Candidate:
    f_start, f_end, masks = _time_masks(state)
    return Q4Candidate(
        index=index,
        state_id=f"{state.plan.plan_id}:{action}:{shift:+d}",
        state=state,
        action=action,
        shift=shift,
        f_start=f_start,
        f_end=f_end,
        time_masks=masks,
    )


def generate_candidates(plan: Plan, horizon: int = 643) -> list[Q4Candidate]:
    """Enumerate all legal Q4 states for one plan."""

    states: list[tuple[str, int, PlanState]] = [("keep", 0, PlanState(plan))]
    for shift in range(-10, 11):
        if shift == 0:
            continue
        if plan.f_start + shift < 0 or plan.f_end + shift > 100:
            continue
        states.append(
            (
                "frequency",
                shift,
                PlanState(plan, action="frequency", f_shift=shift),
            )
        )
    for shift in range(-5, 6):
        if shift == 0:
            continue
        last_end = plan.t_end + (plan.count - 1) * plan.period + shift
        if plan.t_start + shift < 0 or last_end > horizon:
            continue
        states.append(
            (
                "time",
                shift,
                PlanState(plan, action="time", t_shift=shift),
            )
        )

    if plan.category == "C":
        # Original gap is 8.  |g'-8|<=10 and g'>=0 gives gap shifts -8..10.
        for shift in range(-10, 11):
            if shift == 0 or plan.gap + shift < 0:
                continue
            period = plan.period + shift
            if plan.t_end + (plan.count - 1) * period > horizon:
                continue
            states.append(
                (
                    "gap",
                    shift,
                    PlanState(plan, action="gap", gap_shift=shift),
                )
            )

    states.append(("cancel", 0, PlanState(plan, action="cancel")))
    return [
        _make_candidate(index, state, action, shift)
        for index, (action, shift, state) in enumerate(states)
    ]


def generate_all_candidates(
    plans: Sequence[Plan], horizon: int = 643
) -> tuple[list[list[Q4Candidate]], list[Q4Candidate]]:
    grouped: list[list[Q4Candidate]] = []
    flat: list[Q4Candidate] = []
    next_index = 0
    for plan in plans:
        group: list[Q4Candidate] = []
        for candidate in generate_candidates(plan, horizon=horizon):
            candidate = Q4Candidate(
                index=next_index,
                state_id=candidate.state_id,
                state=candidate.state,
                action=candidate.action,
                shift=candidate.shift,
                f_start=candidate.f_start,
                f_end=candidate.f_end,
                time_masks=candidate.time_masks,
            )
            group.append(candidate)
            flat.append(candidate)
            next_index += 1
        grouped.append(group)
    return grouped, flat


def candidates_conflict(left: Q4Candidate, right: Q4Candidate) -> bool:
    if left.cancelled or right.cancelled:
        return False
    lo = max(left.f_start, right.f_start)
    hi = min(left.f_end, right.f_end)
    if lo >= hi:
        return False
    for frequency in range(lo, hi):
        if left.time_masks[frequency - left.f_start] & right.time_masks[frequency - right.f_start]:
            return True
    return False


def selected_conflicts(selected: Sequence[Q4Candidate]) -> list[tuple[int, int]]:
    return [
        (left.index, right.index)
        for left, right in combinations(selected, 2)
        if candidates_conflict(left, right)
    ]


def generate_conflict_edges(
    grouped: Sequence[Sequence[Q4Candidate]],
) -> list[tuple[int, int]]:
    edges: list[tuple[int, int]] = []
    for left_group, right_group in combinations(grouped, 2):
        for left, right in product(left_group, right_group):
            if candidates_conflict(left, right):
                edges.append((left.index, right.index))
    return edges


def generate_cell_cliques(flat: Sequence[Q4Candidate]) -> list[tuple[int, ...]]:
    cells: dict[tuple[int, int], list[int]] = {}
    for candidate in flat:
        if candidate.cancelled:
            continue
        for offset, mask in enumerate(candidate.time_masks):
            frequency = candidate.f_start + offset
            remaining = mask
            while remaining:
                lowest = remaining & -remaining
                time_slot = lowest.bit_length() - 1
                cells.setdefault((frequency, time_slot), []).append(candidate.index)
                remaining ^= lowest
    return [tuple(indices) for indices in cells.values() if len(indices) > 1]


def verify_mask_sample(
    flat: Sequence[Q4Candidate], pairs: Sequence[tuple[int, int]]
) -> int:
    by_index = {candidate.index: candidate for candidate in flat}
    checked = 0
    for left_index, right_index in pairs:
        left = by_index[left_index]
        right = by_index[right_index]
        canonical, _ = states_conflict(left.state, right.state)
        accelerated = candidates_conflict(left, right)
        if canonical != accelerated:
            raise AssertionError(
                f"mask mismatch for {left.state_id} and {right.state_id}: "
                f"canonical={canonical}, mask={accelerated}"
            )
        checked += 1
    return checked
