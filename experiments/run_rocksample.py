#!/usr/bin/env python3
"""
RockSample experiment: interleaved observe-act POMDP.

Demonstrates that EFE-based information gathering extends beyond
observe-then-commit POMDPs to settings with state transitions.
Uses proper depth-limited belief-space tree search agents.
"""

import numpy as np
import pandas as pd
import time
import os

from rho_aif.environments.rocksample import RockSampleEnv
from rho_aif.agents.rocksample_agents import (
    RockSampleGreedyAgent,
    RockSampleEFEAgent,
    RockSamplePlanningIGAgent,
    RockSamplePOMCPAgent,
    RockSampleTreeSearchAgent,
)
from run_experiment import SEEDS


ROCKSAMPLE_CONFIGS = {
    "RS[5,3]": {
        "grid_size": 5,
        "num_rocks": 3,
        "rock_positions": [(1, 2), (3, 1), (2, 4)],
        "tree_depth": 3,
    },
    "RS[7,4]": {
        "grid_size": 7,
        "num_rocks": 4,
        "rock_positions": [(2, 2), (4, 3), (1, 5), (5, 1)],
        "tree_depth": 4,
    },
    "RS[7,8]": {
        "grid_size": 7,
        "num_rocks": 8,
        "rock_positions": [
            (1, 1), (1, 4), (2, 2), (2, 6),
            (4, 1), (4, 5), (5, 3), (6, 6),
        ],
        "tree_depth": 3,
    },
    "RS[11,11]": {
        "grid_size": 11,
        "num_rocks": 11,
        "rock_positions": [
            (0, 3), (1, 7), (2, 1), (2, 9),
            (4, 4), (4, 8), (5, 0), (6, 6),
            (8, 2), (8, 10), (10, 5),
        ],
        "tree_depth": 2,
    },
}


def run_rocksample_episode(agent, env, seed=None, max_steps=100):
    obs, info = env.reset(seed=seed)
    agent.reset()
    total_reward = 0.0
    num_checks = 0

    for _ in range(max_steps):
        action = agent.select_action()
        obs, reward, terminated, truncated, info = env.step(action)
        total_reward += reward
        agent.update(action, obs)

        if env.NUM_MOVE_ACTIONS <= action < env.NUM_MOVE_ACTIONS + env.num_rocks:
            num_checks += 1

        if terminated or truncated:
            break

    return {
        "total_reward": total_reward,
        "good_sampled": info.get("total_good_sampled", 0),
        "bad_sampled": info.get("total_bad_sampled", 0),
        "steps": env._step_count,
        "checks": num_checks,
    }


def run_rocksample_experiment(
    config_name="RS[5,3]", num_episodes=500, seeds=None
):
    if seeds is None:
        seeds = SEEDS
    cfg = ROCKSAMPLE_CONFIGS[config_name]
    gs = cfg["grid_size"]
    nr = cfg["num_rocks"]
    rp = cfg["rock_positions"]
    td = cfg["tree_depth"]
    max_steps = gs * gs + nr * 10

    print(f"\n{config_name} (grid={gs}, rocks={nr}, depth={td}) -- "
          f"{num_episodes} episodes x {len(seeds)} seeds")
    print("=" * 70)

    env = RockSampleEnv(
        grid_size=gs,
        num_rocks=nr,
        rock_positions=rp,
        move_cost=-0.5,
        max_steps=max_steps,
    )

    agent_configs = [
        ("Greedy", lambda: RockSampleGreedyAgent(env)),
        ("POMCP (1000)", lambda: RockSamplePOMCPAgent(env, num_simulations=1000)),
        (f"Planning (d={td})",
         lambda: RockSampleTreeSearchAgent(env, info_weight=0.0, max_depth=td)),
        (f"Plan+IG w=5 (d={td})",
         lambda: RockSampleTreeSearchAgent(env, info_weight=5.0, max_depth=td)),
        (f"Plan+IG w=10 (d={td})",
         lambda: RockSampleTreeSearchAgent(env, info_weight=10.0, max_depth=td)),
        (f"EFE w=1 (d={td})",
         lambda: RockSampleTreeSearchAgent(env, info_weight=1.0, max_depth=td)),
    ]

    results = []
    for label, make_agent_fn in agent_configs:
        t0 = time.time()
        episode_results = []
        for seed in seeds:
            np.random.seed(seed)
            agent = make_agent_fn()
            for ep_i in range(num_episodes):
                r = run_rocksample_episode(
                    agent, env, seed=seed * 10000 + ep_i, max_steps=max_steps
                )
                episode_results.append(r)

        dt = time.time() - t0
        rewards = [r["total_reward"] for r in episode_results]
        goods = [r["good_sampled"] for r in episode_results]
        bads = [r["bad_sampled"] for r in episode_results]
        checks = [r["checks"] for r in episode_results]

        row = {
            "instance": config_name,
            "agent": label,
            "mean_reward": np.mean(rewards),
            "std_reward": np.std(rewards),
            "se_reward": np.std(rewards) / np.sqrt(len(rewards)),
            "mean_good": np.mean(goods),
            "mean_bad": np.mean(bads),
            "mean_checks": np.mean(checks),
            "mean_steps": np.mean([r["steps"] for r in episode_results]),
            "time_s": dt,
        }
        results.append(row)
        print(
            f"  {label:25s}: reward={row['mean_reward']:+.2f} +/- {row['se_reward']:.2f}  "
            f"good={row['mean_good']:.2f}  bad={row['mean_bad']:.2f}  "
            f"checks={row['mean_checks']:.1f}  steps={row['mean_steps']:.1f}  ({dt:.1f}s)"
        )

    df = pd.DataFrame(results)
    csv_name = f"results/results_rocksample_{gs}x{nr}.csv"
    df.to_csv(csv_name, index=False)
    print(f"\nResults saved to {csv_name}")
    return df


if __name__ == "__main__":
    for config_name in ROCKSAMPLE_CONFIGS:
        run_rocksample_experiment(config_name=config_name)
        print()
