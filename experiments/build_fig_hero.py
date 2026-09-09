#!/usr/bin/env python3
"""
Hero figure (graphical abstract) for the Introduction.

Schematic, not data-bearing: no episodes are run and no CSV is read or
written. Every other figure in this paper reports a measured result: this
one instead gives a first-time reader, in one picture, the two claims the
rest of the paper backs with data.

(1) The information weight is a price. A usage curve U(w) relates the
    info-gain weight w to how much sensing an agent spends, and a stated
    sensing budget B picks out the bracket of weights (w_lo, w_hi] whose
    usage meets B, the budget's operational shadow price w*(B)
    (Definition PI-3). This is the dominant visual, matching the paper's
    own framing of the budgeted reformulation as its primary contribution.

(2) Active inference's canonical w=1 is one point on that same curve, not
    a second free hyperparameter. Minimizing Expected Free Energy is
    exactly equivalent to solving the same weighted objective at w=1
    (Proposition 1), so w=1 is drawn as a star sitting on the curve,
    deliberately outside the drawn bracket so the figure never implies a
    coincidence between EFE's weight and this particular budget's price.

The staircase, budget, and bracket reuse the exact axhline/axvspan
conventions of plot_cost_budget (run_price_of_information.py), and the
vermillion five-point star reuses the exact EFE-agent marker convention of
run_pareto.py's Pareto panels, so this figure introduces no new visual
vocabulary relative to the rest of the paper.
"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

from rho_aif import figstyle


def _rainbow_text(ax, fig, x, y, fragments, fontsize=7.5, va="bottom",
                   right_limit=None, line_name=""):
    """Draw left-to-right text fragments [(text, color), ...] starting at
    (x, y) in axes-fraction coordinates, each fragment colored separately.

    Matplotlib cannot color a substring within one mathtext string, so each
    fragment is its own Text artist, placed by measuring the previous
    fragment's actual rendered width (the standard "rainbow text" recipe)
    rather than by guessing pixel offsets. If right_limit is given, raise
    rather than silently ship a line that overflows it: a first version of
    this figure placed an unmeasured line into a too-narrow box and the
    text ran out past the box's own border into the plot next to it.
    """
    renderer = fig.canvas.get_renderer()
    for text, color in fragments:
        t = ax.text(x, y, text, color=color, fontsize=fontsize, va=va,
                    ha="left", transform=ax.transAxes, zorder=7)
        fig.canvas.draw()
        bbox_axes = t.get_window_extent(renderer=renderer).transformed(
            ax.transAxes.inverted())
        x = bbox_axes.x1
    if right_limit is not None and x > right_limit:
        raise RuntimeError(
            f"hero figure callout line {line_name!r} overflows its box: "
            f"ends at axes-fraction x={x:.4f}, limit is {right_limit:.4f}")


def plot_hero(path: str = "figures/fig_hero_price_curve.pdf") -> None:
    figstyle.apply()
    fig, ax = plt.subplots(figsize=figstyle.figsize(1.0, aspect=0.62))

    # Schematic usage curve: flat, one clean rise, flat. Illustrative only,
    # not measured data, and not a claim that real usage curves are always
    # monotone (several in this paper plateau, jump, or dip). The rise
    # starts at w=4 rather than w=3 specifically to leave visible breathing
    # room between the shaded bracket band and the callout box beside it
    # (Pat flagged the two as reading too close together at w=3).
    w = [0.1, 0.3, 1, 4, 10, 30, 100]
    u = [3, 3, 3, 3, 10, 10, 10]
    ax.plot(w, u, color=figstyle.BLUE, marker="o", ms=5, lw=1.8,
             zorder=3, label="$U(w)$: schematic usage curve")
    ax.set_xscale("log")
    ax.set_xlim(0.08, 140)
    ax.set_ylim(0, 13)

    # Stated sensing budget B.
    ax.axhline(6.5, color=figstyle.GRAY, ls="--", lw=1.2, zorder=2,
               label="stated sensing budget $B$")

    # Shadow-price bracket (w_lo, w_hi], half-open and closed at w_hi per
    # Definition PI-3: the shaded fill is solid flush to both edges, with no
    # open-circle or dashed-edge cue at either boundary that would read as
    # excluded (the exact ambiguity a prior figure in this paper had to be
    # corrected for).
    w_lo, w_hi = 4, 10
    ax.axvspan(w_lo, w_hi, color=figstyle.GRAY, alpha=0.15, zorder=0,
               label=r"shadow price $w^*(B)=(w_{\mathrm{lo}}, w_{\mathrm{hi}}]$")
    # Labeled near the top of the band, not the bottom: the bottom-right of
    # the panel is where the legend sits, and a first pass collided the two.
    ax.text(w_lo, 12.5, r"$w_{\mathrm{lo}}$", fontsize=7.5,
            color=figstyle.GRAY, ha="center", va="top")
    ax.text(w_hi, 12.5, r"$w_{\mathrm{hi}}$", fontsize=7.5,
            color=figstyle.GRAY, ha="center", va="top")

    # EFE's canonical w=1, on the curve's low plateau, deliberately outside
    # the drawn bracket.
    ax.plot([1], [3], marker="*", ms=16,
            markerfacecolor=figstyle.AGENT_COLORS["EFE"],
            markeredgecolor="black", markeredgewidth=0.7, linestyle="none",
            zorder=5, label="$w{=}1$ (EFE)")

    ax.set_xlabel("Information weight $w$ (log scale)")
    ax.set_ylabel("$U(w)$: expected sensing usage per episode\n(schematic units)")
    figstyle.style_axis(ax)
    ax.legend(loc="lower right", fontsize=7.8, handlelength=1.6)

    # Leader line from the star up to the box's bottom-left corner (short,
    # and never crosses the box's own text). No text yet: matplotlib's
    # annotate bbox cannot mix colors within one string, so the box and its
    # two-color text are drawn separately below.
    # Right edge kept well left of w_lo=4 (axes-fraction ~0.524 on this log
    # axis, measured, not guessed), with a real visible gap rather than a
    # bare-minimum one: an earlier version's right edge sat only ~0.025
    # axes-fraction from the band's left edge and read as visually crowded
    # (Pat flagged it directly). Narrowed here and paired with the smaller
    # callout fontsize below, both measured against the box interior.
    box_xy = (0.04, 0.53)
    box_wh = (0.40, 0.42)
    box_right = box_xy[0] + box_wh[0]
    ax.annotate("", xy=(1, 3), xycoords="data",
                xytext=(box_xy[0] + 0.03, box_xy[1] + 0.03),
                textcoords="axes fraction",
                arrowprops=dict(arrowstyle="-", lw=0.6,
                                color=figstyle.AGENT_COLORS["EFE"],
                                shrinkA=2, shrinkB=4))

    ax.add_patch(FancyBboxPatch(
        box_xy, box_wh[0], box_wh[1], transform=ax.transAxes,
        boxstyle="round,pad=0.012", facecolor="#F7F6F2",
        edgecolor="0.75", linewidth=0.6, zorder=6))

    pad_x, top_y = box_xy[0] + 0.02, box_xy[1] + box_wh[1] - 0.07
    line_h = 0.10
    fs = 6.6
    _rainbow_text(ax, fig, pad_x, top_y, [
        ("Active inference minimizes", "0.15"),
    ], fontsize=fs, right_limit=box_right - 0.01, line_name="line 1")
    _rainbow_text(ax, fig, pad_x, top_y - line_h, [
        ("$G(\\pi){=}$ pragmatic $+$ epistemic", "0.15"),
    ], fontsize=fs, right_limit=box_right - 0.01, line_name="line 2")
    _rainbow_text(ax, fig, pad_x, top_y - 2 * line_h, [
        ("is exactly maximizing $R(s,a){+}w{\\cdot}I(b,a)$ at ", "0.15"),
        ("$w{=}1$", figstyle.AGENT_COLORS["EFE"]),
    ], fontsize=fs, right_limit=box_right - 0.01, line_name="line 3")
    _rainbow_text(ax, fig, pad_x, top_y - 3 * line_h, [
        ("(Prop. 1, exact under log scoring)", "0.15"),
    ], fontsize=fs, right_limit=box_right - 0.01, line_name="line 4")

    fig.savefig(path)
    fig.savefig(path.replace(".pdf", ".png"))
    print(f"Saved {path} and its .png twin")


if __name__ == "__main__":
    plot_hero()
