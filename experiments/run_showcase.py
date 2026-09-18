#!/usr/bin/env python3
"""
Showcase experiments: reward asymmetry sweep, EFE decomposition trajectories,
and observation-action scaling.

Produces publication-quality figures that visualize the core dynamics of
EFE-as-rho: automatic adaptation to reward structure and the intrinsic
explore-exploit transition.

Provenance: the two sweeps persist their data to
``results/results_showcase_asymmetry.csv`` and
``results/results_showcase_obs_scaling.csv`` (this script is the single
producer of both), and the figures can be regenerated from those committed
CSVs without re-running the batteries::

    python experiments/run_showcase.py            # full battery: run + CSVs + figures
    python experiments/run_showcase.py --replot   # figures only, from committed CSVs

The trajectory figure (fig_efe_trajectory) is a seeded demo-episode trace
with no numeric table claim behind it; it is deterministic and cheap, so it
is re-traced in both modes rather than persisted.

Protocol: 5 canonical seeds {42, 123, 456, 789, 1024} x 100 episodes per
seed = 500 episodes per sweep point (matching the 500-episodes-per-point
protocol the figures have always used, now with explicit per-episode
seeding via env.reset(seed=...) instead of an unseeded episode stream).
"""

import argparse
import os

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib.lines import Line2D
from matplotlib.ticker import MaxNLocator
from scipy.stats import entropy as scipy_entropy
from dataclasses import dataclass
from typing import List, Dict, Tuple

from rho_aif import figstyle
from rho_aif.environments.tiger import TigerEnv
from rho_aif.environments.diagnosis import DiagnosisEnv
from rho_aif.agents.myopic import MyopicAgent
from rho_aif.agents.planning import PlanningAgent
from rho_aif.agents.info_gain import InformationGainAgent
from rho_aif.agents.planning_infogain import PlanningInfoGainAgent
from rho_aif.agents.efe import EFEAgent
from run_experiment import (
    SEEDS,
    make_agent,
    provenance_fields,
    run_experiment_multi_seed,
    summarize_results,
    tune_info_gain_weight,
)

ASYMMETRY_CSV = "results/results_showcase_asymmetry.csv"
OBS_SCALING_CSV = "results/results_showcase_obs_scaling.csv"

# 5 canonical seeds x 100 episodes = 500 episodes per sweep point, the
# episode count both sweeps have always used per point.
EPISODES_PER_SEED = 100


# ---------------------------------------------------------------------------
# Experiment 1: Reward asymmetry sweep on Tiger
# ---------------------------------------------------------------------------

def run_reward_asymmetry_sweep(
    penalties: List[float] = None,
    episodes_per_seed: int = EPISODES_PER_SEED,
    horizon: int = 6,
    seeds: List[int] = None,
    csv_path: str = ASYMMETRY_CSV,
) -> Dict:
    """Sweep Tiger penalty from mild to extreme, measuring each agent's
    response, and persist the sweep to ``csv_path``."""

    if penalties is None:
        penalties = [1, 2, 5, 10, 20, 50, 100, 200, 500]
    if seeds is None:
        seeds = SEEDS

    results = {name: {"penalties": [], "success": [], "reward": [], "obs": [],
                      "se_success": [], "se_reward": []}
               for name in ["Myopic", "Planning", "InfoGain-Tuned", "Planning+IG", "EFE"]}
    rows = []

    for pen in penalties:
        env = TigerEnv(
            listen_accuracy=0.85,
            listen_cost=1.0,
            correct_reward=10.0,
            incorrect_penalty=-float(pen),
        )
        print(f"  Penalty = -{pen}")

        # NOTE: this weight is tuned on the myopic InformationGainAgent (on
        # the dedicated TUNING_SEED stream) and reused for Planning+IG, the
        # protocol this figure has always used. The main-table baselines tune
        # Planning+IG on its own class per the tuner's contract.
        best_w = tune_info_gain_weight(env, tune_episodes=100)

        configs = [
            ("Myopic", MyopicAgent, {}),
            ("Planning", PlanningAgent, {"planning_horizon": horizon}),
            ("InfoGain-Tuned", InformationGainAgent, {"info_gain_weight": best_w}),
            ("Planning+IG", PlanningInfoGainAgent,
             {"planning_horizon": horizon, "info_gain_weight": best_w}),
            ("EFE", EFEAgent, {"planning_horizon": horizon}),
        ]

        for name, cls, kwargs in configs:
            raw = run_experiment_multi_seed(cls, env, episodes_per_seed,
                                            seeds=seeds, **kwargs)
            s = summarize_results(raw)
            results[name]["penalties"].append(pen)
            results[name]["success"].append(s["success_rate"])
            results[name]["reward"].append(s["mean_reward"])
            results[name]["obs"].append(s["mean_observations"])
            results[name]["se_success"].append(s["se_success_seed_level"])
            results[name]["se_reward"].append(s["se_reward_seed_level"])

            row = {
                "penalty": pen,
                "agent": name,
                "success_rate": s["success_rate"],
                "se_success_seed_level": s["se_success_seed_level"],
                "mean_reward": s["mean_reward"],
                "se_reward_seed_level": s["se_reward_seed_level"],
                "mean_observations": s["mean_observations"],
                "planning_horizon": kwargs.get("planning_horizon", float("nan")),
                "info_gain_weight": kwargs.get("info_gain_weight", float("nan")),
                "n_seeds": s["n_seeds"],
            }
            row.update(provenance_fields(seeds, episodes_per_seed))
            rows.append(row)

    os.makedirs(os.path.dirname(csv_path), exist_ok=True)
    pd.DataFrame(rows).to_csv(csv_path, index=False)
    print(f"  Saved {csv_path}")

    return results


