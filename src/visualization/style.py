"""Shared plotting style for competition paper figures.

This module defines a restrained default. Official paper-template constraints,
if any, remain authoritative and may require later adjustment.
"""

from __future__ import annotations

import matplotlib as mpl

PALETTE = {
    "primary": "#4C78A8",
    "secondary": "#7A7A7A",
    "positive": "#54A24B",
    "warning": "#E45756",
    "accent": "#F58518",
    "grid": "#D9D9D9",
}


def apply_competition_style() -> None:
    """Apply the repository's default publication style to Matplotlib."""
    mpl.rcParams.update(
        {
            "figure.dpi": 140,
            "savefig.dpi": 300,
            "savefig.bbox": "tight",
            "axes.spines.top": False,
            "axes.spines.right": False,
            "axes.grid": False,
            "axes.titleweight": "normal",
            "axes.labelsize": 9,
            "xtick.labelsize": 8,
            "ytick.labelsize": 8,
            "legend.fontsize": 8,
            "legend.frameon": False,
            "lines.linewidth": 1.4,
            "lines.markersize": 4.5,
            "pdf.fonttype": 42,
            "ps.fonttype": 42,
        }
    )
