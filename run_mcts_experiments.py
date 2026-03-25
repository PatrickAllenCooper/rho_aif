#!/usr/bin/env python3
"""
MCTS-EFE experiments: approximate planning with EFE as leaf heuristic.

Demonstrates that MCTS-EFE scales to higher horizons where exact tree search
is infeasible, while preserving the epistemic-pragmatic balance. Compares
against exact EFE and POMCP at matched simulation budgets.

Saves results incrementally to results_mcts_efe.csv.
"""

import numpy as np
import pandas as pd
import time
import os

from environments.tiger import TigerEnv
from environments.tileworld import TileworldEnv
from environments.diagnosis import DiagnosisEnv
from agents.mcts_efe import MCTSEFEAgent
from agents.efe import EFEAgent
from agents.pomcp import POMCPAgent
from run_experiment import (
    make_agent, run_experiment, run_experiment_multi_seed,
    summarize_results, SEEDS,
)


def run_mcts_tiger_sweep(seeds=None, csv_path="results_mcts_efe.csv"):
    """Sweep MCTS-EFE on Tiger at multiple horizons and simulation budgets."""
    if seeds is None:
        seeds = SEEDS

    env = TigerEnv(
        listen_accuracy=0.85, listen_cost=1.0,
        correct_reward=10.0, incorrect_penalty=-100.0,
    )

    horizons = [6, 8, 10]
    sim_budgets = [200, 500, 1000]
    num_episodes = 200
    total_ep = num_episodes * len(seeds)
    rows = []

    print("=" * 70)
    print("MCTS-EFE EXPERIMENTS: Tiger")
    print("=" * 70)

    for horizon in horizons:
        print(f"\n--- Horizon H={horizon} ---")

        if horizon <= 6:
            print(f"  Running Exact EFE (H={horizon})...", flush=True)
            t0 = time.time()
            exact_raw = run_experiment_multi_seed(
                EFEAgent, env, num_episodes, seeds=seeds,
                planning_horizon=horizon,
            )
            exact_s = summarize_results(exact_raw)
            exact_time = time.time() - t0
            rows.append({
                "env": "Tiger", "agent": f"Exact-EFE", "horizon": horizon,
                "sim_budget": 0, "success": exact_s["success_rate"],
                "reward": exact_s["mean_reward"], "std_reward": exact_s["std_reward"],
                "obs": exact_s["mean_observations"],
                "wall_clock_s": exact_time, "ms_per_ep": exact_time / total_ep * 1000,
            })
            print(
                f"    Exact EFE(H={horizon}): success={exact_s['success_rate']:.1%}  "
                f"reward={exact_s['mean_reward']:+.3f}  "
                f"obs={exact_s['mean_observations']:.2f}  ({exact_time:.1f}s)"
            )

        for n_sims in sim_budgets:
            print(f"  Running MCTS-EFE (H={horizon}, sims={n_sims})...", flush=True)
            t0 = time.time()
            mcts_raw = run_experiment_multi_seed(
                MCTSEFEAgent, env, num_episodes, seeds=seeds,
                num_simulations=n_sims,
                planning_horizon=horizon,
                rollout_depth=3,
            )
            mcts_s = summarize_results(mcts_raw)
            mcts_time = time.time() - t0
            rows.append({
                "env": "Tiger", "agent": f"MCTS-EFE({n_sims})",
                "horizon": horizon, "sim_budget": n_sims,
                "success": mcts_s["success_rate"],
                "reward": mcts_s["mean_reward"], "std_reward": mcts_s["std_reward"],
                "obs": mcts_s["mean_observations"],
                "wall_clock_s": mcts_time, "ms_per_ep": mcts_time / total_ep * 1000,
            })
            print(
                f"    MCTS-EFE({n_sims}): success={mcts_s['success_rate']:.1%}  "
                f"reward={mcts_s['mean_reward']:+.3f}  "
                f"obs={mcts_s['mean_observations']:.2f}  ({mcts_time:.1f}s)"
            )

            print(f"  Running POMCP (H={horizon}, sims={n_sims})...", flush=True)
            t0 = time.time()
            pomcp_raw = run_experiment_multi_seed(
                POMCPAgent, env, num_episodes, seeds=seeds,
                num_simulations=n_sims,
                rollout_depth=horizon + 3,
                exploration_constant=5.0,
            )
            pomcp_s = summarize_results(pomcp_raw)
            pomcp_time = time.time() - t0
            rows.append({
                "env": "Tiger", "agent": f"POMCP({n_sims})",
                "horizon": horizon, "sim_budget": n_sims,
                "success": pomcp_s["success_rate"],
                "reward": pomcp_s["mean_reward"], "std_reward": pomcp_s["std_reward"],
                "obs": pomcp_s["mean_observations"],
                "wall_clock_s": pomcp_time, "ms_per_ep": pomcp_time / total_ep * 1000,
            })
            print(
                f"    POMCP({n_sims}): success={pomcp_s['success_rate']:.1%}  "
                f"reward={pomcp_s['mean_reward']:+.3f}  "
                f"obs={pomcp_s['mean_observations']:.2f}  ({pomcp_time:.1f}s)"
            )

        pd.DataFrame(rows).to_csv(csv_path, index=False)
        print(f"  [checkpoint] saved {len(rows)} rows to {csv_path}")

    return rows