# ---------------------------------------------------------------------------
# Experiment 2: EFE decomposition trajectories
# ---------------------------------------------------------------------------

@dataclass
class StepTrace:
    step: int
    belief_entropy: float
    info_gain: float
    best_commit_efe: float
    best_observe_efe: float
    action_taken: int
    action_type: str


def trace_efe_episode(env, agent, max_steps: int = 30, seed=None) -> Tuple[List[StepTrace], bool, float]:
    """Run one episode recording EFE components at each decision point."""
    obs, info = env.reset(seed=seed)
    agent.reset()
    traces = []
    total_reward = 0.0

    for step in range(max_steps):
        belief = agent.belief.belief.copy()
        b_entropy = float(scipy_entropy(belief, base=2))

        _, commit_g = agent._best_commit_efe(belief)

        best_obs_g = float("inf")
        best_ig = 0.0
        for k in range(agent.num_observe_actions):
            model = agent.obs_models[k]
            prior_h = scipy_entropy(belief, base=2)
            post_h = 0.0
            for oi in range(model.shape[1]):
                p_o = float(np.dot(belief, model[:, oi]))
                if p_o < 1e-10:
                    continue
                posterior = model[:, oi] * belief
                posterior = posterior / posterior.sum()
                post_h += p_o * scipy_entropy(posterior, base=2)
            ig = prior_h - post_h
            g, _ = agent._efe_observe(k, belief, 0)
            if g < best_obs_g:
                best_obs_g = g
                best_ig = ig

        action = agent.select_action()
        is_commit = action >= agent.num_observe_actions

        traces.append(StepTrace(
            step=step,
            belief_entropy=b_entropy,
            info_gain=best_ig,
            best_commit_efe=float(commit_g),
            best_observe_efe=float(best_obs_g),
            action_taken=action,
            action_type="commit" if is_commit else "observe",
        ))

        obs, reward, terminated, truncated, info = env.step(action)
        total_reward += reward

        if terminated or truncated:
            return traces, info.get("correct", False), total_reward

        agent.update_belief(obs, obs_action=action)

    return traces, False, total_reward


def collect_trajectories(
    env, agent, n_episodes: int = 20, max_steps: int = 30, seed: int = 42
) -> List[Tuple[List[StepTrace], bool, float]]:
    """Collect multiple traced episodes."""
    all_traces = []
    for ep_i in range(n_episodes):
        traces, success, reward = trace_efe_episode(env, agent, max_steps, seed=seed * 10000 + ep_i)
        all_traces.append((traces, success, reward))
    return all_traces


