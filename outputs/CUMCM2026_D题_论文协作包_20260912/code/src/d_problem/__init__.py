"""Core data and conflict-detection primitives for CUMCM2026 D."""

from .domain import ConflictPair, ConflictWitness, Occurrence, Plan, PlanState

__all__ = [
    "ConflictPair",
    "ConflictWitness",
    "Occurrence",
    "Plan",
    "PlanState",
]
