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
    RockSampleFlatMCAgent,
    RockSampleTreeSearchAgent,
)
from rho_aif.stats import cohens_d, holm_bonferroni, seed_level_ttest, seed_means
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
    config_name="RS[5,3]", num_episodes=500, seeds=None,
    override_depth=None, csv_name=None,
):
    if seeds is None:
        seeds = SEEDS
    cfg = ROCKSAMPLE_CONFIGS[config_name]
    gs = cfg["grid_size"]
    nr = cfg["num_rocks"]
    rp = cfg["rock_positions"]
    td = override_depth if override_depth is not None else cfg["tree_depth"]
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
        ("Flat-MC (1000)", lambda: RockSampleFlatMCAgent(env, num_simulations=1000)),
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
    all_episode_results = {}
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
                r["seed"] = seed
                episode_results.append(r)

        dt = time.time() - t0
        rewards = [r["total_reward"] for r in episode_results]
        goods = [r["good_sampled"] for r in episode_results]
        bads = [r["bad_sampled"] for r in episode_results]
        checks = [r["checks"] for r in episode_results]

        seed_reward_means = seed_means(episode_results, lambda r: r["total_reward"])
        seed_bad_means = seed_means(episode_results, lambda r: r["bad_sampled"])
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
            "mean_good": np.mean(goods),
            "mean_bad": np.mean(bads),
            "se_bad_seed_level": (
                float(np.std(seed_bad_means, ddof=1) / np.sqrt(n_seeds))
                if n_seeds > 1 else float("nan")
            ),
            "mean_checks": np.mean(checks),
            "mean_steps": np.mean([r["steps"] for r in episode_results]),
            "time_s": dt,
            "n_seeds": n_seeds,
            "episodes_per_seed": num_episodes,
            "seed_list": "|".join(str(s) for s in seeds),
            "tree_depth": td,
        }
        results.append(row)
        print(
            f"  {label:25s}: reward={row['mean_reward']:+.2f} +/- {row['se_reward_seed_level']:.2f}(seed)  "
            f"good={row['mean_good']:.2f}  bad={row['mean_bad']:.2f}  "
            f"checks={row['mean_checks']:.1f}  steps={row['mean_steps']:.1f}  ({dt:.1f}s)"
        )
        all_episode_results[label] = episode_results

    df = pd.DataFrame(results)
    if csv_name is None:
        csv_name = f"results/results_rocksample_{gs}x{nr}.csv"
    os.makedirs(os.path.dirname(os.path.abspath(csv_name)), exist_ok=True)
    df.to_csv(csv_name, index=False)
    print(f"\nResults saved to {csv_name}")

    stats_df = compute_rocksample_stats(all_episode_results, config_name)
    stats_csv = csv_name.replace(".csv", "_stats.csv")
    stats_df.to_csv(stats_csv, index=False)
    print(f"Statistics saved to {stats_csv}")
    return df


def compute_rocksample_stats(all_episode_results, config_name):
    """Pairwise seed-level Welch t-tests on reward, Holm-Bonferroni
    corrected, mirroring compute_full_statistics in run_experiment.py but
    for RockSample's dict-based episode results."""
    from scipy.stats import ttest_ind

    labels = list(all_episode_results.keys())
    rows = []
    for metric_name, extractor in [
        ("Reward", lambda r: r["total_reward"]),
        ("Bad", lambda r: r["bad_sampled"]),
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


# The paper's declared per-instance protocol: episodes per seed and seed set.
# RS[5,3] and RS[7,4] run the extended 10-seed sweep; the larger instances
# run 100 episodes over the canonical 5 seeds.
from run_experiment import EXTENDED_SEEDS

ROCKSAMPLE_PROTOCOL = {
    "RS[5,3]": {"num_episodes": 500, "seeds": EXTENDED_SEEDS},
    "RS[7,4]": {"num_episodes": 500, "seeds": EXTENDED_SEEDS},
    "RS[7,8]": {"num_episodes": 100, "seeds": SEEDS},
    "RS[11,11]": {"num_episodes": 100, "seeds": SEEDS},
}


def run_depth_check():
    """Reproduce results_rocksample_11x11_depth3_check.csv: RS[11,11] at
    depth 3 (vs the reported depth 2), verifying policy saturation rather
    than a depth ceiling explains the EFE/Planning tie at this scale."""
    return run_rocksample_experiment(
        config_name="RS[11,11]",
        num_episodes=100,
        seeds=SEEDS,
        override_depth=3,
        csv_name="results/results_rocksample_11x11_depth3_check.csv",
    )


if __name__ == "__main__":
    import sys

    cmd = sys.argv[1] if len(sys.argv) > 1 else "all"
    if cmd == "depth-check":
        run_depth_check()
    elif cmd in ROCKSAMPLE_CONFIGS:
        proto = ROCKSAMPLE_PROTOCOL[cmd]
        run_rocksample_experiment(config_name=cmd, **proto)
    else:
        for config_name in ROCKSAMPLE_CONFIGS:
            proto = ROCKSAMPLE_PROTOCOL[config_name]
            run_rocksample_experiment(config_name=config_name, **proto)
            print()
        run_depth_check()
