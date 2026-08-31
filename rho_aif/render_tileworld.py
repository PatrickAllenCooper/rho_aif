"""
Tileworld visual renderer for publication-quality grid figures.

Produces:
  1. Step-by-step belief evolution strips (single agent)
  2. Side-by-side agent comparison panels (same episode, multiple agents)
  3. Scan region atlas showing all spatial partitions
"""

import os

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.patheffects as mpatheffects
from matplotlib.collections import LineCollection
from matplotlib.colors import ListedColormap, PowerNorm
from matplotlib.lines import Line2D
from typing import List, Optional
from dataclasses import dataclass

from rho_aif.environments.tileworld import TileworldEnv
from rho_aif.agents.base import BaseAgent
from rho_aif.belief import BeliefState
from rho_aif import figstyle


def _save_fig(fig, save_path):
    """Save the PDF artifact of record plus its PNG twin."""
    base = os.path.splitext(save_path)[0]
    fig.savefig(base + ".pdf", bbox_inches="tight", dpi=300)
    fig.savefig(base + ".png", bbox_inches="tight", dpi=300)


@dataclass
class TileworldStepRecord:
    """One step of a Tileworld episode for rendering."""
    step: int
    belief: np.ndarray
    action: int
    action_type: str  # "scan" or "commit"
    scan_idx: Optional[int]
    observation: Optional[int]
    reward: float
    cumulative_reward: float


@dataclass
class TileworldEpisodeRecord:
    """Full episode record for rendering."""
    grid_size: int
    target_cell: int
    steps: List[TileworldStepRecord]
    success: bool
    total_reward: float
    agent_name: str


def run_recorded_episode(
    agent: BaseAgent,
    env: TileworldEnv,
    max_steps: int = 100,
    agent_name: str = "",
    seed: Optional[int] = None,
) -> TileworldEpisodeRecord:
    """Run an episode and record every step for rendering."""
    if seed is not None:
        obs, info = env.reset(seed=seed)
    else:
        obs, info = env.reset()
    agent.reset()
    target_cell = info["target_cell"]
    records = []
    cum_reward = 0.0

    initial_belief = agent.belief.belief.copy()
    records.append(TileworldStepRecord(
        step=0, belief=initial_belief, action=-1,
        action_type="initial", scan_idx=None,
        observation=None, reward=0.0, cumulative_reward=0.0,
    ))

    for t in range(1, max_steps + 1):
        action = agent.select_action()
        is_scan = action < env.num_scans

        obs, reward, terminated, truncated, step_info = env.step(action)
        cum_reward += reward

        if is_scan:
            agent.update_belief(obs, obs_action=action)

        records.append(TileworldStepRecord(
            step=t,
            belief=agent.belief.belief.copy(),
            action=action,
            action_type="scan" if is_scan else "commit",
            scan_idx=action if is_scan else None,
            observation=obs if is_scan else None,
            reward=reward,
            cumulative_reward=cum_reward,
        ))

        if terminated or truncated:
            break

    return TileworldEpisodeRecord(
        grid_size=env.grid_size,
        target_cell=target_cell,
        steps=records,
        success=step_info.get("correct", False),
        total_reward=cum_reward,
        agent_name=agent_name,
    )


def _mask_boundary_segments(mask: np.ndarray) -> list:
    """Cell-edge segments on the boundary of a boolean mask.

    Drawing only the outer boundary renders each connected scanned band as
    one contiguous outline instead of a chain of per-cell boxes.
    """
    segs = []
    n_rows, n_cols = mask.shape
    for r in range(n_rows):
        for c in range(n_cols):
            if not mask[r, c]:
                continue
            if r == 0 or not mask[r - 1, c]:
                segs.append([(c - 0.5, r - 0.5), (c + 0.5, r - 0.5)])
            if r == n_rows - 1 or not mask[r + 1, c]:
                segs.append([(c - 0.5, r + 0.5), (c + 0.5, r + 0.5)])
            if c == 0 or not mask[r, c - 1]:
                segs.append([(c - 0.5, r - 0.5), (c - 0.5, r + 0.5)])
            if c == n_cols - 1 or not mask[r, c + 1]:
                segs.append([(c + 0.5, r - 0.5), (c + 0.5, r + 0.5)])
    return segs


