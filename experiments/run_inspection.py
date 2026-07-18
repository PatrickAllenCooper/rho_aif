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
from run_experiment import SEEDS


INSPECTION_CONFIGS = {
    "Inspection-N8": {
        "num_components": 8,
        "num_test_types": 2,
        "test_accuracies": [0.70, 0.90],
        "test_costs": [-0.5, -2.0],
        "fault_prior": 0.3,
        "correct_nominal_reward": 2.0,
        "correct_fault_reward": 5.0,
        "missed_fault_penalty": -50.0,
        "false_alarm_penalty": -5.0,
        "move_cost": -0.5,
        "tree_depth": 3,
        "max_steps": 200,
    },
    "Inspection-N16": {
        "num_components": 16,
        "num_test_types": 2,
        "test_accuracies": [0.70, 0.90],
        "test_costs": [-0.5, -2.0],
        "fault_prior": 0.3,
        "correct_nominal_reward": 2.0,
        "correct_fault_reward": 5.0,
        "missed_fault_penalty": -50.0,
        "false_alarm_penalty": -5.0,
        "move_cost": -0.5,
        "tree_depth": 2,
        "max_steps": 400,
    },
}


def run_inspection_episode(agent, env, seed=None):
    obs, info = env.reset(seed=seed)
    agent.reset()
    total_reward = 0.0
    num_tests = 0

    for _ in range(env.max_steps):
        action = agent.select_action()
        obs, reward, terminated, truncated, info = env.step(action)
        total_reward += reward
        agent.update(action, obs)

        if env.test_action_start <= action < env.diagnose_action_start:
            num_tests += 1

        if terminated or truncated:
            break

    return {
        "total_reward": total_reward,
        "correct": info.get("total_correct", 0),
        "missed": info.get("total_missed", 0),
        "false_alarm": info.get("total_false_alarm", 0),
        "components_diagnosed": info.get("components_diagnosed", 0),
        "all_diagnosed": info.get("all_diagnosed", False),
        "tests": num_tests,
        "steps": env._step_count,
    }


def run_inspection_experiment(config_name="Inspection-N8", num_episodes=200, seeds=None):
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
            "time_s": dt,
        }
        results.append(row)
        print(
            f"  {label:25s}: reward={row['mean_reward']:+.2f} +/- {row['se_reward']:.2f}  "
            f"acc={accuracy:.1%}  missed={row['mean_missed']:.2f}  "
            f"tests={row['mean_tests']:.1f}  complete={row['completion_rate']:.1%}  ({dt:.1f}s)"
        )

    df = pd.DataFrame(results)
    csv_name = f"results/results_inspection_n{nc}.csv"
    df.to_csv(csv_name, index=False)
    print(f"\nResults saved to {csv_name}")
    return df


if __name__ == "__main__":
    for config_name in INSPECTION_CONFIGS:
        run_inspection_experiment(config_name=config_name)
        print()
