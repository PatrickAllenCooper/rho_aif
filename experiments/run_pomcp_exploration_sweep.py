"""
POMCP exploration-constant sweep and informed rollouts on the observe-then-
commit environments.

The Discussion of the manuscript says the observe-then-commit POMCP "runs
with a single untuned UCB1 exploration constant per battery ... and a
per-environment exploration sweep could narrow this gap", and that "POMCP
with fully informed rollouts ... would narrow the gap further". Both were
admissions without data. This script supplies the data under the MCTS
battery's own protocol (experiments/run_mcts_experiments.py: 200 episodes x
the 5 canonical seeds, the same horizons, simulation budgets, and rollout
depths). Per environment it runs:

    POMCP, uniform rollouts, c in {1, 2, 5, 10, 20, 50, R}, where R is the
        commit reward range (Tiger 110, Diagnosis and Tileworld 60), the
        value MCTS-EFE defaults to;
    POMCP, information-gain rollouts (each rollout step takes the
        observation with the largest exact one-step expected information
        gain), at c = 5 and c = R;
    MCTS-EFE at its default c = R (the manuscript's configuration) and at
        c = 5 (POMCP's constant), as the reference pair.

POMCP's internal stream is seeded per run from the outer seed
(vary_agent_seed=True, the protocol the reproducibility checklist states),
so POMCP rows here are not bit-identical to results_mcts_efe.csv's, whose
producer left the planner seed at its constant default; the c = 5 uniform
row is the like-for-like reference within this file.

Outputs
    results/results_pomcp_exploration_sweep.csv        one row per config
    results/results_pomcp_exploration_sweep_stats.csv  seed-level Welch tests
        of every configuration against MCTS-EFE (default c) on success and
        reward, plus each POMCP configuration against POMCP c = 5 uniform,
        Holm-Bonferroni within metric and family over the whole battery.

Timing columns are wall clock on a shared machine and are not a compute
comparison.
"""
from __future__ import annotations

import argparse
import os
import sys
import time

import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from rho_aif.agents.mcts_efe import MCTSEFEAgent
from rho_aif.agents.pomcp import POMCPAgent
from rho_aif.environments.diagnosis import DiagnosisEnv
from rho_aif.environments.tiger import TigerEnv
from rho_aif.environments.tileworld import TileworldEnv
from rho_aif.stats import holm_bonferroni, seed_level_ttest
from run_experiment import SEEDS, provenance_fields, run_experiment_multi_seed, summarize_results

ENVS = {
    "Tiger": dict(
        make=lambda: TigerEnv(listen_accuracy=0.85, listen_cost=1.0,
                              correct_reward=10.0, incorrect_penalty=-100.0),
        horizon=10, sims=500, mcts_rollout_depth=3, reward_range=110.0,
    ),
    "Diagnosis-N4": dict(
        make=lambda: DiagnosisEnv(num_conditions=4, test_accuracy=0.80, test_cost=1.0,
                                  correct_reward=10.0, incorrect_penalty=-50.0),
        horizon=5, sims=200, mcts_rollout_depth=3, reward_range=60.0,
    ),
    "Tileworld-6x6": dict(
        make=lambda: TileworldEnv(grid_size=6, scan_accuracy=0.80, scan_cost=1.0,
                                  correct_reward=10.0, incorrect_penalty=-50.0),
        horizon=2, sims=200, mcts_rollout_depth=2, reward_range=60.0,
    ),
}
C_GRID = [1.0, 2.0, 5.0, 10.0, 20.0, 50.0]

METRICS = {"success": lambda r: float(r.success), "reward": lambda r: float(r.total_reward)}


def configs_for(cfg):
    R = cfg["reward_range"]
    out = []
    for c in C_GRID + [R]:
        out.append(dict(agent="POMCP", label=f"POMCP c={c:g} uniform", c=c, rollout="uniform"))
    for c in (5.0, R):
        out.append(dict(agent="POMCP", label=f"POMCP c={c:g} info-gain", c=c, rollout="info_gain"))
    out.append(dict(agent="MCTS-EFE", label=f"MCTS-EFE c={R:g} (default)", c=R, rollout="efe"))
    out.append(dict(agent="MCTS-EFE", label="MCTS-EFE c=5", c=5.0, rollout="efe"))
    return out


