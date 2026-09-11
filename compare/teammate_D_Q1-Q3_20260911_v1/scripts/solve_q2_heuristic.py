#!/usr/bin/env python3
"""Heuristic candidate generator for D-Q2; never claims optimality."""
from __future__ import annotations

import argparse
from collections import defaultdict
import json
from pathlib import Path
import random

from scripts.solve_q1 import read_plans
from scripts.solve_q2 import Candidate, build_candidates


def pair(left: str, right: str) -> tuple[str, str]:
    return tuple(sorted((left, right)))


def owners_for_selected(candidates: list[Candidate], selected: dict[str, int]) -> defaultdict[tuple[int, int], set[str]]:
    owners: defaultdict[tuple[int, int], set[str]] = defaultdict(set)
    for index in selected.values():
        for cell in candidates[index].cells:
            owners[cell].add(candidates[index].plan_id)
    return owners


def candidate_neighbours(candidate: Candidate, owners, plan_id: str) -> set[str]:
    neighbours: set[str] = set()
    for cell in candidate.cells:
        neighbours.update(owner for owner in owners.get(cell, set()) if owner != plan_id)
    return neighbours


def replace_selection(
    candidates: list[Candidate],
    selected: dict[str, int],
    conflicts: set[tuple[str, str]],
    plan_id: str,
    candidate_index: int,
    owners,
) -> set[tuple[str, str]]:
    old_index = selected[plan_id]
    old_neighbours = {edge for edge in conflicts if plan_id in edge}
    conflicts.difference_update(old_neighbours)
    for cell in candidates[old_index].cells:
        owners[cell].discard(plan_id)
        if not owners[cell]:
            del owners[cell]
    selected[plan_id] = candidate_index
    new_neighbours = candidate_neighbours(candidates[candidate_index], owners, plan_id)
    for neighbour in new_neighbours:
        conflicts.add(pair(plan_id, neighbour))
    for cell in candidates[candidate_index].cells:
        owners[cell].add(plan_id)
    return conflicts


def action_key(candidate: Candidate, category_rank: dict[str, int]) -> tuple:
    return (
        int(candidate.action == "revoke"),
        int(candidate.action in {"freq", "time"}),
        category_rank[candidate.category],
        abs(candidate.df) + abs(candidate.dt),
        candidate.action,
        candidate.df,
        candidate.dt,
    )


def initial_selection(plans: list[dict], candidates: list[Candidate], rng: random.Random) -> tuple[dict[str, int], dict[str, list[int]]]:
    by_plan: defaultdict[str, list[int]] = defaultdict(list)
    for index, candidate in enumerate(candidates):
        by_plan[candidate.plan_id].append(index)
    revoke_index = {plan_id: next(index for index in indexes if candidates[index].action == "revoke") for plan_id, indexes in by_plan.items()}
    selected = dict(revoke_index)
    owners = owners_for_selected(candidates, selected)
    order = [plan["id"] for plan in plans]
    rng.shuffle(order)
    rng.shuffle(order)
    category_rank = {"A": 0, "B": 1, "C": 2}
    order.sort(key=lambda identifier: (category_rank[identifier[0]], rng.random()))
    for plan_id in order:
        options = [index for index in by_plan[plan_id] if candidates[index].action != "revoke"]
        rng.shuffle(options)
        feasible = [index for index in options if not candidate_neighbours(candidates[index], owners, plan_id)]
        if feasible:
            best = min(feasible, key=lambda index: action_key(candidates[index], category_rank))
            replace_selection(candidates, selected, set(), plan_id, best, owners)
    return selected, by_plan


