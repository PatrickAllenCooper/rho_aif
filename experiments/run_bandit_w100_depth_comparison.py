#!/usr/bin/env python3
"""
Bandit w=100 depth comparison (Stage K statistical-audit item 34).

Backs the Discussion's "The information-unit weight and why it works"
paragraph's claim that adding planning depth to a weighted information-gain
bonus amplifies the weight's effect: Planning+IG (H=2, w=100) inspects more
than myopic Info Gain (H=1, w=100) on Bandit, illustrating why the tuning
problem gets harder with depth. This specific comparison, at this specific
weight, was never run at the canonical 5-seed protocol before -- this script
closes that gap rather than asserting the claim from an untraceable number.

Saves results/results_bandit_w100_depth.csv.
"""

import os

from rho_aif.agents.info_gain import InformationGainAgent
from rho_aif.agents.planning_infogain import PlanningInfoGainAgent
from rho_aif.environments.bandit import BanditEnv
from rho_aif.stats import seed_level_ttest
from run_experiment import run_experiment_multi_seed, summarize_results, provenance_fields, SEEDS


def main():
    os.makedirs("results", exist_ok=True)
    env = BanditEnv(
        num_arms=4, inspect_accuracy=0.80, inspect_cost=0.5,
        correct_reward=10.0, small_reward=1.0,
    )
    seeds = SEEDS
    num_episodes = 500
    w = 100.0

    print("=" * 70)
    print(f"Bandit w={w:g} depth comparison: myopic Info Gain vs. Planning+IG (H=2)")
    print("=" * 70)

    myopic_raw = run_experiment_multi_seed(
        InformationGainAgent, env, num_episodes, seeds=seeds, info_gain_weight=w,
    )
    myopic_s = summarize_results(myopic_raw)
    print(
        f"  Info Gain (myopic, w={w:g}): obs={myopic_s['mean_observations']:.2f}  "
        f"success={myopic_s['success_rate']:.1%}  reward={myopic_s['mean_reward']:+.3f}"
    )

    planning_ig_raw = run_experiment_multi_seed(
        PlanningInfoGainAgent, env, num_episodes, seeds=seeds,
        planning_horizon=2, info_gain_weight=w,
    )
    planning_ig_s = summarize_results(planning_ig_raw)
    print(
        f"  Planning+IG (H=2, w={w:g}): obs={planning_ig_s['mean_observations']:.2f}  "
        f"success={planning_ig_s['success_rate']:.1%}  reward={planning_ig_s['mean_reward']:+.3f}"
    )

    cmp_obs = seed_level_ttest(
        planning_ig_raw, myopic_raw, lambda r: r.num_observations
    )
    print(
        f"\n  Seed-level Welch on inspections (Planning+IG vs. myopic Info Gain): "
        f"p={cmp_obs['p_value']:.4g}"
    )

    import pandas as pd
    rows = [
        {
            "env": "Bandit", "agent": "InfoGain-myopic", "w": w, "horizon": 1,
            "mean_observations": myopic_s["mean_observations"],
            "success_rate": myopic_s["success_rate"],
            "mean_reward": myopic_s["mean_reward"],
            "n_seeds": myopic_s.get("n_seeds", float("nan")),
            "se_observations_seed_level": float("nan"),
            "se_reward_seed_level": myopic_s.get("se_reward_seed_level", float("nan")),
        },
        {
            "env": "Bandit", "agent": "Planning+IG", "w": w, "horizon": 2,
            "mean_observations": planning_ig_s["mean_observations"],
            "success_rate": planning_ig_s["success_rate"],
            "mean_reward": planning_ig_s["mean_reward"],
            "n_seeds": planning_ig_s.get("n_seeds", float("nan")),
            "se_observations_seed_level": float("nan"),
            "se_reward_seed_level": planning_ig_s.get("se_reward_seed_level", float("nan")),
            "p_observations_vs_myopic_seed_level": cmp_obs["p_value"],
        },
    ]
    for r in rows:
        r.update(provenance_fields(seeds, num_episodes))
    df = pd.DataFrame(rows)
    csv_path = "results/results_bandit_w100_depth.csv"
    df.to_csv(csv_path, index=False)
    print(f"\nSaved {csv_path}")


if __name__ == "__main__":
    main()
