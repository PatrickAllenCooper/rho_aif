#!/usr/bin/env python3
"""
Run the observe-then-commit IDS baseline on core environments.

Compares IDS (Russo & Van Roy information ratio) against Myopic, Planning,
Planning+IG (tuned), and EFE.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT))
sys.path.insert(0, str(_ROOT / "experiments"))

import pandas as pd

from rho_aif.agents.efe import EFEAgent
from rho_aif.agents.ids import IDSAgent
from rho_aif.agents.myopic import MyopicAgent
from rho_aif.agents.planning import PlanningAgent
from rho_aif.agents.planning_infogain import PlanningInfoGainAgent
from rho_aif.environments.bandit import BanditEnv
from rho_aif.environments.diagnosis import DiagnosisEnv
from rho_aif.environments.tiger import TigerEnv
from run_experiment import SEEDS, run_experiment_multi_seed, summarize_results


ENVS = {
    "Tiger": {
        "make": lambda: TigerEnv(),
        "horizon": 6,
        "w_succ": 20,
    },
    "Diagnosis": {
        "make": lambda: DiagnosisEnv(num_conditions=4),
        "horizon": 3,
        "w_succ": 100,
    },
    "Bandit": {
        "make": lambda: BanditEnv(num_arms=4),
        "horizon": 2,
        "w_succ": 100,
    },
}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--episodes", type=int, default=500)
    parser.add_argument("--seeds", type=int, default=5)
    parser.add_argument("--output", type=Path, default=Path("results/results_ids.csv"))
    args = parser.parse_args()

    seeds = SEEDS[: args.seeds]
    rows = []

    for env_name, cfg in ENVS.items():
        env = cfg["make"]()
        H = cfg["horizon"]
        print(f"\n=== {env_name} (H={H}) ===", flush=True)

        agents = [
            ("Myopic", MyopicAgent, {}),
            ("Planning", PlanningAgent, {"planning_horizon": H}),
            (
                f"Planning+IG(w={cfg['w_succ']})",
                PlanningInfoGainAgent,
                {"planning_horizon": H, "info_gain_weight": cfg["w_succ"]},
            ),
            ("EFE", EFEAgent, {"planning_horizon": H}),
            ("IDS", IDSAgent, {}),
        ]

        for name, cls, kwargs in agents:
            raw = run_experiment_multi_seed(
                cls, env, args.episodes, seeds=seeds, **kwargs
            )
            s = summarize_results(raw)
            row = {
                "environment": env_name,
                "agent": name,
                "mean_observations": s["mean_observations"],
                "success_rate": s["success_rate"],
                "mean_reward": s["mean_reward"],
                "std_reward": s["std_reward"],
                "n_episodes": len(raw),
            }
            rows.append(row)
            print(
                f"  {name:28s} obs={row['mean_observations']:.2f}  "
                f"succ={row['success_rate']:.1%}  "
                f"rew={row['mean_reward']:+.3f}",
                flush=True,
            )

    df = pd.DataFrame(rows)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(args.output, index=False)
    print(f"\nWrote {args.output}")


if __name__ == "__main__":
    main()
