"""Finite Q2 candidate states and an exact bit-mask compatibility index.

The candidate set follows the Q2 interpretation frozen in the modeling record:
keep, one non-zero frequency shift, one non-zero first-use time shift, or
cancel.  Frequency/time masks are only an acceleration of the same half-open
integer occupancy semantics used by :mod:`d_problem.conflicts`.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations, product
from typing import Iterable, Sequence

from .conflicts import states_conflict
from .domain import Plan, PlanState


@dataclass(frozen=True, slots=True)
class CandidateState:
    """One legal Q2 state together with an exact occupancy bit mask."""

    index: int
    state_id: str
    state: PlanState
    action: str
    shift: int
    f_start: int
    f_end: int
    # One integer time mask per frequency slot in [f_start, f_end).
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
        return self.action in {"frequency", "time"}

    @property
    def disturbed(self) -> bool:
        return self.action != "keep"

    @property
    def displacement_cost(self) -> int:
        """Integer-scaled Q2 displacement: |df| + 2|dt|."""

        return abs(self.state.f_shift) + 2 * abs(self.state.t_shift)


def _time_masks(state: PlanState) -> tuple[int, int, tuple[int, ...]]:
    """Build (frequency start, end, masks) for a non-cancelled state."""

    if state.action == "cancel":
        return 0, 0, ()
    plan = state.plan
    f_start = plan.f_start + state.f_shift
    f_end = plan.f_end + state.f_shift
    duration = plan.duration
    period = plan.period
    base = (1 << duration) - 1
    masks = [0] * (f_end - f_start)
    for k in range(plan.count):
        start = plan.t_start + state.t_shift + k * period
        occurrence_mask = base << start
        for offset in range(len(masks)):
            masks[offset] |= occurrence_mask
    return f_start, f_end, tuple(masks)


def _make_candidate(index: int, state: PlanState, action: str, shift: int) -> CandidateState:
    f_start, f_end, masks = _time_masks(state)
    return CandidateState(
        index=index,
        state_id=f"{state.plan.plan_id}:{action}:{shift:+d}",
        state=state,
        action=action,
        shift=shift,
        f_start=f_start,
        f_end=f_end,
        time_masks=masks,
    )


def generate_candidates(plan: Plan, horizon: int = 643) -> list[CandidateState]:
    """Enumerate every legal Q2 state for one plan.

    The zero-shift state is represented only by ``keep``; it is not duplicated
    as a frequency/time adjustment.  Every returned state fits [0,100) and
    [0,horizon) after all repetitions are expanded.
    """

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
    states.append(("cancel", 0, PlanState(plan, action="cancel")))

    result = [_make_candidate(index, state, action, shift) for index, (action, shift, state) in enumerate(states)]
    return result


def generate_all_candidates(
    plans: Sequence[Plan], horizon: int = 643
) -> tuple[list[list[CandidateState]], list[CandidateState]]:
    """Return candidates grouped by plan and in one deterministic flat list."""

    grouped: list[list[CandidateState]] = []
    flat: list[CandidateState] = []
    next_index = 0
    for plan in plans:
        group: list[CandidateState] = []
        for candidate in generate_candidates(plan, horizon=horizon):
            candidate = CandidateState(
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


def candidates_conflict(left: CandidateState, right: CandidateState) -> bool:
    """Exact compatibility test using integer half-open occupancy masks."""

    if left.cancelled or right.cancelled:
        return False
    lo = max(left.f_start, right.f_start)
    hi = min(left.f_end, right.f_end)
    if lo >= hi:
        return False
    for frequency in range(lo, hi):
        left_mask = left.time_masks[frequency - left.f_start]
        right_mask = right.time_masks[frequency - right.f_start]
        if left_mask & right_mask:
            return True
    return False


def selected_conflicts(selected: Sequence[CandidateState]) -> list[tuple[int, int]]:
    """Return all pairwise conflicts in a selected one-state-per-plan schedule."""

    return [
        (left.index, right.index)
        for left, right in combinations(selected, 2)
        if candidates_conflict(left, right)
    ]


def generate_conflict_edges(
    grouped: Sequence[Sequence[CandidateState]],
) -> list[tuple[int, int]]:
    """Enumerate all state-level incompatibility edges deterministically."""

    edges: list[tuple[int, int]] = []
    for left_group, right_group in combinations(grouped, 2):
        for left, right in product(left_group, right_group):
            if candidates_conflict(left, right):
                edges.append((left.index, right.index))
    return edges


def generate_cell_cliques(
    flat: Sequence[CandidateState],
) -> list[tuple[int, ...]]:
    """Return exact resource-cell cliques for an integer time-frequency grid.

    Every candidate occupying the same integer cell (f, t) belongs to one
    at-most-one clique.  Because all intervals are half-open and integer,
    these cliques are equivalent to the pairwise state conflict edges while
    giving CP-SAT stronger propagation with fewer repeated binary clauses.
    """

    cells = generate_cell_clique_map(flat)
    return [tuple(indices) for indices in cells.values() if len(indices) > 1]


def generate_cell_clique_map(
    flat: Sequence[CandidateState],
) -> dict[tuple[int, int], tuple[int, ...]]:
    """Map each occupied integer (frequency, time) cell to candidate IDs."""

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
    return {cell: tuple(indices) for cell, indices in cells.items()}


def selected_conflict_cliques(
    selected: Sequence[CandidateState],
    cell_map: dict[tuple[int, int], tuple[int, ...]],
) -> list[tuple[int, ...]]:
    """Return full resource-cell cliques exposed by a selected conflict."""

    selected_ids = {candidate.index for candidate in selected}
    occupied: dict[tuple[int, int], list[int]] = {}
    for candidate in selected:
        if candidate.cancelled:
            continue
        for offset, mask in enumerate(candidate.time_masks):
            frequency = candidate.f_start + offset
            remaining = mask
            while remaining:
                lowest = remaining & -remaining
                time_slot = lowest.bit_length() - 1
                occupied.setdefault((frequency, time_slot), []).append(candidate.index)
                remaining ^= lowest
    cliques: list[tuple[int, ...]] = []
    seen: set[tuple[int, ...]] = set()
    for cell, ids in occupied.items():
        if len(ids) < 2:
            continue
        clique = cell_map.get(cell, ())
        if len(clique) > 1 and any(index in selected_ids for index in clique):
            clique = tuple(sorted(clique))
            if clique not in seen:
                seen.add(clique)
                cliques.append(clique)
    return cliques


def verify_mask_sample(
    flat: Sequence[CandidateState], pairs: Iterable[tuple[int, int]]
) -> int:
    """Cross-check mask conflicts against the canonical interval detector."""

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
