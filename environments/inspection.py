"""
Structural Inspection POMDP: multi-component fault detection with spatial navigation.

A factored observation POMDP where an agent inspects N components arranged
spatially, each with a hidden binary state (nominal/faulty). The agent can:
  - Move between component locations (navigation actions)
  - Run non-destructive tests at the current location (observation actions)
  - Declare a diagnosis for each component (exploitation actions)

This maps directly to industrial inspection, medical screening, and fault
detection -- domains where information-gathering preserves the hidden state.

Factored observation structure: tests do not change component fault states,
navigation does not change fault states, so Proposition 3.3 applies.
"""

import gymnasium as gym
from gymnasium import spaces
import numpy as np
from typing import Tuple, List, Optional


class InspectionEnv(gym.Env):
    """
    Structural Inspection environment.

    State: agent position (known) + component fault states (hidden binary vector).
    Actions: move(variable) + test(K per component at location) + diagnose(2 per component).
    Observations: {negative, positive, null} for tests; null otherwise.

    Parameters:
        num_components: N components to inspect.
        component_positions: spatial locations (1D or 2D).
        num_test_types: K different test types with varying accuracy/cost.
        test_accuracies: accuracy of each test type.
        test_costs: cost of each test type.
        fault_prior: prior probability each component is faulty.
        correct_nominal_reward: reward for correctly diagnosing nominal.
        correct_fault_reward: reward for correctly diagnosing faulty.
        missed_fault_penalty: penalty for diagnosing nominal when faulty.
        false_alarm_penalty: penalty for diagnosing faulty when nominal.
        move_cost: cost per move action.
        max_steps: episode length limit.
    """

    def __init__(
        self,
        num_components: int = 8,
        num_test_types: int = 2,
        test_accuracies: Optional[List[float]] = None,
        test_costs: Optional[List[float]] = None,
        fault_prior: float = 0.3,
        correct_nominal_reward: float = 2.0,
        correct_fault_reward: float = 5.0,
        missed_fault_penalty: float = -50.0,
        false_alarm_penalty: float = -5.0,
        move_cost: float = -0.5,
        max_steps: int = 200,
        component_positions: Optional[List[Tuple[int, int]]] = None,
        grid_size: Optional[int] = None,
    ):
        super().__init__()
        self.num_components = num_components
        self.num_test_types = num_test_types
        self.fault_prior = fault_prior
        self.correct_nominal_reward = correct_nominal_reward
        self.correct_fault_reward = correct_fault_reward
        self.missed_fault_penalty = missed_fault_penalty
        self.false_alarm_penalty = false_alarm_penalty
        self.move_cost = move_cost
        self.max_steps = max_steps

        if test_accuracies is None:
            self.test_accuracies = [0.70, 0.90] if num_test_types == 2 else [0.80]
        else:
            self.test_accuracies = list(test_accuracies)

        if test_costs is None:
            self.test_costs = [-0.5, -2.0] if num_test_types == 2 else [-1.0]
        else:
            self.test_costs = list(test_costs)

        if grid_size is None:
            self.grid_size = max(4, int(np.ceil(np.sqrt(num_components * 3))))
        else:
            self.grid_size = grid_size

        if component_positions is not None:
            self._fixed_positions = list(component_positions)
        else:
            self._fixed_positions = self._default_positions()

        self.MOVE_N, self.MOVE_S, self.MOVE_E, self.MOVE_W = 0, 1, 2, 3
        self.NUM_MOVE_ACTIONS = 4

        self.num_test_actions = num_test_types
        self.num_diagnose_actions = 2

        self.num_actions = (
            self.NUM_MOVE_ACTIONS
            + self.num_test_types
            + self.num_diagnose_actions
        )

        self.action_space = spaces.Discrete(self.num_actions)
        self.observation_space = spaces.Discrete(3)

        self._agent_pos = (0, 0)
        self._fault_states = np.zeros(num_components, dtype=int)
        self._diagnosed = np.zeros(num_components, dtype=bool)
        self._diagnoses = np.full(num_components, -1, dtype=int)
        self._step_count = 0

    def _default_positions(self):
        n = self.num_components
        g = self.grid_size
        positions = set()
        for i in range(n):
            r = (i * g) // n
            c = (i * 2 + 1) % g
            while (r, c) in positions:
                c = (c + 1) % g
                if c == (i * 2 + 1) % g:
                    r = (r + 1) % g
            positions.add((r, c))
        return list(positions)

    @property
    def test_action_start(self):
        return self.NUM_MOVE_ACTIONS

    @property
    def diagnose_action_start(self):
        return self.NUM_MOVE_ACTIONS + self.num_test_types

    def component_at_position(self, pos):
        for i, cp in enumerate(self._component_positions):
            if cp == pos:
                return i
        return None

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)
        self._agent_pos = (0, 0)
        self._component_positions = list(self._fixed_positions)
        self._fault_states = (
            self.np_random.random(self.num_components) < self.fault_prior
        ).astype(int)
        self._diagnosed = np.zeros(self.num_components, dtype=bool)
        self._diagnoses = np.full(self.num_components, -1, dtype=int)
        self._step_count = 0
        self._total_correct = 0
        self._total_missed = 0
        self._total_false_alarm = 0

        obs = 2  # null
        info = {
            "agent_pos": self._agent_pos,
            "component_positions": self._component_positions,
            "fault_states": self._fault_states.copy(),
        }
        return obs, info

    def step(self, action: int):
        self._step_count += 1
        reward = 0.0
        terminated = False
        truncated = self._step_count >= self.max_steps
        obs = 2  # null

        if action < self.NUM_MOVE_ACTIONS:
            reward += self.move_cost
            self._agent_pos = self._apply_move(action)

        elif action < self.diagnose_action_start:
            test_type = action - self.test_action_start
            comp_idx = self.component_at_position(self._agent_pos)
            if comp_idx is not None and not self._diagnosed[comp_idx]:
                reward += self.test_costs[test_type]
                obs = self._run_test(comp_idx, test_type)
            else:
                reward += self.test_costs[test_type]

        else:
            diag_value = action - self.diagnose_action_start
            comp_idx = self.component_at_position(self._agent_pos)
            if comp_idx is not None and not self._diagnosed[comp_idx]:
                self._diagnosed[comp_idx] = True
                self._diagnoses[comp_idx] = diag_value
                true_state = self._fault_states[comp_idx]

                if diag_value == true_state:
                    if true_state == 0:
                        reward += self.correct_nominal_reward
                    else:
                        reward += self.correct_fault_reward
                    self._total_correct += 1
                else:
                    if true_state == 1 and diag_value == 0:
                        reward += self.missed_fault_penalty
                        self._total_missed += 1
                    else:
                        reward += self.false_alarm_penalty
                        self._total_false_alarm += 1

            if np.all(self._diagnosed):
                terminated = True

        info = {"agent_pos": self._agent_pos, "step": self._step_count}

        if terminated or truncated:
            info["total_correct"] = self._total_correct
            info["total_missed"] = self._total_missed
            info["total_false_alarm"] = self._total_false_alarm
            info["components_diagnosed"] = int(np.sum(self._diagnosed))
            info["all_diagnosed"] = bool(np.all(self._diagnosed))

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

    def _run_test(self, comp_idx: int, test_type: int) -> int:
        accuracy = self.test_accuracies[test_type]
        true_state = self._fault_states[comp_idx]
        if self.np_random.random() < accuracy:
            return true_state  # 0=nominal, 1=faulty
        else:
            return 1 - true_state

    def get_component_positions(self) -> List[Tuple[int, int]]:
        return list(self._component_positions)
