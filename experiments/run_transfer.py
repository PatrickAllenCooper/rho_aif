#!/usr/bin/env python3
"""
Zero-shot transfer experiment: success-tuned vs reward-tuned weights.

Demonstrates that EFE's untuned w=1 generalizes across environments, while
per-environment tuned weights transfer poorly. Reports both:
  - w*_succ: success-maximizing (as used in prior transfer tables)
  - w*_ret:  reward-maximizing (addresses the review critique that transferring
             success-tuned weights while evaluating reward manufactures failure)
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT))
sys.path.insert(0, str(_ROOT / "experiments"))

import numpy as np
import pandas as pd

from rho_aif.agents.planning_infogain import PlanningInfoGainAgent
from rho_aif.environments.bandit import BanditEnv
from rho_aif.environments.diagnosis import DiagnosisEnv
from rho_aif.environments.info_seeking import InfoSeekingEnv
from rho_aif.environments.tiger import TigerEnv
from run_experiment import (
    SEEDS,
    provenance_fields,
    run_experiment_multi_seed,
    summarize_results,
)

# w*_succ from prior success-rate grid search; w*_ret from Pareto reward knee.
TRANSFER_ENVS = {
    "Tiger": {
        "make_env": lambda: TigerEnv(
            listen_accuracy=0.85,
            correct_reward=10.0,
            incorrect_penalty=-100.0,
            listen_cost=1.0,
        ),
        "horizon": 6,
        "w_succ": 20,
        "w_ret": 1.0,
    },
    "Diagnosis": {
        "make_env": lambda: DiagnosisEnv(
            num_conditions=4,
            test_accuracy=0.80,
            correct_reward=10.0,
            incorrect_penalty=-50.0,
            test_cost=1.0,
        ),
        "horizon": 3,
        "w_succ": 100,
        "w_ret": 0.5,
    },
    "Bandit": {
        "make_env": lambda: BanditEnv(
            num_arms=4,
            inspect_accuracy=0.80,
            correct_reward=10.0,
            small_reward=1.0,
            inspect_cost=0.5,
        ),
        "horizon": 2,
        "w_succ": 100,
        "w_ret": 1.0,
    },
    "Testbed": {
        "make_env": lambda: InfoSeekingEnv(
            observation_accuracy=0.75,
            correct_reward=1.0,
            incorrect_penalty=-1.0,
            observation_cost=0.1,
        ),
        "horizon": 4,
        "w_succ": 50,
        "w_ret": 0.5,
    },
}


def run_transfer_experiment(
    num_episodes: int = 500,
    seeds=None,
    output: Path = Path("results/results_transfer.csv"),
):
    if seeds is None:
        seeds = SEEDS[:5]

    # Evaluate w=1 plus every distinct success- and reward-tuned weight.
    weight_meta = {1.0: [("EFE", "canonical")]}
    for src_name, cfg in TRANSFER_ENVS.items():
        for kind, key in (("succ", "w_succ"), ("ret", "w_ret")):
            w = float(cfg[key])
            weight_meta.setdefault(w, []).append((src_name, kind))

    results = []

    for env_name, env_cfg in TRANSFER_ENVS.items():
        env = env_cfg["make_env"]()
        horizon = env_cfg["horizon"]
        print(f"\nEvaluating on {env_name} (H={horizon}):")
        print("-" * 60)

        for w in sorted(weight_meta):
            sources = weight_meta[w]
            source_parts = []
            for src, kind in sources:
                if src == "EFE":
                    source_parts.append("EFE (canonical w=1)")
                elif src == env_name:
                    source_parts.append(f"{kind}-tuned on {src} (native)")
                else:
                    source_parts.append(f"{kind}-tuned on {src} (transfer)")
            source_label = "; ".join(source_parts)

            all_episode_results = run_experiment_multi_seed(
                PlanningInfoGainAgent,
                env,
                num_episodes=num_episodes,
                seeds=seeds,
                planning_horizon=horizon,
                info_gain_weight=w,
            )
            summary = summarize_results(all_episode_results)

            # Classify whether this weight is native success/reward tuned.
            is_native_succ = abs(w - float(env_cfg["w_succ"])) < 1e-9
            is_native_ret = abs(w - float(env_cfg["w_ret"])) < 1e-9

            row = {
                "target_env": env_name,
                "weight": w,
                "source": source_label,
                "is_w1": abs(w - 1.0) < 1e-9,
                "is_native_succ": is_native_succ,
                "is_native_ret": is_native_ret,
                "success_rate": summary["success_rate"],
                "mean_reward": summary["mean_reward"],
                "std_reward": summary["std_reward"],
                "se_reward": summary["std_reward"] / np.sqrt(len(all_episode_results)),
                "mean_observations": summary["mean_observations"],
                "n_seeds": summary.get("n_seeds", float("nan")),
                "se_reward_seed_level": summary.get("se_reward_seed_level", float("nan")),
                "se_success_seed_level": summary.get("se_success_seed_level", float("nan")),
            }
            row.update(provenance_fields(seeds, num_episodes))
            results.append(row)
            print(
                f"  w={w:6.1f} [{source_label[:50]:50s}]: "
                f"success={row['success_rate']:.1%}  "
                f"reward={row['mean_reward']:+.2f} +/- {row['se_reward']:.2f}  "
                f"obs={row['mean_observations']:.1f}"
            )

    df = pd.DataFrame(results)
    output.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output, index=False)
    print(f"\nResults saved to {output}")
    return df


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--episodes", type=int, default=500)
    parser.add_argument("--seeds", type=int, default=5)
    args = parser.parse_args()
    run_transfer_experiment(num_episodes=args.episodes, seeds=SEEDS[: args.seeds])
