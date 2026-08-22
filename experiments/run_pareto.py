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

from rho_aif.environments.info_seeking import InfoSeekingEnv
from rho_aif.environments.tiger import TigerEnv
from rho_aif.environments.diagnosis import DiagnosisEnv
from rho_aif.environments.bandit import BanditEnv
from rho_aif.environments.tileworld import TileworldEnv
from rho_aif.agents.planning_infogain import PlanningInfoGainAgent
from rho_aif.agents.efe import EFEAgent
from run_experiment import (
    make_agent, run_experiment, run_experiment_multi_seed, summarize_results,
    provenance_fields, SEEDS,
)


def run_pareto_sweep(
    env,
    horizon: int,
    weights: List[float] = None,
    num_episodes: int = 500,
    seeds: List[int] = None,
) -> Dict:
    """Sweep Planning+IG weight w, also run EFE for reference."""
    if weights is None:
        weights = [0.01, 0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 20.0, 50.0, 100.0, 200.0]
    if seeds is None:
        seeds = SEEDS

    sweep = {"w": [], "success": [], "reward": [], "obs": [],
             "se_reward_seed_level": [], "se_success_seed_level": [], "n_seeds": []}
    for w in weights:
        raw = run_experiment_multi_seed(PlanningInfoGainAgent, env, num_episodes,
                                        seeds=seeds,
                                        planning_horizon=horizon, info_gain_weight=w)
        s = summarize_results(raw)
        sweep["w"].append(w)
        sweep["success"].append(s["success_rate"])
        sweep["reward"].append(s["mean_reward"])
        sweep["obs"].append(s["mean_observations"])
        sweep["se_reward_seed_level"].append(s.get("se_reward_seed_level", float("nan")))
        sweep["se_success_seed_level"].append(s.get("se_success_seed_level", float("nan")))
        sweep["n_seeds"].append(s.get("n_seeds", float("nan")))
        print(f"    w={w:>6.2f}  success={s['success_rate']:.1%}  reward={s['mean_reward']:+.2f}"
              f"  (seed SE {s.get('se_reward_seed_level', float('nan')):.3f})")

    efe_raw = run_experiment_multi_seed(EFEAgent, env, num_episodes, seeds=seeds,
                                        planning_horizon=horizon)
    efe_s = summarize_results(efe_raw)
    efe = {"success": efe_s["success_rate"], "reward": efe_s["mean_reward"],
           "obs": efe_s["mean_observations"]}
    print(f"    EFE     success={efe['success']:.1%}  reward={efe['reward']:+.2f}")

    return {"sweep": sweep, "efe": efe}


def plot_pareto(all_results: Dict, save_path: str = "figures/fig_pareto.pdf"):
    """4-panel Pareto frontier: success vs reward for each environment."""
    envs = list(all_results.keys())
    n = len(envs)
    fig, axes = plt.subplots(1, n, figsize=(3.2 * n, 3.5))
    if n == 1:
        axes = [axes]

    panel_labels = ["(a)", "(b)", "(c)", "(d)", "(e)", "(f)"]

    for idx, (env_name, ax) in enumerate(zip(envs, axes)):
        data = all_results[env_name]
        sw = data["sweep"]
        efe = data["efe"]

        succ = [s * 100 for s in sw["success"]]
        rew = sw["reward"]
        ws = sw["w"]

        ax.plot(succ, rew, color="#2196F3", lw=2.0, alpha=0.5, zorder=1)
        ax.scatter(succ, rew, c="#2196F3", s=60, zorder=2, edgecolors="white", linewidths=0.7)

        for i, w in enumerate(ws):
            if w in [0.01, 1.0, 10.0, 100.0]:
                if w == 1.0:
                    offset = (7, -14)
                elif w == 0.01:
                    offset = (-10, 8)
                elif w == 100.0:
                    offset = (-10, -12)
                else:
                    offset = (7, 7)
                ax.annotate(f"$w$={w:g}", (succ[i], rew[i]),
                            textcoords="offset points", xytext=offset,
                            fontsize=7, color="#2196F3", alpha=0.9,
                            fontweight="bold")

        w1_idx = next((i for i, w in enumerate(ws) if abs(w - 1.0) < 0.01), None)
        if w1_idx is not None:
            ax.scatter([succ[w1_idx]], [rew[w1_idx]], c="#2196F3", s=140,
                       marker="D", zorder=4, edgecolors="black", linewidths=1.2)

        ax.scatter([efe["success"] * 100], [efe["reward"]], c="#D32F2F", s=180,
                   marker="*", zorder=5, edgecolors="black", linewidths=1.0)

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


