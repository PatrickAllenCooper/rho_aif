#!/usr/bin/env python3
"""
Showcase experiments: reward asymmetry sweep and EFE decomposition trajectories.

Produces publication-quality figures that visualize the core dynamics of
EFE-as-rho: automatic adaptation to reward structure and the intrinsic
explore-exploit transition.
"""

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from scipy.stats import entropy as scipy_entropy
from dataclasses import dataclass
from typing import List, Dict, Tuple
import json

from rho_aif.environments.tiger import TigerEnv
from rho_aif.environments.diagnosis import DiagnosisEnv
from rho_aif.agents.myopic import MyopicAgent
from rho_aif.agents.planning import PlanningAgent
from rho_aif.agents.info_gain import InformationGainAgent
from rho_aif.agents.planning_infogain import PlanningInfoGainAgent
from rho_aif.agents.efe import EFEAgent
from run_experiment import make_agent, run_episode, run_experiment, summarize_results, tune_info_gain_weight


# ---------------------------------------------------------------------------
# Experiment 1: Reward asymmetry sweep on Tiger
# ---------------------------------------------------------------------------

def run_reward_asymmetry_sweep(
    penalties: List[float] = None,
    num_episodes: int = 500,
    horizon: int = 6,
    seed: int = 42,
) -> Dict:
    """Sweep Tiger penalty from mild to extreme, measuring each agent's response."""

    if penalties is None:
        penalties = [1, 2, 5, 10, 20, 50, 100, 200, 500]

    results = {name: {"penalties": [], "success": [], "reward": [], "obs": []}
               for name in ["Myopic", "Planning", "InfoGain-Tuned", "Planning+IG", "EFE"]}

    for pen in penalties:
        np.random.seed(seed)
        env = TigerEnv(
            listen_accuracy=0.85,
            listen_cost=1.0,
            correct_reward=10.0,
            incorrect_penalty=-float(pen),
        )
        print(f"  Penalty = -{pen}")

        best_w = tune_info_gain_weight(env, tune_episodes=100)

        configs = [
            ("Myopic", MyopicAgent, {}),
            ("Planning", PlanningAgent, {"planning_horizon": horizon}),
            ("InfoGain-Tuned", InformationGainAgent, {"info_gain_weight": best_w}),
            ("Planning+IG", PlanningInfoGainAgent, {"planning_horizon": horizon, "info_gain_weight": best_w}),
            ("EFE", EFEAgent, {"planning_horizon": horizon}),
        ]

        for name, cls, kwargs in configs:
            raw = run_experiment(cls, env, num_episodes, **kwargs)
            s = summarize_results(raw)
            results[name]["penalties"].append(pen)
            results[name]["success"].append(s["success_rate"])
            results[name]["reward"].append(s["mean_reward"])
            results[name]["obs"].append(s["mean_observations"])

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


def trace_efe_episode(env, agent, max_steps: int = 30) -> Tuple[List[StepTrace], bool, float]:
    """Run one episode recording EFE components at each decision point."""
    obs, info = env.reset()
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
    env, agent, n_episodes: int = 20, max_steps: int = 30
) -> List[Tuple[List[StepTrace], bool, float]]:
    """Collect multiple traced episodes."""
    all_traces = []
    for _ in range(n_episodes):
        traces, success, reward = trace_efe_episode(env, agent, max_steps)
        all_traces.append((traces, success, reward))
    return all_traces


# ---------------------------------------------------------------------------
# Experiment 3: Observation action complexity scaling
# ---------------------------------------------------------------------------

def run_obs_action_scaling(
    n_states: int = 8,
    num_episodes: int = 500,
    horizon: int = 3,
    seed: int = 42,
) -> Dict:
    """Vary K (number of tests) while holding N fixed."""

    results = {name: {"K": [], "success": [], "reward": []}
               for name in ["Myopic", "Planning", "Planning+IG", "EFE"]}

    for k in [1, 2, 3]:
        np.random.seed(seed)
        env = DiagnosisEnv(
            num_conditions=n_states,
            num_tests=k,
            test_accuracy=0.80,
            test_cost=1.0,
            correct_reward=10.0,
            incorrect_penalty=-50.0,
        )
        print(f"  K = {k} tests (N = {n_states})")

        best_w = tune_info_gain_weight(env, tune_episodes=100)

        configs = [
            ("Myopic", MyopicAgent, {}),
            ("Planning", PlanningAgent, {"planning_horizon": horizon}),
            ("Planning+IG", PlanningInfoGainAgent, {"planning_horizon": horizon, "info_gain_weight": best_w}),
            ("EFE", EFEAgent, {"planning_horizon": horizon}),
        ]

        for name, cls, kwargs in configs:
            raw = run_experiment(cls, env, num_episodes, **kwargs)
            s = summarize_results(raw)
            results[name]["K"].append(k)
            results[name]["success"].append(s["success_rate"])
            results[name]["reward"].append(s["mean_reward"])

    return results


