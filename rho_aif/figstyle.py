"""Shared figure style for every figure in the paper.

One aesthetic, applied by every figure producer. The rules this module
enforces came out of a figure audit before JAIR submission:

- One agent, one color, everywhere. A reader who learns that EFE is
  vermillion in Figure 1 can rely on that in Figure 12. The mapping uses the
  Okabe-Ito colorblind-safe palette.
- Serif text and mathtext, matching the manuscript's Libertine body face
  closely enough that figures do not look pasted in from another document.
- No in-figure suptitles duplicating the caption. Panel labels (a), (b) stay.
- Top and right spines off, light y-grid only, frameless legends.
- No overlapping labels. Point annotations that would collide are offset and
  connected with a thin leader arrow instead.
- Vector PDF is the artifact of record; the PNG twin exists for quick review.
"""

from __future__ import annotations

import matplotlib as mpl
import matplotlib.pyplot as plt

# Okabe-Ito palette.
BLUE = "#0072B2"
VERMILLION = "#D55E00"
GREEN = "#009E73"
ORANGE = "#E69F00"
SKY = "#56B4E9"
PINK = "#CC79A7"
YELLOW = "#F0E442"
GRAY = "#7F7F7F"
BLACK = "#000000"

# The canonical agent-to-color mapping. Every producer draws agents in these
# colors, so the mapping is the legend a reader carries between figures.
AGENT_COLORS = {
    "EFE": VERMILLION,
    "Planning": BLUE,
    "Planning+IG": PINK,
    "InfoGain": ORANGE,
    "InfoGain-Tuned": ORANGE,
    "Myopic": GRAY,
    "Greedy": GRAY,
    "POMCP": GREEN,
    "MCTS-EFE": SKY,
    "Thompson": YELLOW,
    "SARSOP": BLACK,
    "IDS": SKY,
}

# Line styles distinguish agents sharing a color family when they co-occur.
AGENT_LINESTYLES = {
    "Myopic": "--",
    "Greedy": "--",
    "InfoGain-Tuned": "-.",
    "Planning+IG": ":",
}

AGENT_MARKERS = {
    "EFE": "o",
    "Planning": "^",
    "Planning+IG": "v",
    "InfoGain": "D",
    "InfoGain-Tuned": "D",
    "Myopic": "s",
    "Greedy": "s",
    "POMCP": "P",
    "MCTS-EFE": "X",
    "Thompson": "*",
    "SARSOP": "h",
    "IDS": "X",
}

# Environments, for figures whose series are environments rather than agents.
# ENV_COLORS is the stable name-keyed mapping ("one environment, one color,
# everywhere"); ENV_CYCLE is the documented fallback for unlisted names.
ENV_COLORS = {
    "Tiger": BLUE,
    "Diagnosis": ORANGE,
    "Bandit": GREEN,
    "Testbed": YELLOW,
    "Tileworld-6x6": VERMILLION,
    "Tileworld-8x8": VERMILLION,
    "Inspection-N8": PINK,
    "Inspection-N16": SKY,
    "RS[5,3]": GRAY,
    "RS[7,4]": BLACK,
    "Navigation": SKY,
}
ENV_CYCLE = [BLUE, ORANGE, GREEN, VERMILLION, PINK, SKY, GRAY, YELLOW]

# Shared error-bar cap size so uncertainty renders identically across figures.
CAPSIZE = 2

# Belief colormap shared by every belief-probability heatmap (light ground,
# low ink, matches the light-ground line-figure aesthetic).
BELIEF_CMAP = "YlOrRd"

# JAIR text block is ~6.5in wide; LNCS ~4.8in. Figures must be authored at
# the width they are printed at so rcParams point sizes are the printed sizes.
TEXT_WIDTH_IN = 6.5


def env_color(name: str) -> str:
    """Stable color for an environment name, with a deterministic fallback."""
    if name in ENV_COLORS:
        return ENV_COLORS[name]
    # str.__hash__ is salted per process, so use a content hash.
    return ENV_CYCLE[sum(name.encode()) % len(ENV_CYCLE)]


