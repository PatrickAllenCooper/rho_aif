#!/usr/bin/env python3
"""
Run epistemic foraging experiments across environments and agents.

Compares Myopic, Information Gain, and VFE agents on discrete POMDP
environments, measuring belief convergence, sample efficiency, and
policy quality.
"""

import numpy as np
import pandas as pd
from scipy import stats
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Type

from environments.info_seeking import InfoSeekingEnv
from environments.tiger import TigerEnv
from agents.base import BaseAgent
from agents.myopic import MyopicAgent
from agents.info_gain import InformationGainAgent
from agents.vfe import VFEAgent


@dataclass
class EpisodeResult:
    agent_name: str
    num_observations: int
    final_belief_entropy: float
    final_confidence: float
    success: bool
    total_reward: float
    belief_history: List[np.ndarray] = field(default_factory=list)


def make_env_config(env) -> dict:
    """Extract agent-facing config from any environment."""
    return {
        "observation_cost": env.observation_cost,
        "correct_reward": env.correct_reward,
        "incorrect_penalty": env.incorrect_penalty,
        "commit_reward_matrix": env.get_commit_reward_matrix(),
    }


def make_agent(
    agent_class: Type[BaseAgent],
    env,
    **kwargs,
) -> BaseAgent:
    obs_model = env.get_observation_model()
    config = make_env_config(env)
    return agent_class(obs_model, config, **kwargs)


def run_episode(agent: BaseAgent, env) -> EpisodeResult:
    obs, info = env.reset()
    agent.reset()
    total_reward = 0.0
    observation_count = 0

    for _ in range(200):
        action = agent.select_action()
        obs, reward, terminated, truncated, info = env.step(action)
        total_reward += reward

        if terminated:
            return EpisodeResult(
                agent_name=agent.__class__.__name__,
                num_observations=observation_count,
                final_belief_entropy=agent.belief.entropy(),
                final_confidence=agent.belief.confidence(),
                success=info.get("correct", False),
                total_reward=total_reward,
                belief_history=[b.copy() for b in agent.belief.history],
            )

        agent.update_belief(obs)
        observation_count += 1

    return EpisodeResult(
        agent_name=agent.__class__.__name__,
        num_observations=observation_count,
        final_belief_entropy=agent.belief.entropy(),
        final_confidence=agent.belief.confidence(),
        success=False,
        total_reward=total_reward,
    )