def run_accuracy_sensitivity(
    accuracies: List[float] = None,
    num_episodes: int = 500,
    seeds: List[int] = None,
    save_path: str = "figures/fig_accuracy_sensitivity.pdf",
):
    """Sweep observation accuracy and check w=1 knee persistence."""
    if accuracies is None:
        accuracies = [0.55, 0.60, 0.65, 0.70, 0.75, 0.80, 0.85]
    if seeds is None:
        seeds = SEEDS

    env_configs = {
        "Tiger": lambda acc: TigerEnv(listen_accuracy=acc, listen_cost=1.0,
                                       correct_reward=10.0, incorrect_penalty=-100.0),
        "Diagnosis": lambda acc: DiagnosisEnv(num_conditions=4, test_accuracy=acc, test_cost=1.0,
                                               correct_reward=10.0, incorrect_penalty=-50.0),
    }

    horizons = {"Tiger": 6, "Diagnosis": 3}
    weights = [0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 50.0]

    results = {}
    for env_name, make_env in env_configs.items():
        horizon = horizons[env_name]
        results[env_name] = {"accuracy": [], "w1_reward": [], "best_w": [], "best_reward": []}

        for acc in accuracies:
            env = make_env(acc)
            print(f"  {env_name} accuracy={acc:.2f}...")

            best_w_score = -float("inf")
            best_w = 1.0
            w1_reward = None

            for w in weights:
                raw = run_experiment_multi_seed(PlanningInfoGainAgent, env, num_episodes,
                                                seeds=seeds,
                                                planning_horizon=horizon, info_gain_weight=w)
                s = summarize_results(raw)
                if abs(w - 1.0) < 0.01:
                    w1_reward = s["mean_reward"]
                if s["mean_reward"] > best_w_score:
                    best_w_score = s["mean_reward"]
                    best_w = w

            results[env_name]["accuracy"].append(acc)
            results[env_name]["w1_reward"].append(w1_reward)
            results[env_name]["best_w"].append(best_w)
            results[env_name]["best_reward"].append(best_w_score)
            print(f"    w=1 reward={w1_reward:+.2f}  best_w={best_w}  best_reward={best_w_score:+.2f}")

    fig, axes = plt.subplots(1, 2, figsize=(10, 4))
    for idx, (env_name, data) in enumerate(results.items()):
        ax = axes[idx]
        ax.plot(data["accuracy"], data["w1_reward"], "o-", color="#D32F2F", lw=2, label="$w=1$ (EFE)")
        ax.plot(data["accuracy"], data["best_reward"], "s--", color="#2196F3", lw=2, label="Best $w$ (tuned)")
        ax.set_xlabel("Observation accuracy")
        ax.set_ylabel("Mean reward")
        ax.set_title(env_name)
        ax.legend(fontsize=8)
        ax.grid(True, alpha=0.2)

    plt.tight_layout()
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    plt.savefig(save_path, bbox_inches="tight", dpi=300)
    plt.close()
    print(f"  Saved {save_path}")
    return results


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
        "Tileworld": (
            TileworldEnv(grid_size=6),
            2
        ),
    }

    import sys
    cmd = sys.argv[1] if len(sys.argv) > 1 else "pareto"

    if cmd in ("pareto", "all"):
        all_results = {}
        for env_name, (env, horizon) in envs_config.items():
            print(f"\n{'=' * 60}")
            print(f"Pareto sweep: {env_name} (H={horizon})")
            print("=" * 60)
            all_results[env_name] = run_pareto_sweep(env, horizon, num_episodes=500)

        plot_pareto(all_results)
        print("\nPareto figure saved to figures/fig_pareto.pdf")

        # Persist the full sweep plus each environment's reward-maximizing
        # weight w*_ret and its seed-level SE, so Table tab:alpha_eta's
        # w*_ret column is traceable to a committed, regenerable CSV instead
        # of being an undocumented literal (Stage-K statistical audit finding).
        import pandas as pd
        sweep_rows = []
        summary_rows = []
        for env_name, data in all_results.items():
            sw = data["sweep"]
            for i, w in enumerate(sw["w"]):
                sweep_rows.append({
                    "env": env_name, "w": w, "success": sw["success"][i],
                    "reward": sw["reward"][i], "obs": sw["obs"][i],
                    "se_reward_seed_level": sw["se_reward_seed_level"][i],
                    "se_success_seed_level": sw["se_success_seed_level"][i],
                    "n_seeds": sw["n_seeds"][i],
                })
            best_idx = int(np.argmax(sw["reward"]))
            summary_rows.append({
                "env": env_name,
                "w_star_ret": sw["w"][best_idx],
                "reward_at_w_star_ret": sw["reward"][best_idx],
                "se_reward_seed_level_at_w_star_ret": sw["se_reward_seed_level"][best_idx],
                "success_at_w_star_ret": sw["success"][best_idx],
                "efe_reward": data["efe"]["reward"],
                "efe_success": data["efe"]["success"],
            })
        sweep_df = pd.DataFrame(sweep_rows)
        summary_df = pd.DataFrame(summary_rows)
        for df in (sweep_df, summary_df):
            prov = provenance_fields(SEEDS, 500)
            for k, v in prov.items():
                df[k] = v
        sweep_df.to_csv("results/results_pareto_sweep.csv", index=False)
        summary_df.to_csv("results/results_pareto_wstar.csv", index=False)
        print("\nSaved results/results_pareto_sweep.csv and results/results_pareto_wstar.csv")
        print(summary_df.to_string(index=False))

    if cmd in ("accuracy", "all"):
        print(f"\n{'=' * 60}")
        print("ACCURACY SENSITIVITY SWEEP")
        print("=" * 60)
        run_accuracy_sensitivity()
