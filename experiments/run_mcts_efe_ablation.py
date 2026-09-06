"""
MCTS-EFE component ablation.

Suggested by the confirmation round's associate editor (ledger 9.17.27,
non-blocking item 22) after required change 4 disclosed that MCTS-EFE and
the observe-then-commit POMCP differ in more than the leaf: MCTS-EFE adds
exact per-node information gain to the in-tree observe reward and backs up
the max over action children, where POMCP backs up sampled means. The
manuscript therefore said the comparison "does not separate the
contribution of the leaf evaluation from that of the in-tree information
reward or the backup operator, and no ablation of those components was
run". This script runs that ablation under the MCTS battery's own protocol
(experiments/run_mcts_experiments.py: 200 episodes x the 5 canonical seeds
per environment, the same horizon, simulation budget, and rollout depth).

Variants (rho_aif/agents/mcts_efe.py switches):

    full          max-backup, in-tree IG      the manuscript's MCTS-EFE
    mean-backup   mean-backup, in-tree IG     UCT's backup, EFE objective kept
    no-tree-ig    max-backup, no in-tree IG   epistemic term only via the leaf
    mean-no-ig    mean-backup, no in-tree IG  a UCT tree with an EFE-greedy leaf

Outputs
    results/results_mcts_efe_ablation.csv         one row per env x variant
    results/results_mcts_efe_ablation_stats.csv   seed-level Welch tests of
        each variant against ``full`` per environment and metric (success,
        reward, observations), Holm-Bonferroni within metric over the whole
        battery, plus pooled SE for the appendix convention.

Timing columns are wall clock on a shared machine and are not a compute
comparison.
"""
from __future__ import annotations

import argparse
import os
import sys
import time

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from rho_aif.agents.mcts_efe import MCTSEFEAgent
from rho_aif.environments.diagnosis import DiagnosisEnv
from rho_aif.environments.tiger import TigerEnv
from rho_aif.environments.tileworld import TileworldEnv
from rho_aif.stats import holm_bonferroni, seed_level_ttest
from run_experiment import SEEDS, provenance_fields, run_experiment_multi_seed, summarize_results

VARIANTS = [
    ("full", dict(backup="max", in_tree_info_gain=True)),
    ("mean-backup", dict(backup="mean", in_tree_info_gain=True)),
    ("no-tree-ig", dict(backup="max", in_tree_info_gain=False)),
    ("mean-no-ig", dict(backup="mean", in_tree_info_gain=False)),
]

# The MCTS battery's own configurations (run_mcts_experiments.py), one per
# environment: the horizon and budget the manuscript's numbers come from.
ENVS = {
    "Tiger": dict(
        make=lambda: TigerEnv(listen_accuracy=0.85, listen_cost=1.0,
                              correct_reward=10.0, incorrect_penalty=-100.0),
        planning_horizon=10, num_simulations=500, rollout_depth=3,
    ),
    "Diagnosis-N4": dict(
        make=lambda: DiagnosisEnv(num_conditions=4, test_accuracy=0.80, test_cost=1.0,
                                  correct_reward=10.0, incorrect_penalty=-50.0),
        planning_horizon=5, num_simulations=200, rollout_depth=3,
    ),
    "Tileworld-6x6": dict(
        make=lambda: TileworldEnv(grid_size=6, scan_accuracy=0.80, scan_cost=1.0,
                                  correct_reward=10.0, incorrect_penalty=-50.0),
        planning_horizon=2, num_simulations=200, rollout_depth=2,
    ),
}

METRICS = {
    "success": lambda r: float(r.success),
    "reward": lambda r: float(r.total_reward),
    "observations": lambda r: float(r.num_observations),
}


