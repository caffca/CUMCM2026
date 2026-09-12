"""CP-SAT implementation of the Q2 exact state-compatibility model."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Literal, Mapping, Sequence

from ortools.sat.python import cp_model

from .candidates import (
    CandidateState,
    candidates_conflict,
    selected_conflicts,
)
from .objectives import (
    Policy,
    candidate_coefficients,
    objective_names,
    objective_specs,
    objective_value_from_selection,
)


Mode = Literal["full", "lazy"]
ConstraintForm = Literal["edges", "cells", "hybrid"]


@dataclass(frozen=True, slots=True)
class SolverConfig:
    time_limit_seconds: float = 120.0
    num_search_workers: int = 8
    random_seed: int = 20260911


@dataclass(frozen=True, slots=True)
class LayerReport:
    name: str
    status: str
    objective_value: int | None
    best_bound: float | None
    gap: float | None
    seconds: float
    cuts_added: int = 0
    num_conflicts: int | None = None
    num_branches: int | None = None


@dataclass(frozen=True, slots=True)
class Q2SolveResult:
    policy: str
    mode: str
    selected: tuple[CandidateState, ...]
    metrics: Mapping[str, int]
    layers: tuple[LayerReport, ...]
    edge_count: int
    cut_count: int
    iterations: int
    proven_optimal: bool

    def layer_dicts(self) -> list[dict[str, object]]:
        return [asdict(layer) for layer in self.layers]


def _gap(value: float | None, bound: float | None) -> float | None:
    if value is None or bound is None:
        return None
    if abs(value) < 1e-9:
        return 0.0 if abs(bound) < 1e-9 else None
    return abs(value - bound) / max(1.0, abs(value))


def _build_model(
    grouped: Sequence[Sequence[CandidateState]],
    flat: Sequence[CandidateState],
    edges: Sequence[tuple[int, int]],
    cell_cliques: Sequence[Sequence[int]],
    dynamic_cliques: Sequence[Sequence[int]],
    constraint_form: ConstraintForm,
    fixed: Mapping[str, int],
    budgets: Mapping[str, int] | None,
    hints: Mapping[int, int] | None,
    required_names: Sequence[str],
) -> tuple[cp_model.CpModel, list[cp_model.IntVar], dict[str, cp_model.LinearExpr]]:
    model = cp_model.CpModel()
    variables = [model.NewBoolVar(f"x_{candidate.index}") for candidate in flat]

    for group in grouped:
        model.Add(sum(variables[candidate.index] for candidate in group) == 1)

    # Propagation strengthening implied by the exact state-conflict model:
    # if a non-cancelled state has no compatible non-cancelled state in some
    # other plan, selecting it necessarily forces that other plan's cancel
    # state.  These links do not remove any feasible solution; they expose a
    # consequence that would otherwise require CP-SAT to combine many cell
    # cliques before learning it.
    for group_index, group in enumerate(grouped):
        cancel_candidates = [candidate for candidate in group if candidate.cancelled]
        if not cancel_candidates:
            continue
        cancel_var = variables[cancel_candidates[0].index]
        active_group = [candidate for candidate in group if not candidate.cancelled]
        own_plan_id = group[0].plan.plan_id
        for candidate in flat:
            if candidate.cancelled or candidate.plan.plan_id == own_plan_id:
                continue
            if not any(
                not candidates_conflict(candidate, other)
                for other in active_group
            ):
                model.Add(variables[candidate.index] <= cancel_var)
    if constraint_form in {"edges", "hybrid"}:
        for left, right in edges:
            model.Add(variables[left] + variables[right] <= 1)
    if constraint_form in {"cells", "hybrid"}:
        for clique in cell_cliques:
            if len(clique) > 1:
                model.AddAtMostOne(variables[index] for index in clique)
    for clique in dynamic_cliques:
        if len(clique) > 1:
            model.AddAtMostOne(variables[index] for index in clique)

    expressions: dict[str, cp_model.LinearExpr] = {}
    all_names = {
        "C",
        "M",
        "P_A",
        "C_A",
        "P_B",
        "C_B",
        "P_C",
        "C_C",
        "M_A",
        "M_B",
        "M_C",
        "S_sum",
    }
    coefficient_cache = [candidate_coefficients(candidate) for candidate in flat]
    for name in sorted(set(required_names) & all_names):
        expressions[name] = sum(
            coefficient_cache[index][name] * variables[index]
            for index in range(len(flat))
        )

    if "S_max" in required_names:
        maximum_displacement = max(
            (candidate.displacement_cost for candidate in flat), default=0
        )
        s_max = model.NewIntVar(0, maximum_displacement, "S_max")
        for candidate in flat:
            if candidate.displacement_cost:
                model.Add(
                    s_max
                    >= candidate.displacement_cost * variables[candidate.index]
                )
        expressions["S_max"] = s_max

    for name, value in fixed.items():
        model.Add(expressions[name] == int(value))
    if budgets:
        for name, value in budgets.items():
            model.Add(expressions[name] <= int(value))
    if hints:
        for index, value in hints.items():
            if 0 <= index < len(variables):
                model.add_hint(variables[index], int(value))
    return model, variables, expressions


def _solver(config: SolverConfig) -> cp_model.CpSolver:
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = config.time_limit_seconds
    solver.parameters.num_search_workers = config.num_search_workers
    solver.parameters.random_seed = config.random_seed
    solver.parameters.log_search_progress = False
    return solver


def _selected(
    grouped: Sequence[Sequence[CandidateState]],
    variables: Sequence[cp_model.IntVar],
    solver: cp_model.CpSolver,
) -> tuple[CandidateState, ...]:
    selected: list[CandidateState] = []
    for group in grouped:
        chosen = [candidate for candidate in group if solver.Value(variables[candidate.index])]
        if len(chosen) != 1:
            raise RuntimeError(
                f"solver returned {len(chosen)} states for {group[0].plan.plan_id}"
            )
        selected.append(chosen[0])
    return tuple(selected)


def _solve_layer(
    grouped: Sequence[Sequence[CandidateState]],
    flat: Sequence[CandidateState],
    edges: Sequence[tuple[int, int]],
    fixed: Mapping[str, int],
    budgets: Mapping[str, int] | None,
    objective_name: str,
    config: SolverConfig,
    cell_cliques: Sequence[Sequence[int]],
    dynamic_cliques: Sequence[Sequence[int]],
    constraint_form: ConstraintForm,
    hints: Mapping[int, int] | None,
) -> tuple[LayerReport, tuple[CandidateState, ...], int | None]:
    import time

    model, variables, expressions = _build_model(
        grouped,
        flat,
        edges,
        cell_cliques,
        dynamic_cliques,
        constraint_form,
        fixed=fixed,
        budgets=budgets,
        hints=hints,
        required_names=list(set([objective_name, *fixed.keys(), *(budgets or {}).keys()])),
    )
    model.Minimize(expressions[objective_name])
    solver = _solver(config)
    started = time.perf_counter()
    status = solver.Solve(model)
    elapsed = time.perf_counter() - started
    status_name = solver.StatusName(status)
    if status not in (cp_model.OPTIMAL, cp_model.FEASIBLE):
        return (
            LayerReport(
                name=objective_name,
                status=status_name,
                objective_value=None,
                best_bound=None,
                gap=None,
                seconds=elapsed,
                num_conflicts=solver.NumConflicts(),
                num_branches=solver.NumBranches(),
            ),
            (),
            None,
        )

    value = int(round(solver.ObjectiveValue()))
    bound = float(solver.BestObjectiveBound())
    selected = _selected(grouped, variables, solver)
    report = LayerReport(
        name=objective_name,
        status=status_name,
        objective_value=value,
        best_bound=bound,
        gap=_gap(float(value), bound),
        seconds=elapsed,
        num_conflicts=solver.NumConflicts(),
        num_branches=solver.NumBranches(),
    )
    return report, selected, value


def solve_lexicographic(
    grouped: Sequence[Sequence[CandidateState]],
    flat: Sequence[CandidateState],
    policy: Policy = "T",
    mode: Mode = "full",
    edges: Sequence[tuple[int, int]] = (),
    budgets: Mapping[str, int] | None = None,
    config: SolverConfig | None = None,
    max_lazy_iterations: int = 1000,
    cell_cliques: Sequence[Sequence[int]] = (),
    cell_clique_map: Mapping[tuple[int, int], tuple[int, ...]] | None = None,
    constraint_form: ConstraintForm = "edges",
    hints: Mapping[int, int] | None = None,
    fixed_initial: Mapping[str, int] | None = None,
) -> Q2SolveResult:
    """Solve one policy exactly layer by layer.

    In ``lazy`` mode the master initially has no state-level conflict edges.
    After each optimal master solve, all conflicts among the selected states
    are added as exact no-good cuts.  The same cuts are retained at subsequent
    lexicographic layers.
    """

    if config is None:
        config = SolverConfig()
    if mode not in {"full", "lazy"}:
        raise ValueError(f"unknown Q2 mode: {mode}")
    if constraint_form not in {"edges", "cells", "hybrid"}:
        raise ValueError(f"unknown constraint form: {constraint_form}")
    current_edges = {tuple(sorted(edge)) for edge in edges}
    initial_edge_count = len(current_edges)
    # ``fixed_initial`` is used when an earlier exact feasibility/boundary
    # run has already established a lexicographic prefix (for example,
    # ``C*=6``).  Keeping the prefix as an equality lets the subsequent
    # layers be solved without spending another full time limit reproving the
    # same first objective.  It does not enlarge or change the feasible set:
    # it merely restricts the run to the already-certified optimal face.
    fixed: dict[str, int] = dict(fixed_initial or {})
    layers: list[LayerReport] = []
    selected: tuple[CandidateState, ...] = ()
    last_selection: tuple[CandidateState, ...] = ()
    cut_count = 0
    dynamic_cliques: set[tuple[int, ...]] = set()
    iterations = 0
    proven = True

    for spec in objective_specs(policy):
        if spec.name in fixed:
            # The caller may pass a prefix that was certified by an earlier
            # exact run (e.g. C<=5 infeasible and C=6 feasible).  Do not spend
            # another full solver limit re-optimizing a constant layer; record
            # it explicitly so reports remain auditable and the subsequent
            # layers are solved on the certified optimal face.
            value = int(fixed[spec.name])
            layers.append(
                LayerReport(
                    name=spec.name,
                    status="FIXED",
                    objective_value=value,
                    best_bound=float(value),
                    gap=0.0,
                    seconds=0.0,
                )
            )
            continue
        layer_completed = False
        while True:
            if iterations >= max_lazy_iterations:
                proven = False
                break
            report, candidate_selection, value = _solve_layer(
                grouped,
                flat,
                sorted(current_edges),
                fixed=fixed,
                budgets=budgets,
                objective_name=spec.name,
                config=config,
                cell_cliques=cell_cliques,
                dynamic_cliques=sorted(dynamic_cliques),
                constraint_form=constraint_form,
                hints=hints,
            )
            iterations += 1
            if candidate_selection:
                last_selection = candidate_selection
            if report.status not in {"OPTIMAL", "FEASIBLE"} or value is None:
                layers.append(report)
                proven = False
                selected = candidate_selection or last_selection
                break

            if mode == "lazy":
                conflicts = selected_conflicts(candidate_selection)
                new_conflicts = [edge for edge in conflicts if edge not in current_edges]
                new_cliques: list[tuple[int, ...]] = []
                if cell_clique_map:
                    from .candidates import selected_conflict_cliques

                    new_cliques = [
                        clique
                        for clique in selected_conflict_cliques(
                            candidate_selection, cell_clique_map
                        )
                        if clique not in dynamic_cliques
                    ]
                if new_conflicts or new_cliques:
                    current_edges.update(new_conflicts)
                    cut_count += len(new_conflicts)
                    dynamic_cliques.update(new_cliques)
                    report = LayerReport(
                        name=report.name,
                        status=report.status,
                        objective_value=report.objective_value,
                        best_bound=report.best_bound,
                        gap=report.gap,
                        seconds=report.seconds,
                        cuts_added=len(new_conflicts) + len(new_cliques),
                        num_conflicts=report.num_conflicts,
                        num_branches=report.num_branches,
                    )
                    # Do not fix an objective value until the master optimum is
                    # feasible for the true conflict system.
                    continue

            layers.append(report)
            selected = candidate_selection
            fixed[spec.name] = value
            if report.status != "OPTIMAL":
                proven = False
            layer_completed = True
            break
        if not layer_completed or not proven:
            break

    if not selected:
        selected = last_selection
    if selected:
        metrics = objective_value_from_selection(selected, policy=policy)
    else:
        metrics = {}
    return Q2SolveResult(
        policy=policy,
        mode=mode,
        selected=selected,
        metrics=metrics,
        layers=tuple(layers),
        edge_count=len(current_edges) if mode == "lazy" else initial_edge_count,
        cut_count=cut_count,
        iterations=iterations,
        proven_optimal=proven and len(layers) == len(objective_specs(policy)),
    )


def validate_selected_pairwise(selected: Sequence[CandidateState]) -> int:
    """Fast final check used by scripts before canonical schedule validation."""

    return len(selected_conflicts(selected))
