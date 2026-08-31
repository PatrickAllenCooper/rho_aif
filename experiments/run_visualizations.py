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

from rho_aif.environments.diagnosis import DiagnosisEnv
from rho_aif.environments.bandit import BanditEnv
from rho_aif.agents.myopic import MyopicAgent
from rho_aif.agents.planning import PlanningAgent
from rho_aif.agents.info_gain import InformationGainAgent
from rho_aif.agents.planning_infogain import PlanningInfoGainAgent
from rho_aif.agents.efe import EFEAgent
from run_experiment import make_agent, EpisodeResult, tune_info_gain_weight
from rho_aif.belief import BeliefState
from rho_aif import figstyle


def _style(name, lw):
    """Line style for an agent from the shared figstyle mapping."""
    s = figstyle.agent_style(name)
    return {"color": s["color"], "ls": s["linestyle"], "marker": s["marker"], "lw": lw}


AGENT_STYLES = {
    "Myopic":         _style("Myopic", 1.5),
    "Planning":       _style("Planning", 1.8),
    "InfoGain-Tuned": _style("InfoGain-Tuned", 1.8),
    "Planning+IG":    _style("Planning+IG", 2.0),
    "EFE":            _style("EFE", 2.2),
}

# Observation-action (test) colors: tests are not agents, so they must not
# reuse hues from figstyle.AGENT_COLORS ("one agent, one color, everywhere").
# A single-hue purple ramp keeps the tests ordered and off the agent palette.
TEST_COLORS = ["#3F007D", "#6A51A3", "#9E9AC8", "#CBC9E2"]

# The canonical belief colormap shared by every belief heatmap in the paper
# (light ground, darker = higher probability), set in figstyle.
HEATMAP_CMAP = figstyle.BELIEF_CMAP


def _save_fig(fig, save_path):
    """Save the PDF artifact of record plus its PNG twin."""
    base = os.path.splitext(save_path)[0]
    fig.savefig(base + ".pdf", bbox_inches="tight", dpi=300)
    fig.savefig(base + ".png", bbox_inches="tight", dpi=300)


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

def run_detailed_episode(agent, env, max_steps=200, seed=None):
    """Run an episode capturing per-step belief, EFE decomposition, and actions."""
    obs, info = env.reset(seed=seed)
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
                g, _ = agent._efe_observe(k, belief, 0)
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


def run_simple_episode(agent, env, max_steps=200, seed=None):
    """Run an episode capturing belief history and basic metrics per step."""
    obs, info = env.reset(seed=seed)
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
    figstyle.apply()
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
        efe_agent = make_agent(EFEAgent, env, planning_horizon=3)
        result = run_simple_episode(efe_agent, env, max_steps=50, seed=trial_seed)
        if result["success"] and result["num_observations"] >= 6:
            target_seed = trial_seed
            break

    if target_seed is None:
        target_seed = seed

    # Run the three episodes up front so every panel can share one time axis.
    # Equal physical width per time step makes the episode-length differences
    # (Planning commits early, InfoGain-Tuned over-explores) directly visible.
    episode_results = []
    for label, agent_cls, kwargs in agents_config:
        np.random.seed(target_seed)
        agent = make_agent(agent_cls, env, **kwargs)
        episode_results.append(
            run_simple_episode(agent, env, max_steps=50, seed=target_seed))
    max_len = max(len(r["belief_history"]) for r in episode_results)

    # Authored at the width it is printed at (0.78 of the JAIR text block).
    fig, axes = plt.subplots(1, 3, figsize=figstyle.figsize(0.78, 0.42),
                             sharey=True)
    panel_labels = ["(a) EFE ($w{=}1$)", "(b) Planning ($\\rho{=}0$)", "(c) InfoGain-Tuned"]

    from matplotlib.ticker import MultipleLocator
    for ax_idx, (label, agent_cls, kwargs) in enumerate(agents_config):
        result = episode_results[ax_idx]

        beliefs = result["belief_history"]
        true_state = result["true_state"]
        n_states = beliefs[0].shape[0]

        belief_matrix = np.array(beliefs).T

        ax = axes[ax_idx]
        im = ax.imshow(
            belief_matrix, aspect="auto", cmap=HEATMAP_CMAP,
            vmin=0, vmax=1.0, interpolation="nearest",
        )
        ax.grid(False)
        ax.set_xlim(-0.5, max_len + 0.5)

        commit_step = result["num_observations"]
        ax.axvline(commit_step, color=figstyle.BLACK, ls="--", lw=1.0, alpha=0.85)
        if ax_idx == 0:
            ax.annotate("commit", xy=(commit_step + 0.7, n_states - 1.0),
                        fontsize=7, color=figstyle.BLACK, rotation=90,
                        ha="left", va="bottom")

        # The true-state row is marked in the margin (shared y-axis label plus
        # a small tick per panel) rather than by a line bisecting the row.
        ax.plot([-0.5], [true_state], marker=">", ms=4, color=figstyle.GREEN,
                clip_on=False, zorder=6)

        ax.set_xlabel("Time step")
        if ax_idx == 0:
            ax.set_ylabel("State index")
            ax.set_yticks(range(n_states))
            ytick_labels = [str(i) for i in range(n_states)]
            ytick_labels[true_state] = f"{true_state} (true)"
            ax.set_yticklabels(ytick_labels)
            for tick in ax.get_yticklabels():
                if tick.get_text().endswith("(true)"):
                    tick.set_color(figstyle.GREEN)
        ax.set_title(
            f"{panel_labels[ax_idx]}\n"
            f"obs={result['num_observations']}, "
            f"{'correct' if result['success'] else 'wrong'}, "
            f"R={result['total_reward']:+.0f}",
            fontsize=8,
        )

        ax.xaxis.set_major_locator(MultipleLocator(5))

    cbar_ax = fig.add_axes([0.92, 0.15, 0.015, 0.7])
    fig.colorbar(im, cax=cbar_ax, label="Belief probability")

    plt.tight_layout(rect=[0, 0, 0.91, 1])
    _save_fig(fig, save_path)
    plt.close()
    print(f"  Saved {save_path} (+ .png)")