def _draw_grid(
    ax: plt.Axes,
    belief: np.ndarray,
    grid_size: int,
    target_cell: Optional[int] = None,
    scan_mask: Optional[np.ndarray] = None,
    commit_cell: Optional[int] = None,
    title: str = "",
    show_target: bool = False,
    norm=None,
    title_fontsize: float = 7.0,
):
    """Render a single grid frame with belief heatmap and annotations.

    The heat carries the belief values (a shared colorbar decodes them, so
    no per-cell numbers are drawn). Overlay marks stay off the agent palette:
    the scanned region is a black contiguous outline, the true tile a
    black-edged white star, and the committed cell a white ring with a black
    stroke, all legible on both ends of the belief colormap.
    """
    belief_grid = belief.reshape(grid_size, grid_size)

    im = ax.imshow(
        belief_grid, cmap=figstyle.BELIEF_CMAP, norm=norm,
        interpolation="nearest", aspect="equal",
    )

    if scan_mask is not None:
        segs = _mask_boundary_segments(scan_mask)
        outline = LineCollection(segs, colors="black", linewidths=1.4,
                                 capstyle="projecting", zorder=4)
        outline.set_path_effects([
            mpatheffects.withStroke(linewidth=2.8, foreground="white"),
        ])
        ax.add_collection(outline)

    if show_target and target_cell is not None:
        tr, tc = target_cell // grid_size, target_cell % grid_size
        ax.plot(tc, tr, marker="*", markersize=9, color="white",
                markeredgecolor="black", markeredgewidth=0.9, zorder=6)

    if commit_cell is not None:
        cr, cc = commit_cell // grid_size, commit_cell % grid_size
        circle = plt.Circle((cc, cr), 0.42, fill=False,
                            edgecolor="white", linewidth=1.4, zorder=5)
        circle.set_path_effects([
            mpatheffects.withStroke(linewidth=3.0, foreground="black"),
        ])
        ax.add_patch(circle)

    for r in range(grid_size + 1):
        ax.axhline(r - 0.5, color="#666666", linewidth=0.4, zorder=2)
    for c in range(grid_size + 1):
        ax.axvline(c - 0.5, color="#666666", linewidth=0.4, zorder=2)

    ax.set_xlim(-0.5, grid_size - 0.5)
    ax.set_ylim(grid_size - 0.5, -0.5)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_title(title, fontsize=title_fontsize, pad=3)
    return im


