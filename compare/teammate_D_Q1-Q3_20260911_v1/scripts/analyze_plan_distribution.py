#!/usr/bin/env python3
"""Audit D-problem frequency/time distributions before Q1-Q3 modeling.

This is an exploratory evidence script. It reads the unchanged Attachment 1,
expands every repeated-use event, summarizes one- and two-dimensional resource
loads, and demonstrates how a complete C-class periodic plan must be tested.

The provisional time resource domain is the smallest envelope containing every
expanded raw event. It is not promoted as the official Q3 boundary until the
Markdown statement confirms the time-domain definition.
"""
from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
import sys

import matplotlib.pyplot as plt
from matplotlib.colors import ListedColormap
import numpy as np
from PIL import Image


SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from solve_q1 import expanded_events, read_plans, validate_recurrence_examples  # noqa: E402


COLORS = {"A": "#4C78A8", "B": "#D9823B", "C": "#2A7F74"}
FREQUENCY_EDGES = np.arange(0, 101, 10, dtype=int)
FIRST_TIME_EDGES = np.arange(0, 541, 90, dtype=int)
C_FREQUENCY_WIDTH = 3
C_DURATION = 2
C_IDLE_GAP = 8
C_USES = 12
C_START_STEP = C_DURATION + C_IDLE_GAP


def configure_matplotlib() -> None:
    plt.rcParams.update(
        {
            "font.sans-serif": ["Microsoft YaHei", "SimHei", "DengXian", "Arial"],
            "font.family": "sans-serif",
            "axes.unicode_minus": False,
            "font.size": 9,
            "axes.labelsize": 9,
            "axes.titlesize": 10,
            "legend.fontsize": 8,
            "xtick.labelsize": 8,
            "ytick.labelsize": 8,
            "axes.edgecolor": "#777777",
            "axes.linewidth": 0.8,
            "grid.color": "#D9D9D9",
            "grid.linewidth": 0.6,
            "grid.alpha": 0.7,
            "savefig.bbox": "tight",
            "savefig.facecolor": "white",
        }
    )


def quantile_summary(values: list[int]) -> dict[str, float | int]:
    array = np.asarray(values, dtype=float)
    return {
        "min": int(array.min()),
        "q25": float(np.quantile(array, 0.25)),
        "median": float(np.median(array)),
        "q75": float(np.quantile(array, 0.75)),
        "max": int(array.max()),
        "mean": float(array.mean()),
        "unique": int(np.unique(array).size),
    }


def build_occupancy(plans: list[dict]) -> tuple[int, np.ndarray, dict[str, np.ndarray]]:
    horizon = max(event[3] for plan in plans for event in expanded_events(plan))
    occupancy = np.zeros((horizon, 100), dtype=np.int16)
    by_category = {category: np.zeros_like(occupancy) for category in "ABC"}
    for plan in plans:
        for frequency_start, frequency_end, time_start, time_end in expanded_events(plan):
            occupancy[time_start:time_end, frequency_start:frequency_end] += 1
            by_category[plan["category"]][
                time_start:time_end, frequency_start:frequency_end
            ] += 1
    return horizon, occupancy, by_category


def evaluate_c_candidates(
    occupancy: np.ndarray,
    frequency_width: int = C_FREQUENCY_WIDTH,
    duration: int = C_DURATION,
    idle_gap: int = C_IDLE_GAP,
    uses: int = C_USES,
) -> np.ndarray:
    horizon, frequency_count = occupancy.shape
    start_step = duration + idle_gap
    last_offset = (uses - 1) * start_step + duration
    time_start_count = horizon - last_offset + 1
    frequency_start_count = frequency_count - frequency_width + 1
    if time_start_count <= 0 or frequency_start_count <= 0:
        raise ValueError("resource domain is smaller than one C-class plan")

    feasible = np.ones((time_start_count, frequency_start_count), dtype=bool)
    for time_start in range(time_start_count):
        for frequency_start in range(frequency_start_count):
            for occurrence in range(uses):
                event_time = time_start + occurrence * start_step
                if np.any(
                    occupancy[
                        event_time : event_time + duration,
                        frequency_start : frequency_start + frequency_width,
                    ]
                    > 0
                ):
                    feasible[time_start, frequency_start] = False
                    break
    return feasible


