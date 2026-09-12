"""Run Q2 T/P policies and a bounded E (epsilon-constraint) grid."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
sys.path.insert(0, str(ROOT / "scripts"))

from d_problem.candidates import (  # noqa: E402
    generate_all_candidates,
    generate_cell_clique_map,
    generate_cell_cliques,
    generate_conflict_edges,
    verify_mask_sample,
)
from d_problem.io import load_plans, write_q2_result  # noqa: E402
from d_problem.objectives import objective_names  # noqa: E402
from d_problem.q2_model import SolverConfig, solve_lexicographic  # noqa: E402
from d_problem.validation import validate_schedule  # noqa: E402
from solve_d_q2 import _candidate_record, _write_json, _write_summary  # noqa: E402


def _run_one(
    label: str,
    policy: str,
    grouped,
    flat,
    edges,
    cell_cliques,
    cell_clique_map,
    args,
    budgets=None,
    fixed_initial=None,
):
    result = solve_lexicographic(
        grouped,
        flat,
        policy=policy,
        mode=args.mode,
        edges=edges,
        budgets=budgets,
        config=SolverConfig(
            time_limit_seconds=args.time_limit,
            num_search_workers=args.workers,
            random_seed=args.seed,
        ),
        max_lazy_iterations=args.max_lazy_iterations,
        cell_cliques=cell_cliques,
        cell_clique_map=cell_clique_map,
        constraint_form=args.constraint_form,
        fixed_initial=fixed_initial,
    )
    validation = None
    if result.selected:
        validation = validate_schedule(
            [candidate.state for candidate in result.selected], horizon=args.horizon
        )
        output = args.output_dir / f"result2_{label}.xlsx"
        selected_path = args.output_dir / f"selected_{label}.json"
        report_path = args.output_dir / f"solver_{label}.json"
        summary_path = args.output_dir / f"summary_{label}.md"
        write_q2_result(output, result.selected, args.template)
        _write_json(
            selected_path,
            {
                "label": label,
                "policy": result.policy,
                "mode": result.mode,
                "proven_optimal": result.proven_optimal,
                "budgets": budgets or {},
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
            report_path,
            {
                "label": label,
                "policy": result.policy,
                "mode": result.mode,
                "horizon": args.horizon,
                "objective_names": list(objective_names(policy)),
                "budgets": budgets or {},
                "fixed_initial": fixed_initial or {},
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
        candidate_summary = {
            "plan_count": len(grouped),
            "candidate_state_count": len(flat),
        }
        _write_summary(summary_path, result, candidate_summary, validation)
    return result, validation


def _row(label, result, validation, budgets=None):
    metrics = dict(result.metrics)
    row = {
        "方案": label,
        "policy": result.policy,
        "mode": result.mode,
        "proven_optimal": result.proven_optimal,
        "C": metrics.get("C"),
        "M": metrics.get("M"),
        "P_A": metrics.get("P_A"),
        "P_B": metrics.get("P_B"),
        "P_C": metrics.get("P_C"),
        "C_A": metrics.get("C_A"),
        "C_B": metrics.get("C_B"),
        "C_C": metrics.get("C_C"),
        "M_A": metrics.get("M_A"),
        "M_B": metrics.get("M_B"),
        "M_C": metrics.get("M_C"),
        "S_sum": metrics.get("S_sum"),
        "S_max": metrics.get("S_max"),
        "Df_sum": metrics.get("Df_sum"),
        "Dt_sum": metrics.get("Dt_sum"),
        "Df_max": metrics.get("Df_max"),
        "Dt_max": metrics.get("Dt_max"),
        "conflicts": None if validation is None else validation.conflict_count,
        "budgets": json.dumps(budgets or {}, ensure_ascii=False),
    }
    return row


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, default=ROOT / "D题/附件/附件1.xlsx")
    parser.add_argument("--template", type=Path, default=ROOT / "D题/附件/附件2/result2.xlsx")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "outputs/q2")
    parser.add_argument("--mode", choices=("full", "lazy"), default="full")
    parser.add_argument("--constraint-form", choices=("edges", "cells", "hybrid"), default="cells")
    parser.add_argument("--horizon", type=int, default=643)
    parser.add_argument("--time-limit", type=float, default=120.0)
    parser.add_argument("--workers", type=int, default=8)
    parser.add_argument("--seed", type=int, default=20260911)
    parser.add_argument("--max-lazy-iterations", type=int, default=1000)
    parser.add_argument("--fixed-c", type=int, default=None, help="certified T prefix, if available")
    parser.add_argument("--fixed-m", type=int, default=None, help="incumbent T prefix, if deliberately conditioned")
    parser.add_argument("--run-e", action="store_true")
    parser.add_argument("--delta-c", type=int, nargs="*", default=[0, 1])
    parser.add_argument("--delta-m", type=int, nargs="*", default=[0, 1, 2])
    args = parser.parse_args()
    if args.mode == "lazy" and args.constraint_form != "edges":
        parser.error("lazy mode requires --constraint-form edges")

    args.output_dir.mkdir(parents=True, exist_ok=True)
    plans = load_plans(args.input)
    grouped, flat = generate_all_candidates(plans, horizon=args.horizon)
    edges = generate_conflict_edges(grouped) if args.mode == "full" else []
    cell_cliques = generate_cell_cliques(flat) if args.mode == "full" and args.constraint_form in {"cells", "hybrid"} else []
    cell_clique_map = generate_cell_clique_map(flat) if args.mode == "lazy" else None
    if edges:
        verify_mask_sample(flat, edges[:500] + edges[-500:])

    rows = []
    t_fixed = {}
    if args.fixed_c is not None:
        t_fixed["C"] = args.fixed_c
    if args.fixed_m is not None:
        t_fixed["M"] = args.fixed_m
    t_result, t_validation = _run_one(
        "T", "T", grouped, flat, edges, cell_cliques, cell_clique_map, args,
        fixed_initial=t_fixed or None,
    )
    rows.append(_row("T", t_result, t_validation))
    p_result, p_validation = _run_one("P", "P", grouped, flat, edges, cell_cliques, cell_clique_map, args)
    rows.append(_row("P", p_result, p_validation))

    if args.run_e and t_result.proven_optimal:
        for delta_c in args.delta_c:
            for delta_m in args.delta_m:
                budgets = {
                    "C": int(t_result.metrics["C"]) + delta_c,
                    "M": int(t_result.metrics["M"]) + delta_m,
                }
                label = f"E_dc{delta_c}_dm{delta_m}"
                e_result, e_validation = _run_one(
                    label,
                    "P",
                    grouped,
                    flat,
                    edges,
                    cell_cliques,
                    cell_clique_map,
                    args,
                    budgets=budgets,
                )
                rows.append(_row(label, e_result, e_validation, budgets))
    elif args.run_e:
        rows.append({"方案": "E_SKIPPED", "reason": "T is not proven optimal"})

    comparison = args.output_dir / "policy_comparison.csv"
    fieldnames = sorted({key for row in rows for key in row})
    with comparison.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    _write_json(
        args.output_dir / "policy_run_meta.json",
        {
            "candidate_state_count": len(flat),
            "state_conflict_edges": len(edges),
            "cell_clique_count": len(cell_cliques),
            "mode": args.mode,
            "constraint_form": args.constraint_form,
            "horizon": args.horizon,
            "rows": rows,
        },
    )
    print(json.dumps({"rows": len(rows), "comparison": str(comparison)}, ensure_ascii=False))


if __name__ == "__main__":
    main()
