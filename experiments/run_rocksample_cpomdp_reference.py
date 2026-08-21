#!/usr/bin/env python3
"""
Approximate constrained-POMDP (CPOMDP) reference for RockSample[7,8] (Stage K item 2).

The exact Lagrangian-sweep CPOMDP reference of run_cpomdp_baseline.py (SARSOP
solved to precision 1e-3) is not available for RockSample: SARSOP is not
practical at this state-space size (Section sec:rocksample). This script
extends the SAME idea -- sweep a literal usage-cap Lagrangian penalty and
trace the resulting (E[U], E[R]) frontier -- using the depth-limited
belief-space tree search that is already this project's validated primary
solver for RockSample (RockSampleTreeSearchAgent), rather than SARSOP.

IMPORTANT SCOPE CAVEAT, stated here and in the manuscript: this is NOT a
near-optimal reference in the sense the SARSOP-based one is. Depth-3 tree
search is a heuristic-augmented, depth-limited planner, not a certified
solver for the true infinite-horizon POMDP. The resulting frontier is an
ACHIEVABLE reference (the best policy this specific planner family can find
at each usage-cap penalty), not a proven upper bound on the achievable
(E[U], E[R]) region. Report it as "depth-3 tree-search Lagrangian reference",
never as "near-optimal" or "exact" for RockSample.

Mechanism: RockSampleTreeSearchAgent(usage_lambda=lam) replaces the
information-floor dual (self.info_weight * ig) used by Planning+IG/EFE with
a literal usage-cap dual (-lam per check action, independent of information
gain) in the SAME recursive tree-search evaluation already used and reported
for RockSample -- this is a minimal, additive change to
rho_aif/agents/rocksample_agents.py (usage_lambda=None preserves all
existing behavior exactly; existing RockSample tests still pass).

Saves results/results_rocksample_cpomdp_frontier.csv and
results/results_rocksample_cpomdp_reference.csv.
"""

import os
import time

import numpy as np
import pandas as pd

from rho_aif.environments.rocksample import RockSampleEnv
from rho_aif.agents.rocksample_agents import RockSampleTreeSearchAgent
from run_rocksample import ROCKSAMPLE_CONFIGS, run_rocksample_episode
from run_experiment import SEEDS, provenance_fields

LAMBDA_GRID = [0.0] + list(np.logspace(np.log10(0.05), np.log10(100.0), 11))


def evaluate_lambda(env, lam, seeds, num_episodes, max_depth, max_steps):
    episode_results = []
    for seed in seeds:
        np.random.seed(seed)
        agent = RockSampleTreeSearchAgent(env, max_depth=max_depth, usage_lambda=lam)
        for ep_i in range(num_episodes):
            r = run_rocksample_episode(agent, env, seed=seed * 10000 + ep_i, max_steps=max_steps)
            r["seed"] = seed
            episode_results.append(r)

    rewards = np.array([r["total_reward"] for r in episode_results])
    checks = np.array([r["checks"] for r in episode_results])
    return {
        "reward": float(np.mean(rewards)),
        "reward_se": float(np.std(rewards) / np.sqrt(len(rewards))),
        "usage": float(np.mean(checks)),
        "usage_se": float(np.std(checks) / np.sqrt(len(checks))),
        "n_episodes": len(episode_results),
    }