def write_csv(path: Path, headers: list[str], rows: list[list[object]]) -> None:
    with path.open("w", encoding="utf-8-sig", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(headers)
        writer.writerows(rows)


def save_figure(fig: plt.Figure, output_dir: Path, stem: str) -> None:
    png_path = output_dir / f"{stem}.png"
    fig.savefig(png_path, dpi=320)
    fig.savefig(output_dir / f"{stem}.pdf")
    plt.close(fig)
    with Image.open(png_path) as image:
        image.convert("L").save(output_dir / f"{stem}_grayscale.png")


def plot_frequency_distribution(
    plans: list[dict],
    by_category: dict[str, np.ndarray],
    output_dir: Path,
) -> None:
    """Chart contract: show whether class locations are frequency-segregated."""
    labels = [f"{left}–{right}" for left, right in zip(FREQUENCY_EDGES[:-1], FREQUENCY_EDGES[1:])]
    x = np.arange(len(labels))
    width = 0.24
    fig, axes = plt.subplots(2, 1, figsize=(6.2, 6.0), sharex=True, constrained_layout=True)

    for offset, category in zip((-1, 0, 1), "ABC"):
        category_plans = [plan for plan in plans if plan["category"] == category]
        counts, _ = np.histogram(
            [plan["frequency"][0] for plan in category_plans], bins=FREQUENCY_EDGES
        )
        axes[0].bar(
            x + offset * width,
            counts / len(category_plans) * 100,
            width=width,
            color=COLORS[category],
            label=f"{category} 类",
        )

        loads = np.array(
            [
                by_category[category][:, left:right].sum()
                for left, right in zip(FREQUENCY_EDGES[:-1], FREQUENCY_EDGES[1:])
            ],
            dtype=float,
        )
        axes[1].plot(
            x,
            loads / loads.sum() * 100,
            color=COLORS[category],
            marker={"A": "o", "B": "s", "C": "^"}[category],
            linewidth=1.4,
            markersize=4,
            label=f"{category} 类",
        )

    axes[0].set_ylabel("计划占比（%）")
    axes[0].set_title("首次频段起点分布")
    axes[0].grid(axis="y")
    axes[0].legend(ncol=3, frameon=False)
    axes[1].set_ylabel("事件占用量占比（%）")
    axes[1].set_xlabel("频率区间（Δf）")
    axes[1].set_title("展开全部重复事件后的频率负载")
    axes[1].set_xticks(x, labels, rotation=30, ha="right")
    axes[1].grid(axis="y")
    axes[1].legend(ncol=3, frameon=False)
    save_figure(fig, output_dir, "frequency_distribution")


def plot_time_distribution(
    plans: list[dict],
    occupancy: np.ndarray,
    output_dir: Path,
) -> None:
    """Chart contract: show initial-time spread and expanded timeline load."""
    labels = [f"{left}–{right}" for left, right in zip(FIRST_TIME_EDGES[:-1], FIRST_TIME_EDGES[1:])]
    x = np.arange(len(labels))
    width = 0.24
    fig, axes = plt.subplots(2, 1, figsize=(6.2, 6.0), constrained_layout=True)

    for offset, category in zip((-1, 0, 1), "ABC"):
        category_plans = [plan for plan in plans if plan["category"] == category]
        counts, _ = np.histogram(
            [plan["time"][0] for plan in category_plans], bins=FIRST_TIME_EDGES
        )
        axes[0].bar(
            x + offset * width,
            counts / len(category_plans) * 100,
            width=width,
            color=COLORS[category],
            label=f"{category} 类",
        )

    axes[0].set_ylabel("计划占比（%）")
    axes[0].set_xlabel("首次开始时刻（Δt）")
    axes[0].set_title("首次时间起点分布")
    axes[0].set_xticks(x, labels)
    axes[0].grid(axis="y")
    axes[0].legend(ncol=3, frameon=False)

    time_load = (occupancy > 0).mean(axis=1) * 100
    axes[1].plot(
        np.arange(occupancy.shape[0]),
        time_load,
        color=COLORS["A"],
        linewidth=1.0,
    )
    axes[1].axhline(
        float(time_load.mean()),
        color=COLORS["B"],
        linestyle="--",
        linewidth=1.2,
        label=f"平均 {time_load.mean():.1f}%",
    )
    axes[1].set_xlim(0, occupancy.shape[0])
    axes[1].set_ylim(bottom=0)
    axes[1].set_ylabel("该时刻频率占用率（%）")
    axes[1].set_xlabel("展开后的时间（Δt）")
    axes[1].set_title("展开全部重复事件后的时间负载")
    axes[1].grid(axis="y")
    axes[1].legend(frameon=False)
    save_figure(fig, output_dir, "time_distribution")


def plot_occupancy_heatmap(occupancy: np.ndarray, output_dir: Path) -> None:
    """Chart contract: show the raw two-dimensional load and overlap clusters."""
    fig, ax = plt.subplots(figsize=(6.3, 3.6), constrained_layout=True)
    image = ax.imshow(
        occupancy.T,
        aspect="auto",
        origin="lower",
        interpolation="nearest",
        extent=[0, occupancy.shape[0], 0, occupancy.shape[1]],
        cmap="viridis",
        vmin=0,
        vmax=max(1, int(occupancy.max())),
    )
    ax.set_xlabel("展开后的时间（Δt）")
    ax.set_ylabel("频率（Δf）")
    ax.set_title("原始计划的时频占用次数")
    colorbar = fig.colorbar(image, ax=ax, pad=0.02)
    colorbar.set_label("同一资源单元上的计划数")
    save_figure(fig, output_dir, "raw_time_frequency_occupancy")


def plot_candidate_map(feasible: np.ndarray, output_dir: Path) -> None:
    """Chart contract: show why free-cell area is not a C-plan capacity proof."""
    fig, ax = plt.subplots(figsize=(6.3, 3.8), constrained_layout=True)
    cmap = ListedColormap(["#EDF2F7", "#2A7F74"])
    ax.imshow(
        feasible.T,
        aspect="auto",
        origin="lower",
        interpolation="nearest",
        extent=[0, feasible.shape[0], 0, feasible.shape[1]],
        cmap=cmap,
        vmin=0,
        vmax=1,
    )
    rate = feasible.mean() * 100
    ax.text(
        0.99,
        0.98,
        f"可行起点 {feasible.sum():,}/{feasible.size:,}（{rate:.2f}%）",
        transform=ax.transAxes,
        ha="right",
        va="top",
        color="#222222",
        bbox={"facecolor": "white", "edgecolor": "#D9D9D9", "alpha": 0.9, "pad": 3},
    )
    ax.set_xlabel("C 类计划首次开始时刻（Δt）")
    ax.set_ylabel("C 类计划频段起点（Δf）")
    ax.set_title("原始占用下完整 C 类有限重复计划的可行起点（方法演示）")
    save_figure(fig, output_dir, "raw_c_candidate_feasibility")


def analyze(plans: list[dict], output_dir: Path) -> dict:
    horizon, occupancy, by_category = build_occupancy(plans)
    feasible = evaluate_c_candidates(occupancy)

    summary: dict[str, object] = {
        "status": "EXPLORE_ONLY",
        "input_plan_count": len(plans),
        "resource_domain": {
            "frequency": "[0,100) from statement",
            "provisional_time": f"[0,{horizon}) from maximum expanded raw-event end",
            "warning": "The provisional time boundary is not the official Q3 boundary until checked against the Markdown statement.",
        },
        "class_parameters": {},
        "global_occupancy": {},
        "raw_c_candidate_demo": {},
    }

    for category in "ABC":
        category_plans = [plan for plan in plans if plan["category"] == category]
        events = [event for plan in category_plans for event in expanded_events(plan)]
        plan = category_plans[0]
        summary["class_parameters"][category] = {
            "plans": len(category_plans),
            "events": len(events),
            "frequency_width": plan["frequency"][1] - plan["frequency"][0],
            "event_duration": plan["time"][1] - plan["time"][0],
            "gap": plan["gap"],
            "start_step": (plan["time"][1] - plan["time"][0]) + plan["gap"],
            "uses": plan["uses"],
            "cells_per_plan": (
                (plan["frequency"][1] - plan["frequency"][0])
                * (plan["time"][1] - plan["time"][0])
                * plan["uses"]
            ),
            "frequency_start": quantile_summary(
                [plan["frequency"][0] for plan in category_plans]
            ),
            "first_time_start": quantile_summary(
                [plan["time"][0] for plan in category_plans]
            ),
            "expanded_time_end_max": max(event[3] for event in events),
            "weighted_cell_demand": int(by_category[category].sum()),
            "union_cells_within_class": int((by_category[category] > 0).sum()),
        }

    occupied = occupancy > 0
    summary["global_occupancy"] = {
        "provisional_rectangle_cells": int(occupancy.size),
        "occupied_union_cells": int(occupied.sum()),
        "occupied_union_rate": float(occupied.mean()),
        "free_cell_rate": float(1 - occupied.mean()),
        "weighted_plan_cell_demand": int(occupancy.sum()),
        "overlap_excess_cells": int(np.clip(occupancy - 1, 0, None).sum()),
        "maximum_plans_on_one_cell": int(occupancy.max()),
        "time_slots_ever_used": int(np.any(occupied, axis=1).sum()),
        "frequency_bins_ever_used": int(np.any(occupied, axis=0).sum()),
    }
    summary["raw_c_candidate_demo"] = {
        "c_parameters": {
            "frequency_width": C_FREQUENCY_WIDTH,
            "duration": C_DURATION,
            "idle_gap": C_IDLE_GAP,
            "start_step": C_START_STEP,
            "uses": C_USES,
        },
        "candidate_time_start": [0, feasible.shape[0] - 1],
        "candidate_frequency_start": [0, feasible.shape[1] - 1],
        "candidate_count": int(feasible.size),
        "individually_feasible_count": int(feasible.sum()),
        "individually_feasible_rate": float(feasible.mean()),
        "warning": "This uses the raw conflicting schedule, not the Q2 output, and is not the Q3 answer.",
    }

    frequency_rows: list[list[object]] = []
    for left, right in zip(FREQUENCY_EDGES[:-1], FREQUENCY_EDGES[1:]):
        row: list[object] = [int(left), int(right)]
        for category in "ABC":
            category_plans = [plan for plan in plans if plan["category"] == category]
            count = sum(left <= plan["frequency"][0] < right for plan in category_plans)
            row.extend([count, count / len(category_plans)])
        band = occupancy[:, left:right]
        row.extend([int(band.sum()), float((band > 0).mean())])
        frequency_rows.append(row)
    write_csv(
        output_dir / "frequency_deciles.csv",
        [
            "频率左端点",
            "频率右端点",
            "A类起点数",
            "A类起点占比",
            "B类起点数",
            "B类起点占比",
            "C类起点数",
            "C类起点占比",
            "计划单元占用量",
            "资源单元占用率",
        ],
        frequency_rows,
    )

    time_rows: list[list[object]] = []
    for left in range(0, horizon, 100):
        right = min(left + 100, horizon)
        block = occupancy[left:right, :]
        time_rows.append(
            [
                left,
                right,
                int(block.sum()),
                float((block > 0).mean()),
                *[int(by_category[category][left:right, :].sum()) for category in "ABC"],
            ]
        )
    write_csv(
        output_dir / "time_windows.csv",
        ["时间左端点", "时间右端点", "计划单元占用量", "资源单元占用率", "A类占用量", "B类占用量", "C类占用量"],
        time_rows,
    )

    phase_rows = []
    for phase in range(C_START_STEP):
        mask = np.arange(feasible.shape[0]) % C_START_STEP == phase
        total = int(mask.sum() * feasible.shape[1])
        count = int(feasible[mask, :].sum())
        phase_rows.append([phase, count, total, count / total])
    write_csv(
        output_dir / "raw_c_candidate_by_phase.csv",
        [f"首次时刻模{C_START_STEP}", "可行起点数", "候选起点数", "可行率"],
        phase_rows,
    )

    candidate_frequency_rows = []
    for left in range(0, feasible.shape[1], 10):
        right = min(left + 10, feasible.shape[1])
        block = feasible[:, left:right]
        candidate_frequency_rows.append(
            [left, right, int(block.sum()), int(block.size), float(block.mean())]
        )
    write_csv(
        output_dir / "raw_c_candidate_by_frequency.csv",
        ["频率起点左端点", "频率起点右端点", "可行起点数", "候选起点数", "可行率"],
        candidate_frequency_rows,
    )

    plot_frequency_distribution(plans, by_category, output_dir)
    plot_time_distribution(plans, occupancy, output_dir)
    plot_occupancy_heatmap(occupancy, output_dir)
    plot_candidate_map(feasible, output_dir)
    return summary


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--input",
        type=Path,
        default=Path("data/raw/D题/附件/附件1.xlsx"),
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("work/intake/distribution"),
    )
    args = parser.parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)
    configure_matplotlib()
    plans = read_plans(args.input)
    validate_recurrence_examples(plans)
    summary = analyze(plans, args.output_dir)
    (args.output_dir / "summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(
        json.dumps(
            {
                "status": "PASS",
                "output_dir": str(args.output_dir),
                "plan_count": summary["input_plan_count"],
                "raw_c_candidate_feasible_rate": summary["raw_c_candidate_demo"][
                    "individually_feasible_rate"
                ],
            },
            ensure_ascii=False,
        )
    )


if __name__ == "__main__":
    main()