def run_mcts_tileworld(seeds=None, csv_path="results_mcts_efe.csv", existing_rows=None):
    """Run MCTS-EFE on small Tileworld (4x4) if feasible."""
    if seeds is None:
        seeds = SEEDS

    rows = list(existing_rows) if existing_rows else []

    env = TileworldEnv(
        grid_size=4, scan_accuracy=0.80, scan_cost=1.0,
        correct_reward=10.0, incorrect_penalty=-50.0,
    )

    num_episodes = 200
    total_ep = num_episodes * len(seeds)
    horizon = 2

    print("\n" + "=" * 70)
    print("MCTS-EFE EXPERIMENTS: Tileworld 4x4")
    print("=" * 70)

    print("  Running Exact EFE (H=2)...", flush=True)
    t0 = time.time()
    exact_raw = run_experiment_multi_seed(
        EFEAgent, env, num_episodes, seeds=seeds, planning_horizon=horizon,
    )
    exact_s = summarize_results(exact_raw)
    exact_time = time.time() - t0
    rows.append({
        "env": "Tileworld-4x4", "agent": "Exact-EFE", "horizon": horizon,
        "sim_budget": 0, "success": exact_s["success_rate"],
        "reward": exact_s["mean_reward"], "std_reward": exact_s["std_reward"],
        "obs": exact_s["mean_observations"],
        "wall_clock_s": exact_time, "ms_per_ep": exact_time / total_ep * 1000,
    })
    print(
        f"    Exact EFE: success={exact_s['success_rate']:.1%}  "
        f"reward={exact_s['mean_reward']:+.3f}  ({exact_time:.1f}s)"
    )

    for n_sims in [200, 500]:
        print(f"  Running MCTS-EFE (sims={n_sims})...", flush=True)
        t0 = time.time()
        mcts_raw = run_experiment_multi_seed(
            MCTSEFEAgent, env, num_episodes, seeds=seeds,
            num_simulations=n_sims, planning_horizon=horizon, rollout_depth=2,
        )
        mcts_s = summarize_results(mcts_raw)
        mcts_time = time.time() - t0
        rows.append({
            "env": "Tileworld-4x4", "agent": f"MCTS-EFE({n_sims})",
            "horizon": horizon, "sim_budget": n_sims,
            "success": mcts_s["success_rate"],
            "reward": mcts_s["mean_reward"], "std_reward": mcts_s["std_reward"],
            "obs": mcts_s["mean_observations"],
            "wall_clock_s": mcts_time, "ms_per_ep": mcts_time / total_ep * 1000,
        })
        print(
            f"    MCTS-EFE({n_sims}): success={mcts_s['success_rate']:.1%}  "
            f"reward={mcts_s['mean_reward']:+.3f}  ({mcts_time:.1f}s)"
        )

        print(f"  Running POMCP (sims={n_sims})...", flush=True)
        t0 = time.time()
        pomcp_raw = run_experiment_multi_seed(
            POMCPAgent, env, num_episodes, seeds=seeds,
            num_simulations=n_sims, rollout_depth=horizon + 3,
            exploration_constant=5.0,
        )
        pomcp_s = summarize_results(pomcp_raw)
        pomcp_time = time.time() - t0
        rows.append({
            "env": "Tileworld-4x4", "agent": f"POMCP({n_sims})",
            "horizon": horizon, "sim_budget": n_sims,
            "success": pomcp_s["success_rate"],
            "reward": pomcp_s["mean_reward"], "std_reward": pomcp_s["std_reward"],
            "obs": pomcp_s["mean_observations"],
            "wall_clock_s": pomcp_time, "ms_per_ep": pomcp_time / total_ep * 1000,
        })
        print(
            f"    POMCP({n_sims}): success={pomcp_s['success_rate']:.1%}  "
            f"reward={pomcp_s['mean_reward']:+.3f}  ({pomcp_time:.1f}s)"
        )

    pd.DataFrame(rows).to_csv(csv_path, index=False)
    print(f"  [checkpoint] saved {len(rows)} rows to {csv_path}")
    return rows