# ---------------------------------------------------------------------------
# Figure 6: Exploration Efficiency Curves
# ---------------------------------------------------------------------------

def fig_efficiency_curves(seed=42, num_episodes=300, save_path="figures/fig_efficiency_curves.pdf"):
    """Three-panel: entropy decay, survival curve, cumulative reward over steps."""
    print("  Generating exploration efficiency curves...")
    figstyle.apply()
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

        for ep_i in range(num_episodes):
            result = run_simple_episode(agent, env, max_steps=max_step, seed=seed * 10000 + ep_i)
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

    # Stacked 3x1 with a shared time axis, authored at the printed width
    # (0.78 of the JAIR text block), so commit times can be compared
    # vertically across panels and rcParams type prints at rcParams size.
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=figstyle.figsize(0.78, 1.18),
                                        sharex=True)

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
        # End-of-series marker so short-lived curves (Myopic commits by step
        # ~3 under identical early entropy) remain visible.
        ax1.plot(steps[-1], means[-1], marker=style["marker"], ms=5,
                 color=style["color"], zorder=4)

    ax1.set_ylabel("Belief entropy (bits)")
    ax1.set_title("(a) Entropy decay")
    # Entropy has a meaningful zero and a meaningful maximum (log2 8 = 3 bits).
    ax1.set_ylim(0, 3.05)
    ax1.legend(loc="upper right")

    for label, style in AGENT_STYLES.items():
        if label not in all_data:
            continue
        data = all_data[label]
        cs = np.array(data["commit_steps"])
        n = len(cs)
        steps_range = np.arange(0, max_step)
        survival = np.array([np.sum(cs > s) / n for s in steps_range])
        # Binomial SE band, matching the SE convention of panels (a) and (c).
        se = np.sqrt(survival * (1.0 - survival) / n)
        ax2.step(steps_range, survival * 100, where="post",
                 color=style["color"], ls=style["ls"], lw=style["lw"], label=label)
        ax2.fill_between(steps_range, (survival - se) * 100, (survival + se) * 100,
                         step="post", color=style["color"], alpha=0.1)

    ax2.set_ylabel("Episodes still observing (%)")
    ax2.set_title("(b) Observation survival")
    ax2.set_ylim([-2, 102])

    # Draw Planning+IG last in panel (c): its dotted line stays legible on
    # top of EFE's solid one where the two curves coincide.
    order_c = [l for l in AGENT_STYLES if l != "Planning+IG"] + ["Planning+IG"]
    for label in order_c:
        if label not in all_data:
            continue
        style = AGENT_STYLES[label]
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

    for ax in (ax1, ax2, ax3):
        figstyle.style_axis(ax)

    plt.tight_layout()
    _save_fig(fig, save_path)
    plt.close()
    print(f"  Saved {save_path} (+ .png)")


