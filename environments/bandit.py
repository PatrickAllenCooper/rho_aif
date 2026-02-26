"""
Multi-Armed Bandit with Hidden Structure as a Gymnasium env.

K arms, one of which is the best. The agent can inspect arms (noisy signal
about whether an arm is the best) or pull an arm (receive reward, episode ends).
Tests whether VFE produces better exploration when the agent must choose
WHICH information to gather, not just WHETHER to gather.
"""

import gymnasium as gym
from gymnasium import spaces
import numpy as np
from typing import Optional, Tuple, Dict, Any, List


class BanditEnv(gym.Env):
    """
    Structured multi-armed bandit POMDP.

    Hidden state: which arm is the best (K possible states).

    Action layout:
      0..K-1   = inspect arm k (observation action, noisy binary signal)
      K..2K-1  = pull arm k (commit action, terminal)

    Inspecting arm k returns a noisy signal about whether k is the best arm.
    Pulling the best arm gives correct_reward; pulling any other gives small_reward.
    """

    metadata = {"render_modes": []}

    def __init__(
        self,
        num_arms: int = 4,
        inspect_accuracy: float = 0.80,
        inspect_cost: float = 0.5,
        correct_reward: float = 10.0,
        small_reward: float = 1.0,
    ):
        super().__init__()

        self.num_arms = num_arms
        self.inspect_accuracy = inspect_accuracy
        self.inspect_cost = inspect_cost
        self.correct_reward = correct_reward
        self.small_reward = small_reward

        self.action_space = spaces.Discrete(2 * num_arms)
        self.observation_space = spaces.Discrete(3)  # 0=no, 1=yes, 2=null

        self._best_arm: Optional[int] = None
        self._inspect_count = 0

    @property
    def observation_cost(self) -> float:
        return self.inspect_cost

    @property
    def observation_accuracy(self) -> float:
        return self.inspect_accuracy

    @property
    def incorrect_penalty(self) -> float:
        return self.small_reward

    def get_observation_models(self) -> List[np.ndarray]:
        """
        One model per arm. For arm k, the model returns:
        - P(signal=yes | best=k) = accuracy (true positive)
        - P(signal=yes | best!=k) = 1-accuracy (false positive)
        """
        models = []
        acc = self.inspect_accuracy
        for k in range(self.num_arms):
            model = np.zeros((self.num_arms, 2))
            for state in range(self.num_arms):
                if state == k:
                    model[state] = [1.0 - acc, acc]  # [no, yes]
                else:
                    model[state] = [acc, 1.0 - acc]
            models.append(model)
        return models

    def get_observation_model(self) -> np.ndarray:
        return self.get_observation_models()[0]

    def get_observation_costs(self) -> List[float]:
        return [self.inspect_cost] * self.num_arms

    def get_commit_reward_matrix(self) -> np.ndarray:
        """
        Shape (num_arms, num_arms). Row k = pull arm k.
        R[k, best] = correct_reward if k == best, else small_reward.
        """
        mat = np.full((self.num_arms, self.num_arms), self.small_reward)
        np.fill_diagonal(mat, self.correct_reward)
        return mat

    def reset(
        self, *, seed: Optional[int] = None, options: Optional[Dict[str, Any]] = None
    ) -> Tuple[int, Dict[str, Any]]:
        super().reset(seed=seed)
        self._best_arm = int(self.np_random.integers(0, self.num_arms))
        self._inspect_count = 0
        return 2, {"best_arm": self._best_arm}  # 2 = null obs

    def step(self, action: int) -> Tuple[int, float, bool, bool, Dict[str, Any]]:
        if action < self.num_arms:
            obs = self._inspect(action)
            self._inspect_count += 1
            info = {
                "best_arm": self._best_arm,
                "inspected_arm": action,
                "inspect_count": self._inspect_count,
            }
            return obs, -self.inspect_cost, False, False, info

        pulled = action - self.num_arms
        correct = pulled == self._best_arm
        reward = self.correct_reward if correct else self.small_reward
        info = {
            "best_arm": self._best_arm,
            "pulled_arm": pulled,
            "correct": correct,
            "inspect_count": self._inspect_count,
            "total_reward": reward - self.inspect_cost * self._inspect_count,
        }
        return 2, reward, True, False, info

    def _inspect(self, arm: int) -> int:
        is_best = arm == self._best_arm
        if self.np_random.random() < self.inspect_accuracy:
            return 1 if is_best else 0
        return 0 if is_best else 1
