#!/usr/bin/env python3
"""Build four explanatory diagrams for the full manuscript.

These are analytical schematics, not experimental results.  No episodes
are run and no result files are read or modified.  The destructive-test
diagram is the exact binary example in Example ``ex:destructive``.  The
target-versus-cap diagram uses the explicitly illustrative policy points
A=(1,4), C=(2,6), D=(5,3), with coordinates (expected usage, reward), and
B=4.  Episode randomization linearly interpolates these coordinates:
the A--D mixture at B is (4, 13/4), the C--D mixture is (4,4), and the
reward optimum under usage <= B is the slack policy C=(2,6).

Run from the repository root:
    .venv/bin/python experiments/build_fig_concepts.py

PDF is the vector artifact; PNG is a review twin.  All four are authored
at the JAIR text width, with shapes/line styles as well as color cues.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Polygon

from rho_aif import figstyle


INK = "#252525"
MUTED = "#595959"
LIGHT = "#F6F6F6"


def canvas(height: float):
    fig, ax = plt.subplots(figsize=(figstyle.TEXT_WIDTH_IN, height))
    fig.subplots_adjust(left=0.025, right=0.975, bottom=0.025, top=0.975)
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.set_axis_off()
    return fig, ax


def label(ax, x, y, text, **kwargs):
    options = dict(ha="center", va="center", color=INK,
                   fontsize=10, linespacing=1.4)
    options.update(kwargs)
    return ax.text(x, y, text, **options)


def box(ax, x, y, w, h, text, color=INK, fill=LIGHT, fontsize=10):
    patch = FancyBboxPatch((x - w / 2, y - h / 2), w, h,
                          boxstyle="round,pad=0.008,rounding_size=0.016",
                          linewidth=1.0, edgecolor=color, facecolor=fill,
                          zorder=3)
    ax.add_patch(patch)
    txt = ax.text(x, y, text, ha="center", va="center", color=INK,
                  fontsize=fontsize, linespacing=1.45, zorder=4)
    return patch, txt


def arrow(ax, start, end, color=INK, lw=1.15, **kwargs):
    patch = FancyArrowPatch(start, end, arrowstyle="-|>", mutation_scale=10,
                            linewidth=lw, color=color, zorder=2, **kwargs)
    ax.add_patch(patch)
    return patch


def save(fig, name: str, output: Path):
    output.mkdir(parents=True, exist_ok=True)
    # Keep the intended 6.5-inch print width rather than tight-cropping it.
    fig.savefig(output / f"{name}.pdf", bbox_inches=None,
                metadata={"CreationDate": None, "ModDate": None})
    fig.savefig(output / f"{name}.png", bbox_inches=None, dpi=220)
    plt.close(fig)


def plot_otc_loop(output: Path):
    fig, ax = canvas(2.75)
    box(ax, .10, .52, .17, .22, "Belief $b$\nchoose action")
    box(ax, .35, .70, .18, .22, "Observe $a$\npay cost $c_a$", color=figstyle.BLUE)
    box(ax, .61, .70, .20, .22, "Sample $o$\n$P(o\\mid s,a)$", color=figstyle.BLUE)
    box(ax, .88, .70, .20, .22, "Update belief\n$b'\\propto P(o\\mid s,a)b(s)$",
        color=figstyle.BLUE, fontsize=9.5)
    arrow(ax, (.19, .57), (.25, .70), color=figstyle.BLUE)
    arrow(ax, (.45, .70), (.50, .70), color=figstyle.BLUE)
    arrow(ax, (.72, .70), (.77, .70), color=figstyle.BLUE)
    # The return path is the next real decision, not an open-loop policy.
    ax.plot([.88, .88, .10, .10], [.82, .93, .93, .75],
            color=figstyle.BLUE, lw=1.15, zorder=1)
    arrow(ax, (.10, .75), (.10, .64), color=figstyle.BLUE)
    label(ax, .51, .935, "Replan from $b'$", backgroundcolor="white")
    label(ax, .62, .48, "Hidden state $s$ is unchanged", fontsize=9.5)

    box(ax, .35, .28, .18, .20, "Commit $a$", color=INK)
    box(ax, .61, .28, .20, .20, "Receive reward\n$R(s,a)$", color=INK)
    box(ax, .88, .28, .20, .20, "End episode\nno observation", color=INK)
    arrow(ax, (.19, .47), (.25, .28))
    arrow(ax, (.45, .28), (.50, .28))
    arrow(ax, (.72, .28), (.77, .28))
    label(ax, .53, .055, "Rewards contribute to return, not to belief updates.", fontsize=9.5)
    save(fig, "fig_otc_loop", output)


def plot_state_preservation(output: Path):
    fig, ax = canvas(3.10)
    label(ax, .50, .975, "Uniform prior on $s\\in\\{0,1\\}$ and perfect signal $o=s$", fontsize=10)
    # A common two-outcome signal is followed by two different transitions.
    for left, title, destructive in [(.015, "(a) State-preserving observation", False),
                                     (.525, "(b) Destructive test", True)]:
        cx = left + .22
        label(ax, cx, .86, title, fontsize=10)
        xs = [left + .045, left + .215, left + .385]
        for x, header in zip(xs, ["Before $s$", "Signal $o$", "After $s'$"]):
            label(ax, x, .75, header, fontsize=9.5)
        ys = [.59, .39]
        for value, y in enumerate(ys):
            box(ax, xs[0], y, .067, .115, str(value), fill="white")
            box(ax, xs[1], y, .067, .115, str(value), fill="white")
            arrow(ax, (xs[0] + .043, y), (xs[1] - .043, y))
        if destructive:
            box(ax, xs[2], .49, .067, .115, "0", color=figstyle.VERMILLION, fill="white")
            for y in ys:
                arrow(ax, (xs[1] + .043, y), (xs[2] - .043, .49), color=figstyle.VERMILLION)
            label(ax, cx, .20, "$s'=0$ for either signal\n0 bits about the post-test state", fontsize=9.8)
        else:
            for value, y in enumerate(ys):
                box(ax, xs[2], y, .067, .115, str(value), color=figstyle.BLUE, fill="white")
                arrow(ax, (xs[1] + .043, y), (xs[2] - .043, y), color=figstyle.BLUE)
            label(ax, cx, .20, "$s'=s=o$\n1 bit about the post-test state", fontsize=9.8)
    ax.plot([.5, .5], [.11, .87], color="#BBBBBB", lw=.65)
    label(ax, .5, .035, "Only (a)'s signal reduces uncertainty about the post-test state.", fontsize=9.5)
    save(fig, "fig_state_preservation", output)


def plot_target_vs_cap(output: Path):
    fig, ax = plt.subplots(figsize=(figstyle.TEXT_WIDTH_IN, 3.4))
    fig.subplots_adjust(left=.105, right=.985, bottom=.23, top=.95)
    a, c, d, budget = (1, 4), (2, 6), (5, 3), 4
    q_ad = (budget - a[0]) / (d[0] - a[0])
    q_cd = (budget - c[0]) / (d[0] - c[0])
    selected_reward = (1 - q_ad) * a[1] + q_ad * d[1]
    equality_reward = (1 - q_cd) * c[1] + q_cd * d[1]
    assert selected_reward == 3.25 and equality_reward == 4.0

    ax.add_patch(Polygon([a, c, (budget, equality_reward), (budget, selected_reward)],
                         facecolor="#F0F0F0", edgecolor="none", zorder=1))
    ax.plot([a[0], c[0], d[0]], [a[1], c[1], d[1]], color=INK, lw=1.25, zorder=2)
    ax.plot([a[0], d[0]], [a[1], d[1]], color=MUTED, lw=1.25, ls="--", zorder=2)
    ax.axvline(budget, color=MUTED, lw=1.0, ls=":", zorder=1)
    ax.text(budget + .06, 6.65, "$B=4$", fontsize=10, ha="left", va="center")
    ax.plot([a[0], d[0]], [a[1], d[1]], "o", color=INK, mfc="white", ms=6, zorder=4)
    ax.plot(*c, marker="*", color=figstyle.BLUE, mec=INK, mew=.65, ms=13, zorder=5)
    ax.plot(budget, equality_reward, marker="s", color=figstyle.BLUE, mec=INK,
            mew=.65, ms=6, zorder=5)
    ax.plot(budget, selected_reward, marker="D", color=figstyle.VERMILLION,
            mec=INK, mew=.65, ms=6, zorder=5)
    ax.annotate("Policy A\n$(1,4)$", a, xytext=(.33, 3.05), ha="center", fontsize=9.5,
                arrowprops={"arrowstyle": "-", "color": MUTED, "lw": .65})
    ax.annotate("Policy D\n$(5,3)$", d, xytext=(5.65, 2.50), ha="center", fontsize=9.5,
                arrowprops={"arrowstyle": "-", "color": MUTED, "lw": .65})
    ax.annotate("Cap optimum C\n$U=2<B,\ R=6$", c, xytext=(1.60, 6.50),
                ha="center", fontsize=10,
                arrowprops={"arrowstyle": "-", "color": MUTED, "lw": .65})
    ax.annotate("Best target mixture\n$U=4,\ R=4$", (budget, equality_reward),
                xytext=(5.22, 5.15), ha="center", fontsize=10,
                arrowprops={"arrowstyle": "-", "color": MUTED, "lw": .65})
    ax.annotate("Selected endpoint mixture\n$U=4,\ R=3.25$", (budget, selected_reward),
                xytext=(2.80, 1.72), ha="center", fontsize=10,
                arrowprops={"arrowstyle": "-", "color": MUTED, "lw": .65})
    ax.set(xlim=(0, 6.05), ylim=(1.25, 7.05), xlabel="Expected sensing usage $U$",
           ylabel="Expected reward $R$", xticks=range(7), yticks=[2, 3, 4, 5, 6, 7])
    ax.grid(False)
    fig.text(.55, .070, "Illustrative policy points. Line segments are per-episode mixtures.",
             ha="center", va="center", color=MUTED, fontsize=9.5)
    fig.text(.55, .025, "Shading marks cap-feasible mixtures.",
             ha="center", va="center", color=MUTED, fontsize=9.5)
    save(fig, "fig_target_vs_cap", output)


def plot_dual_feedback(output: Path):
    fig, ax = canvas(2.95)
    box(ax, .055, .66, .08, .17, "$w_t$", fill="white", fontsize=12)
    box(ax, .275, .66, .23, .21, "Run one episode\nobserve usage $U_t$")
    box(ax, .565, .66, .18, .21, "Usage error\n$B-U_t$")
    box(ax, .855, .66, .25, .21, "$w_t+a_t(B-U_t)$\nclip to $[0,w_{\\max}]$", color=figstyle.BLUE)
    arrow(ax, (.104, .66), (.151, .66))
    arrow(ax, (.398, .66), (.467, .66))
    arrow(ax, (.663, .66), (.722, .66))
    label(ax, .565, .925, "Target $B$", fontsize=10)
    arrow(ax, (.565, .865), (.565, .785))
    ax.plot([.855, .855, .055, .055], [.545, .405, .405, .47],
            color=figstyle.BLUE, lw=1.15, zorder=1)
    arrow(ax, (.055, .47), (.055, .565), color=figstyle.BLUE)
    label(ax, .52, .408, "$w_{t+1}$ for the next episode", backgroundcolor="white")
    label(ax, .27, .27, "$U_t<B$ pushes $w$ up", fontsize=10)
    label(ax, .75, .27, "$U_t>B$ pushes $w$ down", fontsize=10)
    label(ax, .50, .135,
          "Stationary guarantee requires a single sign-consistent crossing and the stated assumptions.",
          fontsize=9.2)
    label(ax, .50, .040,
          "Decaying step $a_t=\\eta_0/(1+\\delta t)$, $\\delta>0$. Reset-on-shift is a heuristic.",
          fontsize=9.5)
    save(fig, "fig_dual_feedback", output)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output-dir", type=Path, default=Path("figures"))
    args = parser.parse_args()
    figstyle.apply()
    for plot in [plot_otc_loop, plot_state_preservation, plot_target_vs_cap, plot_dual_feedback]:
        plot(args.output_dir)


if __name__ == "__main__":
    main()
