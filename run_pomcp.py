#!/usr/bin/env python3
"""
POMCP baseline comparison experiment.

Runs POMCP (Silver & Veness, 2010) on Tiger, Diagnosis, Bandit, and Tileworld
to compare against EFE and Planning baselines.
"""

import numpy as np
import time
import os

from environments.tiger import TigerEnv
from environments.diagnosis import DiagnosisEnv
from environments.bandit import BanditEnv
from environments.tileworld import TileworldEnv
from agents.pomcp import POMCPAgent
from agents.efe import EFEAgent
from agents.planning import PlanningAgent
from run_experiment import make_agent, run_experiment, run_experiment_multi_seed, summarize_results, SEEDS


def run_pomcp_comparison(seeds=None, num_episodes=500):
    if seeds is None:
        seeds = SEEDS

    envs = {
        "Tiger": (
            TigerEnv(listen_accuracy=0.85, listen_cost=1.0,
                     correct_reward=10.0, incorrect_penalty=-100.0),
            6,
        ),
        "Diagnosis": (
            DiagnosisEnv(num_conditions=4, test_accuracy=0.80, test_cost=1.0,
                         correct_reward=10.0, incorrect_penalty=-50.0),
            3,
        ),
        "Bandit": (
            BanditEnv(num_arms=4, inspect_accuracy=0.80, inspect_cost=0.5,
                      correct_reward=10.0, small_reward=1.0),
            2,
        ),
    }

    sim_budgets = [500, 1000, 2000, 5000]

    for env_name, (env, horizon) in envs.items():
        print(f"\n{'=' * 60}")
        print(f"POMCP comparison: {env_name} (H={horizon}, {len(seeds)} seeds)")
        print("=" * 60)

        print("  Running EFE...")
        t0 = time.time()
        efe_raw = run_experiment_multi_seed(EFEAgent, env, num_episodes, seeds=seeds, planning_horizon=horizon)
        efe_s = summarize_results(efe_raw)
        efe_time = time.time() - t0
        efe_per_decision = efe_time / len(efe_raw)
        print(
            f"    EFE: success={efe_s['success_rate']:.1%}  "
            f"reward={efe_s['mean_reward']:+.3f}  "
            f"obs={efe_s['mean_observations']:.2f}  ({efe_time:.1f}s, {efe_per_decision*1000:.1f}ms/ep)"
        )

        print("  Running Planning...")
        t0 = time.time()
        plan_raw = run_experiment_multi_seed(PlanningAgent, env, num_episodes, seeds=seeds, planning_horizon=horizon)
        plan_s = summarize_results(plan_raw)
        plan_time = time.time() - t0
        print(
            f"    Planning: success={plan_s['success_rate']:.1%}  "
            f"reward={plan_s['mean_reward']:+.3f}  "
            f"obs={plan_s['mean_observations']:.2f}  ({plan_time:.1f}s)"
        )

        for n_sims in sim_budgets:
            print(f"  Running POMCP (sims={n_sims})...")
            t0 = time.time()
            pomcp_raw = run_experiment_multi_seed(
                POMCPAgent, env, num_episodes, seeds=seeds,
                num_simulations=n_sims,
                rollout_depth=horizon + 3,
                exploration_constant=5.0,
            )
            pomcp_s = summarize_results(pomcp_raw)
            pomcp_time = time.time() - t0
            pomcp_per_decision = pomcp_time / len(pomcp_raw)
            print(
                f"    POMCP({n_sims}): success={pomcp_s['success_rate']:.1%}  "
                f"reward={pomcp_s['mean_reward']:+.3f}  "
                f"obs={pomcp_s['mean_observations']:.2f}  "
                f"({pomcp_time:.1f}s, {pomcp_per_decision*1000:.1f}ms/ep)"
            )

    print("\n" + "=" * 60)
    print("POMCP on Tileworld 6x6")
    print("=" * 60)
    env = TileworldEnv(grid_size=6, scan_accuracy=0.80, scan_cost=1.0,
                       correct_reward=10.0, incorrect_penalty=-50.0)
    horizon = 2

    print("  Running EFE...")
    t0 = time.time()
    efe_raw = run_experiment_multi_seed(EFEAgent, env, 200, seeds=seeds, planning_horizon=horizon)
    efe_s = summarize_results(efe_raw)
    efe_time = time.time() - t0
    print(
        f"    EFE: success={efe_s['success_rate']:.1%}  "
        f"reward={efe_s['mean_reward']:+.3f}  ({efe_time:.1f}s)"
    )

    print("  Running Planning...")
    t0 = time.time()
    plan_raw = run_experiment_multi_seed(PlanningAgent, env, 200, seeds=seeds, planning_horizon=horizon)
    plan_s = summarize_results(plan_raw)
    plan_time = time.time() - t0
    print(
        f"    Planning: success={plan_s['success_rate']:.1%}  "
        f"reward={plan_s['mean_reward']:+.3f}  ({plan_time:.1f}s)"
    )

    for n_sims in [500, 1000, 2000, 5000]:
        print(f"  Running POMCP (sims={n_sims})...")
        t0 = time.time()
        pomcp_raw = run_experiment_multi_seed(
            POMCPAgent, env, 200, seeds=seeds,
            num_simulations=n_sims,
            rollout_depth=horizon + 3,
            exploration_constant=5.0,
        )
        pomcp_s = summarize_results(pomcp_raw)
        pomcp_time = time.time() - t0
        print(
            f"    POMCP({n_sims}): success={pomcp_s['success_rate']:.1%}  "
            f"reward={pomcp_s['mean_reward']:+.3f}  ({pomcp_time:.1f}s)"
        )


if __name__ == "__main__":
    os.makedirs("figures", exist_ok=True)
    run_pomcp_comparison()
