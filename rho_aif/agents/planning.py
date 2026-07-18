"""
Multi-step lookahead reward-only agent (rho-POMDP with rho = 0, H > 1).

Extends the myopic baseline to recursive H-step planning over expected
reward. Uses the same tree-search structure as EFEAgent but evaluates
only reward -- no information gain, no EFE. This isolates whether the
EFE agent's advantage comes from deeper planning or from the EFE objective.

Action evaluation (maximizing expected reward):
  V(obs_k, b, d) = -cost_k + E_o[max_a V(a, posterior, d+1)]
  V(commit_i, b, d) = E_b[reward_i]
"""

import numpy as np
from typing import Union, List
from rho_aif.agents.base import BaseAgent


class PlanningAgent(BaseAgent):
    """
    Multi-step reward-only baseline matching the EFE agent's planning depth.

    Identical recursive structure to EFEAgent but optimizes cumulative
    expected reward without any belief-dependent utility (rho = 0).
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
        Recursively evaluate expected reward for all actions at a given belief.
        Returns (best_action, best_value).
        """
        if depth >= self.planning_horizon:
            return self._best_commit_from_belief(belief)

        best_commit_action, best_commit_value = self._best_commit_from_belief(belief)

        best_obs_action = None
        best_obs_value = -float("inf")
        for k in range(self.num_observe_actions):
            v = self._expected_value_of_observe(k, belief, depth)
            if v > best_obs_value:
                best_obs_value = v
                best_obs_action = k

        if best_obs_value > best_commit_value:
            return best_obs_action, best_obs_value
        return best_commit_action, best_commit_value

    def _expected_value_of_observe(self, obs_action: int, belief: np.ndarray, depth: int) -> float:
        """
        Expected cumulative reward from observing with action obs_action,
        then acting optimally for remaining depth.
        """
        model = self.obs_models[obs_action]
        num_outcomes = model.shape[1]
        expected_value = -self.obs_costs[obs_action]

        for obs_idx in range(num_outcomes):
            prob_obs = float(np.dot(belief, model[:, obs_idx]))
            if prob_obs < 1e-10:
                continue

            posterior = model[:, obs_idx] * belief
            posterior = posterior / posterior.sum()

            _, continuation_value = self._evaluate(posterior, depth + 1)
            expected_value += prob_obs * self.discount * continuation_value

        return expected_value