def render_belief_evolution(
    episode: TileworldEpisodeRecord,
    env: TileworldEnv,
    save_path: str,
    max_panels: int = 7,
    show_target: bool = True,
):
    """
    Render a two-row grid of panels showing belief evolution: the initial
    state, selected scan steps, and the final commit. Authored at the width
    it is printed at (0.78 of the JAIR text block) so type prints at size.
    A shared colorbar decodes the belief colormap; a square-root color
    normalization keeps the low-probability early-episode structure visible.
    """
    scan_steps = [s for s in episode.steps if s.action_type == "scan"]
    commit_step = next((s for s in episode.steps if s.action_type == "commit"), None)
    initial = episode.steps[0]

    if len(scan_steps) + 2 <= max_panels:
        selected = scan_steps
    else:
        n_show = max_panels - 2
        indices = np.linspace(0, len(scan_steps) - 1, n_show, dtype=int)
        selected = [scan_steps[i] for i in indices]

    panels = [initial] + selected
    if commit_step:
        panels.append(commit_step)
    n = len(panels)

    # One spare slot is always reserved for the colorbar.
    n_cols = 4
    n_rows = max(1, (n + 1 + n_cols - 1) // n_cols)
    fig_w = figstyle.TEXT_WIDTH_IN * 0.78
    panel_w = fig_w / n_cols
    fig, axes = plt.subplots(
        n_rows, n_cols,
        figsize=(fig_w, n_rows * (panel_w + 0.38)),
        squeeze=False,
    )

    vmax = max(s.belief.max() for s in panels)
    vmax = max(vmax, 1.0 / episode.grid_size ** 2 * 2)
    norm = PowerNorm(gamma=0.5, vmin=0.0, vmax=vmax)

    im = None
    for i, step_rec in enumerate(panels):
        ax = axes[divmod(i, n_cols)]
        scan_mask = None
        commit_cell = None
        letter = chr(ord("a") + i)

        if step_rec.action_type == "initial":
            title = f"({letter}) $t{{=}}0$\nuniform prior"
        elif step_rec.action_type == "scan":
            scan_desc = env.get_scan_description(step_rec.scan_idx)
            scan_label = scan_desc.split(":")[0].lower()
            obs_label = "A" if step_rec.observation == 0 else "B"
            title = (f"({letter}) $t{{=}}{step_rec.step}$: {scan_label}\n"
                     f"obs $=$ {obs_label}")
            scan_mask = env.get_scan_mask(step_rec.scan_idx)
        elif step_rec.action_type == "commit":
            commit_cell = step_rec.action - env.num_scans
            result_str = "correct" if episode.success else "wrong"
            title = (f"({letter}) $t{{=}}{step_rec.step}$: collect\n"
                     f"{result_str}, $R{{=}}{episode.total_reward:+.1f}$")

        im = _draw_grid(
            ax, step_rec.belief, episode.grid_size,
            target_cell=episode.target_cell,
            scan_mask=scan_mask,
            commit_cell=commit_cell,
            title=title,
            show_target=show_target,
            norm=norm,
        )

    for i in range(n, n_rows * n_cols):
        axes[divmod(i, n_cols)].axis("off")

    # Colorbar in the spare slot.
    spare = axes[divmod(n_rows * n_cols - 1, n_cols)]
    cax = spare.inset_axes([0.10, 0.52, 0.80, 0.10])
    cbar = fig.colorbar(im, cax=cax, orientation="horizontal")
    cbar.set_label("Belief probability", fontsize=7)
    cbar.set_ticks([t for t in (0.0, 0.05, 0.2, 0.5) if t <= vmax])
    cbar.ax.tick_params(labelsize=6.5)

    # No suptitle: the LaTeX caption carries the description.
    plt.tight_layout()
    _save_fig(fig, save_path)
    plt.close()


def render_agent_comparison(
    episodes: List[TileworldEpisodeRecord],
    env: TileworldEnv,
    save_path: str,
    max_panels_per_row: int = 7,
):
    """
    Multi-row figure: one row per agent, same episode seed, showing
    different exploration strategies side by side.

    Authored at the JAIR text-block width (printed at width=linewidth) so
    type prints at rcParams size. The identical uniform prior is stated in
    the caption rather than drawn once per row, a shared colorbar decodes
    the belief colormap, and a legend explains the overlay marks. Scan
    panels are subsampled evenly per row (rows are not time-aligned), which
    an in-figure note states.
    """
    n_agents = len(episodes)

    all_panel_data = []
    for ep in episodes:
        scan_steps = [s for s in ep.steps if s.action_type == "scan"]
        commit_step = next((s for s in ep.steps if s.action_type == "commit"), None)

        # The uniform t=0 prior is identical across rows and is stated in
        # the caption, so the panel budget goes to scans plus the commit.
        n_show = max_panels_per_row - 2
        if len(scan_steps) <= n_show:
            selected = scan_steps
        else:
            indices = np.linspace(0, len(scan_steps) - 1, n_show, dtype=int)
            selected = [scan_steps[i] for i in indices]

        row_panels = list(selected)
        if commit_step:
            row_panels.append(commit_step)
        all_panel_data.append(row_panels)

    n_cols = max(len(row) for row in all_panel_data)

    fig, axes = plt.subplots(
        n_agents, n_cols,
        figsize=(figstyle.TEXT_WIDTH_IN, n_agents * 1.22),
        squeeze=False,
    )

    global_vmax = max(
        s.belief.max()
        for panels in all_panel_data
        for s in panels
    )
    global_vmax = max(global_vmax, 0.1)
    norm = PowerNorm(gamma=0.5, vmin=0.0, vmax=global_vmax)

    im = None
    for row_idx, (ep, panels) in enumerate(zip(episodes, all_panel_data)):
        for col_idx in range(n_cols):
            ax = axes[row_idx, col_idx]

            if col_idx >= len(panels):
                ax.axis("off")
                continue

            step_rec = panels[col_idx]
            scan_mask = None
            commit_cell = None

            if step_rec.action_type == "scan":
                scan_label = (env.get_scan_description(step_rec.scan_idx)
                              .split(":")[0].lower())
                obs_label = "A" if step_rec.observation == 0 else "B"
                title = f"$t{{=}}{step_rec.step}$: {scan_label}\nobs $=$ {obs_label}"
                scan_mask = env.get_scan_mask(step_rec.scan_idx)
            elif step_rec.action_type == "commit":
                commit_cell = step_rec.action - env.num_scans
                result_str = "correct" if ep.success else "wrong"
                title = f"$t{{=}}{step_rec.step}$: commit\n{result_str}"

            show_target = (col_idx == len(panels) - 1)

            im = _draw_grid(
                ax, step_rec.belief, ep.grid_size,
                target_cell=ep.target_cell,
                scan_mask=scan_mask,
                commit_cell=commit_cell,
                title=title,
                show_target=show_target,
                norm=norm,
                title_fontsize=6.5,
            )

            if col_idx == 0:
                n_scans = sum(1 for s in ep.steps if s.action_type == "scan")
                ax.set_ylabel(
                    f"{ep.agent_name}\n{n_scans} scans\n$R{{=}}{ep.total_reward:+.1f}$",
                    fontsize=8.5, rotation=0, labelpad=8,
                    va="center", ha="right",
                )

    cbar = fig.colorbar(im, ax=axes.ravel().tolist(),
                        fraction=0.025, pad=0.015)
    cbar.set_label("Belief P(tile)", fontsize=8)
    cbar.ax.tick_params(labelsize=7)

    legend_handles = [
        mpatches.Patch(facecolor="none", edgecolor="black", linewidth=1.2,
                       label="Scanned region"),
        Line2D([], [], marker="*", linestyle="none", markersize=9,
               markerfacecolor="white", markeredgecolor="black",
               markeredgewidth=0.9, label="True tile"),
        Line2D([], [], marker="o", linestyle="none", markersize=8,
               markerfacecolor="none", markeredgecolor="black",
               markeredgewidth=1.2, label="Committed cell"),
    ]
    fig.legend(handles=legend_handles, loc="lower center", ncol=3,
               bbox_to_anchor=(0.5, -0.045), frameon=False, fontsize=8)
    fig.text(0.5, -0.085,
             "Scan panels are subsampled evenly per row; $t$ gives the true step.",
             ha="center", fontsize=7, color=figstyle.GRAY)

    _save_fig(fig, save_path)
    plt.close()


def render_scan_atlas(
    env: TileworldEnv,
    save_path: str,
):
    """Render all scan region masks in a single figure.

    Three columns fill a 2x3 grid with no empty cells for the six scans of
    the 6x6 grid. The mask uses a white/Okabe-Ito-blue two-color map, and
    the LaTeX caption carries the description (no suptitle).
    """
    figstyle.apply()
    n = env.num_scans
    cols = min(n, 3)
    rows = (n + cols - 1) // cols
    fig, axes = plt.subplots(rows, cols, figsize=(2.1 * cols, 2.35 * rows),
                             squeeze=False)

    cmap = ListedColormap(["white", figstyle.BLUE])
    for k in range(n):
        r, c = divmod(k, cols)
        ax = axes[r, c]
        mask = env.get_scan_mask(k).astype(float)
        ax.imshow(mask, cmap=cmap, vmin=0, vmax=1, interpolation="nearest")
        for ri in range(env.grid_size):
            for ci in range(env.grid_size):
                label = "B" if mask[ri, ci] else "A"
                color = "white" if mask[ri, ci] else "black"
                ax.text(ci, ri, label, ha="center", va="center",
                        fontsize=8, color=color)
        for ri in range(env.grid_size + 1):
            ax.axhline(ri - 0.5, color="gray", lw=0.5)
        for ci in range(env.grid_size + 1):
            ax.axvline(ci - 0.5, color="gray", lw=0.5)
        desc = env.get_scan_description(k)
        ax.set_title(desc.replace(": ", "\n", 1), fontsize=8)
        ax.set_xticks([])
        ax.set_yticks([])

    for k in range(n, rows * cols):
        r, c = divmod(k, cols)
        axes[r, c].axis("off")

    plt.tight_layout()
    _save_fig(fig, save_path)
    plt.close()
