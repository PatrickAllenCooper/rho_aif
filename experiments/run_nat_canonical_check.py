#!/usr/bin/env python3
"""
Closes the "exactly nat-canonical agent... not separately measured" hedge
in the reward-to-nats calibration paragraph (Section 3.3).

The implementation computes information gain in bits (scipy.stats.entropy,
base=2) and reports every "EFE (w=1)" result at w=1 in those bit units, an
effective nat-denominated weight of 1/ln(2) ~= 1.44. Proposition 1's exact
identity is stated in nats, so the literally canonical agent runs at
w = ln(2) ~= 0.6931 in the implementation's bit units. That exact weight was
never a point in the Pareto sweep's default grid (0.01, 0.1, 0.5, 1, 2, 5,
10, 20, 50, 100, 200), so the paper could only reason from neighboring
tested points, not measure it directly.

This script runs w = ln(2) under the identical protocol as the Pareto sweep
(experiments/run_pareto.py: same env configs, same horizons, 500 episodes,
the 5 canonical seeds) on all five swept environments. Tiger, Diagnosis, and
Bandit are the three whose reward-maximizing tied bracket the paragraph
cites. Tileworld's clause ("both conventions are Pareto-dominated by w=20")
and Testbed's position relative to its tied bracket [0.01, 0.5] had both
rested on the swept neighbours w=0.5 and w=1, an interpolation across the
same kind of grid gap rather than a measurement of the nat-canonical point,
so they are run too. Every quantity the sweep reports per grid point is
compared (mean reward, success rate, mean observations), not just the two
the tied bracket is defined on. Each environment also gets a fresh w=1 run
on the same seeds for a same-session, apples-to-apples comparison rather
than diffing against the committed sweep CSV (the fresh w=1 rows
reproducing the committed rows is the protocol-fidelity check).

The committed CSV is the full run. --only exists for development only.
"""

import argparse
import math
import os

import numpy as np
import pandas as pd

from rho_aif.environments.tiger import TigerEnv
from rho_aif.environments.info_seeking import InfoSeekingEnv
from rho_aif.environments.diagnosis import DiagnosisEnv
from rho_aif.environments.bandit import BanditEnv
from rho_aif.environments.tileworld import TileworldEnv
from rho_aif.agents.planning_infogain import PlanningInfoGainAgent
from rho_aif.stats import seed_level_ttest
from run_experiment import run_experiment_multi_seed, summarize_results, provenance_fields, SEEDS

W_NAT_CANONICAL = math.log(2)  # ~0.6931471805599453

