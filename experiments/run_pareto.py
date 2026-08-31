#!/usr/bin/env python3
"""
Pareto frontier experiment: sweep Planning+IG weight w across environments.

Demonstrates that EFE (= Planning+IG at w=1 by Proposition 1) sits near the
Pareto knee of the success-vs-reward tradeoff, providing a principled
canonical weight derived from the variational bound rather than per-environment
grid search.
"""

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from typing import Dict, List
import os

from rho_aif import figstyle
from rho_aif.environments.info_seeking import InfoSeekingEnv
from rho_aif.environments.tiger import TigerEnv
from rho_aif.environments.diagnosis import DiagnosisEnv
from rho_aif.environments.bandit import BanditEnv
from rho_aif.environments.tileworld import TileworldEnv
from rho_aif.agents.planning_infogain import PlanningInfoGainAgent
from rho_aif.agents.efe import EFEAgent
from run_experiment import (
    make_agent, run_experiment, run_experiment_multi_seed, summarize_results,
    provenance_fields, SEEDS,
)


def run_pareto_sweep(
    env,
    horizon: int,
    weights: List[float] = None,
    num_episodes: int = 500,
    seeds: List[int] = None,
) -> Dict:
    """Sweep Planning+IG weight w, also run EFE for reference."""
    if weights is None:
        weights = [0.01, 0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 20.0, 50.0, 100.0, 200.0]
    if seeds is None:
        seeds = SEEDS

    sweep = {"w": [], "success": [], "reward": [], "obs": [],
             "se_reward_seed_level": [], "se_success_seed_level": [], "n_seeds": []}
    for w in weights:
        raw = run_experiment_multi_seed(PlanningInfoGainAgent, env, num_episodes,
                                        seeds=seeds,
                                        planning_horizon=horizon, info_gain_weight=w)
        s = summarize_results(raw)
        sweep["w"].append(w)
        sweep["success"].append(s["success_rate"])
        sweep["reward"].append(s["mean_reward"])
        sweep["obs"].append(s["mean_observations"])
        sweep["se_reward_seed_level"].append(s.get("se_reward_seed_level", float("nan")))
        sweep["se_success_seed_level"].append(s.get("se_success_seed_level", float("nan")))
        sweep["n_seeds"].append(s.get("n_seeds", float("nan")))
        print(f"    w={w:>6.2f}  success={s['success_rate']:.1%}  reward={s['mean_reward']:+.2f}"
              f"  (seed SE {s.get('se_reward_seed_level', float('nan')):.3f})")

    efe_raw = run_experiment_multi_seed(EFEAgent, env, num_episodes, seeds=seeds,
                                        planning_horizon=horizon)
    efe_s = summarize_results(efe_raw)
    efe = {"success": efe_s["success_rate"], "reward": efe_s["mean_reward"],
           "obs": efe_s["mean_observations"]}
    print(f"    EFE     success={efe['success']:.1%}  reward={efe['reward']:+.2f}")

    return {"sweep": sweep, "efe": efe}


# Weights whose points get an in-panel annotation. Where consecutive weights
# are exactly reward-and-success tied (the paper's bracket convention), the
# whole tied bracket is labeled once, e.g. "w=0.01-20".
ANNOTATED_WEIGHTS = {0.01, 1.0, 10.0, 100.0}
# Caption-named points beyond the default subset (fig:pareto names w=20 as
# Pareto-dominating w=1 on Tileworld).
CAPTION_WEIGHTS = {"Tileworld": {20.0}}
# The bracket containing w=1 sits under the large diamond+star markers, so
# its label needs a longer manual leader. Offsets are in points, chosen per
# environment to point into empty plot area; the fallback works for any
# environment added later.
W1_LABEL_OFFSETS = {
    "Tiger": (30, 8, "left"),
    "Testbed": (-26, -16, "right"),
    "Diagnosis": (-30, 6, "right"),
    "Bandit": (-20, 12, "right"),
    "Tileworld": (-16, -16, "right"),
}
# Targeted nudges for non-w=1 labels that would otherwise sit on the sweep
# polyline or on a point's seed-level error bar, keyed by (env, first weight
# of the tied bracket). Each offset points into empty plot area; the
# Tileworld bracket leader departs away from the w=1 diamond so the two
# leaders do not converge on the same neighborhood.
MANUAL_LABEL_OFFSETS = {
    ("Tiger", 50.0): (-8, 9, "right"),
    ("Testbed", 0.01): (10, 10, "left"),
    ("Diagnosis", 0.01): (8, -14, "left"),
    ("Bandit", 0.01): (8, -14, "left"),
    ("Tileworld", 0.01): (0, 18, "left"),
    ("Tileworld", 10.0): (8, -10, "left"),
}


