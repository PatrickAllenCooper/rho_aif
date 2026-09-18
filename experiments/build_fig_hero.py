#!/usr/bin/env python3
"""
Hero figure (graphical abstract) for the Introduction.

Schematic, not data-bearing: no episodes are run and no CSV is read or
written. Every other figure in this paper reports a measured result: this
one instead gives a first-time reader, in one picture, the two claims the
rest of the paper backs with data.

(1) The information weight is a price. A usage curve U(w) relates the
    info-gain weight w to how much sensing an agent spends. A stated
    expected sensing budget B is a target for expected usage, and the curve
    jumps over it between two sampled grid weights, so the sampled grid can
    only bracket the crossing threshold by (w_lo, w_hi], the crossing
    bracket of Definition PI-3, and no single weight attains B. The policy
    that attains B in expectation is the endpoint mixture, which plays w_hi
    with probability q and w_lo otherwise, drawn afresh each episode, and is
    drawn separately from the bracket. Redrawn 2026-09-18 (ledger 9.17.46)
    after a re-review found the earlier diagonal rise, "shadow price
    w*(B) = (w_lo, w_hi]" legend, and "met partway through the rise" caption
    still carried the interval-valued-price reading the revised definition
    withdrew. This is the dominant visual, matching the paper's own framing
    of the budgeted reformulation as its primary contribution.

(2) Active inference's canonical w=1 is one point on that same curve, not
    a second free hyperparameter. Minimizing the recursive, reward-based
    Expected Free Energy objective the paper specifies is equivalent to
    solving the same weighted objective at w=1 (the equivalence
    proposition, numbered 3.1 in the JAIR master and 1 in the LNCS master,
    so the producer takes the label as an argument and each master reads
    its own file), so w=1 is drawn as a star sitting on the curve,
    deliberately outside the drawn bracket so the figure never implies a
    coincidence between EFE's weight and this particular budget's price.

The staircase, budget, and bracket reuse the exact axhline/axvspan
conventions of plot_cost_budget (run_price_of_information.py), and the
vermillion five-point star reuses the exact EFE-agent marker convention of
run_pareto.py's Pareto panels, so this figure introduces no new visual
vocabulary relative to the rest of the paper.
"""
import argparse

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


