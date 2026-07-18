"""
Animated side-by-side comparison of a reward-only planner vs the EFE agent
on the same Tileworld episode, for a LinkedIn post announcing the IWAI paper.

Outputs (in linkedin_post/):
  efe_vs_planning.mp4   (upload this to LinkedIn as a video)
  efe_vs_planning.gif   (fallback / preview)
"""

import numpy as np
import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import matplotlib.animation as animation
from scipy.stats import entropy as scipy_entropy

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from environments.tileworld import TileworldEnv
from agents.planning import PlanningAgent
from agents.efe import EFEAgent
from run_experiment import make_agent
from render_tileworld import run_recorded_episode, TileworldEpisodeRecord

GRID = 6
HORIZON = 2

BG = "#0F1420"
PANEL_BG = "#161D2E"
FG = "#E8ECF4"
DIM = "#8A94A8"
BLUE = "#4FC3F7"
RED = "#FF6E6E"
GREEN = "#69F0AE"
GOLD = "#FFD54F"
CMAP = "magma"


def find_contrast_seed(env_kwargs, start=0, max_tries=400):
    """Find a seed where EFE commits correctly and Planning commits wrong."""
    for seed in range(start, start + max_tries):
        env = TileworldEnv(**env_kwargs)
        efe = make_agent(EFEAgent, env, planning_horizon=HORIZON)
        np.random.seed(seed)
        ep_efe = run_recorded_episode(efe, env, agent_name="EFE", seed=seed)

        env2 = TileworldEnv(**env_kwargs)
        plan = make_agent(PlanningAgent, env2, planning_horizon=HORIZON)
        np.random.seed(seed)
        ep_plan = run_recorded_episode(plan, env2, agent_name="Planning", seed=seed)

        n_efe = sum(1 for s in ep_efe.steps if s.action_type == "scan")
        n_plan = sum(1 for s in ep_plan.steps if s.action_type == "scan")
        if (
            ep_efe.success
            and not ep_plan.success
            and 6 <= n_efe <= 14
            and 4 <= n_plan <= 18
            and ep_efe.target_cell == ep_plan.target_cell
        ):
            return seed, ep_efe, ep_plan
    return None, None, None


def draw_grid(ax, belief, grid_size, scan_mask=None, commit_cell=None,
              target_cell=None, show_target=False, vmax=0.5):
    ax.clear()
    ax.set_facecolor(PANEL_BG)
    belief_grid = belief.reshape(grid_size, grid_size)
    ax.imshow(belief_grid, cmap=CMAP, vmin=0.0, vmax=vmax,
              interpolation="nearest", aspect="equal")

    for r in range(grid_size + 1):
        ax.axhline(r - 0.5, color="#2A3348", linewidth=1.0, zorder=2)
    for c in range(grid_size + 1):
        ax.axvline(c - 0.5, color="#2A3348", linewidth=1.0, zorder=2)

    if scan_mask is not None:
        for r in range(grid_size):
            for c in range(grid_size):
                if scan_mask[r, c]:
                    rect = mpatches.FancyBboxPatch(
                        (c - 0.46, r - 0.46), 0.92, 0.92,
                        boxstyle="round,pad=0.02",
                        linewidth=2.2, edgecolor=BLUE,
                        facecolor="none", zorder=3,
                    )
                    ax.add_patch(rect)

    if show_target and target_cell is not None:
        tr, tc = target_cell // grid_size, target_cell % grid_size
        ax.plot(tc, tr, marker="*", markersize=22, color=GREEN,
                markeredgecolor="black", markeredgewidth=1.0, zorder=5)

    if commit_cell is not None:
        cr, cc = commit_cell // grid_size, commit_cell % grid_size
        circle = plt.Circle((cc, cr), 0.42, fill=False,
                            edgecolor=RED, linewidth=3.0, zorder=5)
        ax.add_patch(circle)

    ax.set_xlim(-0.5, grid_size - 0.5)
    ax.set_ylim(grid_size - 0.5, -0.5)
    ax.set_xticks([])
    ax.set_yticks([])
    for spine in ax.spines.values():
        spine.set_color("#2A3348")


def build_frames(episode: TileworldEpisodeRecord):
    """One frame per step; hold final frame handled by caller."""
    frames = []
    for s in episode.steps:
        frames.append(s)
    return frames