def frontier_reward_at_budget(frontier: pd.DataFrame, budget: float):
    """Mirrors run_cpomdp_baseline.exact_reward_at_budget: usage-weighted
    mixture interpolation on the swept (usage, reward) frontier, sorted by
    realized usage (usage is not monotone in lambda)."""
    df = frontier.sort_values("usage").reset_index(drop=True)
    usages = df["usage"].to_numpy(dtype=float)
    rewards = df["reward"].to_numpy(dtype=float)
    lams = df["lam"].to_numpy(dtype=float)

    if budget <= usages[0]:
        return float(rewards[0]), float(lams[0]), float(lams[0])
    if budget >= usages[-1]:
        return float(rewards[-1]), float(lams[-1]), float(lams[-1])

    lo_mask = usages <= budget
    hi_mask = usages >= budget
    idx_lo = int(np.where(lo_mask)[0][-1])
    idx_hi = int(np.where(hi_mask)[0][0])
    u_lo, u_hi = float(usages[idx_lo]), float(usages[idx_hi])
    r_lo, r_hi = float(rewards[idx_lo]), float(rewards[idx_hi])
    if u_hi == u_lo:
        return r_lo, float(lams[idx_lo]), float(lams[idx_hi])
    q = min(1.0, max(0.0, (budget - u_lo) / (u_hi - u_lo)))
    return (1.0 - q) * r_lo + q * r_hi, float(lams[idx_lo]), float(lams[idx_hi])


def main():
    os.makedirs("results", exist_ok=True)
    config_name = "RS[7,8]"
    cfg = ROCKSAMPLE_CONFIGS[config_name]
    gs, nr, rp, td = cfg["grid_size"], cfg["num_rocks"], cfg["rock_positions"], cfg["tree_depth"]
    max_steps = gs * gs + nr * 10
    seeds = SEEDS
    num_episodes = 100  # matches the committed RS[7,8] table's protocol exactly

    env = RockSampleEnv(
        grid_size=gs, num_rocks=nr, rock_positions=rp, move_cost=-0.5, max_steps=max_steps,
    )

    print("=" * 70)
    print(f"RockSample[7,8] depth-{td} tree-search Lagrangian sweep ({len(LAMBDA_GRID)} lambdas)")
    print("NOT a near-optimal reference -- see module docstring for the scope caveat.")
    print("=" * 70)

    rows = []
    for lam in LAMBDA_GRID:
        t0 = time.time()
        r = evaluate_lambda(env, lam, seeds, num_episodes, td, max_steps)
        dt = time.time() - t0
        r["lam"] = float(lam)
        r["env"] = config_name
        rows.append(r)
        print(
            f"  [lam={lam:8.4g}] reward={r['reward']:8.3f}+-{r['reward_se']:.3f}  "
            f"usage={r['usage']:6.3f}+-{r['usage_se']:.3f}  ({dt:.1f}s)",
            flush=True,
        )

    frontier = pd.DataFrame(rows)
    for r in rows:
        r.update(provenance_fields(seeds, num_episodes))
    frontier = pd.DataFrame(rows)
    frontier_out = "results/results_rocksample_cpomdp_frontier.csv"
    frontier.to_csv(frontier_out, index=False)
    print(f"\nSaved {frontier_out}")

    # EFE's usage on this instance (from the committed RS[7,8] table:
    # mean_checks=9.842, EFE w=1, depth=3) is the budget B_EFE to interpolate at.
    b_efe = 9.842
    r_ref, lam_lo, lam_hi = frontier_reward_at_budget(frontier, b_efe)

    r_efe = 21.849  # committed results_rocksample_7x8.csv, EFE w=1 (d=3)
    gap_efe = r_ref - r_efe

    summary = pd.DataFrame([{
        "env": config_name,
        "budget_B_EFE": b_efe,
        "R_ref_depth3_lagrangian": r_ref,
        "lam_bracket_lo": lam_lo,
        "lam_bracket_hi": lam_hi,
        "R_EFE": r_efe,
        "gap_EFE": gap_efe,
        "gap_EFE_pct": 100.0 * gap_efe / abs(r_ref) if r_ref != 0 else float("nan"),
        "note": "R_ref is a depth-3 tree-search Lagrangian reference, NOT a near-optimal bound "
                "(SARSOP is not tractable at this scale); see module docstring.",
    }])
    for col in ["seed_list", "episodes_per_seed", "git_sha", "generated_utc"]:
        summary[col] = frontier[col].iloc[0]
    summary_out = "results/results_rocksample_cpomdp_reference.csv"
    summary.to_csv(summary_out, index=False)
    print(f"Saved {summary_out}")
    print(summary.to_string(index=False))


if __name__ == "__main__":
    main()