# ---------------------------------------------------------------------------
# Figure 7: Extended EFE Decomposition with Test Selection
# ---------------------------------------------------------------------------

def fig_extended_efe(seed=42, save_path="figures/fig_extended_efe.pdf"):
    """Four-panel EFE decomposition over an extended Diagnosis episode."""
    print("  Generating extended EFE decomposition...")
    figstyle.apply()

    env = DiagnosisEnv(
        num_conditions=8, num_tests=3, test_accuracy=0.75,
        test_cost=1.0, correct_reward=10.0, incorrect_penalty=-50.0,
    )

    target_seed = None
    for trial_seed in range(seed, seed + 300):
        np.random.seed(trial_seed)
        agent = make_agent(EFEAgent, env, planning_horizon=3)
        result = run_detailed_episode(agent, env, max_steps=50, seed=trial_seed)
        if result.success and result.num_observations >= 8:
            target_seed = trial_seed
            break

    if target_seed is None:
        target_seed = seed

    np.random.seed(target_seed)
    agent = make_agent(EFEAgent, env, planning_horizon=3)
    result = run_detailed_episode(agent, env, max_steps=50, seed=target_seed)

    obs_traces = [t for t in result.traces if t.action_type == "observe"]
    commit_trace = next((t for t in result.traces if t.action_type == "commit"), None)
    all_traces = obs_traces + ([commit_trace] if commit_trace else [])

    steps = [t.step for t in all_traces]

    # Authored at the printed width (0.78 of the JAIR text block). The test-
    # selection strip gets a slim row since it carries no y quantity.
    fig, axes = plt.subplots(4, 1, figsize=figstyle.figsize(0.78, 1.12), sharex=True,
                             gridspec_kw={"height_ratios": [3, 2.5, 2, 0.6]})

    ax1 = axes[0]
    commit_vals = [t.best_commit_value for t in all_traces]
    observe_vals = [t.best_observe_value for t in all_traces]
    # Neutral encoding: these are value curves, not agents, so they stay off
    # the agent palette (vermillion/blue mean EFE/Planning elsewhere).
    ax1.plot(steps, commit_vals, color=figstyle.BLACK, ls="-", lw=1.8,
             label="Value of committing", zorder=3)
    ax1.plot(steps, observe_vals, color=figstyle.GRAY, ls="--", lw=1.8,
             label="Value of observing", zorder=3)

    if commit_trace:
        # One commit rule running down all four shared-x panels.
        for ax in axes:
            ax.axvline(commit_trace.step, color=figstyle.GRAY, ls=":",
                       lw=1.2, alpha=0.8)
        y0, y1 = ax1.get_ylim()
        ax1.annotate("commit", xy=(commit_trace.step - 0.3, y0 + 0.55 * (y1 - y0)),
                     fontsize=8, ha="right", va="center", color=figstyle.GRAY)

    # Keep the crossover inside the axes with margin instead of pinned to the
    # right spine, and mark the crossing point itself.
    if commit_trace:
        ax1.set_xlim(-1, commit_trace.step + 2)
    cross_x = cross_y = None
    for i in range(len(steps) - 1, 0, -1):
        d1 = commit_vals[i] - observe_vals[i]
        d0 = commit_vals[i - 1] - observe_vals[i - 1]
        if d0 < 0 <= d1:
            frac = -d0 / (d1 - d0) if d1 != d0 else 0.0
            cross_x = steps[i - 1] + frac * (steps[i] - steps[i - 1])
            cross_y = commit_vals[i - 1] + frac * (commit_vals[i] - commit_vals[i - 1])
            break
    if cross_x is not None:
        ax1.plot([cross_x], [cross_y], marker="o", ms=7, mfc="none",
                 mec=figstyle.BLACK, mew=1.2, ls="none", zorder=4)
        ax1.annotate("crossover", xy=(cross_x, cross_y),
                     xytext=(cross_x - 1.2, cross_y - 9), fontsize=7.5,
                     ha="right", va="top", color=figstyle.BLACK,
                     arrowprops=dict(arrowstyle="-", lw=0.5,
                                     color=figstyle.GRAY, shrinkA=1, shrinkB=4))

    ax1.set_ylabel("$-\\mathcal{G}$ (reward units)")
    ax1.set_title("(a) Value of committing vs observing", fontsize=9)
    ax1.legend(loc="lower right")

    ax2 = axes[1]
    num_tests = len(all_traces[0].per_test_ig)
    ig_max = 0.0
    for k in range(num_tests):
        ig_vals = [t.per_test_ig[k] for t in all_traces]
        ig_max = max(ig_max, max(ig_vals))
        ax2.plot(steps, ig_vals, color=TEST_COLORS[k % len(TEST_COLORS)],
                 lw=1.8, label=f"Test {k}", marker=".", markersize=4)

    ax2.set_ylabel("Information gain (bits)")
    # Single in-axes legend (panel (d) reuses the same colors directly below,
    # so it carries no legend of its own).
    ax2.set_ylim(top=ig_max * 1.30)
    ax2.legend(loc="upper right", ncol=num_tests, columnspacing=1.0,
               handlelength=1.4)
    ax2.set_title("(b) Per-test expected information gain", fontsize=9)

    ax3 = axes[2]
    entropies = [t.belief_entropy for t in all_traces]
    # Same belief-entropy styling as fig_efe_trajectory (green dashed + fill).
    ax3.fill_between(steps, entropies, alpha=0.12, color=figstyle.GREEN)
    ax3.plot(steps, entropies, color=figstyle.GREEN, lw=1.4, ls="--")
    ax3.set_ylabel("Entropy (bits)")
    ax3.set_title("(c) Belief entropy", fontsize=9)

    ax4 = axes[3]
    obs_steps_only = [t.step for t in obs_traces]
    obs_actions = [t.action_taken for t in obs_traces]
    for i, (s, a) in enumerate(zip(obs_steps_only, obs_actions)):
        ax4.barh(0, 1, left=s - 0.5, height=0.6,
                 color=TEST_COLORS[a % len(TEST_COLORS)], edgecolor="white", linewidth=0.5)

    ax4.set_yticks([])
    ax4.grid(False)
    ax4.spines["left"].set_visible(False)
    ax4.set_xlabel("Time step")
    ax4.set_title("(d) Test selection sequence", fontsize=9)
    ax4.set_ylim(-0.35, 0.35)

    for ax in (ax1, ax2, ax3, ax4):
        figstyle.style_axis(ax)

    plt.tight_layout()
    _save_fig(fig, save_path)
    plt.close()
    print(f"  Saved {save_path} (+ .png)")


