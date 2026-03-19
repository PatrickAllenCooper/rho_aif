#!/usr/bin/env python3
"""
Pareto frontier experiment: sweep Planning+IG weight w across environments.

Demonstrates that EFE (= Planning+IG at w=1 by Proposition 1) sits near the
Pareto knee of the success-vs-reward tradeoff, providing a principled
canonical weight derived from the variational bound rather than per-environment
grid search.
"""

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from typing import Dict, List
import os

from environments.info_seeking import InfoSeekingEnv
from environments.tiger import TigerEnv
from environments.diagnosis import DiagnosisEnv
from environments.bandit import BanditEnv
from agents.planning_infogain import PlanningInfoGainAgent
from agents.efe import EFEAgent
from run_experiment import make_agent, run_experiment, summarize_results


def run_pareto_sweep(
    env,
    horizon: int,
    weights: List[float] = None,
    num_episodes: int = 500,
    seed: int = 42,
) -> Dict:
    """Sweep Planning+IG weight w, also run EFE for reference."""
    if weights is None:
        weights = [0.01, 0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 20.0, 50.0, 100.0, 200.0]

    sweep = {"w": [], "success": [], "reward": [], "obs": []}
    for w in weights:
        np.random.seed(seed)
        raw = run_experiment(PlanningInfoGainAgent, env, num_episodes,
                             planning_horizon=horizon, info_gain_weight=w)
        s = summarize_results(raw)
        sweep["w"].append(w)
        sweep["success"].append(s["success_rate"])
        sweep["reward"].append(s["mean_reward"])
        sweep["obs"].append(s["mean_observations"])
        print(f"    w={w:>6.2f}  success={s['success_rate']:.1%}  reward={s['mean_reward']:+.2f}")

    np.random.seed(seed)
    vfe_raw = run_experiment(EFEAgent, env, num_episodes, planning_horizon=horizon)
    vfe_s = summarize_results(vfe_raw)
    vfe = {"success": vfe_s["success_rate"], "reward": vfe_s["mean_reward"],
           "obs": vfe_s["mean_observations"]}
    print(f"    EFE     success={vfe['success']:.1%}  reward={vfe['reward']:+.2f}")

    return {"sweep": sweep, "vfe": vfe}


def plot_pareto(all_results: Dict, save_path: str = "figures/fig_pareto.pdf"):
    """4-panel Pareto frontier: success vs reward for each environment."""
    envs = list(all_results.keys())
    n = len(envs)
    fig, axes = plt.subplots(1, n, figsize=(3.2 * n, 3.5))
    if n == 1:
        axes = [axes]

    panel_labels = ["(a)", "(b)", "(c)", "(d)"]

    for idx, (env_name, ax) in enumerate(zip(envs, axes)):
        data = all_results[env_name]
        sw = data["sweep"]
        vfe = data["vfe"]

        succ = [s * 100 for s in sw["success"]]
        rew = sw["reward"]
        ws = sw["w"]

        ax.plot(succ, rew, color="#2196F3", lw=1.5, alpha=0.5, zorder=1)
        ax.scatter(succ, rew, c="#2196F3", s=30, zorder=2, edgecolors="white", linewidths=0.5)

        for i, w in enumerate(ws):
            if w in [0.01, 1.0, 10.0, 100.0]:
                offset = (5, 5) if w != 1.0 else (5, -12)
                ax.annotate(f"$w$={w:g}", (succ[i], rew[i]),
                            textcoords="offset points", xytext=offset,
                            fontsize=6, color="#2196F3", alpha=0.8)

        w1_idx = next((i for i, w in enumerate(ws) if abs(w - 1.0) < 0.01), None)
        if w1_idx is not None:
            ax.scatter([succ[w1_idx]], [rew[w1_idx]], c="#2196F3", s=100,
                       marker="D", zorder=4, edgecolors="black", linewidths=1.0)

        ax.scatter([vfe["success"] * 100], [vfe["reward"]], c="#D32F2F", s=120,
                   marker="*", zorder=5, edgecolors="black", linewidths=0.8)

        ax.set_xlabel("Success rate (%)", fontsize=9)
        if idx == 0:
            ax.set_ylabel("Mean reward", fontsize=9)
        ax.set_title(f"{panel_labels[idx]} {env_name}", fontsize=10)
        ax.grid(True, alpha=0.2)
        ax.tick_params(labelsize=8)

    from matplotlib.lines import Line2D
    legend_elements = [
        Line2D([0], [0], color="#2196F3", lw=1.5, marker="o", markersize=5,
               label="Planning+IG (sweep over $w$)"),
        Line2D([0], [0], color="#2196F3", marker="D", markersize=8, ls="none",
               markeredgecolor="black", label="Planning+IG $w{=}1$"),
        Line2D([0], [0], color="#D32F2F", marker="*", markersize=12, ls="none",
               markeredgecolor="black", label="EFE agent ($w{=}1$)"),
    ]
    fig.legend(handles=legend_elements, loc="lower center", ncol=3, fontsize=8,
               bbox_to_anchor=(0.5, -0.08))

    plt.tight_layout()
    plt.savefig(save_path, bbox_inches="tight", dpi=300)
    plt.close()
    print(f"  Saved {save_path}")


if __name__ == "__main__":
    os.makedirs("figures", exist_ok=True)

    envs_config = {
        "Tiger": (
            TigerEnv(listen_accuracy=0.85, listen_cost=1.0,
                     correct_reward=10.0, incorrect_penalty=-100.0),
            6
        ),
        "Testbed": (
            InfoSeekingEnv(observation_accuracy=0.75, observation_cost=0.1,
                           correct_reward=1.0, incorrect_penalty=-1.0),
            4
        ),
        "Diagnosis": (
            DiagnosisEnv(num_conditions=4, test_accuracy=0.80, test_cost=1.0,
                         correct_reward=10.0, incorrect_penalty=-50.0),
            3
        ),
        "Bandit": (
            BanditEnv(num_arms=4, inspect_accuracy=0.80, inspect_cost=0.5,
                      correct_reward=10.0, small_reward=1.0),
            2
        ),
    }

    all_results = {}
    for env_name, (env, horizon) in envs_config.items():
        print(f"\n{'=' * 60}")
        print(f"Pareto sweep: {env_name} (H={horizon})")
        print("=" * 60)
        all_results[env_name] = run_pareto_sweep(env, horizon, num_episodes=500)

    plot_pareto(all_results)
    print("\nPareto figure saved to figures/fig_pareto.pdf")
