#!/usr/bin/env python3
"""
Zero-shot transfer experiment: demonstrates that EFE's canonical w=1
generalizes across environments without retuning, while per-environment
tuned weights transfer poorly.

For each environment, we evaluate Planning+IG at:
  - w=1 (EFE canonical weight)
  - w* tuned on that environment
  - w* tuned on every OTHER environment (transfer)

The hypothesis: w=1 achieves near-Pareto-knee reward everywhere,
while transferred tuned weights fail catastrophically because optimal
weights vary by orders of magnitude across environments.
"""

import numpy as np
import pandas as pd
import time

from rho_aif.environments.tiger import TigerEnv
from rho_aif.environments.diagnosis import DiagnosisEnv
from rho_aif.environments.bandit import BanditEnv
from rho_aif.environments.info_seeking import InfoSeekingEnv
from run_experiment import (
    SEEDS, make_agent, run_episode, run_experiment_multi_seed,
    summarize_results, get_obs_models, make_env_config,
)
from rho_aif.agents.planning_infogain import PlanningInfoGainAgent

TRANSFER_ENVS = {
    "Tiger": {
        "make_env": lambda: TigerEnv(
            listen_accuracy=0.85,
            correct_reward=10.0,
            incorrect_penalty=-100.0,
            listen_cost=1.0,
        ),
        "horizon": 6,
        "w_star": 20,
    },
    "Diagnosis": {
        "make_env": lambda: DiagnosisEnv(
            num_conditions=4,
            test_accuracy=0.80,
            correct_reward=10.0,
            incorrect_penalty=-50.0,
            test_cost=1.0,
        ),
        "horizon": 3,
        "w_star": 100,
    },
    "Bandit": {
        "make_env": lambda: BanditEnv(
            num_arms=4,
            inspect_accuracy=0.80,
            correct_reward=10.0,
            small_reward=1.0,
            inspect_cost=0.5,
        ),
        "horizon": 2,
        "w_star": 100,
    },
    "Testbed": {
        "make_env": lambda: InfoSeekingEnv(
            observation_accuracy=0.75,
            correct_reward=1.0,
            incorrect_penalty=-1.0,
            observation_cost=0.1,
        ),
        "horizon": 4,
        "w_star": 50,
    },
}


def run_transfer_experiment(num_episodes=500, seeds=None):
    if seeds is None:
        seeds = SEEDS[:5]

    all_weights = set([1.0])
    for cfg in TRANSFER_ENVS.values():
        all_weights.add(float(cfg["w_star"]))

    results = []

    for env_name, env_cfg in TRANSFER_ENVS.items():
        env = env_cfg["make_env"]()
        horizon = env_cfg["horizon"]
        print(f"\nEvaluating on {env_name} (H={horizon}):")
        print("-" * 60)

        for w in sorted(all_weights):
            source_envs = []
            if w == 1.0:
                source_envs.append("EFE (canonical)")
            for src_name, src_cfg in TRANSFER_ENVS.items():
                if float(src_cfg["w_star"]) == w:
                    if src_name == env_name:
                        source_envs.append(f"tuned on {src_name} (native)")
                    else:
                        source_envs.append(f"tuned on {src_name} (transfer)")

            if not source_envs:
                continue

            source_label = "; ".join(source_envs)

            all_episode_results = run_experiment_multi_seed(
                PlanningInfoGainAgent,
                env,
                num_episodes=num_episodes,
                seeds=seeds,
                planning_horizon=horizon,
                info_gain_weight=w,
            )

            summary = summarize_results(all_episode_results)

            row = {
                "target_env": env_name,
                "weight": w,
                "source": source_label,
                "success_rate": summary["success_rate"],
                "mean_reward": summary["mean_reward"],
                "std_reward": summary["std_reward"],
                "se_reward": summary["std_reward"] / np.sqrt(len(all_episode_results)),
                "mean_observations": summary["mean_observations"],
            }
            results.append(row)
            print(
                f"  w={w:6.1f} [{source_label:40s}]: "
                f"success={row['success_rate']:.1%}  "
                f"reward={row['mean_reward']:+.2f} +/- {row['se_reward']:.2f}  "
                f"obs={row['mean_observations']:.1f}"
            )

    df = pd.DataFrame(results)
    df.to_csv("results/results_transfer.csv", index=False)
    print(f"\nResults saved to results/results_transfer.csv")
    return df


if __name__ == "__main__":
    run_transfer_experiment()
