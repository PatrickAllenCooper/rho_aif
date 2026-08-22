#!/usr/bin/env python3
"""
Compute-matched POMCP comparison (Stage K item 6).

The main POMCP comparison (Appendix app:pomcp) and the MCTS-EFE comparison
are simulation-matched, not compute-matched: MCTS-EFE's leaf evaluations are
more expensive per simulation, so at equal simulation counts POMCP finishes
faster. This script finds, empirically and on this machine, the POMCP
simulation count whose wall-clock time for the full Tiger H=10 protocol
(200 episodes x 5 seeds) matches MCTS-EFE(500)'s wall-clock time for the
same protocol, then reports POMCP's success rate at that matched budget.

Saves results/results_pomcp_compute_matched.csv.
"""

import os
import time

import numpy as np
import pandas as pd

from rho_aif.environments.tiger import TigerEnv
from rho_aif.agents.mcts_efe import MCTSEFEAgent
from rho_aif.agents.pomcp import POMCPAgent
from rho_aif.stats import seed_level_ttest
from run_experiment import run_experiment_multi_seed, summarize_results, provenance_fields, SEEDS


def timed_run(agent_cls, env, num_episodes, seeds, **kwargs):
    t0 = time.time()
    raw = run_experiment_multi_seed(agent_cls, env, num_episodes, seeds=seeds, **kwargs)
    elapsed = time.time() - t0
    return raw, elapsed