def main():
    env_kwargs = dict(grid_size=GRID)
    seed, ep_efe, ep_plan = find_contrast_seed(env_kwargs)
    if seed is None:
        raise RuntimeError("No contrasting seed found")
    print(f"Using seed {seed}: EFE {ep_efe.total_reward:+.0f} (correct), "
          f"Planning {ep_plan.total_reward:+.0f} (wrong)")

    env = TileworldEnv(**env_kwargs)

    frames_efe = build_frames(ep_efe)
    frames_plan = build_frames(ep_plan)
    n_steps = max(len(frames_efe), len(frames_plan))
    HOLD_END = 10  # frames to hold the final result
    total_frames = n_steps + HOLD_END

    fig = plt.figure(figsize=(10.8, 7.2), dpi=100)
    fig.patch.set_facecolor(BG)

    gs = fig.add_gridspec(
        2, 2, height_ratios=[1.0, 0.16],
        left=0.06, right=0.94, top=0.80, bottom=0.05,
        wspace=0.18, hspace=0.24,
    )
    ax_plan = fig.add_subplot(gs[0, 0])
    ax_efe = fig.add_subplot(gs[0, 1])
    ax_bar_plan = fig.add_subplot(gs[1, 0])
    ax_bar_efe = fig.add_subplot(gs[1, 1])

    title = fig.text(
        0.5, 0.955, "Where is the hidden target?",
        ha="center", va="top", fontsize=21, color=FG, fontweight="bold",
    )
    subtitle = fig.text(
        0.5, 0.895,
        "Same maze. Same scans available. One agent values information. One doesn't.",
        ha="center", va="top", fontsize=12.5, color=DIM,
    )

    label_plan = fig.text(0.27, 0.845, "Reward-only planner",
                          ha="center", fontsize=14, color=BLUE, fontweight="bold")
    label_efe = fig.text(0.73, 0.845, "Active inference (EFE, w = 1)",
                         ha="center", fontsize=14, color=GOLD, fontweight="bold")

    status_plan = fig.text(0.27, 0.815, "", ha="center", fontsize=10.5, color=DIM)
    status_efe = fig.text(0.73, 0.815, "", ha="center", fontsize=10.5, color=DIM)

    fig.text(
        0.5, 0.012,
        "Spotlight, International Workshop on Active Inference (IWAI) 2026  |  "
        "Expected Free Energy as Belief-Dependent Utility for \u03c1-POMDPs",
        ha="center", va="bottom", fontsize=9, color=DIM,
    )

    max_h = np.log2(GRID * GRID)

    def entropy_bar(ax, belief, color):
        ax.clear()
        ax.set_facecolor(BG)
        h = float(scipy_entropy(belief, base=2))
        frac = h / max_h
        ax.barh([0], [1.0], color="#232B40", height=0.55)
        ax.barh([0], [frac], color=color, height=0.55)
        ax.set_xlim(0, 1)
        ax.set_ylim(-0.6, 0.6)
        ax.set_xticks([])
        ax.set_yticks([])
        for spine in ax.spines.values():
            spine.set_visible(False)
        ax.text(0.0, 0.85, "uncertainty", fontsize=9, color=DIM,
                transform=ax.transAxes, va="bottom")
        ax.text(1.0, 0.85, f"{h:.1f} bits", fontsize=9, color=FG,
                transform=ax.transAxes, va="bottom", ha="right")

    def frame_state(frames, ep, i):
        """Return (step_record, done) clamped to episode length."""
        if i < len(frames):
            return frames[i], (i == len(frames) - 1)
        return frames[-1], True

    def update(i):
        for frames, ep, ax, ax_bar, status, color in (
            (frames_plan, ep_plan, ax_plan, ax_bar_plan, status_plan, BLUE),
            (frames_efe, ep_efe, ax_efe, ax_bar_efe, status_efe, GOLD),
        ):
            rec, done = frame_state(frames, ep, i)
            scan_mask = None
            commit_cell = None
            if rec.action_type == "scan" and not (i >= len(frames)):
                scan_mask = env.get_scan_mask(rec.scan_idx)
            if rec.action_type == "commit":
                commit_cell = rec.action - env.num_scans

            show_target = done and rec.action_type == "commit"
            draw_grid(ax, rec.belief, GRID,
                      scan_mask=scan_mask,
                      commit_cell=commit_cell,
                      target_cell=ep.target_cell,
                      show_target=show_target,
                      vmax=0.5)
            entropy_bar(ax_bar, rec.belief, color)

            n_scans_so_far = sum(
                1 for s in frames[: min(i, len(frames) - 1) + 1]
                if s.action_type == "scan"
            )
            if done and rec.action_type == "commit":
                verdict = "CORRECT" if ep.success else "WRONG"
                vcolor = GREEN if ep.success else RED
                status.set_text(
                    f"scans: {n_scans_so_far}   reward: {ep.total_reward:+.0f}   {verdict}"
                )
                status.set_color(vcolor)
            else:
                status.set_text(
                    f"scans: {n_scans_so_far}   reward: {rec.cumulative_reward:+.0f}"
                )
                status.set_color(DIM)

        if i >= n_steps + 2:
            title.set_text("Curiosity has a price. Active inference sets it.")
            subtitle.set_text(
                "Expected Free Energy = reward + information gain at weight 1. "
                "Derived, not tuned."
            )
        else:
            title.set_text("Where is the hidden target?")
            subtitle.set_text(
                "Same maze. Same scans available. One agent values information. One doesn't."
            )
        return []

    anim = animation.FuncAnimation(
        fig, update, frames=total_frames, interval=650, blit=False,
    )

    out_dir = os.path.dirname(os.path.abspath(__file__))
    mp4_path = os.path.join(out_dir, "efe_vs_planning.mp4")
    gif_path = os.path.join(out_dir, "efe_vs_planning.gif")

    anim.save(mp4_path, writer=animation.FFMpegWriter(fps=1.6, bitrate=2400))
    print(f"Saved {mp4_path}")
    anim.save(gif_path, writer=animation.PillowWriter(fps=1.6))
    print(f"Saved {gif_path}")
    plt.close(fig)


if __name__ == "__main__":
    main()