# ---------------------------------------------------------------------------
# Experiment 3: Observation action complexity scaling
# ---------------------------------------------------------------------------

def run_obs_action_scaling(
    n_states: int = 8,
    episodes_per_seed: int = EPISODES_PER_SEED,
    horizon: int = 3,
    seeds: List[int] = None,
    csv_path: str = OBS_SCALING_CSV,
) -> Dict:
    """Vary K (number of tests) while holding N fixed, and persist the sweep
    to ``csv_path``."""

    if seeds is None:
        seeds = SEEDS

    results = {name: {"K": [], "success": [], "reward": [], "obs": [],
                      "se_success": [], "se_reward": []}
               for name in ["Myopic", "Planning", "Planning+IG", "EFE"]}
    rows = []

    for k in [1, 2, 3]:
        env = DiagnosisEnv(
            num_conditions=n_states,
            num_tests=k,
            test_accuracy=0.80,
            test_cost=1.0,
            correct_reward=10.0,
            incorrect_penalty=-50.0,
        )
        print(f"  K = {k} tests (N = {n_states})")

        # Same weight-transfer note as the asymmetry sweep applies here.
        best_w = tune_info_gain_weight(env, tune_episodes=100)

        configs = [
            ("Myopic", MyopicAgent, {}),
            ("Planning", PlanningAgent, {"planning_horizon": horizon}),
            ("Planning+IG", PlanningInfoGainAgent,
             {"planning_horizon": horizon, "info_gain_weight": best_w}),
            ("EFE", EFEAgent, {"planning_horizon": horizon}),
        ]

        for name, cls, kwargs in configs:
            raw = run_experiment_multi_seed(cls, env, episodes_per_seed,
                                            seeds=seeds, **kwargs)
            s = summarize_results(raw)
            results[name]["K"].append(k)
            results[name]["success"].append(s["success_rate"])
            results[name]["reward"].append(s["mean_reward"])
            results[name]["obs"].append(s["mean_observations"])
            results[name]["se_success"].append(s["se_success_seed_level"])
            results[name]["se_reward"].append(s["se_reward_seed_level"])

            row = {
                "num_tests_K": k,
                "num_conditions_N": n_states,
                "agent": name,
                "success_rate": s["success_rate"],
                "se_success_seed_level": s["se_success_seed_level"],
                "mean_reward": s["mean_reward"],
                "se_reward_seed_level": s["se_reward_seed_level"],
                "mean_observations": s["mean_observations"],
                "planning_horizon": kwargs.get("planning_horizon", float("nan")),
                "info_gain_weight": kwargs.get("info_gain_weight", float("nan")),
                "n_seeds": s["n_seeds"],
            }
            row.update(provenance_fields(seeds, episodes_per_seed))
            rows.append(row)

    os.makedirs(os.path.dirname(csv_path), exist_ok=True)
    pd.DataFrame(rows).to_csv(csv_path, index=False)
    print(f"  Saved {csv_path}")

    return results


# ---------------------------------------------------------------------------
# Replot path: rebuild the sweep dicts from the committed CSVs
# ---------------------------------------------------------------------------

def load_asymmetry_from_csv(csv_path: str = ASYMMETRY_CSV) -> Dict:
    df = pd.read_csv(csv_path)
    results = {}
    for name, g in df.groupby("agent", sort=False):
        g = g.sort_values("penalty")
        results[name] = {
            "penalties": g["penalty"].tolist(),
            "success": g["success_rate"].tolist(),
            "reward": g["mean_reward"].tolist(),
            "obs": g["mean_observations"].tolist(),
            "se_success": g["se_success_seed_level"].tolist(),
            "se_reward": g["se_reward_seed_level"].tolist(),
        }
    return results


def load_obs_scaling_from_csv(csv_path: str = OBS_SCALING_CSV) -> Dict:
    df = pd.read_csv(csv_path)
    results = {}
    for name, g in df.groupby("agent", sort=False):
        g = g.sort_values("num_tests_K")
        results[name] = {
            "K": g["num_tests_K"].tolist(),
            "success": g["success_rate"].tolist(),
            "reward": g["mean_reward"].tolist(),
            "obs": g["mean_observations"].tolist(),
            "se_success": g["se_success_seed_level"].tolist(),
            "se_reward": g["se_reward_seed_level"].tolist(),
        }
    return results


