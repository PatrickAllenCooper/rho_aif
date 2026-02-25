"""
Classic Tiger Problem as a Gymnasium environment.

The Tiger problem (Kaelbling et al., 1998) is a canonical POMDP benchmark.
An agent faces two doors; behind one is a tiger (large penalty), behind
the other is a reward. The agent can listen (noisy observation about
the tiger's location at a small cost) or open a door (ending the episode).

The extreme reward asymmetry (+10 vs -100) makes information gathering
critical and amplifies behavioral differences between agents with
different epistemic strategies.
"""

import gymnasium as gym
from gymnasium import spaces
import numpy as np
from typing import Optional, Tuple, Dict, Any


LISTEN = 0
OPEN_LEFT = 1
OPEN_RIGHT = 2

HEAR_LEFT = 0
HEAR_RIGHT = 1
NULL_OBS = 2

TIGER_LEFT = 0
TIGER_RIGHT = 1


class TigerEnv(gym.Env):
    """
    Tiger Problem POMDP environment.

    Observation space: Discrete(3) -- HEAR_LEFT, HEAR_RIGHT, NULL_OBS
    Action space: Discrete(3) -- LISTEN, OPEN_LEFT, OPEN_RIGHT
    """

    metadata = {"render_modes": []}

    def __init__(
        self,
        listen_accuracy: float = 0.85,
        listen_cost: float = 1.0,
        correct_reward: float = 10.0,
        incorrect_penalty: float = -100.0,
    ):
        super().__init__()

        self.listen_accuracy = listen_accuracy
        self.listen_cost = listen_cost
        self.correct_reward = correct_reward
        self.incorrect_penalty = incorrect_penalty

        self.action_space = spaces.Discrete(3)
        self.observation_space = spaces.Discrete(3)

        self._tiger_location: Optional[int] = None
        self._listen_count = 0

    @property
    def observation_accuracy(self) -> float:
        return self.listen_accuracy

    @property
    def observation_cost(self) -> float:
        return self.listen_cost

    def get_observation_model(self) -> np.ndarray:
        """
        P(obs | state) matrix, shape (2, 2).

        Rows = tiger location (LEFT, RIGHT).
        Columns = heard signal (HEAR_LEFT, HEAR_RIGHT).
        """
        acc = self.listen_accuracy
        return np.array([
            [acc, 1.0 - acc],
            [1.0 - acc, acc],
        ])

    def get_commit_reward_matrix(self) -> np.ndarray:
        """
        Reward for each (commit_action_index, tiger_location) pair.

        Shape (num_commit_actions, num_states).
        commit_action_index 0 = OPEN_LEFT, 1 = OPEN_RIGHT.
        Opening a door gives correct_reward if tiger is behind the OTHER door,
        and incorrect_penalty if tiger is behind THIS door.
        """
        return np.array([
            [self.incorrect_penalty, self.correct_reward],
            [self.correct_reward, self.incorrect_penalty],
        ])

    def reset(
        self, *, seed: Optional[int] = None, options: Optional[Dict[str, Any]] = None
    ) -> Tuple[int, Dict[str, Any]]:
        super().reset(seed=seed)
        self._tiger_location = self.np_random.choice([TIGER_LEFT, TIGER_RIGHT])
        self._listen_count = 0
        return NULL_OBS, {"tiger_location": self._tiger_location}

    def step(self, action: int) -> Tuple[int, float, bool, bool, Dict[str, Any]]:
        if action == LISTEN:
            obs = self._generate_observation()
            self._listen_count += 1
            info = {
                "tiger_location": self._tiger_location,
                "listen_count": self._listen_count,
            }
            return obs, -self.listen_cost, False, False, info

        opened_door = TIGER_LEFT if action == OPEN_LEFT else TIGER_RIGHT
        tiger_behind_opened = opened_door == self._tiger_location
        reward = self.incorrect_penalty if tiger_behind_opened else self.correct_reward

        info = {
            "tiger_location": self._tiger_location,
            "listen_count": self._listen_count,
            "opened_door": opened_door,
            "correct": not tiger_behind_opened,
            "total_reward": reward - self.listen_cost * self._listen_count,
        }
        return NULL_OBS, reward, True, False, info

    def _generate_observation(self) -> int:
        if self.np_random.random() < self.listen_accuracy:
            return HEAR_LEFT if self._tiger_location == TIGER_LEFT else HEAR_RIGHT
        else:
            return HEAR_RIGHT if self._tiger_location == TIGER_LEFT else HEAR_LEFT
