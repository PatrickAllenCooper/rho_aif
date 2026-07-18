#!/usr/bin/env python3
"""
Monte Carlo study of near-optimality of w=1 across planning horizons.

For randomly generated two-state observe-then-commit environments, compute
the exact reward-optimal weight w* at H=1..5 and measure how often w=1
achieves >= 95% of optimal reward.
"""

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import os

from rho_aif.environments.info_seeking import InfoSeekingEnv
from rho_aif.agents.planning_infogain import PlanningInfoGainAgent
from run_experiment import make_agent, run_episode


def evaluate_weight_fast(env, w, horizon, num_episodes=100, seed=42):
    """Run PlanningInfoGainAgent at given weight, return mean reward (no logging)."""
    np.random.seed(seed)
    agent = make_agent(PlanningInfoGainAgent, env,
                       planning_horizon=horizon, info_gain_weight=w)
    rewards = []
    for _ in range(num_episodes):
        result = run_episode(agent, env)
        rewards.append(result.total_reward)
    return np.mean(rewards)


def run_nearopt_study(
    num_envs=200,
    horizons=(1, 2, 3, 5),
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
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    alpha_bins = [
        (1, 3, "$\\alpha < 3$"),
        (3, 10, "$3 \\leq \\alpha < 10$"),
        (10, 51, "$\\alpha \\geq 10$"),
    ]

    fig, ax = plt.subplots(1, 1, figsize=(5, 3.5))
    horizons = sorted(df["horizon"].unique())
    colors = ["#E57373", "#64B5F6", "#81C784"]

    for (lo, hi, label), color in zip(alpha_bins, colors):
        mask = (df["alpha"] >= lo) & (df["alpha"] < hi)
        sub = df[mask]
        fracs = []
        for h in horizons:
            hm = sub[sub["horizon"] == h]
            fracs.append(hm["near_optimal"].mean() * 100 if len(hm) > 0 else 0)
        ax.plot(horizons, fracs, marker="o", label=label,
                color=color, linewidth=2, markersize=6)

    all_fracs = [df[df["horizon"] == h]["near_optimal"].mean() * 100 for h in horizons]
    ax.plot(horizons, all_fracs, marker="s", label="All", color="black",
            linewidth=2, markersize=6, linestyle="--")

    ax.set_xlabel("Planning horizon $H$")
    ax.set_ylabel("$w{=}1$ near-optimal (% of envs)")
    ax.set_xticks(horizons)
    ax.set_ylim(0, 102)
    ax.legend(fontsize=8, loc="upper left")
    ax.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(output_path, bbox_inches="tight")
    print(f"  Saved {output_path}")
    plt.close()


if __name__ == "__main__":
    os.makedirs("figures", exist_ok=True)

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
