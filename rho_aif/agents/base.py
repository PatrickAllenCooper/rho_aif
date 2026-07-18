"""
Base agent class for discrete POMDP agents with belief tracking.

Supports multiple observation actions, each with its own observation model
and cost, alongside multiple commit (terminal) actions.

Action layout: actions 0..K-1 are observation actions, K..K+N-1 are commit actions.
"""

import numpy as np
from typing import List, Union
from rho_aif.belief import BeliefState


class BaseAgent:
    """
    Base class providing belief management for POMDP agents.

    Subclasses must implement select_action().
    """

    def __init__(self, observation_models: Union[np.ndarray, List[np.ndarray]], env_config: dict):
        """
        Args:
            observation_models: Either a single P(obs|state) matrix (backward compat)
                or a list of such matrices, one per observation action.
            env_config: Dict with keys:
                - 'observation_costs': list of floats (or single float for backward compat)
                - 'commit_reward_matrix': shape (num_commit_actions, num_states)
        """
        if isinstance(observation_models, np.ndarray) and observation_models.ndim == 2:
            observation_models = [observation_models]

        self.obs_models: List[np.ndarray] = observation_models
        self.num_observe_actions = len(self.obs_models)
        self.num_states = self.obs_models[0].shape[0]
        self.num_obs = self.obs_models[0].shape[1]

        self.config = env_config
        costs = env_config.get("observation_costs", env_config.get("observation_cost", 0.0))
        if isinstance(costs, (int, float)):
            self.obs_costs = [float(costs)] * self.num_observe_actions
        else:
            self.obs_costs = [float(c) for c in costs]

        self.commit_rewards = env_config["commit_reward_matrix"]
        self.num_commit_actions = self.commit_rewards.shape[0]
        self.belief = BeliefState(self.num_states)

        self._active_obs_model_idx = 0

    def reset(self) -> None:
        self.belief.reset()

    def update_belief(self, observation: int, obs_action: int = 0) -> None:
        """Update belief given an observation from a specific observation action."""
        model_idx = obs_action if obs_action < self.num_observe_actions else 0
        self.belief.update(observation, self.obs_models[model_idx])

    def select_action(self) -> int:
        raise NotImplementedError

    def expected_reward_of_commit(self) -> float:
        _, best_reward = self.best_commit()
        return best_reward

    def best_commit(self):
        """Return (action_index, expected_reward) for the best commit action."""
        best_action = self.num_observe_actions
        best_reward = -float("inf")
        for i in range(self.num_commit_actions):
            r = float(np.dot(self.belief.belief, self.commit_rewards[i]))
            if r > best_reward:
                best_reward = r
                best_action = self.num_observe_actions + i
        return best_action, best_reward

    def _best_commit_from_belief(self, belief: np.ndarray):
        """Return (action_index, expected_reward) for the best commit at a given belief."""
        best_action = self.num_observe_actions
        best_reward = -float("inf")
        for i in range(self.num_commit_actions):
            r = float(np.dot(belief, self.commit_rewards[i]))
            if r > best_reward:
                best_reward = r
                best_action = self.num_observe_actions + i
        return best_action, best_reward

    def get_commit_action(self) -> int:
        action, _ = self.best_commit()
        return action
