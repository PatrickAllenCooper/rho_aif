"""
Position-aware VFE agent for navigation environments.

Extends VFEAgent to handle position-dependent observation models: for each
movement action, computes the observation model at the resulting position
and evaluates EFE accordingly. The agent reasons about WHERE to move to
maximally reduce uncertainty about the hidden goal location.
"""

import numpy as np
from scipy.stats import entropy as scipy_entropy
from typing import List, Tuple
from agents.base import BaseAgent


class NavigationVFEAgent(BaseAgent):
    """
    VFE agent for grid navigation with hidden goal.

    All actions are movement (non-terminal). The episode ends when the agent
    enters the goal cell (determined by the environment, not by a commit action).
    The agent evaluates EFE for each movement direction by computing the
    observation model at the resulting position.
    """

    def __init__(
        self,
        env,
        planning_horizon: int = 3,
    ):
        self.nav_env = env
        self.grid_size = env.grid_size
        self.num_cells = env.num_cells
        self.num_states = self.num_cells
        self.step_cost = env.step_cost
        self.goal_reward = env.goal_reward
        self.planning_horizon = planning_horizon
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

    def select_action(self) -> int:
        best_action, _ = self._evaluate(
            self.belief.belief,
            self.nav_env._agent_pos,
            depth=0,
        )
        return best_action

    def _resulting_pos(self, action: int):
        from environments.navigation import _DELTAS
        pos = self.nav_env._agent_pos
        dr, dc = _DELTAS[action]
        return self.nav_env._clamp((pos[0] + dr, pos[1] + dc))

    def _evaluate(self, belief: np.ndarray, agent_pos: Tuple[int, int], depth: int):
        """Recursively evaluate EFE for all movement actions."""
        if depth >= self.planning_horizon:
            return self._best_move_heuristic(belief, agent_pos)

        best_action = 0
        best_g = float("inf")

        from environments.navigation import _DELTAS
        for action in range(4):
            dr, dc = _DELTAS[action]
            new_pos = self.nav_env._clamp((agent_pos[0] + dr, agent_pos[1] + dc))

            if new_pos == agent_pos:
                continue

            g = self._efe_move(belief, new_pos, depth)
            if g < best_g:
                best_g = g
                best_action = action

        return best_action, best_g

    def _efe_move(self, belief: np.ndarray, new_pos: Tuple[int, int], depth: int) -> float:
        goal_idx = self.nav_env._pos_to_idx(new_pos)
        p_found = belief[goal_idx]

        g_found = -(self.goal_reward - self.step_cost)

        if p_found > 1.0 - 1e-10:
            return self.step_cost + g_found

        model = self.nav_env.get_observation_model_at(new_pos)
        belief_not_here = belief.copy()
        belief_not_here[goal_idx] = 0.0
        norm = belief_not_here.sum()
        if norm > 1e-10:
            belief_not_here /= norm
        else:
            belief_not_here = np.ones(self.num_states) / self.num_states

        prior_entropy = scipy_entropy(belief_not_here, base=2)
        expected_posterior_entropy = 0.0
        expected_continuation = 0.0
        num_obs_outcomes = model.shape[1]

        for obs_idx in range(num_obs_outcomes):
            prob_obs = float(np.dot(belief_not_here, model[:, obs_idx]))
            if prob_obs < 1e-10:
                continue
            posterior = model[:, obs_idx] * belief_not_here
            posterior = posterior / posterior.sum()
            expected_posterior_entropy += prob_obs * scipy_entropy(posterior, base=2)
            _, cont_g = self._evaluate(posterior, new_pos, depth + 1)
            expected_continuation += prob_obs * cont_g

        info_gain = prior_entropy - expected_posterior_entropy
        g_not_found = self.step_cost - info_gain + expected_continuation

        return p_found * g_found + (1.0 - p_found) * g_not_found

    def _best_move_heuristic(self, belief: np.ndarray, agent_pos: Tuple[int, int]):
        """At the planning horizon, move toward the highest-belief cell."""
        best_idx = int(np.argmax(belief))
        target = self.nav_env._idx_to_pos(best_idx)

        dr = target[0] - agent_pos[0]
        dc = target[1] - agent_pos[1]

        if abs(dr) >= abs(dc):
            action = 1 if dr > 0 else 0  # DOWN or UP
        else:
            action = 3 if dc > 0 else 2  # RIGHT or LEFT

        g = self.step_cost - scipy_entropy(belief, base=2) * 0.1
        return action, g
