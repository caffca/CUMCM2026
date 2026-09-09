"""Shared plotting style for competition paper figures.

This module defines a restrained default. Official paper-template constraints,
if any, remain authoritative and may require later adjustment.
"""

from __future__ import annotations

import matplotlib as mpl
from matplotlib import font_manager, ft2font
from cycler import cycler

PALETTE = {
    "primary": "#4C78A8",
    "secondary": "#7A7A7A",
    "positive": "#54A24B",
    "warning": "#E45756",
    "accent": "#F58518",
    "grid": "#D9D9D9",
    "main": "#4C78A8",
    "baseline": "#7A7A7A",
    "reference": "#F58518",
}

FONT_CANDIDATES = ("Noto Sans SC", "Microsoft YaHei", "SimHei", "SimSun")
ROLE_STYLES = {
    "main": {"color": PALETTE["main"], "linestyle": "-", "marker": "o"},
    "baseline": {"color": PALETTE["baseline"], "linestyle": "--", "marker": "s"},
    "reference": {"color": PALETTE["reference"], "linestyle": ":", "marker": "^"},
    "warning": {"color": PALETTE["warning"], "linestyle": "-.", "marker": "x"},
}


def select_chinese_font(text="中文图表结果负号−±×αβ"):
    """Resolve an installed font and verify its glyphs; never silently use DejaVu."""
    required = {ord(c) for c in text if not c.isspace()}
    for family in FONT_CANDIDATES:
        try:
            path = font_manager.findfont(family, fallback_to_default=False)
            covered = ft2font.FT2Font(path).get_charmap()
            if required <= covered.keys():
                return family, path
        except (ValueError, OSError, RuntimeError):
            continue
    raise ValueError("BLOCKED: no configured Chinese font covers the requested glyphs; "
                     "inspect installed fonts/labels. Do not translate labels to hide this error.")


def figure_size(width_mm=155, height_mm=90):
    if not 40 <= width_mm <= 210 or not 25 <= height_mm <= 280:
        raise ValueError("Figure dimensions must be explicit paper-size millimetres")
    return width_mm / 25.4, height_mm / 25.4


def apply_competition_style(width_mm=155, height_mm=90) -> None:
    """Apply the repository's default publication style to Matplotlib."""
    family, _ = select_chinese_font()
    mpl.rcParams.update(
        {
            "font.family": [family, "DejaVu Sans"],
            "font.size": 10,
            "mathtext.fontset": "dejavusans",
            "axes.unicode_minus": True,
            "axes.prop_cycle": cycler(color=[PALETTE[r] for r in ROLE_STYLES]),
            "figure.figsize": figure_size(width_mm, height_mm),
            "figure.dpi": 140,
            "savefig.dpi": 300,
            "savefig.bbox": None,
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.grid": False,
            "axes.titleweight": "normal",
            "axes.labelsize": 9,
            "xtick.labelsize": 9,
            "ytick.labelsize": 9,
            "legend.fontsize": 9,
            "legend.frameon": False,
            "lines.linewidth": 1.4,
            "lines.markersize": 4.5,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
        }
    )