def figsize(width_frac: float = 1.0, aspect: float = 0.45) -> tuple:
    """Figure size in inches for a figure printed at width_frac of the JAIR
    text block. Authoring at the printed width keeps type at rcParams size."""
    w = TEXT_WIDTH_IN * width_frac
    return (w, w * aspect)


def agent_color(label: str) -> str:
    """Color for an agent label, matching on the longest known prefix."""
    best = None
    for key in AGENT_COLORS:
        if label.startswith(key) and (best is None or len(key) > len(best)):
            best = key
    return AGENT_COLORS.get(best, BLACK)


def agent_style(label: str) -> dict:
    """Full kwargs (color, linestyle, marker) for an agent series."""
    best = None
    for key in AGENT_COLORS:
        if label.startswith(key) and (best is None or len(key) > len(best)):
            best = key
    return {
        "color": AGENT_COLORS.get(best, BLACK),
        "linestyle": AGENT_LINESTYLES.get(best, "-"),
        "marker": AGENT_MARKERS.get(best, "o"),
    }


def apply() -> None:
    """Install the shared rcParams. Call once, before any figure is created."""
    mpl.rcParams.update({
        "font.family": "serif",
        "font.serif": ["Linux Libertine O", "Libertinus Serif", "STIXGeneral",
                       "DejaVu Serif"],
        "mathtext.fontset": "stix",
        "font.size": 9.5,
        "axes.titlesize": 10,
        "axes.labelsize": 9.5,
        "xtick.labelsize": 8.5,
        "ytick.labelsize": 8.5,
        "legend.fontsize": 8.5,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.grid": True,
        "axes.grid.axis": "y",
        "grid.alpha": 0.25,
        "grid.linewidth": 0.6,
        "axes.axisbelow": True,
        "lines.linewidth": 1.8,
        "lines.markersize": 5,
        "legend.frameon": False,
        "figure.dpi": 150,
        "savefig.bbox": "tight",
        "savefig.dpi": 300,
        "pdf.fonttype": 42,
    })


def style_axis(ax, xgrid: bool = False) -> None:
    """Per-axis touches beyond rcParams."""
    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    if xgrid:
        ax.grid(True, axis="x", alpha=0.25, linewidth=0.6)


def annotate_no_overlap(ax, points, fmt="{}", color=GRAY, fontsize=7.5,
                        min_sep_frac=0.045):
    """Annotate (x, y, label) points, offsetting colliding labels with a thin
    leader arrow so every label displays cleanly.

    ``points`` is an iterable of (x, y, label, side) where side is +1 to place
    the label to the right and -1 to the left. Labels closer than
    ``min_sep_frac`` of the axis span to an already-placed label are pushed
    outward along y and connected to their point by a leader line.
    """
    placed = []
    x0, x1 = ax.get_xlim()
    y0, y1 = ax.get_ylim()
    xspan, yspan = (x1 - x0) or 1.0, (y1 - y0) or 1.0
    for x, y, label, side in points:
        tx, ty = x + side * 0.02 * xspan, y
        bumps = 0
        while any(abs(tx - px) < min_sep_frac * xspan
                  and abs(ty - py) < min_sep_frac * yspan
                  for px, py in placed) and bumps < 12:
            ty += min_sep_frac * yspan * (1 if bumps % 2 == 0 else -(bumps + 1))
            bumps += 1
        placed.append((tx, ty))
        needs_leader = abs(ty - y) > 0.02 * yspan or bumps > 0
        if needs_leader:
            ax.annotate(fmt.format(label), xy=(x, y), xytext=(tx, ty),
                        fontsize=fontsize, color=color,
                        ha="left" if side > 0 else "right", va="center",
                        arrowprops=dict(arrowstyle="-", lw=0.5, color=color,
                                        shrinkA=1, shrinkB=2))
        else:
            ax.annotate(fmt.format(label), xy=(x, y), xytext=(tx, ty),
                        fontsize=fontsize, color=color,
                        ha="left" if side > 0 else "right", va="center")