def run_mcts_tileworld_6x6(seeds=None, csv_path="results_mcts_efe.csv", existing_rows=None):
    """Run MCTS-EFE on Tileworld 6x6 (|S|=36, K=6 scans)."""
    if seeds is None:
        seeds = SEEDS[:5]

    rows = list(existing_rows) if existing_rows else []

    env = TileworldEnv(
        grid_size=6, scan_accuracy=0.80, scan_cost=1.0,
        correct_reward=10.0, incorrect_penalty=-50.0,
    )

    num_episodes = 200
    total_ep = num_episodes * len(seeds)
    horizon = 2

    print("\n" + "=" * 70)
    print("MCTS-EFE EXPERIMENTS: Tileworld 6x6")
    print("=" * 70)

    print("  Running Exact EFE (H=2)...", flush=True)
    t0 = time.time()
    exact_raw = run_experiment_multi_seed(
        EFEAgent, env, num_episodes, seeds=seeds, planning_horizon=horizon,
    )
    exact_s = summarize_results(exact_raw)
    exact_time = time.time() - t0
    rows.append({
        "env": "Tileworld-6x6", "agent": "Exact-EFE", "horizon": horizon,
        "sim_budget": 0, "success": exact_s["success_rate"],
        "reward": exact_s["mean_reward"], "std_reward": exact_s["std_reward"],
        "obs": exact_s["mean_observations"],
        "wall_clock_s": exact_time, "ms_per_ep": exact_time / total_ep * 1000,
    })
    print(
        f"    Exact EFE: success={exact_s['success_rate']:.1%}  "
        f"reward={exact_s['mean_reward']:+.3f}  ({exact_time:.1f}s)"
    )

    for n_sims in [200, 500]:
        print(f"  Running MCTS-EFE (sims={n_sims})...", flush=True)
        t0 = time.time()
        mcts_raw = run_experiment_multi_seed(
            MCTSEFEAgent, env, num_episodes, seeds=seeds,
            num_simulations=n_sims, planning_horizon=horizon, rollout_depth=2,
        )
        mcts_s = summarize_results(mcts_raw)
        mcts_time = time.time() - t0
        rows.append({
            "env": "Tileworld-6x6", "agent": f"MCTS-EFE({n_sims})",
            "horizon": horizon, "sim_budget": n_sims,
            "success": mcts_s["success_rate"],
            "reward": mcts_s["mean_reward"], "std_reward": mcts_s["std_reward"],
            "obs": mcts_s["mean_observations"],
            "wall_clock_s": mcts_time, "ms_per_ep": mcts_time / total_ep * 1000,
        })
        print(
            f"    MCTS-EFE({n_sims}): success={mcts_s['success_rate']:.1%}  "
            f"reward={mcts_s['mean_reward']:+.3f}  ({mcts_time:.1f}s)"
        )

        print(f"  Running POMCP (sims={n_sims})...", flush=True)
        t0 = time.time()
        pomcp_raw = run_experiment_multi_seed(
            POMCPAgent, env, num_episodes, seeds=seeds,
            num_simulations=n_sims, rollout_depth=horizon + 3,
            exploration_constant=5.0,
        )
        pomcp_s = summarize_results(pomcp_raw)
        pomcp_time = time.time() - t0
        rows.append({
            "env": "Tileworld-6x6", "agent": f"POMCP({n_sims})",
            "horizon": horizon, "sim_budget": n_sims,
            "success": pomcp_s["success_rate"],
            "reward": pomcp_s["mean_reward"], "std_reward": pomcp_s["std_reward"],
            "obs": pomcp_s["mean_observations"],
            "wall_clock_s": pomcp_time, "ms_per_ep": pomcp_time / total_ep * 1000,
        })
        print(
            f"    POMCP({n_sims}): success={pomcp_s['success_rate']:.1%}  "
            f"reward={pomcp_s['mean_reward']:+.3f}  ({pomcp_time:.1f}s)"
        )

    pd.DataFrame(rows).to_csv(csv_path, index=False)
    print(f"  [checkpoint] saved {len(rows)} rows to {csv_path}")
    return rows


