#!/usr/bin/env python3
"""
Price of Information experiments (upgraded battery).

  1. Shadow-price staircases w*(B) from powered usage curves with SEs
  2. Curve-collapse scale test: U vs w/alpha across reward scales
  3. Positive-threshold Prop 2 jump-location check
  4. Online dual descent with lr decay / Polyak average + mid-run rescale
  5. Implicit budget B(w=1) that EFE corresponds to

See Guidance_Documents/price_of_information.md.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Callable, Dict, List, Optional, Sequence, Tuple

_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT))
sys.path.insert(0, str(_ROOT / "experiments"))

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from rho_aif.agents.dual_descent import DualWeightAgent
from rho_aif.benchmark import get_benchmark, get_obs_models, make_env_config, run_otc_episode
from rho_aif.budget import (
    episode_sensing_usage,
    estimate_usage,
    estimate_usage_curve,
    identifiable_budgets,
    make_log_w_grid,
    solve_shadow_price_from_curve,
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


def make_scaled_bandit(k: float) -> BanditEnv:
    return BanditEnv(
        num_arms=4,
        inspect_accuracy=0.80,
        correct_reward=10.0 * k,
        small_reward=1.0 * k,
        inspect_cost=0.5 * k,
    )


def curve_to_rows(env_name: str, curve, extra: Optional[dict] = None) -> List[dict]:
    rows = []
    for p in curve:
        row = {
            "env": env_name,
            "w": p.w,
            "mean_usage": p.mean_usage,
            "se_usage": p.se_usage,
            "n_seeds": p.n_seeds,
        }
        if extra:
            row.update(extra)
        rows.append(row)
    return rows


# ---------------------------------------------------------------------------
# 1. Shadow-price staircases from powered usage curves
# ---------------------------------------------------------------------------

def run_shadow_price_curves(
    env_names: Sequence[str],
    seeds: Sequence[int],
    num_episodes: int,
    n_grid: int = 16,
    n_budgets: int = 5,
    episodes_by_env: Optional[Dict[str, int]] = None,
    grid_by_env: Optional[Dict[str, int]] = None,
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    curve_rows: List[dict] = []
    price_rows: List[dict] = []
    episodes_by_env = episodes_by_env or {}
    grid_by_env = grid_by_env or {}

    for name in env_names:
        cfg = get_benchmark(name)
        env = cfg.env_factory()
        ep = int(episodes_by_env.get(name, num_episodes))
        ng = int(grid_by_env.get(name, n_grid))
        print(f"\n=== Shadow prices: {name} ({cfg.family})  ep={ep} grid={ng} ===", flush=True)
        w_grid = make_log_w_grid(0.0, 100.0, ng)
        curve = []
        for i, w in enumerate(w_grid):
            print(f"  [{i+1}/{len(w_grid)}] estimating U(w={float(w):.4g}) ...", flush=True)
            pts = estimate_usage_curve(
                env,
                w_grid=[float(w)],
                seeds=seeds,
                num_episodes=ep,
                planning_horizon=cfg.planning_horizon,
                usage_kind="count",
                family=cfg.family,
                tree_depth=cfg.tree_depth,
            )
            curve.extend(pts)
            p = pts[0]
            print(
                f"    U={p.mean_usage:.3f}±{p.se_usage:.3f}",
                flush=True,
            )
        curve_rows.extend(curve_to_rows(name, curve))
        u_min = min(p.mean_usage for p in curve)
        u_max = max(p.mean_usage for p in curve)
        print(f"  U range [{u_min:.3f}, {u_max:.3f}]", flush=True)

        budgets = identifiable_budgets(curve, n_budgets=n_budgets, margin=0.08)
        for B in budgets:
            res = solve_shadow_price_from_curve(curve, budget=float(B), tol=max(0.3, 0.1 * float(B)))
            price_rows.append(
                {
                    "env": name,
                    "budget": float(B),
                    "w_star": res.w_star,
                    "w_lo": res.w_lo,
                    "w_hi": res.w_hi,
                    "usage_at_star": res.usage_at_star,
                    "usage_lo": res.usage_lo,
                    "usage_hi": res.usage_hi,
                    "usage_se_at_star": res.usage_se_at_star,
                    "bracketed": res.bracketed,
                    "achievable": res.achievable,
                    "u_min": res.u_min,
                    "u_max": res.u_max,
                    "note": res.note,
                }
            )
            print(
                f"  B={B:.3f}: w*={res.w_star:.4g}  bracket=[{res.w_lo:.3g},{res.w_hi:.3g}]  "
                f"U={res.usage_at_star:.3f}±{res.usage_se_at_star:.3f}",
                flush=True,
            )
        # Incremental save so a slow later env cannot erase prior results
        pd.DataFrame(curve_rows).to_csv(RESULTS / "results_price_usage_curves.csv", index=False)
        pd.DataFrame(price_rows).to_csv(RESULTS / "results_price_shadow_curves.csv", index=False)
    return pd.DataFrame(curve_rows), pd.DataFrame(price_rows)


def plot_shadow_price_curves(price_df: pd.DataFrame, path: Path) -> None:
    fig, ax = plt.subplots(figsize=(7.5, 4.8))
    for env_name, sub in price_df.groupby("env"):
        sub = sub.sort_values("budget")
        ax.step(sub["budget"], sub["w_star"], where="mid", label=env_name)
        ax.scatter(sub["budget"], sub["w_star"], s=28)
        # Shaded bracket intervals in w at each budget
        for _, row in sub.iterrows():
            ax.plot(
                [row["budget"], row["budget"]],
                [row["w_lo"], row["w_hi"]],
                color="gray",
                alpha=0.5,
                lw=1.5,
            )
    ax.set_xlabel("Sensing budget B (mean observations)")
    ax.set_ylabel("Shadow price w*(B)")
    ax.set_yscale("symlog", linthresh=0.1)
    ax.set_title("Operational shadow price (staircase with brackets)")
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


# ---------------------------------------------------------------------------
# 2. Curve-collapse scale test
# ---------------------------------------------------------------------------

def run_scale_collapse(
    scales: Sequence[float],
    seeds: Sequence[int],
    num_episodes: int,
    n_grid: int = 14,
    budget: float = 8.0,
    env_kind: str = "Diagnosis",
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Estimate U(w; alpha) on alpha-scaled grids so w/alpha points align.
    Prediction: curves collapse when plotted vs w/alpha.

    Returns (curve_df, cross_df, collapse_df).
    """
    makers: Dict[str, Tuple[Callable[[float], object], int]] = {
        "Diagnosis": (make_scaled_diagnosis, 3),
        "Bandit": (make_scaled_bandit, 2),
    }
    make_env, horizon = makers[env_kind]
    base_grid = make_log_w_grid(0.0, 20.0, n_grid)  # base = alpha=1 grid
    curve_rows: List[dict] = []
    cross_rows: List[dict] = []

    for alpha in scales:
        env = make_env(alpha)
        # Scale the positive weights; keep 0.
        w_grid = np.array([0.0 if w == 0.0 else float(alpha) * float(w) for w in base_grid])
        # Deduplicate while preserving order
        seen = set()
        w_unique = []
        for w in w_grid:
            key = round(w, 12)
            if key not in seen:
                seen.add(key)
                w_unique.append(float(w))
        print(f"\n=== Scale collapse {env_kind} alpha={alpha} ===", flush=True)
        curve = estimate_usage_curve(
            env,
            w_grid=w_unique,
            seeds=seeds,
            num_episodes=num_episodes,
            planning_horizon=horizon,
        )
        for p in curve:
            w_over_a = 0.0 if alpha == 0 else p.w / float(alpha)
            curve_rows.append(
                {
                    "env": env_kind,
                    "scale_k": float(alpha),
                    "w": p.w,
                    "w_over_alpha": w_over_a,
                    "mean_usage": p.mean_usage,
                    "se_usage": p.se_usage,
                    "n_seeds": p.n_seeds,
                }
            )
            print(
                f"  w={p.w:.4g}  w/a={w_over_a:.4g}  U={p.mean_usage:.3f}±{p.se_usage:.3f}",
                flush=True,
            )

        res = solve_shadow_price_from_curve(curve, budget=budget, tol=max(0.4, 0.1 * budget))
        w_star_over_a = res.w_star / float(alpha) if alpha else float("nan")
        cross_rows.append(
            {
                "env": env_kind,
                "scale_k": float(alpha),
                "budget": budget,
                "w_star": res.w_star,
                "w_star_over_alpha": w_star_over_a,
                "usage_at_star": res.usage_at_star,
                "usage_se": res.usage_se_at_star,
                "achievable": res.achievable,
            }
        )
        print(
            f"  B={budget}: w*={res.w_star:.4g}  w*/a={w_star_over_a:.4g}  "
            f"U*={res.usage_at_star:.3f}",
            flush=True,
        )

    curve_df = pd.DataFrame(curve_rows)
    # Collapse metric: at matched w/alpha, max vertical deviation across scales
    collapse_rows = []
    if not curve_df.empty:
        # Round w_over_alpha for matching
        curve_df["w_key"] = curve_df["w_over_alpha"].round(6)
        for key, sub in curve_df.groupby("w_key"):
            if len(sub) < 2:
                continue
            spread = float(sub["mean_usage"].max() - sub["mean_usage"].min())
            mean_se = float(np.nanmean(sub["se_usage"]))
            collapse_rows.append(
                {
                    "env": env_kind,
                    "w_over_alpha": float(key),
                    "usage_spread": spread,
                    "mean_se": mean_se,
                    "n_scales": len(sub),
                    "within_noise": spread <= max(2.0 * mean_se, 0.5),
                }
            )
    collapse_df = pd.DataFrame(collapse_rows)
    if not collapse_df.empty:
        frac = float(collapse_df["within_noise"].mean())
        max_spread = float(collapse_df["usage_spread"].max())
        print(
            f"  Collapse: {frac:.0%} of matched points within 2·SE; "
            f"max spread={max_spread:.3f}",
            flush=True,
        )
    return curve_df.drop(columns=["w_key"], errors="ignore"), pd.DataFrame(cross_rows), collapse_df


