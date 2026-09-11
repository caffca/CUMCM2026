#!/usr/bin/env python3
"""Create the formal D-Q1 conflict-structure figure from frozen Q1 data."""
from __future__ import annotations

import csv
from pathlib import Path

import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Rectangle
import numpy as np

from src.visualization.style import PALETTE, apply_competition_style


ROOT = Path(__file__).resolve().parents[1]
Q1 = ROOT / "outputs" / "q1"
PNG_DPI = 400


def read_rows(path: Path) -> list[dict[str, str]]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def build_figure(grayscale: bool = False, variant: str = "modern") -> plt.Figure:
    degree_rows = read_rows(Q1 / "plot_data" / "degree_by_plan.csv")
    pair_rows = read_rows(Q1 / "conflict_pairs.csv")
    category_rows = read_rows(Q1 / "plot_data" / "conflict_counts_by_category.csv")
    plan_ids = [row["装备编号"] for row in degree_rows]
    index = {identifier: position for position, identifier in enumerate(plan_ids)}
    n = len(plan_ids)

    normal_x: list[int] = []
    normal_y: list[int] = []
    bc_x: list[int] = []
    bc_y: list[int] = []
    for row in pair_rows:
        left_id, right_id = row["冲突装备1"], row["冲突装备2"]
        left, right = index[left_id], index[right_id]
        is_bc = {left_id[0], right_id[0]} == {"B", "C"}
        x_values, y_values = (bc_x, bc_y) if is_bc else (normal_x, normal_y)
        x_values.extend([left, right])
        y_values.extend([right, left])

    apply_competition_style(width_mm=155, height_mm=92, variant=variant)
    fig, axes = plt.subplots(1, 2, gridspec_kw={"width_ratios": [1.12, 0.88]})
    fig.set_size_inches(155 / 25.4, 92 / 25.4)
    fig.subplots_adjust(left=0.075, right=0.985, bottom=0.19, top=0.89, wspace=0.34)

    if grayscale:
        normal_color = "#7A8085"
        bc_color = "#30363A"
        boundary_color = "#8A8F93"
        bar_color = "#9DA3A7"
    else:
        normal_color = PALETTE["primary"]
        bc_color = PALETTE["accent"]
        boundary_color = PALETTE["muted"]
        bar_color = PALETTE["primary"]

    matrix = axes[0]
    matrix.set_facecolor("#FBFCFD" if not grayscale else "#FAFAFA")
    for start, end, fill in [
        (0, 20, PALETTE["pale_primary"] if not grayscale else "#F0F0F0"),
        (20, 60, "#F4F7F8" if not grayscale else "#F7F7F7"),
        (60, n, PALETTE["pale_accent"] if not grayscale else "#EEEEEE"),
    ]:
        matrix.add_patch(
            Rectangle(
                (start - 0.5, start - 0.5),
                end - start,
                end - start,
                facecolor=fill,
                edgecolor="none",
                zorder=0,
            )
        )
    matrix.scatter(normal_x, normal_y, s=6.5, marker="s", color=normal_color, linewidths=0, zorder=3)
    matrix.scatter(bc_x, bc_y, s=6.5, marker="s", color=bc_color, linewidths=0, zorder=4)
    for boundary in [20, 60]:
        matrix.axhline(boundary - 0.5, color=boundary_color, linewidth=0.7, zorder=5)
        matrix.axvline(boundary - 0.5, color=boundary_color, linewidth=0.7, zorder=5)
    centers = [9.5, 39.5, 104.5]
    matrix.set_xlim(-0.5, n - 0.5)
    matrix.set_ylim(n - 0.5, -0.5)
    matrix.set_aspect("equal", adjustable="box")
    matrix.set_xticks(centers, ["A", "B", "C"])
    matrix.set_yticks(centers, ["A", "B", "C"])
    matrix.set_xlabel("冲突装备的类别")
    matrix.set_ylabel("冲突装备的类别")
    matrix.set_title("冲突邻接", loc="left", pad=7, fontsize=9.0)
    matrix.text(-0.08, 1.035, "(a)", transform=matrix.transAxes, fontsize=9.0, fontweight="bold")

    labels = [row["类别组合"] for row in category_rows]
    values = np.asarray([100 * float(row["冲突率"]) for row in category_rows])
    colors = [bar_color] * len(labels)
    highlight = labels.index("B-C")
    colors[highlight] = "#565D63" if grayscale else PALETTE["accent"]
    bars = axes[1].barh(labels, values, color=colors, height=0.56, edgecolor="white", linewidth=0.6)
    axes[1].invert_yaxis()
    axes[1].set_xlabel("冲突率（%）")
    # Reserve a dedicated text column for the exact count/denominator labels.
    axes[1].set_xlim(0, max(values) + 3.5)
    axes[1].set_xticks([0, 2, 4, 6])
    axes[1].xaxis.grid(True, color=PALETTE["grid"], linewidth=0.55)
    axes[1].set_axisbelow(True)
    axes[1].set_title("归一化冲突率", loc="left", pad=7, fontsize=9.0)
    axes[1].text(-0.16, 1.035, "(b)", transform=axes[1].transAxes, fontsize=9.0, fontweight="bold")
    for bar, value, row in zip(bars, values, category_rows):
        count_label = f'{row["冲突对数"]}/{row["可配对数"]}'
        x = value + 0.12 if value > 0 else 0.12
        axes[1].text(
            x,
            bar.get_y() + bar.get_height() / 2,
            f"{value:.2f}% · {count_label}",
            va="center",
            fontsize=7.4,
            color=PALETTE["ink"],
            fontweight="bold" if row["类别组合"] == "B-C" else "normal",
        )

    legend_handles = [
        Line2D([], [], marker="s", linestyle="", color=normal_color, markersize=5.2, label="其他组合"),
        Line2D([], [], marker="s", linestyle="", color=bc_color, markersize=5.2, label="B–C 组合"),
    ]
    fig.legend(
        handles=legend_handles,
        loc="lower center",
        bbox_to_anchor=(0.33, 0.025),
        ncol=2,
        frameon=False,
        handletextpad=0.35,
        columnspacing=1.0,
    )
    return fig


def save_figure(fig: plt.Figure, path: Path) -> None:
    fig.savefig(path.with_suffix(".pdf"), bbox_inches=None)
    fig.savefig(path.with_suffix(".svg"), bbox_inches=None)
    fig.savefig(path.with_suffix(".png"), dpi=PNG_DPI, bbox_inches=None)


def main() -> None:
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--style", choices=("modern", "print"), default="modern")
    parser.add_argument("--output-dir", type=Path, default=Q1 / "figures")
    args = parser.parse_args()
    figures = args.output_dir
    figures.mkdir(parents=True, exist_ok=True)
    figure = build_figure(grayscale=False, variant=args.style)
    save_figure(figure, figures / "fig_q1_conflict_structure")
    plt.close(figure)
    gray = build_figure(grayscale=True, variant=args.style)
    gray.savefig(figures / "fig_q1_conflict_structure_grayscale.png", dpi=PNG_DPI, bbox_inches=None)
    plt.close(gray)
    print(figures / "fig_q1_conflict_structure.svg")


if __name__ == "__main__":
    main()
