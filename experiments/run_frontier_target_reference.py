#!/usr/bin/env python3
"""
Target-matched constrained reference for the budget-frontier study.

The feasible-envelope reference (run_frontier_reference_heldout.py) caps
expected usage at B. Its penalty grid is nonnegative, so at budgets above the
unpenalized SARSOP policy's usage the cap is slack and the reference is the
unconstrained reward optimum. A gap there combines the cost of spending B with
any inefficiency of the calibrated family. This script adds subsidized
policies (negative usage penalties) and compares each committed family
mixture with the best sampled mixture whose expected usage equals B.

Protocol (predeclared 2026-09-30, ledger 9.17.58, before any output was seen):

1. For Tiger, Diagnosis, and Bandit, solve SARSOP (precision 1e-3, discount
   0.999) at lambda = -c * s, s in {0.1, ..., 0.9, 0.95, 0.98}, c the
   smallest observation cost, so net observation reward stays negative.
2. Evaluate every subsidized policy on the held-out seeds {7..11} and the
   fresh seeds {12..21}, 100 episodes per seed, per-episode seeding
   (seed * 10000 + episode). The committed nonnegative-penalty policies are
   re-evaluated on both streams, and the run aborts unless their held-out
   per-seed rewards reproduce results_cpomdp_frontier_heldout.csv.
3. At each frontier budget B, the target reference is the equality-
   constrained mixture over the held-out means of all sampled points
   (lp_mixture(..., equality=True)), fitted on held-out seeds and frozen for
   the fresh stream. Paired per-seed gaps (family minus reference) get a
   seed-level SE and a nominal pointwise two-sided 95 percent t interval.
   The reference remains a maximum over noisy sampled points.

Outputs:
  results/results_cpomdp_frontier_subsidy.csv
  results/results_budget_frontier_target_reference.csv

``--usage-matched`` (post hoc sensitivity, added 2026-09-30 after the
predeclared output was seen, runs no episodes): the family mixture meets B
only within its usage error, so a target gap also carries that error. This
mode refits the equality-constrained reference at each mixture's realized
held-out usage instead of B, reusing the committed per-seed archives, and
writes results/results_budget_frontier_target_reference_usage_matched.csv.
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
from rho_aif.budget import _obs_costs_from_env, episode_sensing_usage, lp_mixture, usage_value
from run_experiment import provenance_fields
from run_sarsop_baseline import AlphaVectorAgent, parse_policy, solve_sarsop
from run_cpomdp_baseline import write_pomdp_file_lagrangian
from run_budget_frontier import run_weight
from run_frontier_reference_heldout import POMDP_DIR, episode_seed, se

RESULTS = _ROOT / "results"
POMDPSOL = _ROOT / "tools" / "sarsop" / "src" / "pomdpsol"
ENVS = ["Tiger", "Diagnosis", "Bandit"]
SUBSIDY_FRACTIONS = [0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 0.95, 0.98]
HELDOUT_SEEDS = [7, 8, 9, 10, 11]
FRESH_SEEDS = list(range(12, 22))
EPISODES = 100


def evaluate(agent, env, costs, seeds):
    us, rs = [], []
    for s in seeds:
        su, sr = [], []
        for ep in range(EPISODES):
            res = run_otc_episode(agent, env, seed=episode_seed(s, ep))
            su.append(usage_value(episode_sensing_usage(res, obs_costs=costs, usage_kind="count"), "count"))
            sr.append(float(res["total_reward"]))
        us.append(float(np.mean(su)))
        rs.append(float(np.mean(sr)))
    return np.array(us), np.array(rs)


def main() -> None:
    heldout = pd.read_csv(RESULTS / "results_cpomdp_frontier_heldout.csv")
    points = []
    for name in ENVS:
        env = get_benchmark(name).env_factory()
        obs_models, config, costs = get_obs_models(env), make_env_config(env), _obs_costs_from_env(env)
        c = float(min(config["observation_costs"]))
        lams = [(float(l), False) for l in heldout[heldout["env"] == name]["lam"]]
        lams += [(-c * s, True) for s in SUBSIDY_FRACTIONS]
        for lam, new in lams:
            policy = POMDP_DIR / f"{name.lower()}_lam{lam:.6g}.policy"
            if new:
                pomdp = POMDP_DIR / f"{name.lower()}_lam{lam:.6g}.pomdp"
                write_pomdp_file_lagrangian(env, pomdp, lam=lam)
                solve_sarsop(pomdp, policy, POMDPSOL, precision=1e-3)
            agent = AlphaVectorAgent(obs_models, config, parse_policy(policy))
            hu, hr = evaluate(agent, env, costs, HELDOUT_SEEDS)
            if not new:
                row = heldout[(heldout["env"] == name) & (heldout["lam"] == lam)].iloc[0]
                committed = np.array([float(x) for x in row["per_seed_reward"].split("|")])
                if np.max(np.abs(np.round(hr, 4) - committed)) > 1e-9:
                    raise SystemExit(f"{name} lam={lam}: held-out rewards do not reproduce the committed reference")
            fu, fr = evaluate(agent, env, costs, FRESH_SEEDS)
            points.append(dict(env=name, lam=lam, subsidy=new,
                               heldout_usage=hu.mean(), heldout_reward=hr.mean(), heldout_reward_se=se(hr),
                               fresh_usage=fu.mean(), fresh_reward=fr.mean(), fresh_reward_se=se(fr),
                               heldout_per_seed_reward="|".join(f"{x:.4f}" for x in hr),
                               fresh_per_seed_reward="|".join(f"{x:.4f}" for x in fr)))
            print(f"  {name} lam={lam:+.4g} held-out U={hu.mean():.3f} R={hr.mean():.3f} | "
                  f"fresh U={fu.mean():.3f} R={fr.mean():.3f}", flush=True)
    pts = pd.DataFrame(points)
    for k, v in provenance_fields(HELDOUT_SEEDS + FRESH_SEEDS, EPISODES).items():
        pts[k] = v
    pts.to_csv(RESULTS / "results_cpomdp_frontier_subsidy.csv", index=False)

    fam = pd.read_csv(RESULTS / "results_budget_frontier.csv")
    fam = fam[(fam["policy"] == "mixture") & fam["heldout_reward"].notna()]
    out = []
    for name in ENVS:
        cfg = get_benchmark(name)
        env = cfg.env_factory()
        p = pts[pts["env"] == name].reset_index(drop=True)
        ho = np.array([[float(x) for x in s.split("|")] for s in p["heldout_per_seed_reward"]])
        fr = np.array([[float(x) for x in s.split("|")] for s in p["fresh_per_seed_reward"]])
        for r in fam[fam["env"] == name].itertuples():
            sol = lp_mixture(p["heldout_usage"].to_numpy(float), p["heldout_reward"].to_numpy(float),
                             float(r.budget), equality=True)
            if sol is None:
                out.append(dict(env=name, budget_kind=r.budget_kind, budget=r.budget,
                                note="budget outside the sampled reference usage range"))
                continue
            q = np.asarray(sol["weights"], dtype=float)
            support = "|".join(f"lam={lam:.4g}:q={qq:.4f}" for lam, qq in zip(p["lam"], q) if qq > 0)
            row = dict(env=name, budget_kind=r.budget_kind, budget=r.budget, target_reference=float(sol["value"]),
                       target_reference_usage=float(q @ p["heldout_usage"].to_numpy(float)),
                       target_reference_support=support, note="")
            fam_ho = np.array([float(x) for x in str(r.per_seed_reward).split("|")])
            _, fam_fr = run_weight(env, None, cfg.planning_horizon, FRESH_SEEDS, EPISODES,
                                   mixture=(float(r.w_lo), float(r.w_hi), float(r.q)))
            for tag, fam_seed, ref_seed in (("heldout", fam_ho, q @ ho), ("fresh", np.asarray(fam_fr, float), q @ fr)):
                d = fam_seed - ref_seed
                g, gse = float(d.mean()), se(d)
                tc = float(stats.t.ppf(0.975, len(d) - 1))
                row.update({f"{tag}_family_reward": float(fam_seed.mean()), f"{tag}_reference_reward": float(ref_seed.mean()),
                            f"{tag}_gap": g, f"{tag}_gap_se": gse,
                            f"{tag}_ci_lo": g - tc * gse, f"{tag}_ci_hi": g + tc * gse,
                            f"{tag}_per_seed_gap": "|".join(f"{x:.4f}" for x in d)})
            out.append(row)
            print(f"  {name} B={r.budget:.3f} support {support}: held-out gap {row['heldout_gap']:+.3f} "
                  f"[{row['heldout_ci_lo']:+.3f}, {row['heldout_ci_hi']:+.3f}] fresh gap {row['fresh_gap']:+.3f} "
                  f"[{row['fresh_ci_lo']:+.3f}, {row['fresh_ci_hi']:+.3f}]", flush=True)
    res = pd.DataFrame(out)
    for k, v in provenance_fields(HELDOUT_SEEDS + FRESH_SEEDS, EPISODES).items():
        res[k] = v
    res.to_csv(RESULTS / "results_budget_frontier_target_reference.csv", index=False)
    print(f"wrote {len(res)} rows")


def usage_matched() -> None:
    pts = pd.read_csv(RESULTS / "results_cpomdp_frontier_subsidy.csv")
    fam = pd.read_csv(RESULTS / "results_budget_frontier.csv")
    fam = fam[(fam["policy"] == "mixture") & fam["heldout_reward"].notna()]
    tr = pd.read_csv(RESULTS / "results_budget_frontier_target_reference.csv").set_index(["env", "budget_kind"])
    out = []
    for name in ENVS:
        p = pts[pts["env"] == name].reset_index(drop=True)
        ho = np.array([[float(x) for x in s.split("|")] for s in p["heldout_per_seed_reward"]])
        fr = np.array([[float(x) for x in s.split("|")] for s in p["fresh_per_seed_reward"]])
        for r in fam[fam["env"] == name].itertuples():
            t0 = tr.loc[(name, r.budget_kind)]
            sol = lp_mixture(p["heldout_usage"].to_numpy(float), p["heldout_reward"].to_numpy(float),
                             float(r.heldout_usage), equality=True)
            q = np.asarray(sol["weights"], dtype=float)
            q0 = np.zeros(len(p))
            for part in t0["target_reference_support"].split("|"):
                lam, qq = part.split(":q=")
                q0[[f"lam={l:.4g}" for l in p["lam"]].index(lam)] = float(qq)
            fam_ho = np.array([float(x) for x in str(r.per_seed_reward).split("|")])
            fam_fr = np.array([float(x) for x in t0["fresh_per_seed_gap"].split("|")]) + q0 @ fr
            row = dict(env=name, budget_kind=r.budget_kind, budget=r.budget, matched_usage=float(r.heldout_usage),
                       reference_support="|".join(f"lam={l:.4g}:q={qq:.4f}" for l, qq in zip(p["lam"], q) if qq > 0))
            for tag, fam_seed, ref_seed in (("heldout", fam_ho, q @ ho), ("fresh", fam_fr, q @ fr)):
                d = fam_seed - ref_seed
                g, gse = float(d.mean()), se(d)
                tc = float(stats.t.ppf(0.975, len(d) - 1))
                row.update({f"{tag}_gap": g, f"{tag}_gap_se": gse, f"{tag}_ci_lo": g - tc * gse, f"{tag}_ci_hi": g + tc * gse})
            out.append(row)
            print(f"  {name} B={r.budget:.3f} U={r.heldout_usage:.3f}: held-out {row['heldout_gap']:+.3f} "
                  f"[{row['heldout_ci_lo']:+.3f}, {row['heldout_ci_hi']:+.3f}] fresh {row['fresh_gap']:+.3f} "
                  f"[{row['fresh_ci_lo']:+.3f}, {row['fresh_ci_hi']:+.3f}]", flush=True)
    pd.DataFrame(out).to_csv(RESULTS / "results_budget_frontier_target_reference_usage_matched.csv", index=False)


if __name__ == "__main__":
    if "--usage-matched" in sys.argv:
        usage_matched()
    else:
        main()