def plot_scale_collapse(
    curve_df: pd.DataFrame,
    cross_df: pd.DataFrame,
    path: Path,
    budget: float,
) -> None:
    fig, axes = plt.subplots(1, 2, figsize=(10, 4.2))
    ax = axes[0]
    for alpha, sub in curve_df.groupby("scale_k"):
        sub = sub.sort_values("w_over_alpha")
        ax.errorbar(
            sub["w_over_alpha"],
            sub["mean_usage"],
            yerr=sub["se_usage"],
            fmt="o-",
            label=f"α={alpha:g}",
            capsize=2,
            ms=4,
        )
    ax.axhline(budget, color="gray", ls="--", label=f"B={budget:g}")
    ax.set_xscale("symlog", linthresh=0.05)
    ax.set_xlabel("w / α")
    ax.set_ylabel("Mean observations U")
    ax.set_title("Curve collapse: U(w/α)")
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3)

    ax2 = axes[1]
    if not cross_df.empty:
        ax2.plot(cross_df["scale_k"], cross_df["w_star"], "o-", label="w*")
        ax2.plot(cross_df["scale_k"], cross_df["w_star_over_alpha"], "s-", label="w*/α")
        ax2.set_xscale("log")
        ax2.set_yscale("log")
        ax2.set_xlabel("Reward scale α")
        ax2.set_ylabel("Weight")
        ax2.set_title(f"Shadow price at B={budget:g}")
        ax2.legend(fontsize=8)
        ax2.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


