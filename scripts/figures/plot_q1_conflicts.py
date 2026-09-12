"""Create the Q1 category-composition figure from frozen plot-ready data."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from src.visualization.style import PALETTE, apply_competition_style  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--source",
        type=Path,
        default=ROOT / "outputs/q1/plot_data/q1_conflict_categories.json",
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=ROOT / "outputs/q1/figures/fig_q1_conflict_categories",
    )
    args = parser.parse_args()

    source = json.loads(args.source.read_text(encoding="utf-8"))
    categories = source["categories"]
    labels = [item["label"] for item in categories]
    values = [int(item["value"]) for item in categories]
    if len(labels) != len(values) or any(value < 0 for value in values):
        raise ValueError("invalid Q1 plot data")
    if sum(values) != int(source["total_conflicts"]):
        raise ValueError("category counts do not sum to total conflicts")

    apply_competition_style(width_mm=155, height_mm=90)
    fig, ax = plt.subplots()
    bars = ax.bar(labels, values, color=PALETTE["primary"], width=0.64)
    ax.set_xlabel("类别组合")
    ax.set_ylabel("冲突计划对数（对）")
    ax.set_ylim(0, max(values) * 1.18)
    ax.tick_params(axis="x", length=0)
    for bar, value in zip(bars, values):
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            value + max(values) * 0.025,
            str(value),
            ha="center",
            va="bottom",
            fontsize=9,
        )
    fig.subplots_adjust(left=0.10, right=0.98, bottom=0.22, top=0.95)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(args.output.with_suffix(".pdf"), bbox_inches=None)
    fig.savefig(args.output.with_suffix(".png"), dpi=300, bbox_inches=None)
    plt.close(fig)
    print(json.dumps({"output": str(args.output), "status": "written"}, ensure_ascii=False))


if __name__ == "__main__":
    main()
