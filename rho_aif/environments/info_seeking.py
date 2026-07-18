"""
Two-state information-seeking environment as a Gymnasium env.

A minimal POMDP testbed: two hidden states, noisy observations, and a
commit-or-observe decision structure that isolates epistemic foraging behavior.
"""

import gymnasium as gym
from gymnasium import spaces
import numpy as np
from typing import Optional, Tuple, Dict, Any


OBSERVE = 0
COMMIT_A = 1
COMMIT_B = 2

SIGNAL_A = 0
SIGNAL_B = 1
NULL_OBS = 2

STATE_A = 0
STATE_B = 1


class InfoSeekingEnv(gym.Env):
    """
    Two-state partially observable environment for epistemic foraging.

    The agent must determine which of two hidden states the world is in.
    It can pay a cost to observe (receiving a noisy signal) or commit to
    a guess, ending the episode with reward or penalty.

    Observation space: Discrete(3) -- SIGNAL_A, SIGNAL_B, NULL_OBS
    Action space: Discrete(3) -- OBSERVE, COMMIT_A, COMMIT_B
    """

    metadata = {"render_modes": []}

    def __init__(
        self,
        observation_accuracy: float = 0.75,
        observation_cost: float = 0.1,
        correct_reward: float = 1.0,
        incorrect_penalty: float = -1.0,
    ):
        super().__init__()

        self.observation_accuracy = observation_accuracy
        self.observation_cost = observation_cost
        self.correct_reward = correct_reward
        self.incorrect_penalty = incorrect_penalty

        self.action_space = spaces.Discrete(3)
        self.observation_space = spaces.Discrete(3)

        self._true_state: Optional[int] = None
        self._observation_count = 0
        self._total_reward = 0.0

    def get_observation_model(self) -> np.ndarray:
        """Single observation model (backward compat)."""
        acc = self.observation_accuracy
        return np.array([
            [acc, 1.0 - acc],
            [1.0 - acc, acc],
        ])

    def get_observation_models(self):
        return [self.get_observation_model()]

    def get_observation_costs(self):
        return [self.observation_cost]

    def get_commit_reward_matrix(self) -> np.ndarray:
        """
        Reward for each (commit_action_index, true_state) pair.

        Shape (num_commit_actions, num_states).
        commit_action_index 0 = COMMIT_A, 1 = COMMIT_B.
        COMMIT_A is correct when true state is A (index 0).
        """
        return np.array([
            [self.correct_reward, self.incorrect_penalty],
            [self.incorrect_penalty, self.correct_reward],
        ])

    def reset(
        self, *, seed: Optional[int] = None, options: Optional[Dict[str, Any]] = None
    ) -> Tuple[int, Dict[str, Any]]:
        super().reset(seed=seed)
        self._true_state = self.np_random.choice([STATE_A, STATE_B])
        self._observation_count = 0
        self._total_reward = 0.0
        return NULL_OBS, {"true_state": self._true_state}

    def step(self, action: int) -> Tuple[int, float, bool, bool, Dict[str, Any]]:
        if action == OBSERVE:
            obs = self._generate_observation()
            reward = -self.observation_cost
            self._observation_count += 1
            self._total_reward += reward
            info = {
                "true_state": self._true_state,
                "observation_count": self._observation_count,
            }
            return obs, reward, False, False, info

        committed_state = STATE_A if action == COMMIT_A else STATE_B
        correct = committed_state == self._true_state
        reward = self.correct_reward if correct else self.incorrect_penalty
        self._total_reward += reward
        info = {
            "true_state": self._true_state,
            "observation_count": self._observation_count,
            "committed_state": committed_state,
            "correct": correct,
            "total_reward": self._total_reward,
        }
        return NULL_OBS, reward, True, False, info

    def _generate_observation(self) -> int:
        if self.np_random.random() < self.observation_accuracy:
            return SIGNAL_A if self._true_state == STATE_A else SIGNAL_B
        else:
            return SIGNAL_B if self._true_state == STATE_A else SIGNAL_A
