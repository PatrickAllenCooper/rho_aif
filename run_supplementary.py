#!/usr/bin/env python3
"""
Generate supplementary material: bootstrap CIs, Cohen's d, and
Holm-Bonferroni-corrected p-values for all environments.

Runs concise versions of each experiment (same seed, same config)
and produces CSV tables and LaTeX-formatted output for the paper appendix.
"""

import numpy as np
import pandas as pd
from typing import List, Dict

from environments.info_seeking import InfoSeekingEnv
from environments.tiger import TigerEnv
from environments.diagnosis import DiagnosisEnv
from environments.bandit import BanditEnv
from agents.myopic import MyopicAgent
from agents.planning import PlanningAgent
from agents.info_gain import InformationGainAgent
from agents.planning_infogain import PlanningInfoGainAgent
from agents.epistemic_only import EpistemicOnlyAgent
from agents.efe import EFEAgent
from run_experiment import (
    make_agent, run_episode, run_experiment, summarize_results,
    tune_info_gain_weight, EpisodeResult, compute_full_statistics,
)
from stats import bootstrap_ci, cohens_d


def run_env_with_stats(env, env_name, agent_configs, num_episodes=1000, seed=42):
    """Run all agents on an environment and return raw results."""
    np.random.seed(seed)
    all_raw = {}

    for label, agent_class, kwargs in agent_configs:
        agent = make_agent(agent_class, env, **kwargs)
        results = []
        for _ in range(num_episodes):
            results.append(run_episode(agent, env))
        all_raw[label] = results
        s = summarize_results(results)
        print(f"  {label:18s}: obs={s['mean_observations']:.2f}  "
              f"success={s['success_rate']:.1%}  reward={s['mean_reward']:+.3f}")

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

    vfe_rewards = np.array([r.total_reward for r in all_raw["EFE"]])
    rows = []
    for label, results in all_raw.items():
        if label == "EFE":
            continue
        other_rewards = np.array([r.total_reward for r in results])
        d = cohens_d(vfe_rewards, other_rewards)
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
    seed = 42
    num_episodes = 1000

    all_bootstrap_rows = []
    all_effect_rows = []
    all_stats_dfs = []

    # Tiger
    print("=" * 60)
    print("Tiger (H=6, 1000 episodes)")
    print("=" * 60)
    np.random.seed(seed)
    tiger_env = TigerEnv(listen_accuracy=0.85, listen_cost=1.0,
                         correct_reward=10.0, incorrect_penalty=-100.0)
    best_w = tune_info_gain_weight(tiger_env, tune_episodes=200)
    tiger_configs = [
        ("Myopic", MyopicAgent, {}),
        ("Planning", PlanningAgent, {"planning_horizon": 6}),
        ("InfoGain-Tuned", InformationGainAgent, {"info_gain_weight": best_w}),
        ("Planning+IG", PlanningInfoGainAgent, {"planning_horizon": 6, "info_gain_weight": best_w}),
        ("EFE", EFEAgent, {"planning_horizon": 6}),
    ]
    tiger_raw = run_env_with_stats(tiger_env, "Tiger", tiger_configs, num_episodes, seed)
    all_bootstrap_rows.append(generate_bootstrap_table(tiger_raw, "Tiger"))
    all_effect_rows.append(generate_effect_size_table(tiger_raw, "Tiger"))
    all_stats_dfs.append(compute_full_statistics(tiger_raw, "Tiger"))

    # Testbed
    print("\n" + "=" * 60)
    print("Testbed (H=4, 1000 episodes)")
    print("=" * 60)
    np.random.seed(seed)
    testbed_env = InfoSeekingEnv(observation_accuracy=0.75, observation_cost=0.1,
                                correct_reward=1.0, incorrect_penalty=-1.0)
    best_w_tb = tune_info_gain_weight(testbed_env, tune_episodes=200)
    testbed_configs = [
        ("Myopic", MyopicAgent, {}),
        ("Planning", PlanningAgent, {"planning_horizon": 4}),
        ("InfoGain-Tuned", InformationGainAgent, {"info_gain_weight": best_w_tb}),
        ("Planning+IG", PlanningInfoGainAgent, {"planning_horizon": 4, "info_gain_weight": best_w_tb}),
        ("EFE", EFEAgent, {"planning_horizon": 4}),
    ]
    testbed_raw = run_env_with_stats(testbed_env, "Testbed", testbed_configs, num_episodes, seed)
    all_bootstrap_rows.append(generate_bootstrap_table(testbed_raw, "Testbed"))
    all_effect_rows.append(generate_effect_size_table(testbed_raw, "Testbed"))
    all_stats_dfs.append(compute_full_statistics(testbed_raw, "Testbed"))

    # Diagnosis
    print("\n" + "=" * 60)
    print("Diagnosis (N=4, H=3, 1000 episodes)")
    print("=" * 60)
    np.random.seed(seed)
    diag_env = DiagnosisEnv(num_conditions=4, test_accuracy=0.80, test_cost=1.0,
                            correct_reward=10.0, incorrect_penalty=-50.0)
    best_w_d = tune_info_gain_weight(diag_env, tune_episodes=200)
    diag_configs = [
        ("Myopic", MyopicAgent, {}),
        ("Planning", PlanningAgent, {"planning_horizon": 3}),
        ("InfoGain-Tuned", InformationGainAgent, {"info_gain_weight": best_w_d}),
        ("Planning+IG", PlanningInfoGainAgent, {"planning_horizon": 3, "info_gain_weight": best_w_d}),
        ("EFE", EFEAgent, {"planning_horizon": 3}),
    ]
    diag_raw = run_env_with_stats(diag_env, "Diagnosis", diag_configs, num_episodes, seed)
    all_bootstrap_rows.append(generate_bootstrap_table(diag_raw, "Diagnosis"))
    all_effect_rows.append(generate_effect_size_table(diag_raw, "Diagnosis"))
    all_stats_dfs.append(compute_full_statistics(diag_raw, "Diagnosis"))

    # Bandit
    print("\n" + "=" * 60)
    print("Bandit (K=4, H=2, 1000 episodes)")
    print("=" * 60)
    np.random.seed(seed)
    bandit_env = BanditEnv(num_arms=4, inspect_accuracy=0.80, inspect_cost=0.5,
                           correct_reward=10.0, small_reward=1.0)
    best_w_b = tune_info_gain_weight(bandit_env, tune_episodes=200)
    bandit_configs = [
        ("Myopic", MyopicAgent, {}),
        ("Planning", PlanningAgent, {"planning_horizon": 2}),
        ("InfoGain-Tuned", InformationGainAgent, {"info_gain_weight": best_w_b}),
        ("Planning+IG", PlanningInfoGainAgent, {"planning_horizon": 2, "info_gain_weight": best_w_b}),
        ("EFE", EFEAgent, {"planning_horizon": 2}),
    ]
    bandit_raw = run_env_with_stats(bandit_env, "Bandit", bandit_configs, num_episodes, seed)
    all_bootstrap_rows.append(generate_bootstrap_table(bandit_raw, "Bandit"))
    all_effect_rows.append(generate_effect_size_table(bandit_raw, "Bandit"))
    all_stats_dfs.append(compute_full_statistics(bandit_raw, "Bandit"))

    # Save all tables
    bootstrap_df = pd.concat(all_bootstrap_rows, ignore_index=True)
    bootstrap_df.to_csv("results_bootstrap_ci.csv", index=False)
    print(f"\nBootstrap CIs saved to results_bootstrap_ci.csv")

    effect_df = pd.concat(all_effect_rows, ignore_index=True)
    effect_df.to_csv("results_effect_sizes.csv", index=False)
    print(f"Effect sizes saved to results_effect_sizes.csv")

    full_stats_df = pd.concat(all_stats_dfs, ignore_index=True)
    full_stats_df.to_csv("results_full_statistics.csv", index=False)
    print(f"Full pairwise statistics saved to results_full_statistics.csv")

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
