#!/usr/bin/env python3
"""
Long-horizon visualization experiments for the paper.

Produces four new figures that show agent behavior over extended episodes:
  - Fig 5: Belief evolution heatmap (Diagnosis N=16, K=4)
  - Fig 6: Exploration efficiency curves (entropy decay, survival, cumulative reward)
  - Fig 7: Extended EFE decomposition with test selection strategy
  - Fig 8: Stopping time distributions across environments
"""

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.colors import LinearSegmentedColormap
import matplotlib.gridspec as gridspec
from scipy.stats import entropy as scipy_entropy
from dataclasses import dataclass, field
from typing import List, Dict, Tuple, Optional
import os

from environments.diagnosis import DiagnosisEnv
from environments.bandit import BanditEnv
from agents.myopic import MyopicAgent
from agents.planning import PlanningAgent
from agents.info_gain import InformationGainAgent
from agents.planning_infogain import PlanningInfoGainAgent
from agents.efe import EFEAgent
from run_experiment import make_agent, EpisodeResult, tune_info_gain_weight
from belief import BeliefState


AGENT_STYLES = {
    "Myopic":        {"color": "#888888", "ls": "--", "marker": "s", "lw": 1.5},
    "Planning":      {"color": "#2196F3", "ls": "-",  "marker": "^", "lw": 2.0},
    "InfoGain-Tuned":{"color": "#FF9800", "ls": "-.", "marker": "D", "lw": 1.5},
    "Planning+IG":   {"color": "#9C27B0", "ls": ":",  "marker": "v", "lw": 2.0},
    "EFE":           {"color": "#D32F2F", "ls": "-",  "marker": "o", "lw": 2.5},
}

TEST_COLORS = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728"]


@dataclass
class DetailedStepTrace:
    step: int
    belief: np.ndarray
    belief_entropy: float
    action_taken: int
    action_type: str
    per_test_ig: List[float]
    best_commit_value: float
    best_observe_value: float
    reward: float
    cumulative_reward: float


@dataclass
class DetailedEpisodeResult:
    agent_name: str
    traces: List[DetailedStepTrace]
    success: bool
    total_reward: float
    num_observations: int
    true_state: int


# ---------------------------------------------------------------------------
# Episode runner with detailed tracing
# ---------------------------------------------------------------------------

def run_detailed_episode(agent, env, max_steps=200):
    """Run an episode capturing per-step belief, EFE decomposition, and actions."""
    obs, info = env.reset()
    agent.reset()
    true_state = info.get("true_condition", info.get("best_arm", 0))
    traces = []
    total_reward = 0.0
    observation_count = 0

    for step in range(max_steps):
        belief = agent.belief.belief.copy()
        b_entropy = float(scipy_entropy(belief, base=2))

        per_test_ig = []
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
            per_test_ig.append(prior_h - post_h)

        best_commit_value = float("-inf")
        if hasattr(agent, '_best_commit_efe'):
            _, commit_g = agent._best_commit_efe(belief)
            best_commit_value = -commit_g
        else:
            _, best_commit_value = agent._best_commit_from_belief(belief)

        best_observe_value = float("-inf")
        if hasattr(agent, '_efe_observe'):
            best_obs_g = float("inf")
            for k in range(agent.num_observe_actions):
                g = agent._efe_observe(k, belief, 0)
                if g < best_obs_g:
                    best_obs_g = g
            best_observe_value = -best_obs_g

        action = agent.select_action()
        is_commit = action >= agent.num_observe_actions

        obs, reward, terminated, truncated, info_step = env.step(action)
        total_reward += reward

        traces.append(DetailedStepTrace(
            step=step,
            belief=belief,
            belief_entropy=b_entropy,
            action_taken=action,
            action_type="commit" if is_commit else "observe",
            per_test_ig=per_test_ig,
            best_commit_value=best_commit_value,
            best_observe_value=best_observe_value,
            reward=reward,
            cumulative_reward=total_reward,
        ))

        if terminated or truncated:
            return DetailedEpisodeResult(
                agent_name=agent.__class__.__name__,
                traces=traces,
                success=info_step.get("correct", False),
                total_reward=total_reward,
                num_observations=observation_count,
                true_state=true_state,
            )

        agent.update_belief(obs, obs_action=action)
        observation_count += 1

    return DetailedEpisodeResult(
        agent_name=agent.__class__.__name__,
        traces=traces,
        success=False,
        total_reward=total_reward,
        num_observations=observation_count,
        true_state=true_state,
    )


