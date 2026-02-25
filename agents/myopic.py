"""
Myopic reward-maximizing agent (rho-POMDP with rho = 0).

One-step lookahead baseline: compares immediate expected reward of committing
versus observing once and then committing optimally.
"""

import numpy as np
from belief import BeliefState
from agents.base import BaseAgent


class MyopicAgent(BaseAgent):
    """Baseline agent using one-step lookahead over expected reward only."""

    def select_action(self) -> int:
        commit_value = self.expected_reward_of_commit()
        observe_value = self._expected_value_of_observe()
        if observe_value > commit_value:
            return 0  # OBSERVE
        return self.get_commit_action()

    def _expected_value_of_observe(self) -> float:
        expected_value = -self.config["observation_cost"]
        for obs_idx in range(self.num_obs):
            prob_obs = (self.belief.belief * self.obs_model[:, obs_idx]).sum()
            temp = BeliefState(self.num_states, self.belief.belief.copy())
            temp.update(obs_idx, self.obs_model)
            best_commit_reward = max(
                float(np.dot(temp.belief, self.commit_rewards[i]))
                for i in range(self.num_commit_actions)
            )
            expected_value += prob_obs * best_commit_reward
        return expected_value
