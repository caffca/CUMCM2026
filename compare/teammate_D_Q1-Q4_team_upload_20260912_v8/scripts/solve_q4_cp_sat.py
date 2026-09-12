#!/usr/bin/env python3
"""Solve D-Q4 with finite legal actions and CP-SAT resource cliques."""
from __future__ import annotations

import argparse
from collections import defaultdict
from dataclasses import dataclass
import json
from pathlib import Path
from typing import Iterable

from ortools.sat.python import cp_model

from scripts.solve_q1 import read_plans


OBJECTIVE_ORDER = [
    "revoke",
    "revoke_A",
    "revoke_B",
    "adjust",
    "adjust_A",
    "adjust_B",
    "normalized_shift",
]


@dataclass(frozen=True)
class Candidate:
    plan_id: str
    category: str
    action: str
    df: int
    dt: int
    dg: int
    frequency: tuple[int, int] | None
    time: tuple[int, int] | None
    gap: int | None
    cells: frozenset[tuple[int, int]]


def expanded_cells(
    frequency: tuple[int, int],
    time: tuple[int, int],
    gap: int,
    uses: int,
) -> frozenset[tuple[int, int]]:
    f0, f1 = frequency
    t0, t1 = time
    duration = t1 - t0
    step = duration + gap
    return frozenset(
        (event_t0 + offset, frequency_index)
        for k in range(uses)
        for event_t0 in [t0 + k * step]
        for offset in range(duration)
        for frequency_index in range(f0, f1)
    )


def candidate_fits(
    frequency: tuple[int, int],
    time: tuple[int, int],
    gap: int,
    uses: int,
    horizon: int,
) -> bool:
    f0, f1 = frequency
    t0, t1 = time
    duration = t1 - t0
    final_end = t1 + (uses - 1) * (duration + gap)
    return 0 <= f0 < f1 <= 100 and 0 <= t0 < t1 and final_end <= horizon


def build_candidates(plans: list[dict], horizon: int) -> list[Candidate]:
    candidates: list[Candidate] = []
    for plan in plans:
        plan_id = plan["id"]
        category = plan["category"]
        f0, f1 = plan["frequency"]
        t0, t1 = plan["time"]
        gap = int(plan["gap"])
        uses = int(plan["uses"])

        actions: list[tuple[str, int, int, int]] = [("keep", 0, 0, 0)]
        actions.extend(("freq", df, 0, 0) for df in range(-10, 11) if df != 0)
        actions.extend(("time", 0, dt, 0) for dt in range(-5, 6) if dt != 0)
        if category == "C":
            actions.extend(
                ("gap", 0, 0, dg)
                for dg in range(-10, 11)
                if dg != 0 and gap + dg >= 0
            )

        for action, df, dt, dg in actions:
            frequency = (f0 + df, f1 + df)
            time = (t0 + dt, t1 + dt)
            adjusted_gap = gap + dg
            if not candidate_fits(frequency, time, adjusted_gap, uses, horizon):
                continue
            candidates.append(
                Candidate(
                    plan_id=plan_id,
                    category=category,
                    action=action,
                    df=df,
                    dt=dt,
                    dg=dg,
                    frequency=frequency,
                    time=time,
                    gap=adjusted_gap,
                    cells=expanded_cells(frequency, time, adjusted_gap, uses),
                )
            )
        candidates.append(
            Candidate(plan_id, category, "revoke", 0, 0, 0, None, None, None, frozenset())
        )
    return candidates


def feature_vectors(candidates: list[Candidate]) -> dict[str, list[int]]:
    adjusted_actions = {"freq", "time", "gap"}
    return {
        "revoke": [int(c.action == "revoke") for c in candidates],
        "revoke_A": [int(c.category == "A" and c.action == "revoke") for c in candidates],
        "revoke_B": [int(c.category == "B" and c.action == "revoke") for c in candidates],
        "adjust": [int(c.action in adjusted_actions) for c in candidates],
        "adjust_A": [int(c.category == "A" and c.action in adjusted_actions) for c in candidates],
        "adjust_B": [int(c.category == "B" and c.action in adjusted_actions) for c in candidates],
        "normalized_shift": [abs(c.df) + 2 * abs(c.dt) + abs(c.dg) for c in candidates],
    }