def run(envs, num_episodes, seeds, out_csv, stats_csv):
    os.makedirs(os.path.dirname(out_csv) or ".", exist_ok=True)
    rows, stats, raw = [], [], {}
    for env_name in envs:
        cfg = ENVS[env_name]
        env = cfg["make"]()
        print(f"\n{'=' * 70}\nPOMCP EXPLORATION SWEEP: {env_name} (H={cfg['horizon']}, sims={cfg['sims']}, "
              f"{num_episodes} episodes x {len(seeds)} seeds)\n{'=' * 70}", flush=True)
        for spec in configs_for(cfg):
            t0 = time.time()
            if spec["agent"] == "POMCP":
                res = run_experiment_multi_seed(
                    POMCPAgent, env, num_episodes, seeds=seeds, vary_agent_seed=True,
                    num_simulations=cfg["sims"], rollout_depth=cfg["horizon"] + 3,
                    exploration_constant=spec["c"], rollout_policy=spec["rollout"],
                )
            else:
                res = run_experiment_multi_seed(
                    MCTSEFEAgent, env, num_episodes, seeds=seeds,
                    num_simulations=cfg["sims"], planning_horizon=cfg["horizon"],
                    rollout_depth=cfg["mcts_rollout_depth"], exploration_constant=spec["c"],
                )
            dt = time.time() - t0
            s = summarize_results(res)
            raw[(env_name, spec["label"])] = res
            row = {
                "env": env_name, "agent": spec["agent"], "label": spec["label"],
                "exploration_constant": spec["c"], "rollout_policy": spec["rollout"],
                "horizon": cfg["horizon"], "sim_budget": cfg["sims"],
                "vary_agent_seed": spec["agent"] == "POMCP",
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
            print(f"  {spec['label']:28s} success={s['success_rate']:.3f} reward={s['mean_reward']:+.3f} "
                  f"obs={s['mean_observations']:.2f} ({dt:.0f}s)", flush=True)
            pd.DataFrame(rows).to_csv(out_csv, index=False)

        ref_label = f"MCTS-EFE c={cfg['reward_range']:g} (default)"
        ref = raw[(env_name, ref_label)]
        pomcp5 = raw[(env_name, "POMCP c=5 uniform")]
        for spec in configs_for(cfg):
            if spec["label"] == ref_label:
                continue
            for metric, fn in METRICS.items():
                t = seed_level_ttest(ref, raw[(env_name, spec["label"])], fn)
                stats.append({
                    "env": env_name, "family": "vs MCTS-EFE default", "metric": metric,
                    "label_a": ref_label, "label_b": spec["label"],
                    "mean_a": t["mean_of_seed_means_a"], "mean_b": t["mean_of_seed_means_b"],
                    "diff": t["mean_of_seed_means_a"] - t["mean_of_seed_means_b"],
                    "t_stat": t["t_stat"], "p_seed_level": t["p_value"], "n_seeds": t["n_seeds_a"],
                })
            if spec["agent"] == "POMCP" and spec["label"] != "POMCP c=5 uniform":
                for metric, fn in METRICS.items():
                    t = seed_level_ttest(pomcp5, raw[(env_name, spec["label"])], fn)
                    stats.append({
                        "env": env_name, "family": "vs POMCP c=5 uniform", "metric": metric,
                        "label_a": "POMCP c=5 uniform", "label_b": spec["label"],
                        "mean_a": t["mean_of_seed_means_a"], "mean_b": t["mean_of_seed_means_b"],
                        "diff": t["mean_of_seed_means_a"] - t["mean_of_seed_means_b"],
                        "t_stat": t["t_stat"], "p_seed_level": t["p_value"], "n_seeds": t["n_seeds_a"],
                    })
    df_stats = pd.DataFrame(stats)
    if len(df_stats):
        df_stats["significant_hb_seed_level"] = False
        for (family, metric), grp in df_stats.groupby(["family", "metric"]):
            flags = holm_bonferroni([float(x) for x in grp["p_seed_level"]])
            for i, f in zip(grp.index, flags):
                df_stats.loc[i, "significant_hb_seed_level"] = bool(f)
        df_stats.to_csv(stats_csv, index=False)
    print(f"\nSaved {out_csv} and {stats_csv}", flush=True)
    return pd.DataFrame(rows), df_stats


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--envs", nargs="*", default=list(ENVS))
    p.add_argument("--episodes", type=int, default=200)
    p.add_argument("--quick", action="store_true", help="smoke test: 4 episodes, 2 seeds, scratch output")
    p.add_argument("--out", default="results/results_pomcp_exploration_sweep.csv")
    args = p.parse_args()
    seeds, episodes, out = list(SEEDS), args.episodes, args.out
    if args.quick:
        seeds, episodes = seeds[:2], 4
        out = os.path.join(os.environ.get("TMPDIR", "/tmp"), "results_pomcp_exploration_sweep_quick.csv")
        print("QUICK MODE: scratch output, canonical CSVs untouched", flush=True)
    run(args.envs, episodes, seeds, out, out.replace(".csv", "_stats.csv"))


if __name__ == "__main__":
    main()
