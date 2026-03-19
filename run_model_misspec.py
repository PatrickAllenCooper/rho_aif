#!/usr/bin/env python3
"""
Model misspecification experiment: agents believe observation accuracy
differs from the true value.

Tests robustness of EFE and baselines when the generative model is wrong.
The environment has true accuracy p_true, but agents are configured with
p_agent, creating a systematic mismatch.
"""

import numpy as np
import pandas as pd
import os

from environments.tiger import TigerEnv
from environments.diagnosis import DiagnosisEnv
from agents.efe import EFEAgent
from agents.planning import PlanningAgent
from agents.myopic import MyopicAgent
from agents.thompson import ThompsonSamplingAgent
from run_experiment import run_episode, summarize_results


def make_misspec_agent(agent_cls, env, true_accuracy, agent_accuracy, **kwargs):
    """Create an agent with a misspecified observation model."""
    if hasattr(env, "get_observation_models"):
        true_models = env.get_observation_models()
    else:
        true_models = [env.get_observation_model()]

    if hasattr(env, "get_observation_costs"):
        costs = env.get_observation_costs()
    else:
        costs = [env.observation_cost]

    config = {
        "observation_costs": costs,
        "commit_reward_matrix": env.get_commit_reward_matrix(),
    }

    misspec_models = []
    for model in true_models:
        n_states = model.shape[0]
        n_obs = model.shape[1]
        misspec = np.full_like(model, (1 - agent_accuracy) / (n_obs - 1))
        for s in range(n_states):
            correct_obs = np.argmax(model[s])
            misspec[s, correct_obs] = agent_accuracy
            row_sum = misspec[s].sum()
            misspec[s] /= row_sum
        misspec_models.append(misspec)

    return agent_cls(misspec_models, config, **kwargs)


def run_misspec_sweep(seed=42, num_episodes=200):
    true_accuracy = 0.85
    agent_accuracies = [0.70, 0.75, 0.80, 0.85, 0.90, 0.95]

    print("=" * 70)
    print("MODEL MISSPECIFICATION: Tiger (true accuracy = 0.85)")
    print("=" * 70, flush=True)

    env = TigerEnv(
        listen_accuracy=true_accuracy, listen_cost=1.0,
        correct_reward=10.0, incorrect_penalty=-100.0,
    )

    rows = []
    for p_agent in agent_accuracies:
        mismatch = p_agent - true_accuracy
        for agent_name, agent_cls, kwargs in [
            ("EFE", EFEAgent, {"planning_horizon": 4}),
            ("Planning", PlanningAgent, {"planning_horizon": 4}),
            ("Thompson", ThompsonSamplingAgent, {"num_samples": 100}),
        ]:
            np.random.seed(seed)
            agent = make_misspec_agent(
                agent_cls, env, true_accuracy, p_agent, **kwargs
            )
            results = []
            for _ in range(num_episodes):
                results.append(run_episode(agent, env))
            s = summarize_results(results)
            rows.append({
                "env": "Tiger",
                "agent": agent_name,
                "true_acc": true_accuracy,
                "agent_acc": p_agent,
                "mismatch": mismatch,
                "success": s["success_rate"],
                "reward": s["mean_reward"],
                "obs": s["mean_observations"],
            })
            print(
                f"  {agent_name:10s} p_agent={p_agent:.2f} "
                f"(mismatch={mismatch:+.2f})  "
                f"success={s['success_rate']:.1%}  "
                f"reward={s['mean_reward']:+.2f}",
                flush=True,
            )

    print("\n" + "=" * 70)
    print("MODEL MISSPECIFICATION: Diagnosis (true accuracy = 0.80)")
    print("=" * 70, flush=True)

    true_acc_diag = 0.80
    env_diag = DiagnosisEnv(
        num_conditions=4, test_accuracy=true_acc_diag, test_cost=1.0,
        correct_reward=10.0, incorrect_penalty=-50.0,
    )

    agent_accs_diag = [0.65, 0.70, 0.75, 0.80, 0.85, 0.90]
    for p_agent in agent_accs_diag:
        mismatch = p_agent - true_acc_diag
        for agent_name, agent_cls, kwargs in [
            ("EFE", EFEAgent, {"planning_horizon": 3}),
            ("Planning", PlanningAgent, {"planning_horizon": 3}),
        ]:
            np.random.seed(seed)
            agent = make_misspec_agent(
                agent_cls, env_diag, true_acc_diag, p_agent, **kwargs
            )
            results = []
            for _ in range(num_episodes):
                results.append(run_episode(agent, env_diag))
            s = summarize_results(results)
            rows.append({
                "env": "Diagnosis",
                "agent": agent_name,
                "true_acc": true_acc_diag,
                "agent_acc": p_agent,
                "mismatch": mismatch,
                "success": s["success_rate"],
                "reward": s["mean_reward"],
                "obs": s["mean_observations"],
            })
            print(
                f"  {agent_name:10s} p_agent={p_agent:.2f} "
                f"(mismatch={mismatch:+.2f})  "
                f"success={s['success_rate']:.1%}  "
                f"reward={s['mean_reward']:+.2f}",
                flush=True,
            )

    df = pd.DataFrame(rows)
    df.to_csv("results_model_misspec.csv", index=False)
    print(f"\nResults saved to results_model_misspec.csv")
    return df


if __name__ == "__main__":
    df = run_misspec_sweep()
    print("\n" + df.to_string(index=False))
