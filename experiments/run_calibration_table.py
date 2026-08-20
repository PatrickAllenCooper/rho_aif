#!/usr/bin/env python3
"""
Proper-scoring calibration table (Section 4.2 of the review-response plan).

Reports log score and Brier score of the terminal belief against the true
hidden state -- not another reward/usage winner-count table -- for reward-only
Planning, EFE (w=1), and the strongest available reference per instance:
SARSOP's near-optimal alpha-vector policy for the three OTC environments with
a built solver (Tiger, Diagnosis, Bandit; Stage F), and a Planning+IG agent at
the Stage G w* atlas's higher canonical budget for Structural Inspection,
where SARSOP was not run (state spaces of 256 and 65,536 are outside the
scope of the near-optimal solver used here).

Both run_otc_episode and run_inspection_episode already compute per-episode
log_score/brier_score against the correct proper-scoring targets (this file
adds no new scoring code); this script only aggregates them, with SE, from
one canonical multi-seed run per agent/instance and writes a CSV plus a
LaTeX table fragment.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Callable, Dict, List, Sequence

import numpy as np
import pandas as pd

_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT))
sys.path.insert(0, str(_ROOT / "experiments"))

from rho_aif.benchmark import (
    get_benchmark,
    get_obs_models,
    make_env_config,
    make_inspection_agent,
    make_otc_agent,
    run_inspection_episode,
    run_otc_episode,
)
from run_sarsop_baseline import (
    AlphaVectorAgent,
    DEFAULT_POMDPSOL,
    parse_policy,
    solve_sarsop,
    write_pomdp_file,
)

RESULTS = _ROOT / "results"
TABLES = _ROOT / "paper" / "tables"
POMDP_DIR = RESULTS / "sarsop_models"

OTC_ENVS = ["Tiger", "Diagnosis", "Bandit"]
INSPECTION_ENVS = ["Inspection-N8", "Inspection-N16"]

# Planning+IG weight for Inspection reference agent: the Stage G w* atlas's
# higher canonical budget bracket (results/results_w_atlas.csv, w_hi2),
# reused here rather than re-tuned, so the two artifacts stay consistent.
INSPECTION_REFERENCE_W = {
    "Inspection-N8": 100.0,
    "Inspection-N16": 23.71373705661655,
}


def _mean_se(xs: Sequence[float]) -> tuple:
    arr = np.asarray(list(xs), dtype=float)
    m = float(arr.mean())
    se = float(arr.std(ddof=1) / np.sqrt(len(arr))) if len(arr) > 1 else 0.0
    return m, se


def evaluate_otc(make_agent: Callable, env, seeds: Sequence[int], episodes: int) -> dict:
    per_seed_reward, per_seed_log, per_seed_brier, per_seed_success = [], [], [], []
    for seed in seeds:
        np.random.seed(int(seed))
        env.reset(seed=int(seed))
        agent = make_agent()
        rewards, logs, briers, succ = [], [], [], []
        for _ in range(episodes):
            r = run_otc_episode(agent, env)
            rewards.append(r["total_reward"])
            logs.append(r["log_score"])
            briers.append(r["brier_score"])
            succ.append(float(r["success"]))
        per_seed_reward.append(float(np.mean(rewards)))
        per_seed_log.append(float(np.mean(logs)))
        per_seed_brier.append(float(np.mean(briers)))
        per_seed_success.append(float(np.mean(succ)))
    r_m, r_se = _mean_se(per_seed_reward)
    l_m, l_se = _mean_se(per_seed_log)
    b_m, b_se = _mean_se(per_seed_brier)
    s_m, _ = _mean_se(per_seed_success)
    return {
        "reward": r_m, "reward_se": r_se,
        "log_score": l_m, "log_score_se": l_se,
        "brier": b_m, "brier_se": b_se,
        "success": s_m,
    }


def evaluate_inspection(make_agent: Callable, env, seeds: Sequence[int], episodes: int) -> dict:
    per_seed_reward, per_seed_log, per_seed_brier = [], [], []
    for seed in seeds:
        agent = make_agent()
        rewards, logs, briers = [], [], []
        for ep_i in range(episodes):
            r = run_inspection_episode(agent, env, seed=int(seed) * 10000 + ep_i)
            rewards.append(r["total_reward"])
            logs.append(r["log_score"])
            briers.append(r["brier_score"])
        per_seed_reward.append(float(np.mean(rewards)))
        per_seed_log.append(float(np.mean(logs)))
        per_seed_brier.append(float(np.mean(briers)))
    r_m, r_se = _mean_se(per_seed_reward)
    l_m, l_se = _mean_se(per_seed_log)
    b_m, b_se = _mean_se(per_seed_brier)
    return {
        "reward": r_m, "reward_se": r_se,
        "log_score": l_m, "log_score_se": l_se,
        "brier": b_m, "brier_se": b_se,
        "success": float("nan"),
    }


def get_sarsop_agent(name: str, env, pomdpsol: Path, precision: float) -> Callable:
    """Reuse a cached alpha-vector policy if present; otherwise solve fresh."""
    pomdp_path = POMDP_DIR / f"{name.lower()}.pomdp"
    policy_path = POMDP_DIR / f"{name.lower()}.policy"
    POMDP_DIR.mkdir(parents=True, exist_ok=True)
    if not (pomdp_path.exists() and policy_path.exists()):
        write_pomdp_file(env, pomdp_path)
        solve_sarsop(pomdp_path, policy_path, pomdpsol, precision=precision)
    alphas = parse_policy(policy_path)
    obs_models = get_obs_models(env)
    config = make_env_config(env)
    return lambda: AlphaVectorAgent(obs_models, config, alphas)


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--pomdpsol", default=str(DEFAULT_POMDPSOL))
    p.add_argument("--precision", type=float, default=1e-3)
    p.add_argument("--seeds", type=int, nargs="*", default=[42, 123, 456, 789, 1024])
    p.add_argument("--otc-episodes", type=int, default=500)
    p.add_argument(
        "--inspection-episodes",
        type=int,
        default=None,
        help="Defaults to each instance's canonical episodes_per_seed if unset.",
    )
    args = p.parse_args()

    rows: List[dict] = []

    pomdpsol = Path(args.pomdpsol)
    have_sarsop = pomdpsol.exists()
    if not have_sarsop:
        print(f"Warning: pomdpsol not found at {pomdpsol}; skipping SARSOP rows", flush=True)

    for name in OTC_ENVS:
        cfg = get_benchmark(name)
        env = cfg.env_factory()
        agents: Dict[str, Callable] = {
            "Planning (reward-only)": lambda: make_otc_agent(
                "planning", env, planning_horizon=cfg.planning_horizon
            ),
            "EFE (w=1)": lambda: make_otc_agent(
                "efe", env, planning_horizon=cfg.planning_horizon
            ),
        }
        if have_sarsop:
            agents["SARSOP"] = get_sarsop_agent(name, env, pomdpsol, args.precision)
        for label, make_agent in agents.items():
            r = evaluate_otc(make_agent, env, args.seeds, args.otc_episodes)
            rows.append({"instance": name, "agent": label, **r})
            print(
                f"{name:14s} {label:24s} log {r['log_score']:7.3f}+-{r['log_score_se']:.3f}  "
                f"brier {r['brier']:.3f}+-{r['brier_se']:.3f}  reward {r['reward']:7.3f}+-{r['reward_se']:.3f}",
                flush=True,
            )

    for name in INSPECTION_ENVS:
        cfg = get_benchmark(name)
        env = cfg.env_factory()
        w_ref = INSPECTION_REFERENCE_W[name]
        n_ep = args.inspection_episodes if args.inspection_episodes is not None else cfg.episodes_per_seed
        agents = {
            "Planning (reward-only)": lambda: make_inspection_agent(
                "planning", env, tree_depth=cfg.tree_depth
            ),
            "EFE (w=1)": lambda: make_inspection_agent(
                "efe", env, tree_depth=cfg.tree_depth
            ),
            f"Planning+IG (w={w_ref:.3g})": lambda: make_inspection_agent(
                "planning+ig", env, tree_depth=cfg.tree_depth, info_weight=w_ref
            ),
        }
        for label, make_agent in agents.items():
            r = evaluate_inspection(make_agent, env, args.seeds, n_ep)
            rows.append({"instance": name, "agent": label, **r})
            print(
                f"{name:14s} {label:24s} log {r['log_score']:7.3f}+-{r['log_score_se']:.3f}  "
                f"brier {r['brier']:.3f}+-{r['brier_se']:.3f}  reward {r['reward']:7.3f}+-{r['reward_se']:.3f}",
                flush=True,
            )

    df = pd.DataFrame(rows)
    out_csv = RESULTS / "results_calibration_table.csv"
    df.to_csv(out_csv, index=False)
    print(f"\nSaved {out_csv}")

    TABLES.mkdir(parents=True, exist_ok=True)
    lines = [
        "% Auto-generated by experiments/run_calibration_table.py -- do not edit by hand.",
        "\\begin{table}[t]",
        "\\centering",
        "\\caption{Proper-scoring calibration of the terminal belief against the",
        " true hidden state (log score in nats, Brier score; mean $\\pm$ SE over",
        " 5 seeds). Reference is SARSOP for the three OTC environments and",
        " Planning+IG at the Stage G atlas's higher canonical budget for",
        " Structural Inspection, where the near-optimal solver used here does not",
        " scale to the instance's state space.}",
        "\\label{tab:calibration}",
        "\\small",
        "\\begin{tabular}{llcc}",
        "\\toprule",
        "Instance & Agent & Log score & Brier score \\\\",
        "\\midrule",
    ]
    for instance, sub in df.groupby("instance", sort=False):
        for _, r in sub.iterrows():
            inst_tex = str(instance).replace("[", "{[}").replace("]", "{]}")
            lines.append(
                f"{inst_tex} & {r['agent']} & "
                f"${r['log_score']:.3f} \\pm {r['log_score_se']:.3f}$ & "
                f"${r['brier']:.3f} \\pm {r['brier_se']:.3f}$ \\\\"
            )
        lines.append("\\midrule")
    if lines[-1] == "\\midrule":
        lines.pop()
    lines += ["\\bottomrule", "\\end{tabular}", "\\end{table}", ""]
    out_tex = TABLES / "calibration_table.tex"
    out_tex.write_text("\n".join(lines))
    print(f"Saved {out_tex}")


if __name__ == "__main__":
    main()
