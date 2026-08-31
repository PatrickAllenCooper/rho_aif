#!/usr/bin/env python3
"""
Monte Carlo study of near-optimality of w=1 across planning horizons.

For randomly generated two-state observe-then-commit environments, compute
the grid-search reward-optimal weight w* at each horizon H in {1, 2, 3} and
measure how often w=1 achieves >= 95% of optimal reward.

[Corrected 2026-08-31] This docstring previously promised H=1..5. The
committed battery (results/results_nearopt_horizon.csv) was run at
H in {1, 2, 3}, matching both manuscripts. The figure draws the three
measured horizons as unconnected markers over a light guide line so the
reader is not invited to interpolate a continuous trend beyond the
measured points.
"""

import argparse
import os
import sys
from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT))
sys.path.insert(0, str(_ROOT / "experiments"))

from rho_aif import figstyle
from rho_aif.environments.info_seeking import InfoSeekingEnv
from rho_aif.agents.planning_infogain import PlanningInfoGainAgent
from run_experiment import make_agent, run_episode

RESULTS_CSV = _ROOT / "results" / "results_nearopt_horizon.csv"


def evaluate_weight_fast(env, w, horizon, num_episodes=100, seed=42):
    """Run PlanningInfoGainAgent at given weight, return mean reward (no logging)."""
    np.random.seed(seed)
    agent = make_agent(PlanningInfoGainAgent, env,
                       planning_horizon=horizon, info_gain_weight=w)
    rewards = []
    for i in range(num_episodes):
        result = run_episode(agent, env, seed=seed * 10000 + i)
        rewards.append(result.total_reward)
    return np.mean(rewards)


def run_nearopt_study(
    num_envs=200,
    horizons=(1, 2, 3),
    weights=None,
    num_episodes=100,
    seed=42,
):
    if weights is None:
        weights = [0.01, 0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 50.0]

    rng = np.random.RandomState(seed)
    records = []

    for env_i in range(num_envs):
        alpha = rng.uniform(1.0, 50.0)
        p = rng.uniform(0.55, 0.95)
        cost = rng.uniform(0.1, 5.0)

        R_plus = 10.0
        R_minus = -alpha * R_plus

        env = InfoSeekingEnv(
            observation_accuracy=p,
            observation_cost=cost,
            correct_reward=R_plus,
            incorrect_penalty=R_minus,
        )

        if (env_i + 1) % 25 == 0:
            print(f"  Environment {env_i + 1}/{num_envs} "
                  f"(alpha={alpha:.1f}, p={p:.2f}, cost={cost:.1f})",
                  flush=True)

        for H in horizons:
            reward_by_w = {}
            for w in weights:
                r = evaluate_weight_fast(env, w, H, num_episodes,
                                         seed=seed + env_i * 100 + H)
                reward_by_w[w] = r

            best_w = max(reward_by_w, key=reward_by_w.get)
            best_reward = reward_by_w[best_w]
            w1_reward = reward_by_w.get(1.0, float("-inf"))

            gap = best_reward - w1_reward
            threshold = max(0.05 * abs(best_reward), 0.5)
            near_opt = gap <= threshold

            ratio = w1_reward / best_reward if abs(best_reward) > 0.01 else 1.0

            records.append({
                "env_id": env_i,
                "alpha": alpha,
                "p": p,
                "cost": cost,
                "horizon": H,
                "best_w": best_w,
                "best_reward": best_reward,
                "w1_reward": w1_reward,
                "ratio": ratio,
                "near_optimal": near_opt,
            })

    return pd.DataFrame(records)


