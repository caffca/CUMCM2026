"""Small frozen-input and export checks, not an experiment registry."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
import warnings

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.text import Text

from .style import select_chinese_font


def read_frozen(path, expected_sha256):
    path = Path(path)
    if not path.is_file():
        raise ValueError(f"BLOCKED: frozen input missing: {path}")
    raw = path.read_bytes()
    actual = hashlib.sha256(raw).hexdigest()
    if actual != expected_sha256:
        raise ValueError(f"STALE: frozen input identity differs: {path}")
    return json.loads(raw), actual


def check_brief(source, brief):
    for field in ("figure_id", "question", "purpose", "supported_claim", "source",
                  "unit_and_population", "uncertainty", "aggregation",
                  "required_comparison", "final_width_mm", "language", "forbidden_inference"):
        if field not in brief or brief[field] in ("", None):
            raise ValueError(f"BLOCKED: missing brief field {field}")
    for key in ("unit_and_population", "uncertainty", "aggregation"):
        if source[key] != brief[key]:
            raise ValueError(f"BLOCKED: {key} mismatch between source and brief")
    if brief["supported_claim"] not in source["supported_claims"]:
        raise ValueError("BLOCKED: unsupported claim; return to Builder for interpretation")
    if brief["language"] != "zh-CN":
        raise ValueError("This publication example requires zh-CN labels")


def check_comparisons(required, present):
    """Match explicit object IDs, not natural-language claims about their existence."""
    if required == "none":
        return
    if not isinstance(required, list) or not required or not all(isinstance(x, str) for x in required):
        raise ValueError("BLOCKED: required_comparison needs object IDs (e.g. ['series:baseline']) or 'none'")
    missing = set(required) - set(present)
    if missing:
        raise ValueError(f"BLOCKED: required comparison objects missing: {sorted(missing)}")


def check_plot_data(source, brief):
    """Validate shape and finite values before Matplotlib can silently mask them.

    Only sensitivity y-series allow declared NaN/null gaps; never impute or interpolate.
    Claim membership elsewhere checks approved wording, not scientific truth.
    """
    policy = brief.get("missing_data_policy", "reject")
    if policy not in ("reject", "gap") or policy != source.get("missing_data_policy", "reject"):
        raise ValueError("BLOCKED: missing-data policy must agree with frozen source")
    if policy == "gap" and (source["kind"] != "sensitivity" or not brief.get("missing_data_note")):
        raise ValueError("BLOCKED: only sensitivity y gaps are supported; declare reason in brief")

    def vector(value, name, length=None, gaps=False):
        try:
            array = np.asarray(value, dtype=float)
        except (ValueError, TypeError) as exc:
            raise ValueError(f"BLOCKED: nonnumeric/ragged {name}") from exc
        if array.ndim != 1 or not array.size or (length is not None and len(array) != length):
            raise ValueError(f"BLOCKED: invalid shape for {name}")
        if np.isinf(array).any() or (not gaps and not np.isfinite(array).all()) or not np.isfinite(array).any():
            raise ValueError(f"BLOCKED: nonfinite or entirely missing {name}")
        return array

    kind = source["kind"]
    if kind == "comparison":
        vector([v["value"] for v in source["values"]], "comparison.value")
        vector([v["lower"] for v in source["values"]], "comparison.lower")
        vector([v["upper"] for v in source["values"]], "comparison.upper")
        vector(source["x_limits"], "x_limits", 2)
        present = {"series:"+v["role"] for v in source["values"]}
    elif kind == "sensitivity":
        x = vector(source["x"], "x")
        if not source["series"]:
            raise ValueError("BLOCKED: no series")
        for s in source["series"]:
            vector(s["y"], s["role"]+".y", len(x), policy == "gap")
        present = {"series:"+s["role"] for s in source["series"]}
    elif kind == "prediction":
        observed = vector(source["observed"], "observed")
        vector(source["predicted"], "predicted", len(observed))
        vector(source["residual"], "residual", len(observed))
        vector(source["limits"], "limits", 2)
        present = {"series:main", "reference:identity", "reference:zero"}
    else:
        present = set()
    check_comparisons(brief["required_comparison"], present)


def export_figure(fig, stem, width_mm):
    """Fixed page size; fail on missing glyphs or text outside the figure, close always."""
    stem = Path(stem)
    try:
        if abs(fig.get_figwidth() * 25.4 - width_mm) > 0.01:
            raise ValueError("BLOCKED: final width mismatch")
        labels = [t.get_text() for t in fig.findobj(Text) if t.get_visible()]
        family, font_path = select_chinese_font("".join(labels))
        with warnings.catch_warnings():
            warnings.filterwarnings("error", message="Glyph .* missing from font")
            fig.canvas.draw()
            renderer = fig.canvas.get_renderer()
            # Locators also create tick labels outside the view interval. They are
            # retained artists but Axis.draw does not paint those labels.
            not_drawn = set()
            for ax in fig.axes:
                for axis in (ax.xaxis, ax.yaxis):
                    lo, hi = sorted(axis.get_view_interval())
                    for tick in axis.get_major_ticks() + axis.get_minor_ticks():
                        if not lo <= tick.get_loc() <= hi:
                            not_drawn.update((id(tick.label1), id(tick.label2)))
            for t in fig.findobj(Text):
                if not t.get_visible() or not t.get_text() or id(t) in not_drawn:
                    continue
                box = t.get_window_extent(renderer)
                if box.x0 < -1 or box.y0 < -1 or box.x1 > fig.bbox.x1 + 1 or box.y1 > fig.bbox.y1 + 1:
                    raise ValueError(f"BLOCKED: text outside final canvas: {t.get_text()}")
            stem.parent.mkdir(parents=True, exist_ok=True)
            fig.savefig(stem.with_suffix(".pdf"), bbox_inches=None)
            fig.savefig(stem.with_suffix(".png"), dpi=200, bbox_inches=None)
        return {"font_family": family, "font_path": font_path,
                "width_mm": width_mm, "height_mm": fig.get_figheight() * 25.4,
                "visual_status": "NOT_VISUALLY_VERIFIED"}
    finally:
        plt.close(fig)