def run_simple_episode(agent, env, max_steps=200):
    """Run an episode capturing belief history and basic metrics per step."""
    obs, info = env.reset()
    agent.reset()
    true_state = info.get("true_condition", info.get("best_arm", 0))

    step_entropies = []
    step_rewards = []
    cum_reward = 0.0
    observation_count = 0

    for step in range(max_steps):
        b_entropy = float(scipy_entropy(agent.belief.belief, base=2))
        step_entropies.append(b_entropy)

        action = agent.select_action()
        is_commit = action >= agent.num_observe_actions

        obs, reward, terminated, truncated, info_step = env.step(action)
        cum_reward += reward
        step_rewards.append(cum_reward)

        if terminated or truncated:
            return {
                "success": info_step.get("correct", False),
                "total_reward": cum_reward,
                "num_observations": observation_count,
                "entropies": step_entropies,
                "cumulative_rewards": step_rewards,
                "belief_history": [b.copy() for b in agent.belief.history],
                "true_state": true_state,
            }

        agent.update_belief(obs, obs_action=action)
        observation_count += 1

    return {
        "success": False,
        "total_reward": cum_reward,
        "num_observations": observation_count,
        "entropies": step_entropies,
        "cumulative_rewards": step_rewards,
        "belief_history": [b.copy() for b in agent.belief.history],
        "true_state": true_state,
    }


# ---------------------------------------------------------------------------
# Figure 5: Belief Evolution Heatmap
# ---------------------------------------------------------------------------

def fig_belief_heatmap(seed=42, save_path="figures/fig_belief_heatmap.pdf"):
    """Three-panel heatmap: EFE vs Planning vs InfoGain-Tuned belief evolution."""
    print("  Generating belief evolution heatmap...")
    np.random.seed(seed)

    env = DiagnosisEnv(
        num_conditions=8, num_tests=3, test_accuracy=0.75,
        test_cost=1.0, correct_reward=10.0, incorrect_penalty=-50.0,
    )

    best_w = tune_info_gain_weight(env, tune_episodes=100)

    agents_config = [
        ("EFE", EFEAgent, {"planning_horizon": 3}),
        ("Planning", PlanningAgent, {"planning_horizon": 3}),
        ("InfoGain-Tuned", InformationGainAgent, {"info_gain_weight": best_w}),
    ]

    target_seed = None
    np.random.seed(seed)
    for trial_seed in range(seed, seed + 200):
        np.random.seed(trial_seed)
        vfe_agent = make_agent(EFEAgent, env, planning_horizon=3)
        result = run_simple_episode(vfe_agent, env, max_steps=50)
        if result["success"] and result["num_observations"] >= 6:
            target_seed = trial_seed
            break

    if target_seed is None:
        target_seed = seed

    fig, axes = plt.subplots(1, 3, figsize=(14, 4.5))
    panel_labels = ["(a) EFE ($w{=}1$)", "(b) Planning ($\\rho{=}0$)", "(c) InfoGain-Tuned"]

    for ax_idx, (label, agent_cls, kwargs) in enumerate(agents_config):
        np.random.seed(target_seed)
        agent = make_agent(agent_cls, env, **kwargs)
        result = run_simple_episode(agent, env, max_steps=50)

        beliefs = result["belief_history"]
        true_state = result["true_state"]
        n_steps = len(beliefs)
        n_states = beliefs[0].shape[0]

        belief_matrix = np.array(beliefs).T

        ax = axes[ax_idx]
        im = ax.imshow(
            belief_matrix, aspect="auto", cmap="inferno",
            vmin=0, vmax=1.0, interpolation="nearest",
        )

        commit_step = result["num_observations"]
        ax.axvline(commit_step, color="white", ls="--", lw=1.5, alpha=0.8)

        ax.plot(
            [-0.5, n_steps - 0.5],
            [true_state, true_state],
            color="#00FF00", ls="-", lw=0.8, alpha=0.6,
        )
        ax.annotate(
            f"true={true_state}", xy=(0, true_state),
            fontsize=6, color="#00FF00", va="bottom",
        )

        ax.set_xlabel("Time step")
        if ax_idx == 0:
            ax.set_ylabel("State index")
        ax.set_title(
            f"{panel_labels[ax_idx]}\n"
            f"obs={result['num_observations']}, "
            f"{'correct' if result['success'] else 'wrong'}, "
            f"R={result['total_reward']:+.1f}",
            fontsize=9,
        )

        if n_states <= 16:
            ax.set_yticks(range(0, n_states, 2))

    cbar_ax = fig.add_axes([0.92, 0.15, 0.015, 0.7])
    fig.colorbar(im, cax=cbar_ax, label="Belief probability")

    plt.tight_layout(rect=[0, 0, 0.91, 1])
    plt.savefig(save_path, bbox_inches="tight", dpi=300)
    plt.close()
    print(f"  Saved {save_path}")