def plot_nearopt(df, output_path="figures/fig_nearopt_horizon.pdf"):
    figstyle.apply()
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    alpha_bins = [
        (1, 3, "$\\alpha < 3$"),
        (3, 10, "$3 \\leq \\alpha < 10$"),
        (10, 51, "$\\alpha \\geq 10$"),
    ]

    # Authored at the printed width (0.7\linewidth of the JAIR text block)
    # so the rcParams point sizes are the printed sizes.
    fig, ax = plt.subplots(1, 1, figsize=figstyle.figsize(0.7, 0.63))
    horizons = sorted(df["horizon"].unique())
    markers = ["o", "^", "D"]

    def _frac_and_se(frame):
        """Proportion near-optimal (in %) and its binomial SE per horizon."""
        fracs, ses = [], []
        for h in horizons:
            hm = frame[frame["horizon"] == h]
            n = len(hm)
            p = hm["near_optimal"].mean() if n > 0 else 0.0
            fracs.append(p * 100)
            ses.append(100 * np.sqrt(p * (1 - p) / n) if n > 0 else 0.0)
        return fracs, ses

    # Only H in {1, 2, 3} was measured: draw unconnected markers with a
    # light guide line underneath so the points are not read as a trend.
    for (lo, hi, label), color, marker in zip(
            alpha_bins, figstyle.ENV_CYCLE, markers):
        sub = df[(df["alpha"] >= lo) & (df["alpha"] < hi)]
        n_envs = sub["env_id"].nunique()
        fracs, ses = _frac_and_se(sub)
        ax.plot(horizons, fracs, color=color, lw=1.0, alpha=0.3, zorder=1)
        ax.errorbar(horizons, fracs, yerr=ses, marker=marker, color=color,
                    linestyle="none", capsize=figstyle.CAPSIZE,
                    elinewidth=0.8, label=f"{label} ($n{{=}}{n_envs}$)",
                    zorder=3)

    all_fracs, all_ses = _frac_and_se(df)
    n_all = df["env_id"].nunique()
    ax.plot(horizons, all_fracs, color=figstyle.BLACK, lw=1.0, alpha=0.3,
            linestyle="--", zorder=1)
    ax.errorbar(horizons, all_fracs, yerr=all_ses, marker="s",
                color=figstyle.BLACK, linestyle="none",
                markerfacecolor="none", capsize=figstyle.CAPSIZE,
                elinewidth=0.8, label=f"All ($n{{=}}{n_all}$)", zorder=2)

    figstyle.style_axis(ax)
    ax.set_xlabel("Planning horizon $H$")
    ax.set_ylabel("$w{=}1$ near-optimal (% of environments)")
    ax.set_xticks(horizons)
    ax.set_xlim(0.85, 3.15)
    ax.set_ylim(0, 102)
    ax.legend(loc="lower right", title=r"Reward asymmetry $\alpha$")
    fig.tight_layout()
    fig.savefig(output_path)
    fig.savefig(output_path.with_suffix(".png"))
    print(f"  Saved {output_path} and {output_path.with_suffix('.png')}")
    plt.close(fig)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--replot", action="store_true",
        help="Rebuild the figure from the committed CSV without re-running "
             "any episodes.")
    args = parser.parse_args()

    os.makedirs("figures", exist_ok=True)

    if args.replot:
        df = pd.read_csv(RESULTS_CSV)
        plot_nearopt(df)
        sys.exit(0)

    print("Near-optimality Monte Carlo study")
    print("=" * 60)

    df = run_nearopt_study(
        num_envs=100, horizons=[1, 2, 3],
        num_episodes=50, weights=[0.01, 0.5, 1.0, 2.0, 5.0, 50.0],
    )
    df.to_csv("results/results_nearopt_horizon.csv", index=False)

    print("\nSummary by horizon:")
    for h in sorted(df["horizon"].unique()):
        sub = df[df["horizon"] == h]
        print(f"  H={h}: {sub['near_optimal'].mean():.1%} near-optimal "
              f"(mean ratio={sub['ratio'].mean():.3f})")

    print("\nBy alpha bin and horizon:")
    for lo, hi, label in [(1, 3, "alpha<3"), (3, 10, "3<=alpha<10"), (10, 51, "alpha>=10")]:
        mask = (df["alpha"] >= lo) & (df["alpha"] < hi)
        sub = df[mask]
        for h in sorted(df["horizon"].unique()):
            hm = sub[sub["horizon"] == h]
            if len(hm) > 0:
                print(f"  {label}, H={h}: {hm['near_optimal'].mean():.1%} ({len(hm)} envs)")

    plot_nearopt(df)
