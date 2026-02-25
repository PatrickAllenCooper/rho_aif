"""
Information Gain agent (rho-POMDP with rho = entropy reduction).

Augments the myopic expected reward with an explicit information gain bonus
weighted by info_gain_weight.
"""

import numpy as np
from belief import BeliefState
from agents.base import BaseAgent


class InformationGainAgent(BaseAgent):
    """rho-POMDP agent using expected entropy reduction as belief utility."""

    def __init__(
        self,
        observation_model: np.ndarray,
        env_config: dict,
        info_gain_weight: float = 1.0,
    ):
        super().__init__(observation_model, env_config)
        self.info_gain_weight = info_gain_weight

    def select_action(self) -> int:
        commit_value = self.expected_reward_of_commit()
        observe_value = self._expected_value_of_observe_with_info_gain()
        if observe_value > commit_value:
            return 0  # OBSERVE
        return self.get_commit_action()

    def _expected_value_of_observe_with_info_gain(self) -> float:
        current_entropy = self.belief.entropy()
        expected_value = -self.config["observation_cost"]
        expected_future_entropy = 0.0
        expected_future_reward = 0.0

        for obs_idx in range(self.num_obs):
            prob_obs = (self.belief.belief * self.obs_model[:, obs_idx]).sum()
            temp = BeliefState(self.num_states, self.belief.belief.copy())
            temp.update(obs_idx, self.obs_model)
            expected_future_entropy += prob_obs * temp.entropy()
            best_commit_reward = max(
                float(np.dot(temp.belief, self.commit_rewards[i]))
                for i in range(self.num_commit_actions)
            )
            expected_future_reward += prob_obs * best_commit_reward

        info_gain = current_entropy - expected_future_entropy
        return expected_value + expected_future_reward + self.info_gain_weight * info_gain
