#!/usr/bin/env python3
"""
Predeclared-margin TOST equivalence test: EFE (w=1) vs SARSOP.

Both referees asked for a formal equivalence test rather than the
"within sampling error" / non-overlapping-CI language used elsewhere for
the EFE-vs-SARSOP comparison on the three discrete OTC benchmarks. This
script runs a two one-sided tests (TOST) procedure (Schuirmann, 1987) on
per-seed mean reward, using the pre-declared margin of one sensing
action's cost per environment (Tiger/Diagnosis: 1.0 reward unit, one
listen/test; Bandit: 0.5, one inspection) -- a difference smaller than
the price of a single sensing action is not operationally meaningful in
this budgeted-sensing framing, and the margin is fixed by the
environment's own cost parameter rather than chosen after seeing the
reward gap.

Reuses the already-solved SARSOP policies in results/sarsop_models/ when
present (falls back to solving fresh); reuses run_sarsop_baseline's
export/solve/parse/AlphaVectorAgent machinery so this is the same exact
policy already reported in Section on the near-optimal reference.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import List, Sequence

import numpy as np
import pandas as pd

_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT))
sys.path.insert(0, str(_ROOT / "experiments"))

from rho_aif.benchmark import get_benchmark, get_obs_models, make_env_config, make_otc_agent
from rho_aif.stats import tost_equivalence

from run_sarsop_baseline import (
    AlphaVectorAgent,
    parse_policy,
    solve_sarsop,
    write_pomdp_file,
)

RESULTS = _ROOT / "results"
POMDP_DIR = RESULTS / "sarsop_models"
DEFAULT_POMDPSOL = _ROOT / "tools" / "sarsop" / "src" / "pomdpsol"

ENV_MARGINS = {"Tiger": 1.0, "Diagnosis": 1.0, "Bandit": 0.5}


def per_seed_rewards(make_agent, env, seeds: Sequence[int], num_episodes: int) -> List[float]:
    from rho_aif.benchmark import run_otc_episode

    means = []
    for seed in seeds:
        np.random.seed(int(seed))
        env.reset(seed=int(seed))
        agent = make_agent()
        rewards = [run_otc_episode(agent, env)["total_reward"] for _ in range(num_episodes)]
        means.append(float(np.mean(rewards)))
    return means


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--pomdpsol", default=str(DEFAULT_POMDPSOL))
    p.add_argument("--precision", type=float, default=1e-3)
    p.add_argument("--seeds", type=int, nargs="*", default=[42, 123, 456, 789, 1024])
    p.add_argument("--episodes", type=int, default=500)
    p.add_argument("--alpha", type=float, default=0.05)
    p.add_argument("--envs", nargs="*", default=["Tiger", "Diagnosis", "Bandit"])
    args = p.parse_args()

    pomdpsol = Path(args.pomdpsol)
    POMDP_DIR.mkdir(parents=True, exist_ok=True)

    rows = []
    for name in args.envs:
        cfg = get_benchmark(name)
        env = cfg.env_factory()
        obs_models = get_obs_models(env)
        config = make_env_config(env)

        policy_path = POMDP_DIR / f"{name.lower()}.policy"
        pomdp_path = POMDP_DIR / f"{name.lower()}.pomdp"
        if not policy_path.exists():
            write_pomdp_file(env, pomdp_path)
            solve_sarsop(pomdp_path, policy_path, pomdpsol, precision=args.precision)
        alphas = parse_policy(policy_path)

        sarsop_means = per_seed_rewards(
            lambda: AlphaVectorAgent(obs_models, config, alphas), env, args.seeds, args.episodes
        )
        efe_means = per_seed_rewards(
            lambda: make_otc_agent("efe", env, planning_horizon=cfg.planning_horizon),
            env,
            args.seeds,
            args.episodes,
        )

        margin = ENV_MARGINS[name]
        result = tost_equivalence(np.array(efe_means), np.array(sarsop_means), margin=margin, alpha=args.alpha)
        rows.append(
            {
                "env": name,
                "margin": margin,
                "alpha": args.alpha,
                "n_seeds": len(args.seeds),
                "episodes_per_seed": args.episodes,
                "mean_EFE": float(np.mean(efe_means)),
                "mean_SARSOP": float(np.mean(sarsop_means)),
                "diff": result["diff"],
                "se": result["se"],
                "df": result["df"],
                "p_lower": result["p_lower"],
                "p_upper": result["p_upper"],
                "p_tost": result["p_tost"],
                "equivalent": result["equivalent"],
                "ci_conf": result["ci_conf"],
                "ci_lo": result["ci"][0],
                "ci_hi": result["ci"][1],
            }
        )
        verdict = "EQUIVALENT" if result["equivalent"] else "NOT EQUIVALENT (or underpowered)"
        print(
            f"{name}: EFE={np.mean(efe_means):+.4f}  SARSOP={np.mean(sarsop_means):+.4f}  "
            f"diff={result['diff']:+.4f}  margin=±{margin}  "
            f"{int(result['ci_conf']*100)}% CI=[{result['ci'][0]:+.4f}, {result['ci'][1]:+.4f}]  "
            f"p_TOST={result['p_tost']:.4g}  -> {verdict}",
            flush=True,
        )

    df = pd.DataFrame(rows)
    out = RESULTS / "results_tost_sarsop.csv"
    df.to_csv(out, index=False)
    print(f"\nSaved {out}")
    print(df.to_string(index=False))


if __name__ == "__main__":
    main()