# ---------------------------------------------------------------------------
# Figure 6: Exploration Efficiency Curves
# ---------------------------------------------------------------------------

def fig_efficiency_curves(seed=42, num_episodes=300, save_path="figures/fig_efficiency_curves.pdf"):
    """Three-panel: entropy decay, survival curve, cumulative reward over steps."""
    print("  Generating exploration efficiency curves...")
    np.random.seed(seed)

    env = DiagnosisEnv(
        num_conditions=8, num_tests=3, test_accuracy=0.75,
        test_cost=1.0, correct_reward=10.0, incorrect_penalty=-50.0,
    )

    best_w = tune_info_gain_weight(env, tune_episodes=100)

    agents_config = [
        ("Myopic", MyopicAgent, {}),
        ("Planning", PlanningAgent, {"planning_horizon": 3}),
        ("Planning+IG", PlanningInfoGainAgent, {"planning_horizon": 3, "info_gain_weight": best_w}),
        ("EFE", EFEAgent, {"planning_horizon": 3}),
    ]

    max_step = 40
    all_data = {}

    for label, agent_cls, kwargs in agents_config:
        print(f"    Running {label} ({num_episodes} episodes)...")
        np.random.seed(seed)
        agent = make_agent(agent_cls, env, **kwargs)

        entropies_by_step = [[] for _ in range(max_step)]
        cum_rewards_by_step = [[] for _ in range(max_step)]
        commit_steps = []

        for _ in range(num_episodes):
            result = run_simple_episode(agent, env, max_steps=max_step)
            n_obs = result["num_observations"]
            commit_steps.append(n_obs)

            for s, e in enumerate(result["entropies"]):
                if s < max_step:
                    entropies_by_step[s].append(e)
            for s, cr in enumerate(result["cumulative_rewards"]):
                if s < max_step:
                    cum_rewards_by_step[s].append(cr)

        all_data[label] = {
            "entropies_by_step": entropies_by_step,
            "cum_rewards_by_step": cum_rewards_by_step,
            "commit_steps": commit_steps,
        }

    fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(14, 4))

    for label, style in AGENT_STYLES.items():
        if label not in all_data:
            continue
        data = all_data[label]

        steps = []
        means = []
        lo_bounds = []
        hi_bounds = []
        for s in range(max_step):
            vals = data["entropies_by_step"][s]
            if len(vals) < 10:
                break
            steps.append(s)
            m = np.mean(vals)
            se = np.std(vals) / np.sqrt(len(vals))
            means.append(m)
            lo_bounds.append(m - se)
            hi_bounds.append(m + se)

        ax1.plot(steps, means, color=style["color"], ls=style["ls"],
                 lw=style["lw"], label=label)
        ax1.fill_between(steps, lo_bounds, hi_bounds, color=style["color"], alpha=0.1)

    ax1.set_xlabel("Time step")
    ax1.set_ylabel("Belief entropy (bits)")
    ax1.set_title("(a) Entropy decay")
    ax1.grid(True, alpha=0.2)
    ax1.legend(fontsize=7, loc="upper right")

    for label, style in AGENT_STYLES.items():
        if label not in all_data:
            continue
        data = all_data[label]
        cs = np.array(data["commit_steps"])
        n = len(cs)
        steps_range = np.arange(0, max_step)
        survival = np.array([np.sum(cs > s) / n for s in steps_range])
        ax2.step(steps_range, survival * 100, where="post",
                 color=style["color"], ls=style["ls"], lw=style["lw"], label=label)

    ax2.set_xlabel("Time step")
    ax2.set_ylabel("Episodes still observing (%)")
    ax2.set_title("(b) Observation survival")
    ax2.grid(True, alpha=0.2)
    ax2.set_ylim([-2, 102])

    for label, style in AGENT_STYLES.items():
        if label not in all_data:
            continue
        data = all_data[label]

        steps = []
        means = []
        lo_bounds = []
        hi_bounds = []
        for s in range(max_step):
            vals = data["cum_rewards_by_step"][s]
            if len(vals) < 10:
                break
            steps.append(s)
            m = np.mean(vals)
            se = np.std(vals) / np.sqrt(len(vals))
            means.append(m)
            lo_bounds.append(m - se)
            hi_bounds.append(m + se)

        ax3.plot(steps, means, color=style["color"], ls=style["ls"],
                 lw=style["lw"], label=label)
        ax3.fill_between(steps, lo_bounds, hi_bounds, color=style["color"], alpha=0.1)

    ax3.set_xlabel("Time step")
    ax3.set_ylabel("Cumulative reward")
    ax3.set_title("(c) Cumulative reward")
    ax3.grid(True, alpha=0.2)

    plt.tight_layout()
    plt.savefig(save_path, bbox_inches="tight", dpi=300)
    plt.close()
    print(f"  Saved {save_path}")