def _tied_weight_groups(ws, succ, rew, rtol=1e-9):
    """Group consecutive sweep points that are exactly tied on both axes."""
    groups = []
    for i, w in enumerate(ws):
        if groups and np.isclose(succ[i], groups[-1]["succ"], rtol=rtol) \
                and np.isclose(rew[i], groups[-1]["rew"], rtol=rtol):
            groups[-1]["ws"].append(w)
        else:
            groups.append({"ws": [w], "succ": succ[i], "rew": rew[i]})
    return groups


def plot_pareto(all_results: Dict, save_path: str = "figures/fig_pareto.pdf"):
    """Pareto frontier panels: success vs reward for each environment.

    Layout is a 2x3 grid (five environment panels plus the legend in the
    empty sixth cell). Styling comes from rho_aif.figstyle: the sweep series
    is Planning+IG (pink, dotted), the w=1 diamond is Planning+IG's marker
    for the canonical weight, and the EFE agent is the vermillion star. The
    two markers coincide by Proposition 1, so the star is drawn smaller on
    top of the diamond.
    """
    figstyle.apply()
    envs = list(all_results.keys())
    n = len(envs)
    if n >= 5:
        nrows, ncols = 2, 3
        fig, axes = plt.subplots(nrows, ncols, figsize=(9.6, 5.4))
        axes = axes.ravel()
    else:
        nrows, ncols = 1, n
        fig, axes = plt.subplots(1, n, figsize=(3.2 * n, 3.5))
        axes = np.atleast_1d(axes)

    panel_labels = ["(a)", "(b)", "(c)", "(d)", "(e)", "(f)"]
    pig = figstyle.agent_style("Planning+IG")

    for idx, (env_name, ax) in enumerate(zip(envs, axes)):
        data = all_results[env_name]
        sw = data["sweep"]
        efe = data["efe"]

        succ = [s * 100 for s in sw["success"]]
        rew = list(sw["reward"])
        ws = list(sw["w"])

        # w-ordered sweep polyline, kept light so markers and labels dominate.
        ax.plot(succ, rew, color=pig["color"], linestyle=pig["linestyle"],
                lw=1.4, alpha=0.5, zorder=1)
        # Seed-level SE on both axes, from the committed sweep CSV, so the
        # frontier is read against its sampling uncertainty rather than as
        # exactly resolved.
        ax.errorbar(succ, rew,
                    xerr=[se * 100 for se in sw["se_success_seed_level"]],
                    yerr=sw["se_reward_seed_level"],
                    fmt="none", ecolor=pig["color"], elinewidth=0.8,
                    capsize=figstyle.CAPSIZE, alpha=0.6, zorder=1)
        ax.scatter(succ, rew, c=pig["color"], s=32, zorder=2,
                   edgecolors="white", linewidths=0.6)

        # Planning+IG at w=1 (diamond) and the EFE agent (star). They
        # coincide by Proposition 1, so draw the star smaller on top.
        w1_idx = next((i for i, w in enumerate(ws) if abs(w - 1.0) < 0.01), None)
        if w1_idx is not None:
            ax.scatter([succ[w1_idx]], [rew[w1_idx]], c=pig["color"], s=170,
                       marker="D", zorder=4, edgecolors="black", linewidths=1.0)
        ax.scatter([efe["success"] * 100], [efe["reward"]],
                   c=figstyle.AGENT_COLORS["EFE"], s=120,
                   marker="*", zorder=5, edgecolors="black", linewidths=0.7)

        # Per-panel limits fitted to the data, with headroom for labels.
        lo_x, hi_x = min(succ), max(succ)
        lo_y = min(rew + [efe["reward"]])
        hi_y = max(rew + [efe["reward"]])
        xr = (hi_x - lo_x) or 1.0
        # Floor the fitted x-span at 2pp so a degenerate success range (all
        # points within sampling error of each other, as on Tiger) is not
        # magnified to full panel width. Pad downward, since success caps
        # at 100%.
        if xr < 2.0:
            lo_x = hi_x - 2.0
            xr = 2.0
        yr = (hi_y - lo_y) or 1.0
        ax.set_xlim(lo_x - 0.22 * xr, hi_x + 0.22 * xr)
        ax.set_ylim(lo_y - 0.14 * yr, hi_y + 0.16 * yr)

        # Annotate the labeled weight subset plus caption-named points. Tied
        # brackets get one label spanning the bracket (e.g. "w=0.01-20").
        wanted = ANNOTATED_WEIGHTS | CAPTION_WEIGHTS.get(env_name, set())
        points = []
        x_mid = lo_x + 0.55 * xr
        for g in _tied_weight_groups(ws, succ, rew):
            if not wanted & set(g["ws"]):
                continue
            if len(g["ws"]) > 1:
                label = f"$w$={g['ws'][0]:g}–{g['ws'][-1]:g}"
            else:
                label = f"$w$={g['ws'][0]:g}"
            manual = None
            if 1.0 in g["ws"]:
                # This point carries the diamond and star markers. Label it
                # with a longer leader into empty area so nothing occludes.
                manual = W1_LABEL_OFFSETS.get(env_name, (-24, -14, "right"))
            elif (env_name, g["ws"][0]) in MANUAL_LABEL_OFFSETS:
                manual = MANUAL_LABEL_OFFSETS[(env_name, g["ws"][0])]
            if manual is not None:
                dx, dy, ha = manual
                # The w=1 leader stops short of the large diamond+star
                # markers (shrinkB=10); other manual leaders touch their
                # small dot (shrinkB=3) so the target is unambiguous.
                shrink_b = 10 if 1.0 in g["ws"] else 3
                ax.annotate(label, xy=(g["succ"], g["rew"]),
                            xytext=(dx, dy), textcoords="offset points",
                            fontsize=7.5, color=figstyle.GRAY,
                            ha=ha, va="center",
                            arrowprops=dict(arrowstyle="-", lw=0.5,
                                            color=figstyle.GRAY,
                                            shrinkA=2, shrinkB=shrink_b))
                continue
            side = -1 if g["succ"] > x_mid else 1
            points.append((g["succ"], g["rew"], label, side))
        figstyle.annotate_no_overlap(ax, points)

        ax.set_xlabel("Success rate (%)")
        if idx % ncols == 0:
            ax.set_ylabel("Mean reward")
        ax.set_title(f"{panel_labels[idx]} {env_name}")
        figstyle.style_axis(ax)

    from matplotlib.lines import Line2D
    legend_elements = [
        Line2D([0], [0], color=pig["color"], linestyle=pig["linestyle"],
               lw=1.4, alpha=0.7, marker="o", markersize=4.5,
               label="Planning+IG (sweep over $w$)"),
        Line2D([0], [0], color=pig["color"], marker="D", markersize=9,
               ls="none", markeredgecolor="black",
               label="Planning+IG $w{=}1$"),
        Line2D([0], [0], color=figstyle.AGENT_COLORS["EFE"], marker="*",
               markersize=12, ls="none", markeredgecolor="black",
               label="EFE agent ($w{=}1$)"),
    ]
    # Legend below the panels, matching fig_tileworld_scaling and
    # fig_asymmetry_sweep, rather than parked inside an empty grid cell.
    if n >= 5 and len(axes) > n:
        for extra_ax in axes[n:]:
            extra_ax.axis("off")
    fig.legend(handles=legend_elements, loc="lower center", ncol=3,
               bbox_to_anchor=(0.5, -0.05))
    plt.tight_layout()

    base, _ = os.path.splitext(save_path)
    plt.savefig(base + ".pdf")
    plt.savefig(base + ".png")
    plt.close()
    print(f"  Saved {base}.pdf and {base}.png")


