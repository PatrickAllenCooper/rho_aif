#!/usr/bin/env python3
"""
Generate supplementary material: bootstrap CIs, Cohen's d, and
Holm-Bonferroni-corrected p-values for all environments.

Runs experiments with multi-seed support and produces CSV tables
and LaTeX-formatted output for the paper appendix.
"""

import numpy as np
import pandas as pd
from typing import List, Dict

from rho_aif.environments.info_seeking import InfoSeekingEnv
from rho_aif.environments.tiger import TigerEnv
from rho_aif.environments.diagnosis import DiagnosisEnv
from rho_aif.environments.bandit import BanditEnv
from rho_aif.agents.myopic import MyopicAgent
from rho_aif.agents.planning import PlanningAgent
from rho_aif.agents.info_gain import InformationGainAgent
from rho_aif.agents.planning_infogain import PlanningInfoGainAgent
from rho_aif.agents.epistemic_only import EpistemicOnlyAgent
from rho_aif.agents.efe import EFEAgent
from rho_aif.agents.thompson import ThompsonSamplingAgent
from run_experiment import (
    make_agent, run_episode, run_experiment, run_experiment_multi_seed,
    summarize_results, tune_info_gain_weight, EpisodeResult,
    compute_full_statistics, SEEDS,
)
from rho_aif.stats import bootstrap_ci, cohens_d


def run_env_with_stats(env, env_name, agent_configs, num_episodes=1000, seeds=None):
    """Run all agents on an environment across multiple seeds and return raw results."""
    if seeds is None:
        seeds = SEEDS
    all_raw = {}

    for label, agent_class, kwargs in agent_configs:
        results = run_experiment_multi_seed(
            agent_class, env, num_episodes, seeds=seeds, **kwargs
        )
        all_raw[label] = results
        s = summarize_results(results)
        print(f"  {label:18s}: obs={s['mean_observations']:.2f}  "
              f"success={s['success_rate']:.1%}  reward={s['mean_reward']:+.3f}"
              f"  ({len(seeds)} seeds x {num_episodes} ep = {len(results)} total)")

    return all_raw


def generate_bootstrap_table(all_raw, env_name):
    """Generate a table with point estimates and 95% bootstrap CIs."""
    rows = []
    for label, results in all_raw.items():
        rewards = np.array([r.total_reward for r in results])
        successes = np.array([float(r.success) for r in results])
        obs = np.array([r.num_observations for r in results])

        r_mean, r_lo, r_hi = bootstrap_ci(rewards)
        s_mean, s_lo, s_hi = bootstrap_ci(successes)
        o_mean, o_lo, o_hi = bootstrap_ci(obs)

        rows.append({
            "Environment": env_name,
            "Agent": label,
            "Reward": f"{r_mean:+.2f}",
            "Reward CI": f"[{r_lo:+.2f}, {r_hi:+.2f}]",
            "Success": f"{s_mean:.1%}",
            "Success CI": f"[{s_lo:.1%}, {s_hi:.1%}]",
            "Obs": f"{o_mean:.2f}",
            "Obs CI": f"[{o_lo:.2f}, {o_hi:.2f}]",
        })
    return pd.DataFrame(rows)


def generate_effect_size_table(all_raw, env_name):
    """Cohen's d for EFE vs each baseline on reward metric."""
    if "EFE" not in all_raw:
        return pd.DataFrame()

    efe_rewards = np.array([r.total_reward for r in all_raw["EFE"]])
    rows = []
    for label, results in all_raw.items():
        if label == "EFE":
            continue
        other_rewards = np.array([r.total_reward for r in results])
        d = cohens_d(efe_rewards, other_rewards)
        interpretation = (
            "negligible" if abs(d) < 0.2 else
            "small" if abs(d) < 0.5 else
            "medium" if abs(d) < 0.8 else
            "large"
        )
        rows.append({
            "Environment": env_name,
            "Comparison": f"EFE vs {label}",
            "Cohen's d": f"{d:+.3f}",
            "Effect": interpretation,
        })
    return pd.DataFrame(rows)


