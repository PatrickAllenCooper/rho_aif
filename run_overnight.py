#!/usr/bin/env python3
"""
Master overnight experiment runner with checkpointing.

Runs all experiment groups (A-I) sequentially, saving results incrementally.
Each completed group is recorded in checkpoint.json so the script can be
restarted without re-running finished experiments.

Usage:
    python run_overnight.py           # run all pending groups
    python run_overnight.py --reset   # clear checkpoint and run everything
    python run_overnight.py --status  # show checkpoint status
"""

import json
import os
import sys
import time
import traceback
from datetime import datetime

CHECKPOINT_FILE = "checkpoint_overnight.json"


def load_checkpoint():
    if os.path.exists(CHECKPOINT_FILE):
        with open(CHECKPOINT_FILE) as f:
            return json.load(f)
    return {"completed": [], "started": None, "log": []}


def save_checkpoint(ckpt):
    with open(CHECKPOINT_FILE, "w") as f:
        json.dump(ckpt, f, indent=2)


def mark_started(ckpt, group_id):
    ckpt["started"] = group_id
    ckpt["log"].append({"group": group_id, "event": "started", "time": datetime.now().isoformat()})
    save_checkpoint(ckpt)


def mark_completed(ckpt, group_id):
    if group_id not in ckpt["completed"]:
        ckpt["completed"].append(group_id)
    ckpt["started"] = None
    ckpt["log"].append({"group": group_id, "event": "completed", "time": datetime.now().isoformat()})
    save_checkpoint(ckpt)


def mark_failed(ckpt, group_id, error_msg):
    ckpt["started"] = None
    ckpt["log"].append({"group": group_id, "event": "failed", "time": datetime.now().isoformat(), "error": error_msg})
    save_checkpoint(ckpt)


# ---------------------------------------------------------------------------
# Group A: Core multi-seed experiments
# ---------------------------------------------------------------------------
def run_group_a():
    from run_experiment import (
        run_info_seeking_experiment, run_tiger_experiment,
        run_diagnosis_experiment, run_bandit_experiment,
        run_navigation_experiment, run_scaling_analysis,
    )

    print("\n" + "#" * 72)
    print("# GROUP A: Core multi-seed experiments")
    print("#" * 72)

    print("\n[A.1] Info-seeking testbed")
    run_info_seeking_experiment()

    print("\n[A.2] Tiger")
    run_tiger_experiment()

    print("\n[A.3] Diagnosis N=4")
    run_diagnosis_experiment()

    print("\n[A.4] Bandit K=4")
    run_bandit_experiment()

    print("\n[A.5] Navigation 3x3")
    run_navigation_experiment()

    print("\n[A.6] Scaling analysis")
    run_scaling_analysis()


# ---------------------------------------------------------------------------
# Group B: RockSample with all baselines
# ---------------------------------------------------------------------------
def run_group_b():
    from run_rocksample import run_rocksample_experiment

    print("\n" + "#" * 72)
    print("# GROUP B: RockSample with all baselines")
    print("#" * 72)

    for gs, nr in [(5, 3), (7, 4)]:
        print(f"\n[B] RockSample[{gs},{nr}]")
        run_rocksample_experiment(grid_size=gs, num_rocks=nr)


# ---------------------------------------------------------------------------
# Group C: POMCP compute-matched comparison
# ---------------------------------------------------------------------------
def run_group_c():
    from run_pomcp import run_pomcp_comparison

    print("\n" + "#" * 72)
    print("# GROUP C: POMCP compute-matched with wall-clock timing")
    print("#" * 72)

    run_pomcp_comparison()


# ---------------------------------------------------------------------------
# Group D: MCTS-EFE experiments
# ---------------------------------------------------------------------------
def run_group_d():
    from run_mcts_experiments import run_mcts_tiger_sweep, run_mcts_tileworld

    print("\n" + "#" * 72)
    print("# GROUP D: MCTS-EFE approximate planning")
    print("#" * 72)

    rows = run_mcts_tiger_sweep()
    run_mcts_tileworld(existing_rows=rows)


