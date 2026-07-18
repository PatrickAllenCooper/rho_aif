"""
Myopic reward-maximizing agent (rho-POMDP with rho = 0).

One-step lookahead baseline: compares immediate expected reward of committing
versus observing once (with any available observation action) and then
committing optimally.
"""

import numpy as np
from rho_aif.belief import BeliefState
from rho_aif.agents.base import BaseAgent


class MyopicAgent(BaseAgent):
    """Baseline agent using one-step lookahead over expected reward only."""

    def select_action(self) -> int:
        _, commit_value = self.best_commit()

        best_obs_action = None
        best_obs_value = -float("inf")
        for k in range(self.num_observe_actions):
            v = self._expected_value_of_observe(k)
            if v > best_obs_value:
                best_obs_value = v
                best_obs_action = k

        if best_obs_value > commit_value:
            return best_obs_action
        return self.get_commit_action()

    def _expected_value_of_observe(self, obs_action: int) -> float:
        model = self.obs_models[obs_action]
        num_outcomes = model.shape[1]
        expected_value = -self.obs_costs[obs_action]
        for obs_idx in range(num_outcomes):
            prob_obs = float(np.dot(self.belief.belief, model[:, obs_idx]))
            if prob_obs < 1e-10:
                continue
            posterior = model[:, obs_idx] * self.belief.belief
            posterior = posterior / posterior.sum()
            best_commit_reward = max(
                float(np.dot(posterior, self.commit_rewards[i]))
                for i in range(self.num_commit_actions)
            )
            expected_value += prob_obs * best_commit_reward
        return expected_value
