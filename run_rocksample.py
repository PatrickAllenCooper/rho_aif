#!/usr/bin/env python3
"""
RockSample experiment: interleaved observe-act POMDP.

Demonstrates that EFE-based information gathering extends beyond
observe-then-commit POMDPs to settings with state transitions.
"""

import numpy as np
import pandas as pd
import time
import os

from environments.rocksample import RockSampleEnv
from agents.rocksample_agents import (
    RockSampleGreedyAgent,
    RockSampleEFEAgent,
)


def run_rocksample_episode(agent, env, max_steps=100):
    obs, info = env.reset()
    agent.reset()
    total_reward = 0.0

    for _ in range(max_steps):
        action = agent.select_action()
        obs, reward, terminated, truncated, info = env.step(action)
        total_reward += reward
        agent.update(action, obs)

        if terminated or truncated:
            break

    return {
        "total_reward": total_reward,
        "good_sampled": info.get("total_good_sampled", 0),
        "bad_sampled": info.get("total_bad_sampled", 0),
        "steps": env._step_count,
    }


def run_rocksample_experiment(
    grid_size=5, num_rocks=3, num_episodes=500, seed=42
):
    print(f"RockSample[{grid_size},{num_rocks}] -- {num_episodes} episodes")
    print("=" * 60)

    rock_positions = []
    np.random.seed(seed)
    positions = set()
    while len(positions) < num_rocks:
        r = np.random.randint(0, grid_size)
        c = np.random.randint(0, grid_size)
        positions.add((r, c))
    rock_positions = list(positions)

    env = RockSampleEnv(
        grid_size=grid_size,
        num_rocks=num_rocks,
        rock_positions=rock_positions,
        max_steps=grid_size * grid_size + num_rocks * 5,
    )

    agent_configs = [
        ("Greedy", lambda: RockSampleGreedyAgent(env)),
        ("EFE (w=1)", lambda: RockSampleEFEAgent(env, info_weight=1.0)),
        ("EFE (w=5)", lambda: RockSampleEFEAgent(env, info_weight=5.0)),
        ("EFE (w=10)", lambda: RockSampleEFEAgent(env, info_weight=10.0)),
    ]

    results = []
    for label, make_agent in agent_configs:
        np.random.seed(seed)
        agent = make_agent()
        t0 = time.time()
        episode_results = []

        for _ in range(num_episodes):
            r = run_rocksample_episode(agent, env)
            episode_results.append(r)

        dt = time.time() - t0
        rewards = [r["total_reward"] for r in episode_results]
        goods = [r["good_sampled"] for r in episode_results]
        bads = [r["bad_sampled"] for r in episode_results]

        row = {
            "agent": label,
            "mean_reward": np.mean(rewards),
            "std_reward": np.std(rewards),
            "mean_good": np.mean(goods),
            "mean_bad": np.mean(bads),
            "mean_steps": np.mean([r["steps"] for r in episode_results]),
            "time_s": dt,
        }
        results.append(row)
        print(
            f"  {label:15s}: reward={row['mean_reward']:+.2f} +/- {row['std_reward']:.2f}  "
            f"good={row['mean_good']:.2f}  bad={row['mean_bad']:.2f}  "
            f"steps={row['mean_steps']:.1f}  ({dt:.1f}s)"
        )

    df = pd.DataFrame(results)
    csv_name = f"results_rocksample_{grid_size}x{num_rocks}.csv"
    df.to_csv(csv_name, index=False)
    print(f"\nResults saved to {csv_name}")
    return df


if __name__ == "__main__":
    for gs, nr in [(5, 3), (7, 4)]:
        run_rocksample_experiment(grid_size=gs, num_rocks=nr)
        print()