def main():
    seeds = SEEDS
    num_episodes = 1000

    tuned_weights = []
    all_bootstrap_rows = []
    all_effect_rows = []
    all_stats_dfs = []

    # Tiger
    print("=" * 60)
    print(f"Tiger (H=6, {num_episodes} ep x {len(seeds)} seeds)")
    print("=" * 60)
    np.random.seed(seeds[0])
    tiger_env = TigerEnv(listen_accuracy=0.85, listen_cost=1.0,
                         correct_reward=10.0, incorrect_penalty=-100.0)
    best_w = tune_info_gain_weight(tiger_env, tune_episodes=200)
    best_w_pig = tune_info_gain_weight(
        tiger_env, tune_episodes=200,
        agent_class=PlanningInfoGainAgent,
        agent_kwargs={"planning_horizon": 6},
    )
    tuned_weights.append({"env": "tiger_env", "planning_horizon": 6,
                          "w_succ_infogain_myopic": float(best_w),
                          "w_succ_planning_ig": float(best_w_pig)})
    tiger_configs = [
        ("Myopic", MyopicAgent, {}),
        ("Planning", PlanningAgent, {"planning_horizon": 6}),
        ("InfoGain-Tuned", InformationGainAgent, {"info_gain_weight": best_w}),
        ("Planning+IG", PlanningInfoGainAgent, {"planning_horizon": 6, "info_gain_weight": best_w_pig}),
        ("EFE", EFEAgent, {"planning_horizon": 6}),
        ("Thompson", ThompsonSamplingAgent, {"num_samples": 100}),
    ]
    tiger_raw = run_env_with_stats(tiger_env, "Tiger", tiger_configs, num_episodes, seeds)
    all_bootstrap_rows.append(generate_bootstrap_table(tiger_raw, "Tiger"))
    all_effect_rows.append(generate_effect_size_table(tiger_raw, "Tiger"))
    all_stats_dfs.append(compute_full_statistics(tiger_raw, "Tiger"))

    # Testbed
    print("\n" + "=" * 60)
    print(f"Testbed (H=4, {num_episodes} ep x {len(seeds)} seeds)")
    print("=" * 60)
    np.random.seed(seeds[0])
    testbed_env = InfoSeekingEnv(observation_accuracy=0.75, observation_cost=0.1,
                                correct_reward=1.0, incorrect_penalty=-1.0)
    best_w_tb = tune_info_gain_weight(testbed_env, tune_episodes=200)
    best_w_tb_pig = tune_info_gain_weight(
        testbed_env, tune_episodes=200,
        agent_class=PlanningInfoGainAgent,
        agent_kwargs={"planning_horizon": 4},
    )
    tuned_weights.append({"env": "testbed_env", "planning_horizon": 4,
                          "w_succ_infogain_myopic": float(best_w_tb),
                          "w_succ_planning_ig": float(best_w_tb_pig)})
    testbed_configs = [
        ("Myopic", MyopicAgent, {}),
        ("Planning", PlanningAgent, {"planning_horizon": 4}),
        ("InfoGain-Tuned", InformationGainAgent, {"info_gain_weight": best_w_tb}),
        ("Planning+IG", PlanningInfoGainAgent, {"planning_horizon": 4, "info_gain_weight": best_w_tb_pig}),
        ("EFE", EFEAgent, {"planning_horizon": 4}),
        ("Thompson", ThompsonSamplingAgent, {"num_samples": 100}),
    ]
    testbed_raw = run_env_with_stats(testbed_env, "Testbed", testbed_configs, num_episodes, seeds)
    all_bootstrap_rows.append(generate_bootstrap_table(testbed_raw, "Testbed"))
    all_effect_rows.append(generate_effect_size_table(testbed_raw, "Testbed"))
    all_stats_dfs.append(compute_full_statistics(testbed_raw, "Testbed"))

    # Diagnosis
    print("\n" + "=" * 60)
    print(f"Diagnosis (N=4, H=3, {num_episodes} ep x {len(seeds)} seeds)")
    print("=" * 60)
    np.random.seed(seeds[0])
    diag_env = DiagnosisEnv(num_conditions=4, test_accuracy=0.80, test_cost=1.0,
                            correct_reward=10.0, incorrect_penalty=-50.0)
    best_w_d = tune_info_gain_weight(diag_env, tune_episodes=200)
    best_w_d_pig = tune_info_gain_weight(
        diag_env, tune_episodes=200,
        agent_class=PlanningInfoGainAgent,
        agent_kwargs={"planning_horizon": 3},
    )
    tuned_weights.append({"env": "diag_env", "planning_horizon": 3,
                          "w_succ_infogain_myopic": float(best_w_d),
                          "w_succ_planning_ig": float(best_w_d_pig)})
    diag_configs = [
        ("Myopic", MyopicAgent, {}),
        ("Planning", PlanningAgent, {"planning_horizon": 3}),
        ("InfoGain-Tuned", InformationGainAgent, {"info_gain_weight": best_w_d}),
        ("Planning+IG", PlanningInfoGainAgent, {"planning_horizon": 3, "info_gain_weight": best_w_d_pig}),
        ("EFE", EFEAgent, {"planning_horizon": 3}),
        ("Thompson", ThompsonSamplingAgent, {"num_samples": 100}),
    ]
    diag_raw = run_env_with_stats(diag_env, "Diagnosis", diag_configs, num_episodes, seeds)
    all_bootstrap_rows.append(generate_bootstrap_table(diag_raw, "Diagnosis"))
    all_effect_rows.append(generate_effect_size_table(diag_raw, "Diagnosis"))
    all_stats_dfs.append(compute_full_statistics(diag_raw, "Diagnosis"))

    # Bandit
    print("\n" + "=" * 60)
    print(f"Bandit (K=4, H=2, {num_episodes} ep x {len(seeds)} seeds)")
    print("=" * 60)
    np.random.seed(seeds[0])
    bandit_env = BanditEnv(num_arms=4, inspect_accuracy=0.80, inspect_cost=0.5,
                           correct_reward=10.0, small_reward=1.0)
    best_w_b = tune_info_gain_weight(bandit_env, tune_episodes=200)
    best_w_b_pig = tune_info_gain_weight(
        bandit_env, tune_episodes=200,
        agent_class=PlanningInfoGainAgent,
        agent_kwargs={"planning_horizon": 2},
    )
    tuned_weights.append({"env": "bandit_env", "planning_horizon": 2,
                          "w_succ_infogain_myopic": float(best_w_b),
                          "w_succ_planning_ig": float(best_w_b_pig)})
    bandit_configs = [
        ("Myopic", MyopicAgent, {}),
        ("Planning", PlanningAgent, {"planning_horizon": 2}),
        ("InfoGain-Tuned", InformationGainAgent, {"info_gain_weight": best_w_b}),
        ("Planning+IG", PlanningInfoGainAgent, {"planning_horizon": 2, "info_gain_weight": best_w_b_pig}),
        ("EFE", EFEAgent, {"planning_horizon": 2}),
        ("Thompson", ThompsonSamplingAgent, {"num_samples": 100}),
    ]
    bandit_raw = run_env_with_stats(bandit_env, "Bandit", bandit_configs, num_episodes, seeds)
    all_bootstrap_rows.append(generate_bootstrap_table(bandit_raw, "Bandit"))
    all_effect_rows.append(generate_effect_size_table(bandit_raw, "Bandit"))
    all_stats_dfs.append(compute_full_statistics(bandit_raw, "Bandit"))

    # Save all tables
    bootstrap_df = pd.concat(all_bootstrap_rows, ignore_index=True)
    bootstrap_df.to_csv("results/results_bootstrap_ci.csv", index=False)
    print(f"\nBootstrap CIs saved to results/results_bootstrap_ci.csv")

    effect_df = pd.concat(all_effect_rows, ignore_index=True)
    effect_df.to_csv("results/results_effect_sizes.csv", index=False)
    print(f"Effect sizes saved to results/results_effect_sizes.csv")

    full_stats_df = pd.concat(all_stats_dfs, ignore_index=True)
    pd.DataFrame(tuned_weights).to_csv("results/results_supplementary_tuned_weights.csv", index=False)
    print("Tuned weights saved to results/results_supplementary_tuned_weights.csv")
    full_stats_df.to_csv("results/results_full_statistics.csv", index=False)
    print(f"Full pairwise statistics saved to results/results_full_statistics.csv")

    print("\n" + "=" * 60)
    print("BOOTSTRAP CI SUMMARY")
    print("=" * 60)
    print(bootstrap_df.to_string(index=False))

    print("\n" + "=" * 60)
    print("EFFECT SIZE SUMMARY (EFE vs baselines)")
    print("=" * 60)
    print(effect_df.to_string(index=False))


if __name__ == "__main__":
    main()
