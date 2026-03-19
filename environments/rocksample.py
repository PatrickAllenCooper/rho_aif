"""
RockSample environment: interleaved observe-act POMDP with state transitions.

A standard POMDP benchmark that directly addresses the observe-then-commit
limitation. The agent moves on an NxM grid with K rocks at known locations.
Each rock has a hidden binary quality (good/bad). The agent can:
  - Move {N,S,E,W}: changes position (state transition)
  - Check(k): noisy observation of rock k's quality (accuracy decays with distance)
  - Sample: collect rock at current position (good=+10, bad=-10)
  - Exit: move off the right edge for +10 terminal reward

This implements RockSample[N,K] following Smith and Simmons (2004).
"""

import gymnasium as gym
from gymnasium import spaces
import numpy as np
from typing import Tuple, List, Optional


class RockSampleEnv(gym.Env):
    """
    RockSample[grid_size, num_rocks] environment.

    State: agent position (known) + rock qualities (hidden binary vector).
    Actions: move(4) + check(K) + sample(1) + exit(1) = K + 6.
    Observation: {good, bad, null} for check actions; null otherwise.

    The agent's position is fully observable; only rock qualities are hidden.
    """

    MOVE_N, MOVE_S, MOVE_E, MOVE_W = 0, 1, 2, 3
    NUM_MOVE_ACTIONS = 4

    def __init__(
        self,
        grid_size: int = 5,
        num_rocks: int = 3,
        check_base_accuracy: float = 0.95,
        half_efficiency_distance: float = 4.0,
        good_rock_reward: float = 10.0,
        bad_rock_penalty: float = -10.0,
        exit_reward: float = 10.0,
        move_cost: float = 0.0,
        max_steps: int = 100,
        rock_positions: Optional[List[Tuple[int, int]]] = None,
    ):
        super().__init__()
        self.grid_size = grid_size
        self.num_rocks = num_rocks
        self.check_base_accuracy = check_base_accuracy
        self.half_efficiency_distance = half_efficiency_distance
        self.good_rock_reward = good_rock_reward
        self.bad_rock_penalty = bad_rock_penalty
        self.exit_reward = exit_reward
        self.move_cost = move_cost
        self.max_steps = max_steps

        self.num_check_actions = num_rocks
        self.num_actions = self.NUM_MOVE_ACTIONS + num_rocks + 2

        self.action_space = spaces.Discrete(self.num_actions)
        self.observation_space = spaces.Discrete(3)

        self._rock_positions = rock_positions
        self._agent_pos = (0, 0)
        self._rock_qualities = np.zeros(num_rocks, dtype=int)
        self._rock_sampled = np.zeros(num_rocks, dtype=bool)
        self._step_count = 0

    @property
    def sample_action(self):
        return self.NUM_MOVE_ACTIONS + self.num_rocks

    @property
    def exit_action(self):
        return self.NUM_MOVE_ACTIONS + self.num_rocks + 1

    def _generate_rock_positions(self):
        if self._rock_positions is not None:
            return list(self._rock_positions)
        positions = set()
        while len(positions) < self.num_rocks:
            r = self.np_random.integers(0, self.grid_size)
            c = self.np_random.integers(0, self.grid_size)
            positions.add((r, c))
        return list(positions)

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self._agent_pos = (self.grid_size // 2, 0)
        self._rock_pos_list = self._generate_rock_positions()
        self._rock_qualities = self.np_random.integers(0, 2, size=self.num_rocks)
        self._rock_sampled = np.zeros(self.num_rocks, dtype=bool)
        self._step_count = 0

        obs = 2  # null
        info = {
            "agent_pos": self._agent_pos,
            "rock_positions": self._rock_pos_list,
            "rock_qualities": self._rock_qualities.copy(),
        }
        return obs, info

    def step(self, action: int):
        self._step_count += 1
        reward = self.move_cost
        terminated = False
        truncated = self._step_count >= self.max_steps
        obs = 2  # null

        if action < self.NUM_MOVE_ACTIONS:
            self._agent_pos = self._apply_move(action)

        elif action < self.NUM_MOVE_ACTIONS + self.num_rocks:
            rock_idx = action - self.NUM_MOVE_ACTIONS
            obs = self._check_rock(rock_idx)

        elif action == self.sample_action:
            reward += self._sample_rock()

        elif action == self.exit_action:
            reward += self.exit_reward
            terminated = True

        info = {
            "agent_pos": self._agent_pos,
            "step": self._step_count,
        }

        if terminated or truncated:
            info["total_good_sampled"] = int(
                np.sum(self._rock_sampled & (self._rock_qualities == 1))
            )
            info["total_bad_sampled"] = int(
                np.sum(self._rock_sampled & (self._rock_qualities == 0))
            )

        return obs, reward, terminated, truncated, info

    def _apply_move(self, action: int) -> Tuple[int, int]:
        r, c = self._agent_pos
        if action == self.MOVE_N:
            r = max(0, r - 1)
        elif action == self.MOVE_S:
            r = min(self.grid_size - 1, r + 1)
        elif action == self.MOVE_E:
            c = min(self.grid_size - 1, c + 1)
        elif action == self.MOVE_W:
            c = max(0, c - 1)
        return (r, c)

    def _check_rock(self, rock_idx: int) -> int:
        """Return noisy observation of rock quality. Accuracy decays with distance."""
        rock_pos = self._rock_pos_list[rock_idx]
        dist = np.sqrt(
            (self._agent_pos[0] - rock_pos[0]) ** 2
            + (self._agent_pos[1] - rock_pos[1]) ** 2
        )

        accuracy = self.check_base_accuracy * (
            0.5 ** (dist / self.half_efficiency_distance)
        )
        accuracy = max(0.5, min(accuracy, self.check_base_accuracy))

        true_quality = self._rock_qualities[rock_idx]
        if self.np_random.random() < accuracy:
            return true_quality  # 0=bad, 1=good (correct)
        else:
            return 1 - true_quality  # incorrect

    def _sample_rock(self) -> float:
        """Sample rock at current position. Returns reward."""
        for k in range(self.num_rocks):
            rp = self._rock_pos_list[k]
            if rp == self._agent_pos and not self._rock_sampled[k]:
                self._rock_sampled[k] = True
                if self._rock_qualities[k] == 1:
                    return self.good_rock_reward
                else:
                    return self.bad_rock_penalty
        return 0.0

    def get_rock_positions(self) -> List[Tuple[int, int]]:
        return list(self._rock_pos_list)

    def get_check_accuracy_at(self, agent_pos: Tuple[int, int], rock_idx: int) -> float:
        """Compute check accuracy for a rock from a given position."""
        rock_pos = self._rock_pos_list[rock_idx]
        dist = np.sqrt(
            (agent_pos[0] - rock_pos[0]) ** 2
            + (agent_pos[1] - rock_pos[1]) ** 2
        )
        accuracy = self.check_base_accuracy * (
            0.5 ** (dist / self.half_efficiency_distance)
        )
        return max(0.5, min(accuracy, self.check_base_accuracy))
