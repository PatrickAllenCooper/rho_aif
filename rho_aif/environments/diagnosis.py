"""
Sequential Diagnosis environment as a Gymnasium env.

Generalizes the Tiger problem to N conditions and K diagnostic tests.
Each test provides noisy information about a specific partition of the
state space, enabling hierarchical disambiguation. Directly supports
scaling analysis from N=2 (equivalent to Tiger) to N=16+.
"""

import gymnasium as gym
from gymnasium import spaces
import numpy as np
from typing import Optional, Tuple, Dict, Any, List
import math


NULL_OBS = -1


class DiagnosisEnv(gym.Env):
    """
    N-condition sequential diagnosis POMDP.

    The world has one of N hidden conditions. The agent can run K diagnostic
    tests (each with its own accuracy and cost) or commit to a diagnosis.

    Action layout:
      0..K-1   = run test k (observation action)
      K..K+N-1 = diagnose condition i (commit action)

    Each test k partitions the N conditions into two groups and returns a
    noisy binary signal indicating which group the true condition belongs to.
    Test k distinguishes conditions at the k-th level of a binary tree over
    the state space, so K = ceil(log2(N)) tests suffice for full disambiguation.
    """

    metadata = {"render_modes": []}

    def __init__(
        self,
        num_conditions: int = 4,
        test_accuracy: float = 0.80,
        test_cost: float = 1.0,
        correct_reward: float = 10.0,
        incorrect_penalty: float = -50.0,
        num_tests: Optional[int] = None,
        test_costs: Optional[List[float]] = None,
    ):
        super().__init__()

        self.num_conditions = num_conditions
        self.test_accuracy = test_accuracy
        self.test_cost = test_cost
        self.correct_reward = correct_reward
        self.incorrect_penalty = incorrect_penalty
        self.num_tests = num_tests or max(1, math.ceil(math.log2(num_conditions)))
        if test_costs is not None:
            if len(test_costs) != self.num_tests:
                raise ValueError(
                    f"test_costs must have length {self.num_tests}, got {len(test_costs)}"
                )
            self.test_costs = [float(c) for c in test_costs]
        else:
            self.test_costs = [float(test_cost)] * self.num_tests

        self.action_space = spaces.Discrete(self.num_tests + self.num_conditions)
        self.observation_space = spaces.Discrete(3)  # 0=group_A, 1=group_B, 2=null

        self._true_condition: Optional[int] = None
        self._test_count = 0
        self._cost_paid = 0.0
        self._obs_models = self._build_observation_models()

    @property
    def observation_cost(self) -> float:
        return self.test_cost

    @property
    def observation_accuracy(self) -> float:
        return self.test_accuracy

    def _build_observation_models(self) -> List[np.ndarray]:
        """
        Build one observation model per test. Test k partitions conditions
        using bit k of the condition index: conditions with bit k = 0 go to
        group A, bit k = 1 go to group B. The test returns a noisy signal
        indicating the group.
        """
        models = []
        acc = self.test_accuracy
        for k in range(self.num_tests):
            model = np.zeros((self.num_conditions, 2))
            for cond in range(self.num_conditions):
                bit = (cond >> k) & 1
                if bit == 0:
                    model[cond] = [acc, 1.0 - acc]
                else:
                    model[cond] = [1.0 - acc, acc]
            models.append(model)
        return models

    def get_observation_models(self) -> List[np.ndarray]:
        return list(self._obs_models)

    def get_observation_model(self) -> np.ndarray:
        return self._obs_models[0]

    def get_observation_costs(self) -> List[float]:
        return list(self.test_costs)

    def get_commit_reward_matrix(self) -> np.ndarray:
        """
        Shape (num_conditions, num_conditions). Row i = diagnose condition i.
        R[i, j] = correct_reward if i == j, else incorrect_penalty.
        """
        mat = np.full((self.num_conditions, self.num_conditions), self.incorrect_penalty)
        np.fill_diagonal(mat, self.correct_reward)
        return mat

    def reset(
        self, *, seed: Optional[int] = None, options: Optional[Dict[str, Any]] = None
    ) -> Tuple[int, Dict[str, Any]]:
        super().reset(seed=seed)
        self._true_condition = int(self.np_random.integers(0, self.num_conditions))
        self._test_count = 0
        self._cost_paid = 0.0
        return 2, {"true_condition": self._true_condition}  # 2 = null obs

    def step(self, action: int) -> Tuple[int, float, bool, bool, Dict[str, Any]]:
        if action < self.num_tests:
            obs = self._run_test(action)
            self._test_count += 1
            cost = self.test_costs[action]
            self._cost_paid += cost
            info = {
                "true_condition": self._true_condition,
                "test_index": action,
                "test_count": self._test_count,
                "test_cost_paid": self._cost_paid,
            }
            return obs, -cost, False, False, info

        diagnosed = action - self.num_tests
        correct = diagnosed == self._true_condition
        reward = self.correct_reward if correct else self.incorrect_penalty
        info = {
            "true_condition": self._true_condition,
            "diagnosed": diagnosed,
            "correct": correct,
            "test_count": self._test_count,
            "total_reward": reward - self._cost_paid,
        }
        return 2, reward, True, False, info

    def _run_test(self, test_idx: int) -> int:
        bit = (self._true_condition >> test_idx) & 1
        if self.np_random.random() < self.test_accuracy:
            return bit
        return 1 - bit