def build_model(
    candidates: list[Candidate],
    fixed: Iterable[tuple[str, int]],
    upper_bounds: Iterable[tuple[str, int]],
    encoding: str = "clique",
) -> tuple[cp_model.CpModel, list[cp_model.IntVar], dict[str, list[int]], int]:
    model = cp_model.CpModel()
    variables = [model.new_bool_var(f"x_{index}") for index in range(len(candidates))]
    features = feature_vectors(candidates)
    by_plan: defaultdict[str, list[int]] = defaultdict(list)
    by_cell: defaultdict[tuple[int, int], list[int]] = defaultdict(list)

    for index, candidate in enumerate(candidates):
        by_plan[candidate.plan_id].append(index)
        for cell in candidate.cells:
            by_cell[cell].append(index)

    for indexes in by_plan.values():
        if encoding == "bool":
            model.add_exactly_one(variables[index] for index in indexes)
        else:
            model.add(sum(variables[index] for index in indexes) == 1)

    resource_rows = 0
    for indexes in by_cell.values():
        if len(indexes) >= 2:
            if encoding == "clique":
                model.add(sum(variables[index] for index in indexes) <= 1)
                resource_rows += 1
            elif encoding == "bool":
                model.add_at_most_one(variables[index] for index in indexes)
                resource_rows += 1
            elif encoding == "pairwise":
                for left_position, left in enumerate(indexes):
                    for right in indexes[left_position + 1 :]:
                        if candidates[left].plan_id != candidates[right].plan_id:
                            model.add_bool_or([variables[left].Not(), variables[right].Not()])
                            resource_rows += 1
            elif encoding == "dedup_pairwise":
                # The same pair of action candidates may share several cells.
                # Materialize each conflict edge once before adding clauses so
                # the global threshold model does not repeat an equivalent
                # binary constraint thousands of times.
                pass
            else:
                raise ValueError(f"unknown resource encoding: {encoding}")

    if encoding == "dedup_pairwise":
        conflict_edges = {
            (left, right)
            for indexes in by_cell.values()
            if len(indexes) >= 2
            for left_position, left in enumerate(indexes)
            for right in indexes[left_position + 1 :]
            if candidates[left].plan_id != candidates[right].plan_id
        }
        for left, right in conflict_edges:
            model.add_bool_or([variables[left].Not(), variables[right].Not()])
        resource_rows = len(conflict_edges)

    for feature_name, value in fixed:
        model.add(
            sum(features[feature_name][i] * variables[i] for i in range(len(variables))) == value
        )
    for feature_name, value in upper_bounds:
        model.add(
            sum(features[feature_name][i] * variables[i] for i in range(len(variables))) <= value
        )
    return model, variables, features, resource_rows


def q2_hint(candidates: list[Candidate], path: Path | None) -> list[int] | None:
    if path is None:
        return None
    payload = json.loads(path.read_text(encoding="utf-8"))
    actions = {row["装备编号"]: row for row in payload["summary"]["actions"]}
    hint: list[int] = []
    for candidate in candidates:
        row = actions.get(candidate.plan_id)
        if row is None:
            match = candidate.action == "keep"
        else:
            match = (
                candidate.action == row["动作"]
                and candidate.df == int(row.get("频移", 0))
                and candidate.dt == int(row.get("时移", 0))
                and candidate.dg == int(row.get("间隔变化", 0))
            )
        hint.append(int(match))
    return hint


def selected_values(
    solver: cp_model.CpSolver,
    variables: list[cp_model.IntVar],
    status: cp_model.CpSolverStatus,
) -> list[int] | None:
    if solver.status_name(status) not in {"OPTIMAL", "FEASIBLE"}:
        return None
    return [int(solver.value(variable)) for variable in variables]


