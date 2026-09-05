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
import math
import sys
from pathlib import Path
from typing import Callable, Dict, List, Optional, Sequence, Tuple

_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT))
sys.path.insert(0, str(_ROOT / "experiments"))

import matplotlib

matplotlib.use("Agg")
import matplotlib.patches as mpl_patches
import matplotlib.pyplot as plt
import matplotlib.ticker
import numpy as np
import pandas as pd
from matplotlib.lines import Line2D

from rho_aif import figstyle
from rho_aif.agents.dual_descent import DualWeightAgent
from rho_aif.benchmark import get_benchmark, get_obs_models, make_env_config, run_otc_episode
from rho_aif.budget import (
    UsageCurvePoint,
    crossing_bracket,
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


def make_scaled_tiger(k: float) -> TigerEnv:
    return TigerEnv(
        listen_accuracy=0.85,
        listen_cost=1.0 * k,
        correct_reward=10.0 * k,
        incorrect_penalty=-100.0 * k,
    )


def make_scaled_tileworld(k: float):
    from rho_aif.environments.tileworld import TileworldEnv

    return TileworldEnv(
        grid_size=6,
        scan_accuracy=0.80,
        scan_cost=1.0 * k,
        correct_reward=10.0 * k,
        incorrect_penalty=-50.0 * k,
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


def _savefig(fig, path: Path) -> None:
    """Save figure as PNG (always) and PDF when path is .png or .pdf."""
    path = Path(path)
    fig.savefig(path, dpi=150)
    if path.suffix.lower() == ".png":
        fig.savefig(path.with_suffix(".pdf"))
    elif path.suffix.lower() == ".pdf":
        fig.savefig(path.with_suffix(".png"), dpi=150)


def _log_x_with_zero(ax, min_pos: float, max_pos: float) -> float:
    """Configure a log x-axis for w > 0 with an explicit w = 0 position.

    A weight axis is never negative, so instead of symlog (which renders
    negative decade ticks) the axis is a true log axis over the positive
    grid, with the w = 0 point drawn at a reserved position left of the
    smallest positive decade, marked by a literal "0" tick and a
    broken-axis marker. Returns the x position at which w = 0 data should
    be plotted.
    """
    zero_pos = min_pos / 6.0
    ax.set_xscale("log")
    ax.set_xlim(zero_pos / 2.2, max_pos * 1.7)
    lo_dec = int(math.floor(math.log10(min_pos)))
    hi_dec = int(math.floor(math.log10(max_pos)))
    ticks = [zero_pos] + [10.0 ** k for k in range(lo_dec, hi_dec + 1)]
    labels = ["$0$"] + [f"$10^{{{k}}}$" for k in range(lo_dec, hi_dec + 1)]
    ax.set_xticks(ticks)
    ax.set_xticklabels(labels)
    ax.xaxis.set_minor_locator(matplotlib.ticker.NullLocator())
    # Broken-axis slashes between the "0" tick and the first positive decade.
    xb = math.sqrt(zero_pos * min_pos)
    for factor in (0.94, 1.07):
        ax.plot(
            [xb * factor],
            [0],
            transform=ax.get_xaxis_transform(),
            marker=(2, 0, -65),
            markersize=7,
            markeredgewidth=1.0,
            color="black",
            clip_on=False,
            zorder=5,
        )
    return zero_pos


# Display names for environment series, matching the manuscripts' math
# typesetting (Tileworld-$6{\times}6$, Inspection-$N{=}8$, ...).
ENV_DISPLAY = {
    "Tileworld-6x6": "Tileworld-$6{\\times}6$",
    "Tileworld-8x8": "Tileworld-$8{\\times}8$",
    "Inspection-N8": "Inspection-$N{=}8$",
    "Inspection-N16": "Inspection-$N{=}16$",
}

# Ceiling of the tested log-w grid (make_log_w_grid(0, 100, .)). A bracketed
# row whose w_hi sits here is closed at 100 under Definition PI-3, because
# ``bracketed`` means U(w_hi) >= B was observed on the grid. Only an
# unbracketed row (budget above the observed usage range, budget.py's
# flagged fallback) is genuinely unresolved above the grid. Until 2026-09-05
# every w_hi = 100 bar was drawn with an arrowhead, which overstated the
# uncertainty of brackets the manuscript's own atlas prints as (w_lo, 100].
W_GRID_TOP = 100.0


def plot_shadow_price_curves(price_df: pd.DataFrame, path: Path) -> None:
    """Staircase of w*(B) per environment with crossing-bracket bars.

    Encoding conventions:
    - brackets are drawn in the series color with end ticks (same treatment
      as plot_scale_collapse), so they cannot be read as SE error bars;
    - slack budgets (w* = 0, or w* below its own recorded bracket) draw an
      open marker and a dotted bracket for the first binding crossing;
    - brackets whose upper edge sits at the top of the tested w grid are
      capped there like any other bracket, since a bracketed row has
      U(100) >= B and is closed at 100 under Definition PI-3, with a dotted
      rule marking the grid ceiling. Only an unbracketed row (budget above
      the observed usage range) terminates in an upward arrowhead, and the
      legend names that glyph only when such a row is plotted.
    """
    figstyle.apply()
    fig, ax = plt.subplots(figsize=figstyle.figsize(1.0, 0.58))
    envs = sorted(price_df["env"].unique())
    # Linear symlog band sized to the smallest positive plotted value so the
    # w* = 0 leg does not inflate to a full decade of dead space.
    pos_vals = pd.concat(
        [price_df.loc[price_df["w_star"] > 0, "w_star"],
         price_df.loc[price_df["w_lo"] > 0, "w_lo"]]
    )
    linthresh = float(pos_vals.min()) if len(pos_vals) else 0.1
    arrow_tip = 170.0
    any_unresolved = False
    for env_name in envs:
        sub = price_df[price_df["env"] == env_name].sort_values("budget")
        c = figstyle.env_color(env_name)
        ax.step(
            sub["budget"], sub["w_star"], where="mid", color=c,
            label=ENV_DISPLAY.get(env_name, env_name), zorder=2,
        )
        slack = (sub["w_star"] <= 0) | (sub["w_star"] < sub["w_lo"])
        bind = sub[~slack]
        ax.scatter(bind["budget"], bind["w_star"], s=20, color=c, zorder=4)
        sl = sub[slack]
        ax.scatter(
            sl["budget"], sl["w_star"], s=20, facecolors="none",
            edgecolors=c, linewidths=1.1, zorder=4,
        )
        # Vertical bars: the set-valued crossing bracket (w_lo, w_hi] at each B.
        for _, row in sub.iterrows():
            B = float(row["budget"])
            lo, hi = float(row["w_lo"]), float(row["w_hi"])
            is_slack = row["w_star"] <= 0 or row["w_star"] < lo
            bar_alpha = 0.35 if is_slack else 0.5
            bar_ls = ":" if is_slack else "-"
            unresolved = ("bracketed" in row.index) and not bool(row["bracketed"])
            if unresolved:
                any_unresolved = True
                # Budget above the observed usage range: the upper edge is
                # not on the grid, so an arrowhead rather than a capped bar.
                ax.annotate(
                    "", xy=(B, arrow_tip), xytext=(B, lo),
                    arrowprops=dict(
                        arrowstyle="-|>", color=c, alpha=bar_alpha,
                        lw=1.3, linestyle=bar_ls, mutation_scale=8,
                    ),
                    zorder=1,
                )
                ax.plot([B / 1.025, B * 1.025], [lo, lo], color=c,
                        alpha=bar_alpha, lw=1.2, zorder=1)
            else:
                ax.plot([B, B], [lo, hi], color=c, alpha=bar_alpha,
                        lw=1.4, ls=bar_ls, zorder=1)
                for v in (lo, hi):
                    ax.plot([B / 1.025, B * 1.025], [v, v], color=c,
                            alpha=bar_alpha, lw=1.2, zorder=1)
    # Log budget axis: keeps the small-budget staircases readable when one
    # series (e.g. Inspection-N16) spans much larger budgets.
    ax.set_xscale("log")
    bmin = float(price_df["budget"].min())
    bmax = float(price_df["budget"].max())
    xticks = [t for t in (2, 3, 5, 7, 10, 15, 20, 30, 50, 70)
              if bmin / 1.15 <= t <= bmax * 1.15]
    ax.set_xticks(xticks)
    ax.set_xticklabels([f"{t:g}" for t in xticks])
    ax.xaxis.set_minor_locator(matplotlib.ticker.NullLocator())
    ax.set_xlabel("Sensing budget $B$ (mean observations, log scale)")
    ax.set_ylabel("Shadow price $w^*(B)$")
    # symlog: w* is 0 at slack budgets, so the "0" tick is a real data value.
    ax.set_yscale("symlog", linthresh=linthresh)
    yticks = [0.0] + [d for d in (0.1, 1.0, 10.0, 100.0) if d >= linthresh - 1e-12]
    ax.set_yticks(yticks)
    ax.set_yticklabels(
        ["$0$"] + [f"$10^{{{int(round(math.log10(d)))}}}$" for d in yticks[1:]]
    )
    ax.set_ylim(-0.35 * linthresh, 300.0)
    # Dotted rule at the grid ceiling, the largest tested weight.
    ax.axhline(W_GRID_TOP, color=figstyle.GRAY, ls=":", lw=0.8, zorder=0)
    ax.annotate(
        "top of tested $w$ grid", xy=(0.01, W_GRID_TOP * 1.12),
        xycoords=("axes fraction", "data"), fontsize=7.5,
        color=figstyle.GRAY, ha="left", va="bottom",
    )
    figstyle.style_axis(ax)
    handles, _ = ax.get_legend_handles_labels()
    handles.append(
        Line2D(
            [], [], color=figstyle.GRAY, alpha=0.6, lw=1.4,
            label="bracket $(w_{\\mathrm{lo}}, w_{\\mathrm{hi}}]$ (series color)",
        )
    )
    handles.append(
        Line2D(
            [], [], color=figstyle.GRAY, alpha=0.6, lw=1.4, ls=":",
            marker="o", markerfacecolor="none", markersize=4.5,
            label="slack budget: $w^*$ below first binding bracket",
        )
    )
    if any_unresolved:
        handles.append(
            Line2D(
                [], [], color=figstyle.GRAY, alpha=0.6, lw=1.4,
                marker="^", markersize=5,
                label="unbracketed: budget above observed usage range",
            )
        )
    ax.legend(
        handles=handles, ncol=3, loc="upper center",
        bbox_to_anchor=(0.5, -0.22), frameon=False,
    )
    fig.tight_layout()
    _savefig(fig, path)
    plt.close(fig)


# ---------------------------------------------------------------------------
# 1b. Interleaved usage curves (Stage B of the full-paper plan)
# ---------------------------------------------------------------------------

def _interleaved_configs() -> Dict[str, dict]:
    """
    Interleaved observe-act settings: RockSample (research code, configs from
    run_rocksample.py) and Inspection-N16 (benchmark config).
    """
    from run_rocksample import ROCKSAMPLE_CONFIGS
    from rho_aif.environments.rocksample import RockSampleEnv

    def make_rs(config_name: str):
        cfg = ROCKSAMPLE_CONFIGS[config_name]
        max_steps = cfg["grid_size"] ** 2 + cfg["num_rocks"] * 10
        env = RockSampleEnv(
            grid_size=cfg["grid_size"],
            num_rocks=cfg["num_rocks"],
            rock_positions=cfg["rock_positions"],
            move_cost=-0.5,
            max_steps=max_steps,
        )
        return env, cfg["tree_depth"], max_steps

    out: Dict[str, dict] = {}
    for rs_name in ("RS[5,3]", "RS[7,4]"):
        env, depth, max_steps = make_rs(rs_name)
        out[rs_name] = {
            "env": env,
            "family": "rocksample",
            "tree_depth": depth,
            "max_steps": max_steps,
            "planning_horizon": depth,
        }
    insp = get_benchmark("Inspection-N16")
    out["Inspection-N16"] = {
        "env": insp.env_factory(),
        "family": insp.family,
        "tree_depth": insp.tree_depth,
        "max_steps": 200,
        "planning_horizon": insp.planning_horizon,
    }
    return out


def run_interleaved_curves(
    env_names: Sequence[str],
    seeds: Sequence[int],
    num_episodes: int,
    n_grid: int = 10,
    n_budgets: int = 4,
    episodes_by_env: Optional[Dict[str, int]] = None,
    grid_by_env: Optional[Dict[str, int]] = None,
) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """Usage curves + crossing brackets on interleaved observe-act settings."""
    configs = _interleaved_configs()
    curve_rows: List[dict] = []
    price_rows: List[dict] = []
    episodes_by_env = episodes_by_env or {}
    grid_by_env = grid_by_env or {}

    for name in env_names:
        cfg = configs[name]
        ep = int(episodes_by_env.get(name, num_episodes))
        ng = int(grid_by_env.get(name, n_grid))
        print(
            f"\n=== Interleaved: {name} ({cfg['family']})  ep={ep} grid={ng} ===",
            flush=True,
        )
        w_grid = make_log_w_grid(0.0, 100.0, ng)
        curve = []
        for i, w in enumerate(w_grid):
            print(f"  [{i+1}/{len(w_grid)}] estimating U(w={float(w):.4g}) ...", flush=True)
            pts = estimate_usage_curve(
                cfg["env"],
                w_grid=[float(w)],
                seeds=seeds,
                num_episodes=ep,
                planning_horizon=cfg["planning_horizon"],
                usage_kind="count",
                family=cfg["family"],
                tree_depth=cfg["tree_depth"],
                max_steps=cfg["max_steps"],
            )
            curve.extend(pts)
            p = pts[0]
            print(f"    U={p.mean_usage:.3f}±{p.se_usage:.3f}", flush=True)
        curve_rows.extend(curve_to_rows(name, curve))
        u_min = min(p.mean_usage for p in curve)
        u_max = max(p.mean_usage for p in curve)
        print(f"  U range [{u_min:.3f}, {u_max:.3f}]", flush=True)

        budgets = identifiable_budgets(curve, n_budgets=n_budgets, margin=0.08)
        for B in budgets:
            res = solve_shadow_price_from_curve(
                curve, budget=float(B), tol=max(0.3, 0.1 * float(B))
            )
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
        pd.DataFrame(curve_rows).to_csv(
            RESULTS / "results_price_interleaved_curves.csv", index=False
        )
        pd.DataFrame(price_rows).to_csv(
            RESULTS / "results_price_interleaved_prices.csv", index=False
        )
    return pd.DataFrame(curve_rows), pd.DataFrame(price_rows)


# ---------------------------------------------------------------------------
# 1c. Cost-denominated budgets (Stage D of the full-paper plan)
# ---------------------------------------------------------------------------

def make_hetero_diagnosis() -> DiagnosisEnv:
    """Diagnosis with heterogeneous per-test costs (cheap 0.5, expensive 2.5)."""
    return DiagnosisEnv(
        num_conditions=4,
        test_accuracy=0.80,
        correct_reward=10.0,
        incorrect_penalty=-50.0,
        test_costs=[0.5, 2.5],
    )


def run_cost_budget(
    seeds: Sequence[int],
    num_episodes: int,
    n_grid: int = 12,
    n_budgets: int = 2,
) -> Tuple[pd.DataFrame, pd.DataFrame, dict]:
    """
    Count- vs cost-denominated usage curves and shadow-price brackets on a
    heterogeneous-cost Diagnosis variant. The unit story is nontrivial iff
    the mean cost per test U_cost/U_count varies with w (test mix shifts).
    """
    env = make_hetero_diagnosis()
    w_grid = make_log_w_grid(0.0, 100.0, n_grid)
    curve_rows: List[dict] = []
    curves: Dict[str, list] = {}
    print(
        f"\n=== Cost budgets: Diagnosis-hetero (test costs {env.get_observation_costs()}) ===",
        flush=True,
    )
    for kind in ("count", "cost"):
        curve = []
        for i, w in enumerate(w_grid):
            pts = estimate_usage_curve(
                env,
                w_grid=[float(w)],
                seeds=seeds,
                num_episodes=num_episodes,
                planning_horizon=3,
                usage_kind=kind,
            )
            curve.extend(pts)
            print(
                f"  [{kind} {i+1}/{len(w_grid)}] U(w={float(w):.4g}) = "
                f"{pts[0].mean_usage:.3f}±{pts[0].se_usage:.3f}",
                flush=True,
            )
        curves[kind] = curve
        curve_rows.extend(curve_to_rows("Diagnosis-hetero", curve, extra={"usage_kind": kind}))
        pd.DataFrame(curve_rows).to_csv(
            RESULTS / "results_price_cost_curves.csv", index=False
        )

    price_rows: List[dict] = []
    for kind in ("count", "cost"):
        curve = curves[kind]
        budgets = identifiable_budgets(curve, n_budgets=n_budgets, margin=0.15)
        for B in budgets:
            res = solve_shadow_price_from_curve(curve, budget=float(B), tol=max(0.3, 0.1 * float(B)))
            price_rows.append(
                {
                    "env": "Diagnosis-hetero",
                    "usage_kind": kind,
                    "budget": float(B),
                    "w_star": res.w_star,
                    "w_lo": res.w_lo,
                    "w_hi": res.w_hi,
                    "usage_at_star": res.usage_at_star,
                    "usage_se_at_star": res.usage_se_at_star,
                    "bracketed": res.bracketed,
                    "achievable": res.achievable,
                }
            )
            print(
                f"  {kind}: B={B:.3f}  w*={res.w_star:.4g}  "
                f"bracket=[{res.w_lo:.3g},{res.w_hi:.3g}]",
                flush=True,
            )

    # Mean cost per test as a function of w: constant iff units are trivially
    # interchangeable (matched w grid, same seeds/episodes).
    ratios = []
    for pc, pg in zip(curves["count"], curves["cost"]):
        if pc.mean_usage > 0:
            ratios.append(pg.mean_usage / pc.mean_usage)
    metrics = {
        "cost_ratio_min": float(np.min(ratios)) if ratios else float("nan"),
        "cost_ratio_max": float(np.max(ratios)) if ratios else float("nan"),
        "cost_ratio_rel_spread": (
            float((np.max(ratios) - np.min(ratios)) / np.mean(ratios)) if ratios else float("nan")
        ),
        "cost_test_costs": env.get_observation_costs(),
    }
    print(
        f"  cost/test ratio range [{metrics['cost_ratio_min']:.3f}, "
        f"{metrics['cost_ratio_max']:.3f}]  rel spread "
        f"{100*metrics['cost_ratio_rel_spread']:.1f}%",
        flush=True,
    )
    return pd.DataFrame(curve_rows), pd.DataFrame(price_rows), metrics


def plot_cost_budget(
    curve_df: pd.DataFrame,
    path: Path,
    price_df: Optional[pd.DataFrame] = None,
) -> None:
    """(a) count and cost usage curves with the tested budgets and their
    shared crossing brackets. (b) mean cost per test vs w, zoomed to the
    range the ratio actually occupies."""
    figstyle.apply()
    fig, axes = plt.subplots(1, 2, figsize=figstyle.figsize(1.0, 0.45))
    ax = axes[0]
    pos_w = curve_df.loc[curve_df["w"] > 0, "w"]
    zero_pos = _log_x_with_zero(ax, float(pos_w.min()), float(pos_w.max()))
    kind_style = {
        "count": (figstyle.BLUE, "o", "$U_{\\mathrm{count}}(w)$"),
        "cost": (figstyle.ORANGE, "s", "$U_{\\mathrm{cost}}(w)$"),
    }
    for kind, (color, marker, label) in kind_style.items():
        sub = curve_df[curve_df["usage_kind"] == kind].sort_values("w")
        xs = np.where(sub["w"] > 0, sub["w"], zero_pos)
        ax.errorbar(
            xs,
            sub["mean_usage"],
            yerr=sub["se_usage"],
            marker=marker,
            ms=4,
            capsize=figstyle.CAPSIZE,
            color=color,
            label=label,
        )
    # Tested operating points: budget rules per usage kind, plus the shared
    # crossing brackets (the caption's coincidence claim, drawn not asserted).
    if price_df is not None and not price_df.empty:
        kind_color = {"count": figstyle.BLUE, "cost": figstyle.ORANGE}
        # Budget labels sit at the LEFT edge, where every usage curve is flat
        # and nothing else is drawn, so they cannot collide with the bracket
        # labels anchored near the top right (audit: label overprint at B=19.20).
        x_left = float(pos_w.min()) * 1.15
        spans: Dict[Tuple[float, float], None] = {}
        for _, row in price_df.sort_values("budget").iterrows():
            c = kind_color.get(str(row["usage_kind"]), figstyle.GRAY)
            b = float(row["budget"])
            ax.axhline(b, ls="--", lw=0.9, alpha=0.55, color=c, zorder=1)
            ax.annotate(
                f"$B{{=}}{b:.2f}$", (x_left, b), fontsize=7,
                color=c, ha="left", va="bottom",
            )
            spans[(round(float(row["w_lo"]), 6), round(float(row["w_hi"]), 6))] = None
        for i, (lo, hi) in enumerate(sorted(spans)):
            ax.axvspan(lo, hi, color=figstyle.GRAY, alpha=0.10 + 0.08 * i, zorder=0)
            ax.annotate(
                f"$w^*\\!\\in\\!({lo:.3g}, {hi:.3g}]$",
                (math.sqrt(lo * hi), 0.99 - 0.08 * i),
                xycoords=("data", "axes fraction"),
                fontsize=7, color="0.35", ha="center", va="top",
            )
    ax.set_xlabel("Info-gain weight $w$")
    ax.set_ylabel(
        "Usage per episode\n($U_{\\mathrm{count}}$: observations, "
        "$U_{\\mathrm{cost}}$: cost units)"
    )
    ax.set_title("(a) Usage curves")
    figstyle.style_axis(ax)
    # Anchored below the B=19.20 rule so no budget rule runs through the text.
    ax.legend(loc="upper left", bbox_to_anchor=(0.02, 0.86))

    ax2 = axes[1]
    zero_pos2 = _log_x_with_zero(ax2, float(pos_w.min()), float(pos_w.max()))
    piv = curve_df.pivot_table(index="w", columns="usage_kind", values="mean_usage")
    piv_se = curve_df.pivot_table(index="w", columns="usage_kind", values="se_usage")
    piv_se = piv_se.loc[piv["count"] > 0]
    piv = piv[piv["count"] > 0]
    ratio = piv["cost"] / piv["count"]
    # Delta-method SE of the ratio from the two usage SEs.
    ratio_se = ratio * np.sqrt(
        (piv_se["cost"] / piv["cost"]) ** 2 + (piv_se["count"] / piv["count"]) ** 2
    )
    xs2 = np.where(piv.index.to_numpy() > 0, piv.index.to_numpy(), zero_pos2)
    ax2.errorbar(
        xs2, ratio, yerr=ratio_se, marker="o", ms=4,
        capsize=figstyle.CAPSIZE, color=figstyle.GREEN,
    )
    # Zoom to the range the ratio occupies; the reference per-test costs are
    # far outside it and are reported as a corner note instead of rules.
    ax2.set_ylim(1.20, 1.45)
    ax2.text(
        0.02, 0.97,
        "reference costs: cheap 0.5,\nuniform mix 1.5, expensive 2.5",
        transform=ax2.transAxes, fontsize=7.5, color=figstyle.GRAY, va="top",
    )
    ax2.set_xlabel("Info-gain weight $w$")
    ax2.set_ylabel("Mean cost per test $U_{\\mathrm{cost}}/U_{\\mathrm{count}}$")
    ax2.set_title("(b) Mean cost per test")
    figstyle.style_axis(ax2)
    fig.tight_layout()
    _savefig(fig, path)
    plt.close(fig)


# ---------------------------------------------------------------------------
# 2. Curve-collapse scale test
# ---------------------------------------------------------------------------

def _curve_points_from_df(sub: pd.DataFrame) -> List[UsageCurvePoint]:
    """Rebuild UsageCurvePoint list from a saved scale-curve subframe."""
    pts: List[UsageCurvePoint] = []
    for _, row in sub.sort_values("w").iterrows():
        pts.append(
            UsageCurvePoint(
                w=float(row["w"]),
                mean_usage=float(row["mean_usage"]),
                se_usage=float(row["se_usage"]) if np.isfinite(row["se_usage"]) else float("nan"),
                n_seeds=int(row["n_seeds"]) if "n_seeds" in row and pd.notna(row["n_seeds"]) else 0,
                per_seed_means=[],
            )
        )
    return pts


def _scale_crossings_from_curves(
    curve_df: pd.DataFrame,
    budget: float,
) -> pd.DataFrame:
    """Compute crossing brackets in w and w/α units from saved usage curves."""
    rows: List[dict] = []
    for (env_kind, alpha), sub in curve_df.groupby(["env", "scale_k"]):
        curve = _curve_points_from_df(sub)
        br = crossing_bracket(curve, budget=budget)
        a = float(alpha)
        rows.append(
            {
                "env": env_kind,
                "scale_k": a,
                "budget": budget,
                "w_lo": br.w_lo,
                "w_hi": br.w_hi,
                "w_lo_over_alpha": br.w_lo / a if a else float("nan"),
                "w_hi_over_alpha": br.w_hi / a if a else float("nan"),
                "usage_lo": br.usage_lo,
                "usage_hi": br.usage_hi,
                "bracketed": br.bracketed,
                "achievable": br.achievable,
                "note": br.note,
                # Keep legacy point fields for compatibility (mid-bracket).
                "w_star": 0.5 * (br.w_lo + br.w_hi),
                "w_star_over_alpha": (
                    0.5 * (br.w_lo + br.w_hi) / a if a else float("nan")
                ),
                "usage_at_star": 0.5 * (br.usage_lo + br.usage_hi),
                "usage_se": float("nan"),
            }
        )
        print(
            f"  [{env_kind} α={a:g}] B={budget}: bracket w/α=("
            f"{rows[-1]['w_lo_over_alpha']:.4g}, {rows[-1]['w_hi_over_alpha']:.4g}]  "
            f"U=({br.usage_lo:.3f}, {br.usage_hi:.3f}]",
            flush=True,
        )
    return pd.DataFrame(rows)


def _collapse_stats(curve_df: pd.DataFrame, env_kind: Optional[str] = None) -> pd.DataFrame:
    collapse_rows = []
    if curve_df.empty:
        return pd.DataFrame()
    df = curve_df.copy()
    if env_kind is not None:
        df = df[df["env"] == env_kind]
    df["w_key"] = df["w_over_alpha"].round(6)
    for (env, key), sub in df.groupby(["env", "w_key"]):
        if len(sub) < 2:
            continue
        spread = float(sub["mean_usage"].max() - sub["mean_usage"].min())
        mean_se = float(np.nanmean(sub["se_usage"]))
        collapse_rows.append(
            {
                "env": env,
                "w_over_alpha": float(key),
                "usage_spread": spread,
                "mean_se": mean_se,
                "n_scales": len(sub),
                "within_noise": spread <= max(2.0 * mean_se, 0.5),
            }
        )
    return pd.DataFrame(collapse_rows)


def run_scale_collapse(
    scales: Sequence[float],
    seeds: Sequence[int],
    num_episodes: int,
    n_grid: int = 14,
    budget: float = 8.0,
    env_kind: str = "Diagnosis",
    existing_curve_df: Optional[pd.DataFrame] = None,
) -> Tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Estimate U(w; alpha) on alpha-scaled grids so w/alpha points align.
    Prediction: curves collapse when plotted vs w/alpha.

    When ``existing_curve_df`` is provided (replot mode), skip simulation and
    recompute crossing brackets + collapse stats from the saved curves.

    Returns (curve_df, cross_df, collapse_df).
    """
    if existing_curve_df is not None and not existing_curve_df.empty:
        sub = existing_curve_df[existing_curve_df["env"] == env_kind].copy()
        if not sub.empty:
            print(f"\n=== Scale collapse {env_kind} (replot from saved curves) ===", flush=True)
            cross_df = _scale_crossings_from_curves(sub, budget=budget)
            collapse_df = _collapse_stats(sub, env_kind=env_kind)
            if not collapse_df.empty:
                frac = float(collapse_df["within_noise"].mean())
                max_spread = float(collapse_df["usage_spread"].max())
                print(
                    f"  Collapse: {frac:.0%} of matched points within 2·SE; "
                    f"max spread={max_spread:.3f}",
                    flush=True,
                )
            return sub, cross_df, collapse_df

    makers: Dict[str, Tuple[Callable[[float], object], int]] = {
        "Diagnosis": (make_scaled_diagnosis, 3),
        "Bandit": (make_scaled_bandit, 2),
        "Tiger": (make_scaled_tiger, 6),
        "Tileworld-6x6": (make_scaled_tileworld, 2),
    }
    make_env, horizon = makers[env_kind]
    base_grid = make_log_w_grid(0.0, 20.0, n_grid)  # base = alpha=1 grid
    curve_rows: List[dict] = []

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

    curve_df = pd.DataFrame(curve_rows)
    cross_df = _scale_crossings_from_curves(curve_df, budget=budget) if not curve_df.empty else pd.DataFrame()
    collapse_df = _collapse_stats(curve_df, env_kind=env_kind)
    if not collapse_df.empty:
        frac = float(collapse_df["within_noise"].mean())
        max_spread = float(collapse_df["usage_spread"].max())
        print(
            f"  Collapse: {frac:.0%} of matched points within 2·SE; "
            f"max spread={max_spread:.3f}",
            flush=True,
        )
    return curve_df, cross_df, collapse_df


def plot_scale_collapse(
    curve_df: pd.DataFrame,
    cross_df: pd.DataFrame,
    path: Path,
    budget: float,
) -> None:
    figstyle.apply()
    fig, axes = plt.subplots(
        1, 2, figsize=figstyle.figsize(1.0, 0.45),
        gridspec_kw={"width_ratios": [3, 1]},
    )
    ax = axes[0]
    alphas = sorted(curve_df["scale_k"].unique())
    # Fixed per-alpha colors (deliberately not the env mapping: these series
    # are reward scales within one environment, not environments).
    alpha_palette = [figstyle.BLUE, figstyle.ORANGE, figstyle.GREEN, figstyle.PINK]
    colors = {a: alpha_palette[i % len(alpha_palette)] for i, a in enumerate(alphas)}
    markers = ["o", "s", "^", "D"]
    # Nested open markers of decreasing size; the innermost stays legible at
    # print scale (a 3.8 pt marker did not survive reduction).
    msizes = [11.0, 7.5, 4.6, 2.8]
    pos = curve_df.loc[curve_df["w_over_alpha"] > 0, "w_over_alpha"]
    zero_pos = _log_x_with_zero(ax, float(pos.min()), float(pos.max()))
    # The three alpha curves coincide bit-exactly (that IS the result), so the
    # connecting line and error bars are drawn once in neutral gray and each
    # alpha contributes nested open markers of decreasing size: all three
    # series are visibly present and lie exactly on one curve.
    base_alpha = 1.0 if 1.0 in alphas else alphas[0]
    base = curve_df[curve_df["scale_k"] == base_alpha].sort_values("w_over_alpha")
    xb = np.where(base["w_over_alpha"] > 0, base["w_over_alpha"], zero_pos)
    ax.errorbar(
        xb,
        base["mean_usage"],
        yerr=base["se_usage"],
        color="0.4",
        lw=1.4,
        capsize=figstyle.CAPSIZE,
        marker="",
        zorder=2,
    )
    for i, a in enumerate(alphas):
        sub = curve_df[curve_df["scale_k"] == a].sort_values("w_over_alpha")
        xs = np.where(sub["w_over_alpha"] > 0, sub["w_over_alpha"], zero_pos)
        ax.plot(
            xs,
            sub["mean_usage"],
            linestyle="none",
            marker=markers[i % len(markers)],
            ms=msizes[i % len(msizes)],
            markerfacecolor="none",
            markeredgewidth=1.1,
            color=colors[a],
            label=f"$\\alpha={a:g}$",
            zorder=3 + i,
        )
    ax.axhline(budget, color=figstyle.GRAY, ls="--", lw=1.2, label=f"$B={budget:g}$")
    ax.set_xlabel("$w/\\alpha$")
    ax.set_ylabel("Mean observations per episode $U$")
    ax.set_title("(a) Usage curves across reward scales")
    figstyle.style_axis(ax)
    ax.legend(loc="upper left")

    ax2 = axes[1]
    if not cross_df.empty and "w_lo_over_alpha" in cross_df.columns:
        # Interval bars of the crossing bracket in w/α units per scale.
        # Scale invariance <=> brackets coincide across α.
        sub = cross_df.sort_values("scale_k")
        xs = np.arange(len(sub))
        labels = [f"$\\alpha={a:g}$" for a in sub["scale_k"]]
        lo = sub["w_lo_over_alpha"].to_numpy(dtype=float)
        hi = sub["w_hi_over_alpha"].to_numpy(dtype=float)
        # Shared bracket edges: dashed rules labeled with their values (the
        # quantitative content of the panel), no legend needed.
        lo_shared = float(np.min(lo))
        hi_shared = float(np.max(hi))
        for v in (lo_shared, hi_shared):
            ax2.axhline(v, color=figstyle.GRAY, ls="--", lw=0.9, zorder=1)
        for i, (l, h, a) in enumerate(zip(lo, hi, sub["scale_k"])):
            c = colors.get(float(a), figstyle.BLUE)
            ax2.plot([i, i], [l, h], color=c, lw=3.5, solid_capstyle="butt", zorder=3)
            ax2.plot([i - 0.07, i + 0.07], [l, l], color=c, lw=1.6, zorder=3)
            ax2.plot([i - 0.07, i + 0.07], [h, h], color=c, lw=1.6, zorder=3)
        if len(xs):
            for v, va in ((hi_shared, "bottom"), (lo_shared, "top")):
                ax2.annotate(
                    f"{v:.3f}",
                    (xs[-1] + 0.35, v),
                    fontsize=8.5,
                    color=figstyle.BLACK,
                    va=va,
                    ha="left",
                )
        ax2.set_xticks(xs)
        ax2.set_xticklabels(labels)
        ax2.set_xlim(-0.6, len(xs) - 1 + 1.1)
        span = hi_shared - lo_shared
        ax2.set_ylim(lo_shared - 0.3 * span, hi_shared + 0.3 * span)
        ax2.yaxis.set_major_locator(matplotlib.ticker.MaxNLocator(nbins=6))
        ax2.set_ylabel(f"Crossing bracket $w^*(B{{=}}{budget:g})/\\alpha$")
        ax2.set_title("(b) Brackets")
        figstyle.style_axis(ax2)
    fig.tight_layout()
    _savefig(fig, path)
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
    Positive-threshold onset-bracket test + negative-threshold sanity table.

    Reports the onset bracket (last w with U≈0, first w with U>0.5], not a
    single jump point — the H=1 closed form predicts zero observing for all
    w ≤ w_thresh and onset in (w_thresh, next grid].
    """
    jump_rows: List[dict] = []
    curve_rows: List[dict] = []
    sanity_rows: List[dict] = []

    for name, cfg in POSITIVE_THRESH_CONFIGS.items():
        w_closed = w_thresh_lower(cfg["p"], cfg["c"], cfg["R_plus"], cfg["R_minus"], base=2)
        assert w_closed > 0, f"Expected positive threshold for {name}, got {w_closed}"
        env = cfg["make"]()
        # Coarse grid 0.25x–4x plus refinement just above the threshold so the
        # onset bracket is not limited by the coarse geomspace spacing.
        coarse = np.geomspace(0.25, 4.0, num=max(2, n_grid - 1))
        refine = np.geomspace(1.03, 1.5, num=5)
        factors = np.unique(np.concatenate([[0.0], coarse, refine]))
        w_grid = [float(f * w_closed) if f > 0 else 0.0 for f in factors]
        print(f"\n=== Prop2 positive: {name}  w_thresh={w_closed:.4g} ===", flush=True)
        curve = estimate_usage_curve(
            env,
            w_grid=w_grid,
            seeds=seeds,
            num_episodes=num_episodes,
            planning_horizon=cfg["horizon"],
        )
        us = [p.mean_usage for p in curve]
        u_floor = min(us)
        u_ceil = max(us)
        sorted_curve = sorted(curve, key=lambda x: x.w)
        for p in sorted_curve:
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
        # Onset bracket: (last w with U≈0, first w with U>0.5]
        onset_lo = 0.0
        onset_hi = float("nan")
        for p in sorted_curve:
            if p.mean_usage <= 0.25:
                onset_lo = p.w
            elif not np.isfinite(onset_hi) and p.mean_usage > 0.5 and p.w > 0:
                onset_hi = p.w
                break
        jump_w = onset_hi
        below = [p.mean_usage for p in curve if p.w < w_closed]
        above = [p.mean_usage for p in curve if p.w >= w_closed]
        u_below = float(np.mean(below)) if below else float("nan")
        u_above = float(np.mean(above)) if above else float("nan")
        # Pass: zero below threshold, onset bracket starts at/above w_thresh,
        # and the upper edge is within ~20% after refinement.
        upper_rel = (
            (onset_hi / w_closed - 1.0)
            if (w_closed > 0 and np.isfinite(onset_hi))
            else float("nan")
        )
        jump_ok = bool(
            np.isfinite(onset_hi)
            and onset_lo >= w_closed - 1e-9
            and upper_rel <= 0.20
            and u_floor <= 0.25
            and u_above > u_below + 0.25
        )
        jump_rows.append(
            {
                "env": name,
                "w_thresh": w_closed,
                "onset_lo": onset_lo,
                "onset_hi": onset_hi,
                "jump_w": jump_w,
                "rel_err": upper_rel,
                "U_below": u_below,
                "U_above": u_above,
                "U_floor": u_floor,
                "U_ceil": u_ceil,
                "jump_ok": jump_ok,
            }
        )
        print(
            f"  onset=({onset_lo:.4g}, {onset_hi:.4g}]  upper_rel={upper_rel:.3f}  "
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
    """Usage onset vs the closed-form threshold, with a zoom inset.

    The onset bracket spans under 1% of the full axis, so each panel gets an
    inset zoomed to the threshold neighborhood where the containment claim
    (threshold inside the measured onset bracket) is actually visible.
    Colors are deliberately non-agent: the usage curve is neutral gray, the
    hatched gray band is the measured onset bracket, and vermillion is
    reserved for the theory line.
    """
    figstyle.apply()
    envs = list(curve_df["env"].unique()) if not curve_df.empty else []
    n = max(1, len(envs))
    fig, axes = plt.subplots(
        1, n, figsize=(figstyle.TEXT_WIDTH_IN / 2 * n, 2.9), squeeze=False
    )
    panel = "abcdefgh"
    band_kw = dict(
        facecolor="0.82", alpha=0.6, hatch="/////", edgecolor="0.55", linewidth=0
    )
    for i, name in enumerate(envs):
        ax = axes[0, i]
        sub = curve_df[curve_df["env"] == name].sort_values("w")
        ax.errorbar(
            sub["w"],
            sub["mean_usage"],
            yerr=sub["se_usage"],
            fmt="o-",
            capsize=figstyle.CAPSIZE,
            ms=3.5,
            lw=1.4,
            color="0.4",
            label="$U(w)$",
        )
        w_th = float(sub["w_thresh"].iloc[0])
        ax.axvline(
            w_th,
            color=figstyle.VERMILLION,
            ls="--",
            lw=1.4,
            label=f"$w_{{\\mathrm{{thresh}}}}={w_th:.3g}$",
        )
        jrow = jump_df[jump_df["env"] == name]
        lo = hi = float("nan")
        if not jrow.empty:
            lo = float(jrow["onset_lo"].iloc[0]) if "onset_lo" in jrow.columns else float("nan")
            hi = float(jrow["onset_hi"].iloc[0]) if "onset_hi" in jrow.columns else float("nan")
            if np.isfinite(lo) and np.isfinite(hi) and hi > lo:
                ax.axvspan(lo, hi, label="onset bracket", **band_kw)
            elif np.isfinite(hi):
                ax.axvline(
                    hi, color="0.4", ls=":", label=f"onset $={hi:.3g}$"
                )
        ymax = float(sub["mean_usage"].max())
        ax.set_ylim(bottom=-0.04 * ymax)
        ax.set_xlabel("Info-gain weight $w$ (linear scale)")
        ax.set_ylabel("Mean observations per episode $U(w)$")
        cfg = POSITIVE_THRESH_CONFIGS.get(name)
        if cfg is not None:
            ax.set_title(
                f"({panel[i]}) Testbed, $p{{=}}{cfg['p']:.2f}$, $c{{=}}{cfg['c']:g}$"
            )
        else:
            ax.set_title(f"({panel[i]}) {name}")
        figstyle.style_axis(ax)
        # The curve hugs zero left of the threshold, so upper left is empty.
        # Compact spacing keeps the legend clear of the threshold rule.
        ax.legend(loc="upper left", fontsize=8, handlelength=1.6,
                  handletextpad=0.6, borderaxespad=0.2)
        # Zoom inset on the onset neighborhood: the bracket and the threshold
        # rule are sub-pixel on the full axis.
        if np.isfinite(lo) and np.isfinite(hi) and hi > lo:
            # Upper-middle placement: right of the legend, above the flat
            # pre-onset run, left of the final steep segment in both panels.
            axin = ax.inset_axes([0.40, 0.62, 0.31, 0.33])
            axin.errorbar(
                sub["w"], sub["mean_usage"], yerr=sub["se_usage"],
                fmt="o-", capsize=figstyle.CAPSIZE, ms=3.5, lw=1.2, color="0.4",
            )
            axin.axvline(w_th, color=figstyle.VERMILLION, ls="--", lw=1.2)
            axin.axvspan(lo, hi, **band_kw)
            pad = max(0.1, 0.6 * (hi - lo))
            axin.set_xlim(w_th - pad, hi + pad)
            in_view = sub[(sub["w"] >= w_th - pad) & (sub["w"] <= hi + pad)]
            in_max = float(in_view["mean_usage"].max()) if not in_view.empty else 1.0
            axin.set_ylim(-0.08 * max(in_max, 0.5), 1.25 * max(in_max, 0.5))
            axin.set_xticks([w_th, hi])
            axin.set_xticklabels([f"{w_th:.2f}", f"{hi:.2f}"], fontsize=7)
            axin.tick_params(axis="y", labelsize=7)
            ax.indicate_inset_zoom(axin, edgecolor="0.6", alpha=0.8)
    fig.tight_layout()
    _savefig(fig, path)
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
    reset_window: Optional[int] = None,
    reset_k: float = 3.0,
    variant: str = "decay",
    ref=None,
    verbose: bool = True,
) -> Tuple[pd.DataFrame, DualWeightAgent]:
    np.random.seed(seed)
    env = make_scaled_diagnosis(1.0)
    # Seed the environment stream once; run_otc_episode with no seed then
    # continues this generator deterministically (Gymnasium reset() without
    # a seed does not re-seed np_random).
    env.reset(seed=int(seed))
    agent = DualWeightAgent(
        get_obs_models(env),
        make_env_config(env),
        budget=budget,
        lr=lr,
        lr_decay=lr_decay,
        planning_horizon=3,
        initial_weight=1.0,
        reset_window=reset_window,
        reset_k=reset_k,
    )
    if ref is None:
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
    if verbose:
        print(
            f"\n=== Dual descent Diagnosis ({variant})  B={budget}  lr0={lr}  "
            f"decay={lr_decay}  reset_window={reset_window}  curve w*≈{ref.w_star:.4g} ===",
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
            old_reset_events = list(agent.reset_events)
            old_n = agent._n_updates
            old_sum = agent._w_sum
            old_cooldown = agent._cooldown_remaining
            agent = DualWeightAgent(
                get_obs_models(env),
                make_env_config(env),
                budget=budget,
                lr=lr,
                lr_decay=lr_decay,
                planning_horizon=3,
                initial_weight=cur_w,
                reset_window=reset_window,
                reset_k=reset_k,
            )
            agent.weight_history = old_w_hist
            agent.avg_weight_history = old_avg_hist
            agent.usage_history = old_u_hist
            agent.lr_history = old_lr_hist
            agent.reset_events = old_reset_events
            agent._n_updates = old_n
            agent._w_sum = old_sum
            agent._cooldown_remaining = old_cooldown
            if verbose:
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
                "variant": variant,
                "n_resets": len(agent.reset_events),
            }
        )
        if verbose and (t + 1) % max(1, n_episodes // 10) == 0:
            recent = np.mean([r["usage"] for r in rows[-20:]])
            print(
                f"  t={t+1}/{n_episodes}  w={new_w:.4g}  w_avg={agent.w_avg:.4g}  "
                f"recent_U={recent:.2f}  resets={len(agent.reset_events)}",
                flush=True,
            )
    return pd.DataFrame(rows), agent


def readaptation_episodes(
    df: pd.DataFrame,
    rescale_at: int,
    tol: float = 1.0,
    hold: int = 20,
    roll: int = 20,
) -> Optional[int]:
    """
    Episodes from rescale until rolling usage returns within tol of B and
    stays there for ``hold`` consecutive episodes. None if never recovered.

    The rolling mean is computed strictly from post-rescale episodes
    (``min_periods=roll``), not from the full pre+post series. A window
    that straddles the rescale point would otherwise mix in the converged
    pre-rescale usage and can report a spurious near-zero adaptation time
    even though the post-rescale process has not yet re-converged.
    """
    if df.empty or "usage" not in df.columns:
        return None
    budget = float(df["budget"].iloc[0])
    usages = df["usage"].to_numpy(dtype=float)
    post = usages[rescale_at:]
    if len(post) < roll:
        return None
    smooth = (
        pd.Series(post)
        .rolling(roll, min_periods=roll)
        .mean()
        .to_numpy(dtype=float)
    )
    within = np.abs(smooth - budget) <= tol
    for t in range(0, len(within) - hold + 1):
        if bool(np.all(within[t : t + hold])):
            return int(t)
    return None


def plot_dual_descent(
    df: pd.DataFrame,
    path: Path,
    bracket: Optional[Tuple[float, float]] = None,
) -> None:
    fig, axes = plt.subplots(2, 1, figsize=(7.5, 5.8), sharex=True)
    axes[0].plot(df["episode"], df["weight"], label="w_t", alpha=0.7)
    axes[0].plot(df["episode"], df["w_avg"], label="w_avg", lw=2)
    if bracket is not None and np.isfinite(bracket[0]) and np.isfinite(bracket[1]):
        axes[0].axhspan(
            bracket[0],
            bracket[1],
            color="C2",
            alpha=0.18,
            label=f"crossing [{bracket[0]:.3g},{bracket[1]:.3g}]",
        )
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
    _savefig(fig, path)
    plt.close(fig)


def _diagnosis_crossing_from_scale_csv(budget: float) -> Optional[Tuple[float, float]]:
    """Load α=1 Diagnosis crossing bracket from saved scale curves, if present."""
    path = RESULTS / "results_price_scale_curves.csv"
    if not path.exists():
        return None
    df = pd.read_csv(path)
    sub = df[(df["env"] == "Diagnosis") & (np.isclose(df["scale_k"], 1.0))]
    if sub.empty:
        return None
    br = crossing_bracket(_curve_points_from_df(sub), budget=budget)
    if not br.bracketed:
        return None
    return (br.w_lo, br.w_hi)


def run_dual_reset_comparison(
    n_episodes: int,
    budget: float,
    lr: float,
    lr_decay: float,
    rescale_at: int,
    rescale_factor: float = 10.0,
    seed: int = 42,
    reset_window: int = 20,
    reset_k: float = 3.0,
) -> Tuple[pd.DataFrame, dict]:
    """
    Run decay-only vs reset-on-shift dual controllers on the same protocol.
    """
    df_decay, agent_decay = run_dual_descent(
        n_episodes=n_episodes,
        budget=budget,
        lr=lr,
        lr_decay=lr_decay,
        rescale_at=rescale_at,
        rescale_factor=rescale_factor,
        seed=seed,
        reset_window=None,
        variant="decay",
    )
    df_reset, agent_reset = run_dual_descent(
        n_episodes=n_episodes,
        budget=budget,
        lr=lr,
        lr_decay=lr_decay,
        rescale_at=rescale_at,
        rescale_factor=rescale_factor,
        seed=seed,
        reset_window=reset_window,
        reset_k=reset_k,
        variant="reset",
    )
    combined = pd.concat([df_decay, df_reset], ignore_index=True)
    metrics = {
        "dual_readapt_decay": readaptation_episodes(df_decay, rescale_at),
        "dual_readapt_reset": readaptation_episodes(df_reset, rescale_at),
        "dual_reset_events": list(agent_reset.reset_events),
        "dual_decay_reset_events": list(agent_decay.reset_events),
    }
    print(
        f"\n=== Re-adaptation: decay={metrics['dual_readapt_decay']}  "
        f"reset={metrics['dual_readapt_reset']}  "
        f"reset_events={metrics['dual_reset_events']} ===",
        flush=True,
    )
    return combined, metrics


def plot_dual_reset(
    df: pd.DataFrame,
    path: Path,
    bracket: Optional[Tuple[float, float]] = None,
    reset_events: Optional[Sequence[int]] = None,
) -> None:
    """Two-column comparison: decay-only vs reset-on-shift."""
    fig, axes = plt.subplots(2, 2, figsize=(10.5, 6.0), sharex="col")
    variants = [("decay", "Decay only"), ("reset", "Reset on shift")]
    for col, (variant, title) in enumerate(variants):
        sub = df[df["variant"] == variant].sort_values("episode")
        if sub.empty:
            continue
        ax_w, ax_u = axes[0, col], axes[1, col]
        ax_w.plot(sub["episode"], sub["weight"], label="w_t", alpha=0.75, color="C0")
        ax_w.plot(sub["episode"], sub["w_avg"], label="w_avg", lw=2, color="C1")
        if bracket is not None and np.isfinite(bracket[0]) and np.isfinite(bracket[1]):
            ax_w.axhspan(
                bracket[0],
                bracket[1],
                color="C2",
                alpha=0.15,
                label=f"α=1 bracket",
            )
            ax_w.axhspan(
                10.0 * bracket[0],
                10.0 * bracket[1],
                color="C3",
                alpha=0.12,
                label="×10 bracket",
            )
        if sub["rescaled"].any():
            t0 = int(sub.loc[sub["rescaled"], "episode"].iloc[0])
            ax_w.axvline(t0, color="gray", ls=":", label="rescale")
            ax_u.axvline(t0, color="gray", ls=":")
        if variant == "reset" and reset_events:
            for i, ep in enumerate(reset_events):
                ax_w.axvline(
                    ep,
                    color="C3",
                    ls="--",
                    alpha=0.8,
                    label="lr reset" if i == 0 else None,
                )
                ax_u.axvline(ep, color="C3", ls="--", alpha=0.8)
        ax_w.set_title(title)
        ax_w.set_ylabel("Weight w")
        ax_w.legend(fontsize=7)
        ax_w.grid(True, alpha=0.3)

        window = 20
        smooth = sub["usage"].rolling(window, min_periods=1).mean()
        ax_u.plot(sub["episode"], smooth, label=f"usage (roll-{window})", color="C0")
        ax_u.axhline(sub["budget"].iloc[0], color="C1", ls="--", label="budget B")
        ax_u.set_xlabel("Episode")
        ax_u.set_ylabel("Usage")
        ax_u.legend(fontsize=7)
        ax_u.grid(True, alpha=0.3)
    fig.suptitle("Dual control: lr decay vs reset-on-shift after reward rescale")
    fig.tight_layout()
    _savefig(fig, path)
    plt.close(fig)


# ---------------------------------------------------------------------------
# 4c. Multi-seed dual control (Stage C of the full-paper plan)
# ---------------------------------------------------------------------------

def _mean_ci(values: Sequence[float]) -> Tuple[float, float, float]:
    """Mean and normal-approximation 95% CI half-width; (mean, lo, hi)."""
    arr = np.asarray([v for v in values if v is not None and np.isfinite(v)], dtype=float)
    if arr.size == 0:
        return float("nan"), float("nan"), float("nan")
    m = float(arr.mean())
    if arr.size == 1:
        return m, m, m
    half = 1.96 * float(arr.std(ddof=1)) / math.sqrt(arr.size)
    return m, m - half, m + half


def run_dual_multiseed(
    n_episodes: int,
    budget: float,
    lr: float,
    lr_decay: float,
    rescale_at: int,
    rescale_factor: float,
    controller_seeds: Sequence[int],
    reset_window: int = 20,
    reset_k: float = 3.0,
    steady_window: int = 50,
) -> Tuple[pd.DataFrame, dict]:
    """
    Stage C: sweep controller seeds for decay-only vs reset-on-shift dual
    control. Reports per-seed re-adaptation times and steady-state usage
    error with 95% CIs.
    """
    env = make_scaled_diagnosis(1.0)
    ref_curve = estimate_usage_curve(
        env,
        w_grid=make_log_w_grid(0.0, 50.0, 10),
        seeds=[42],
        num_episodes=30,
        planning_horizon=3,
    )
    ref = solve_shadow_price_from_curve(ref_curve, budget=budget, tol=1.0)

    all_rows: List[pd.DataFrame] = []
    per_seed: List[dict] = []
    for variant, window in (("decay", None), ("reset", reset_window)):
        for s in controller_seeds:
            df, agent = run_dual_descent(
                n_episodes=n_episodes,
                budget=budget,
                lr=lr,
                lr_decay=lr_decay,
                rescale_at=rescale_at,
                rescale_factor=rescale_factor,
                seed=int(s),
                reset_window=window,
                reset_k=reset_k,
                variant=variant,
                ref=ref,
                verbose=False,
            )
            df["controller_seed"] = int(s)
            all_rows.append(df)
            usages = df["usage"].to_numpy(dtype=float)
            pre_err = abs(float(np.mean(usages[rescale_at - steady_window : rescale_at])) - budget)
            post_err = abs(float(np.mean(usages[-steady_window:])) - budget)
            readapt = readaptation_episodes(df, rescale_at)
            per_seed.append(
                {
                    "variant": variant,
                    "controller_seed": int(s),
                    "readapt": readapt,
                    "pre_steady_err": pre_err,
                    "post_steady_err": post_err,
                    "n_resets": len(agent.reset_events),
                }
            )
            print(
                f"  [{variant} seed={s}] readapt={readapt}  "
                f"pre_err={pre_err:.2f}  post_err={post_err:.2f}  "
                f"resets={len(agent.reset_events)}",
                flush=True,
            )
        # Incremental save after each variant completes
        pd.concat(all_rows, ignore_index=True).to_csv(
            RESULTS / "results_price_dual_multiseed.csv", index=False
        )

    combined = pd.concat(all_rows, ignore_index=True)
    seed_df = pd.DataFrame(per_seed)
    metrics: dict = {"dual_ms_n_seeds": len(list(controller_seeds))}
    for variant in ("decay", "reset"):
        sub = seed_df[seed_df["variant"] == variant]
        readapts = sub["readapt"].tolist()
        recovered = [r for r in readapts if r is not None and np.isfinite(r)]
        m, lo, hi = _mean_ci(recovered)
        metrics[f"dual_ms_readapt_{variant}"] = {
            "mean": m,
            "ci_lo": lo,
            "ci_hi": hi,
            "n_recovered": len(recovered),
            "n_total": len(readapts),
        }
        for phase in ("pre", "post"):
            m2, lo2, hi2 = _mean_ci(sub[f"{phase}_steady_err"].tolist())
            metrics[f"dual_ms_{phase}_err_{variant}"] = {
                "mean": m2,
                "ci_lo": lo2,
                "ci_hi": hi2,
            }
    d = metrics["dual_ms_readapt_decay"]
    r = metrics["dual_ms_readapt_reset"]
    metrics["dual_ms_cis_disjoint"] = bool(
        np.isfinite(d["ci_lo"]) and np.isfinite(r["ci_hi"]) and r["ci_hi"] < d["ci_lo"]
    )
    print(
        f"\n=== Multi-seed dual: readapt decay {d['mean']:.1f} "
        f"[{d['ci_lo']:.1f},{d['ci_hi']:.1f}] ({d['n_recovered']}/{d['n_total']} recovered)  "
        f"vs reset {r['mean']:.1f} [{r['ci_lo']:.1f},{r['ci_hi']:.1f}] "
        f"({r['n_recovered']}/{r['n_total']})  disjoint={metrics['dual_ms_cis_disjoint']} ===",
        flush=True,
    )
    seed_df.to_csv(RESULTS / "results_price_dual_multiseed_metrics.csv", index=False)
    return combined, metrics


def plot_dual_multiseed(df: pd.DataFrame, path: Path, roll: int = 20) -> None:
    """Median trajectory with interquartile band per variant.

    One figure-level legend below the panels (nothing inside the data area,
    where a legend swatch at the post-reset plateau height once read as the
    trace continuing left of the rescale rule). All four panels are labeled
    (a)-(d). The rolling usage mean uses a full window (min_periods=roll) so
    no warm-up sliver hugs the y-axis.
    """
    figstyle.apply()
    fig, axes = plt.subplots(
        2, 2, figsize=figstyle.figsize(1.0, 0.65), sharex="col", sharey="row"
    )
    variants = [("decay", "Decay only"), ("reset", "Reset on shift")]
    budget = float(df["budget"].iloc[0])
    n_seeds = int(df["controller_seed"].nunique())
    for col, (variant, title) in enumerate(variants):
        sub = df[df["variant"] == variant]
        if sub.empty:
            continue
        ax_w, ax_u = axes[0, col], axes[1, col]
        w_piv = sub.pivot_table(index="episode", columns="controller_seed", values="weight")
        u_piv = sub.pivot_table(index="episode", columns="controller_seed", values="usage")
        u_roll = u_piv.rolling(roll, min_periods=roll).mean()
        eps = w_piv.index.to_numpy()

        band_kw = dict(
            color=figstyle.BLUE, alpha=0.30, linewidth=0.4, edgecolor=figstyle.BLUE
        )
        ax_w.plot(eps, w_piv.median(axis=1), color=figstyle.BLUE, lw=1.8)
        ax_w.fill_between(
            eps,
            w_piv.quantile(0.25, axis=1),
            w_piv.quantile(0.75, axis=1),
            **band_kw,
        )
        ax_u.plot(eps, u_roll.median(axis=1), color=figstyle.BLUE, lw=1.8)
        ax_u.fill_between(
            eps,
            u_roll.quantile(0.25, axis=1),
            u_roll.quantile(0.75, axis=1),
            **band_kw,
        )
        ax_u.axhline(budget, color=figstyle.VERMILLION, ls="--", lw=1.4)
        if sub["rescaled"].any():
            t0 = int(sub.loc[sub["rescaled"], "episode"].iloc[0])
            ax_w.axvline(t0, color=figstyle.GRAY, ls=":")
            ax_u.axvline(t0, color=figstyle.GRAY, ls=":")
        ax_w.set_title(f"({'ab'[col]}) {title}")
        ax_u.set_title(f"({'cd'[col]}) {title}, usage")
        figstyle.style_axis(ax_w)
        figstyle.style_axis(ax_u)
        ax_u.set_xlim(left=0)
        if col == 0:
            ax_w.set_ylabel("Weight $w$")
            ax_u.set_ylabel(
                f"Sensing actions per episode\n(rolling mean, {roll} ep)"
            )
        ax_u.set_xlabel("Episode")
    legend_handles = [
        Line2D([], [], color=figstyle.BLUE, lw=1.8,
               label=f"median ({n_seeds} seeds)"),
        mpl_patches.Patch(facecolor=figstyle.BLUE, alpha=0.30,
                          edgecolor=figstyle.BLUE, linewidth=0.4, label="IQR"),
        Line2D([], [], color=figstyle.VERMILLION, ls="--", lw=1.4,
               label=f"budget $B={budget:g}$"),
        Line2D([], [], color=figstyle.GRAY, ls=":", lw=1.4, label="rescale"),
    ]
    fig.legend(
        handles=legend_handles, loc="upper center", ncol=4,
        bbox_to_anchor=(0.5, 0.02), frameon=False,
    )
    fig.tight_layout()
    _savefig(fig, path)
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
# Figure-only replot (no simulation)
# ---------------------------------------------------------------------------

def replot_all_figures() -> None:
    """Rebuild all six committed price figures from the results CSVs only.

    Reads exactly the CSVs the full battery wrote; runs no episodes. This is
    the single producer's replot path — the full-battery path reaches the
    same plotting functions with freshly computed frames.
    """
    figstyle.apply()

    price_df = pd.read_csv(RESULTS / "results_price_shadow_curves.csv")
    plot_shadow_price_curves(price_df, FIGURES / "price_shadow_curves.png")
    print("  price_shadow_curves: rebuilt from results_price_shadow_curves.csv", flush=True)

    iprice_df = pd.read_csv(RESULTS / "results_price_interleaved_prices.csv")
    plot_shadow_price_curves(iprice_df, FIGURES / "price_staircase_interleaved.png")
    print(
        "  price_staircase_interleaved: rebuilt from results_price_interleaved_prices.csv",
        flush=True,
    )

    scale_curves = pd.read_csv(RESULTS / "results_price_scale_curves.csv")
    scale_cross = pd.read_csv(RESULTS / "results_price_scale_invariance.csv")
    env = "Diagnosis" if "Diagnosis" in scale_curves["env"].unique() else str(
        scale_curves["env"].iloc[0]
    )
    sub_cross = scale_cross[scale_cross["env"] == env]
    budget = float(sub_cross["budget"].iloc[0])
    plot_scale_collapse(
        scale_curves[scale_curves["env"] == env],
        sub_cross,
        FIGURES / "price_scale_invariance.png",
        budget=budget,
    )
    print(
        "  price_scale_invariance: rebuilt from results_price_scale_curves.csv "
        "+ results_price_scale_invariance.csv",
        flush=True,
    )

    cost_curves = pd.read_csv(RESULTS / "results_price_cost_curves.csv")
    cost_prices_path = RESULTS / "results_price_cost_prices.csv"
    cost_prices = pd.read_csv(cost_prices_path) if cost_prices_path.exists() else None
    plot_cost_budget(cost_curves, FIGURES / "price_cost_budget.png", price_df=cost_prices)
    print(
        "  price_cost_budget: rebuilt from results_price_cost_curves.csv "
        "+ results_price_cost_prices.csv",
        flush=True,
    )

    ms_df = pd.read_csv(RESULTS / "results_price_dual_multiseed.csv")
    plot_dual_multiseed(ms_df, FIGURES / "price_dual_multiseed.png")
    print(
        "  price_dual_multiseed: rebuilt from results_price_dual_multiseed.csv",
        flush=True,
    )

    pcurve_df = pd.read_csv(RESULTS / "results_price_prop2_curves.csv")
    jump_df = pd.read_csv(RESULTS / "results_price_prop2_jumps.csv")
    plot_prop2_jumps(pcurve_df, jump_df, FIGURES / "price_prop2_jumps.png")
    print(
        "  price_prop2_jumps: rebuilt from results_price_prop2_curves.csv "
        "+ results_price_prop2_jumps.csv",
        flush=True,
    )


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def staircase_verdict(curve_df: pd.DataFrame, tol: float = 1e-9) -> str:
    """Derive the shadow-staircase verdict from the saved usage curves.

    A usage curve is nondecreasing when ``mean_usage`` never drops by more
    than ``tol`` between consecutive grid weights. The verdict is recomputed
    from ``results_price_usage_curves.csv`` on every run because the summary
    JSON merges prior verdict keys forward, and from 2026-08 to 2026-09-05 it
    carried a fossil string saying Tiger and Diagnosis were non-monotone while
    the CSV and Section 6.6 of the manuscript said the opposite.
    """
    monotone: List[str] = []
    wobbly: List[str] = []
    for env, g in curve_df.groupby("env", sort=False):
        u = g.sort_values("w")["mean_usage"].to_numpy(dtype=float)
        target = monotone if bool(np.all(np.diff(u) >= -tol)) else wobbly
        target.append(str(env))
    if not wobbly:
        return (
            "HOLD: every usage curve nondecreasing at every sampled grid point; "
            "brackets with SEs reported"
        )
    return (
        f"PARTIAL: {', '.join(monotone) or 'none'} nondecreasing at every sampled "
        f"grid point; {', '.join(wobbly)} locally non-monotone from discrete policy "
        "switches (count-usage gap, Proposition PI-2 scope note); brackets with SEs "
        "reported, not singleton prices"
    )


def refresh_summary_verdicts() -> Dict[str, str]:
    """Recompute the summary verdicts that derive from saved CSVs alone.

    Runs no episodes and touches no CSV. Used by ``--refresh-summary`` and at
    the end of every ``main()`` run.
    """
    summary_path = RESULTS / "results_price_of_information_summary.json"
    summary: Dict = {}
    if summary_path.exists():
        with open(summary_path) as f:
            summary = json.load(f)
    verdict = dict(summary.get("verdict", {}))
    curve_path = RESULTS / "results_price_usage_curves.csv"
    if curve_path.exists():
        verdict["shadow_staircases"] = staircase_verdict(pd.read_csv(curve_path))
    summary["verdict"] = verdict
    with open(summary_path, "w") as f:
        json.dump(summary, f, indent=2)
    print(json.dumps(verdict, indent=2), flush=True)
    return verdict


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
        help="Subset: curves interleaved cost scale prop2 dual dual-reset dual-multiseed efe",
    )
    p.add_argument(
        "--replot",
        action="store_true",
        help="Reuse saved CSVs for scale/dual (no re-simulation); prop2 still re-runs",
    )
    p.add_argument(
        "--replot-figures",
        action="store_true",
        help="Rebuild all six committed figures from the results CSVs only "
        "(no episodes run at all), then exit",
    )
    p.add_argument(
        "--refresh-summary",
        action="store_true",
        help="Recompute the summary JSON verdicts that derive from saved CSVs "
        "(no episodes run, no CSV touched), then exit",
    )
    args = p.parse_args()
    # Guard against a silent artifact overwrite. ``--replot`` re-plots only the
    # stages whose saved CSV exists and SIMULATES every other stage in whatever
    # mode is set, and the default mode is ``quick`` (3 seeds, 40 episodes).
    # Run that way it overwrote seven canonical 5-seed CSVs on 2026-09-04
    # (caught before commit, restored from HEAD). Figure-only rebuilds are
    # ``--replot-figures``; a genuine partial replot must say ``--mode full``.
    if args.replot and not args.replot_figures and args.mode != "full":
        p.error(
            "--replot without --mode full would overwrite canonical results CSVs "
            "with quick-mode data. Use --replot-figures to rebuild figures only, "
            "or add --mode full."
        )
    return args


def main() -> None:
    args = parse_args()
    _ensure_dirs()
    if args.replot_figures:
        replot_all_figures()
        return
    if args.refresh_summary:
        refresh_summary_verdicts()
        return
    only = set(args.only) if args.only else {
        "curves", "interleaved", "cost", "scale", "prop2",
        "dual", "dual-reset", "dual-multiseed", "efe",
    }

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
        scale_envs = ["Diagnosis", "Bandit", "Tiger", "Tileworld-6x6"]
        scale_budget = 8.0
        # Budgets sized to each env's usage range (Tiger B_EFE 4.2, Tileworld 14.8)
        scale_budgets = {"Diagnosis": 8.0, "Bandit": 8.0, "Tiger": 4.0, "Tileworld-6x6": 15.0}
        scale_episodes_by_env = {"Tileworld-6x6": 30}
        scale_grid_by_env = {"Tileworld-6x6": 10}
        dual_budget = 8.0
        dual_lr0 = 0.05
        dual_decay = 0.02
        interleaved_envs = ["RS[5,3]", "RS[7,4]", "Inspection-N16"]
        interleaved_ep = 50
        interleaved_grid = 10
        interleaved_episodes_by_env = {"RS[7,4]": 30}
        interleaved_grid_by_env = {"RS[7,4]": 8}
        dual_ms_seeds = 10
        cost_ep = 100
        cost_grid = 12
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
        scale_budgets = {"Diagnosis": 8.0}
        scale_episodes_by_env = {}
        scale_grid_by_env = {}
        dual_budget = 8.0
        dual_lr0 = 0.05
        dual_decay = 0.02
        interleaved_envs = ["RS[5,3]", "Inspection-N16"]
        interleaved_ep = 10
        interleaved_grid = 6
        interleaved_episodes_by_env = {}
        interleaved_grid_by_env = {}
        dual_ms_seeds = 3
        cost_ep = 30
        cost_grid = 8

    summary: dict = {
        "mode": args.mode,
        "seeds": list(seeds),
        "episodes": ep,
        "replot": bool(args.replot),
    }

    # Preserve existing summary fields when running a subset (replot or not).
    summary_path = RESULTS / "results_price_of_information_summary.json"
    if summary_path.exists():
        try:
            with open(summary_path) as f:
                prior = json.load(f)
            for k, v in prior.items():
                if k not in summary:
                    summary[k] = v
        except (json.JSONDecodeError, OSError):
            pass

    if "curves" in only:
        if args.replot and (RESULTS / "results_price_shadow_curves.csv").exists():
            price_df = pd.read_csv(RESULTS / "results_price_shadow_curves.csv")
            plot_shadow_price_curves(price_df, FIGURES / "price_shadow_curves.png")
            summary["curves_rows"] = len(price_df)
        else:
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

    if "interleaved" in only:
        saved = RESULTS / "results_price_interleaved_prices.csv"
        if args.replot and saved.exists():
            iprice_df = pd.read_csv(saved)
            plot_shadow_price_curves(
                iprice_df, FIGURES / "price_staircase_interleaved.png"
            )
            summary["interleaved_rows"] = len(iprice_df)
        else:
            icurve_df, iprice_df = run_interleaved_curves(
                interleaved_envs,
                seeds,
                interleaved_ep,
                n_grid=interleaved_grid,
                n_budgets=4,
                episodes_by_env=interleaved_episodes_by_env,
                grid_by_env=interleaved_grid_by_env,
            )
            if not iprice_df.empty:
                plot_shadow_price_curves(
                    iprice_df, FIGURES / "price_staircase_interleaved.png"
                )
            summary["interleaved_rows"] = len(iprice_df)
            summary["interleaved_curve_rows"] = len(icurve_df)
            summary["interleaved_envs"] = list(interleaved_envs)

    if "cost" in only:
        saved = RESULTS / "results_price_cost_curves.csv"
        saved_prices = RESULTS / "results_price_cost_prices.csv"
        if args.replot and saved.exists():
            cost_curve_df = pd.read_csv(saved)
            cost_price_df = pd.read_csv(saved_prices) if saved_prices.exists() else None
            plot_cost_budget(
                cost_curve_df, FIGURES / "price_cost_budget.png", price_df=cost_price_df
            )
        else:
            cost_curve_df, cost_price_df, cost_metrics = run_cost_budget(
                seeds,
                cost_ep,
                n_grid=cost_grid,
                n_budgets=2,
            )
            cost_price_df.to_csv(RESULTS / "results_price_cost_prices.csv", index=False)
            plot_cost_budget(
                cost_curve_df, FIGURES / "price_cost_budget.png", price_df=cost_price_df
            )
            summary.update(cost_metrics)
            summary["cost_rows"] = len(cost_price_df)

    if "scale" in only:
        existing = None
        saved = RESULTS / "results_price_scale_curves.csv"
        if args.replot and saved.exists():
            existing = pd.read_csv(saved)
            # When replotting, cover every env present in the CSV.
            scale_envs = list(existing["env"].unique())
        all_curve = []
        all_cross = []
        all_collapse = []
        for env_kind in scale_envs:
            out = run_scale_collapse(
                scales=[0.1, 1.0, 10.0],
                seeds=seeds,
                num_episodes=int(scale_episodes_by_env.get(env_kind, ep)),
                n_grid=int(scale_grid_by_env.get(env_kind, max(10, n_grid - 2))),
                budget=float(scale_budgets.get(env_kind, scale_budget)),
                env_kind=env_kind,
                existing_curve_df=existing,
            )
            c_df, x_df, col_df = out
            all_curve.append(c_df)
            all_cross.append(x_df)
            all_collapse.append(col_df)
        curve_df = pd.concat(all_curve, ignore_index=True) if all_curve else pd.DataFrame()
        cross_df = pd.concat(all_cross, ignore_index=True) if all_cross else pd.DataFrame()
        collapse_df = pd.concat(all_collapse, ignore_index=True) if all_collapse else pd.DataFrame()
        # Plot Diagnosis (preferred) or first available env.
        plot_env = "Diagnosis" if "Diagnosis" in curve_df.get("env", pd.Series(dtype=str)).unique() else (
            scale_envs[0] if scale_envs else None
        )
        if plot_env is not None:
            plot_scale_collapse(
                curve_df[curve_df["env"] == plot_env],
                cross_df[cross_df["env"] == plot_env],
                FIGURES / "price_scale_invariance.png",
                budget=scale_budget,
            )
        curve_df.to_csv(RESULTS / "results_price_scale_curves.csv", index=False)
        cross_df.to_csv(RESULTS / "results_price_scale_invariance.csv", index=False)
        collapse_df.to_csv(RESULTS / "results_price_scale_collapse.csv", index=False)
        if not collapse_df.empty:
            summary["collapse_frac_within_noise"] = float(collapse_df["within_noise"].mean())
            summary["collapse_max_spread"] = float(collapse_df["usage_spread"].max())
        # Bracket coincidence: max |edge difference| across scales, per env.
        if not cross_df.empty and "w_lo_over_alpha" in cross_df.columns:
            coinc = {}
            for env, sub in cross_df.groupby("env"):
                lo_spread = float(sub["w_lo_over_alpha"].max() - sub["w_lo_over_alpha"].min())
                hi_spread = float(sub["w_hi_over_alpha"].max() - sub["w_hi_over_alpha"].min())
                coinc[env] = {
                    "lo_spread": lo_spread,
                    "hi_spread": hi_spread,
                    "coincide": lo_spread <= 1e-9 and hi_spread <= 1e-9,
                }
            summary["bracket_coincidence"] = coinc
            summary["brackets_coincide"] = all(v["coincide"] for v in coinc.values())
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
        if not jump_df.empty and "onset_hi" in jump_df.columns:
            summary["prop2_onset_brackets"] = {
                str(r["env"]): {
                    "w_thresh": float(r["w_thresh"]),
                    "onset_lo": float(r["onset_lo"]),
                    "onset_hi": float(r["onset_hi"]),
                    "upper_rel": float(r["rel_err"]),
                }
                for _, r in jump_df.iterrows()
            }
        summary["prop2_rows"] = len(jump_df)

    if "dual" in only:
        dual_csv = RESULTS / "results_price_dual_descent.csv"
        if args.replot and dual_csv.exists():
            df = pd.read_csv(dual_csv)
            print("\n=== Dual descent (replot from saved CSV) ===", flush=True)
        else:
            df, _agent = run_dual_descent(
                n_episodes=dual_episodes,
                budget=dual_budget,
                lr=dual_lr0,
                lr_decay=dual_decay,
                rescale_at=dual_episodes // 2,
                rescale_factor=10.0,
            )
            df.to_csv(dual_csv, index=False)
        bracket = _diagnosis_crossing_from_scale_csv(dual_budget)
        plot_dual_descent(df, FIGURES / "price_dual_descent.png", bracket=bracket)
        # Windowed averages of raw w near the end of each half (Polyak avg is
        # contaminated by the whole-run history after a mid-run rescale).
        pre = df.loc[~df["rescaled"], "weight"]
        post = df.loc[df["rescaled"], "weight"]
        if len(pre) and len(post):
            pre_w = float(pre.iloc[-min(20, len(pre)) :].mean())
            post_w = float(post.iloc[-min(20, len(post)) :].mean())
            ratio = post_w / pre_w if pre_w > 1e-9 else float("nan")
            summary["dual_w_ratio_post_pre"] = ratio
            summary["dual_pre_w"] = pre_w
            summary["dual_post_w"] = post_w
            summary["dual_pre_usage"] = float(df.loc[~df["rescaled"], "usage"].tail(20).mean())
            summary["dual_post_usage"] = float(df.loc[df["rescaled"], "usage"].tail(20).mean())
        if bracket is not None:
            summary["dual_crossing_bracket"] = {"w_lo": bracket[0], "w_hi": bracket[1]}
        summary["dual_rows"] = len(df)

    if "dual-reset" in only:
        reset_csv = RESULTS / "results_price_dual_reset.csv"
        rescale_at = dual_episodes // 2
        if args.replot and reset_csv.exists():
            combined = pd.read_csv(reset_csv)
            print("\n=== Dual reset comparison (replot from saved CSV) ===", flush=True)
            metrics = {
                "dual_readapt_decay": readaptation_episodes(
                    combined[combined["variant"] == "decay"], rescale_at
                ),
                "dual_readapt_reset": readaptation_episodes(
                    combined[combined["variant"] == "reset"], rescale_at
                ),
                "dual_reset_events": [],
            }
            # Recover reset markers from lr jumps if present
            reset_sub = combined[combined["variant"] == "reset"].sort_values("episode")
            if not reset_sub.empty and "lr" in reset_sub.columns:
                lrs = reset_sub["lr"].to_numpy()
                eps = reset_sub["episode"].to_numpy()
                events = []
                for i in range(1, len(lrs)):
                    if lrs[i] > lrs[i - 1] + 1e-12 and abs(lrs[i] - dual_lr0) < 1e-9:
                        events.append(int(eps[i]))
                metrics["dual_reset_events"] = events
        else:
            combined, metrics = run_dual_reset_comparison(
                n_episodes=dual_episodes,
                budget=dual_budget,
                lr=dual_lr0,
                lr_decay=dual_decay,
                rescale_at=rescale_at,
                rescale_factor=10.0,
                seed=42,
                reset_window=20,
                reset_k=3.0,
            )
            combined.to_csv(reset_csv, index=False)
        bracket = _diagnosis_crossing_from_scale_csv(dual_budget)
        plot_dual_reset(
            combined,
            FIGURES / "price_dual_reset.png",
            bracket=bracket,
            reset_events=metrics.get("dual_reset_events"),
        )
        summary["dual_readapt_decay"] = metrics["dual_readapt_decay"]
        summary["dual_readapt_reset"] = metrics["dual_readapt_reset"]
        summary["dual_reset_events"] = metrics["dual_reset_events"]
        summary["dual_reset_rows"] = len(combined)

    if "dual-multiseed" in only:
        ms_csv = RESULTS / "results_price_dual_multiseed.csv"
        rescale_at = dual_episodes // 2
        if args.replot and ms_csv.exists():
            ms_df = pd.read_csv(ms_csv)
            print("\n=== Multi-seed dual (replot from saved CSV) ===", flush=True)
            ms_metrics = {}
        else:
            controller_seeds = list(range(101, 101 + dual_ms_seeds))
            ms_df, ms_metrics = run_dual_multiseed(
                n_episodes=dual_episodes,
                budget=dual_budget,
                lr=dual_lr0,
                lr_decay=dual_decay,
                rescale_at=rescale_at,
                rescale_factor=10.0,
                controller_seeds=controller_seeds,
                reset_window=20,
                reset_k=3.0,
            )
        plot_dual_multiseed(ms_df, FIGURES / "price_dual_multiseed.png")
        summary.update(ms_metrics)
        summary["dual_multiseed_rows"] = len(ms_df)

    if "efe" in only and not args.replot:
        df = run_implicit_efe_budget(env_names, seeds, ep)
        df.to_csv(RESULTS / "results_price_efe_implicit_budget.csv", index=False)
        summary["efe_rows"] = len(df)

    # Refresh headline verdicts when the relevant protocols ran.
    if "scale" in only or "prop2" in only or "dual" in only or "dual-reset" in only:
        verdict = {}
        if "collapse_frac_within_noise" in summary:
            coinc = summary.get("brackets_coincide", False)
            verdict["curve_collapse"] = (
                f"HOLD — {100*summary['collapse_frac_within_noise']:.0f}% of matched "
                f"w/α points within 2·SE; max spread ≤{summary.get('collapse_max_spread', float('nan')):.2f}; "
                f"crossing brackets {'coincide' if coinc else 'differ'} across α"
            )
        if "prop2_jump_ok" in summary:
            brackets = summary.get("prop2_onset_brackets", {})
            rels = {k: v.get("upper_rel") for k, v in brackets.items()} if brackets else {}
            verdict["prop2_jump"] = (
                f"{'HOLD' if summary['prop2_jump_ok'] else 'FAIL'} — onset brackets "
                f"{rels}; U=0 below closed-form threshold"
            )
        if "dual_w_ratio_post_pre" in summary:
            readapt_note = ""
            if summary.get("dual_readapt_decay") is not None and summary.get("dual_readapt_reset") is not None:
                readapt_note = (
                    f"; re-adaptation {summary['dual_readapt_decay']}→"
                    f"{summary['dual_readapt_reset']} episodes with lr reset-on-shift"
                )
            elif summary.get("dual_readapt_decay") is not None:
                readapt_note = f"; re-adaptation ~{summary['dual_readapt_decay']} episodes under lr decay"
            else:
                readapt_note = "; ~150-episode re-adaptation transient under lr decay"
            verdict["dual_rescale"] = (
                f"HOLD — usage pinned near B; windowed w ratio post/pre "
                f"≈{summary['dual_w_ratio_post_pre']:.2f} after ×10 reward rescale"
                f"{readapt_note}"
            )
        if verdict:
            summary["verdict"] = {**summary.get("verdict", {}), **verdict}

    # The staircase verdict derives from a saved CSV alone, so it is refreshed
    # on every run rather than merged forward from the prior summary.
    curve_path = RESULTS / "results_price_usage_curves.csv"
    if curve_path.exists():
        summary["verdict"] = {
            **summary.get("verdict", {}),
            "shadow_staircases": staircase_verdict(pd.read_csv(curve_path)),
        }

    with open(RESULTS / "results_price_of_information_summary.json", "w") as f:
        json.dump(summary, f, indent=2)
    print("\nDone.", json.dumps(summary, indent=2), flush=True)


if __name__ == "__main__":
    main()
