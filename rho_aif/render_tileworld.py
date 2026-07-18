"""
Tileworld visual renderer for publication-quality grid figures.

Produces:
  1. Step-by-step belief evolution strips (single agent)
  2. Side-by-side agent comparison panels (same episode, multiple agents)
  3. Scan region atlas showing all spatial partitions
"""

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.colors import Normalize
from typing import List, Tuple, Optional, Dict
from dataclasses import dataclass, field

from rho_aif.environments.tileworld import TileworldEnv
from rho_aif.agents.base import BaseAgent
from rho_aif.belief import BeliefState


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


def _draw_grid(
    ax: plt.Axes,
    belief: np.ndarray,
    grid_size: int,
    target_cell: Optional[int] = None,
    scan_mask: Optional[np.ndarray] = None,
    commit_cell: Optional[int] = None,
    title: str = "",
    show_target: bool = False,
    vmin: float = 0.0,
    vmax: float = 1.0,
):
    """Render a single grid frame with belief heatmap and annotations."""
    belief_grid = belief.reshape(grid_size, grid_size)

    ax.imshow(
        belief_grid, cmap="YlOrRd", vmin=vmin, vmax=vmax,
        interpolation="nearest", aspect="equal",
    )

    for r in range(grid_size):
        for c in range(grid_size):
            val = belief_grid[r, c]
            color = "white" if val > 0.5 * vmax else "black"
            ax.text(
                c, r, f"{val:.2f}", ha="center", va="center",
                fontsize=max(4, 8 - grid_size), color=color, fontweight="bold",
            )

    if scan_mask is not None:
        for r in range(grid_size):
            for c in range(grid_size):
                if scan_mask[r, c]:
                    rect = mpatches.FancyBboxPatch(
                        (c - 0.48, r - 0.48), 0.96, 0.96,
                        boxstyle="round,pad=0.02",
                        linewidth=2.0, edgecolor="#2196F3",
                        facecolor="none", zorder=3,
                    )
                    ax.add_patch(rect)

    if show_target and target_cell is not None:
        tr, tc = target_cell // grid_size, target_cell % grid_size
        ax.plot(tc, tr, marker="*", markersize=14, color="#00C853",
                markeredgecolor="black", markeredgewidth=0.8, zorder=5)

    if commit_cell is not None:
        cr, cc = commit_cell // grid_size, commit_cell % grid_size
        circle = plt.Circle((cc, cr), 0.4, fill=False,
                            edgecolor="#D32F2F", linewidth=2.5, zorder=5)
        ax.add_patch(circle)

    for r in range(grid_size + 1):
        ax.axhline(r - 0.5, color="#666666", linewidth=0.5, zorder=2)
    for c in range(grid_size + 1):
        ax.axvline(c - 0.5, color="#666666", linewidth=0.5, zorder=2)

    ax.set_xlim(-0.5, grid_size - 0.5)
    ax.set_ylim(grid_size - 0.5, -0.5)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_title(title, fontsize=8, pad=4)