# ---------------------------------------------------------------------------
# Figure generation
# ---------------------------------------------------------------------------

def _plot_agent_series(ax, x, y, yerr, name, label=True):
    """One agent series in the shared style, with seed-level error bars."""
    style = figstyle.agent_style(name)
    ax.errorbar(x, y, yerr=yerr, label=name if label else None,
                capsize=figstyle.CAPSIZE, elinewidth=0.8, **style)


def plot_reward_asymmetry_sweep(results: Dict, save_path: str = "figures/fig_asymmetry_sweep.pdf"):
    """Three-panel figure: success rate, reward, and a reward zoom detail.

    Panel (b)'s range is set by Myopic's collapse to about -75, which
    crushes the other four series into a narrow band near the top. An
    overlapping inset zoom, even with its connector lines suppressed, still
    read as messy: cramming a second full set of axes into a quarter of
    panel (b) left no room for x-tick labels at all and only two sparse
    y-ticks, and the four dodged series tangled together in the small box.
    Replaced with a third, full-size panel (c) dedicated to the zoom, with
    its own complete tick labels, plus a shaded band on panel (b) at the
    same y-range (c) magnifies, the same locator device used for fig:prop2.
    """
    figstyle.apply()
    fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=figstyle.figsize(1.0, 0.37))

    order = ["Myopic", "Planning", "InfoGain-Tuned", "Planning+IG", "EFE"]
    # Several series are exactly tied at many penalties (e.g. Planning and
    # EFE, InfoGain-Tuned and Planning+IG), so dodge each series on the log
    # x-axis by a small multiplicative factor to keep coincident markers and
    # error bars side by side rather than stacked.
    dodge = {name: f for name, f in zip(order, [0.82, 0.90, 1.0, 1.11, 1.22])}
    zoom_lo, zoom_hi = 3.4, 7.9
    penalties = None
    for name in order:
        if name not in results:
            continue
        d = results[name]
        penalties = d["penalties"]
        x = [p * dodge[name] for p in d["penalties"]]
        se_s = [s * 100 for s in d.get("se_success", [0] * len(d["penalties"]))]
        _plot_agent_series(ax1, x, [s * 100 for s in d["success"]], se_s, name)
        _plot_agent_series(ax2, x, d["reward"], d.get("se_reward"), name)
        if name != "Myopic":
            _plot_agent_series(ax3, x, d["reward"], d.get("se_reward"), name,
                               label=False)

    from matplotlib.ticker import FixedLocator, NullFormatter
    # Nine labeled ticks (1, 2, 5, ..., 500) on a panel about two inches
    # wide ran into each other at print size ("100200" touched). Label the
    # decades plus the sweep's endpoint and keep every other swept penalty
    # as an unlabeled minor tick, so each sampled position stays marked on
    # the axis without the labels colliding.
    major = [p for p in penalties if p in (1, 10, 100, 500)]
    minor = [p for p in penalties if p not in major]
    for ax in (ax1, ax2, ax3):
        ax.set_xscale("log")
        ax.set_xlabel("Penalty magnitude $\\left|R^{-}\\right|$")
        ax.set_xticks(major)
        ax.set_xticklabels([f"{p:g}" for p in major])
        ax.xaxis.set_minor_locator(FixedLocator(minor))
        ax.xaxis.set_minor_formatter(NullFormatter())
        figstyle.style_axis(ax)

    ax1.set_ylabel("Success rate (%)")
    ax1.set_title("(a) Success rate vs. reward asymmetry")
    ax2.set_ylabel("Mean reward")
    ax2.set_title("(b) Reward vs. reward asymmetry")
    ax3.set_ylabel("Mean reward")
    ax3.set_title("(c) Reward, zoom near the top")
    ax3.set_ylim(zoom_lo, zoom_hi)

    # Shaded band on panel (b) marks exactly the y-range panel (c)
    # magnifies, replacing indicate_inset_zoom's connector lines (which ran
    # diagonally across real data at a similar gray tone and read as extra
    # trend lines rather than a zoom pointer).
    ax2.axhspan(zoom_lo, zoom_hi, color=figstyle.GRAY, alpha=0.15, zorder=0)

    handles, labels = ax1.get_legend_handles_labels()
    fig.legend(handles, labels, loc="lower center", ncol=5,
               bbox_to_anchor=(0.5, -0.08))

    fig.tight_layout()
    fig.savefig(save_path)
    fig.savefig(save_path.replace(".pdf", ".png"))
    plt.close(fig)
    print(f"  Saved {save_path} (+ .png)")


