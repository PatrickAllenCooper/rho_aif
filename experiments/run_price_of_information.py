#!/usr/bin/env python3
"""
Price of Information experiments.

Demonstrates that the Planning+IG weight w can be recovered as an operational
shadow price of a sensing budget B:

  1. Shadow-price curves w*(B) via bisection
  2. Scale-invariance under reward rescaling
  3. Duality check against Proposition 2 thresholds
  4. Online dual-descent convergence (and mid-run rescaling)
  5. Implicit budget B(w=1) that EFE corresponds to

See Guidance_Documents/price_of_information.md.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Dict, List, Optional, Sequence

_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT))
sys.path.insert(0, str(_ROOT / "experiments"))

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from rho_aif.agents.dual_descent import DualWeightAgent
from rho_aif.agents.planning_infogain import PlanningInfoGainAgent
from rho_aif.benchmark import (
    BENCHMARKS,
    get_benchmark,
    get_obs_models,
    make_env_config,
    make_inspection_agent,
    run_inspection_episode,
    run_otc_episode,
)
from rho_aif.budget import (
    episode_sensing_usage,
    estimate_usage,
    solve_shadow_price,
    usage_value,
)
from rho_aif.environments.bandit import BanditEnv
from rho_aif.environments.diagnosis import DiagnosisEnv
from rho_aif.environments.info_seeking import InfoSeekingEnv
from rho_aif.environments.tiger import TigerEnv
from run_thresholds import ENV_PARAMS, w_thresh_lower


RESULTS = _ROOT / "results"
FIGURES = _ROOT / "figures"


def _ensure_dirs() -> None:
    RESULTS.mkdir(exist_ok=True)
    FIGURES.mkdir(exist_ok=True)


# ---------------------------------------------------------------------------
# Environment helpers
# ---------------------------------------------------------------------------

def make_scaled_diagnosis(k: float) -> DiagnosisEnv:
    return DiagnosisEnv(
        num_conditions=4,
        test_accuracy=0.80,
        correct_reward=10.0 * k,
        incorrect_penalty=-50.0 * k,
        test_cost=1.0 * k,
    )


def make_scaled_tiger(k: float) -> TigerEnv:
    return TigerEnv(
        listen_accuracy=0.85,
        listen_cost=1.0 * k,
        correct_reward=10.0 * k,
        incorrect_penalty=-100.0 * k,
    )


def otc_family(name: str) -> bool:
    return get_benchmark(name).family == "observe_then_commit"


# ---------------------------------------------------------------------------
# 1. Shadow-price curves
# ---------------------------------------------------------------------------

def run_shadow_price_curves(
    env_names: Sequence[str],
    budgets: Sequence[float],
    seeds: Sequence[int],
    num_episodes: int,
    n_grid: int = 8,
) -> pd.DataFrame:
    rows = []
    for name in env_names:
        cfg = get_benchmark(name)
        env = cfg.env_factory()
        family = cfg.family
        print(f"\n=== Shadow prices: {name} ({family}) ===", flush=True)
        # Per-env budget grid: Tiger has a narrow U range near ~4–6.
        env_budgets = list(budgets)
        if name == "Tiger":
            env_budgets = [4.0, 4.5, 5.0, 5.5]
        for B in env_budgets:
            print(f"  B={B} ...", flush=True)
            res = solve_shadow_price(
                env,
                budget=float(B),
                w_lo=0.0,
                w_hi=100.0,
                tol=max(0.4, 0.15 * float(B)),
                seeds=seeds,
                num_episodes=num_episodes,
                planning_horizon=cfg.planning_horizon,
                usage_kind="count",
                family=family,
                tree_depth=cfg.tree_depth,
                n_grid=n_grid,
                method="grid",
            )
            rows.append(
                {
                    "env": name,
                    "budget": float(B),
                    "w_star": res.w_star,
                    "w_lo": res.w_lo,
                    "w_hi": res.w_hi,
                    "usage_at_star": res.usage_at_star,
                    "usage_lo": res.usage_lo,
                    "usage_hi": res.usage_hi,
                    "bracketed": res.bracketed,
                    "achievable": res.achievable,
                    "n_iters": res.n_iters,
                    "note": res.note,
                }
            )
            print(
                f"    w*={res.w_star:.4g}  U={res.usage_at_star:.3f}  "
                f"achievable={res.achievable}  note={res.note!r}",
                flush=True,
            )
    return pd.DataFrame(rows)


def plot_shadow_price_curves(df: pd.DataFrame, path: Path) -> None:
    fig, ax = plt.subplots(figsize=(7, 4.5))
    for env_name, sub in df.groupby("env"):
        sub = sub.sort_values("budget")
        ax.plot(sub["budget"], sub["w_star"], marker="o", label=env_name)
    ax.set_xlabel("Sensing budget B (mean observations)")
    ax.set_ylabel("Shadow price w*(B)")
    ax.set_title("Operational shadow price of sensing")
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


# ---------------------------------------------------------------------------
# 2. Scale invariance
# ---------------------------------------------------------------------------

def run_scale_invariance(
    scales: Sequence[float],
    budget: float,
    seeds: Sequence[int],
    num_episodes: int,
    fixed_w: float = 1.0,
    n_grid: int = 8,
) -> pd.DataFrame:
    rows = []
    for k in scales:
        env = make_scaled_diagnosis(k)
        print(f"\n=== Scale invariance Diagnosis k={k} ===", flush=True)
        u_fixed = estimate_usage(
            env,
            w=fixed_w,
            seeds=seeds,
            num_episodes=num_episodes,
            planning_horizon=3,
            usage_kind="count",
        )
        res = solve_shadow_price(
            env,
            budget=budget,
            w_lo=0.0,
            w_hi=max(200.0, 50.0 * k),
            tol=1.0,
            seeds=seeds,
            num_episodes=num_episodes,
            planning_horizon=3,
            usage_kind="count",
            n_grid=n_grid,
            method="grid",
        )
        rows.append(
            {
                "env": "Diagnosis",
                "scale_k": float(k),
                "budget": budget,
                "fixed_w": fixed_w,
                "usage_fixed_w": u_fixed,
                "w_star": res.w_star,
                "usage_at_star": res.usage_at_star,
            }
        )
        print(
            f"  fixed w={fixed_w}: U={u_fixed:.3f}  |  "
            f"w*(B={budget})={res.w_star:.4g}  U*={res.usage_at_star:.3f}",
            flush=True,
        )
    return pd.DataFrame(rows)


def plot_scale_invariance(df: pd.DataFrame, path: Path) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(9, 3.8))
    axes[0].plot(df["scale_k"], df["usage_fixed_w"], "o-", label="fixed w=1")
    axes[0].plot(df["scale_k"], df["usage_at_star"], "s-", label="w*(B)")
    axes[0].axhline(df["budget"].iloc[0], color="gray", ls="--", label="budget B")
    axes[0].set_xscale("log")
    axes[0].set_xlabel("Reward scale α")
    axes[0].set_ylabel("Mean observations")
    axes[0].set_title("Usage under rescaling")
    axes[0].legend(fontsize=8)
    axes[0].grid(True, alpha=0.3)

    # Normalize w* by scale to check approximate constancy of w*/α
    w_over_k = df["w_star"] / df["scale_k"]
    axes[1].plot(df["scale_k"], df["w_star"], "o-", label="w*")
    axes[1].plot(df["scale_k"], w_over_k, "s-", label="w*/α")
    axes[1].set_xscale("log")
    axes[1].set_yscale("log")
    axes[1].set_xlabel("Reward scale α")
    axes[1].set_ylabel("Weight")
    axes[1].set_title("Shadow price scaling")
    axes[1].legend(fontsize=8)
    axes[1].grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


# ---------------------------------------------------------------------------
# 3. Prop 2 duality
# ---------------------------------------------------------------------------

def run_prop2_duality(
    seeds: Sequence[int],
    num_episodes: int,
) -> pd.DataFrame:
    """
    Duality / complementary-slackness check against Prop 2 thresholds.

    If the closed-form lower threshold w_thresh <= 0, pure planning (w=0) must
    already observe (U(0) > 0): the zero-observation budget is unachievable.
    If w_thresh > 0, U just below the threshold should be below U just above it.
    """
    rows = []
    makers = {
        "Testbed": lambda: InfoSeekingEnv(
            observation_accuracy=0.75,
            observation_cost=0.1,
            correct_reward=1.0,
            incorrect_penalty=-1.0,
        ),
        "Tiger": lambda: TigerEnv(
            listen_accuracy=0.85,
            listen_cost=1.0,
            correct_reward=10.0,
            incorrect_penalty=-100.0,
        ),
    }
    horizons = {"Testbed": 4, "Tiger": 6}

    for name, make in makers.items():
        params = ENV_PARAMS[name]
        w_closed = w_thresh_lower(
            params["p"], params["c"], params["R_plus"], params["R_minus"], base=2
        )
        env = make()
        H = horizons[name]
        print(f"\n=== Prop2 duality: {name}  w_thresh={w_closed:.4g} ===", flush=True)
        u0 = estimate_usage(env, w=0.0, seeds=seeds, num_episodes=num_episodes, planning_horizon=H)
        w_plus = max(w_closed, 0.0) + 0.5
        u_plus = estimate_usage(env, w=w_plus, seeds=seeds, num_episodes=num_episodes, planning_horizon=H)
        if w_closed > 0:
            w_minus = max(0.0, 0.5 * w_closed)
            u_minus = estimate_usage(
                env, w=w_minus, seeds=seeds, num_episodes=num_episodes, planning_horizon=H
            )
        else:
            w_minus = 0.0
            u_minus = u0

        consistent = (w_closed <= 0 and u0 > 0.5) or (w_closed > 0 and u_plus >= u_minus - 0.25)
        rows.append(
            {
                "env": name,
                "w_closed_lower": w_closed,
                "U_w0": u0,
                "w_minus": w_minus,
                "U_w_minus": u_minus,
                "w_plus": w_plus,
                "U_w_plus": u_plus,
                "consistent_with_prop2": consistent,
            }
        )
        print(
            f"  U(0)={u0:.3f}  U({w_minus:.3g})={u_minus:.3f}  "
            f"U({w_plus:.3g})={u_plus:.3f}  consistent={consistent}",
            flush=True,
        )
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# 4. Dual descent online
# ---------------------------------------------------------------------------

def run_dual_descent(
    n_episodes: int,
    budget: float,
    lr: float,
    rescale_at: Optional[int],
    rescale_factor: float,
    seed: int = 42,
) -> pd.DataFrame:
    np.random.seed(seed)
    env = make_scaled_diagnosis(1.0)
    agent = DualWeightAgent(
        get_obs_models(env),
        make_env_config(env),
        budget=budget,
        lr=lr,
        planning_horizon=3,
        initial_weight=1.0,
    )
    # Static reference via bisection (cheap)
    ref = solve_shadow_price(
        env,
        budget=budget,
        seeds=[seed],
        num_episodes=max(20, n_episodes // 10),
        planning_horizon=3,
        tol=1.0,
        n_grid=8,
        method="grid",
    )
    rows = []
    print(
        f"\n=== Dual descent Diagnosis  B={budget}  lr={lr}  "
        f"bisection w*≈{ref.w_star:.4g} ===",
        flush=True,
    )
    for t in range(n_episodes):
        if rescale_at is not None and t == rescale_at:
            env = make_scaled_diagnosis(rescale_factor)
            # Rebuild agent config for new reward scale; keep current w and histories.
            cur_w = agent.weight
            old_w_hist = list(agent.weight_history)
            old_u_hist = list(agent.usage_history)
            agent = DualWeightAgent(
                get_obs_models(env),
                make_env_config(env),
                budget=budget,
                lr=lr,
                planning_horizon=3,
                initial_weight=cur_w,
            )
            agent.weight_history = old_w_hist
            agent.usage_history = old_u_hist
            print(f"  t={t}: rescale rewards by {rescale_factor}, keep w={cur_w:.4g}", flush=True)

        result = run_otc_episode(agent, env)
        u = usage_value(episode_sensing_usage(result), "count")
        new_w = agent.end_episode(u)
        rows.append(
            {
                "episode": t,
                "usage": u,
                "weight": new_w,
                "budget": budget,
                "bisection_w_star": ref.w_star,
                "rescaled": bool(rescale_at is not None and t >= rescale_at),
                "reward": result["total_reward"],
                "success": result["success"],
            }
        )
        if (t + 1) % max(1, n_episodes // 10) == 0:
            recent = np.mean([r["usage"] for r in rows[-20:]])
            print(
                f"  t={t+1}/{n_episodes}  w={new_w:.4g}  "
                f"recent_U={recent:.2f}",
                flush=True,
            )
    return pd.DataFrame(rows)


def plot_dual_descent(df: pd.DataFrame, path: Path) -> None:
    fig, axes = plt.subplots(2, 1, figsize=(7, 5.5), sharex=True)
    axes[0].plot(df["episode"], df["weight"], label="w_t")
    axes[0].axhline(df["bisection_w_star"].iloc[0], color="C1", ls="--", label="bisection w*")
    if df["rescaled"].any():
        t0 = int(df.loc[df["rescaled"], "episode"].iloc[0])
        axes[0].axvline(t0, color="gray", ls=":", label="rescale")
        axes[1].axvline(t0, color="gray", ls=":")
    axes[0].set_ylabel("Weight w")
    axes[0].legend(fontsize=8)
    axes[0].grid(True, alpha=0.3)

    # Smoothed usage
    window = max(5, len(df) // 20)
    smooth = df["usage"].rolling(window, min_periods=1).mean()
    axes[1].plot(df["episode"], smooth, label=f"usage (roll-{window})")
    axes[1].axhline(df["budget"].iloc[0], color="C1", ls="--", label="budget B")
    axes[1].set_xlabel("Episode")
    axes[1].set_ylabel("Usage")
    axes[1].legend(fontsize=8)
    axes[1].grid(True, alpha=0.3)
    fig.suptitle("Online dual control of w")
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


# ---------------------------------------------------------------------------
# 5. Implicit EFE budget B(w=1)
# ---------------------------------------------------------------------------

def run_implicit_efe_budget(
    env_names: Sequence[str],
    seeds: Sequence[int],
    num_episodes: int,
) -> pd.DataFrame:
    rows = []
    for name in env_names:
        cfg = get_benchmark(name)
        env = cfg.env_factory()
        print(f"\n=== Implicit EFE budget: {name} ===", flush=True)
        u = estimate_usage(
            env,
            w=1.0,
            seeds=seeds,
            num_episodes=num_episodes,
            planning_horizon=cfg.planning_horizon,
            usage_kind="count",
            family=cfg.family,
            tree_depth=cfg.tree_depth,
        )
        rows.append({"env": name, "w": 1.0, "implicit_budget": u, "family": cfg.family})
        print(f"  B_EFE = U(w=1) = {u:.3f}", flush=True)
    return pd.DataFrame(rows)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument(
        "--mode",
        choices=["quick", "full"],
        default="quick",
        help="quick: reduced seeds/episodes for CI-scale runs; full: paper-scale",
    )
    p.add_argument(
        "--only",
        nargs="*",
        default=None,
        help="Subset of experiments: curves scale prop2 dual efe",
    )
    return p.parse_args()


def main() -> None:
    args = parse_args()
    _ensure_dirs()
    only = set(args.only) if args.only else {"curves", "scale", "prop2", "dual", "efe"}

    if args.mode == "full":
        seeds = [42, 123, 456, 789, 1024]
        ep = 80
        # Budgets sit above typical U(0) instrumental baselines.
        curve_budgets = [6.0, 8.0, 10.0, 12.0]
        dual_episodes = 400
        scale_budget = 8.0
        dual_budget = 8.0
        env_names = ["Tiger", "Diagnosis", "Bandit", "Tileworld-6x6", "Inspection-N8"]
        n_grid = 10
    else:
        seeds = [42, 123]
        ep = 30
        curve_budgets = [6.0, 8.0, 10.0]
        dual_episodes = 100
        scale_budget = 8.0
        dual_budget = 8.0
        env_names = ["Tiger", "Diagnosis", "Bandit"]
        n_grid = 7

    summary = {"mode": args.mode, "seeds": list(seeds), "episodes": ep}

    if "curves" in only:
        df = run_shadow_price_curves(env_names, curve_budgets, seeds, ep, n_grid=n_grid)
        df.to_csv(RESULTS / "price_shadow_curves.csv", index=False)
        plot_shadow_price_curves(df, FIGURES / "price_shadow_curves.png")
        summary["curves_rows"] = len(df)

    if "scale" in only:
        df = run_scale_invariance(
            scales=[0.1, 1.0, 10.0],
            budget=scale_budget,
            seeds=seeds,
            num_episodes=ep,
            n_grid=n_grid,
        )
        df.to_csv(RESULTS / "price_scale_invariance.csv", index=False)
        plot_scale_invariance(df, FIGURES / "price_scale_invariance.png")
        summary["scale_rows"] = len(df)

    if "prop2" in only:
        df = run_prop2_duality(seeds, ep)
        df.to_csv(RESULTS / "price_prop2_duality.csv", index=False)
        summary["prop2_rows"] = len(df)

    if "dual" in only:
        df = run_dual_descent(
            n_episodes=dual_episodes,
            budget=dual_budget,
            lr=0.2,
            rescale_at=dual_episodes // 2,
            rescale_factor=10.0,
        )
        df.to_csv(RESULTS / "price_dual_descent.csv", index=False)
        plot_dual_descent(df, FIGURES / "price_dual_descent.png")
        summary["dual_rows"] = len(df)

    if "efe" in only:
        df = run_implicit_efe_budget(env_names, seeds, ep)
        df.to_csv(RESULTS / "price_efe_implicit_budget.csv", index=False)
        summary["efe_rows"] = len(df)

    with open(RESULTS / "price_of_information_summary.json", "w") as f:
        json.dump(summary, f, indent=2)
    print("\nDone.", json.dumps(summary, indent=2), flush=True)


if __name__ == "__main__":
    main()