ENVS = {
    "Tiger": (
        TigerEnv(listen_accuracy=0.85, listen_cost=1.0,
                 correct_reward=10.0, incorrect_penalty=-100.0),
        6,
    ),
    "Testbed": (
        InfoSeekingEnv(observation_accuracy=0.75, observation_cost=0.1,
                       correct_reward=1.0, incorrect_penalty=-1.0),
        4,
    ),
    "Diagnosis": (
        DiagnosisEnv(num_conditions=4, test_accuracy=0.80, test_cost=1.0,
                     correct_reward=10.0, incorrect_penalty=-50.0),
        3,
    ),
    "Bandit": (
        BanditEnv(num_arms=4, inspect_accuracy=0.80, inspect_cost=0.5,
                  correct_reward=10.0, small_reward=1.0),
        2,
    ),
    "Tileworld": (
        TileworldEnv(grid_size=6),
        2,
    ),
}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--only", default=None,
                        help="comma-separated subset of environments (development "
                             "only, the committed CSV is the full run)")
    args = parser.parse_args()
    envs = ENVS
    if args.only:
        wanted = [e.strip() for e in args.only.split(",")]
        unknown = [e for e in wanted if e not in ENVS]
        if unknown:
            raise SystemExit(f"unknown environment(s): {unknown}, choose from {list(ENVS)}")
        envs = {k: ENVS[k] for k in wanted}

    os.makedirs("results", exist_ok=True)
    rows = []
    print(f"w = ln(2) = {W_NAT_CANONICAL:.10f}\n")
    for env_name, (env, horizon) in envs.items():
        print(f"{'=' * 60}\n{env_name} (H={horizon})\n{'=' * 60}")

        raw_nat = run_experiment_multi_seed(
            PlanningInfoGainAgent, env, 500, seeds=SEEDS,
            planning_horizon=horizon, info_gain_weight=W_NAT_CANONICAL)
        s_nat = summarize_results(raw_nat)

        raw_w1 = run_experiment_multi_seed(
            PlanningInfoGainAgent, env, 500, seeds=SEEDS,
            planning_horizon=horizon, info_gain_weight=1.0)
        s_w1 = summarize_results(raw_w1)

        # Exact equality, not a tolerance: the column is named bit_identical
        # and the paper's prose says bit-identical, so the guard must test
        # exactly that (an audit caught the original np.isclose(rtol=1e-9)
        # promising less than its name).
        # All three per-grid-point quantities the sweep reports (reward,
        # success, mean observations), so "none of the sweep's numbers move"
        # is a measured statement rather than one about two of the three.
        bit_identical = (
            s_nat["mean_reward"] == s_w1["mean_reward"]
            and s_nat["success_rate"] == s_w1["success_rate"]
            and s_nat["mean_observations"] == s_w1["mean_observations"]
        )

        welch_reward = seed_level_ttest(raw_nat, raw_w1, lambda r: r.total_reward)
        welch_success = seed_level_ttest(raw_nat, raw_w1, lambda r: float(r.success))
        welch_obs = seed_level_ttest(raw_nat, raw_w1, lambda r: float(r.num_observations))

        print(f"  w=ln(2):  reward={s_nat['mean_reward']:+.4f} (seed SE "
              f"{s_nat['se_reward_seed_level']:.4f})  success={s_nat['success_rate']:.4f}"
              f"  obs={s_nat['mean_observations']:.4f}")
        print(f"  w=1.0  :  reward={s_w1['mean_reward']:+.4f} (seed SE "
              f"{s_w1['se_reward_seed_level']:.4f})  success={s_w1['success_rate']:.4f}"
              f"  obs={s_w1['mean_observations']:.4f}")
        print(f"  bit-identical to w=1 (reward, success, obs): {bit_identical}")
        print(f"  seed-level Welch p (reward)={welch_reward['p_value']:.4g}, "
              f"(success)={welch_success['p_value']:.4g}, (obs)={welch_obs['p_value']:.4g}\n")

        rows.append({
            "env": env_name,
            "w_nat_canonical": W_NAT_CANONICAL,
            "reward_nat": s_nat["mean_reward"],
            "se_reward_seed_level_nat": s_nat["se_reward_seed_level"],
            "success_nat": s_nat["success_rate"],
            "se_success_seed_level_nat": s_nat["se_success_seed_level"],
            "obs_nat": s_nat["mean_observations"],
            "reward_w1": s_w1["mean_reward"],
            "se_reward_seed_level_w1": s_w1["se_reward_seed_level"],
            "success_w1": s_w1["success_rate"],
            "se_success_seed_level_w1": s_w1["se_success_seed_level"],
            "obs_w1": s_w1["mean_observations"],
            "bit_identical_to_w1": bit_identical,
            "welch_p_reward": welch_reward["p_value"],
            "welch_p_success": welch_success["p_value"],
            "welch_p_obs": welch_obs["p_value"],
        })

    df = pd.DataFrame(rows)
    prov = provenance_fields(SEEDS, 500)
    for k, v in prov.items():
        df[k] = v
    out_path = "results/results_nat_canonical_check.csv"
    df.to_csv(out_path, index=False)
    print(f"Saved {out_path}")
    print(df.to_string(index=False))


if __name__ == "__main__":
    main()