def main():
    os.makedirs("results", exist_ok=True)
    env = TigerEnv(
        listen_accuracy=0.85, listen_cost=1.0,
        correct_reward=10.0, incorrect_penalty=-100.0,
    )
    seeds = SEEDS
    num_episodes = 200
    horizon = 10

    print("=" * 70)
    print("Compute-matched POMCP comparison: Tiger H=10")
    print("=" * 70)

    print("\n[1/3] Timing MCTS-EFE(500) target budget...", flush=True)
    mcts_raw, mcts_time = timed_run(
        MCTSEFEAgent, env, num_episodes, seeds,
        num_simulations=500, planning_horizon=horizon, rollout_depth=3,
    )
    mcts_s = summarize_results(mcts_raw)
    print(
        f"    MCTS-EFE(500): success={mcts_s['success_rate']:.1%}  "
        f"reward={mcts_s['mean_reward']:+.3f}  obs={mcts_s['mean_observations']:.2f}  "
        f"wall_clock={mcts_time:.2f}s"
    )

    print("\n[2/3] Calibrating POMCP wall-clock scaling on this machine...", flush=True)
    calib_budgets = [200, 500, 1000]
    calib_times = []
    for n_sims in calib_budgets:
        _, t = timed_run(
            POMCPAgent, env, num_episodes, seeds,
            num_simulations=n_sims, rollout_depth=horizon + 3, exploration_constant=5.0,
        )
        calib_times.append(t)
        print(f"    POMCP({n_sims}): wall_clock={t:.2f}s", flush=True)

    # Linear fit sims -> wall_clock_s, then invert to find the sim count
    # whose wall-clock time matches mcts_time on this machine.
    slope, intercept = np.polyfit(calib_budgets, calib_times, 1)
    matched_sims = int(round((mcts_time - intercept) / slope))
    matched_sims = max(50, matched_sims)
    print(
        f"    Linear fit: wall_clock = {intercept:.3f} + {slope:.5f} * n_sims "
        f"-> matched budget for {mcts_time:.2f}s is n_sims={matched_sims}"
    )

    print(f"\n[3/3] Running POMCP at matched budget n_sims={matched_sims} "
          f"and at the simulation-matched budget n_sims=500...", flush=True)
    pomcp_raw, pomcp_time = timed_run(
        POMCPAgent, env, num_episodes, seeds,
        num_simulations=matched_sims, rollout_depth=horizon + 3, exploration_constant=5.0,
    )
    pomcp_s = summarize_results(pomcp_raw)
    print(
        f"    POMCP({matched_sims}) [compute-matched]: success={pomcp_s['success_rate']:.1%}  "
        f"reward={pomcp_s['mean_reward']:+.3f}  obs={pomcp_s['mean_observations']:.2f}  "
        f"wall_clock={pomcp_time:.2f}s (target was {mcts_time:.2f}s)"
    )

    # Simulation-matched arm (same n_sims=500 as MCTS-EFE), run fresh in this
    # same script so the comparison p-value is computed on a contemporaneous
    # pair rather than mixed with a possibly-stale results_mcts_efe.csv row.
    pomcp500_raw, pomcp500_time = timed_run(
        POMCPAgent, env, num_episodes, seeds,
        num_simulations=500, rollout_depth=horizon + 3, exploration_constant=5.0,
    )
    pomcp500_s = summarize_results(pomcp500_raw)
    print(
        f"    POMCP(500) [simulation-matched]: success={pomcp500_s['success_rate']:.1%}  "
        f"reward={pomcp500_s['mean_reward']:+.3f}  wall_clock={pomcp500_time:.2f}s"
    )

    cmp_compute_matched_success = seed_level_ttest(mcts_raw, pomcp_raw, lambda r: float(r.success))
    cmp_compute_matched_reward = seed_level_ttest(mcts_raw, pomcp_raw, lambda r: r.total_reward)
    cmp_sim_matched_success = seed_level_ttest(mcts_raw, pomcp500_raw, lambda r: float(r.success))
    cmp_sim_matched_reward = seed_level_ttest(mcts_raw, pomcp500_raw, lambda r: r.total_reward)
    # The manuscript claim this script backs is specifically "does giving POMCP
    # more simulations to spend the same wall-clock budget change its own
    # performance" -- i.e. POMCP(matched_sims) vs POMCP(500), not either POMCP
    # arm vs MCTS-EFE (which is a different, and here strongly significant,
    # comparison -- see the two blocks above).
    cmp_pomcp_vs_pomcp_success = seed_level_ttest(pomcp_raw, pomcp500_raw, lambda r: float(r.success))
    cmp_pomcp_vs_pomcp_reward = seed_level_ttest(pomcp_raw, pomcp500_raw, lambda r: r.total_reward)
    print(
        f"\n    Seed-level Welch vs. MCTS-EFE(500): "
        f"compute-matched success p={cmp_compute_matched_success['p_value']:.4g}, "
        f"reward p={cmp_compute_matched_reward['p_value']:.4g}; "
        f"simulation-matched success p={cmp_sim_matched_success['p_value']:.4g}, "
        f"reward p={cmp_sim_matched_reward['p_value']:.4g}"
    )
    print(
        f"    Seed-level Welch, POMCP({matched_sims}) [compute-matched] vs. POMCP(500) "
        f"[simulation-matched]: success p={cmp_pomcp_vs_pomcp_success['p_value']:.4g}, "
        f"reward p={cmp_pomcp_vs_pomcp_reward['p_value']:.4g}"
    )

    rows = [
        {
            "env": "Tiger", "horizon": horizon, "agent": "MCTS-EFE(500)",
            "sim_budget": 500, "success": mcts_s["success_rate"],
            "reward": mcts_s["mean_reward"], "obs": mcts_s["mean_observations"],
            "wall_clock_s": mcts_time,
            "n_seeds": mcts_s.get("n_seeds", float("nan")),
            "se_success_seed_level": mcts_s.get("se_success_seed_level", float("nan")),
            "se_reward_seed_level": mcts_s.get("se_reward_seed_level", float("nan")),
        },
        {
            "env": "Tiger", "horizon": horizon, "agent": f"POMCP({matched_sims})_compute_matched",
            "sim_budget": matched_sims, "success": pomcp_s["success_rate"],
            "reward": pomcp_s["mean_reward"], "obs": pomcp_s["mean_observations"],
            "wall_clock_s": pomcp_time,
            "n_seeds": pomcp_s.get("n_seeds", float("nan")),
            "se_success_seed_level": pomcp_s.get("se_success_seed_level", float("nan")),
            "se_reward_seed_level": pomcp_s.get("se_reward_seed_level", float("nan")),
            "p_success_vs_mcts_seed_level": cmp_compute_matched_success["p_value"],
            "p_reward_vs_mcts_seed_level": cmp_compute_matched_reward["p_value"],
            "p_success_vs_simulation_matched_pomcp_seed_level": cmp_pomcp_vs_pomcp_success["p_value"],
            "p_reward_vs_simulation_matched_pomcp_seed_level": cmp_pomcp_vs_pomcp_reward["p_value"],
        },
        {
            "env": "Tiger", "horizon": horizon, "agent": "POMCP(500)_simulation_matched",
            "sim_budget": 500, "success": pomcp500_s["success_rate"],
            "reward": pomcp500_s["mean_reward"], "obs": pomcp500_s["mean_observations"],
            "wall_clock_s": pomcp500_time,
            "n_seeds": pomcp500_s.get("n_seeds", float("nan")),
            "se_success_seed_level": pomcp500_s.get("se_success_seed_level", float("nan")),
            "se_reward_seed_level": pomcp500_s.get("se_reward_seed_level", float("nan")),
            "p_success_vs_mcts_seed_level": cmp_sim_matched_success["p_value"],
            "p_reward_vs_mcts_seed_level": cmp_sim_matched_reward["p_value"],
        },
    ]
    for r in rows:
        r.update(provenance_fields(seeds, num_episodes))
        r["calibration_fit_slope"] = slope
        r["calibration_fit_intercept"] = intercept
        r["calibration_budgets"] = "|".join(str(b) for b in calib_budgets)
        r["calibration_times_s"] = "|".join(f"{t:.3f}" for t in calib_times)

    df = pd.DataFrame(rows)
    csv_path = "results/results_pomcp_compute_matched.csv"
    df.to_csv(csv_path, index=False)
    print(f"\nSaved {csv_path}")


if __name__ == "__main__":
    main()