def load_pareto_results(
    sweep_csv: str = "results/results_pareto_sweep.csv",
    wstar_csv: str = "results/results_pareto_wstar.csv",
) -> Dict:
    """Reconstruct plot_pareto's input from the committed sweep CSVs.

    Reads the sweep points from results_pareto_sweep.csv and the EFE
    reference point from results_pareto_wstar.csv (columns efe_reward and
    efe_success), so the figure can be rebuilt without re-running episodes.
    """
    import pandas as pd
    sweep_df = pd.read_csv(sweep_csv)
    wstar_df = pd.read_csv(wstar_csv).set_index("env")
    all_results = {}
    for env_name in sweep_df["env"].drop_duplicates():
        g = sweep_df[sweep_df["env"] == env_name].sort_values("w")
        all_results[env_name] = {
            "sweep": {
                "w": g["w"].tolist(),
                "success": g["success"].tolist(),
                "reward": g["reward"].tolist(),
                "obs": g["obs"].tolist(),
                "se_reward_seed_level": g["se_reward_seed_level"].tolist(),
                "se_success_seed_level": g["se_success_seed_level"].tolist(),
            },
            "efe": {
                "success": float(wstar_df.loc[env_name, "efe_success"]),
                "reward": float(wstar_df.loc[env_name, "efe_reward"]),
            },
        }
    return all_results


