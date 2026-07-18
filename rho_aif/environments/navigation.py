"""
Partially Observable Navigation as a Gymnasium env.

Small grid world with a hidden goal location. The agent knows its own
position and receives proximity-based observations after each move.
Tests spatial information gathering: the agent must decide WHERE to
move to learn the most about the goal's location.
"""

import gymnasium as gym
from gymnasium import spaces
import numpy as np
from typing import Optional, Tuple, Dict, Any, List


MOVE_UP = 0
MOVE_DOWN = 1
MOVE_LEFT = 2
MOVE_RIGHT = 3

_DELTAS = {
    MOVE_UP: (-1, 0),
    MOVE_DOWN: (1, 0),
    MOVE_LEFT: (0, -1),
    MOVE_RIGHT: (0, 1),
}


class NavigationEnv(gym.Env):
    """
    Grid navigation POMDP with hidden goal.

    Hidden state: goal cell index (grid_size^2 possible states).
    Agent state: current position (known, tracked internally).

    Actions: move up/down/left/right (4 actions).
    Observations: proximity signal after each move. Closer to goal = higher
    probability of a "warm" signal. Discrete: {cold=0, warm=1, found=2, null=3}.
    Episode ends when agent enters the goal cell or exceeds max_steps.
    """

    metadata = {"render_modes": []}

    def __init__(
        self,
        grid_size: int = 4,
        base_accuracy: float = 0.55,
        proximity_bonus: float = 0.35,
        step_cost: float = 0.5,
        goal_reward: float = 20.0,
        max_steps: int = 30,
    ):
        super().__init__()

        self.grid_size = grid_size
        self.num_cells = grid_size * grid_size
        self.base_accuracy = base_accuracy
        self.proximity_bonus = proximity_bonus
        self.step_cost = step_cost
        self.goal_reward = goal_reward
        self.max_steps = max_steps

        self.action_space = spaces.Discrete(4)
        self.observation_space = spaces.Discrete(4)  # cold, warm, found, null

        self._goal_pos: Optional[Tuple[int, int]] = None
        self._agent_pos: Optional[Tuple[int, int]] = None
        self._steps = 0

    @property
    def observation_cost(self) -> float:
        return self.step_cost

    @property
    def observation_accuracy(self) -> float:
        return self.base_accuracy

    @property
    def correct_reward(self) -> float:
        return self.goal_reward

    @property
    def incorrect_penalty(self) -> float:
        return -self.step_cost * self.max_steps

    def _pos_to_idx(self, pos: Tuple[int, int]) -> int:
        return pos[0] * self.grid_size + pos[1]

    def _idx_to_pos(self, idx: int) -> Tuple[int, int]:
        return (idx // self.grid_size, idx % self.grid_size)

    def _manhattan(self, p1: Tuple[int, int], p2: Tuple[int, int]) -> int:
        return abs(p1[0] - p2[0]) + abs(p1[1] - p2[1])

    def _clamp(self, pos: Tuple[int, int]) -> Tuple[int, int]:
        return (
            max(0, min(self.grid_size - 1, pos[0])),
            max(0, min(self.grid_size - 1, pos[1])),
        )

    def _warm_prob(self, agent_pos: Tuple[int, int], goal_pos: Tuple[int, int]) -> float:
        dist = self._manhattan(agent_pos, goal_pos)
        if dist == 0:
            return 1.0
        max_dist = 2 * (self.grid_size - 1)
        return self.base_accuracy + self.proximity_bonus * (1.0 - dist / max_dist)

    def get_observation_model_at(self, agent_pos: Tuple[int, int]) -> np.ndarray:
        """
        P(obs | goal_location) for a given agent position.
        Shape (num_cells, 2). Columns: [cold, warm].
        """
        model = np.zeros((self.num_cells, 2))
        for goal_idx in range(self.num_cells):
            goal_pos = self._idx_to_pos(goal_idx)
            if agent_pos == goal_pos:
                model[goal_idx] = [0.0, 1.0]
            else:
                pw = self._warm_prob(agent_pos, goal_pos)
                model[goal_idx] = [1.0 - pw, pw]
        return model

    def get_observation_models(self) -> List[np.ndarray]:
        """One model per action, based on the resulting position."""
        models = []
        if self._agent_pos is None:
            center = (self.grid_size // 2, self.grid_size // 2)
        else:
            center = self._agent_pos
        for action in range(4):
            dr, dc = _DELTAS[action]
            new_pos = self._clamp((center[0] + dr, center[1] + dc))
            models.append(self.get_observation_model_at(new_pos))
        return models

    def get_observation_model(self) -> np.ndarray:
        pos = self._agent_pos or (self.grid_size // 2, self.grid_size // 2)
        return self.get_observation_model_at(pos)

    def get_observation_costs(self) -> List[float]:
        return [self.step_cost] * 4

    def get_commit_reward_matrix(self) -> np.ndarray:
        """
        No explicit commit actions in navigation -- the episode ends when
        the agent enters the goal cell. We encode this as a dummy matrix
        with zero commit actions so agents never commit explicitly.
        """
        return np.zeros((0, self.num_cells))

    def reset(
        self, *, seed: Optional[int] = None, options: Optional[Dict[str, Any]] = None
    ) -> Tuple[int, Dict[str, Any]]:
        super().reset(seed=seed)
        self._goal_pos = self._idx_to_pos(int(self.np_random.integers(0, self.num_cells)))
        self._agent_pos = (0, 0)
        self._steps = 0
        return 3, {  # 3 = null obs
            "goal_pos": self._goal_pos,
            "agent_pos": self._agent_pos,
        }

    def step(self, action: int) -> Tuple[int, float, bool, bool, Dict[str, Any]]:
        dr, dc = _DELTAS[action]
        self._agent_pos = self._clamp(
            (self._agent_pos[0] + dr, self._agent_pos[1] + dc)
        )
        self._steps += 1

        if self._agent_pos == self._goal_pos:
            info = {
                "goal_pos": self._goal_pos,
                "agent_pos": self._agent_pos,
                "steps": self._steps,
                "correct": True,
            }
            return 2, self.goal_reward, True, False, info  # 2 = found

        pw = self._warm_prob(self._agent_pos, self._goal_pos)
        obs = 1 if self.np_random.random() < pw else 0

        truncated = self._steps >= self.max_steps
        info = {
            "goal_pos": self._goal_pos,
            "agent_pos": self._agent_pos,
            "steps": self._steps,
        }
        if truncated:
            info["correct"] = False

        return obs, -self.step_cost, False, truncated, info