def plot_efe_trajectories(all_traces, save_path: str = "figures/fig_efe_trajectory.pdf"):
    """Plot EFE decomposition for representative episodes."""
    figstyle.apply()
    successful = [(t, s, r) for t, s, r in all_traces if s and len(t) >= 3]
    if not successful:
        successful = all_traces[:3]

    # One representative per distinct episode length, so the three panels
    # genuinely show three different episodes (index-based selection from a
    # length-sorted list once picked the same shortest-length trace twice).
    by_len = {}
    for item in sorted(successful, key=lambda x: len(x[0])):
        by_len.setdefault(len(item[0]), item)
    lengths = sorted(by_len)
    if len(lengths) < 3:
        raise RuntimeError(
            "fig_efe_trajectory needs episodes of three distinct lengths, "
            f"got lengths {lengths}")
    chosen_lengths = [lengths[0], lengths[len(lengths) // 2], lengths[-1]]
    assert len(set(chosen_lengths)) == 3
    selected = [by_len[n] for n in chosen_lengths]

    fig, axes = plt.subplots(1, 3, figsize=figstyle.figsize(1.0, 0.35),
                             sharey=True)
    titles = [f"({letter}) {n}-step episode"
              for letter, n in zip("abc", chosen_lengths)]

    commit_color = figstyle.VERMILLION
    observe_color = figstyle.BLUE
    entropy_color = figstyle.GREEN

    for ax_idx, (ax, title) in enumerate(zip(axes, titles)):
        traces, success, reward = selected[ax_idx]
        steps = [t.step for t in traces]
        commit_vals = [-t.best_commit_efe for t in traces]
        observe_vals = [-t.best_observe_efe for t in traces]
        entropies = [t.belief_entropy for t in traces]

        # Distinct markers on the two solid series keep them apart in
        # grayscale, where their colours land at similar gray levels.
        ax.plot(steps, commit_vals, color=commit_color, lw=1.8, marker="o", markersize=3.5)
        ax.plot(steps, observe_vals, color=observe_color, lw=1.8, marker="s", markersize=3.2)

        ax_twin = ax.twinx()
        ax_twin.fill_between(steps, entropies, alpha=0.12, color=entropy_color)
        ax_twin.plot(steps, entropies, color=entropy_color, lw=1.4, ls="--")
        ax_twin.set_ylim([0, 1.25])
        ax_twin.grid(False)
        ax_twin.spines["top"].set_visible(False)
        # The entropy axis is shown on every panel, in the entropy series'
        # green, so the dashed curve is never read against the left scale.
        ax_twin.tick_params(axis="y", colors=entropy_color, labelsize=7.5)
        ax_twin.spines["right"].set_color(entropy_color)
        if ax_idx == 2:
            ax_twin.set_ylabel("Belief entropy (bits)", color=entropy_color)

        commit_step = None
        for t in traces:
            if t.action_type == "commit":
                commit_step = t.step
                break
        if commit_step is not None:
            ax.axvline(commit_step, color=figstyle.GRAY, ls=":", lw=1, alpha=0.8)
            y0, y1 = ax.get_ylim()
            # Mid-height, just left of the line: the curves occupy the top
            # and bottom of the panel, so mid-height is reliably empty.
            ax.annotate("commit", xy=(commit_step, y0 + 0.52 * (y1 - y0)),
                        xytext=(-4, 0), textcoords="offset points",
                        fontsize=8, ha="right", va="center",
                        color=figstyle.GRAY, rotation=90)

        ax.set_xlabel("Step")
        ax.xaxis.set_major_locator(MaxNLocator(integer=True))
        if ax_idx == 0:
            ax.set_ylabel("Value ($-\\mathcal{G}$)")
        ax.set_title(title)
        figstyle.style_axis(ax)

    handles = [Line2D([0], [0], color=commit_color, lw=1.8, marker="o", markersize=3.5,
                      label="$-\\mathcal{G}$(commit)"),
               Line2D([0], [0], color=observe_color, lw=1.8, marker="s", markersize=3.2,
                      label="$-\\mathcal{G}$(observe)"),
               Line2D([0], [0], color=entropy_color, lw=1.4, ls="--",
                      label="Belief entropy $H(b)$")]
    fig.legend(handles=handles, loc="lower center", ncol=3,
               bbox_to_anchor=(0.5, -0.08))

    fig.tight_layout()
    fig.savefig(save_path)
    fig.savefig(save_path.replace(".pdf", ".png"))
    plt.close(fig)
    print(f"  Saved {save_path} (+ .png)")


def plot_obs_action_scaling(results: Dict, save_path: str = "figures/fig_obs_scaling.pdf"):
    """Plot success and reward vs number of observation actions K."""
    figstyle.apply()
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=figstyle.figsize(1.0, 0.42))

    order = ["Myopic", "Planning", "Planning+IG", "EFE"]
    # Planning and EFE are exactly tied at K=1 and near-tied at K=2, so dodge
    # each series on x to keep coincident markers and error bars visible.
    dodge = {name: off for name, off in zip(order, [-0.06, -0.02, 0.02, 0.06])}
    for name in order:
        if name not in results:
            continue
        d = results[name]
        x = [k + dodge[name] for k in d["K"]]
        se_s = [s * 100 for s in d.get("se_success", [0] * len(d["K"]))]
        _plot_agent_series(ax1, x, [s * 100 for s in d["success"]],
                           se_s, name)
        _plot_agent_series(ax2, x, d["reward"], d.get("se_reward"), name)

    for ax in (ax1, ax2):
        ax.set_xlabel("Number of observation actions $K$")
        ax.set_xticks([1, 2, 3])
        figstyle.style_axis(ax)

    ax1.set_ylabel("Success rate (%)")
    ax1.set_title("(a) Success rate")
    ax1.legend(loc="upper left")
    ax2.set_ylabel("Mean reward")
    ax2.set_title("(b) Mean reward")

    fig.tight_layout()
    fig.savefig(save_path)
    fig.savefig(save_path.replace(".pdf", ".png"))
    plt.close(fig)
    print(f"  Saved {save_path} (+ .png)")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def run_trajectory_demo():
    """Seeded demo-episode traces for fig_efe_trajectory (deterministic)."""
    np.random.seed(42)
    env = TigerEnv(listen_accuracy=0.85, listen_cost=1.0,
                   correct_reward=10.0, incorrect_penalty=-100.0)
    agent = make_agent(EFEAgent, env, planning_horizon=6)
    trajectories = collect_trajectories(env, agent, n_episodes=50, seed=42)
    plot_efe_trajectories(trajectories)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--replot", action="store_true",
                        help="Regenerate the figures from the committed CSVs "
                             "(and re-trace the cheap seeded demo) without "
                             "re-running the sweep batteries.")
    args = parser.parse_args()

    os.makedirs("figures", exist_ok=True)

    print("=" * 72)
    print("EXPERIMENT 1: Reward Asymmetry Sweep")
    print("=" * 72)
    if args.replot:
        sweep_results = load_asymmetry_from_csv()
        print(f"  Loaded {ASYMMETRY_CSV}")
    else:
        sweep_results = run_reward_asymmetry_sweep()
    plot_reward_asymmetry_sweep(sweep_results)

    print("\n" + "=" * 72)
    print("EXPERIMENT 2: EFE Decomposition Trajectories")
    print("=" * 72)
    run_trajectory_demo()

    print("\n" + "=" * 72)
    print("EXPERIMENT 3: Observation Action Complexity Scaling")
    print("=" * 72)
    if args.replot:
        obs_results = load_obs_scaling_from_csv()
        print(f"  Loaded {OBS_SCALING_CSV}")
    else:
        obs_results = run_obs_action_scaling()
    plot_obs_action_scaling(obs_results)

    print("\nAll figures saved to figures/")
