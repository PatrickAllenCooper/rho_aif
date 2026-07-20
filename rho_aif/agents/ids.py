"""
Information-Directed Sampling adapted to observe-then-commit ρ-POMDPs.

Following Russo & Van Roy (2014), IDS minimizes the information ratio
Ψ(a) = Δ(a)² / g(a), where Δ is expected instantaneous regret and g is
expected information gain about the optimal commit action.

Adaptation to observe-then-commit (one observation menu, terminal commits):
  - Among observation actions, select argmin_k Δ(k)² / I(k).
  - Commit when the instrumental value of that observation is nonpositive
    and the current belief is already decisive, or when no observation
    yields positive information about the optimal commit.
"""

from __future__ import annotations

from typing import List, Union

import numpy as np
from scipy.stats import entropy as scipy_entropy

from rho_aif.agents.base import BaseAgent


class IDSAgent(BaseAgent):
    """Observe-then-commit IDS: minimize Δ² / I over observation actions."""

    def __init__(
        self,
        observation_models: Union[np.ndarray, List[np.ndarray]],
        env_config: dict,
        confidence_commit: float = 0.99,
        eps: float = 1e-12,
    ):
        super().__init__(observation_models, env_config)
        self.confidence_commit = confidence_commit
        self.eps = eps

    def select_action(self) -> int:
        best_commit, commit_value = self.best_commit()

        best_obs = None
        best_ratio = float("inf")
        best_info = 0.0

        for k in range(self.num_observe_actions):
            delta, info = self._obs_regret_and_info(k, commit_value)
            if info <= self.eps:
                continue
            delta = max(0.0, delta)
            ratio = (delta * delta) / info
            if ratio < best_ratio:
                best_ratio = ratio
                best_obs = k
                best_info = info

        if best_obs is None:
            return best_commit

        obs_value = self._expected_value_of_observe(best_obs)
        confidence = float(self.belief.belief.max())

        # Observe when instrumentally valuable, or when IDS still sees
        # informative unresolved uncertainty about the optimal commit.
        if obs_value > commit_value:
            return best_obs
        if best_info > self.eps and confidence < self.confidence_commit:
            return best_obs
        return best_commit

    def _expected_value_of_observe(self, obs_action: int) -> float:
        model = self.obs_models[obs_action]
        expected_value = -self.obs_costs[obs_action]
        for obs_idx in range(model.shape[1]):
            prob_obs = float(np.dot(self.belief.belief, model[:, obs_idx]))
            if prob_obs < self.eps:
                continue
            posterior = model[:, obs_idx] * self.belief.belief
            posterior = posterior / posterior.sum()
            best_commit_reward = max(
                float(np.dot(posterior, self.commit_rewards[i]))
                for i in range(self.num_commit_actions)
            )
            expected_value += prob_obs * best_commit_reward
        return expected_value

    def _obs_regret_and_info(self, obs_action: int, commit_value: float):
        """Δ: opportunity cost of observing; g: I(A*; O)."""
        model = self.obs_models[obs_action]
        belief = self.belief.belief
        cost = self.obs_costs[obs_action]

        p_astar = self._optimal_commit_distribution(belief)
        H_astar = float(scipy_entropy(p_astar + self.eps, base=2))

        expected_post = 0.0
        expected_H_astar_post = 0.0
        H_belief = float(scipy_entropy(belief + self.eps, base=2))
        expected_H_post = 0.0

        for obs_idx in range(model.shape[1]):
            prob_obs = float(np.dot(belief, model[:, obs_idx]))
            if prob_obs < self.eps:
                continue
            posterior = model[:, obs_idx] * belief
            posterior = posterior / posterior.sum()
            post_commit = max(
                float(np.dot(posterior, self.commit_rewards[i]))
                for i in range(self.num_commit_actions)
            )
            expected_post += prob_obs * post_commit

            p_astar_o = self._optimal_commit_distribution(posterior)
            expected_H_astar_post += prob_obs * float(
                scipy_entropy(p_astar_o + self.eps, base=2)
            )
            expected_H_post += prob_obs * float(
                scipy_entropy(posterior + self.eps, base=2)
            )

        info_astar = max(0.0, H_astar - expected_H_astar_post)
        info_state = max(0.0, H_belief - expected_H_post)
        info = info_astar if info_astar > self.eps else info_state

        delta = commit_value - (expected_post - cost)
        return float(delta), float(info)

    def _optimal_commit_distribution(self, belief: np.ndarray) -> np.ndarray:
        """P(A*=i) = sum_s b(s) 1[i optimal in s], ties broken uniformly."""
        n = self.num_commit_actions
        p = np.zeros(n)
        rewards = np.asarray(self.commit_rewards)
        for s, bs in enumerate(belief):
            if bs < self.eps:
                continue
            vals = rewards[:, s]
            max_v = vals.max()
            winners = np.flatnonzero(np.isclose(vals, max_v))
            for i in winners:
                p[i] += bs / len(winners)
        total = p.sum()
        if total < self.eps:
            return np.ones(n) / n
        return p / total
