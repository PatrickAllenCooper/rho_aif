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
from rho_aif.benchmark import (
    INSPECTION_CONFIGS,
    run_inspection_episode,
)
from rho_aif.stats import seed_means
from run_experiment import SEEDS


def run_inspection_experiment(config_name="Inspection-N8", num_episodes=500, seeds=None, write_csv=True):
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
    all_episode_results = {}
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
                r["seed"] = seed
                r["accuracy_ep"] = r["correct"] / nc if nc > 0 else 0.0
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
        log_scores = [r["log_score"] for r in episode_results]
        briers = [r["brier_score"] for r in episode_results]

        accuracy = np.mean(corrects) / nc if nc > 0 else 0

        seed_reward_means = seed_means(episode_results, lambda r: r["total_reward"])
        seed_accuracy_means = seed_means(episode_results, lambda r: r["accuracy_ep"])
        seed_tests_means = seed_means(episode_results, lambda r: r["tests"])
        n_seeds = len(seed_reward_means)

        row = {
            "instance": config_name,
            "agent": label,
            "mean_reward": np.mean(rewards),
            "std_reward": np.std(rewards),
            "se_reward_pooled": np.std(rewards) / np.sqrt(len(rewards)),
            "se_reward_seed_level": (
                float(np.std(seed_reward_means, ddof=1) / np.sqrt(n_seeds))
                if n_seeds > 1 else float("nan")
            ),
            "accuracy": accuracy,
            "se_accuracy_seed_level": (
                float(np.std(seed_accuracy_means, ddof=1) / np.sqrt(n_seeds))
                if n_seeds > 1 else float("nan")
            ),
            "n_seeds": n_seeds,
            "mean_correct": np.mean(corrects),
            "mean_missed": np.mean(misseds),
            "mean_false_alarm": np.mean(false_alarms),
            "mean_tests": np.mean(tests),
            "se_tests_seed_level": (
                float(np.std(seed_tests_means, ddof=1) / np.sqrt(n_seeds))
                if n_seeds > 1 else float("nan")
            ),
            "completion_rate": np.mean(all_diag),
            "mean_steps": np.mean([r["steps"] for r in episode_results]),
            "mean_log_score": np.mean(log_scores),
            "mean_brier": np.mean(briers),
            "time_s": dt,
        }
        results.append(row)
        print(
            f"  {label:25s}: reward={row['mean_reward']:+.2f} +/- {row['se_reward_seed_level']:.2f}(seed)  "
            f"acc={accuracy:.1%} +/- {row['se_accuracy_seed_level']:.1%}(seed)  "
            f"log_score={row['mean_log_score']:+.3f}  "
            f"brier={row['mean_brier']:.3f}  tests={row['mean_tests']:.1f}  "
            f"complete={row['completion_rate']:.1%}  ({dt:.1f}s)"
        )
        all_episode_results[label] = episode_results

    df = pd.DataFrame(results)
    if write_csv:
        from run_experiment import provenance_fields
        prov = provenance_fields(seeds, num_episodes)
        for k, v in prov.items():
            df[k] = v
        csv_name = f"results/results_inspection_n{nc}.csv"
        os.makedirs(os.path.dirname(os.path.abspath(csv_name)), exist_ok=True)
        df.to_csv(csv_name, index=False)
        print(f"\nResults saved to {csv_name}")

        stats_df = compute_inspection_stats(all_episode_results, config_name)
        stats_csv = f"results/results_inspection_n{nc}_stats.csv"
        stats_df.to_csv(stats_csv, index=False)
        print(f"Statistics saved to {stats_csv}")
    return df


def compute_inspection_stats(all_episode_results, config_name):
    """Pairwise seed-level Welch t-tests (reward and per-component accuracy),
    Holm-Bonferroni corrected, mirroring compute_full_statistics in
    run_experiment.py but for Structural Inspection's dict-based episode
    results (reward, accuracy) rather than EpisodeResult objects."""
    from rho_aif.stats import cohens_d, holm_bonferroni, seed_level_ttest
    from scipy.stats import ttest_ind

    labels = list(all_episode_results.keys())
    rows = []
    for metric_name, extractor in [
        ("Reward", lambda r: r["total_reward"]),
        ("Accuracy", lambda r: r["accuracy_ep"]),
        ("Tests", lambda r: r["tests"]),
    ]:
        for i in range(len(labels)):
            for j in range(i + 1, len(labels)):
                res_a = all_episode_results[labels[i]]
                res_b = all_episode_results[labels[j]]
                vals_a = np.array([extractor(r) for r in res_a])
                vals_b = np.array([extractor(r) for r in res_b])

                d = cohens_d(vals_a, vals_b)
                t_stat, p_val = ttest_ind(vals_a, vals_b, equal_var=False)

                seed_out = seed_level_ttest(res_a, res_b, extractor)

                rows.append({
                    "instance": config_name,
                    "metric": metric_name,
                    "agent_a": labels[i],
                    "agent_b": labels[j],
                    "mean_a": float(np.mean(vals_a)),
                    "mean_b": float(np.mean(vals_b)),
                    "diff": float(np.mean(vals_a) - np.mean(vals_b)),
                    "cohens_d_pooled": d,
                    "t_stat_pooled": float(t_stat),
                    "p_pooled": float(p_val),
                    "n_seeds": seed_out["n_seeds_a"],
                    "p_seed_level": seed_out["p_value"],
                    "cohens_d_seed_level": seed_out["cohens_d"],
                })

    p_list = [r["p_pooled"] for r in rows]
    for r, sig in zip(rows, holm_bonferroni(p_list)):
        r["significant_hb_pooled"] = sig
    seed_p_list = [r["p_seed_level"] for r in rows]
    for r, sig in zip(rows, holm_bonferroni(seed_p_list)):
        r["significant_hb_seed_level"] = sig

    return pd.DataFrame(rows)


if __name__ == "__main__":
    for config_name in INSPECTION_CONFIGS:
        run_inspection_experiment(config_name=config_name)
        print()
