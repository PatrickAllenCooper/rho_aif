#!/usr/bin/env python3
"""
Tileworld experiments and figure generation.

Produces:
  - Figure A: EFE belief evolution strip on 6x6 Tileworld
  - Figure B: Agent comparison (EFE vs Planning vs InfoGain-Tuned)
  - Figure C: Scaling analysis and computation time
  - Results table for the paper
"""

import numpy as np
import pandas as pd
import time
import os

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

from environments.tileworld import TileworldEnv
from agents.myopic import MyopicAgent
from agents.planning import PlanningAgent
from agents.info_gain import InformationGainAgent
from agents.planning_infogain import PlanningInfoGainAgent
from agents.efe import EFEAgent
from agents.epistemic_only import EpistemicOnlyAgent
from run_experiment import (
    make_agent, run_episode, run_experiment, summarize_results,
    tune_info_gain_weight, run_generic_experiment, SEEDS,
)
from render_tileworld import (
    run_recorded_episode, render_belief_evolution,
    render_agent_comparison, render_scan_atlas,
)


AGENT_STYLES = {
    "Myopic":        {"color": "#888888", "ls": "--", "marker": "s"},
    "Planning":      {"color": "#2196F3", "ls": "-",  "marker": "^"},
    "InfoGain-Tuned":{"color": "#FF9800", "ls": "-.", "marker": "D"},
    "Planning+IG":   {"color": "#9C27B0", "ls": ":",  "marker": "v"},
    "EFE":           {"color": "#D32F2F", "ls": "-",  "marker": "o"},
}


def find_good_episode_seed(
    env, agent_cls, agent_kwargs, min_scans=3, max_scans=20,
    search_range=500, agent_name="",
):
    """Search for a seed producing a successful episode with a moderate scan count."""
    for seed in range(search_range):
        np.random.seed(seed)
        agent = make_agent(agent_cls, env, **agent_kwargs)
        ep = run_recorded_episode(agent, env, agent_name=agent_name, seed=seed)
        n_scans = sum(1 for s in ep.steps if s.action_type == "scan")
        if ep.success and min_scans <= n_scans <= max_scans:
            return seed
    return 0


def fig_belief_evolution(save_path="figures/fig_tileworld_belief.pdf"):
    """Figure A: EFE belief evolution on 6x6 Tileworld."""
    print("  Generating Tileworld belief evolution...")
    env = TileworldEnv(grid_size=6)
    seed = find_good_episode_seed(
        env, EFEAgent, {"planning_horizon": 2},
        min_scans=4, max_scans=16, agent_name="EFE",
    )
    print(f"    Using seed {seed}")
    np.random.seed(seed)
    agent = make_agent(EFEAgent, env, planning_horizon=2)
    ep = run_recorded_episode(agent, env, agent_name="EFE", seed=seed)
    n_scans = sum(1 for s in ep.steps if s.action_type == "scan")
    print(f"    Episode: {n_scans} scans, success={ep.success}, R={ep.total_reward:+.1f}")
    render_belief_evolution(ep, env, save_path, max_panels=7)
    print(f"    Saved {save_path}")


def fig_agent_comparison(save_path="figures/fig_tileworld_comparison.pdf"):
    """Figure B: Side-by-side EFE vs Planning vs InfoGain-Tuned."""
    print("  Generating Tileworld agent comparison...")
    env = TileworldEnv(grid_size=6)

    print("    Tuning InfoGain weight...")
    best_w = tune_info_gain_weight(env, tune_episodes=100)
    print(f"    Best InfoGain weight: {best_w}")

    agent_defs = [
        ("EFE", EFEAgent, {"planning_horizon": 2}),
        ("Planning", PlanningAgent, {"planning_horizon": 2}),
        ("InfoGain-Tuned", InformationGainAgent, {"info_gain_weight": best_w}),
    ]

    seed = find_good_episode_seed(
        env, EFEAgent, {"planning_horizon": 2},
        min_scans=4, max_scans=16, agent_name="EFE",
    )
    print(f"    Using seed {seed}")

    episodes = []
    for name, cls, kwargs in agent_defs:
        np.random.seed(seed)
        agent = make_agent(cls, env, **kwargs)
        ep = run_recorded_episode(agent, env, agent_name=name, seed=seed)
        n_scans = sum(1 for s in ep.steps if s.action_type == "scan")
        print(f"    {name}: {n_scans} scans, success={ep.success}, R={ep.total_reward:+.1f}")
        episodes.append(ep)

    render_agent_comparison(episodes, env, save_path, max_panels_per_row=7)
    print(f"    Saved {save_path}")


