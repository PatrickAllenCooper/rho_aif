"""
Information Gain agent (rho-POMDP with rho = entropy reduction).

Augments the myopic expected reward with an explicit information gain bonus
weighted by info_gain_weight. Evaluates all available observation actions.
"""

import numpy as np
from rho_aif.belief import BeliefState
from rho_aif.agents.base import BaseAgent
from typing import Union, List


class InformationGainAgent(BaseAgent):
    """rho-POMDP agent using expected entropy reduction as belief utility."""

    def __init__(
        self,
        observation_models: Union[np.ndarray, List[np.ndarray]],
        env_config: dict,
        info_gain_weight: float = 1.0,
    ):
        super().__init__(observation_models, env_config)
        self.info_gain_weight = info_gain_weight

    def select_action(self) -> int:
        _, commit_value = self.best_commit()

        best_obs_action = None
        best_obs_value = -float("inf")
        for k in range(self.num_observe_actions):
            v = self._expected_value_of_observe_with_info_gain(k)
            if v > best_obs_value:
                best_obs_value = v
                best_obs_action = k

        if best_obs_value > commit_value:
            return best_obs_action
        return self.get_commit_action()

    def _expected_value_of_observe_with_info_gain(self, obs_action: int) -> float:
        model = self.obs_models[obs_action]
        num_outcomes = model.shape[1]
        current_entropy = self.belief.entropy()
        expected_value = -self.obs_costs[obs_action]
        expected_future_entropy = 0.0
        expected_future_reward = 0.0

        for obs_idx in range(num_outcomes):
            prob_obs = float(np.dot(self.belief.belief, model[:, obs_idx]))
            if prob_obs < 1e-10:
                continue
            posterior = model[:, obs_idx] * self.belief.belief
            posterior = posterior / posterior.sum()
            temp = BeliefState(self.num_states, posterior)
            expected_future_entropy += prob_obs * temp.entropy()
            best_commit_reward = max(
                float(np.dot(posterior, self.commit_rewards[i]))
                for i in range(self.num_commit_actions)
            )
            expected_future_reward += prob_obs * best_commit_reward

        info_gain = current_entropy - expected_future_entropy
        return expected_value + expected_future_reward + self.info_gain_weight * info_gain
