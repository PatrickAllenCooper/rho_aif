#!/usr/bin/env python3
"""
Exact constrained-POMDP (CPOMDP) baseline for the observe-then-commit suite.

Extends the SARSOP export of run_sarsop_baseline.py with a literal usage
penalty in the reward model: R(obs_j, s, *, *) = -(cost_j + lambda * u_j),
where u_j is the sensing-usage unit (1 for count usage). Solving this with
the APPL SARSOP solver at a grid of lambda >= 0 gives, for each lambda, the
EXACT optimal value of

    max_pi  E_pi[R] - lambda * E_pi[U]

over the full space of POMDP policies (not the restricted Planning+IG
family). For a finite discounted CMDP this is a strong-duality Lagrangian
relaxation of the budgeted problem max_pi E[R] s.t. E[U] <= B: the swept
points trace the upper concave envelope of the achievable (E[U], E[R])
region, and any budget between two adjacent swept usages is attained
exactly by a per-episode mixture of the two bracketing policies (the same
mixture argument used for the Planning+IG shadow price in
Definition~\\ref{def:pi3} / rho_aif.budget.crossing_bracket).

This directly answers the "no exact CPOMDP baseline" limitation raised by
both referees: it reports the optimality gap of the Planning+IG family
(and of the canonical EFE weight w=1) relative to the true optimal policy
at a matched sensing budget, for the three discrete OTC benchmarks that
admit exact SARSOP solves (Tiger, Diagnosis, Bandit).

Scope: exact for these three environments under the same discounted
infinite-horizon relaxation (discount 0.999) already used for the
reward-only SARSOP baseline. Does not extend to RockSample or Structural
Inspection's larger factored state spaces -- that remains future work.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np
import pandas as pd

_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT))
sys.path.insert(0, str(_ROOT / "experiments"))

from rho_aif.agents.planning_infogain import PlanningInfoGainAgent
from rho_aif.benchmark import (
    get_benchmark,
    get_obs_models,
    make_env_config,
    make_otc_agent,
    run_otc_episode,
)
from rho_aif.budget import estimate_usage_curve, make_log_w_grid, solve_shadow_price_from_curve

from run_sarsop_baseline import AlphaVectorAgent, evaluate_agent, parse_policy, solve_sarsop

RESULTS = _ROOT / "results"
POMDP_DIR = RESULTS / "sarsop_models"
DEFAULT_POMDPSOL = _ROOT / "tools" / "sarsop" / "src" / "pomdpsol"

ENVS = ["Tiger", "Diagnosis", "Bandit"]
LAMBDA_GRID = [0.0] + list(np.logspace(np.log10(0.05), np.log10(100.0), 11))


def write_pomdp_file_lagrangian(env, path: Path, lam: float, discount: float = 0.999) -> dict:
    """
    Same Cassandra .pomdp export as run_sarsop_baseline.write_pomdp_file,
    except each observation action's reward is additionally penalized by
    ``lam`` per unit of count-usage: R(obs_j, s, *, *) = -(cost_j + lam).

    lam=0 recovers the pure reward-maximizing (ordinary SARSOP) model.
    """
    obs_models = get_obs_models(env)
    config = make_env_config(env)
    commit = np.asarray(config["commit_reward_matrix"], dtype=float)
    costs = [float(c) for c in config["observation_costs"]]

    n = obs_models[0].shape[0]
    n_commit = commit.shape[0]
    k = len(obs_models)
    m = max(mod.shape[1] for mod in obs_models)

    states = [f"s{i}" for i in range(n)] + ["done"]
    actions = [f"obs{j}" for j in range(k)] + [f"commit{i}" for i in range(n_commit)]
    observations = [f"o{j}" for j in range(m)] + ["onull"]

    lines: List[str] = []
    lines.append(f"discount: {discount}")
    lines.append("values: reward")
    lines.append("states: " + " ".join(states))
    lines.append("actions: " + " ".join(actions))
    lines.append("observations: " + " ".join(observations))
    start = [1.0 / n] * n + [0.0]
    lines.append("start: " + " ".join(f"{p:.10f}" for p in start))
    lines.append("")

    for j in range(k):
        lines.append(f"T: obs{j} identity")
    for i in range(n_commit):
        for s in states:
            lines.append(f"T: commit{i} : {s} : done 1.0")
    lines.append("")

    for j, model in enumerate(obs_models):
        for s in range(n):
            row = model[s]
            for o in range(model.shape[1]):
                if row[o] > 0:
                    lines.append(f"O: obs{j} : s{s} : o{o} {row[o]:.10f}")
        lines.append(f"O: obs{j} : done : onull 1.0")
    for i in range(n_commit):
        lines.append(f"O: commit{i} : * : onull 1.0")
    lines.append("")

    for j in range(k):
        penalized_cost = costs[j] + float(lam)
        for s in range(n):
            lines.append(f"R: obs{j} : s{s} : * : * {-penalized_cost:.10f}")
    for i in range(n_commit):
        for s in range(n):
            lines.append(f"R: commit{i} : s{s} : * : * {commit[i, s]:.10f}")
    lines.append("")

    path.write_text("\n".join(lines))
    return {"n_states": n, "n_commit": n_commit, "n_obs_actions": k, "n_outcomes": m}


def sweep_lambda(
    env_name: str,
    pomdpsol: Path,
    lambdas: Sequence[float],
    seeds: Sequence[int],
    episodes: int,
    precision: float,
    timeout_s: int,
) -> pd.DataFrame:
    cfg = get_benchmark(env_name)
    env = cfg.env_factory()
    obs_models = get_obs_models(env)
    config = make_env_config(env)

    rows = []
    for lam in lambdas:
        pomdp_path = POMDP_DIR / f"{env_name.lower()}_lam{lam:.6g}.pomdp"
        policy_path = POMDP_DIR / f"{env_name.lower()}_lam{lam:.6g}.policy"
        write_pomdp_file_lagrangian(env, pomdp_path, lam=float(lam))
        try:
            solve_sarsop(pomdp_path, policy_path, pomdpsol, precision=precision, timeout_s=timeout_s)
        except (subprocess.TimeoutExpired, RuntimeError) as exc:
            print(f"  [{env_name} lam={lam:.4g}] SARSOP solve failed: {exc}", flush=True)
            continue
        alphas = parse_policy(policy_path)
        agent_factory = lambda: AlphaVectorAgent(obs_models, config, alphas)
        r = evaluate_agent(agent_factory, env, seeds, episodes)
        rows.append({"env": env_name, "lam": float(lam), **r})
        print(
            f"  [{env_name} lam={lam:8.4g}] reward {r['reward']:8.3f}+-{r['reward_se']:.3f}  "
            f"usage {r['usage']:6.3f}+-{r['usage_se']:.3f}  success {r['success']:.3f}",
            flush=True,
        )
    return pd.DataFrame(rows)


def exact_reward_at_budget(frontier: pd.DataFrame, budget: float) -> Tuple[float, float, float]:
    """
    Interpolate the exact Lagrangian-sweep frontier at usage == budget.

    R at the budget is the usage-weighted mixture of the two bracketing
    points' rewards (exactly attained by randomizing per episode between
    their policies -- the same mixture argument used for the Planning+IG
    shadow price). Sorts explicitly by realized usage rather than by
    lambda: usage is *decreasing* in lambda here (unlike Planning+IG's w,
    where usage increases in w), so reusing rho_aif.budget.crossing_bracket
    directly on the lambda axis silently picks the wrong endpoint whenever
    the budget falls outside the swept usage range -- this implementation
    is direction-agnostic by construction.
    """
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
    q = (budget - u_lo) / (u_hi - u_lo)
    q = min(1.0, max(0.0, q))
    r_exact = (1.0 - q) * r_lo + q * r_hi
    return r_exact, float(lams[idx_lo]), float(lams[idx_hi])


def planning_ig_at_budget(
    env_name: str, budget: float, seeds: Sequence[int], episodes: int, planning_horizon: int
) -> dict:
    """Usage-matched Planning+IG reward at the same budget, fresh seeds/episodes."""
    cfg = get_benchmark(env_name)
    env = cfg.env_factory()
    curve = estimate_usage_curve(
        env,
        w_grid=make_log_w_grid(0.0, 200.0, 16),
        seeds=seeds,
        num_episodes=max(30, episodes // 5),
        planning_horizon=planning_horizon,
    )
    sol = solve_shadow_price_from_curve(curve, budget=budget, tol=0.2)
    w_star = sol.w_star

    def make_agent():
        obs_models = get_obs_models(env)
        config = make_env_config(env)
        return PlanningInfoGainAgent(
            obs_models, config, planning_horizon=planning_horizon, info_gain_weight=w_star
        )

    r = evaluate_agent(make_agent, env, seeds, episodes)
    r["w_star"] = float(w_star)
    return r


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--pomdpsol", default=str(DEFAULT_POMDPSOL))
    p.add_argument("--precision", type=float, default=1e-3)
    p.add_argument("--timeout", type=int, default=60)
    p.add_argument("--seeds", type=int, nargs="*", default=[42, 123, 456, 789, 1024])
    p.add_argument("--episodes", type=int, default=300)
    p.add_argument("--envs", nargs="*", default=ENVS)
    args = p.parse_args()

    pomdpsol = Path(args.pomdpsol)
    if not pomdpsol.exists():
        raise SystemExit(f"pomdpsol not found at {pomdpsol}; run tools/build_sarsop.sh first")
    POMDP_DIR.mkdir(parents=True, exist_ok=True)

    frontier_rows = []
    summary_rows = []
    for name in args.envs:
        cfg = get_benchmark(name)
        print(f"\n=== {name}: exact Lagrangian sweep ({len(LAMBDA_GRID)} lambdas) ===", flush=True)
        frontier = sweep_lambda(
            name, pomdpsol, LAMBDA_GRID, args.seeds, args.episodes, args.precision, args.timeout
        )
        frontier["env"] = name
        frontier_rows.append(frontier)

        env = cfg.env_factory()
        obs_models = get_obs_models(env)
        config = make_env_config(env)
        efe_r = evaluate_agent(
            lambda: make_otc_agent("efe", env, planning_horizon=cfg.planning_horizon),
            env,
            args.seeds,
            args.episodes,
        )
        budget = float(efe_r["usage"])
        r_exact, lam_lo, lam_hi = exact_reward_at_budget(frontier, budget)
        pig_r = planning_ig_at_budget(
            name, budget, args.seeds, args.episodes, cfg.planning_horizon
        )

        gap_efe = r_exact - efe_r["reward"]
        gap_pig = r_exact - pig_r["reward"]
        row = {
            "env": name,
            "budget_B_EFE": budget,
            "R_exact": r_exact,
            "lam_bracket_lo": lam_lo,
            "lam_bracket_hi": lam_hi,
            "R_EFE": efe_r["reward"],
            "R_EFE_se": efe_r["reward_se"],
            "gap_EFE": gap_efe,
            "gap_EFE_pct": 100.0 * gap_efe / abs(r_exact) if r_exact != 0 else float("nan"),
            "w_star_PIG": pig_r["w_star"],
            "R_PIG": pig_r["reward"],
            "R_PIG_se": pig_r["reward_se"],
            "U_PIG": pig_r["usage"],
            "gap_PIG": gap_pig,
            "gap_PIG_pct": 100.0 * gap_pig / abs(r_exact) if r_exact != 0 else float("nan"),
        }
        summary_rows.append(row)
        print(
            f"\n  {name}: B_EFE={budget:.3f}  R_exact={r_exact:.4f}  "
            f"R_EFE={efe_r['reward']:.4f} (gap {gap_efe:+.4f}, {row['gap_EFE_pct']:+.2f}%)  "
            f"R_PIG(w={pig_r['w_star']:.3g})={pig_r['reward']:.4f} (gap {gap_pig:+.4f}, "
            f"{row['gap_PIG_pct']:+.2f}%)",
            flush=True,
        )

    frontier_df = pd.concat(frontier_rows, ignore_index=True)
    frontier_out = RESULTS / "results_cpomdp_frontier.csv"
    frontier_df.to_csv(frontier_out, index=False)
    print(f"\nSaved {frontier_out}")

    summary_df = pd.DataFrame(summary_rows)
    summary_out = RESULTS / "results_cpomdp_baseline.csv"
    summary_df.to_csv(summary_out, index=False)
    print(f"Saved {summary_out}")
    print(summary_df.to_string(index=False))


if __name__ == "__main__":
    main()