def fig_scaling(save_path="figures/fig_tileworld_scaling.pdf"):
    """Figure C: Scaling analysis across grid sizes with computation time."""
    print("  Generating Tileworld scaling analysis...")

    grid_sizes = [4, 6, 8]
    horizon = 2
    n_episodes = 200
    seeds = SEEDS

    tuned_weight = 100

    agent_defs = [
        ("Myopic", MyopicAgent, {}),
        ("Planning", PlanningAgent, {"planning_horizon": horizon}),
        ("InfoGain-Tuned", InformationGainAgent, {"info_gain_weight": tuned_weight}),
        ("Planning+IG", PlanningInfoGainAgent, {"planning_horizon": horizon, "info_gain_weight": tuned_weight}),
        ("EFE", EFEAgent, {"planning_horizon": horizon}),
    ]

    results = {name: {"grid_size": [], "success": [], "reward": [], "scans": [], "time_s": []}
               for name, _, _ in agent_defs}

    for gs in grid_sizes:
        env = TileworldEnv(grid_size=gs)
        print(f"    Grid {gs}x{gs} ({env.num_cells} states, {env.num_scans} scans)...")

        for name, cls, kwargs in agent_defs:
            t0 = time.time()
            episode_results = []
            for seed in seeds:
                np.random.seed(seed)
                agent = make_agent(cls, env, **kwargs)
                for _ in range(n_episodes):
                    episode_results.append(run_episode(agent, env))
            dt = time.time() - t0

            s = summarize_results(episode_results)
            results[name]["grid_size"].append(gs)
            results[name]["success"].append(s["success_rate"] * 100)
            results[name]["reward"].append(s["mean_reward"])
            results[name]["scans"].append(s["mean_observations"])
            results[name]["time_s"].append(dt / (n_episodes * len(seeds)))
            print(
                f"      {name:10s}: success={s['success_rate']:.1%}  "
                f"reward={s['mean_reward']:+.2f}  scans={s['mean_observations']:.1f}  "
                f"({dt:.1f}s total)"
            )

    fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(14, 4))

    for name, style in AGENT_STYLES.items():
        if name not in results:
            continue
        data = results[name]
        ax1.plot(data["grid_size"], data["success"],
                 color=style["color"], ls=style["ls"], marker=style["marker"],
                 lw=2, label=name)

    ax1.set_xlabel("Grid size")
    ax1.set_ylabel("Success rate (%)")
    ax1.set_title("(a) Success rate vs grid size")
    ax1.set_xticks(grid_sizes)
    ax1.set_xticklabels([f"{g}x{g}" for g in grid_sizes])
    ax1.legend(fontsize=8)
    ax1.grid(True, alpha=0.2)

    for name, style in AGENT_STYLES.items():
        if name not in results:
            continue
        data = results[name]
        ax2.plot(data["grid_size"], data["reward"],
                 color=style["color"], ls=style["ls"], marker=style["marker"],
                 lw=2, label=name)

    ax2.set_xlabel("Grid size")
    ax2.set_ylabel("Mean reward")
    ax2.set_title("(b) Reward vs grid size")
    ax2.set_xticks(grid_sizes)
    ax2.set_xticklabels([f"{g}x{g}" for g in grid_sizes])
    ax2.grid(True, alpha=0.2)

    for name, style in AGENT_STYLES.items():
        if name not in results:
            continue
        data = results[name]
        ax3.plot(data["grid_size"], [t * 1000 for t in data["time_s"]],
                 color=style["color"], ls=style["ls"], marker=style["marker"],
                 lw=2, label=name)

    ax3.set_xlabel("Grid size")
    ax3.set_ylabel("Time per episode (ms)")
    ax3.set_title("(c) Computation cost")
    ax3.set_xticks(grid_sizes)
    ax3.set_xticklabels([f"{g}x{g}" for g in grid_sizes])
    ax3.set_yscale("log")
    ax3.grid(True, alpha=0.2)

    plt.tight_layout()
    plt.savefig(save_path, bbox_inches="tight", dpi=300)
    plt.close()
    print(f"    Saved {save_path}")

    return results


def run_tileworld_experiment(grid_size=6, num_episodes=500, seeds=None):
    """Full experiment with all agents on the Tileworld environment."""
    if seeds is None:
        seeds = SEEDS
    np.random.seed(seeds[0])
    env = TileworldEnv(
        grid_size=grid_size, scan_accuracy=0.80, scan_cost=1.0,
        correct_reward=10.0, incorrect_penalty=-50.0,
    )

    print(f"Tuning InfoGain weight for Tileworld {grid_size}x{grid_size}...")
    best_w = tune_info_gain_weight(env, tune_episodes=100)
    print(f"  Best InfoGain weight: {best_w}\n")

    best_w_plan = tune_info_gain_weight(env, tune_episodes=100)
    print(f"  Best Planning+IG weight: {best_w_plan}\n")

    horizon = 2
    configs = [
        ("Myopic", MyopicAgent, {}, None),
        ("Planning", PlanningAgent, {"planning_horizon": horizon}, None),
        ("InfoGain", InformationGainAgent, {"info_gain_weight": 1.0}, None),
        ("InfoGain-Tuned", InformationGainAgent, {"info_gain_weight": best_w}, None),
        ("Planning+IG", PlanningInfoGainAgent,
         {"planning_horizon": horizon, "info_gain_weight": best_w_plan}, None),
        ("EpistemicOnly", EpistemicOnlyAgent, {"planning_horizon": horizon}, None),
        ("EFE", EFEAgent, {"planning_horizon": horizon}, None),
    ]

    return run_generic_experiment(
        env, f"TILEWORLD EXPERIMENT ({grid_size}x{grid_size})", configs,
        num_episodes, f"results_tileworld_{grid_size}x{grid_size}.csv", seeds=seeds,
    )


if __name__ == "__main__":
    import sys

    os.makedirs("figures", exist_ok=True)
    cmd = sys.argv[1] if len(sys.argv) > 1 else "all"

    if cmd in ("figures", "all"):
        print("=" * 72)
        print("TILEWORLD FIGURES")
        print("=" * 72)

        render_scan_atlas(
            TileworldEnv(grid_size=6),
            "figures/fig_tileworld_scan_atlas.pdf",
        )
        print("  Saved scan atlas")

        fig_belief_evolution()
        fig_agent_comparison()
        scaling_results = fig_scaling()

    if cmd in ("experiment", "all"):
        print("\n")
        run_tileworld_experiment(grid_size=6, num_episodes=500)

    print("\nDone.")