# ---------------------------------------------------------------------------
# Group E: Pareto frontier and accuracy sensitivity
# ---------------------------------------------------------------------------
def run_group_e():
    from run_pareto import run_pareto_sweep, plot_pareto, run_accuracy_sensitivity

    from environments.info_seeking import InfoSeekingEnv
    from environments.tiger import TigerEnv
    from environments.diagnosis import DiagnosisEnv
    from environments.bandit import BanditEnv

    print("\n" + "#" * 72)
    print("# GROUP E: Pareto frontier and accuracy sensitivity")
    print("#" * 72)

    envs_config = {
        "Tiger": (
            TigerEnv(listen_accuracy=0.85, listen_cost=1.0,
                     correct_reward=10.0, incorrect_penalty=-100.0), 6),
        "Testbed": (
            InfoSeekingEnv(observation_accuracy=0.75, observation_cost=0.1,
                           correct_reward=1.0, incorrect_penalty=-1.0), 4),
        "Diagnosis": (
            DiagnosisEnv(num_conditions=4, test_accuracy=0.80, test_cost=1.0,
                         correct_reward=10.0, incorrect_penalty=-50.0), 3),
        "Bandit": (
            BanditEnv(num_arms=4, inspect_accuracy=0.80, inspect_cost=0.5,
                      correct_reward=10.0, small_reward=1.0), 2),
    }

    print("\n[E.1] Pareto sweep")
    all_results = {}
    for env_name, (env, horizon) in envs_config.items():
        print(f"\n  Pareto sweep: {env_name} (H={horizon})")
        all_results[env_name] = run_pareto_sweep(env, horizon, num_episodes=500)
    plot_pareto(all_results)

    print("\n[E.2] Accuracy sensitivity")
    run_accuracy_sensitivity()


# ---------------------------------------------------------------------------
# Group F: Tileworld experiments
# ---------------------------------------------------------------------------
def run_group_f():
    from run_tileworld import run_tileworld_experiment, fig_scaling
    from run_tileworld import fig_belief_evolution, fig_agent_comparison
    from environments.tileworld import TileworldEnv
    from render_tileworld import render_scan_atlas

    print("\n" + "#" * 72)
    print("# GROUP F: Tileworld experiments and figures")
    print("#" * 72)

    print("\n[F.1] Tileworld 6x6 full experiment")
    run_tileworld_experiment(grid_size=6, num_episodes=500)

    print("\n[F.2] Tileworld figures")
    render_scan_atlas(TileworldEnv(grid_size=6), "figures/fig_tileworld_scan_atlas.pdf")
    fig_belief_evolution()
    fig_agent_comparison()
    fig_scaling()


# ---------------------------------------------------------------------------
# Group G: Model misspecification
# ---------------------------------------------------------------------------
def run_group_g():
    from run_model_misspec import run_misspec_sweep

    print("\n" + "#" * 72)
    print("# GROUP G: Model misspecification (multi-seed)")
    print("#" * 72)

    run_misspec_sweep()


# ---------------------------------------------------------------------------
# Group H: Statistical analysis
# ---------------------------------------------------------------------------
def run_group_h():
    from run_supplementary import main as run_supplementary_main

    print("\n" + "#" * 72)
    print("# GROUP H: Statistical analysis (bootstrap CIs, effect sizes)")
    print("#" * 72)

    run_supplementary_main()