def run_experiment(
    agent_class: Type[BaseAgent],
    env,
    num_episodes: int = 1000,
    **agent_kwargs,
) -> List[EpisodeResult]:
    agent = make_agent(agent_class, env, **agent_kwargs)
    results = []
    log_interval = max(1, num_episodes // 10)

    for i in range(num_episodes):
        result = run_episode(agent, env)
        results.append(result)
        if (i + 1) % log_interval == 0:
            pct = ((i + 1) / num_episodes) * 100
            print(f"    {i+1}/{num_episodes} ({pct:.0f}%)", flush=True)

    return results


def summarize_results(results: List[EpisodeResult]) -> Dict:
    return {
        "agent": results[0].agent_name,
        "mean_observations": np.mean([r.num_observations for r in results]),
        "std_observations": np.std([r.num_observations for r in results]),
        "mean_final_entropy": np.mean([r.final_belief_entropy for r in results]),
        "mean_confidence": np.mean([r.final_confidence for r in results]),
        "success_rate": np.mean([r.success for r in results]),
        "mean_reward": np.mean([r.total_reward for r in results]),
        "std_reward": np.std([r.total_reward for r in results]),
    }


def print_statistical_comparison(
    name_a: str,
    name_b: str,
    results_a: List[EpisodeResult],
    results_b: List[EpisodeResult],
):
    for metric_name, extractor in [
        ("Observations", lambda r: r.num_observations),
        ("Reward", lambda r: r.total_reward),
    ]:
        vals_a = [extractor(r) for r in results_a]
        vals_b = [extractor(r) for r in results_b]
        t_stat, p_val = stats.ttest_ind(vals_a, vals_b)
        sig = "***" if p_val < 0.001 else "**" if p_val < 0.01 else "*" if p_val < 0.05 else "n.s."
        print(f"  {metric_name:12s}: {name_a} vs {name_b}  t={t_stat:+.3f}  p={p_val:.6f}  {sig}")


def run_info_seeking_experiment(num_episodes: int = 1000, seed: int = 42):
    """Run the full experiment on the two-state info-seeking environment."""
    np.random.seed(seed)

    env = InfoSeekingEnv(
        observation_accuracy=0.75,
        observation_cost=0.1,
        correct_reward=1.0,
        incorrect_penalty=-1.0,
    )

    print("=" * 72)
    print("INFO-SEEKING TESTBED EXPERIMENT")
    print("=" * 72)
    print(f"  Episodes: {num_episodes}")
    print(f"  Accuracy: {env.observation_accuracy}")
    print(f"  Obs cost: {env.observation_cost}")
    print(f"  Rewards:  +{env.correct_reward} / {env.incorrect_penalty}")
    print()

    agent_configs = [
        ("Myopic", MyopicAgent, {}),
        ("InfoGain", InformationGainAgent, {"info_gain_weight": 1.0}),
        ("VFE", VFEAgent, {"planning_horizon": 4}),
    ]

    all_results = {}
    all_raw = {}

    for label, agent_class, kwargs in agent_configs:
        print(f"Running {label}...")
        raw = run_experiment(agent_class, env, num_episodes, **kwargs)
        all_raw[label] = raw
        all_results[label] = summarize_results(raw)
        s = all_results[label]
        print(
            f"  -> obs={s['mean_observations']:.2f}  "
            f"success={s['success_rate']:.1%}  "
            f"reward={s['mean_reward']:+.3f}\n"
        )

    print("-" * 72)
    print("STATISTICAL COMPARISONS")
    print("-" * 72)
    labels = list(all_raw.keys())
    for i in range(len(labels)):
        for j in range(i + 1, len(labels)):
            print_statistical_comparison(
                labels[i], labels[j], all_raw[labels[i]], all_raw[labels[j]]
            )
    print()

    summary_df = pd.DataFrame(all_results).T
    summary_df.to_csv("results_summary.csv")
    print("Results saved to results_summary.csv")
    return all_results, all_raw


def run_tiger_experiment(num_episodes: int = 1000, seed: int = 42):
    """Run the full experiment on the Tiger problem."""
    np.random.seed(seed)

    env = TigerEnv(
        listen_accuracy=0.85,
        listen_cost=1.0,
        correct_reward=10.0,
        incorrect_penalty=-100.0,
    )

    print("=" * 72)
    print("TIGER PROBLEM EXPERIMENT")
    print("=" * 72)
    print(f"  Episodes:  {num_episodes}")
    print(f"  Accuracy:  {env.listen_accuracy}")
    print(f"  Listen cost: {env.listen_cost}")
    print(f"  Rewards:   +{env.correct_reward} / {env.incorrect_penalty}")
    print()

    agent_configs = [
        ("Myopic", MyopicAgent, {}),
        ("InfoGain", InformationGainAgent, {"info_gain_weight": 1.0}),
        ("VFE", VFEAgent, {"planning_horizon": 6}),
    ]

    all_results = {}
    all_raw = {}

    for label, agent_class, kwargs in agent_configs:
        print(f"Running {label}...")
        raw = run_experiment(agent_class, env, num_episodes, **kwargs)
        all_raw[label] = raw
        all_results[label] = summarize_results(raw)
        s = all_results[label]
        print(
            f"  -> obs={s['mean_observations']:.2f}  "
            f"success={s['success_rate']:.1%}  "
            f"reward={s['mean_reward']:+.3f}\n"
        )

    print("-" * 72)
    print("STATISTICAL COMPARISONS")
    print("-" * 72)
    labels = list(all_raw.keys())
    for i in range(len(labels)):
        for j in range(i + 1, len(labels)):
            print_statistical_comparison(
                labels[i], labels[j], all_raw[labels[i]], all_raw[labels[j]]
            )
    print()

    summary_df = pd.DataFrame(all_results).T
    summary_df.to_csv("results_tiger.csv")
    print("Results saved to results_tiger.csv")
    return all_results, all_raw


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "tiger":
        run_tiger_experiment()
    elif len(sys.argv) > 1 and sys.argv[1] == "all":
        run_info_seeking_experiment()
        print("\n\n")
        run_tiger_experiment()
    else:
        run_info_seeking_experiment()