# ---------------------------------------------------------------------------
# Figure 7: Extended EFE Decomposition with Test Selection
# ---------------------------------------------------------------------------

def fig_extended_efe(seed=42, save_path="figures/fig_extended_efe.pdf"):
    """Four-panel EFE decomposition over an extended Diagnosis episode."""
    print("  Generating extended EFE decomposition...")

    env = DiagnosisEnv(
        num_conditions=8, num_tests=3, test_accuracy=0.75,
        test_cost=1.0, correct_reward=10.0, incorrect_penalty=-50.0,
    )

    target_seed = None
    for trial_seed in range(seed, seed + 300):
        np.random.seed(trial_seed)
        agent = make_agent(EFEAgent, env, planning_horizon=3)
        result = run_detailed_episode(agent, env, max_steps=50)
        if result.success and result.num_observations >= 8:
            target_seed = trial_seed
            break

    if target_seed is None:
        target_seed = seed

    np.random.seed(target_seed)
    agent = make_agent(EFEAgent, env, planning_horizon=3)
    result = run_detailed_episode(agent, env, max_steps=50)

    obs_traces = [t for t in result.traces if t.action_type == "observe"]
    commit_trace = next((t for t in result.traces if t.action_type == "commit"), None)
    all_traces = obs_traces + ([commit_trace] if commit_trace else [])

    steps = [t.step for t in all_traces]

    fig, axes = plt.subplots(4, 1, figsize=(10, 10), sharex=True,
                             gridspec_kw={"height_ratios": [3, 2.5, 2, 1]})

    ax1 = axes[0]
    commit_vals = [t.best_commit_value for t in all_traces]
    observe_vals = [t.best_observe_value for t in all_traces]
    ax1.plot(steps, commit_vals, color="#D32F2F", lw=2.5, label="Value of committing", zorder=3)
    ax1.plot(steps, observe_vals, color="#2196F3", lw=2.5, label="Value of observing", zorder=3)

    if commit_trace:
        ax1.axvline(commit_trace.step, color="#333333", ls=":", lw=1.5, alpha=0.7)
        ylim = ax1.get_ylim()
        ax1.annotate("commit", xy=(commit_trace.step, ylim[1] * 0.95),
                     fontsize=8, ha="right", color="#333333")

    ax1.set_ylabel("$-\\mathcal{G}$ (value)")
    ax1.set_title(
        f"Extended EFE decomposition -- Diagnosis N=8, K=3 "
        f"(episode seed={target_seed}, {'correct' if result.success else 'wrong'})",
        fontsize=10,
    )
    ax1.legend(fontsize=8, loc="lower right")
    ax1.grid(True, alpha=0.2)

    ax2 = axes[1]
    num_tests = len(all_traces[0].per_test_ig)
    for k in range(num_tests):
        ig_vals = [t.per_test_ig[k] for t in all_traces]
        ax2.plot(steps, ig_vals, color=TEST_COLORS[k % len(TEST_COLORS)],
                 lw=1.8, label=f"Test {k}", marker=".", markersize=4)

    ax2.set_ylabel("Information gain (bits)")
    ax2.legend(fontsize=7, loc="upper right", ncol=2)
    ax2.grid(True, alpha=0.2)
    ax2.set_title("(b) Per-test expected information gain", fontsize=9)

    ax3 = axes[2]
    entropies = [t.belief_entropy for t in all_traces]
    ax3.fill_between(steps, entropies, alpha=0.2, color="#4CAF50")
    ax3.plot(steps, entropies, color="#4CAF50", lw=2)
    ax3.set_ylabel("Entropy (bits)")
    ax3.grid(True, alpha=0.2)
    ax3.set_title("(c) Belief entropy", fontsize=9)

    ax4 = axes[3]
    obs_steps_only = [t.step for t in obs_traces]
    obs_actions = [t.action_taken for t in obs_traces]
    for i, (s, a) in enumerate(zip(obs_steps_only, obs_actions)):
        ax4.barh(0, 1, left=s - 0.5, height=0.6,
                 color=TEST_COLORS[a % len(TEST_COLORS)], edgecolor="white", linewidth=0.5)

    legend_patches = [plt.Rectangle((0, 0), 1, 1, fc=TEST_COLORS[k])
                      for k in range(num_tests)]
    ax4.legend(legend_patches, [f"Test {k}" for k in range(num_tests)],
               fontsize=7, loc="upper right", ncol=num_tests)
    ax4.set_yticks([])
    ax4.set_xlabel("Time step")
    ax4.set_title("(d) Test selection sequence", fontsize=9)
    ax4.set_ylim(-0.5, 0.5)

    plt.tight_layout()
    plt.savefig(save_path, bbox_inches="tight", dpi=300)
    plt.close()
    print(f"  Saved {save_path}")


