"""Independent schedule/state checks used before formal output."""

from __future__ import annotations

from dataclasses import dataclass
from itertools import combinations
from typing import Iterable

from .conflicts import expand_occurrences, find_conflict_pairs
from .domain import PlanState


@dataclass(frozen=True, slots=True)
class ValidationReport:
    plan_count: int
    occurrence_count: int
    conflict_count: int
    boundary_violations: int

    @property
    def ok(self) -> bool:
        return self.conflict_count == 0 and self.boundary_violations == 0


def validate_state(state: PlanState, horizon: int | None = None) -> list[str]:
    """Return all state-level errors; an empty list means valid."""

    errors: list[str] = []
    plan = state.plan
    shifts = [state.f_shift != 0, state.t_shift != 0, state.gap_shift != 0]
    if state.action == "keep" and any(shifts):
        errors.append(f"{plan.plan_id}: keep state has a non-zero shift")
    if state.action == "frequency":
        if state.f_shift == 0 or state.t_shift != 0 or state.gap_shift != 0:
            errors.append(f"{plan.plan_id}: invalid frequency-only state")
        if abs(state.f_shift) > 10:
            errors.append(f"{plan.plan_id}: frequency shift exceeds 10")
    if state.action == "time":
        if state.t_shift == 0 or state.f_shift != 0 or state.gap_shift != 0:
            errors.append(f"{plan.plan_id}: invalid time-only state")
        if abs(state.t_shift) > 5:
            errors.append(f"{plan.plan_id}: time shift exceeds 5")
    if state.action == "gap":
        if state.gap_shift == 0 or state.f_shift != 0 or state.t_shift != 0:
            errors.append(f"{plan.plan_id}: invalid gap-only state")
        if plan.category != "C":
            errors.append(f"{plan.plan_id}: only C plans may use gap state")
        if abs(state.gap_shift) > 10 or plan.gap + state.gap_shift < 0:
            errors.append(f"{plan.plan_id}: invalid gap shift")
    if state.action == "cancel" and any(shifts):
        errors.append(f"{plan.plan_id}: cancel state has a non-zero shift")
    if state.action not in {"keep", "frequency", "time", "gap", "cancel"}:
        errors.append(f"{plan.plan_id}: unknown action {state.action!r}")

    if state.action != "cancel":
        occurrences = expand_occurrences(state)
        for occurrence in occurrences:
            if occurrence.f_start < 0 or occurrence.f_end > 100:
                errors.append(f"{plan.plan_id}: frequency boundary violation")
            if horizon is not None and (
                occurrence.t_start < 0 or occurrence.t_end > horizon
            ):
                errors.append(f"{plan.plan_id}: time boundary violation")
    return errors


def validate_schedule(
    states: Iterable[PlanState], horizon: int | None = None
) -> ValidationReport:
    state_list = list(states)
    plan_ids = [state.plan.plan_id for state in state_list]
    if len(plan_ids) != len(set(plan_ids)):
        raise ValueError("schedule contains duplicate plan ids")
    errors = [error for state in state_list for error in validate_state(state, horizon)]
    if errors:
        raise ValueError("; ".join(errors))
    occurrences = sum(
        (expand_occurrences(state) for state in state_list if state.action != "cancel"),
        [],
    )
    conflicts = find_conflict_pairs(state_list)
    return ValidationReport(
        plan_count=len(state_list),
        occurrence_count=len(occurrences),
        conflict_count=len(conflicts),
        boundary_violations=0,
    )