# ---------------------------------------------------------------------------
# Group I: Supplementary figures
# ---------------------------------------------------------------------------
def run_group_i():
    from run_visualizations import (
        fig_belief_heatmap, fig_efficiency_curves,
        fig_extended_efe, fig_stopping_times,
    )
    from run_showcase import (
        run_reward_asymmetry_sweep, plot_reward_asymmetry_sweep,
        run_obs_action_scaling, plot_obs_action_scaling,
        collect_trajectories, plot_efe_trajectories,
    )
    from run_experiment import make_agent
    from agents.efe import EFEAgent
    from environments.tiger import TigerEnv
    import numpy as np

    print("\n" + "#" * 72)
    print("# GROUP I: Supplementary figures")
    print("#" * 72)

    print("\n[I.1] Visualization figures")
    fig_belief_heatmap()
    fig_efficiency_curves()
    fig_extended_efe()
    fig_stopping_times()

    print("\n[I.2] Showcase figures")
    sweep_results = run_reward_asymmetry_sweep(
        penalties=[1, 2, 5, 10, 20, 50, 100, 200, 500],
        num_episodes=500, horizon=6,
    )
    plot_reward_asymmetry_sweep(sweep_results)

    np.random.seed(42)
    tiger_env = TigerEnv(listen_accuracy=0.85, listen_cost=1.0,
                         correct_reward=10.0, incorrect_penalty=-100.0)
    agent = make_agent(EFEAgent, tiger_env, planning_horizon=6)
    trajectories = collect_trajectories(tiger_env, agent, n_episodes=50)
    plot_efe_trajectories(trajectories)

    obs_results = run_obs_action_scaling(n_states=8, num_episodes=500, horizon=3)
    plot_obs_action_scaling(obs_results)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

GROUPS = [
    ("A", "Core multi-seed experiments", run_group_a),
    ("B", "RockSample with all baselines", run_group_b),
    ("C", "POMCP compute-matched comparison", run_group_c),
    ("D", "MCTS-EFE approximate planning", run_group_d),
    ("E", "Pareto + accuracy sensitivity", run_group_e),
    ("F", "Tileworld experiments", run_group_f),
    ("G", "Model misspecification", run_group_g),
    ("H", "Statistical analysis", run_group_h),
    ("I", "Supplementary figures", run_group_i),
]


def main():
    os.makedirs("figures", exist_ok=True)

    if "--reset" in sys.argv:
        if os.path.exists(CHECKPOINT_FILE):
            os.remove(CHECKPOINT_FILE)
        print("Checkpoint cleared.")

    if "--status" in sys.argv:
        ckpt = load_checkpoint()
        print("Overnight experiment status:")
        for gid, desc, _ in GROUPS:
            status = "DONE" if gid in ckpt["completed"] else "PENDING"
            if ckpt.get("started") == gid:
                status = "IN PROGRESS"
            print(f"  [{status:11s}] Group {gid}: {desc}")
        return

    ckpt = load_checkpoint()
    t_global = time.time()

    print("=" * 72)
    print("OVERNIGHT EXPERIMENT SUITE")
    print(f"Started: {datetime.now().isoformat()}")
    print(f"Already completed: {ckpt['completed']}")
    print("=" * 72)

    for group_id, description, run_fn in GROUPS:
        if group_id in ckpt["completed"]:
            print(f"\n[SKIP] Group {group_id}: {description} (already completed)")
            continue

        print(f"\n{'*' * 72}")
        print(f"[START] Group {group_id}: {description}")
        print(f"  Time: {datetime.now().isoformat()}")
        print(f"  Elapsed: {(time.time() - t_global) / 60:.1f} min total")
        print(f"{'*' * 72}")

        mark_started(ckpt, group_id)
        t0 = time.time()

        try:
            run_fn()
            elapsed = time.time() - t0
            mark_completed(ckpt, group_id)
            print(f"\n[DONE] Group {group_id}: {description} ({elapsed/60:.1f} min)")
        except Exception as e:
            elapsed = time.time() - t0
            error_msg = f"{type(e).__name__}: {e}"
            mark_failed(ckpt, group_id, error_msg)
            print(f"\n[FAIL] Group {group_id}: {description} ({elapsed/60:.1f} min)")
            print(f"  Error: {error_msg}")
            traceback.print_exc()
            print("\n  Continuing to next group...")
            continue

    total_time = time.time() - t_global
    print("\n" + "=" * 72)
    print(f"OVERNIGHT SUITE COMPLETE")
    print(f"  Total time: {total_time/3600:.1f} hours ({total_time/60:.0f} min)")
    print(f"  Completed: {ckpt['completed']}")
    print(f"  Finished: {datetime.now().isoformat()}")
    print("=" * 72)


if __name__ == "__main__":
    main()