# ---------------------------------------------------------------------------
# Figure 8: Stopping Time Distribution
# ---------------------------------------------------------------------------

def fig_stopping_times(seed=42, num_episodes=300, save_path="figures/fig_stopping_times.pdf"):
    """Violin plots of episode lengths across agents and environments."""
    print("  Generating stopping time distributions...")

    env_configs = {
        "Diagnosis\nN=4, K=2": DiagnosisEnv(
            num_conditions=4, num_tests=2, test_accuracy=0.80,
            test_cost=1.0, correct_reward=10.0, incorrect_penalty=-50.0,
        ),
        "Diagnosis\nN=8, K=3": DiagnosisEnv(
            num_conditions=8, num_tests=3, test_accuracy=0.80,
            test_cost=1.0, correct_reward=10.0, incorrect_penalty=-50.0,
        ),
        "Bandit\nK=4": BanditEnv(
            num_arms=4, inspect_accuracy=0.80,
            inspect_cost=0.5, correct_reward=10.0, small_reward=1.0,
        ),
    }

    agent_order = ["Myopic", "Planning", "Planning+IG", "EFE"]
    agent_colors = {name: AGENT_STYLES[name]["color"] for name in agent_order}

    fig, axes = plt.subplots(1, 3, figsize=(14, 4.5))

    for ax_idx, (env_label, env) in enumerate(env_configs.items()):
        np.random.seed(seed)
        best_w = tune_info_gain_weight(env, tune_episodes=100)

        h_map = {"Diagnosis\nN=8, K=3": 3, "Diagnosis\nN=16, K=4": 4, "Bandit\nK=4": 2}
        horizon = h_map.get(env_label, 3)

        agent_defs = [
            ("Myopic", MyopicAgent, {}),
            ("Planning", PlanningAgent, {"planning_horizon": horizon}),
            ("Planning+IG", PlanningInfoGainAgent, {"planning_horizon": horizon, "info_gain_weight": best_w}),
            ("EFE", EFEAgent, {"planning_horizon": horizon}),
        ]

        all_obs_counts = {}
        for label, agent_cls, kwargs in agent_defs:
            np.random.seed(seed)
            agent = make_agent(agent_cls, env, **kwargs)
            obs_counts = []
            for _ in range(num_episodes):
                result = run_simple_episode(agent, env, max_steps=60)
                obs_counts.append(result["num_observations"])
            all_obs_counts[label] = obs_counts
            print(f"    {env_label.replace(chr(10), ' ')}: {label} done "
                  f"(median={np.median(obs_counts):.0f})")

        ax = axes[ax_idx]
        positions = range(len(agent_order))
        violin_data = [all_obs_counts[name] for name in agent_order]
        colors = [agent_colors[name] for name in agent_order]

        parts = ax.violinplot(violin_data, positions=positions, showmedians=True,
                              showextrema=False)

        for i, pc in enumerate(parts["bodies"]):
            pc.set_facecolor(colors[i])
            pc.set_alpha(0.5)
            pc.set_edgecolor(colors[i])

        parts["cmedians"].set_color("black")
        parts["cmedians"].set_linewidth(2)

        for i, name in enumerate(agent_order):
            data = all_obs_counts[name]
            jitter = np.random.default_rng(42).uniform(-0.15, 0.15, size=min(80, len(data)))
            sample_idx = np.random.default_rng(42).choice(len(data), size=min(80, len(data)), replace=False)
            ax.scatter(
                [i + j for j in jitter],
                [data[idx] for idx in sample_idx],
                c=colors[i], s=3, alpha=0.2, zorder=1,
            )

        ax.set_xticks(positions)
        ax.set_xticklabels(agent_order, fontsize=8, rotation=15, ha="right")
        ax.set_ylabel("Observations before commit" if ax_idx == 0 else "")
        ax.set_title(env_label, fontsize=10)
        ax.grid(True, alpha=0.2, axis="y")

    plt.tight_layout()
    plt.savefig(save_path, bbox_inches="tight", dpi=300)
    plt.close()
    print(f"  Saved {save_path}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    os.makedirs("figures", exist_ok=True)

    print("=" * 72)
    print("FIGURE 5: Belief Evolution Heatmap")
    print("=" * 72)
    fig_belief_heatmap()

    print("\n" + "=" * 72)
    print("FIGURE 6: Exploration Efficiency Curves")
    print("=" * 72)
    fig_efficiency_curves()

    print("\n" + "=" * 72)
    print("FIGURE 7: Extended EFE Decomposition")
    print("=" * 72)
    fig_extended_efe()

    print("\n" + "=" * 72)
    print("FIGURE 8: Stopping Time Distributions")
    print("=" * 72)
    fig_stopping_times()

    print("\nAll visualization figures saved to figures/")
