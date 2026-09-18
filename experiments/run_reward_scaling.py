#!/usr/bin/env python3
"""
Reward-rescaling invariance experiment.

Demonstrates the reviewers' scale objection: if all rewards and costs are
multiplied by k, the agent maximizing E[k R] + w I matches the original
policy for weight w' = k w. Hence w*_ret(k) ≈ k * w*_ret(1). Equivalently,
keeping w fixed while scaling rewards by k is indistinguishable from
rescaling the weight by 1/k. Thus w=1 is not scale-invariant.

Sweeps k in {0.1, 1, 10} on Diagnosis and Bandit, and for each scale sweeps
Planning+IG weights to find w*_ret.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Callable, Dict, List

_REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_REPO))
sys.path.insert(0, str(_REPO / "experiments"))

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.lines import Line2D

from rho_aif import figstyle
from rho_aif.agents.planning_infogain import PlanningInfoGainAgent
from rho_aif.environments.bandit import BanditEnv
from rho_aif.environments.diagnosis import DiagnosisEnv
from run_experiment import SEEDS, provenance_fields, run_experiment_multi_seed, summarize_results


def make_diagnosis(k: float) -> DiagnosisEnv:
    return DiagnosisEnv(
        num_conditions=4,
        test_accuracy=0.80,
        correct_reward=10.0 * k,
        incorrect_penalty=-50.0 * k,
        test_cost=1.0 * k,
    )


def make_bandit(k: float) -> BanditEnv:
    return BanditEnv(
        num_arms=4,
        inspect_accuracy=0.80,
        correct_reward=10.0 * k,
        small_reward=1.0 * k,
        inspect_cost=0.5 * k,
    )


ENV_SPECS = {
    "Diagnosis": {"make": make_diagnosis, "horizon": 3},
    "Bandit": {"make": make_bandit, "horizon": 2},
}


def sweep_weights(
    make_env: Callable[[float], object],
    horizon: int,
    k: float,
    weights: List[float],
    num_episodes: int,
    seeds: List[int],
) -> List[dict]:
    env = make_env(k)
    rows = []
    for w in weights:
        raw = run_experiment_multi_seed(
            PlanningInfoGainAgent,
            env,
            num_episodes,
            seeds=seeds,
            planning_horizon=horizon,
            info_gain_weight=w,
        )
        s = summarize_results(raw)
        row = {
            "scale_k": k,
            "w": w,
            "success": s["success_rate"],
            "reward": s["mean_reward"],
            "obs": s["mean_observations"],
        }
        row.update(provenance_fields(seeds, num_episodes))
        rows.append(row)
        print(
            f"    k={k:g} w={w:>7g}  success={s['success_rate']:.1%}  "
            f"reward={s['mean_reward']:+.3f}",
            flush=True,
        )
    return rows


def best_w_ret(rows: List[dict]) -> float:
    return float(max(rows, key=lambda r: r["reward"])["w"])


def plot_scaling(df: pd.DataFrame, out_path: Path) -> None:
    """One panel per environment, plotting scale-normalised reward/k so the
    three reward scales share one visible curve family (scale equivariance
    made literal). The open circle marks each curve's reward-maximizing
    weight w*_ret (the argmax is unchanged by the positive rescaling), and
    the dashed vertical rule sits at w=1 (the EFE weight). One figure-level
    legend covers all panels. No SE band is drawn: the committed CSV carries
    only per-(k, w) means, so seed-level uncertainty would require a rerun.
    """
    figstyle.apply()
    envs = sorted(df["environment"].unique())
    panel_letters = "abcdefgh"
    fig, axes = plt.subplots(1, len(envs), figsize=figstyle.figsize(1.0, 0.45),
                             squeeze=False)
    curve_handles: Dict[str, object] = {}
    for panel_i, (ax, env_name) in enumerate(zip(axes[0], envs)):
        sub = df[df["environment"] == env_name]
        # Each reward scale gets its own line style and marker as well as a
        # colour, so the three curves stay distinguishable in grayscale.
        scale_styles = [("-", "o"), ("--", "s"), ("-.", "^"), (":", "D")]
        for (k, grp), color, (ls, mk) in zip(sub.groupby("scale_k"), figstyle.ENV_CYCLE, scale_styles):
            grp = grp.sort_values("w")
            (line,) = ax.plot(grp["w"], grp["reward"] / k, marker=mk, linestyle=ls,
                              color=color, markersize=4)
            curve_handles.setdefault(f"$k={k:g}$", line)
            star_idx = grp["reward"].idxmax()
            w_star = grp.loc[star_idx, "w"]
            r_star = grp.loc[star_idx, "reward"] / k
            ax.scatter([w_star], [r_star], marker="o", s=90, zorder=5,
                       facecolors="none", edgecolors=color, linewidths=1.4)
        ax.axvline(1.0, color=figstyle.GRAY, ls="--", lw=0.8, alpha=0.7,
                   zorder=1)
        ax.set_xscale("log")
        figstyle.style_axis(ax)
        ax.set_xlabel("Planning+IG weight $w$")
        if panel_i == 0:
            ax.set_ylabel("Mean reward / $k$")
        ax.set_title(f"({panel_letters[panel_i]}) {env_name}")
    proxy_handles = [
        Line2D([], [], marker="o", markerfacecolor="none",
               markeredgecolor="0.3", markeredgewidth=1.4, markersize=7,
               linestyle="none", label=r"$w^*_{\mathrm{ret}}$"),
        Line2D([], [], linestyle="--", color=figstyle.GRAY, lw=0.8,
               label=r"$w{=}1$ (EFE)"),
    ]
    handles = list(curve_handles.values()) + proxy_handles
    labels = list(curve_handles.keys()) + [h.get_label() for h in proxy_handles]
    fig.legend(handles, labels, loc="upper center",
               bbox_to_anchor=(0.5, 1.04), ncol=5, frameon=False)
    fig.tight_layout(rect=[0, 0, 1, 0.93])
    out_path.parent.mkdir(parents=True, exist_ok=True)
    fig.savefig(out_path)
    fig.savefig(out_path.with_suffix(".png"))
    plt.close(fig)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--episodes", type=int, default=200)
    parser.add_argument("--seeds", type=int, default=3)
    parser.add_argument(
        "--scales",
        type=float,
        nargs="+",
        default=[0.1, 1.0, 10.0],
    )
    parser.add_argument(
        "--weights",
        type=float,
        nargs="+",
        default=[0.01, 0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 20.0, 50.0, 100.0],
    )
    parser.add_argument("--output", type=Path, default=Path("results/results_reward_scaling.csv"))
    parser.add_argument(
        "--figure", type=Path, default=Path("figures/fig_reward_scaling.pdf")
    )
    parser.add_argument(
        "--replot", action="store_true",
        help="Rebuild the figure from the committed CSVs without re-running "
             "any episodes.")
    args = parser.parse_args()

    if args.replot:
        df = pd.read_csv(args.output)
        summary_path = args.output.with_name("results_reward_scaling_summary.csv")
        sdf = pd.read_csv(summary_path)
        # Cross-check: the starred argmax the figure draws must agree with the
        # committed summary's w_ret for every (environment, k) cell.
        for _, srow in sdf.iterrows():
            grp = df[(df["environment"] == srow["environment"])
                     & (df["scale_k"] == srow["scale_k"])]
            w_star = float(grp.loc[grp["reward"].idxmax(), "w"])
            if abs(w_star - float(srow["w_ret"])) > 1e-9:
                raise SystemExit(
                    f"Summary/detail mismatch for {srow['environment']} "
                    f"k={srow['scale_k']}: detail argmax {w_star} vs summary "
                    f"w_ret {srow['w_ret']}")
        plot_scaling(df, args.figure)
        print(f"Replotted {args.figure} (and .png twin) from {args.output} "
              f"and {summary_path}")
        return

    seeds = SEEDS[: args.seeds]
    all_rows = []
    summary = []

    for env_name, spec in ENV_SPECS.items():
        print(f"=== {env_name} ===", flush=True)
        w_by_k: Dict[float, float] = {}
        for k in args.scales:
            rows = sweep_weights(
                spec["make"],
                spec["horizon"],
                k,
                args.weights,
                args.episodes,
                seeds,
            )
            for r in rows:
                r["environment"] = env_name
            all_rows.extend(rows)
            w_star = best_w_ret(rows)
            w_by_k[k] = w_star
            summary.append(
                {
                    "environment": env_name,
                    "scale_k": k,
                    "w_ret": w_star,
                    "w_ret_times_k": w_star * k,
                }
            )
            print(f"  -> w*_ret(k={k:g}) = {w_star}", flush=True)

    df = pd.DataFrame(all_rows)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(args.output, index=False)
    summary_path = args.output.with_name("results_reward_scaling_summary.csv")
    pd.DataFrame(summary).to_csv(summary_path, index=False)
    plot_scaling(df, args.figure)

    print("\nSummary (w*_ret / k should be roughly constant if scale-covariant):")
    sdf = pd.DataFrame(summary)
    if "w_ret" in sdf.columns:
        sdf["w_ret_over_k"] = sdf["w_ret"] / sdf["scale_k"]
    print(sdf.to_string(index=False))
    print(f"Wrote {args.output}, {summary_path}, {args.figure}")


if __name__ == "__main__":
    main()