def run(envs, num_episodes, seeds, out_csv, stats_csv):
    os.makedirs(os.path.dirname(out_csv) or ".", exist_ok=True)
    rows, stats, raw = [], [], {}
    for env_name in envs:
        cfg = ENVS[env_name]
        env = cfg["make"]()
        print(f"\n{'=' * 70}\nMCTS-EFE ABLATION: {env_name} (H={cfg['planning_horizon']}, "
              f"sims={cfg['num_simulations']}, {num_episodes} episodes x {len(seeds)} seeds)\n{'=' * 70}",
              flush=True)
        for label, switches in VARIANTS:
            t0 = time.time()
            res = run_experiment_multi_seed(
                MCTSEFEAgent, env, num_episodes, seeds=seeds,
                num_simulations=cfg["num_simulations"],
                planning_horizon=cfg["planning_horizon"],
                rollout_depth=cfg["rollout_depth"],
                **switches,
            )
            dt = time.time() - t0
            s = summarize_results(res)
            raw[(env_name, label)] = res
            row = {
                "env": env_name, "variant": label,
                "backup": switches["backup"],
                "in_tree_info_gain": switches["in_tree_info_gain"],
                "horizon": cfg["planning_horizon"], "sim_budget": cfg["num_simulations"],
                "rollout_depth": cfg["rollout_depth"],
                "success": s["success_rate"], "reward": s["mean_reward"],
                "std_reward": s["std_reward"], "obs": s["mean_observations"],
                "se_success_seed_level": s.get("se_success_seed_level", float("nan")),
                "se_reward_seed_level": s.get("se_reward_seed_level", float("nan")),
                "se_reward_pooled": s.get("se_reward_pooled", float("nan")),
                "n_seeds": len(seeds), "wall_clock_s": dt,
                "ms_per_ep": dt / (num_episodes * len(seeds)) * 1000.0,
            }
            row.update(provenance_fields(seeds, num_episodes))
            rows.append(row)
            print(f"  {label:12s} success={s['success_rate']:.3f} reward={s['mean_reward']:+.3f} "
                  f"obs={s['mean_observations']:.2f} ({dt:.0f}s)", flush=True)
            pd.DataFrame(rows).to_csv(out_csv, index=False)

        full = raw[(env_name, "full")]
        for label, _ in VARIANTS[1:]:
            other = raw[(env_name, label)]
            for metric, fn in METRICS.items():
                t = seed_level_ttest(full, other, fn)
                stats.append({
                    "env": env_name, "metric": metric, "variant_a": "full", "variant_b": label,
                    "mean_a": t["mean_of_seed_means_a"], "mean_b": t["mean_of_seed_means_b"],
                    "diff": t["mean_of_seed_means_a"] - t["mean_of_seed_means_b"],
                    "t_stat": t["t_stat"], "p_seed_level": t["p_value"],
                    "n_seeds": t["n_seeds_a"],
                })
    # Holm-Bonferroni within metric across the whole battery (3 envs x 3
    # variants = 9 comparisons per metric).
    df_stats = pd.DataFrame(stats)
    if len(df_stats):
        df_stats["significant_hb_seed_level"] = False
        for metric in df_stats["metric"].unique():
            idx = df_stats.index[df_stats["metric"] == metric]
            flags = holm_bonferroni([float(df_stats.loc[i, "p_seed_level"]) for i in idx])
            for i, f in zip(idx, flags):
                df_stats.loc[i, "significant_hb_seed_level"] = bool(f)
        df_stats.to_csv(stats_csv, index=False)
    print(f"\nSaved {out_csv} and {stats_csv}", flush=True)
    return pd.DataFrame(rows), df_stats


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--envs", nargs="*", default=list(ENVS), help="subset of environments")
    p.add_argument("--episodes", type=int, default=200, help="episodes per seed (battery: 200)")
    p.add_argument("--quick", action="store_true", help="smoke test: 4 episodes, 2 seeds, scratch output")
    p.add_argument("--out", default="results/results_mcts_efe_ablation.csv")
    args = p.parse_args()
    seeds = list(SEEDS)
    episodes = args.episodes
    out = args.out
    if args.quick:
        seeds, episodes = seeds[:2], 4
        out = os.path.join(os.environ.get("TMPDIR", "/tmp"), "results_mcts_efe_ablation_quick.csv")
        print("QUICK MODE: scratch output, canonical CSVs untouched", flush=True)
    stats = out.replace(".csv", "_stats.csv")
    run(args.envs, episodes, seeds, out, stats)


if __name__ == "__main__":
    main()
