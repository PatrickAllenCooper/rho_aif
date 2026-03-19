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
from run_experiment import make_agent, run_experiment, summarize_results


def run_pomcp_comparison(seed=42, num_episodes=500):
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

    sim_budgets = [500, 1000]

    for env_name, (env, horizon) in envs.items():
        print(f"\n{'=' * 60}")
        print(f"POMCP comparison: {env_name} (H={horizon})")
        print("=" * 60)

        np.random.seed(seed)
        print("  Running EFE...")
        t0 = time.time()
        efe_raw = run_experiment(EFEAgent, env, num_episodes, planning_horizon=horizon)
        efe_s = summarize_results(efe_raw)
        dt = time.time() - t0
        print(
            f"    EFE: success={efe_s['success_rate']:.1%}  "
            f"reward={efe_s['mean_reward']:+.3f}  "
            f"obs={efe_s['mean_observations']:.2f}  ({dt:.1f}s)"
        )

        np.random.seed(seed)
        print("  Running Planning...")
        t0 = time.time()
        plan_raw = run_experiment(PlanningAgent, env, num_episodes, planning_horizon=horizon)
        plan_s = summarize_results(plan_raw)
        dt = time.time() - t0
        print(
            f"    Planning: success={plan_s['success_rate']:.1%}  "
            f"reward={plan_s['mean_reward']:+.3f}  "
            f"obs={plan_s['mean_observations']:.2f}  ({dt:.1f}s)"
        )

        for n_sims in sim_budgets:
            np.random.seed(seed)
            print(f"  Running POMCP (sims={n_sims})...")
            t0 = time.time()
            pomcp_raw = run_experiment(
                POMCPAgent, env, num_episodes,
                num_simulations=n_sims,
                rollout_depth=horizon + 3,
                exploration_constant=5.0,
            )
            pomcp_s = summarize_results(pomcp_raw)
            dt = time.time() - t0
            print(
                f"    POMCP({n_sims}): success={pomcp_s['success_rate']:.1%}  "
                f"reward={pomcp_s['mean_reward']:+.3f}  "
                f"obs={pomcp_s['mean_observations']:.2f}  ({dt:.1f}s)"
            )

    print("\n" + "=" * 60)
    print("POMCP on Tileworld 6x6")
    print("=" * 60)
    env = TileworldEnv(grid_size=6, scan_accuracy=0.80, scan_cost=1.0,
                       correct_reward=10.0, incorrect_penalty=-50.0)
    horizon = 2

    np.random.seed(seed)
    print("  Running EFE...")
    t0 = time.time()
    efe_raw = run_experiment(EFEAgent, env, 200, planning_horizon=horizon)
    efe_s = summarize_results(efe_raw)
    dt = time.time() - t0
    print(
        f"    EFE: success={efe_s['success_rate']:.1%}  "
        f"reward={efe_s['mean_reward']:+.3f}  ({dt:.1f}s)"
    )

    np.random.seed(seed)
    print("  Running Planning...")
    t0 = time.time()
    plan_raw = run_experiment(PlanningAgent, env, 200, planning_horizon=horizon)
    plan_s = summarize_results(plan_raw)
    dt = time.time() - t0
    print(
        f"    Planning: success={plan_s['success_rate']:.1%}  "
        f"reward={plan_s['mean_reward']:+.3f}  ({dt:.1f}s)"
    )

    for n_sims in [500, 1000]:
        np.random.seed(seed)
        print(f"  Running POMCP (sims={n_sims})...")
        t0 = time.time()
        pomcp_raw = run_experiment(
            POMCPAgent, env, 200,
            num_simulations=n_sims,
            rollout_depth=horizon + 3,
            exploration_constant=5.0,
        )
        pomcp_s = summarize_results(pomcp_raw)
        dt = time.time() - t0
        print(
            f"    POMCP({n_sims}): success={pomcp_s['success_rate']:.1%}  "
            f"reward={pomcp_s['mean_reward']:+.3f}  ({dt:.1f}s)"
        )


if __name__ == "__main__":
    os.makedirs("figures", exist_ok=True)
    run_pomcp_comparison()