# ---------------------------------------------------------------------------
# Figure generation
# ---------------------------------------------------------------------------

AGENT_STYLES = {
    "Myopic":        {"color": "#888888", "ls": "--", "marker": "s", "lw": 1.5},
    "Planning":      {"color": "#2196F3", "ls": "-",  "marker": "^", "lw": 2.0},
    "InfoGain-Tuned":{"color": "#FF9800", "ls": "-.", "marker": "D", "lw": 1.5},
    "Planning+IG":   {"color": "#9C27B0", "ls": ":",  "marker": "v", "lw": 2.0},
    "EFE":           {"color": "#D32F2F", "ls": "-",  "marker": "o", "lw": 2.5},
}


def plot_reward_asymmetry_sweep(results: Dict, save_path: str = "figures/fig_asymmetry_sweep.pdf"):
    """Two-panel figure: success rate and reward vs penalty magnitude."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))

    for name, style in AGENT_STYLES.items():
        if name not in results:
            continue
        d = results[name]
        ax1.plot(d["penalties"], [s * 100 for s in d["success"]],
                 color=style["color"], ls=style["ls"], marker=style["marker"],
                 lw=style["lw"], markersize=5, label=name)
        ax2.plot(d["penalties"], d["reward"],
                 color=style["color"], ls=style["ls"], marker=style["marker"],
                 lw=style["lw"], markersize=5, label=name)

    ax1.set_xlabel("Penalty magnitude $|R^-|$")
    ax1.set_ylabel("Success rate (%)")
    ax1.set_xscale("log")
    ax1.set_ylim([40, 102])
    ax1.grid(True, alpha=0.3)
    ax1.set_title("(a) Success rate vs. reward asymmetry")

    ax2.set_xlabel("Penalty magnitude $|R^-|$")
    ax2.set_ylabel("Mean reward")
    ax2.set_xscale("log")
    ax2.grid(True, alpha=0.3)
    ax2.set_title("(b) Reward vs. reward asymmetry")

    ax1.legend(fontsize=8, loc="lower right")

    plt.tight_layout()
    plt.savefig(save_path, bbox_inches="tight", dpi=300)
    plt.close()
    print(f"  Saved {save_path}")


def plot_efe_trajectories(all_traces, save_path: str = "figures/fig_efe_trajectory.pdf"):
    """Plot EFE decomposition for representative episodes."""
    successful = [(t, s, r) for t, s, r in all_traces if s and len(t) >= 3]
    if not successful:
        successful = all_traces[:3]

    fig, axes = plt.subplots(1, 3, figsize=(12, 3.5))
    titles = ["(a) Short episode", "(b) Medium episode", "(c) Long episode"]
    successful.sort(key=lambda x: len(x[0]))

    indices = [0, len(successful) // 2, -1]
    for ax_idx, (ax, title) in enumerate(zip(axes, titles)):
        traces, success, reward = successful[min(indices[ax_idx], len(successful) - 1)]
        steps = [t.step for t in traces]
        commit_vals = [-t.best_commit_efe for t in traces]
        observe_vals = [-t.best_observe_efe for t in traces]
        entropies = [t.belief_entropy for t in traces]

        ax.plot(steps, commit_vals, color="#D32F2F", lw=2, label="$-\\mathcal{G}$(commit)")
        ax.plot(steps, observe_vals, color="#2196F3", lw=2, label="$-\\mathcal{G}$(observe)")

        ax2_twin = ax.twinx()
        ax2_twin.fill_between(steps, entropies, alpha=0.15, color="#4CAF50")
        ax2_twin.plot(steps, entropies, color="#4CAF50", lw=1.5, ls="--", label="$H(b)$")
        ax2_twin.set_ylim([0, 1.2])
        if ax_idx == 2:
            ax2_twin.set_ylabel("Belief entropy (bits)", fontsize=9)
        else:
            ax2_twin.set_yticklabels([])

        commit_step = None
        for t in traces:
            if t.action_type == "commit":
                commit_step = t.step
                break
        if commit_step is not None:
            ax.axvline(commit_step, color="#333333", ls=":", lw=1, alpha=0.7)
            ax.annotate("commit", xy=(commit_step, ax.get_ylim()[1] * 0.9),
                        fontsize=7, ha="right", color="#333333")

        ax.set_xlabel("Step")
        if ax_idx == 0:
            ax.set_ylabel("Value ($-\\mathcal{G}$)")
        ax.set_title(title, fontsize=10)
        ax.grid(True, alpha=0.2)

    handles1 = [Line2D([0], [0], color="#D32F2F", lw=2, label="$-\\mathcal{G}$(commit)"),
                Line2D([0], [0], color="#2196F3", lw=2, label="$-\\mathcal{G}$(observe)"),
                Line2D([0], [0], color="#4CAF50", lw=1.5, ls="--", label="$H(b)$ entropy")]
    fig.legend(handles=handles1, loc="lower center", ncol=3, fontsize=9,
               bbox_to_anchor=(0.5, -0.05))

    plt.tight_layout()
    plt.savefig(save_path, bbox_inches="tight", dpi=300)
    plt.close()
    print(f"  Saved {save_path}")


def plot_obs_action_scaling(results: Dict, save_path: str = "figures/fig_obs_scaling.pdf"):
    """Plot success and reward vs number of observation actions K."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(10, 4))

    scale_styles = {
        "Myopic":      {"color": "#888888", "ls": "--", "marker": "s", "lw": 1.5},
        "Planning":    {"color": "#2196F3", "ls": "-",  "marker": "^", "lw": 2.0},
        "Planning+IG": {"color": "#9C27B0", "ls": ":",  "marker": "v", "lw": 2.0},
        "EFE":         {"color": "#D32F2F", "ls": "-",  "marker": "o", "lw": 2.5},
    }

    for name, style in scale_styles.items():
        if name not in results:
            continue
        d = results[name]
        ax1.plot(d["K"], [s * 100 for s in d["success"]],
                 color=style["color"], ls=style["ls"], marker=style["marker"],
                 lw=style["lw"], markersize=7, label=name)
        ax2.plot(d["K"], d["reward"],
                 color=style["color"], ls=style["ls"], marker=style["marker"],
                 lw=style["lw"], markersize=7, label=name)

    ax1.set_xlabel("Number of observation actions $K$")
    ax1.set_ylabel("Success rate (%)")
    ax1.set_xticks([1, 2, 3])
    ax1.grid(True, alpha=0.3)
    ax1.set_title("(a) Success vs. observation action complexity")
    ax1.legend(fontsize=8)

    ax2.set_xlabel("Number of observation actions $K$")
    ax2.set_ylabel("Mean reward")
    ax2.set_xticks([1, 2, 3])
    ax2.grid(True, alpha=0.3)
    ax2.set_title("(b) Reward vs. observation action complexity")

    plt.tight_layout()
    plt.savefig(save_path, bbox_inches="tight", dpi=300)
    plt.close()
    print(f"  Saved {save_path}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import os
    os.makedirs("figures", exist_ok=True)

    print("=" * 72)
    print("EXPERIMENT 1: Reward Asymmetry Sweep")
    print("=" * 72)
    sweep_results = run_reward_asymmetry_sweep(
        penalties=[1, 2, 5, 10, 20, 50, 100, 200, 500],
        num_episodes=500,
        horizon=6,
    )
    plot_reward_asymmetry_sweep(sweep_results)

    print("\n" + "=" * 72)
    print("EXPERIMENT 2: EFE Decomposition Trajectories")
    print("=" * 72)
    np.random.seed(42)
    env = TigerEnv(listen_accuracy=0.85, listen_cost=1.0,
                   correct_reward=10.0, incorrect_penalty=-100.0)
    agent = make_agent(EFEAgent, env, planning_horizon=6)
    trajectories = collect_trajectories(env, agent, n_episodes=50)
    plot_efe_trajectories(trajectories)

    print("\n" + "=" * 72)
    print("EXPERIMENT 3: Observation Action Complexity Scaling")
    print("=" * 72)
    obs_results = run_obs_action_scaling(n_states=8, num_episodes=500, horizon=3)
    plot_obs_action_scaling(obs_results)

    print("\nAll figures saved to figures/")
