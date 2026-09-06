"""
EFE on RS[5,3] under the POMCP horizon diagnostic's own protocol.

The RockSample appendix compares POMCP's best diagnostic configuration
(+15.6 at 530 ms per decision, 5 seeds x 100 episodes,
results_rocksample_pomcp_horizon.csv) with EFE from the main battery
(10 seeds x 500 episodes, results_rocksample_5x3.csv). The confirmation
round's POMDP reviewer called that "a cross-battery point comparison" and
asked for "the diagnostic battery's own EFE-equivalent row if one is run".
This script runs it: EFE (w=1, d=3, the main battery's configuration) on
RS[5,3] with the diagnostic's seeds, episode count, step cap, and
per-episode seeding (seed * 10000 + episode index), so the comparison is
within one protocol.

Because the horizon CSV stores means and seed-level SEs rather than per-seed
values, each test against a POMCP row is a Welch t-test computed from
summary statistics (two means, two seed-level SEs, n = 5 each,
Welch-Satterthwaite degrees of freedom), which is the same test the
per-seed data would give. Holm-Bonferroni over the family of comparisons.

Outputs
    results/results_rocksample_efe_diagnostic.csv
    results/results_rocksample_efe_diagnostic_stats.csv
"""
from __future__ import annotations

import argparse
import os
import sys
import time

import numpy as np
import pandas as pd
from scipy import stats as sps

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), ".."))

from rho_aif.agents.rocksample_agents import RockSampleTreeSearchAgent
from rho_aif.stats import holm_bonferroni
from run_experiment import SEEDS, provenance_fields
from run_rocksample import ROCKSAMPLE_CONFIGS, make_rocksample_env

HORIZON_CSV = "results/results_rocksample_pomcp_horizon.csv"


def run_episode_timed(agent, env, seed, max_steps):
    obs, info = env.reset(seed=seed)
    agent.reset()
    total_reward, checks, ms = 0.0, 0, []
    truncated_flag = True
    for _ in range(max_steps):
        t0 = time.perf_counter()
        action = agent.select_action()
        ms.append((time.perf_counter() - t0) * 1000.0)
        obs, reward, terminated, truncated, info = env.step(action)
        total_reward += reward
        agent.update(action, obs)
        if env.NUM_MOVE_ACTIONS <= action < env.NUM_MOVE_ACTIONS + env.num_rocks:
            checks += 1
        if terminated or truncated:
            truncated_flag = bool(truncated) and not bool(terminated)
            break
    return {
        "total_reward": total_reward,
        "good_sampled": info.get("total_good_sampled", 0),
        "bad_sampled": info.get("total_bad_sampled", 0),
        "steps": env._step_count, "checks": checks,
        "truncated": 1.0 if truncated_flag else 0.0,
        "planning_ms": float(np.mean(ms)) if ms else 0.0,
    }


def welch_from_summary(m1, se1, n1, m2, se2, n2):
    """Welch t-test from two means and their standard errors of the mean."""
    v1, v2 = se1 ** 2, se2 ** 2
    t = (m1 - m2) / np.sqrt(v1 + v2)
    df = (v1 + v2) ** 2 / (v1 ** 2 / (n1 - 1) + v2 ** 2 / (n2 - 1))
    p = 2.0 * sps.t.sf(abs(t), df)
    return float(t), float(df), float(p)


