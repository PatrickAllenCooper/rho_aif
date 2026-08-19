#!/usr/bin/env python3
"""
Structural Inspection experiment: factored observation POMDP for fault detection.

Demonstrates that EFE-based information gathering applies to domain-realistic
settings with multiple test types, spatial navigation, and asymmetric penalties.
"""

import numpy as np
import pandas as pd
import time
import os

from rho_aif.environments.inspection import InspectionEnv
from rho_aif.agents.inspection_agents import (
    InspectionTreeSearchAgent,
    InspectionGreedyAgent,
)
from rho_aif.benchmark import (
    INSPECTION_CONFIGS,
    run_inspection_episode,
)
from run_experiment import SEEDS


def run_inspection_experiment(config_name="Inspection-N8", num_episodes=500, seeds=None):
    if seeds is None:
        seeds = SEEDS
    cfg = INSPECTION_CONFIGS[config_name]
    td = cfg["tree_depth"]
    nc = cfg["num_components"]

    print(f"\n{config_name} (N={nc}, K={cfg['num_test_types']}, depth={td}) -- "
          f"{num_episodes} episodes x {len(seeds)} seeds")
    print("=" * 70)

    env = InspectionEnv(
        num_components=cfg["num_components"],
        num_test_types=cfg["num_test_types"],
        test_accuracies=cfg["test_accuracies"],
        test_costs=cfg["test_costs"],
        fault_prior=cfg["fault_prior"],
        correct_nominal_reward=cfg["correct_nominal_reward"],
        correct_fault_reward=cfg["correct_fault_reward"],
        missed_fault_penalty=cfg["missed_fault_penalty"],
        false_alarm_penalty=cfg["false_alarm_penalty"],
        move_cost=cfg["move_cost"],
        max_steps=cfg["max_steps"],
    )

    agent_configs = [
        ("Greedy", lambda: InspectionGreedyAgent(env)),
        (f"Planning (d={td})",
         lambda: InspectionTreeSearchAgent(env, info_weight=0.0, max_depth=td)),
        (f"Plan+IG w=5 (d={td})",
         lambda: InspectionTreeSearchAgent(env, info_weight=5.0, max_depth=td)),
        (f"EFE w=1 (d={td})",
         lambda: InspectionTreeSearchAgent(env, info_weight=1.0, max_depth=td)),
    ]

    results = []
    for label, make_agent_fn in agent_configs:
        t0 = time.time()
        episode_results = []
        for seed in seeds:
            np.random.seed(seed)
            agent = make_agent_fn()
            for ep_i in range(num_episodes):
                r = run_inspection_episode(
                    agent, env, seed=seed * 10000 + ep_i
                )
                episode_results.append(r)

            pct = len(episode_results) / (num_episodes * len(seeds)) * 100
            if pct % 25 < 100 / (num_episodes * len(seeds)) * 100 + 1:
                print(f"    {label}: {pct:.0f}% done...", flush=True)

        dt = time.time() - t0
        rewards = [r["total_reward"] for r in episode_results]
        corrects = [r["correct"] for r in episode_results]
        misseds = [r["missed"] for r in episode_results]
        false_alarms = [r["false_alarm"] for r in episode_results]
        tests = [r["tests"] for r in episode_results]
        all_diag = [r["all_diagnosed"] for r in episode_results]
        log_scores = [r["log_score"] for r in episode_results]
        briers = [r["brier_score"] for r in episode_results]

        accuracy = np.mean(corrects) / nc if nc > 0 else 0

        row = {
            "instance": config_name,
            "agent": label,
            "mean_reward": np.mean(rewards),
            "std_reward": np.std(rewards),
            "se_reward": np.std(rewards) / np.sqrt(len(rewards)),
            "accuracy": accuracy,
            "mean_correct": np.mean(corrects),
            "mean_missed": np.mean(misseds),
            "mean_false_alarm": np.mean(false_alarms),
            "mean_tests": np.mean(tests),
            "completion_rate": np.mean(all_diag),
            "mean_steps": np.mean([r["steps"] for r in episode_results]),
            "mean_log_score": np.mean(log_scores),
            "mean_brier": np.mean(briers),
            "time_s": dt,
        }
        results.append(row)
        print(
            f"  {label:25s}: reward={row['mean_reward']:+.2f} +/- {row['se_reward']:.2f}  "
            f"acc={accuracy:.1%}  log_score={row['mean_log_score']:+.3f}  "
            f"brier={row['mean_brier']:.3f}  tests={row['mean_tests']:.1f}  "
            f"complete={row['completion_rate']:.1%}  ({dt:.1f}s)"
        )

    os.makedirs("results", exist_ok=True)
    df = pd.DataFrame(results)
    from run_experiment import provenance_fields
    prov = provenance_fields(seeds, num_episodes)
    for k, v in prov.items():
        df[k] = v
    csv_name = f"results/results_inspection_n{nc}.csv"
    import os as _os
    _os.makedirs(_os.path.dirname(_os.path.abspath(csv_name)), exist_ok=True)
    df.to_csv(csv_name, index=False)
    print(f"\nResults saved to {csv_name}")
    return df


if __name__ == "__main__":
    for config_name in INSPECTION_CONFIGS:
        run_inspection_experiment(config_name=config_name)
        print()
