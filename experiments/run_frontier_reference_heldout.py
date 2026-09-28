#!/usr/bin/env python3
"""
Budget-frontier reference re-evaluated on the held-out stream.

The budget-frontier study (run_budget_frontier.py) evaluates the Planning+IG
family on held-out seeds {7..11} with per-episode seeding, but reads its
constrained reference from results_cpomdp_frontier.csv, which evaluated the
saved SARSOP-Lagrangian policies on the canonical seeds with once-per-seed
seeding. The two estimates therefore come from different evaluation streams.
This script puts them on one stream.

Protocol (predeclared 2026-09-28, ledger 9.17.50, before any output was seen):

1. Lineage check. Re-evaluate every saved Lagrangian policy
   (results/sarsop_models/<env>_lam<lam>.policy) under the committed
   protocol (canonical seeds, 300 episodes, once-per-seed seeding,
   run_sarsop_baseline.evaluate_agent) and abort unless the reward and usage
   means reproduce results_cpomdp_frontier.csv to 1e-9.
2. Re-evaluate each policy on the held-out seeds {7, 8, 9, 10, 11}, 100
   episodes per seed, with the frontier study's per-episode seeding
   (seed * 10000 + episode), recording per-seed usage and reward.
3. At every evaluated row of results_budget_frontier.csv, compute the
   feasible envelope (rho_aif.budget.feasible_envelope) of the held-out
   reference means at that budget, the per-seed envelope reward under the
   same mixture weights, and the paired per-seed gap (family minus
   reference), with its seed-level SE and a nominal pointwise plug-in
   two-sided 95 percent t interval on 4 degrees of freedom. The envelope is still a maximum over sampled
   points, so its selection bias is not removed, only the stream mismatch.

Interpretation clarified 2026-09-28 (ledger 9.17.51; computation unchanged):
The reference support and mixture weights are fitted on the same held-out
seed means and held fixed when computing the SE. These descriptive intervals
do not propagate support reselection, uncertainty in fitted weights or cap
feasibility, or multiplicity across budgets. They do not establish coverage
for the population constrained frontier.

Outputs:
  results/results_cpomdp_frontier_heldout.csv
  results/results_budget_frontier_heldout_reference.csv
"""

from __future__ import annotations

import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT))
sys.path.insert(0, str(_ROOT / "experiments"))

import numpy as np
import pandas as pd
from scipy import stats

from rho_aif.benchmark import get_benchmark, get_obs_models, make_env_config, run_otc_episode
from rho_aif.budget import _obs_costs_from_env, episode_sensing_usage, feasible_envelope, usage_value
from run_experiment import provenance_fields
from run_sarsop_baseline import AlphaVectorAgent, evaluate_agent, parse_policy

RESULTS = _ROOT / "results"
POMDP_DIR = RESULTS / "sarsop_models"
ENVS = ["Tiger", "Diagnosis", "Bandit"]
CANONICAL_SEEDS = [42, 123, 456, 789, 1024]
CANONICAL_EPISODES = 300
HELDOUT_SEEDS = [7, 8, 9, 10, 11]
HELDOUT_EPISODES = 100


def episode_seed(seed: int, ep: int) -> int:
    return int(seed) * 10_000 + int(ep)


def se(x) -> float:
    x = np.asarray(x, dtype=float)
    return float(x.std(ddof=1) / np.sqrt(len(x)))


