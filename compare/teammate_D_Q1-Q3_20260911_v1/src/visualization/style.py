"""Shared plotting style for competition paper figures.

The palette is a muted, accessibility-aware scientific theme derived from the
reviewed reference packs and public figure guidance. It is a repository
convention, not a journal-branded template. Keep semantic roles stable across
questions and use shape, position, or direct labels when color alone would be
ambiguous.
"""

from __future__ import annotations

import matplotlib as mpl
from matplotlib import font_manager, ft2font
from cycler import cycler

PALETTE = {
    # Strong semantic accents.
    "primary": "#3B6686",
    "secondary": "#8195A3",
    "positive": "#2A8278",
    "warning": "#B95C50",
    "accent": "#C17B3A",
    # Q2 state roles; these remain stable across figures.
    "keep": "#9AABB5",
    "adjust": "#2A8278",
    "revoke": "#B95C50",
    "probe": "#C17B3A",
    # Neutral and support tokens.
    "ink": "#263238",
    "muted": "#697780",
    "grid": "#D9E1E5",
    "pale_primary": "#EDF3F6",
    "pale_teal": "#EAF4F1",
    "pale_accent": "#F7F0E8",
    "pale_warning": "#F8ECEA",
    # Backward-compatible semantic aliases used by existing renderers.
    "main": "#3B6686",
    "baseline": "#8195A3",
    "reference": "#C17B3A",
}

FONT_VARIANTS = {
    # Default: a clean, modern Chinese sans-serif with generous counters at
    # the final 155 mm paper width.
    "modern": ("Noto Sans SC", "Microsoft YaHei", "SimHei"),
    # Alternative: a restrained Chinese serif suitable for a more traditional
    # printed-paper appearance.  It is a presentation option only; it never
    # changes scientific inputs or plotted values.
    "print": ("STSong", "SimSun", "Noto Sans SC"),
}
LATIN_FALLBACKS = {
    "modern": ("Arial", "DejaVu Sans"),
    "print": ("Times New Roman", "DejaVu Serif"),
}
ROLE_STYLES = {
    "main": {"color": PALETTE["main"], "linestyle": "-", "marker": "o"},
    "baseline": {"color": PALETTE["baseline"], "linestyle": "--", "marker": "s"},
    "reference": {"color": PALETTE["reference"], "linestyle": ":", "marker": "^"},
    "warning": {"color": PALETTE["warning"], "linestyle": "-.", "marker": "x"},
}


def select_chinese_font(text="中文图表结果负号−±×αβ", variant="modern"):
    """Resolve an installed font and verify its glyphs; never silently use DejaVu."""
    required = {ord(c) for c in text if not c.isspace()}
    candidates = FONT_VARIANTS.get(variant)
    if candidates is None:
        raise ValueError(f"Unknown figure style variant: {variant}")
    for family in candidates:
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


def apply_competition_style(width_mm=155, height_mm=90, variant="modern") -> None:
    """Apply the repository's publication style with a presentation variant."""
    family, _ = select_chinese_font(variant=variant)
    latin = LATIN_FALLBACKS[variant]
    mathtext = "dejavusans" if variant == "modern" else "stix"
    base_size = 9.2 if variant == "modern" else 9.0
    mpl.rcParams.update(
        {
            "font.family": [family, *latin],
            "font.size": base_size,
            "mathtext.fontset": mathtext,
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
            "axes.labelsize": 8.8,
            "xtick.labelsize": 8.0,
            "ytick.labelsize": 8.0,
            "legend.fontsize": 7.8,
            "legend.frameon": False,
            "lines.linewidth": 1.35,
            "lines.markersize": 4.5,
            "axes.linewidth": 0.8,
            "axes.edgecolor": PALETTE["muted"],
            "axes.labelcolor": PALETTE["ink"],
            "xtick.color": PALETTE["muted"],
            "ytick.color": PALETTE["muted"],
            "text.color": PALETTE["ink"],
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
            # Keep text as text in SVG; PDF embeds TrueType for paper delivery.
            "svg.fonttype": "none",
            "savefig.facecolor": "white",
            "figure.facecolor": "white",
        }
    )
