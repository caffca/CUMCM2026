"""Render supplied plot-ready JSON without fitting, inference, or aggregation.

See tests/figures/ for SYNTHETIC TEST examples. Run with explicit source identity.
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from src.visualization.style import apply_competition_style, ROLE_STYLES, PALETTE
from src.visualization.export import read_frozen, check_brief, check_plot_data, check_comparisons, export_figure


def render(source_path, identity, brief_path, output_dir, base_sha):
    data, actual = read_frozen(source_path, identity)
    brief = json.loads(Path(brief_path).read_text(encoding="utf-8"))
    source = data[brief["figure_id"]]
    if Path(brief["source"]).resolve() != Path(source_path).resolve():
        raise ValueError("BLOCKED: brief source does not match supplied frozen path")
    if len(base_sha) != 40 or any(c not in "0123456789abcdef" for c in base_sha):
        raise ValueError("BLOCKED: base_sha must be a full resolved commit SHA")
    check_brief(source, brief)
    check_plot_data(source, brief)
    output_dir = Path(output_dir).resolve()
    if output_dir == Path(source_path).resolve().parent:
        raise ValueError("BLOCKED: output directory must be separate from frozen inputs")
    figure_id = brief["figure_id"]
    if Path(figure_id).name != figure_id or "/" in figure_id or "\\" in figure_id:
        raise ValueError("BLOCKED: figure_id must be a filename stem")
    width = brief["final_width_mm"]
    apply_competition_style(width_mm=width, height_mm=90)
    fig, ax = plt.subplots(layout="constrained")
    kind = source["kind"]
    checks = []
    plotted = set()
    try:
        if kind == "comparison":
            for i, item in enumerate(source["values"]):
                value, lo, hi = item["value"], item["lower"], item["upper"]
                if not lo <= value <= hi:
                    raise ValueError("BLOCKED: supplied interval does not contain value")
                style = ROLE_STYLES[item["role"]]
                artist = ax.errorbar(value, i, xerr=[[value-lo], [hi-value]],
                                    color=style["color"], marker=style["marker"],
                                    linestyle="none", capsize=4)
                np.testing.assert_array_equal(artist.lines[0].get_xdata(), [value])
                plotted.add("series:" + item["role"])
                np.testing.assert_allclose(artist.lines[2][0].get_segments(), [[[lo, i], [hi, i]]])
                if not min(source["x_limits"]) <= lo <= hi <= max(source["x_limits"]):
                    raise ValueError("BLOCKED: supplied axis would hide an interval")
            ax.set_yticks(range(len(source["values"])), [v["label"] for v in source["values"]])
            ax.set_xlabel(source["x_label"])
            ax.set_xlim(source["x_limits"])
            checks.append("point and interval artists equal supplied values; intervals visible within supplied axis")
        elif kind == "sensitivity":
            for series in source["series"]:
                line, = ax.plot(source["x"], series["y"], label=series["label"], **ROLE_STYLES[series["role"]])
                np.testing.assert_array_equal(line.get_ydata(), series["y"])
                np.testing.assert_array_equal(line.get_xdata(), source["x"])
                plotted.add("series:" + series["role"])
            ax.set(xlabel=source["x_label"], ylabel=source["y_label"])
            ax.legend()
            checks.append("line artists equal supplied decisions; no optimum assertion")
        elif kind == "prediction":
            fig.clear()
            ax, residual = fig.subplots(1, 2)
            observed, predicted = np.array(source["observed"]), np.array(source["predicted"])
            np.testing.assert_allclose(predicted-observed, source["residual"])
            pts = ax.scatter(observed, predicted, color=PALETTE["main"], s=20)
            np.testing.assert_array_equal(pts.get_offsets(), np.column_stack([observed, predicted]))
            limits = source["limits"]
            if not np.all((np.r_[observed, predicted] >= min(limits)) & (np.r_[observed, predicted] <= max(limits))):
                raise ValueError("BLOCKED: supplied axis would hide observations/predictions")
            ax.plot(limits, limits, color=PALETTE["baseline"], linestyle="--", label="一致线")
            ax.set(xlabel=source["observed_label"], ylabel=source["predicted_label"], xlim=limits, ylim=limits)
            ax.legend()
            residual_pts = residual.scatter(observed, source["residual"], color=PALETTE["main"], s=20)
            np.testing.assert_array_equal(residual_pts.get_offsets(), np.column_stack([observed, source["residual"]]))
            residual.axhline(0, color=PALETTE["baseline"], linestyle="--")
            residual.set(xlabel=source["observed_label"], ylabel=source["residual_label"])
            plotted.update(("series:main", "reference:identity", "reference:zero"))
            checks.append("points equal input; supplied residuals checked against prediction-observation")
        elif kind == "framework":
            ax.set(xlim=(0, 1), ylim=(0, 1))
            ax.axis("off")
            nodes = {n["id"]: n for n in source["nodes"]}
            for n in nodes.values():
                ax.text(*n["position"], n["label"], ha="center", va="center", fontsize=10,
                        bbox={"boxstyle":"round,pad=0.65", "fc":"white", "ec":PALETTE["main"]})
            for edge in source["edges"]:
                start, end = nodes[edge["from"]]["position"], nodes[edge["to"]]["position"]
                ax.annotate("", xy=end, xytext=start, arrowprops={"arrowstyle":"->", "shrinkA":35,"shrinkB":35,"color":PALETTE["baseline"]})
                ax.text((start[0]+end[0])/2, (start[1]+end[1])/2 + .035, edge["label"], ha="center", fontsize=9)
            checks.append("explicit node and dependency mapping; schematic, not numerical evidence")
        else:
            raise ValueError(f"BLOCKED: unsupported plot kind: {kind}")
        if data.get("synthetic"):
            fig.suptitle("SYNTHETIC TEST · 合成表达示例", fontsize=10)
        check_comparisons(brief["required_comparison"], plotted)
        result = export_figure(fig, output_dir / figure_id, width)
    except Exception:
        plt.close(fig)
        raise
    caption = (brief["purpose"] + "。口径：" + brief["unit_and_population"] +
               "；聚合：" + brief["aggregation"] + "；区间：" + brief["uncertainty"] +
               "。" + brief["supported_claim"] + "。边界：" + brief["forbidden_inference"] + "。")
    if brief.get("missing_data_policy") == "gap":
        caption += "缺测处理：保留断线，不填补/插值；" + brief["missing_data_note"] + "。"
    result.update(base_sha=base_sha, source=str(Path(source_path).resolve()), source_sha256=actual,
                  caption=caption, checks=checks, comparison_objects=sorted(plotted),
                  claim_status="BUILDER_TEXT_MATCH_ONLY_NOT_SCIENTIFIC_PROOF",
                  missing_data_policy=brief.get("missing_data_policy", "reject"),
                  synthetic=bool(data.get("synthetic")))
    (output_dir / (figure_id + ".note.json")).write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    for name in ("source", "sha256", "brief", "output-dir", "base-sha"):
        parser.add_argument("--" + name, required=True)
    args = parser.parse_args()
    try:
        result = render(args.source, args.sha256, args.brief, args.output_dir, args.base_sha)
    except (ValueError, KeyError, OSError, AssertionError) as exc:
        parser.exit(2, str(exc) + "\n")
    print(json.dumps(result, ensure_ascii=False))


if __name__ == "__main__":
    main()