def main() -> None:
    frontier = pd.read_csv(RESULTS / "results_cpomdp_frontier.csv")
    rows = []
    for name in ENVS:
        cfg = get_benchmark(name)
        env = cfg.env_factory()
        obs_models, config, costs = get_obs_models(env), make_env_config(env), _obs_costs_from_env(env)
        for fr in frontier[frontier["env"] == name].itertuples():
            alphas = parse_policy(POMDP_DIR / f"{name.lower()}_lam{fr.lam:.6g}.policy")
            make = lambda: AlphaVectorAgent(obs_models, config, alphas)
            chk = evaluate_agent(make, env, CANONICAL_SEEDS, CANONICAL_EPISODES)
            if abs(chk["reward"] - fr.reward) > 1e-9 or abs(chk["usage"] - fr.usage) > 1e-9:
                raise SystemExit(f"{name} lam={fr.lam}: saved policy does not reproduce the committed frontier "
                                 f"(reward {chk['reward']} vs {fr.reward}, usage {chk['usage']} vs {fr.usage})")
            agent = make()
            us, rs = [], []
            for s in HELDOUT_SEEDS:
                su, sr = [], []
                for ep in range(HELDOUT_EPISODES):
                    res = run_otc_episode(agent, env, seed=episode_seed(s, ep))
                    su.append(usage_value(episode_sensing_usage(res, obs_costs=costs, usage_kind="count"), "count"))
                    sr.append(float(res["total_reward"]))
                us.append(float(np.mean(su)))
                rs.append(float(np.mean(sr)))
            rows.append(dict(env=name, lam=fr.lam, canonical_reward=fr.reward, canonical_usage=fr.usage,
                             reward=float(np.mean(rs)), reward_se=se(rs), usage=float(np.mean(us)), usage_se=se(us),
                             per_seed_usage="|".join(f"{u:.4f}" for u in us),
                             per_seed_reward="|".join(f"{r:.4f}" for r in rs)))
            print(f"  {name} lam={fr.lam:.4g} canonical R={fr.reward:.3f} U={fr.usage:.3f} | "
                  f"held-out R={rows[-1]['reward']:.3f} U={rows[-1]['usage']:.3f}", flush=True)
    ref = pd.DataFrame(rows)
    prov = provenance_fields(HELDOUT_SEEDS, HELDOUT_EPISODES)
    for k, v in prov.items():
        ref[k] = v
    RESULTS.mkdir(exist_ok=True)
    ref.to_csv(RESULTS / "results_cpomdp_frontier_heldout.csv", index=False)

    fam = pd.read_csv(RESULTS / "results_budget_frontier.csv")
    fam = fam[fam["heldout_reward"].notna()]
    out = []
    tcrit = float(stats.t.ppf(0.975, len(HELDOUT_SEEDS) - 1))
    for r in fam.itertuples():
        f = ref[ref["env"] == r.env]
        sol = feasible_envelope(f["usage"].to_numpy(float), f["reward"].to_numpy(float), float(r.budget))
        if sol is None:
            out.append(dict(env=r.env, budget_kind=r.budget_kind, budget=r.budget, policy=r.policy,
                            note="budget below the smallest held-out reference usage"))
            continue
        q = np.asarray(sol["weights"], dtype=float)
        ref_seed = np.array([[float(x) for x in s.split("|")] for s in f["per_seed_reward"]])
        env_seed = q @ ref_seed
        fam_seed = np.array([float(x) for x in str(r.per_seed_reward).split("|")])
        d = fam_seed - env_seed
        gse = se(d)
        support = "|".join(f"lam={lam:.4g}:q={qq:.4f}" for lam, qq in zip(f["lam"], q) if qq > 0)
        out.append(dict(env=r.env, budget_kind=r.budget_kind, budget=r.budget, policy=r.policy,
                        heldout_reward=r.heldout_reward, heldout_usage=r.heldout_usage,
                        committed_reference=r.reference_envelope_at_B, committed_gap=r.gap_to_reference,
                        heldout_reference=float(sol["value"]), heldout_reference_support=support,
                        paired_gap=float(d.mean()), paired_gap_se=gse,
                        paired_gap_ci_lo=float(d.mean() - tcrit * gse), paired_gap_ci_hi=float(d.mean() + tcrit * gse),
                        note=""))
        print(f"  {r.env} B={r.budget:.3f} {r.policy:22s} committed gap={r.gap_to_reference:+.3f} "
              f"paired held-out gap={d.mean():+.3f} +- {gse:.3f}", flush=True)
    res = pd.DataFrame(out)
    for k, v in prov.items():
        res[k] = v
    res.to_csv(RESULTS / "results_budget_frontier_heldout_reference.csv", index=False)


if __name__ == "__main__":
    main()