def run_accuracy_sensitivity(
    accuracies: List[float] = None,
    num_episodes: int = 500,
    seeds: List[int] = None,
    save_path: str = "figures/fig_accuracy_sensitivity.pdf",
):
    """Sweep observation accuracy and check w=1 knee persistence."""
    if accuracies is None:
        accuracies = [0.55, 0.60, 0.65, 0.70, 0.75, 0.80, 0.85]
    if seeds is None:
        seeds = SEEDS

    env_configs = {
        "Tiger": lambda acc: TigerEnv(listen_accuracy=acc, listen_cost=1.0,
                                       correct_reward=10.0, incorrect_penalty=-100.0),
        "Diagnosis": lambda acc: DiagnosisEnv(num_conditions=4, test_accuracy=acc, test_cost=1.0,
                                               correct_reward=10.0, incorrect_penalty=-50.0),
    }

    horizons = {"Tiger": 6, "Diagnosis": 3}
    weights = [0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 50.0]

    results = {}
    for env_name, make_env in env_configs.items():
        horizon = horizons[env_name]
        results[env_name] = {"accuracy": [], "w1_reward": [], "best_w": [], "best_reward": []}

        for acc in accuracies:
            env = make_env(acc)
            print(f"  {env_name} accuracy={acc:.2f}...")

            best_w_score = -float("inf")
            best_w = 1.0
            w1_reward = None

            for w in weights:
                raw = run_experiment_multi_seed(PlanningInfoGainAgent, env, num_episodes,
                                                seeds=seeds,
                                                planning_horizon=horizon, info_gain_weight=w)
                s = summarize_results(raw)
                if abs(w - 1.0) < 0.01:
                    w1_reward = s["mean_reward"]
                if s["mean_reward"] > best_w_score:
                    best_w_score = s["mean_reward"]
                    best_w = w

            results[env_name]["accuracy"].append(acc)
            results[env_name]["w1_reward"].append(w1_reward)
            results[env_name]["best_w"].append(best_w)
            results[env_name]["best_reward"].append(best_w_score)
            print(f"    w=1 reward={w1_reward:+.2f}  best_w={best_w}  best_reward={best_w_score:+.2f}")

    # Shared figure style: EFE's canonical vermillion for the w=1 series and
    # Planning+IG's pink for the tuned-weight series (both series are
    # PlanningInfoGainAgent, matching fig_pareto's vocabulary). Authored at
    # the printed width so rcParams point sizes are the on-page sizes.
    figstyle.apply()
    efe_style = figstyle.agent_style("EFE")
    pig_style = figstyle.agent_style("Planning+IG")

    fig, axes = plt.subplots(1, 2, figsize=figstyle.figsize(1.0, 0.4))
    panel_labels = ["(a)", "(b)"]
    for idx, (env_name, data) in enumerate(results.items()):
        ax = axes[idx]
        ax.plot(data["accuracy"], data["w1_reward"],
                label="$w{=}1$ (EFE)", **efe_style)
        ax.plot(data["accuracy"], data["best_reward"],
                label="Best $w$ (tuned)", **pig_style)
        ax.set_xlabel("Observation accuracy")
        if idx == 0:
            ax.set_ylabel("Mean reward")
        ax.set_title(f"{panel_labels[idx]} {env_name}")
        ax.legend()
        figstyle.style_axis(ax)

    plt.tight_layout()
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    base, _ = os.path.splitext(save_path)
    plt.savefig(base + ".pdf")
    plt.savefig(base + ".png")
    plt.close()
    print(f"  Saved {base}.pdf and {base}.png")
    return results