# ---------------------------------------------------------------------------
# Figure 8: Stopping Time Distribution
# ---------------------------------------------------------------------------

def fig_stopping_times(seed=42, num_episodes=300, save_path="figures/fig_stopping_times.pdf"):
    """Violin plots of episode lengths across agents and environments."""
    print("  Generating stopping time distributions...")
    figstyle.apply()

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
    agent_colors = {name: figstyle.agent_color(name) for name in agent_order}

    panel_titles = [
        "(a) Diagnosis $N{=}4$, $K{=}2$",
        "(b) Diagnosis $N{=}8$, $K{=}3$",
        "(c) Bandit $K{=}4$",
    ]

    # Authored at the printed width (full JAIR text block). Shared y-axis
    # anchored at zero so stopping times compare across panels by eye.
    fig, axes = plt.subplots(1, 3, figsize=figstyle.figsize(1.0, 0.36),
                             sharey=True)

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
            for ep_i in range(num_episodes):
                result = run_simple_episode(agent, env, max_steps=60, seed=seed * 10000 + ep_i)
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
        if ax_idx == 0:
            ax.set_ylabel("Observations before commit")
        ax.set_title(panel_titles[ax_idx], fontsize=10)
        figstyle.style_axis(ax)

    axes[0].set_ylim(bottom=0)

    plt.tight_layout()
    _save_fig(fig, save_path)
    plt.close()
    print(f"  Saved {save_path} (+ .png)")


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
