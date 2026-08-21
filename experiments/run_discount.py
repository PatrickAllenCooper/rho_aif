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
from rho_aif.stats import cohens_d, holm_bonferroni, seed_level_ttest
from run_experiment import SEEDS, provenance_fields, run_experiment_multi_seed, summarize_results


def run_discount_sweep(seeds=None, num_episodes=500):
    if seeds is None:
        seeds = SEEDS
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
    stats_rows = []
    for env_name, (env, horizon) in envs.items():
        print(f"\n{'=' * 60}")
        print(f"Discount sweep: {env_name} (H={horizon})")
        print("=" * 60)

        for gamma in gammas:
            raw_by_agent = {}
            for agent_name, agent_cls in [("EFE", EFEAgent), ("Planning", PlanningAgent)]:
                raw = run_experiment_multi_seed(
                    agent_cls, env, num_episodes,
                    seeds=seeds,
                    planning_horizon=horizon, discount=gamma,
                )
                raw_by_agent[agent_name] = raw
                s = summarize_results(raw)
                row = {
                    "env": env_name,
                    "agent": agent_name,
                    "gamma": gamma,
                    "success": s["success_rate"],
                    "reward": s["mean_reward"],
                    "obs": s["mean_observations"],
                    "se_reward_pooled": s["se_reward_pooled"],
                    "se_reward_seed_level": s["se_reward_seed_level"],
                    "se_success_seed_level": s["se_success_seed_level"],
                    "n_seeds": s["n_seeds"],
                }
                row.update(provenance_fields(seeds, num_episodes))
                rows.append(row)
                print(
                    f"  {agent_name:10s} gamma={gamma:.2f}  "
                    f"success={s['success_rate']:.1%}  "
                    f"reward={s['mean_reward']:+.3f} +/- {s['se_reward_seed_level']:.3f}(seed)  "
                    f"obs={s['mean_observations']:.2f}"
                )

            for metric_name, extractor in [
                ("Reward", lambda r: r.total_reward),
                ("Success", lambda r: float(r.success)),
            ]:
                seed_out = seed_level_ttest(raw_by_agent["EFE"], raw_by_agent["Planning"], extractor)
                stats_rows.append({
                    "env": env_name,
                    "gamma": gamma,
                    "metric": metric_name,
                    "diff": seed_out["mean_of_seed_means_a"] - seed_out["mean_of_seed_means_b"],
                    "p_seed_level": seed_out["p_value"],
                    "cohens_d_seed_level": seed_out["cohens_d"],
                    "n_seeds": seed_out["n_seeds_a"],
                })

    p_list = [r["p_seed_level"] for r in stats_rows]
    for r, sig in zip(stats_rows, holm_bonferroni(p_list)):
        r["significant_hb_seed_level"] = sig

    df = pd.DataFrame(rows)
    df.to_csv("results/results_discount.csv", index=False)
    stats_df = pd.DataFrame(stats_rows)
    stats_df.to_csv("results/results_discount_stats.csv", index=False)
    print(f"\nResults saved to results/results_discount.csv")
    print(f"Statistics saved to results/results_discount_stats.csv")
    return df


if __name__ == "__main__":
    os.makedirs("figures", exist_ok=True)
    df = run_discount_sweep()
    print("\n" + df.to_string(index=False))
