#!/usr/bin/env python3
"""Plot the frozen Q2 state composition and objective-bound certificate."""
from __future__ import annotations

import csv
import json
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.patches import Patch, Rectangle
import numpy as np

from scripts.solve_q1 import read_plans
from scripts.validate_q2 import apply_actions, expanded, occupied_cells
from src.visualization.style import PALETTE, apply_competition_style

ROOT = Path(__file__).resolve().parents[1]
Q2 = ROOT / "outputs" / "q2"
RAW = ROOT / "data" / "raw" / "D题" / "附件" / "附件1.xlsx"
PNG_DPI = 400


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_plot_data(result: dict) -> None:
    plot_data = Q2 / "plot_data"
    plot_data.mkdir(parents=True, exist_ok=True)
    with (plot_data / "category_counts.csv").open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["类别", "状态", "数量"])
        for category in "ABC":
            counts = result["summary"]["counts_by_category"][category]
            for field, label in [("保留数量", "保留"), ("调整数量", "调整"), ("撤销数量", "撤销")]:
                writer.writerow([category, label, counts[field]])
    with (plot_data / "objective_bounds.csv").open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["目标层", "下界", "上界", "状态"])
        bound_specs = [
            ("总撤销", "revocations"),
            ("A类撤销（R=6）", "revoke_A_given_R6"),
            ("B类撤销（R=6,RA=0）", "revoke_B_given_R6_RA0"),
            ("调整数（前缀固定）", "adjusted_plans_given_R6_RA0_RB4"),
            ("A类调整数（前缀固定）", "adjust_A_given_prefix"),
            ("B类调整数（前缀固定）", "adjust_B_given_prefix"),
            ("S10平移量（前缀固定）", "normalized_shift_score_x10_given_prefix"),
        ]
        for label, key in bound_specs:
            row = result["bounds"][key]
            writer.writerow([label, row.get("lower_bound"), row.get("upper_bound"), row["status"]])

    plans = read_plans(RAW)
    adjusted, errors = apply_actions(plans, result["summary"]["actions"])
    if errors:
        raise ValueError(f"Cannot build Q2 plot data from invalid result: {errors}")
    time_load = np.zeros(643, dtype=int)
    frequency_load = np.zeros(100, dtype=int)
    occupied = set()
    for plan in adjusted:
        if plan.get("revoked"):
            continue
        events = expanded(plan)
        occupied.update(occupied_cells(events))
        for f0, f1, t0, t1 in events:
            time_load[t0:t1] += f1 - f0
            frequency_load[f0:f1] += t1 - t0
    for filename, header, values in [
        ("primary_occupancy_by_time.csv", ["时间单元", "占用频率单元数"], time_load),
        ("primary_occupancy_by_frequency.csv", ["频率单元", "占用时间单元数"], frequency_load),
    ]:
        with (plot_data / filename).open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.writer(handle)
            writer.writerow(header)
            writer.writerows([[index, int(value)] for index, value in enumerate(values)])
    with (plot_data / "primary_occupied_cells.csv").open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["时间单元", "频率单元"])
        writer.writerows(sorted(occupied))


