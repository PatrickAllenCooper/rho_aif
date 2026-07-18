#!/usr/bin/env python3
"""
Discount factor experiment: test EFE and Planning agents with gamma < 1.

Verifies that the EFE-rho-POMDP equivalence holds under discounting and
measures sensitivity of performance to the discount factor.
"""

import numpy as np
import pandas as pd
import os

from rho_aif.environments.tiger import TigerEnv
from rho_aif.environments.diagnosis import DiagnosisEnv
from rho_aif.environments.bandit import BanditEnv
from rho_aif.agents.efe import EFEAgent
from rho_aif.agents.planning import PlanningAgent
from run_experiment import make_agent, run_experiment, summarize_results


def run_discount_sweep(seed=42, num_episodes=500):
    gammas = [0.9, 0.95, 0.99, 1.0]

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

    rows = []
    for env_name, (env, horizon) in envs.items():
        print(f"\n{'=' * 60}")
        print(f"Discount sweep: {env_name} (H={horizon})")
        print("=" * 60)

        for gamma in gammas:
            np.random.seed(seed)
            for agent_name, agent_cls in [("EFE", EFEAgent), ("Planning", PlanningAgent)]:
                raw = run_experiment(
                    agent_cls, env, num_episodes,
                    planning_horizon=horizon, discount=gamma,
                )
                s = summarize_results(raw)
                rows.append({
                    "env": env_name,
                    "agent": agent_name,
                    "gamma": gamma,
                    "success": s["success_rate"],
                    "reward": s["mean_reward"],
                    "obs": s["mean_observations"],
                })
                print(
                    f"  {agent_name:10s} gamma={gamma:.2f}  "
                    f"success={s['success_rate']:.1%}  "
                    f"reward={s['mean_reward']:+.3f}  "
                    f"obs={s['mean_observations']:.2f}"
                )

    df = pd.DataFrame(rows)
    df.to_csv("results/results_discount.csv", index=False)
    print(f"\nResults saved to results/results_discount.csv")
    return df


if __name__ == "__main__":
    os.makedirs("figures", exist_ok=True)
    df = run_discount_sweep()
    print("\n" + df.to_string(index=False))
