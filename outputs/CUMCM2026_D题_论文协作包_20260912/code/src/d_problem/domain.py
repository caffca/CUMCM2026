"""Typed domain objects shared by Q1--Q4.

All quantities are integer resource slots.  Intervals are half-open: [left, right).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Literal


Action = Literal["keep", "frequency", "time", "gap", "cancel"]


@dataclass(frozen=True, slots=True)
class Plan:
    plan_id: str
    category: str
    f_start: int
    f_end: int
    t_start: int
    t_end: int
    gap: int
    count: int

    @property
    def duration(self) -> int:
        return self.t_end - self.t_start

    @property
    def period(self) -> int:
        return self.duration + self.gap


@dataclass(frozen=True, slots=True)
class PlanState:
    """One legal action applied to a plan.

    Q1 uses only ``action='keep'``.  Q2/Q4 reuse this object with exactly one
    non-zero shift or ``action='cancel'``.
    """

    plan: Plan
    action: Action = "keep"
    f_shift: int = 0
    t_shift: int = 0
    gap_shift: int = 0


@dataclass(frozen=True, slots=True)
class Occurrence:
    plan_id: str
    k: int
    f_start: int
    f_end: int
    t_start: int
    t_end: int


@dataclass(frozen=True, slots=True)
class ConflictWitness:
    plan_i: str
    plan_j: str
    occurrence_i: int
    occurrence_j: int
    f_overlap: tuple[int, int]
    t_overlap: tuple[int, int]


@dataclass(frozen=True, slots=True)
class ConflictPair:
    plan_i: str
    plan_j: str
    witness: ConflictWitness
