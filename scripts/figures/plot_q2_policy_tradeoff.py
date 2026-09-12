"""Plot the staged Q2 policy trade-off from frozen, auditable JSON data."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from src.visualization.style import PALETTE, apply_competition_style  # noqa: E402


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--source", type=Path,
        default=ROOT / "outputs/q2/plot_data/q2_policy_tradeoff_stage.json",
    )
    parser.add_argument(
        "--output", type=Path,
        default=ROOT / "outputs/q2/figures/fig_q2_policy_tradeoff_stage",
    )
    args = parser.parse_args()
    source = json.loads(args.source.read_text(encoding="utf-8"))
    scenarios = source["scenarios"]
    if len(scenarios) != 3:
        raise ValueError("expected T/P/E scenarios")
    ids = [item["id"] for item in scenarios]
    required = set(source["required_comparison"])
    if {f"scenario:{item}" for item in ids} != required:
        raise ValueError("comparison set does not match source")
    for item in scenarios:
        if item["C"] < 0 or item["M"] < 0:
            raise ValueError("negative objective count")
        for category_key in ("A", "B", "C_category"):
            values = item[category_key]
            if any(int(values[action]) < 0 for action in ("keep", "adjust", "cancel")):
                raise ValueError("negative category count")

    apply_competition_style(width_mm=155, height_mm=105)
    fig, axes = plt.subplots(1, 2, figsize=(6.10, 4.13), gridspec_kw={"width_ratios": [0.9, 1.45]})

    labels = ["T\n题面顺序", "P\n优先级优先", "E\n预算扩展"]
    x = np.arange(len(scenarios))
    width = 0.34
    axes[0].bar(x - width / 2, [int(item["C"]) for item in scenarios], width,
                label="撤销 C", color=PALETTE["warning"])
    axes[0].bar(x + width / 2, [int(item["M"]) for item in scenarios], width,
                label="调整 M", color=PALETTE["primary"])
    axes[0].set_xticks(x, labels)
    axes[0].set_ylabel("计划数（个）")
    axes[0].set_ylim(0, 135)
    axes[0].grid(axis="y", color=PALETTE["grid"], linewidth=0.6)
    axes[0].set_axisbelow(True)
    axes[0].legend(frameon=False, fontsize=7.5, ncol=2, loc="upper center", bbox_to_anchor=(0.5, 1.10))
    for xpos, item in zip(x, scenarios):
        axes[0].text(xpos - width / 2, int(item["C"]) + 3, str(item["C"]), ha="center", va="bottom", fontsize=8)
        axes[0].text(xpos + width / 2, int(item["M"]) + 3, str(item["M"]), ha="center", va="bottom", fontsize=8)

    category_labels = ["A", "B", "C"]
    category_keys = ["A", "B", "C_category"]
    action_colors = {"keep": PALETTE["positive"], "adjust": PALETTE["primary"], "cancel": PALETTE["warning"]}
    positions = np.arange(len(scenarios) * len(category_labels))
    bar_labels = []
    for scenario_index, item in enumerate(scenarios):
        for category in category_labels:
            bar_labels.append(f"{category}\n{item['id']}")
    bottom = np.zeros(len(positions))
    for action in ("keep", "adjust", "cancel"):
        heights = []
        for item in scenarios:
            for key in category_keys:
                heights.append(int(item[key][action]))
        axes[1].bar(positions, heights, bottom=bottom, color=action_colors[action], label={"keep": "保持", "adjust": "调整", "cancel": "撤销"}[action], width=0.72)
        bottom += np.asarray(heights)
    axes[1].set_xticks(positions, bar_labels, fontsize=8)
    axes[1].set_ylabel("类别内计划数（个）")
    axes[1].set_ylim(0, 95)
    axes[1].grid(axis="y", color=PALETTE["grid"], linewidth=0.6)
    axes[1].set_axisbelow(True)
    axes[1].legend(frameon=False, fontsize=8, ncol=3, loc="upper center", bbox_to_anchor=(0.5, 1.10))
    axes[1].text(0.01, -0.24, "注：T/E 为阶段性可行 incumbent；P 八层均已证最优。", transform=axes[1].transAxes, fontsize=7.5)

    fig.subplots_adjust(left=0.09, right=0.98, bottom=0.25, top=0.86, wspace=0.36)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(args.output.with_suffix(".pdf"), bbox_inches=None)
    fig.savefig(args.output.with_suffix(".png"), dpi=300, bbox_inches=None)
    plt.close(fig)
    print(json.dumps({"output": str(args.output), "status": "written"}, ensure_ascii=False))


if __name__ == "__main__":
    main()