def format_interval(interval: tuple[int, int] | None) -> str | None:
    return None if interval is None else f"[{interval[0]},{interval[1]})"


def summarize(plans: list[dict], candidates: list[Candidate], values: list[int]) -> dict:
    selected = [candidate for candidate, value in zip(candidates, values) if value]
    actions = []
    for candidate in sorted(selected, key=lambda item: item.plan_id):
        if candidate.action == "keep":
            continue
        actions.append(
            {
                "装备编号": candidate.plan_id,
                "类别": candidate.category,
                "动作": candidate.action,
                "频段区间": format_interval(candidate.frequency),
                "时间区间": format_interval(candidate.time),
                "调整后间隔": candidate.gap,
                "频移": candidate.df,
                "时移": candidate.dt,
                "间隔变化": candidate.dg,
                "撤销": candidate.action == "revoke",
            }
        )
    counts = {}
    for category in "ABC":
        category_selected = [c for c in selected if c.category == category]
        revoked = sum(c.action == "revoke" for c in category_selected)
        adjusted = sum(c.action in {"freq", "time", "gap"} for c in category_selected)
        counts[category] = {
            "保留数量": len(category_selected) - revoked - adjusted,
            "调整数量": adjusted,
            "撤销数量": revoked,
        }
    action_counts = {
        action: sum(candidate.action == action for candidate in selected)
        for action in ["keep", "freq", "time", "gap", "revoke"]
    }
    return {
        "plans": len(plans),
        "selected_candidates": len(selected),
        "actions": actions,
        "counts_by_category": counts,
        "action_counts": action_counts,
        "selected_unique_occupied_cell_count": len(
            set().union(*(candidate.cells for candidate in selected))
        ),
        "selected_weighted_occupied_cell_count": sum(len(candidate.cells) for candidate in selected),
    }


def configure_solver(
    time_limit: float,
    workers: int,
    seed: int,
    search_branching: str = "automatic",
    randomize_search: bool = False,
    random_branches_ratio: float = 0.0,
) -> cp_model.CpSolver:
    solver = cp_model.CpSolver()
    solver.parameters.max_time_in_seconds = time_limit
    solver.parameters.num_search_workers = workers
    solver.parameters.random_seed = seed
    solver.parameters.cp_model_presolve = True
    solver.parameters.linearization_level = 2
    solver.parameters.symmetry_level = 2
    branching_values = {
        "automatic": cp_model.AUTOMATIC_SEARCH,
        "fixed": cp_model.FIXED_SEARCH,
        "portfolio": cp_model.PORTFOLIO_SEARCH,
        "randomized": cp_model.RANDOMIZED_SEARCH,
        "quick_restart": cp_model.PORTFOLIO_WITH_QUICK_RESTART_SEARCH,
    }
    solver.parameters.search_branching = branching_values[search_branching]
    solver.parameters.randomize_search = randomize_search
    solver.parameters.random_branches_ratio = random_branches_ratio
    solver.parameters.log_search_progress = False
    return solver


def solve_model(
    candidates: list[Candidate],
    fixed: list[tuple[str, int]],
    upper_bounds: list[tuple[str, int]],
    objective: str | None,
    time_limit: float,
    workers: int,
    seed: int,
    hint: list[int] | None,
    encoding: str = "clique",
    prefer_active: bool = False,
    search_branching: str = "automatic",
    randomize_search: bool = False,
    random_branches_ratio: float = 0.0,
) -> tuple[dict, list[int] | None, int]:
    model, variables, features, resource_rows = build_model(candidates, fixed, upper_bounds, encoding)
    if objective is not None:
        model.minimize(sum(features[objective][i] * variables[i] for i in range(len(variables))))
    if hint is not None:
        for variable, value in zip(variables, hint):
            model.add_hint(variable, value)
    if prefer_active:
        active_variables = [
            variables[index] for index, candidate in enumerate(candidates) if candidate.action != "revoke"
        ]
        model.add_decision_strategy(
            active_variables,
            cp_model.CHOOSE_FIRST,
            cp_model.SELECT_MAX_VALUE,
        )
    solver = configure_solver(
        time_limit,
        workers,
        seed,
        search_branching,
        randomize_search,
        random_branches_ratio,
    )
    status = solver.solve(model)
    status_name = solver.status_name(status)
    values = selected_values(solver, variables, status)
    record = {
        "objective": objective,
        "status": status_name,
        "time_limit_seconds": time_limit,
        "wall_time_seconds": solver.wall_time,
        "objective_value": (
            float(solver.objective_value) if objective is not None and values is not None else None
        ),
        "best_objective_bound": (
            float(solver.best_objective_bound) if objective is not None else None
        ),
        "num_conflicts": solver.num_conflicts,
        "num_branches": solver.num_branches,
        "optimality": "PROVED" if status_name == "OPTIMAL" else "NOT_PROVED",
        "resource_encoding": encoding,
    }
    if values is not None and objective is not None:
        record["incumbent_value"] = int(
            sum(features[objective][i] * values[i] for i in range(len(values)))
        )
    return record, values, resource_rows


