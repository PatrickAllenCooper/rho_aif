"""
Baseline navigation agents for the partially observable grid world.

NavigationMyopicAgent: Moves toward the highest-belief cell (greedy, no
information seeking).

NavigationInfoGainAgent: Evaluates each movement for expected information
gain from the position-dependent observation model, weighted by
info_gain_weight, combined with proximity to high-belief cells.

Both share the same interface as NavigationEFEAgent for direct comparison.
"""

import numpy as np
from scipy.stats import entropy as scipy_entropy
from typing import Tuple
from agents.base import BaseAgent


class NavigationMyopicAgent(BaseAgent):
    """
    Greedy navigation agent: always moves toward the highest-belief cell.

    No information seeking -- purely exploits current belief to navigate
    toward the most likely goal location.
    """

    def __init__(self, env):
        self.nav_env = env
        self.grid_size = env.grid_size
        self.num_cells = env.num_cells
        self.num_states = self.num_cells
        self.step_cost = env.step_cost
        self.goal_reward = env.goal_reward
        self.num_observe_actions = 4
        self.num_commit_actions = 0

        from belief import BeliefState
        self.belief = BeliefState(self.num_states)
        self.config = {}
        self.obs_models = []
        self.obs_costs = [self.step_cost] * 4
        self.commit_rewards = np.zeros((0, self.num_states))

    def reset(self):
        self.belief.reset()

    def update_belief(self, observation: int, obs_action: int = 0):
        if observation >= 2:
            return
        new_pos = self._resulting_pos(obs_action)
        model = self.nav_env.get_observation_model_at(new_pos)
        self.belief.update(observation, model)

    def _resulting_pos(self, action: int):
        from environments.navigation import _DELTAS
        pos = self.nav_env._agent_pos
        dr, dc = _DELTAS[action]
        return self.nav_env._clamp((pos[0] + dr, pos[1] + dc))

    def select_action(self) -> int:
        best_idx = int(np.argmax(self.belief.belief))
        target = self.nav_env._idx_to_pos(best_idx)
        agent_pos = self.nav_env._agent_pos

        dr = target[0] - agent_pos[0]
        dc = target[1] - agent_pos[1]

        if dr == 0 and dc == 0:
            return 0

        if abs(dr) >= abs(dc):
            return 1 if dr > 0 else 0  # DOWN or UP
        else:
            return 3 if dc > 0 else 2  # RIGHT or LEFT


class NavigationInfoGainAgent(BaseAgent):
    """
    Navigation agent that balances proximity to high-belief cells with
    expected information gain from position-dependent observations.

    For each movement direction, evaluates:
      value(move) = expected_goal_reward(move) + weight * info_gain(move) - step_cost
    """

    def __init__(self, env, info_gain_weight: float = 1.0):
        self.nav_env = env
        self.grid_size = env.grid_size
        self.num_cells = env.num_cells
        self.num_states = self.num_cells
        self.step_cost = env.step_cost
        self.goal_reward = env.goal_reward
        self.info_gain_weight = info_gain_weight
        self.num_observe_actions = 4
        self.num_commit_actions = 0

        from belief import BeliefState
        self.belief = BeliefState(self.num_states)
        self.config = {}
        self.obs_models = []
        self.obs_costs = [self.step_cost] * 4
        self.commit_rewards = np.zeros((0, self.num_states))

    def reset(self):
        self.belief.reset()

    def update_belief(self, observation: int, obs_action: int = 0):
        if observation >= 2:
            return
        new_pos = self._resulting_pos(obs_action)
        model = self.nav_env.get_observation_model_at(new_pos)
        self.belief.update(observation, model)

    def _resulting_pos(self, action: int):
        from environments.navigation import _DELTAS
        pos = self.nav_env._agent_pos
        dr, dc = _DELTAS[action]
        return self.nav_env._clamp((pos[0] + dr, pos[1] + dc))

    def select_action(self) -> int:
        from environments.navigation import _DELTAS

        best_action = 0
        best_value = -float("inf")
        agent_pos = self.nav_env._agent_pos

        for action in range(4):
            dr, dc = _DELTAS[action]
            new_pos = self.nav_env._clamp((agent_pos[0] + dr, agent_pos[1] + dc))

            if new_pos == agent_pos:
                continue

            value = self._evaluate_move(new_pos)
            if value > best_value:
                best_value = value
                best_action = action

        return best_action

    def _evaluate_move(self, new_pos: Tuple[int, int]) -> float:
        goal_idx = self.nav_env._pos_to_idx(new_pos)
        p_found = self.belief.belief[goal_idx]

        goal_value = p_found * (self.goal_reward - self.step_cost)

        if p_found > 1.0 - 1e-10:
            return goal_value

        belief_not_here = self.belief.belief.copy()
        belief_not_here[goal_idx] = 0.0
        norm = belief_not_here.sum()
        if norm > 1e-10:
            belief_not_here /= norm
        else:
            belief_not_here = np.ones(self.num_states) / self.num_states

        model = self.nav_env.get_observation_model_at(new_pos)
        prior_entropy = scipy_entropy(belief_not_here, base=2)
        expected_posterior_entropy = 0.0
        num_obs_outcomes = model.shape[1]

        for obs_idx in range(num_obs_outcomes):
            prob_obs = float(np.dot(belief_not_here, model[:, obs_idx]))
            if prob_obs < 1e-10:
                continue
            posterior = model[:, obs_idx] * belief_not_here
            posterior = posterior / posterior.sum()
            expected_posterior_entropy += prob_obs * scipy_entropy(posterior, base=2)

        info_gain = prior_entropy - expected_posterior_entropy

        proximity_value = self._proximity_heuristic(new_pos)

        return goal_value + proximity_value + self.info_gain_weight * info_gain - self.step_cost

    def _proximity_heuristic(self, new_pos: Tuple[int, int]) -> float:
        """Weighted average inverse distance to high-belief cells."""
        value = 0.0
        for idx in range(self.num_states):
            cell_pos = self.nav_env._idx_to_pos(idx)
            dist = abs(new_pos[0] - cell_pos[0]) + abs(new_pos[1] - cell_pos[1])
            inv_dist = 1.0 / (1.0 + dist)
            value += self.belief.belief[idx] * inv_dist * self.goal_reward
        return value