def plot_result(result: dict, grayscale: bool = False, variant: str = "modern") -> plt.Figure:
    apply_competition_style(width_mm=155, height_mm=105, variant=variant)
    fig, axes = plt.subplots(1, 2, gridspec_kw={"width_ratios": [1.10, 0.90]})
    fig.set_size_inches(155 / 25.4, 105 / 25.4)
    fig.subplots_adjust(left=0.105, right=0.975, bottom=0.17, top=0.91, wspace=0.34)
    colors = ({"保留": "#A5A9AC", "调整": "#666C70", "撤销": "#303438"} if grayscale else
              {"保留": PALETTE["keep"], "调整": PALETTE["adjust"], "撤销": PALETTE["revoke"]})

    composition = axes[0]
    categories = ["A", "B", "C"]
    y = np.arange(3)[::-1]
    left = np.zeros(3)
    for field, label in [("保留数量", "保留"), ("调整数量", "调整"), ("撤销数量", "撤销")]:
        values = np.array([result["summary"]["counts_by_category"][c][field] for c in categories])
        composition.barh(y, values, left=left, height=0.56, color=colors[label], edgecolor="white", linewidth=0.6)
        for pos, start, value in zip(y, left, values):
            if value:
                if value >= 4:
                    composition.text(
                        start + value / 2,
                        pos,
                        str(int(value)),
                        ha="center",
                        va="center",
                        fontsize=7.6,
                        color="white" if label in {"调整", "撤销"} else PALETTE["ink"],
                    )
                else:
                    composition.text(
                        start + value + 0.8,
                        pos,
                        str(int(value)),
                        ha="left",
                        va="center",
                        fontsize=7.2,
                        color=PALETTE["ink"],
                    )
        left += values
    composition.set_yticks(y, categories)
    composition.set_xlim(0, 100)
    composition.set_xlabel("计划数量（条）")
    composition.set_title("方案构成", loc="left", pad=7, fontsize=9.0)
    composition.text(-0.12, 1.035, "(a)", transform=composition.transAxes, fontsize=9.0, fontweight="bold")
    composition.xaxis.grid(True, color=PALETTE["grid"], linewidth=0.55)
    composition.set_axisbelow(True)

    certificate = axes[1]
    certificate.set_xlim(0, 1)
    certificate.set_ylim(0, 1)
    certificate.axis("off")
    certificate.set_title("优先级前缀的界", loc="left", pad=7, fontsize=9.0)
    certificate.text(-0.14, 1.035, "(b)", transform=certificate.transAxes, fontsize=9.0, fontweight="bold")
    certificate.add_patch(Rectangle((0, 0.885), 1, 0.09, facecolor=PALETTE["pale_primary"], edgecolor="none"))
    for x, value in [(0.04, "目标层"), (0.70, "LB–UB"), (0.98, "结论")]:
        certificate.text(x, 0.93, value, ha="right" if x > 0.9 else "left", va="center", fontsize=7.5, color=PALETTE["muted"])

    rows = [
        ("总撤销", 6, 6, "已证明"),
        ("A类撤销 | R=6", 0, 0, "已证明"),
        ("B类撤销 | R=6, RA=0", 4, 4, "已证明"),
        ("调整数 | 前缀固定", 126, 126, "已证明"),
        ("A类调整数 | 前缀固定", 16, 16, "已证明"),
        ("B类调整数 | 前缀固定", 34, 34, "已证明"),
        ("S10平移量 | 前缀固定", None, 775, "可行上界"),
    ]
    y_positions = np.linspace(0.835, 0.145, len(rows))
    for y_pos, (label, lb, ub, status) in zip(y_positions, rows):
        if status == "已证明":
            certificate.add_patch(Rectangle((0, y_pos - 0.045), 1, 0.09,
                                            facecolor=PALETTE["pale_primary"] if not grayscale else "#F2F2F2",
                                            edgecolor="none", zorder=0))
        else:
            certificate.add_patch(Rectangle((0, y_pos - 0.045), 1, 0.09,
                                            facecolor=PALETTE["pale_accent"] if not grayscale else "#E7E7E7",
                                            edgecolor="none", zorder=0))
        certificate.text(0.04, y_pos, label, va="center", fontsize=7.0, color=PALETTE["ink"])
        bound_text = f"≤{ub}" if lb is None else f"{lb}–{ub}"
        certificate.text(0.70, y_pos, bound_text, ha="center", va="center", fontsize=7.9, fontweight="bold")
        certificate.text(0.98, y_pos, status, ha="right", va="center", fontsize=6.9,
                         color=PALETTE["primary"] if status == "已证明" and not grayscale else PALETTE["ink"])
        certificate.plot([0.04, 0.98], [y_pos - 0.052, y_pos - 0.052], color=PALETTE["grid"], linewidth=0.45, zorder=2)
    certificate.text(0.04, 0.045, "末级 S10=775 仅为当前可行上界", fontsize=7.0, color=PALETTE["muted"])

    handles = [Patch(facecolor=colors[label], edgecolor="white", label=label) for label in ["保留", "调整", "撤销"]]
    fig.legend(handles=handles, ncol=3, loc="lower center", bbox_to_anchor=(0.34, 0.035), frameon=False,
               handlelength=1.0, handletextpad=0.35, columnspacing=1.0)
    return fig


def save_figure(fig: plt.Figure, path: Path) -> None:
    fig.savefig(path.with_suffix(".pdf"), bbox_inches=None)
    svg_path = path.with_suffix(".svg")
    fig.savefig(svg_path, bbox_inches=None)
    svg_text = svg_path.read_text(encoding="utf-8")
    svg_path.write_text("\n".join(line.rstrip() for line in svg_text.splitlines()) + "\n", encoding="utf-8")
    fig.savefig(path.with_suffix(".png"), dpi=PNG_DPI, bbox_inches=None)


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--style", choices=("modern", "print"), default="modern")
    parser.add_argument("--output-dir", type=Path, default=Q2 / "figures")
    args = parser.parse_args()
    result = load(Q2 / "results.json")
    write_plot_data(result)
    figures = args.output_dir
    figures.mkdir(parents=True, exist_ok=True)
    figure = plot_result(result, variant=args.style)
    save_figure(figure, figures / "fig_q2_solution_tradeoff")
    plt.close(figure)
    figure = plot_result(result, grayscale=True, variant=args.style)
    figure.savefig(figures / "fig_q2_solution_tradeoff_grayscale.png", dpi=PNG_DPI, bbox_inches=None)
    plt.close(figure)
    print(figures / "fig_q2_solution_tradeoff.svg")


if __name__ == "__main__":
    main()
