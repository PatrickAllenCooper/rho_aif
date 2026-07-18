"""
EFE agent (rho-POMDP with rho = Expected Free Energy).

Selects actions by minimizing Expected Free Energy (EFE), which decomposes
into pragmatic value (goal alignment) and epistemic value (information gain)
without any tunable weight parameter. Uses recursive multi-step planning.

Supports multiple observation actions, each with its own observation model
and cost. The agent evaluates EFE for every observation action and every
commit action, selecting the global argmin.
"""

import numpy as np
from scipy.stats import entropy as scipy_entropy
from typing import Union, List
from rho_aif.belief import BeliefState
from rho_aif.agents.base import BaseAgent


class EFEAgent(BaseAgent):
    """
    rho-POMDP agent minimizing Expected Free Energy.

    For each observation action k:
      G(obs_k) = cost_k - info_gain_k + E_o[min_a G(a, posterior)]
    For each commit action i:
      G(commit_i) = -E_b[reward_i]

    The agent selects argmin over all actions.
    """

    def __init__(
        self,
        observation_models: Union[np.ndarray, List[np.ndarray]],
        env_config: dict,
        planning_horizon: int = 4,
        discount: float = 1.0,
    ):
        super().__init__(observation_models, env_config)
        self.planning_horizon = planning_horizon
        self.discount = discount

    def select_action(self) -> int:
        best_action, _ = self._evaluate(self.belief.belief, depth=0)
        return best_action

    def _evaluate(self, belief: np.ndarray, depth: int):
        """
        Recursively evaluate EFE for all available actions at a given belief.
        Returns (best_action, best_G).
        """
        if depth >= self.planning_horizon:
            return self._best_commit_efe(belief)

        best_commit_action, best_commit_g = self._best_commit_efe(belief)

        best_obs_action = None
        best_obs_g = float("inf")
        for k in range(self.num_observe_actions):
            g = self._efe_observe(k, belief, depth)
            if g < best_obs_g:
                best_obs_g = g
                best_obs_action = k

        if best_obs_g < best_commit_g:
            return best_obs_action, best_obs_g
        return best_commit_action, best_commit_g

    def _best_commit_efe(self, belief: np.ndarray):
        """Find the commit action with lowest EFE (highest expected reward)."""
        best_g = float("inf")
        best_action = self.num_observe_actions

        for i in range(self.num_commit_actions):
            expected_reward = float(np.dot(belief, self.commit_rewards[i]))
            g = -expected_reward
            if g < best_g:
                best_g = g
                best_action = self.num_observe_actions + i
        return best_action, best_g

    def _efe_observe(self, obs_action: int, belief: np.ndarray, depth: int) -> float:
        """
        Compute EFE for a specific observation action with recursive planning.

        G(obs_k) = cost_k - info_gain_k(belief) + E_o[min_a G(a, posterior, depth+1)]
        """
        model = self.obs_models[obs_action]
        num_outcomes = model.shape[1]
        prior_entropy = scipy_entropy(belief, base=2)
        expected_posterior_entropy = 0.0
        expected_continuation = 0.0

        for obs_idx in range(num_outcomes):
            prob_obs = float(np.dot(belief, model[:, obs_idx]))
            if prob_obs < 1e-10:
                continue

            posterior = model[:, obs_idx] * belief
            posterior = posterior / posterior.sum()

            expected_posterior_entropy += prob_obs * scipy_entropy(posterior, base=2)

            _, continuation_g = self._evaluate(posterior, depth + 1)
            expected_continuation += prob_obs * continuation_g

        info_gain = prior_entropy - expected_posterior_entropy

        return self.obs_costs[obs_action] - info_gain + self.discount * expected_continuation
