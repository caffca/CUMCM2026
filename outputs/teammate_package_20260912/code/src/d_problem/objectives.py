"""Q2/Q4 policy vectors and integer lexicographic objective metadata."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Sequence

from .candidates import CandidateState


Policy = Literal["T", "P"]


@dataclass(frozen=True, slots=True)
class ObjectiveSpec:
    """One integer objective layer."""

    name: str
    description: str


T_OBJECTIVES: tuple[ObjectiveSpec, ...] = (
    ObjectiveSpec("C", "total cancellations"),
    ObjectiveSpec("M", "total adjusted plans"),
    ObjectiveSpec("P_A", "disturbed A plans"),
    ObjectiveSpec("C_A", "cancelled A plans"),
    ObjectiveSpec("P_B", "disturbed B plans"),
    ObjectiveSpec("C_B", "cancelled B plans"),
    ObjectiveSpec("S_sum", "integer-scaled total displacement"),
    ObjectiveSpec("S_max", "maximum single-plan displacement"),
)

P_OBJECTIVES: tuple[ObjectiveSpec, ...] = (
    ObjectiveSpec("P_A", "disturbed A plans"),
    ObjectiveSpec("C_A", "cancelled A plans"),
    ObjectiveSpec("P_B", "disturbed B plans"),
    ObjectiveSpec("C_B", "cancelled B plans"),
    ObjectiveSpec("C", "total cancellations"),
    ObjectiveSpec("M", "total adjusted plans"),
    ObjectiveSpec("S_sum", "integer-scaled total displacement"),
    ObjectiveSpec("S_max", "maximum single-plan displacement"),
)


def objective_specs(policy: Policy) -> tuple[ObjectiveSpec, ...]:
    if policy == "T":
        return T_OBJECTIVES
    if policy == "P":
        return P_OBJECTIVES
    raise ValueError(f"unknown Q2 policy: {policy}")


def candidate_coefficients(candidate: CandidateState) -> dict[str, int]:
    """Return all per-state coefficients used by Q2 objectives."""

    category = candidate.category
    cancelled = int(candidate.cancelled)
    adjusted = int(candidate.adjusted)
    disturbed = int(candidate.disturbed)
    displacement = candidate.displacement_cost
    return {
        "C": cancelled,
        "M": adjusted,
        "P_A": disturbed if category == "A" else 0,
        "C_A": cancelled if category == "A" else 0,
        "P_B": disturbed if category == "B" else 0,
        "C_B": cancelled if category == "B" else 0,
        "P_C": disturbed if category == "C" else 0,
        "C_C": cancelled if category == "C" else 0,
        "M_A": adjusted if category == "A" else 0,
        "M_B": adjusted if category == "B" else 0,
        "M_C": adjusted if category == "C" else 0,
        # Keep raw frequency/time/gap shifts alongside the integer-scaled
        # displacement used by the lexicographic objective.  These fields are
        # reporting metrics, not extra objective layers.
        "Df_sum": abs(candidate.state.f_shift),
        "Dt_sum": abs(candidate.state.t_shift),
        "Dg_sum": abs(candidate.state.gap_shift),
        "Df_max": abs(candidate.state.f_shift),
        "Dt_max": abs(candidate.state.t_shift),
        "Dg_max": abs(candidate.state.gap_shift),
        "S_sum": displacement,
        "S_max": displacement,
    }


def objective_value_from_selection(
    selected: Sequence[CandidateState], policy: Policy = "T"
) -> dict[str, int]:
    """Calculate exact report metrics from a selected schedule."""

    values = {
        "C": 0,
        "M": 0,
        "P_A": 0,
        "C_A": 0,
        "P_B": 0,
        "C_B": 0,
        "P_C": 0,
        "C_C": 0,
        "M_A": 0,
        "M_B": 0,
        "M_C": 0,
        "Df_sum": 0,
        "Dt_sum": 0,
        "Dg_sum": 0,
        "Df_max": 0,
        "Dt_max": 0,
        "Dg_max": 0,
        "S_sum": 0,
        "S_max": 0,
    }
    for candidate in selected:
        coefficients = candidate_coefficients(candidate)
        for name in values:
            if name in {"S_max", "Df_max", "Dt_max", "Dg_max"}:
                continue
            values[name] += coefficients[name]
        values["Df_max"] = max(values["Df_max"], coefficients["Df_max"])
        values["Dt_max"] = max(values["Dt_max"], coefficients["Dt_max"])
        values["Dg_max"] = max(values["Dg_max"], coefficients["Dg_max"])
        values["S_max"] = max(values["S_max"], coefficients["S_max"])
    values["P_total"] = values["P_A"] + values["P_B"] + values["P_C"]
    return values


def objective_names(policy: Policy) -> tuple[str, ...]:
    return tuple(spec.name for spec in objective_specs(policy))