def run_mcts_diagnosis_sweep(seeds=None, csv_path="results_mcts_efe.csv", existing_rows=None):
    """Sweep MCTS-EFE on Diagnosis (N=4, K=2 tests) at multiple horizons.

    Diagnosis has 2 observation actions with 2 outcomes each, testing MCTS-EFE
    on a multi-observation environment where exact tree search at higher
    horizons is intractable.
    """
    if seeds is None:
        seeds = SEEDS

    rows = list(existing_rows) if existing_rows else []

    env = DiagnosisEnv(
        num_conditions=4, test_accuracy=0.80, test_cost=1.0,
        correct_reward=10.0, incorrect_penalty=-50.0,
    )

    num_episodes = 200
    total_ep = num_episodes * len(seeds)

    print("\n" + "=" * 70)
    print("MCTS-EFE EXPERIMENTS: Diagnosis (N=4, K=2)")
    print("=" * 70)

    print("  Running Exact EFE (H=3)...", flush=True)
    t0 = time.time()
    exact_raw = run_experiment_multi_seed(
        EFEAgent, env, num_episodes, seeds=seeds, planning_horizon=3,
    )
    exact_s = summarize_results(exact_raw)
    exact_time = time.time() - t0
    rows.append({
        "env": "Diagnosis-N4", "agent": "Exact-EFE", "horizon": 3,
        "sim_budget": 0, "success": exact_s["success_rate"],
        "reward": exact_s["mean_reward"], "std_reward": exact_s["std_reward"],
        "obs": exact_s["mean_observations"],
        "wall_clock_s": exact_time, "ms_per_ep": exact_time / total_ep * 1000,
    })
    print(
        f"    Exact EFE(H=3): success={exact_s['success_rate']:.1%}  "
        f"reward={exact_s['mean_reward']:+.3f}  "
        f"obs={exact_s['mean_observations']:.2f}  ({exact_time:.1f}s)"
    )

    configs = [
        (3, 200), (5, 200), (5, 500), (7, 200), (7, 500),
    ]
    for horizon, n_sims in configs:
        print(f"  Running MCTS-EFE (H={horizon}, sims={n_sims})...", flush=True)
        t0 = time.time()
        mcts_raw = run_experiment_multi_seed(
            MCTSEFEAgent, env, num_episodes, seeds=seeds,
            num_simulations=n_sims,
            planning_horizon=horizon,
            rollout_depth=3,
        )
        mcts_s = summarize_results(mcts_raw)
        mcts_time = time.time() - t0
        rows.append({
            "env": "Diagnosis-N4", "agent": f"MCTS-EFE({n_sims})",
            "horizon": horizon, "sim_budget": n_sims,
            "success": mcts_s["success_rate"],
            "reward": mcts_s["mean_reward"], "std_reward": mcts_s["std_reward"],
            "obs": mcts_s["mean_observations"],
            "wall_clock_s": mcts_time, "ms_per_ep": mcts_time / total_ep * 1000,
        })
        print(
            f"    MCTS-EFE({n_sims}): success={mcts_s['success_rate']:.1%}  "
            f"reward={mcts_s['mean_reward']:+.3f}  "
            f"obs={mcts_s['mean_observations']:.2f}  ({mcts_time:.1f}s)"
        )

        print(f"  Running POMCP (H={horizon}, sims={n_sims})...", flush=True)
        t0 = time.time()
        pomcp_raw = run_experiment_multi_seed(
            POMCPAgent, env, num_episodes, seeds=seeds,
            num_simulations=n_sims,
            rollout_depth=horizon + 3,
            exploration_constant=5.0,
        )
        pomcp_s = summarize_results(pomcp_raw)
        pomcp_time = time.time() - t0
        rows.append({
            "env": "Diagnosis-N4", "agent": f"POMCP({n_sims})",
            "horizon": horizon, "sim_budget": n_sims,
            "success": pomcp_s["success_rate"],
            "reward": pomcp_s["mean_reward"], "std_reward": pomcp_s["std_reward"],
            "obs": pomcp_s["mean_observations"],
            "wall_clock_s": pomcp_time, "ms_per_ep": pomcp_time / total_ep * 1000,
        })
        print(
            f"    POMCP({n_sims}): success={pomcp_s['success_rate']:.1%}  "
            f"reward={pomcp_s['mean_reward']:+.3f}  "
            f"obs={pomcp_s['mean_observations']:.2f}  ({pomcp_time:.1f}s)"
        )

        pd.DataFrame(rows).to_csv(csv_path, index=False)
        print(f"  [checkpoint] saved {len(rows)} rows to {csv_path}")

    return rows


if __name__ == "__main__":
    os.makedirs("figures", exist_ok=True)
    rows = run_mcts_tiger_sweep()
    rows = run_mcts_diagnosis_sweep(existing_rows=rows)
    run_mcts_tileworld(existing_rows=rows)
    print("\nAll MCTS-EFE results saved to results_mcts_efe.csv")