def run_chain(
    plans: list[dict],
    candidates: list[Candidate],
    objectives: list[str],
    time_limit: float,
    workers: int,
    seed: int,
    initial_hint: list[int] | None,
    initial_fixed: list[tuple[str, int]] | None = None,
    encoding: str = "clique",
    prefer_active: bool = False,
    search_branching: str = "automatic",
    randomize_search: bool = False,
    random_branches_ratio: float = 0.0,
) -> dict:
    fixed: list[tuple[str, int]] = list(initial_fixed or [])
    stages = []
    hint = initial_hint
    final_values: list[int] | None = None
    resource_rows = 0
    for stage_index, objective in enumerate(objectives):
        record, values, resource_rows = solve_model(
            candidates,
            fixed,
            [],
            objective,
            time_limit,
            workers,
            seed + stage_index,
            hint,
            encoding,
            prefer_active,
            search_branching,
            randomize_search,
            random_branches_ratio,
        )
        stages.append(record)
        if values is None:
            break
        final_values = values
        hint = values
        if record["optimality"] != "PROVED":
            break
        fixed.append((objective, int(record["incumbent_value"])))

    features = feature_vectors(candidates)
    objective_values = None
    summary = None
    if final_values is not None:
        objective_values = {
            name: int(sum(features[name][i] * final_values[i] for i in range(len(final_values))))
            for name in OBJECTIVE_ORDER
        }
        summary = summarize(plans, candidates, final_values)
    return {
        "question": "D-Q4",
        "mode": "lexicographic_chain",
        "status": (
            "OPTIMAL_PREFIX" if stages and all(s["optimality"] == "PROVED" for s in stages)
            else "FEASIBLE_INCUMBENT" if final_values is not None else stages[-1]["status"]
        ),
        "method": "OR-Tools CP-SAT + finite actions + resource conflict constraints",
        "objective_order": OBJECTIVE_ORDER,
        "requested_objectives": objectives,
        "time_domain": None,
        "frequency_domain": [0, 100],
        "rules": {
            "frequency_shift_limit": 10,
            "time_shift_limit": 5,
            "C_gap_shift_limit": 10,
            "C_gap_nonnegative_integer": True,
            "one_action_per_plan": True,
            "half_open_intervals": True,
        },
        "candidate_count": len(candidates),
        "resource_cell_constraint_count": resource_rows,
        "optimization": {
            "stages": stages,
            "proved_fixed_prefix": [{"feature": name, "value": value} for name, value in fixed],
            "objective_values": objective_values,
            "workers": workers,
            "seed": seed,
        },
        "summary": summary,
    }