def render_belief_evolution(
    episode: TileworldEpisodeRecord,
    env: TileworldEnv,
    save_path: str,
    max_panels: int = 7,
    show_target: bool = True,
    figsize_per_panel: Tuple[float, float] = (2.5, 2.8),
):
    """
    Render a horizontal strip of grid panels showing belief evolution.
    Includes the initial state, selected scan steps, and the final commit.
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

    fig, axes = plt.subplots(1, n, figsize=(figsize_per_panel[0] * n, figsize_per_panel[1]))
    if n == 1:
        axes = [axes]

    vmax = max(s.belief.max() for s in panels)
    vmax = max(vmax, 1.0 / episode.grid_size ** 2 * 2)

    for i, step_rec in enumerate(panels):
        ax = axes[i]
        scan_mask = None
        commit_cell = None

        if step_rec.action_type == "initial":
            title = "t=0 (uniform)"
        elif step_rec.action_type == "scan":
            scan_desc = env.get_scan_description(step_rec.scan_idx)
            obs_label = "A" if step_rec.observation == 0 else "B"
            title = f"t={step_rec.step}: {scan_desc.split(':')[0]}\nobs={obs_label}"
            scan_mask = env.get_scan_mask(step_rec.scan_idx)
        elif step_rec.action_type == "commit":
            collected = step_rec.action - env.num_scans
            commit_cell = collected
            result_str = "correct" if episode.success else "wrong"
            title = f"t={step_rec.step}: collect ({result_str})\nR={episode.total_reward:+.1f}"

        show = show_target and (i == len(panels) - 1)

        _draw_grid(
            ax, step_rec.belief, episode.grid_size,
            target_cell=episode.target_cell,
            scan_mask=scan_mask,
            commit_cell=commit_cell,
            title=title,
            show_target=show,
            vmax=vmax,
        )

    fig.suptitle(
        f"{episode.agent_name} on {episode.grid_size}x{episode.grid_size} Tileworld",
        fontsize=11, fontweight="bold", y=1.02,
    )

    plt.tight_layout()
    plt.savefig(save_path, bbox_inches="tight", dpi=300)
    plt.close()


def render_agent_comparison(
    episodes: List[TileworldEpisodeRecord],
    env: TileworldEnv,
    save_path: str,
    max_panels_per_row: int = 7,
    figsize_per_panel: Tuple[float, float] = (2.2, 2.5),
):
    """
    Multi-row figure: one row per agent, same episode seed, showing
    different exploration strategies side by side.
    """
    n_agents = len(episodes)
    max_steps_shown = max_panels_per_row

    all_panel_data = []
    for ep in episodes:
        scan_steps = [s for s in ep.steps if s.action_type == "scan"]
        commit_step = next((s for s in ep.steps if s.action_type == "commit"), None)
        initial = ep.steps[0]

        if len(scan_steps) + 2 <= max_steps_shown:
            selected = scan_steps
        else:
            n_show = max_steps_shown - 2
            indices = np.linspace(0, len(scan_steps) - 1, n_show, dtype=int)
            selected = [scan_steps[i] for i in indices]

        row_panels = [initial] + selected
        if commit_step:
            row_panels.append(commit_step)
        all_panel_data.append(row_panels)

    n_cols = max(len(row) for row in all_panel_data)

    fig, axes = plt.subplots(
        n_agents, n_cols,
        figsize=(figsize_per_panel[0] * n_cols, figsize_per_panel[1] * n_agents),
        squeeze=False,
    )

    global_vmax = max(
        s.belief.max()
        for panels in all_panel_data
        for s in panels
    )
    global_vmax = max(global_vmax, 0.1)

    for row_idx, (ep, panels) in enumerate(zip(episodes, all_panel_data)):
        for col_idx in range(n_cols):
            ax = axes[row_idx, col_idx]

            if col_idx >= len(panels):
                ax.axis("off")
                continue

            step_rec = panels[col_idx]
            scan_mask = None
            commit_cell = None

            if step_rec.action_type == "initial":
                title = "t=0"
            elif step_rec.action_type == "scan":
                scan_label = env.get_scan_description(step_rec.scan_idx).split(":")[0]
                obs_label = "A" if step_rec.observation == 0 else "B"
                title = f"t={step_rec.step}: {scan_label}\nobs={obs_label}"
                scan_mask = env.get_scan_mask(step_rec.scan_idx)
            elif step_rec.action_type == "commit":
                commit_cell = step_rec.action - env.num_scans
                result_str = "correct" if ep.success else "wrong"
                title = f"Commit ({result_str})"

            show_target = (col_idx == len(panels) - 1)

            _draw_grid(
                ax, step_rec.belief, ep.grid_size,
                target_cell=ep.target_cell,
                scan_mask=scan_mask,
                commit_cell=commit_cell,
                title=title,
                show_target=show_target,
                vmax=global_vmax,
            )

            if col_idx == 0:
                n_scans = sum(1 for s in ep.steps if s.action_type == "scan")
                ax.set_ylabel(
                    f"{ep.agent_name}\n({n_scans} scans, R={ep.total_reward:+.1f})",
                    fontsize=8, rotation=0, labelpad=60, va="center",
                )

    plt.tight_layout()
    plt.savefig(save_path, bbox_inches="tight", dpi=300)
    plt.close()


def render_scan_atlas(
    env: TileworldEnv,
    save_path: str,
):
    """Render all scan region masks in a single figure."""
    n = env.num_scans
    cols = min(n, 4)
    rows = (n + cols - 1) // cols
    fig, axes = plt.subplots(rows, cols, figsize=(3 * cols, 3 * rows))
    if rows == 1 and cols == 1:
        axes = np.array([[axes]])
    elif rows == 1:
        axes = axes[np.newaxis, :]
    elif cols == 1:
        axes = axes[:, np.newaxis]

    for k in range(n):
        r, c = divmod(k, cols)
        ax = axes[r, c]
        mask = env.get_scan_mask(k).astype(float)
        ax.imshow(mask, cmap="Blues", vmin=0, vmax=1, interpolation="nearest")
        for ri in range(env.grid_size):
            for ci in range(env.grid_size):
                label = "B" if mask[ri, ci] else "A"
                color = "white" if mask[ri, ci] else "black"
                ax.text(ci, ri, label, ha="center", va="center",
                        fontsize=8, color=color, fontweight="bold")
        for ri in range(env.grid_size + 1):
            ax.axhline(ri - 0.5, color="gray", lw=0.5)
        for ci in range(env.grid_size + 1):
            ax.axvline(ci - 0.5, color="gray", lw=0.5)
        ax.set_title(env.get_scan_description(k), fontsize=7)
        ax.set_xticks([])
        ax.set_yticks([])

    for k in range(n, rows * cols):
        r, c = divmod(k, cols)
        axes[r, c].axis("off")

    fig.suptitle(
        f"Scan regions for {env.grid_size}x{env.grid_size} Tileworld "
        f"({env.num_scans} scans)",
        fontsize=11, fontweight="bold",
    )
    plt.tight_layout()
    plt.savefig(save_path, bbox_inches="tight", dpi=300)
    plt.close()
