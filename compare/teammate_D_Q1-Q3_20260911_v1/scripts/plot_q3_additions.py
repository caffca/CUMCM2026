#!/usr/bin/env python3
"""Plot the fixed-Q2 Q3 C-class placement and its temporal distribution."""
from __future__ import annotations

import csv
import json
from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

from scripts.solve_q3 import build_q2_occupancy, enumerate_candidates
from src.visualization.style import PALETTE, apply_competition_style


ROOT = Path(__file__).resolve().parents[1]
Q3 = ROOT / "outputs" / "q3"
RAW = ROOT / "data" / "raw" / "D题" / "附件" / "附件1.xlsx"
# The Q3 figure must consume the same workbook-derived Q2 interface as the
# solver and validator, not a separately selected Q2 result file.
Q2_RESULT = ROOT / "outputs" / "q3" / "q2_input_from_result2.json"
PNG_DPI = 400


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def write_plot_data(result: dict, candidates: list) -> None:
    plot_data = Q3 / "plot_data"
    plot_data.mkdir(parents=True, exist_ok=True)
    with (plot_data / "feasible_candidate_starts.csv").open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["频段起点", "时间起点"])
        writer.writerows([[candidate.frequency_start, candidate.time_start] for candidate in candidates])

    selected_rows = result["selected_plans"]
    with (plot_data / "selected_start_positions.csv").open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["新增用频装备序号", "频段起点", "时间起点", "频段区间", "时间区间"])
        writer.writerows(
            [
                [
                    row["新增用频装备序号"],
                    row["频段起点"],
                    row["时间起点"],
                    row["频段区间"],
                    row["时间区间"],
                ]
                for row in selected_rows
            ]
        )

    time_blocks = [(0, 100), (100, 200), (200, 300), (300, 400), (400, 500), (500, 532)]
    with (plot_data / "selected_counts_by_time_block.csv").open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["时间起点区间", "新增计划数量"])
        writer.writerows(
            [[f"[{left},{right})", sum(left <= row["时间起点"] < right for row in selected_rows)] for left, right in time_blocks]
        )

    frequency_blocks = [(left, min(left + 10, 98)) for left in range(0, 98, 10)]
    with (plot_data / "selected_counts_by_frequency_block.csv").open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["频段起点区间", "新增计划数量"])
        writer.writerows(
            [[f"[{left},{right})", sum(left <= row["频段起点"] < right for row in selected_rows)] for left, right in frequency_blocks]
        )


def plot_layout(result: dict, candidates: list, grayscale: bool = False, variant: str = "modern") -> plt.Figure:
    apply_competition_style(width_mm=155, height_mm=96, variant=variant)
    fig, axes = plt.subplots(1, 2, gridspec_kw={"width_ratios": [1.36, 0.84]})
    fig.set_size_inches(155 / 25.4, 96 / 25.4)
    fig.subplots_adjust(left=0.105, right=0.975, bottom=0.17, top=0.90, wspace=0.34)

    if grayscale:
        candidate_color = "#B8BEC2"
        selected_color = "#263238"
        bar_color = "#4D565C"
    else:
        candidate_color = PALETTE["secondary"]
        selected_color = PALETTE["primary"]
        bar_color = PALETTE["primary"]

    selected = result["selected_plans"]
    layout = axes[0]
    layout.scatter(
        [candidate.time_start for candidate in candidates],
        [candidate.frequency_start for candidate in candidates],
        s=4.0,
        color=candidate_color,
        alpha=0.32,
        linewidths=0,
        rasterized=False,
        label="与 Q2 不冲突的候选",
    )
    layout.scatter(
        [row["时间起点"] for row in selected],
        [row["频段起点"] for row in selected],
        s=21,
        color=selected_color,
        edgecolors="white",
        linewidths=0.35,
        alpha=0.95,
        zorder=3,
        label=f"选中新增（{len(selected)} 台）",
    )
    layout.set_xlim(-8, 540)
    layout.set_ylim(-3, 101)
    layout.set_xlabel("首次时间起点 t₀（Δt）")
    layout.set_ylabel("频段起点 f₀（Δf）")
    layout.set_title("可行起点与选中方案", loc="left", pad=7, fontsize=9.0)
    layout.text(-0.10, 1.035, "(a)", transform=layout.transAxes, fontsize=9.0, fontweight="bold")
    layout.grid(True, color=PALETTE["grid"], linewidth=0.55)
    layout.set_axisbelow(True)
    layout.legend(
        loc="upper right",
        frameon=True,
        facecolor="white",
        edgecolor=PALETTE["grid"],
        framealpha=0.92,
        fontsize=7.0,
        markerscale=1.2,
        borderpad=0.45,
        handletextpad=0.45,
    )

    time_blocks = [(0, 100), (100, 200), (200, 300), (300, 400), (400, 500), (500, 532)]
    counts = [sum(left <= row["时间起点"] < right for row in selected) for left, right in time_blocks]
    distribution = axes[1]
    y = np.arange(len(time_blocks))
    distribution.barh(y, counts, color=bar_color, height=0.56, edgecolor="white", linewidth=0.6)
    for position, value in zip(y, counts):
        distribution.text(value + 0.8, position, str(value), ha="left", va="center", fontsize=7.8, color=PALETTE["ink"])
    distribution.set_yticks(y, [f"[{left},{right})" for left, right in time_blocks])
    distribution.invert_yaxis()
    distribution.set_xlim(0, max(counts) + 7)
    distribution.set_xlabel("新增计划数量（台）")
    distribution.set_title("时间起点分布", loc="left", pad=7, fontsize=9.0)
    distribution.text(-0.16, 1.035, "(b)", transform=distribution.transAxes, fontsize=9.0, fontweight="bold")
    distribution.xaxis.grid(True, color=PALETTE["grid"], linewidth=0.55)
    distribution.set_axisbelow(True)
    return fig


def save_figure(fig: plt.Figure, path: Path) -> None:
    fig.savefig(path.with_suffix(".pdf"), bbox_inches=None)
    svg_path = path.with_suffix(".svg")
    fig.savefig(svg_path, bbox_inches=None)
    svg_text = svg_path.read_text(encoding="utf-8")
    svg_path.write_text(
        "\n".join(line.rstrip() for line in svg_text.splitlines()) + "\n",
        encoding="utf-8",
    )
    fig.savefig(path.with_suffix(".png"), dpi=PNG_DPI, bbox_inches=None)


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--style", choices=("modern", "print"), default="modern")
    parser.add_argument("--output-dir", type=Path, default=Q3 / "figures")
    args = parser.parse_args()
    result = load(Q3 / "results.json")
    occupied, _fixed = build_q2_occupancy(RAW, Q2_RESULT, 643)
    candidates, _total = enumerate_candidates(occupied, 643)
    write_plot_data(result, candidates)
    figures = args.output_dir
    figures.mkdir(parents=True, exist_ok=True)
    figure = plot_layout(result, candidates, grayscale=False, variant=args.style)
    save_figure(figure, figures / "fig_q3_addition_layout")
    plt.close(figure)
    figure = plot_layout(result, candidates, grayscale=True, variant=args.style)
    figure.savefig(figures / "fig_q3_addition_layout_grayscale.png", dpi=PNG_DPI, bbox_inches=None)
    plt.close(figure)
    print(figures / "fig_q3_addition_layout.svg")


if __name__ == "__main__":
    main()