def run_threshold(
    plans: list[dict],
    candidates: list[Candidate],
    fixed: list[tuple[str, int]],
    upper_bounds: list[tuple[str, int]],
    time_limit: float,
    workers: int,
    seed: int,
    hint: list[int] | None,
    encoding: str = "clique",
    prefer_active: bool = False,
    search_branching: str = "automatic",
    randomize_search: bool = False,
    random_branches_ratio: float = 0.0,
) -> dict:
    record, values, resource_rows = solve_model(
        candidates,
        fixed,
        upper_bounds,
        None,
        time_limit,
        workers,
        seed,
        hint,
        encoding,
        prefer_active,
        search_branching,
        randomize_search,
        random_branches_ratio,
    )
    summary = summarize(plans, candidates, values) if values is not None else None
    return {
        "question": "D-Q4",
        "mode": "threshold_feasibility",
        "status": record["status"],
        "proof": "PROVED_INFEASIBLE" if record["status"] == "INFEASIBLE" else "NOT_INFEASIBLE",
        "method": "OR-Tools CP-SAT + finite actions + resource conflict constraints",
        "fixed": [{"feature": name, "value": value} for name, value in fixed],
        "upper_bounds": [{"feature": name, "value": value} for name, value in upper_bounds],
        "time_domain": None,
        "frequency_domain": [0, 100],
        "candidate_count": len(candidates),
        "resource_cell_constraint_count": resource_rows,
        "resource_encoding": encoding,
        "optimization": record,
        "summary": summary,
    }


def parse_pairs(values: list[str]) -> list[tuple[str, int]]:
    pairs = []
    for value in values:
        name, raw_number = value.split("=", 1)
        if name not in OBJECTIVE_ORDER:
            raise ValueError(f"unknown feature: {name}")
        pairs.append((name, int(raw_number)))
    return pairs


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=Path("data/raw/D题/附件/附件1.xlsx"))
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--horizon", type=int, default=643)
    parser.add_argument("--mode", choices=["chain", "threshold"], default="chain")
    parser.add_argument("--objectives", default=",".join(OBJECTIVE_ORDER))
    parser.add_argument("--fix", action="append", default=[])
    parser.add_argument("--upper", action="append", default=[])
    parser.add_argument(
        "--encoding",
        choices=["clique", "bool", "pairwise", "dedup_pairwise"],
        default="clique",
    )
    parser.add_argument("--prefer-active", action="store_true")
    parser.add_argument(
        "--search-branching",
        choices=["automatic", "fixed", "portfolio", "randomized", "quick_restart"],
        default="automatic",
    )
    parser.add_argument("--randomize-search", action="store_true")
    parser.add_argument("--random-branches-ratio", type=float, default=0.0)
    parser.add_argument("--q2-hint", type=Path)
    parser.add_argument("--time-limit", type=float, default=300.0)
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--seed", type=int, default=20260911)
    args = parser.parse_args()

    plans = read_plans(args.input)
    candidates = build_candidates(plans, args.horizon)
    hint = q2_hint(candidates, args.q2_hint)
    if args.mode == "chain":
        objectives = [name for name in args.objectives.split(",") if name]
        if any(name not in OBJECTIVE_ORDER for name in objectives):
            raise ValueError(f"invalid objectives: {objectives}")
        payload = run_chain(
            plans,
            candidates,
            objectives,
            args.time_limit,
            args.workers,
            args.seed,
            hint,
            initial_fixed=parse_pairs(args.fix),
            encoding=args.encoding,
            prefer_active=args.prefer_active,
            search_branching=args.search_branching,
            randomize_search=args.randomize_search,
            random_branches_ratio=args.random_branches_ratio,
        )
    else:
        payload = run_threshold(
            plans,
            candidates,
            parse_pairs(args.fix),
            parse_pairs(args.upper),
            args.time_limit,
            args.workers,
            args.seed,
            hint,
            args.encoding,
            args.prefer_active,
            args.search_branching,
            args.randomize_search,
            args.random_branches_ratio,
        )
    payload["time_domain"] = [0, args.horizon]
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(
        json.dumps(
            {
                "status": payload["status"],
                "mode": payload["mode"],
                "candidate_count": payload["candidate_count"],
                "resource_rows": payload["resource_cell_constraint_count"],
                "objective_values": payload.get("optimization", {}).get("objective_values"),
                "output": str(args.output),
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