def run(instance, num_episodes, seeds, out_csv, stats_csv, horizon_csv=HORIZON_CSV):
    os.makedirs(os.path.dirname(out_csv) or ".", exist_ok=True)
    cfg = ROCKSAMPLE_CONFIGS[instance]
    td = cfg["tree_depth"]
    env = make_rocksample_env(instance)  # diagnostic protocol: env default step cap
    max_steps = env.max_steps
    label = f"EFE w=1 (d={td})"
    print(f"{instance} / {label}: {num_episodes} episodes x {len(seeds)} seeds, step cap {max_steps}", flush=True)
    episodes = []
    t0 = time.time()
    for seed in seeds:
        np.random.seed(int(seed))
        agent = RockSampleTreeSearchAgent(env, info_weight=1.0, max_depth=td)
        for ep_i in range(num_episodes):
            r = run_episode_timed(agent, env, seed=int(seed) * 10000 + ep_i, max_steps=max_steps)
            r["seed"] = int(seed)
            episodes.append(r)
    dt = time.time() - t0
    df = pd.DataFrame(episodes)
    per_seed = df.groupby("seed")["total_reward"].mean()
    per_seed_bad = df.groupby("seed")["bad_sampled"].mean()
    n = len(per_seed)
    row = {
        "instance": instance, "agent": label,
        "mean_reward": float(df["total_reward"].mean()),
        "std_reward": float(df["total_reward"].std(ddof=0)),
        "se_reward_pooled": float(df["total_reward"].std(ddof=0) / np.sqrt(len(df))),
        "se_reward_seed_level": float(per_seed.std(ddof=1) / np.sqrt(n)) if n > 1 else float("nan"),
        "seed_reward_means": "|".join(f"{v:.4f}" for v in per_seed.values),
        "mean_good": float(df["good_sampled"].mean()), "mean_bad": float(df["bad_sampled"].mean()),
        "se_bad_seed_level": float(per_seed_bad.std(ddof=1) / np.sqrt(n)) if n > 1 else float("nan"),
        "mean_checks": float(df["checks"].mean()), "mean_steps": float(df["steps"].mean()),
        "truncation_rate": float(df["truncated"].mean()),
        "mean_planning_ms": float(df["planning_ms"].mean()),
        "time_s": dt, "n_seeds": n, "tree_depth": td, "max_steps": max_steps,
    }
    row.update(provenance_fields(seeds, num_episodes))
    pd.DataFrame([row]).to_csv(out_csv, index=False)
    print(f"  {label}: reward={row['mean_reward']:+.3f} +/- {row['se_reward_seed_level']:.3f} (seed) "
          f"good={row['mean_good']:.2f} bad={row['mean_bad']:.2f} ms/dec={row['mean_planning_ms']:.2f} ({dt:.0f}s)",
          flush=True)

    stats = []
    if os.path.exists(horizon_csv):
        h = pd.read_csv(horizon_csv)
        h = h[h["instance"] == instance]
        for _, hr in h.iterrows():
            t, dof, p = welch_from_summary(
                row["mean_reward"], row["se_reward_seed_level"], n,
                float(hr["mean_reward"]), float(hr["se_reward_seed_level"]), int(hr["n_seeds"]),
            )
            stats.append({
                "instance": instance, "metric": "Reward", "agent_a": label, "agent_b": hr["agent"],
                "mean_a": row["mean_reward"], "mean_b": float(hr["mean_reward"]),
                "diff": row["mean_reward"] - float(hr["mean_reward"]),
                "se_a_seed_level": row["se_reward_seed_level"], "se_b_seed_level": float(hr["se_reward_seed_level"]),
                "n_seeds_a": n, "n_seeds_b": int(hr["n_seeds"]),
                "ms_per_decision_a": row["mean_planning_ms"], "ms_per_decision_b": float(hr["mean_planning_ms"]),
                "t_stat": t, "welch_df": dof, "p_seed_level_from_summary": p,
                "same_protocol": bool(int(hr["episodes_per_seed"]) == num_episodes
                                      and str(hr["seed_list"]) == "|".join(str(s) for s in seeds)),
            })
    ds = pd.DataFrame(stats)
    if len(ds):
        flags = holm_bonferroni([float(x) for x in ds["p_seed_level_from_summary"]])
        ds["significant_hb_seed_level"] = [bool(f) for f in flags]
        ds.to_csv(stats_csv, index=False)
        print(ds[["agent_b", "mean_b", "diff", "p_seed_level_from_summary", "significant_hb_seed_level", "same_protocol"]]
              .to_string(index=False), flush=True)
    return pd.DataFrame([row]), ds


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--instance", default="RS[5,3]")
    p.add_argument("--episodes", type=int, default=100, help="episodes per seed (diagnostic: 100)")
    p.add_argument("--quick", action="store_true", help="smoke test: 3 episodes, 2 seeds, scratch output")
    p.add_argument("--out", default="results/results_rocksample_efe_diagnostic.csv")
    args = p.parse_args()
    seeds, episodes, out = list(SEEDS), args.episodes, args.out
    if args.quick:
        seeds, episodes = seeds[:2], 3
        out = os.path.join(os.environ.get("TMPDIR", "/tmp"), "results_rocksample_efe_diagnostic_quick.csv")
        print("QUICK MODE: scratch output, canonical CSVs untouched", flush=True)
    run(args.instance, episodes, seeds, out, out.replace(".csv", "_stats.csv"))


if __name__ == "__main__":
    main()
