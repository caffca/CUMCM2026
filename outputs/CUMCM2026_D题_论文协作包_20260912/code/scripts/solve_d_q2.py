"""Solve CUMCM2026 D, Q2 with exact candidate-state CP-SAT."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from d_problem.candidates import (  # noqa: E402
    generate_all_candidates,
    generate_cell_cliques,
    generate_cell_clique_map,
    generate_conflict_edges,
    verify_mask_sample,
)
from d_problem.io import load_plans, write_q2_result  # noqa: E402
from d_problem.objectives import objective_names  # noqa: E402
from d_problem.q2_model import (  # noqa: E402
    SolverConfig,
    solve_lexicographic,
    validate_selected_pairwise,
)
from d_problem.validation import validate_schedule  # noqa: E402


def _candidate_record(candidate) -> dict[str, object]:
    state = candidate.state
    return {
        "index": candidate.index,
        "state_id": candidate.state_id,
        "plan_id": candidate.plan.plan_id,
        "category": candidate.category,
        "action": candidate.action,
        "shift": candidate.shift,
        "f_shift": state.f_shift,
        "t_shift": state.t_shift,
        "displacement_cost": candidate.displacement_cost,
    }


def _write_json(path: Path, payload: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def _write_summary(
    path: Path,
    result,
    candidate_summary: dict[str, object],
    validation,
) -> None:
    metrics = result.metrics
    lines = [
        "# Q2 求解摘要",
        "",
        f"- policy: `{result.policy}`",
        f"- mode: `{result.mode}`",
        f"- proven_optimal: `{result.proven_optimal}`",
        f"- plans: `{candidate_summary['plan_count']}`",
        f"- candidate states: `{candidate_summary['candidate_state_count']}`",
        f"- state conflict edges used: `{result.edge_count}`",
        f"- lazy cuts added: `{result.cut_count}`",
        f"- solver iterations: `{result.iterations}`",
        "",
        "## 目标向量",
        "",
        "| 层 | 值 | 状态 | 下界 | gap | 秒 | CP 冲突 | 分支 |",
        "|---|---:|---|---:|---:|---:|---:|---:|",
    ]
    for layer in result.layers:
        lines.append(
            f"| {layer.name} | {layer.objective_value} | {layer.status} | "
            f"{layer.best_bound} | {layer.gap} | {layer.seconds:.3f} | "
            f"{layer.num_conflicts} | {layer.num_branches} |"
        )
    lines += [
        "",
        "## 分类统计",
        "",
        "| 指标 | A | B | C | 总计 |",
        "|---|---:|---:|---:|---:|",
        f"| 保留 | {20 - metrics.get('P_A', 0)} | {40 - metrics.get('P_B', 0)} | {90 - metrics.get('P_C', 0)} | {150 - metrics.get('P_total', 0)} |",
        f"| 调整 | {metrics.get('M_A', 0)} | {metrics.get('M_B', 0)} | {metrics.get('M_C', 0)} | {metrics.get('M_total_check', metrics.get('M', 0))} |",
        f"| 撤销 | {metrics.get('C_A', 0)} | {metrics.get('C_B', 0)} | {metrics.get('C_C', 0)} | {metrics.get('C', 0)} |",
        "",
        "## 复验",
        "",
        f"- canonical validation: plans={validation.plan_count}, occurrences={validation.occurrence_count}, conflicts={validation.conflict_count}, ok={validation.ok}",
        f"- fast selected-state conflict count: `{validate_selected_pairwise(result.selected)}`",
        f"- raw displacement: sum|df|={metrics.get('Df_sum', 0)}, sum|dt|={metrics.get('Dt_sum', 0)}, max|df|={metrics.get('Df_max', 0)}, max|dt|={metrics.get('Dt_max', 0)}; `S_sum=10D_sum`.",
        "",
        "本文件由 `scripts/solve_d_q2.py` 生成；若 `proven_optimal=false`，不得将结果称为严格词典序最优。",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _write_failure_summary(path: Path, result, candidate_summary: dict[str, object]) -> None:
    lines = [
        "# Q2 求解摘要（无可行排程）",
        "",
        f"- policy: `{result.policy}`",
        f"- mode: `{result.mode}`",
        f"- plans: `{candidate_summary['plan_count']}`",
        f"- candidate states: `{candidate_summary['candidate_state_count']}`",
        "",
        "| 层 | 状态 | 秒 |",
        "|---|---|---:|",
    ]
    for layer in result.layers:
        lines.append(f"| {layer.name} | {layer.status} | {layer.seconds:.3f} |")
    lines += [
        "",
        "该预算/约束组合没有返回可行排程；它只能作为不可行性或限时未知证据，不能写入 result2.xlsx。",
    ]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=ROOT / "D题/附件/附件1.xlsx")
    parser.add_argument("--template", type=Path, default=ROOT / "D题/附件/附件2/result2.xlsx")
    parser.add_argument("--output", type=Path, default=ROOT / "outputs/q2/result2.xlsx")
    parser.add_argument("--summary", type=Path, default=ROOT / "outputs/q2/summary.md")
    parser.add_argument("--report", type=Path, default=ROOT / "outputs/q2/solver_report.json")
    parser.add_argument("--candidate-summary", type=Path, default=ROOT / "outputs/q2/candidate_summary.json")
    parser.add_argument("--selected", type=Path, default=ROOT / "outputs/q2/selected_schedule.json")
    parser.add_argument("--policy", choices=("T", "P"), default="T")
    parser.add_argument("--mode", choices=("full", "lazy"), default="full")
    parser.add_argument(
        "--constraint-form",
        choices=("edges", "cells", "hybrid"),
        default="edges",
        help="full-mode constraint representation; cells is an equivalent clique reformulation",
    )
    parser.add_argument("--horizon", type=int, default=643)
    parser.add_argument("--time-limit", type=float, default=120.0)
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--seed", type=int, default=20260911)
    parser.add_argument("--max-lazy-iterations", type=int, default=1000)
    parser.add_argument("--budget-c", type=int, default=None)
    parser.add_argument("--budget-m", type=int, default=None)
    parser.add_argument(
        "--fixed-c",
        type=int,
        default=None,
        help="an externally certified lexicographic prefix C*=value",
    )
    parser.add_argument(
        "--fixed-m",
        type=int,
        default=None,
        help="an incumbent/externally certified prefix M=value (use with care)",
    )
    parser.add_argument(
        "--hint",
        type=Path,
        default=None,
        help="optional selected_schedule.json used only as a CP-SAT warm-start hint",
    )
    args = parser.parse_args()
    if args.mode == "lazy" and args.constraint_form != "edges":
        parser.error("lazy mode requires --constraint-form edges")

    plans = load_plans(args.input)
    grouped, flat = generate_all_candidates(plans, horizon=args.horizon)
    edge_list: list[tuple[int, int]] = []
    cell_cliques = []
    cell_clique_map = None
    checked = 0
    if args.mode == "full":
        edge_list = generate_conflict_edges(grouped)
        if args.constraint_form in {"cells", "hybrid"}:
            cell_cliques = generate_cell_cliques(flat)
        # A deterministic sample checks the accelerated edge predicate against
        # the canonical interval detector without duplicating the full O(n^2)
        # validation cost.
        sample_pairs = edge_list[:500] + edge_list[-500:]
        checked = verify_mask_sample(flat, sample_pairs)
    elif args.mode == "lazy":
        # Lazy mode still uses the exact occupancy map to turn an incumbent
        # conflict into a stronger resource-cell clique cut.
        cell_clique_map = generate_cell_clique_map(flat)

    candidate_summary = {
        "plan_count": len(plans),
        "candidate_state_count": len(flat),
        "candidate_min": min(map(len, grouped)),
        "candidate_max": max(map(len, grouped)),
        "horizon": args.horizon,
        "state_conflict_edges": len(edge_list),
        "cell_clique_count": len(cell_cliques),
        "mask_canonical_sample_checked": checked,
        "mode": args.mode,
        "constraint_form": args.constraint_form,
    }
    _write_json(args.candidate_summary, candidate_summary)

    hints = None
    if args.hint is not None:
        hint_payload = json.loads(args.hint.read_text(encoding="utf-8"))
        hints = {int(item["index"]): 1 for item in hint_payload.get("selected", [])}

    budgets = {}
    if args.budget_c is not None:
        budgets["C"] = args.budget_c
    if args.budget_m is not None:
        budgets["M"] = args.budget_m
    fixed_initial = {}
    if args.fixed_c is not None:
        fixed_initial["C"] = args.fixed_c
    if args.fixed_m is not None:
        fixed_initial["M"] = args.fixed_m
    if not fixed_initial:
        fixed_initial = None

    result = solve_lexicographic(
        grouped,
        flat,
        policy=args.policy,
        mode=args.mode,
        edges=edge_list,
        budgets=budgets or None,
        config=SolverConfig(
            time_limit_seconds=args.time_limit,
            num_search_workers=args.workers,
            random_seed=args.seed,
        ),
        max_lazy_iterations=args.max_lazy_iterations,
        cell_cliques=cell_cliques,
        cell_clique_map=cell_clique_map,
        constraint_form=args.constraint_form,
        hints=hints,
        fixed_initial=fixed_initial,
    )
    if not result.selected:
        _write_json(
            args.report,
            {
                "policy": result.policy,
                "mode": result.mode,
                "horizon": args.horizon,
                "budgets": budgets,
                "fixed_initial": fixed_initial or {},
                "objective_names": list(objective_names(args.policy)),
                "solver_config": {
                    "time_limit_seconds_per_layer": args.time_limit,
                    "num_search_workers": args.workers,
                    "random_seed": args.seed,
                },
                "edge_count": result.edge_count,
                "cut_count": result.cut_count,
                "iterations": result.iterations,
                "proven_optimal": result.proven_optimal,
                "layers": result.layer_dicts(),
            },
        )
        _write_failure_summary(args.summary, result, candidate_summary)
        print(
            json.dumps(
                {
                    "policy": result.policy,
                    "mode": result.mode,
                    "proven_optimal": result.proven_optimal,
                    "status": result.layers[-1].status if result.layers else "NO_STATUS",
                    "result": None,
                },
                ensure_ascii=False,
            )
        )
        return

    validation = validate_schedule(
        [candidate.state for candidate in result.selected], horizon=args.horizon
    )
    write_q2_result(args.output, result.selected, args.template)
    _write_json(
        args.selected,
        {
            "policy": result.policy,
            "mode": result.mode,
            "proven_optimal": result.proven_optimal,
            "budgets": budgets,
            "fixed_initial": fixed_initial or {},
            "metrics": dict(result.metrics),
            "selected": [_candidate_record(candidate) for candidate in result.selected],
            "validation": {
                "plan_count": validation.plan_count,
                "occurrence_count": validation.occurrence_count,
                "conflict_count": validation.conflict_count,
                "ok": validation.ok,
            },
        },
    )
    _write_json(
        args.report,
        {
            "policy": result.policy,
            "mode": result.mode,
            "horizon": args.horizon,
            "budgets": budgets,
            "fixed_initial": fixed_initial or {},
            "objective_names": list(objective_names(args.policy)),
            "solver_config": {
                "time_limit_seconds_per_layer": args.time_limit,
                "num_search_workers": args.workers,
                "random_seed": args.seed,
            },
            "metrics": dict(result.metrics),
            "edge_count": result.edge_count,
            "cut_count": result.cut_count,
            "iterations": result.iterations,
            "proven_optimal": result.proven_optimal,
            "layers": result.layer_dicts(),
            "canonical_validation": {
                "plan_count": validation.plan_count,
                "occurrence_count": validation.occurrence_count,
                "conflict_count": validation.conflict_count,
                "ok": validation.ok,
            },
        },
    )
    _write_summary(args.summary, result, candidate_summary, validation)
    print(
        json.dumps(
            {
                "policy": result.policy,
                "mode": result.mode,
                "candidates": len(flat),
                "edges": result.edge_count,
                "cuts": result.cut_count,
                "iterations": result.iterations,
                "metrics": dict(result.metrics),
                "proven_optimal": result.proven_optimal,
                "conflicts": validation.conflict_count,
                "result": str(args.output),
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
