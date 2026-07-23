"""
Diagnosis environment with a reward-irrelevant nuisance factor.

Extends DiagnosisEnv with a second, binary hidden factor that has no effect
on reward: the commit reward depends only on the diagnostic condition, never
on the nuisance bit. One additional "distractor" test is informative only
about the nuisance bit and carries zero information about the condition.

This isolates a specific question (Stage G2 of the full-paper plan, added in
response to review feedback): information gain is reward-blind, so does an
EFE/Planning+IG agent spend sensing budget on a test that can never help it
choose the right commit action? The environment is built from the same
observation-model / commit-reward-matrix interface as DiagnosisEnv, so any
observe-then-commit agent (EFEAgent, PlanningAgent, PlanningInfoGainAgent,
IDSAgent) runs against it unmodified via rho_aif.benchmark.make_env_config /
get_obs_models / run_otc_episode.

State encoding: joint state s = condition * 2 + nuisance, condition in
[0, num_conditions), nuisance in {0, 1}. There are 2 * num_conditions joint
states, but only num_conditions commit actions (diagnosing a condition),
since the nuisance bit is never the target of a commit action.
"""

from __future__ import annotations

import math
from typing import Any, Dict, List, Optional, Tuple

import gymnasium as gym
import numpy as np
from gymnasium import spaces


class DistractorDiagnosisEnv(gym.Env):
    """N-condition diagnosis with one reward-irrelevant nuisance test."""

    metadata = {"render_modes": []}

    def __init__(
        self,
        num_conditions: int = 4,
        test_accuracy: float = 0.80,
        test_cost: float = 1.0,
        distractor_accuracy: float = 0.80,
        distractor_cost: Optional[float] = None,
        correct_reward: float = 10.0,
        incorrect_penalty: float = -50.0,
        num_tests: Optional[int] = None,
    ):
        super().__init__()

        self.num_conditions = num_conditions
        self.test_accuracy = test_accuracy
        self.test_cost = test_cost
        self.distractor_accuracy = distractor_accuracy
        self.distractor_cost = float(
            test_cost if distractor_cost is None else distractor_cost
        )
        self.correct_reward = correct_reward
        self.incorrect_penalty = incorrect_penalty
        self.num_condition_tests = num_tests or max(
            1, math.ceil(math.log2(num_conditions))
        )
        # +1 for the single distractor test, appended last.
        self.num_tests = self.num_condition_tests + 1
        self.distractor_test_idx = self.num_condition_tests
        self.test_costs = [float(test_cost)] * self.num_condition_tests + [
            self.distractor_cost
        ]

        self.num_states = 2 * self.num_conditions
        self.action_space = spaces.Discrete(self.num_tests + self.num_conditions)
        self.observation_space = spaces.Discrete(3)  # 0=group_A, 1=group_B, 2=null

        self._true_condition: Optional[int] = None
        self._true_nuisance: Optional[int] = None
        self._test_count = 0
        self._distractor_count = 0
        self._cost_paid = 0.0
        self._obs_models = self._build_observation_models()

    @property
    def observation_cost(self) -> float:
        return self.test_cost

    @staticmethod
    def state_index(condition: int, nuisance: int) -> int:
        return condition * 2 + nuisance

    def _build_observation_models(self) -> List[np.ndarray]:
        """
        One observation model per test, shape (num_states, 2).

        Condition tests partition on a bit of the condition index and are
        exactly uninformative about the nuisance bit (accuracy identical for
        both nuisance values). The distractor test partitions on the
        nuisance bit and is exactly uninformative about the condition
        (accuracy identical for every condition).
        """
        models = []
        acc = self.test_accuracy
        for k in range(self.num_condition_tests):
            model = np.zeros((self.num_states, 2))
            for cond in range(self.num_conditions):
                bit = (cond >> k) & 1
                row = [acc, 1.0 - acc] if bit == 0 else [1.0 - acc, acc]
                for nuisance in (0, 1):
                    model[self.state_index(cond, nuisance)] = row
            models.append(model)

        dist_model = np.zeros((self.num_states, 2))
        dacc = self.distractor_accuracy
        for nuisance in (0, 1):
            row = [dacc, 1.0 - dacc] if nuisance == 0 else [1.0 - dacc, dacc]
            for cond in range(self.num_conditions):
                dist_model[self.state_index(cond, nuisance)] = row
        models.append(dist_model)
        return models

    def get_observation_models(self) -> List[np.ndarray]:
        return list(self._obs_models)

    def get_observation_costs(self) -> List[float]:
        return list(self.test_costs)

    def get_commit_reward_matrix(self) -> np.ndarray:
        """
        Shape (num_conditions, num_states). Row i = diagnose condition i.
        Reward depends only on the condition component of the joint state:
        correct_reward if state's condition == i, else incorrect_penalty,
        for both nuisance values.
        """
        mat = np.full((self.num_conditions, self.num_states), self.incorrect_penalty)
        for cond in range(self.num_conditions):
            for nuisance in (0, 1):
                mat[cond, self.state_index(cond, nuisance)] = self.correct_reward
        return mat

    def reset(
        self, *, seed: Optional[int] = None, options: Optional[Dict[str, Any]] = None
    ) -> Tuple[int, Dict[str, Any]]:
        super().reset(seed=seed)
        self._true_condition = int(self.np_random.integers(0, self.num_conditions))
        self._true_nuisance = int(self.np_random.integers(0, 2))
        self._test_count = 0
        self._distractor_count = 0
        self._cost_paid = 0.0
        return 2, {
            "true_condition": self._true_condition,
            "true_nuisance": self._true_nuisance,
        }

    def step(self, action: int) -> Tuple[int, float, bool, bool, Dict[str, Any]]:
        if action < self.num_tests:
            is_distractor = action == self.distractor_test_idx
            obs = self._run_test(action, is_distractor)
            self._test_count += 1
            if is_distractor:
                self._distractor_count += 1
            cost = self.test_costs[action]
            self._cost_paid += cost
            info = {
                "true_condition": self._true_condition,
                "true_nuisance": self._true_nuisance,
                "test_index": action,
                "is_distractor": is_distractor,
                "test_count": self._test_count,
                "distractor_count": self._distractor_count,
                "test_cost_paid": self._cost_paid,
            }
            return obs, -cost, False, False, info

        diagnosed = action - self.num_tests
        correct = diagnosed == self._true_condition
        reward = self.correct_reward if correct else self.incorrect_penalty
        info = {
            "true_condition": self._true_condition,
            "true_nuisance": self._true_nuisance,
            "diagnosed": diagnosed,
            "correct": correct,
            "test_count": self._test_count,
            "distractor_count": self._distractor_count,
            "total_reward": reward - self._cost_paid,
        }
        return 2, reward, True, False, info

    def _run_test(self, test_idx: int, is_distractor: bool) -> int:
        if is_distractor:
            bit = self._true_nuisance
            acc = self.distractor_accuracy
        else:
            bit = (self._true_condition >> test_idx) & 1
            acc = self.test_accuracy
        if self.np_random.random() < acc:
            return bit
        return 1 - bit
