#!/usr/bin/env python3
"""
Fresh-seed replication of the same-stream budget-frontier comparison.

run_frontier_reference_heldout.py pairs each held-out endpoint mixture with
its feasible-envelope reference on the held-out seeds {7..11}. A referee
check (ledger 9.17.57) found that the Diagnosis interior_0.5 shortfall, which
compares the w=1 plateau policy with the unpenalized reference, does not
reproduce on other seeds, so the five-seed paired intervals may understate
seed-set variation. This script replicates every row on fresh seeds.

Protocol (predeclared 2026-09-28, ledger 9.17.57, before this script's output
was seen):

1. Seeds {12, ..., 21}, 100 episodes per seed, the frontier study's
   per-episode seeding (seed * 10000 + episode) and mixture-draw stream.
   The referee check had already evaluated the Diagnosis interior_0.5 pair
   on these seeds, so that one comparison is not blind.
2. Nothing is refit. Each mixture keeps its committed (w_lo, w_hi, q) from
   results_budget_frontier.csv, and each reference keeps the support and
   weights committed in results_budget_frontier_heldout_reference.csv.
3. For each row, the paired per-seed gap (family minus reference), its
   seed-level SE, and a nominal two-sided 95 percent t interval on 9 degrees
   of freedom. A row replicates the held-out shortfall if its interval also
   lies below zero.

``--lineage`` first replays every row on the held-out seeds and aborts unless
each paired gap reproduces results_budget_frontier_heldout_reference.csv to
1e-9, so the replication measures seeds and nothing else.

Output: results/results_budget_frontier_fresh_seed_replication.csv
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
from rho_aif.budget import _obs_costs_from_env, feasible_envelope
from run_experiment import provenance_fields
from run_sarsop_baseline import AlphaVectorAgent, parse_policy
from run_budget_frontier import run_weight
from run_frontier_reference_heldout import POMDP_DIR, episode_seed, se

RESULTS = _ROOT / "results"
FRESH_SEEDS = list(range(12, 22))
EPISODES = 100


def reference_per_seed(env, name, lam_label, cache):
    if lam_label in cache:
        return cache[lam_label]
    obs_models, config, costs = get_obs_models(env), make_env_config(env), _obs_costs_from_env(env)
    lams = pd.read_csv(RESULTS / "results_cpomdp_frontier_heldout.csv")
    lams = [l for l in lams[lams["env"] == name]["lam"] if f"{l:.4g}" == lam_label]
    assert len(lams) == 1, (name, lam_label, lams)
    lam = float(lams[0])
    agent = AlphaVectorAgent(obs_models, config, parse_policy(POMDP_DIR / f"{name.lower()}_lam{lam:.6g}.policy"))
    rs = []
    for s in FRESH_SEEDS:
        sr = [float(run_otc_episode(agent, env, seed=episode_seed(s, ep))["total_reward"]) for ep in range(EPISODES)]
        rs.append(float(np.mean(sr)))
    cache[lam_label] = np.array(rs)
    return cache[lam_label]


def main() -> None:
    global FRESH_SEEDS
    lineage = "--lineage" in sys.argv
    if lineage:
        FRESH_SEEDS = [7, 8, 9, 10, 11]
    fam = pd.read_csv(RESULTS / "results_budget_frontier.csv")
    ref = pd.read_csv(RESULTS / "results_budget_frontier_heldout_reference.csv")
    fam = fam[(fam["policy"] == "mixture") & fam["heldout_reward"].notna()]
    heldout_ref = pd.read_csv(RESULTS / "results_cpomdp_frontier_heldout.csv")
    tcrit = float(stats.t.ppf(0.975, len(FRESH_SEEDS) - 1))
    out = []
    for name in ["Tiger", "Diagnosis", "Bandit"]:
        cfg = get_benchmark(name)
        env = cfg.env_factory()
        cache = {}
        for r in fam[fam["env"] == name].itertuples():
            h = ref[(ref["env"] == name) & (ref["budget_kind"] == r.budget_kind) & (ref["policy"] == "mixture")]
            assert len(h) == 1, (name, r.budget_kind)
            h = h.iloc[0]
            hr = heldout_ref[heldout_ref["env"] == name]
            sol = feasible_envelope(hr["usage"].to_numpy(float), hr["reward"].to_numpy(float), float(r.budget))
            weights = np.asarray(sol["weights"], dtype=float)
            label = "|".join(f"lam={lam:.4g}:q={qq:.4f}" for lam, qq in zip(hr["lam"], weights) if qq > 0)
            assert label == h["heldout_reference_support"], (label, h["heldout_reference_support"])
            ref_seed = sum(qq * reference_per_seed(env, name, f"{lam:.4g}", cache)
                           for lam, qq in zip(hr["lam"], weights) if qq > 0)
            fam_u, fam_r = run_weight(env, None, cfg.planning_horizon, FRESH_SEEDS, EPISODES,
                                      mixture=(float(r.w_lo), float(r.w_hi), float(r.q)))
            d = np.asarray(fam_r, dtype=float) - ref_seed
            gse = se(d)
            if lineage:
                if abs(d.mean() - h["paired_gap"]) > 1e-9:
                    raise SystemExit(f"{name} {r.budget_kind}: held-out gap {d.mean()} does not reproduce "
                                     f"the committed {h['paired_gap']}")
                print(f"  lineage OK {name} {r.budget_kind} gap={d.mean():+.6f}", flush=True)
                continue
            out.append(dict(env=name, budget_kind=r.budget_kind, budget=r.budget,
                            w_lo=r.w_lo, w_hi=r.w_hi, q=r.q, reference_support=h["heldout_reference_support"],
                            heldout_paired_gap=h["paired_gap"], heldout_ci_lo=h["paired_gap_ci_lo"],
                            heldout_ci_hi=h["paired_gap_ci_hi"],
                            fresh_usage=float(np.mean(fam_u)), fresh_reward=float(np.mean(fam_r)),
                            fresh_reference=float(ref_seed.mean()),
                            fresh_paired_gap=float(d.mean()), fresh_paired_gap_se=gse,
                            fresh_ci_lo=float(d.mean() - tcrit * gse), fresh_ci_hi=float(d.mean() + tcrit * gse),
                            replicates_shortfall=bool(d.mean() + tcrit * gse < 0),
                            per_seed_gap="|".join(f"{x:.4f}" for x in d)))
            print(f"  {name} {r.budget_kind:14s} held-out gap={h['paired_gap']:+.3f} "
                  f"fresh gap={d.mean():+.3f} +- {gse:.3f} [{out[-1]['fresh_ci_lo']:+.3f}, {out[-1]['fresh_ci_hi']:+.3f}]",
                  flush=True)
    if lineage:
        print("lineage check passed")
        return
    res = pd.DataFrame(out)
    for k, v in provenance_fields(FRESH_SEEDS, EPISODES).items():
        res[k] = v
    RESULTS.mkdir(exist_ok=True)
    res.to_csv(RESULTS / "results_budget_frontier_fresh_seed_replication.csv", index=False)
    print(f"wrote {len(res)} rows")


if __name__ == "__main__":
    main()
