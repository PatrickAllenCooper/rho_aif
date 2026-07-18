#!/usr/bin/env python3
"""
Overnight experiment runner: executes all experiments with full
multi-seed evaluation and saves results with checkpointing.
"""

import json
import time
import traceback
from datetime import datetime

CHECKPOINT_FILE = "checkpoint_overnight.json"


def load_checkpoint():
    try:
        with open(CHECKPOINT_FILE, "r") as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {"completed": [], "start_time": None}


def save_checkpoint(state):
    with open(CHECKPOINT_FILE, "w") as f:
        json.dump(state, f, indent=2)


def run_with_checkpoint(task_name, task_fn, state):
    if task_name in state["completed"]:
        print(f"\n[SKIP] {task_name} (already completed)")
        return

    print(f"\n{'='*70}")
    print(f"[START] {task_name} at {datetime.now().strftime('%H:%M:%S')}")
    print(f"{'='*70}")

    t0 = time.time()
    try:
        task_fn()
        dt = time.time() - t0
        print(f"\n[DONE] {task_name} in {dt:.0f}s")
        state["completed"].append(task_name)
        save_checkpoint(state)
    except Exception as e:
        dt = time.time() - t0
        print(f"\n[FAIL] {task_name} after {dt:.0f}s: {e}")
        traceback.print_exc()


def task_rocksample_53():
    from run_rocksample import run_rocksample_experiment
    run_rocksample_experiment(config_name="RS[5,3]", num_episodes=500)


def task_rocksample_74():
    from run_rocksample import run_rocksample_experiment
    run_rocksample_experiment(config_name="RS[7,4]", num_episodes=500)


def task_rocksample_78():
    from run_rocksample import run_rocksample_experiment
    run_rocksample_experiment(config_name="RS[7,8]", num_episodes=500)


def task_transfer():
    from run_transfer import run_transfer_experiment
    run_transfer_experiment(num_episodes=500)


def task_main_experiments():
    from run_experiment import (
        run_tiger_experiment, run_diagnosis_experiment,
        run_bandit_experiment, run_navigation_experiment,
        run_info_seeking_experiment,
    )
    run_info_seeking_experiment()
    run_tiger_experiment()
    run_diagnosis_experiment()
    run_bandit_experiment()
    run_navigation_experiment()


if __name__ == "__main__":
    state = load_checkpoint()
    if state["start_time"] is None:
        state["start_time"] = datetime.now().isoformat()
        save_checkpoint(state)

    print(f"Overnight run started at {state['start_time']}")
    print(f"Previously completed: {state['completed']}")

    tasks = [
        ("rocksample_53", task_rocksample_53),
        ("rocksample_74", task_rocksample_74),
        ("rocksample_78", task_rocksample_78),
        ("transfer", task_transfer),
        ("main_experiments", task_main_experiments),
    ]

    for name, fn in tasks:
        run_with_checkpoint(name, fn, state)

    print(f"\n{'='*70}")
    print(f"ALL TASKS COMPLETE at {datetime.now().strftime('%H:%M:%S')}")
    print(f"{'='*70}")
