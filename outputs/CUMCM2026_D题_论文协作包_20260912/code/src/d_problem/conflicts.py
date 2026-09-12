"""The single periodic time-frequency conflict implementation."""

from __future__ import annotations

from itertools import combinations
from typing import Iterable

from .domain import ConflictPair, ConflictWitness, Occurrence, PlanState


def interval_overlap(
    left_a: int, right_a: int, left_b: int, right_b: int
) -> tuple[int, int] | None:
    """Return the positive-overlap interval, or None for touching/disjoint ends."""

    left = max(left_a, left_b)
    right = min(right_a, right_b)
    return (left, right) if left < right else None


def expand_occurrences(state: PlanState) -> list[Occurrence]:
    """Expand all repetitions of one non-cancelled state."""

    if state.action == "cancel":
        return []
    plan = state.plan
    if state.action == "frequency" and state.t_shift != 0:
        raise ValueError("frequency state cannot also shift time")
    if state.action == "time" and state.f_shift != 0:
        raise ValueError("time state cannot also shift frequency")
    if state.action != "gap" and state.gap_shift != 0:
        raise ValueError("only gap state may change the interval gap")

    f_start = plan.f_start + state.f_shift
    f_end = plan.f_end + state.f_shift
    t_start = plan.t_start + state.t_shift
    t_end = plan.t_end + state.t_shift
    period = plan.duration + plan.gap + state.gap_shift
    if period <= 0:
        raise ValueError(f"non-positive period for {plan.plan_id}: {period}")

    return [
        Occurrence(
            plan_id=plan.plan_id,
            k=k,
            f_start=f_start,
            f_end=f_end,
            t_start=t_start + k * period,
            t_end=t_end + k * period,
        )
        for k in range(plan.count)
    ]


def states_conflict(
    state_i: PlanState, state_j: PlanState
) -> tuple[bool, ConflictWitness | None]:
    """Check two states and return the first auditable occurrence witness."""

    if state_i.plan.plan_id == state_j.plan.plan_id:
        raise ValueError("conflict is defined between two distinct plans")
    occurrences_i = expand_occurrences(state_i)
    occurrences_j = expand_occurrences(state_j)
    if not occurrences_i or not occurrences_j:
        return False, None

    # Frequency is constant over repetitions, so reject early when disjoint.
    frequency_overlap = interval_overlap(
        occurrences_i[0].f_start,
        occurrences_i[0].f_end,
        occurrences_j[0].f_start,
        occurrences_j[0].f_end,
    )
    if frequency_overlap is None:
        return False, None

    for occurrence_i, occurrence_j in combinations(
        occurrences_i + occurrences_j, 2
    ):
        # combinations above mixes the two lists; only evaluate cross-plan pairs.
        if occurrence_i.plan_id == occurrence_j.plan_id:
            continue
        time_overlap = interval_overlap(
            occurrence_i.t_start,
            occurrence_i.t_end,
            occurrence_j.t_start,
            occurrence_j.t_end,
        )
        if time_overlap is not None:
            # Orient the witness in the same order as the function arguments.
            if occurrence_i.plan_id == state_i.plan.plan_id:
                oi, oj = occurrence_i, occurrence_j
            else:
                oi, oj = occurrence_j, occurrence_i
            return True, ConflictWitness(
                plan_i=state_i.plan.plan_id,
                plan_j=state_j.plan.plan_id,
                occurrence_i=oi.k,
                occurrence_j=oj.k,
                f_overlap=frequency_overlap,
                t_overlap=time_overlap,
            )
    return False, None


def find_conflict_pairs(states: Iterable[PlanState]) -> list[ConflictPair]:
    """Return sorted, de-duplicated plan pairs with one witness each."""

    state_list = list(states)
    pairs: list[ConflictPair] = []
    for state_i, state_j in combinations(state_list, 2):
        conflict, witness = states_conflict(state_i, state_j)
        if conflict and witness is not None:
            if state_i.plan.plan_id <= state_j.plan.plan_id:
                oriented_witness = witness
            else:
                oriented_witness = ConflictWitness(
                    plan_i=state_j.plan.plan_id,
                    plan_j=state_i.plan.plan_id,
                    occurrence_i=witness.occurrence_j,
                    occurrence_j=witness.occurrence_i,
                    f_overlap=witness.f_overlap,
                    t_overlap=witness.t_overlap,
                )
            pairs.append(
                ConflictPair(
                    plan_i=min(state_i.plan.plan_id, state_j.plan.plan_id),
                    plan_j=max(state_i.plan.plan_id, state_j.plan.plan_id),
                    witness=oriented_witness,
                )
            )
    return sorted(pairs, key=lambda pair: (pair.plan_i, pair.plan_j))