def local_search(
    plans: list[dict],
    candidates: list[Candidate],
    rng: random.Random,
    max_rounds: int,
    allow_revoke: bool,
) -> tuple[dict[str, int], set[tuple[str, str]]]:
    selected, by_plan = initial_selection(plans, candidates, rng)
    owners = owners_for_selected(candidates, selected)
    conflicts: set[tuple[str, str]] = set()
    category_rank = {"A": 0, "B": 1, "C": 2}
    for _ in range(max_rounds):
        changed = False
        order = [plan["id"] for plan in plans]
        rng.shuffle(order)
        order.sort(key=lambda identifier: -sum(identifier in edge for edge in conflicts))
        for plan_id in order:
            old_index = selected[plan_id]
            old_count = sum(plan_id in edge for edge in conflicts)
            options = by_plan[plan_id]
            if not allow_revoke:
                options = [index for index in options if candidates[index].action != "revoke"]
            scored = []
            for index in options:
                neighbours = candidate_neighbours(candidates[index], owners, plan_id)
                score = (len(neighbours), action_key(candidates[index], category_rank))
                scored.append((score, index))
            if not scored:
                continue
            best_score, best_index = min(scored)
            if best_index != old_index and (best_score[0] < old_count or rng.random() < 0.03):
                replace_selection(candidates, selected, conflicts, plan_id, best_index, owners)
                changed = True
                if not conflicts:
                    return selected, conflicts
        if not changed:
            plan_id = rng.choice([plan["id"] for plan in plans])
            options = by_plan[plan_id]
            if not allow_revoke:
                options = [index for index in options if candidates[index].action != "revoke"]
            replace_selection(candidates, selected, conflicts, plan_id, rng.choice(options), owners)
    return selected, conflicts


def selection_summary(plans: list[dict], candidates: list[Candidate], selected: dict[str, int]) -> dict:
    counts = {}
    actions = []
    for category in "ABC":
        ids = [plan["id"] for plan in plans if plan["category"] == category]
        selected_candidates = [candidates[selected[identifier]] for identifier in ids]
        revoked = sum(item.action == "revoke" for item in selected_candidates)
        adjusted = sum(item.action in {"freq", "time"} for item in selected_candidates)
        counts[category] = {"保留数量": len(ids) - revoked - adjusted, "调整数量": adjusted, "撤销数量": revoked}
    for identifier, index in sorted(selected.items()):
        candidate = candidates[index]
        if candidate.action == "keep":
            continue
        actions.append({
            "装备编号": identifier,
            "类别": candidate.category,
            "动作": candidate.action,
            "频移": candidate.df,
            "时移": candidate.dt,
            "频段区间": None if candidate.frequency is None else f"[{candidate.frequency[0]},{candidate.frequency[1]})",
            "时间区间": None if candidate.time is None else f"[{candidate.time[0]},{candidate.time[1]})",
            "撤销": candidate.action == "revoke",
        })
    return {"counts_by_category": counts, "actions": actions}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, default=Path("data/raw/D题/附件/附件1.xlsx"))
    parser.add_argument("--output", type=Path, default=Path("tmp/q2_heuristic.json"))
    parser.add_argument("--horizon", type=int, default=643)
    parser.add_argument("--restarts", type=int, default=120)
    parser.add_argument("--rounds", type=int, default=80)
    args = parser.parse_args()
    plans = read_plans(args.input)
    candidates = build_candidates(plans, args.horizon)
    best = None
    for seed in range(args.restarts):
        selected, conflicts = local_search(plans, candidates, random.Random(seed), args.rounds, allow_revoke=True)
        summary = selection_summary(plans, candidates, selected)
        counts = summary["counts_by_category"]
        objective = (
            sum(counts[c]["撤销数量"] for c in "ABC"),
            sum(counts[c]["调整数量"] for c in "ABC"),
            counts["A"]["调整数量"] + counts["A"]["撤销数量"],
            counts["B"]["调整数量"] + counts["B"]["撤销数量"],
            sum(abs(candidates[selected[plan["id"]]].df) + abs(candidates[selected[plan["id"]]].dt) for plan in plans),
            len(conflicts),
        )
        rank = (int(bool(conflicts)), *objective)
        if best is None or rank < best[0]:
            best = (rank, selected, conflicts, summary)
            print(json.dumps({"restart": seed, "objective": objective, "counts": counts}, ensure_ascii=False), flush=True)
        if len(conflicts) == 0 and objective[0] == 0:
            break
    if best is None:
        raise RuntimeError("no heuristic incumbent")
    rank, selected, conflicts, summary = best
    result = {
        "status": "FEASIBLE" if not conflicts else "INFEASIBLE_INCUMBENT",
        "method": "randomized constructive insertion plus conflict-repair local search",
        "objective_tuple": rank[1:],
        "time_domain": [0, args.horizon],
        "summary": summary,
        "unresolved_conflict_count": len(conflicts),
    }
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({"status": result["status"], "objective": objective, "output": str(args.output)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