# ---------------------------------------------------------------------------
# 3. Positive-threshold Prop 2 check
# ---------------------------------------------------------------------------

POSITIVE_THRESH_CONFIGS = {
    "TestbedPos-p06": {
        "p": 0.60,
        "c": 0.3,
        "R_plus": 1.0,
        "R_minus": -1.0,
        "make": lambda: InfoSeekingEnv(
            observation_accuracy=0.60,
            observation_cost=0.3,
            correct_reward=1.0,
            incorrect_penalty=-1.0,
        ),
        "horizon": 4,
    },
    "TestbedPos-p058": {
        "p": 0.58,
        "c": 0.3,
        "R_plus": 1.0,
        "R_minus": -1.0,
        "make": lambda: InfoSeekingEnv(
            observation_accuracy=0.58,
            observation_cost=0.3,
            correct_reward=1.0,
            incorrect_penalty=-1.0,
        ),
        "horizon": 4,
    },
}


def run_prop2_duality(
    seeds: Sequence[int],
    num_episodes: int,
    n_grid: int = 12,
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Positive-threshold jump test + negative-threshold sanity table.
    """
    jump_rows: List[dict] = []
    curve_rows: List[dict] = []
    sanity_rows: List[dict] = []

    for name, cfg in POSITIVE_THRESH_CONFIGS.items():
        w_closed = w_thresh_lower(cfg["p"], cfg["c"], cfg["R_plus"], cfg["R_minus"], base=2)
        assert w_closed > 0, f"Expected positive threshold for {name}, got {w_closed}"
        env = cfg["make"]()
        # Grid from 0.25x to 4x threshold, plus 0
        factors = np.concatenate([[0.0], np.geomspace(0.25, 4.0, num=n_grid - 1)])
        w_grid = [float(f * w_closed) if f > 0 else 0.0 for f in factors]
        print(f"\n=== Prop2 positive: {name}  w_thresh={w_closed:.4g} ===", flush=True)
        curve = estimate_usage_curve(
            env,
            w_grid=w_grid,
            seeds=seeds,
            num_episodes=num_episodes,
            planning_horizon=cfg["horizon"],
        )
        # Empirical jump: first w where U exceeds mid of [U_min, U_max]
        us = [p.mean_usage for p in curve]
        u_floor = min(us)
        u_ceil = max(us)
        jump_level = 0.5 * (u_floor + u_ceil)
        jump_w = None
        for p in sorted(curve, key=lambda x: x.w):
            curve_rows.append(
                {
                    "env": name,
                    "w": p.w,
                    "w_over_thresh": 0.0 if w_closed == 0 else p.w / w_closed,
                    "mean_usage": p.mean_usage,
                    "se_usage": p.se_usage,
                    "w_thresh": w_closed,
                }
            )
            if jump_w is None and p.mean_usage >= jump_level and p.w > 0:
                jump_w = p.w
        if jump_w is None:
            jump_w = float("nan")
        # Also: mean U below vs above threshold
        below = [p.mean_usage for p in curve if p.w < w_closed]
        above = [p.mean_usage for p in curve if p.w >= w_closed]
        u_below = float(np.mean(below)) if below else float("nan")
        u_above = float(np.mean(above)) if above else float("nan")
        # Jump lands near closed form if relative error within a factor of ~2 (grid)
        rel = abs(jump_w - w_closed) / w_closed if (w_closed > 0 and np.isfinite(jump_w)) else float("nan")
        jump_ok = bool(np.isfinite(rel) and rel <= 1.0 and u_above > u_below + 0.25)
        jump_rows.append(
            {
                "env": name,
                "w_thresh": w_closed,
                "jump_w": jump_w,
                "rel_err": rel,
                "U_below": u_below,
                "U_above": u_above,
                "U_floor": u_floor,
                "U_ceil": u_ceil,
                "jump_ok": jump_ok,
            }
        )
        print(
            f"  jump_w={jump_w:.4g}  rel_err={rel:.3f}  "
            f"U_below={u_below:.3f}  U_above={u_above:.3f}  ok={jump_ok}",
            flush=True,
        )

    # Negative-threshold sanity (Testbed / Tiger)
    makers = {
        "Testbed": (
            lambda: InfoSeekingEnv(
                observation_accuracy=0.75,
                observation_cost=0.1,
                correct_reward=1.0,
                incorrect_penalty=-1.0,
            ),
            4,
        ),
        "Tiger": (
            lambda: TigerEnv(
                listen_accuracy=0.85,
                listen_cost=1.0,
                correct_reward=10.0,
                incorrect_penalty=-100.0,
            ),
            6,
        ),
    }
    for name, (make, H) in makers.items():
        params = ENV_PARAMS[name]
        w_closed = w_thresh_lower(
            params["p"], params["c"], params["R_plus"], params["R_minus"], base=2
        )
        env = make()
        u0 = estimate_usage(env, w=0.0, seeds=seeds, num_episodes=num_episodes, planning_horizon=H)
        consistent = bool(w_closed <= 0 and u0 > 0.5)
        sanity_rows.append(
            {
                "env": name,
                "w_closed_lower": w_closed,
                "U_w0": u0,
                "consistent_with_prop2": consistent,
            }
        )
        print(f"\n=== Prop2 sanity {name}: w_thresh={w_closed:.4g} U(0)={u0:.3f} ok={consistent}", flush=True)

    return pd.DataFrame(jump_rows), pd.DataFrame(curve_rows), pd.DataFrame(sanity_rows)


def plot_prop2_jumps(curve_df: pd.DataFrame, jump_df: pd.DataFrame, path: Path) -> None:
    envs = list(curve_df["env"].unique()) if not curve_df.empty else []
    n = max(1, len(envs))
    fig, axes = plt.subplots(1, n, figsize=(4.2 * n, 3.8), squeeze=False)
    for i, name in enumerate(envs):
        ax = axes[0, i]
        sub = curve_df[curve_df["env"] == name].sort_values("w")
        ax.errorbar(sub["w"], sub["mean_usage"], yerr=sub["se_usage"], fmt="o-", capsize=2, ms=4)
        w_th = float(sub["w_thresh"].iloc[0])
        ax.axvline(w_th, color="C1", ls="--", label=f"w_thresh={w_th:.3g}")
        jrow = jump_df[jump_df["env"] == name]
        if not jrow.empty and np.isfinite(jrow["jump_w"].iloc[0]):
            ax.axvline(jrow["jump_w"].iloc[0], color="C2", ls=":", label=f"jump={jrow['jump_w'].iloc[0]:.3g}")
        ax.set_xlabel("w")
        ax.set_ylabel("Mean observations")
        ax.set_title(name)
        ax.legend(fontsize=7)
        ax.grid(True, alpha=0.3)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)


# ---------------------------------------------------------------------------
# 4. Dual descent online
# ---------------------------------------------------------------------------

def run_dual_descent(
    n_episodes: int,
    budget: float,
    lr: float,
    lr_decay: float,
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
        lr_decay=lr_decay,
        planning_horizon=3,
        initial_weight=1.0,
    )
    # Reference from a quick curve
    ref_curve = estimate_usage_curve(
        env,
        w_grid=make_log_w_grid(0.0, 50.0, 10),
        seeds=[seed],
        num_episodes=max(20, n_episodes // 20),
        planning_horizon=3,
    )
    ref = solve_shadow_price_from_curve(ref_curve, budget=budget, tol=1.0)
    rows = []
    print(
        f"\n=== Dual descent Diagnosis  B={budget}  lr0={lr}  decay={lr_decay}  "
        f"curve w*≈{ref.w_star:.4g} ===",
        flush=True,
    )
    for t in range(n_episodes):
        if rescale_at is not None and t == rescale_at:
            env = make_scaled_diagnosis(rescale_factor)
            cur_w = agent.weight
            old_w_hist = list(agent.weight_history)
            old_avg_hist = list(agent.avg_weight_history)
            old_u_hist = list(agent.usage_history)
            old_lr_hist = list(agent.lr_history)
            old_n = agent._n_updates
            old_sum = agent._w_sum
            agent = DualWeightAgent(
                get_obs_models(env),
                make_env_config(env),
                budget=budget,
                lr=lr,
                lr_decay=lr_decay,
                planning_horizon=3,
                initial_weight=cur_w,
            )
            agent.weight_history = old_w_hist
            agent.avg_weight_history = old_avg_hist
            agent.usage_history = old_u_hist
            agent.lr_history = old_lr_hist
            agent._n_updates = old_n
            agent._w_sum = old_sum
            print(f"  t={t}: rescale rewards ×{rescale_factor}, keep w={cur_w:.4g}", flush=True)

        result = run_otc_episode(agent, env)
        u = usage_value(episode_sensing_usage(result), "count")
        new_w = agent.end_episode(u)
        rows.append(
            {
                "episode": t,
                "usage": u,
                "weight": new_w,
                "w_avg": agent.w_avg,
                "lr": agent.lr_history[-1],
                "budget": budget,
                "curve_w_star": ref.w_star,
                "rescaled": bool(rescale_at is not None and t >= rescale_at),
                "reward": result["total_reward"],
                "success": result["success"],
            }
        )
        if (t + 1) % max(1, n_episodes // 10) == 0:
            recent = np.mean([r["usage"] for r in rows[-20:]])
            print(
                f"  t={t+1}/{n_episodes}  w={new_w:.4g}  w_avg={agent.w_avg:.4g}  "
                f"recent_U={recent:.2f}",
                flush=True,
            )
    return pd.DataFrame(rows)


def plot_dual_descent(df: pd.DataFrame, path: Path) -> None:
    fig, axes = plt.subplots(2, 1, figsize=(7.5, 5.8), sharex=True)
    axes[0].plot(df["episode"], df["weight"], label="w_t", alpha=0.7)
    axes[0].plot(df["episode"], df["w_avg"], label="w_avg", lw=2)
    axes[0].axhline(df["curve_w_star"].iloc[0], color="C2", ls="--", label="curve w*")
    if df["rescaled"].any():
        t0 = int(df.loc[df["rescaled"], "episode"].iloc[0])
        axes[0].axvline(t0, color="gray", ls=":", label="rescale")
        axes[1].axvline(t0, color="gray", ls=":")
    axes[0].set_ylabel("Weight w")
    axes[0].legend(fontsize=8)
    axes[0].grid(True, alpha=0.3)

    window = max(5, len(df) // 20)
    smooth = df["usage"].rolling(window, min_periods=1).mean()
    axes[1].plot(df["episode"], smooth, label=f"usage (roll-{window})")
    axes[1].axhline(df["budget"].iloc[0], color="C1", ls="--", label="budget B")
    axes[1].set_xlabel("Episode")
    axes[1].set_ylabel("Usage")
    axes[1].legend(fontsize=8)
    axes[1].grid(True, alpha=0.3)
    fig.suptitle("Online dual control of w (decayed lr + Polyak average)")
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
        curve = estimate_usage_curve(
            env,
            w_grid=[1.0],
            seeds=seeds,
            num_episodes=num_episodes,
            planning_horizon=cfg.planning_horizon,
            family=cfg.family,
            tree_depth=cfg.tree_depth,
        )
        p = curve[0]
        rows.append(
            {
                "env": name,
                "w": 1.0,
                "implicit_budget": p.mean_usage,
                "se": p.se_usage,
                "family": cfg.family,
            }
        )
        print(f"  B_EFE = U(w=1) = {p.mean_usage:.3f}±{p.se_usage:.3f}", flush=True)
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
        help="quick: reduced seeds/episodes; full: paper-scale",
    )
    p.add_argument(
        "--only",
        nargs="*",
        default=None,
        help="Subset: curves scale prop2 dual efe",
    )
    return p.parse_args()


def main() -> None:
    args = parse_args()
    _ensure_dirs()
    only = set(args.only) if args.only else {"curves", "scale", "prop2", "dual", "efe"}

    if args.mode == "full":
        seeds = [42, 123, 456, 789, 1024]
        ep = 100
        n_grid = 16
        dual_episodes = 400
        # OTC envs at full power; Tileworld/Inspection use lighter settings
        # (tree search cost) while remaining in the battery.
        env_names = ["Tiger", "Diagnosis", "Bandit", "Tileworld-6x6", "Inspection-N8"]
        episodes_by_env = {
            "Tileworld-6x6": 40,
            "Inspection-N8": 30,
        }
        grid_by_env = {
            "Tileworld-6x6": 10,
            "Inspection-N8": 8,
        }
        scale_envs = ["Diagnosis", "Bandit"]
        scale_budget = 8.0
        dual_budget = 8.0
        dual_lr0 = 0.05
        dual_decay = 0.02
    else:
        seeds = [42, 123, 456]
        ep = 40
        n_grid = 10
        dual_episodes = 200
        env_names = ["Tiger", "Diagnosis", "Bandit"]
        episodes_by_env = {}
        grid_by_env = {}
        scale_envs = ["Diagnosis"]
        scale_budget = 8.0
        dual_budget = 8.0
        dual_lr0 = 0.05
        dual_decay = 0.02

    summary: dict = {"mode": args.mode, "seeds": list(seeds), "episodes": ep}

    if "curves" in only:
        curve_df, price_df = run_shadow_price_curves(
            env_names,
            seeds,
            ep,
            n_grid=n_grid,
            n_budgets=5,
            episodes_by_env=episodes_by_env,
            grid_by_env=grid_by_env,
        )
        curve_df.to_csv(RESULTS / "results_price_usage_curves.csv", index=False)
        price_df.to_csv(RESULTS / "results_price_shadow_curves.csv", index=False)
        if not price_df.empty:
            plot_shadow_price_curves(price_df, FIGURES / "price_shadow_curves.png")
        summary["curves_rows"] = len(price_df)
        summary["usage_curve_rows"] = len(curve_df)

    if "scale" in only:
        all_curve = []
        all_cross = []
        all_collapse = []
        for env_kind in scale_envs:
            # Unpack carefully: function returns 3 dataframes
            out = run_scale_collapse(
                scales=[0.1, 1.0, 10.0],
                seeds=seeds,
                num_episodes=ep,
                n_grid=max(10, n_grid - 2),
                budget=scale_budget,
                env_kind=env_kind,
            )
            c_df, x_df, col_df = out
            all_curve.append(c_df)
            all_cross.append(x_df)
            all_collapse.append(col_df)
            if env_kind == scale_envs[0] and not c_df.empty:
                plot_scale_collapse(
                    c_df, x_df, FIGURES / "price_scale_invariance.png", budget=scale_budget
                )
        curve_df = pd.concat(all_curve, ignore_index=True) if all_curve else pd.DataFrame()
        cross_df = pd.concat(all_cross, ignore_index=True) if all_cross else pd.DataFrame()
        collapse_df = pd.concat(all_collapse, ignore_index=True) if all_collapse else pd.DataFrame()
        curve_df.to_csv(RESULTS / "results_price_scale_curves.csv", index=False)
        cross_df.to_csv(RESULTS / "results_price_scale_invariance.csv", index=False)
        collapse_df.to_csv(RESULTS / "results_price_scale_collapse.csv", index=False)
        if not collapse_df.empty:
            summary["collapse_frac_within_noise"] = float(collapse_df["within_noise"].mean())
            summary["collapse_max_spread"] = float(collapse_df["usage_spread"].max())
        summary["scale_rows"] = len(cross_df)

    if "prop2" in only:
        jump_df, pcurve_df, sanity_df = run_prop2_duality(seeds, ep, n_grid=12)
        jump_df.to_csv(RESULTS / "results_price_prop2_jumps.csv", index=False)
        pcurve_df.to_csv(RESULTS / "results_price_prop2_curves.csv", index=False)
        sanity_df.to_csv(RESULTS / "results_price_prop2_duality.csv", index=False)
        if not pcurve_df.empty:
            plot_prop2_jumps(pcurve_df, jump_df, FIGURES / "price_prop2_jumps.png")
        summary["prop2_jump_ok"] = (
            bool(jump_df["jump_ok"].all()) if not jump_df.empty else False
        )
        summary["prop2_rows"] = len(jump_df)

    if "dual" in only:
        df = run_dual_descent(
            n_episodes=dual_episodes,
            budget=dual_budget,
            lr=dual_lr0,
            lr_decay=dual_decay,
            rescale_at=dual_episodes // 2,
            rescale_factor=10.0,
        )
        df.to_csv(RESULTS / "results_price_dual_descent.csv", index=False)
        plot_dual_descent(df, FIGURES / "price_dual_descent.png")
        # Ratio of post/pre Polyak averages near the end of each half
        pre = df.loc[~df["rescaled"], "w_avg"]
        post = df.loc[df["rescaled"], "w_avg"]
        if len(pre) and len(post):
            pre_avg = float(pre.iloc[-min(20, len(pre)):].mean())
            post_avg = float(post.iloc[-min(20, len(post)):].mean())
            ratio = post_avg / pre_avg if pre_avg > 1e-9 else float("nan")
            summary["dual_w_avg_ratio_post_pre"] = ratio
            summary["dual_pre_usage"] = float(df.loc[~df["rescaled"], "usage"].tail(20).mean())
            summary["dual_post_usage"] = float(df.loc[df["rescaled"], "usage"].tail(20).mean())
        summary["dual_rows"] = len(df)

    if "efe" in only:
        df = run_implicit_efe_budget(env_names, seeds, ep)
        df.to_csv(RESULTS / "results_price_efe_implicit_budget.csv", index=False)
        summary["efe_rows"] = len(df)

    with open(RESULTS / "results_price_of_information_summary.json", "w") as f:
        json.dump(summary, f, indent=2)
    print("\nDone.", json.dumps(summary, indent=2), flush=True)


if __name__ == "__main__":
    main()