def plot_hero(path: str = "figures/fig_hero_price_curve.pdf",
              prop_label: str = "Prop. 3.1") -> None:
    figstyle.apply()
    fig, ax = plt.subplots(figsize=figstyle.figsize(1.0, aspect=0.50))

    # Schematic usage curve: flat, one jump, flat. Illustrative only, not
    # measured data, and not a claim that real usage curves are always
    # monotone (several in this paper plateau, jump, or dip). The sampled
    # grid weights are drawn as markers. Between the grid weights w_lo=4 and
    # w_hi=10 the underlying curve jumps at an unsampled weight, drawn as a
    # thin dotted riser at w=6.3, so the budget line B=6.5 falls inside a
    # usage gap: no weight attains B exactly (the level set is empty), the
    # crossing threshold is that single jump, and the grid can only bracket
    # it. The jump sits at w=4..10 rather than w=3..10 to leave visible
    # breathing room between the shaded bracket band and the callout box
    # beside it (Pat flagged the two as reading too close together at w=3).
    w_grid = [0.1, 0.3, 1, 4, 10, 30, 100]
    u_grid = [3, 3, 3, 3, 10, 10, 10]
    w_jump = 6.3
    # Underlying curve: low plateau to the jump, riser, high plateau.
    ax.plot([0.08, w_jump], [3, 3], color=figstyle.BLUE, lw=1.8, zorder=3,
            label="$U(w)$: schematic usage curve")
    ax.plot([w_jump, w_jump], [3, 10], color=figstyle.BLUE, lw=1.0, ls=":",
            zorder=3)
    ax.plot([w_jump, 140], [10, 10], color=figstyle.BLUE, lw=1.8, zorder=3)
    ax.plot(w_grid, u_grid, color=figstyle.BLUE, marker="o", ms=5, lw=0,
            linestyle="none", zorder=4, label="sampled grid weights")
    ax.set_xscale("log")
    ax.set_xlim(0.08, 140)
    ax.set_ylim(0, 13)

    # Stated expected sensing budget B, a target for expected usage.
    B = 6.5
    ax.axhline(B, color=figstyle.GRAY, ls="--", lw=1.2, zorder=2,
               label="expected sensing budget $B$ (target)")

    # Crossing bracket (w_lo, w_hi], the grid's estimate of where the curve
    # crosses B, half-open and closed at w_hi per Definition PI-3: the shaded
    # fill is solid flush to both edges, with no open-circle or dashed-edge
    # cue at either boundary that would read as excluded (the exact ambiguity
    # a prior figure in this paper had to be corrected for). It is a grid
    # interval, not a set of prices.
    w_lo, w_hi = 4, 10
    ax.axvspan(w_lo, w_hi, color=figstyle.GRAY, alpha=0.15, zorder=0,
               label=r"crossing bracket $(w_{\mathrm{lo}}, w_{\mathrm{hi}}]$ (grid estimate)")
    # Labeled near the top of the band, not the bottom: the bottom-right of
    # the panel is where the legend sits, and a first pass collided the two.
    ax.text(w_lo, 12.5, r"$w_{\mathrm{lo}}$", fontsize=7.5,
            color=figstyle.GRAY, ha="center", va="top")
    ax.text(w_hi, 12.5, r"$w_{\mathrm{hi}}$", fontsize=7.5,
            color=figstyle.GRAY, ha="center", va="top")

    # Endpoint mixture: the randomized policy that attains B in expectation
    # by playing w_hi with probability q and w_lo otherwise. It is not a
    # weight, so it is drawn as an open diamond on the budget line at the
    # jump, with two thin leader lines from the two endpoint grid points it
    # mixes, and its own legend entry.
    q = (B - 3) / (10 - 3)
    for (wx, uy) in ((w_lo, 3), (w_hi, 10)):
        ax.plot([wx, w_jump], [uy, B], color=figstyle.GRAY, lw=0.7, ls="-",
                alpha=0.8, zorder=2)
    ax.plot([w_jump], [B], marker="D", ms=7, markerfacecolor="white",
            markeredgecolor="black", markeredgewidth=0.9, linestyle="none",
            zorder=6,
            label=(r"endpoint mixture: $w_{\mathrm{hi}}$ w.p. $q$, "
                   r"$w_{\mathrm{lo}}$ otherwise, $\mathbb{E}[U]=B$"))
    ax.text(w_jump * 1.12, B + 0.45, f"$q{{=}}{q:.1f}$", fontsize=7,
            color="0.15", ha="left", va="bottom", zorder=6)

    # EFE's canonical w=1, on the curve's low plateau, deliberately outside
    # the drawn bracket.
    ax.plot([1], [3], marker="*", ms=16,
            markerfacecolor=figstyle.AGENT_COLORS["EFE"],
            markeredgecolor="black", markeredgewidth=0.7, linestyle="none",
            zorder=5, label="$w{=}1$ (EFE)")

    ax.set_xlabel("Information weight $w$ (log scale)")
    ax.set_ylabel("$U(w)$: expected sensing usage per episode\n(schematic units)")
    figstyle.style_axis(ax)
    # Six legend entries no longer fit in the lower-right corner without
    # covering the low plateau or the band, so the legend sits below the
    # axes in two columns (savefig.bbox is "tight" in figstyle, so it is
    # kept in the exported page).
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.19), ncol=3,
              fontsize=6.9, handlelength=1.4, frameon=False,
              columnspacing=1.0, handletextpad=0.5)

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
        (f"({prop_label}, exact under log scoring)", "0.15"),
    ], fontsize=fs, right_limit=box_right - 0.01, line_name="line 4")

    fig.savefig(path)
    fig.savefig(path.replace(".pdf", ".png"))
    print(f"Saved {path} and its .png twin")


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--path", default=None, help="output PDF, used only with --one")
    ap.add_argument("--prop-label", default=None,
                    help="proposition label printed in the callout box, used only with --one: "
                         "'Prop. 3.1' for the JAIR master, 'Prop. 1' for the LNCS master")
    ap.add_argument("--both", action="store_true",
                    help="(default) write figures/fig_hero_price_curve.pdf (LNCS, Prop. 1) and "
                         "figures/fig_hero_price_curve_jair.pdf (JAIR, Prop. 3.1)")
    ap.add_argument("--one", action="store_true",
                    help="write only --path with --prop-label (both must then be given together, "
                         "since the LNCS file needs 'Prop. 1' and the JAIR file 'Prop. 3.1')")
    a = ap.parse_args()
    if a.one:
        # A no-argument run must never pair the LNCS path with the JAIR label
        # (a re-review caught that the earlier defaults did exactly that), so the
        # single-file mode requires both to be stated explicitly.
        if a.path is None or a.prop_label is None:
            ap.error("--one requires both --path and --prop-label")
        plot_hero(a.path, a.prop_label)
    else:
        if a.path is not None or a.prop_label is not None:
            ap.error("--path and --prop-label are only used with --one; a plain run writes both committed files")
        plot_hero("figures/fig_hero_price_curve.pdf", "Prop. 1")
        plot_hero("figures/fig_hero_price_curve_jair.pdf", "Prop. 3.1")
