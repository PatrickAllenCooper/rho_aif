"""
Base agent class for discrete POMDP agents with belief tracking.
"""

import numpy as np
from belief import BeliefState


class BaseAgent:
    """
    Base class providing belief management for POMDP agents.

    Subclasses must implement select_action().
    """

    def __init__(self, observation_model: np.ndarray, env_config: dict):
        """
        Args:
            observation_model: P(obs | state) matrix, shape (num_states, num_obs).
            env_config: Dict with keys 'observation_cost', 'correct_reward',
                        'incorrect_penalty', and 'commit_reward_matrix'
                        (shape: num_commit_actions x num_states).
        """
        self.obs_model = observation_model
        self.config = env_config
        self.num_states = observation_model.shape[0]
        self.num_obs = observation_model.shape[1]
        self.commit_rewards = env_config["commit_reward_matrix"]
        self.num_commit_actions = self.commit_rewards.shape[0]
        self.belief = BeliefState(self.num_states)

    def reset(self) -> None:
        self.belief.reset()

    def update_belief(self, observation: int) -> None:
        self.belief.update(observation, self.obs_model)

    def select_action(self) -> int:
        raise NotImplementedError

    def expected_reward_of_commit(self) -> float:
        """Expected reward from the best commit action."""
        _, best_reward = self.best_commit()
        return best_reward

    def best_commit(self):
        """Return (action, expected_reward) for the best commit action."""
        best_action = 1
        best_reward = -float("inf")
        for i in range(self.num_commit_actions):
            r = float(np.dot(self.belief.belief, self.commit_rewards[i]))
            if r > best_reward:
                best_reward = r
                best_action = i + 1
        return best_action, best_reward

    def get_commit_action(self) -> int:
        """Return the commit action with highest expected reward."""
        action, _ = self.best_commit()
        return action