if __name__ == "__main__":
    os.makedirs("figures", exist_ok=True)

    envs_config = {
        "Tiger": (
            TigerEnv(listen_accuracy=0.85, listen_cost=1.0,
                     correct_reward=10.0, incorrect_penalty=-100.0),
            6
        ),
        "Testbed": (
            InfoSeekingEnv(observation_accuracy=0.75, observation_cost=0.1,
                           correct_reward=1.0, incorrect_penalty=-1.0),
            4
        ),
        "Diagnosis": (
            DiagnosisEnv(num_conditions=4, test_accuracy=0.80, test_cost=1.0,
                         correct_reward=10.0, incorrect_penalty=-50.0),
            3
        ),
        "Bandit": (
            BanditEnv(num_arms=4, inspect_accuracy=0.80, inspect_cost=0.5,
                      correct_reward=10.0, small_reward=1.0),
            2
        ),
        "Tileworld": (
            TileworldEnv(grid_size=6),
            2
        ),
    }

    import sys
    cmd = sys.argv[1] if len(sys.argv) > 1 else "pareto"

    if cmd == "figure":
        # Replot mode: rebuild figures/fig_pareto.{pdf,png} from the
        # committed CSVs without re-running any episodes.
        all_results = load_pareto_results()
        plot_pareto(all_results)
        print("\nPareto figure rebuilt from results/results_pareto_sweep.csv")

    if cmd in ("pareto", "all"):
        all_results = {}
        for env_name, (env, horizon) in envs_config.items():
            print(f"\n{'=' * 60}")
            print(f"Pareto sweep: {env_name} (H={horizon})")
            print("=" * 60)
            all_results[env_name] = run_pareto_sweep(env, horizon, num_episodes=500)

        plot_pareto(all_results)
        print("\nPareto figure saved to figures/fig_pareto.pdf")

        # Persist the full sweep plus each environment's reward-maximizing
        # weight w*_ret and its seed-level SE, so Table tab:alpha_eta's
        # w*_ret column is traceable to a committed, regenerable CSV instead
        # of being an undocumented literal (Stage-K statistical audit finding).
        import pandas as pd
        sweep_rows = []
        summary_rows = []
        for env_name, data in all_results.items():
            sw = data["sweep"]
            for i, w in enumerate(sw["w"]):
                sweep_rows.append({
                    "env": env_name, "w": w, "success": sw["success"][i],
                    "reward": sw["reward"][i], "obs": sw["obs"][i],
                    "se_reward_seed_level": sw["se_reward_seed_level"][i],
                    "se_success_seed_level": sw["se_success_seed_level"][i],
                    "n_seeds": sw["n_seeds"][i],
                })
            best_idx = int(np.argmax(sw["reward"]))
            summary_rows.append({
                "env": env_name,
                "w_star_ret": sw["w"][best_idx],
                "reward_at_w_star_ret": sw["reward"][best_idx],
                "se_reward_seed_level_at_w_star_ret": sw["se_reward_seed_level"][best_idx],
                "success_at_w_star_ret": sw["success"][best_idx],
                "efe_reward": data["efe"]["reward"],
                "efe_success": data["efe"]["success"],
            })
        sweep_df = pd.DataFrame(sweep_rows)
        summary_df = pd.DataFrame(summary_rows)
        for df in (sweep_df, summary_df):
            prov = provenance_fields(SEEDS, 500)
            for k, v in prov.items():
                df[k] = v
        sweep_df.to_csv("results/results_pareto_sweep.csv", index=False)
        summary_df.to_csv("results/results_pareto_wstar.csv", index=False)
        print("\nSaved results/results_pareto_sweep.csv and results/results_pareto_wstar.csv")
        print(summary_df.to_string(index=False))

    if cmd in ("accuracy", "all"):
        print(f"\n{'=' * 60}")
        print("ACCURACY SENSITIVITY SWEEP")
        print("=" * 60)
        run_accuracy_sensitivity()
