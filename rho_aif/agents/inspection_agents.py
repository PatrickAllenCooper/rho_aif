"""
Agents for the Structural Inspection POMDP.

Factored belief over N independent component fault states, with depth-limited
tree search parameterized by info_weight (w=0: Planning, w=1: EFE, w>0: Planning+IG).
Follows the same pattern as RockSampleTreeSearchAgent.
"""

import numpy as np
import math
from typing import List, Tuple, Optional


class InspectionBeliefState:
    """
    Factored belief over N independent component fault probabilities.
    Each component's fault state is tracked as P(faulty_i).
    """

    def __init__(self, num_components: int, fault_prior: float = 0.3):
        self.num_components = num_components
        self.fault_prior = fault_prior
        self.fault_beliefs = np.full(num_components, fault_prior)
        self.diagnosed = np.zeros(num_components, dtype=bool)

    def reset(self):
        self.fault_beliefs = np.full(self.num_components, self.fault_prior)
        self.diagnosed = np.zeros(self.num_components, dtype=bool)

    def update_test(self, comp_idx: int, observation: int, accuracy: float):
        if observation == 2:
            return
        p_faulty = self.fault_beliefs[comp_idx]
        if observation == 1:  # positive (faulty signal)
            p_obs_given_faulty = accuracy
            p_obs_given_nominal = 1.0 - accuracy
        else:  # negative (nominal signal)
            p_obs_given_faulty = 1.0 - accuracy
            p_obs_given_nominal = accuracy

        p_obs = p_faulty * p_obs_given_faulty + (1 - p_faulty) * p_obs_given_nominal
        if p_obs > 1e-10:
            self.fault_beliefs[comp_idx] = (p_faulty * p_obs_given_faulty) / p_obs

    def mark_diagnosed(self, comp_idx: int):
        self.diagnosed[comp_idx] = True


class InspectionTreeSearchAgent:
    """
    Depth-limited belief-space tree search for Structural Inspection.

    Parameterized by info_weight:
      - info_weight=0: reward-only Planning (rho=0)
      - info_weight=1: EFE (rho = information gain, canonical w=1)
      - info_weight=w: Planning+IG with tunable weight

    The tree search evaluates move, test, and diagnose actions at each node.
    Test actions branch on observation outcomes; move actions update position
    deterministically; diagnose actions yield immediate reward and mark the
    component as done.
    """

    def __init__(self, env, info_weight: float = 1.0, max_depth: int = 3):
        self.env = env
        self.belief = InspectionBeliefState(env.num_components, env.fault_prior)
        self.info_weight = info_weight
        self.max_depth = max_depth
        self._cache = {}

    def reset(self):
        self.belief.reset()
        self._cache = {}

    def _apply_move_sim(self, pos, action):
        r, c = pos
        if action == 0:  # N
            r = max(0, r - 1)
        elif action == 1:  # S
            r = min(self.env.grid_size - 1, r + 1)
        elif action == 2:  # E
            c = min(self.env.grid_size - 1, c + 1)
        elif action == 3:  # W
            c = max(0, c - 1)
        return (r, c)

    def _component_at(self, pos, comp_positions):
        for i, cp in enumerate(comp_positions):
            if cp == pos:
                return i
        return None

    def _binary_entropy(self, p):
        if p <= 0 or p >= 1:
            return 0.0
        return -p * math.log(p) - (1 - p) * math.log(1 - p)

    def _leaf_value(self, pos, fault_beliefs, diagnosed, comp_positions):
        """Heuristic: expected reward from diagnosing all remaining components
        based on current beliefs, plus travel cost."""
        value = 0.0
        sim_pos = pos

        for i in range(self.env.num_components):
            if diagnosed[i]:
                continue
            p_faulty = fault_beliefs[i]
            diag_nominal_ev = (
                (1 - p_faulty) * self.env.correct_nominal_reward
                + p_faulty * self.env.missed_fault_penalty
            )
            diag_faulty_ev = (
                p_faulty * self.env.correct_fault_reward
                + (1 - p_faulty) * self.env.false_alarm_penalty
            )
            best_diag_ev = max(diag_nominal_ev, diag_faulty_ev)

            dist = abs(sim_pos[0] - comp_positions[i][0]) + abs(sim_pos[1] - comp_positions[i][1])
            value += best_diag_ev + dist * self.env.move_cost
            sim_pos = comp_positions[i]

        return value

    def _make_cache_key(self, pos, fault_beliefs, diagnosed, depth):
        belief_key = tuple(round(b, 3) for b in fault_beliefs)
        diag_key = tuple(diagnosed)
        return (pos, belief_key, diag_key, depth)

    def _evaluate(self, pos, fault_beliefs, diagnosed, depth, comp_positions):
        if np.all(diagnosed):
            return -1, 0.0

        if depth >= self.max_depth:
            return -1, self._leaf_value(pos, fault_beliefs, diagnosed, comp_positions)

        cache_key = self._make_cache_key(pos, fault_beliefs, diagnosed, depth)
        if cache_key in self._cache:
            return self._cache[cache_key]

        best_action = -1
        best_value = -1e9

        for move_a in range(self.env.NUM_MOVE_ACTIONS):
            new_pos = self._apply_move_sim(pos, move_a)
            if new_pos == pos:
                continue
            _, cont_val = self._evaluate(
                new_pos, fault_beliefs, diagnosed, depth + 1, comp_positions
            )
            val = self.env.move_cost + cont_val
            if val > best_value:
                best_value = val
                best_action = move_a

        comp_idx = self._component_at(pos, comp_positions)
        if comp_idx is not None and not diagnosed[comp_idx]:
            p_faulty = fault_beliefs[comp_idx]

            for test_type in range(self.env.num_test_types):
                accuracy = self.env.test_accuracies[test_type]
                cost = self.env.test_costs[test_type]

                prior_h = self._binary_entropy(p_faulty)

                expected_cont = 0.0
                expected_post_h = 0.0

                for obs_val in [0, 1]:
                    if obs_val == 1:
                        p_obs = p_faulty * accuracy + (1 - p_faulty) * (1 - accuracy)
                        p_post = (p_faulty * accuracy) / p_obs if p_obs > 1e-10 else p_faulty
                    else:
                        p_obs = p_faulty * (1 - accuracy) + (1 - p_faulty) * accuracy
                        p_post = (p_faulty * (1 - accuracy)) / p_obs if p_obs > 1e-10 else p_faulty

                    post_h = self._binary_entropy(p_post)
                    expected_post_h += p_obs * post_h

                    new_beliefs = fault_beliefs.copy()
                    new_beliefs[comp_idx] = p_post
                    _, cont_val = self._evaluate(
                        pos, new_beliefs, diagnosed, depth + 1, comp_positions
                    )
                    expected_cont += p_obs * cont_val

                ig = prior_h - expected_post_h
                test_action = self.env.test_action_start + test_type
                val = cost + self.info_weight * ig + expected_cont
                if val > best_value:
                    best_value = val
                    best_action = test_action

            for diag_val in [0, 1]:
                if diag_val == 0:
                    ev = (
                        (1 - p_faulty) * self.env.correct_nominal_reward
                        + p_faulty * self.env.missed_fault_penalty
                    )
                else:
                    ev = (
                        p_faulty * self.env.correct_fault_reward
                        + (1 - p_faulty) * self.env.false_alarm_penalty
                    )

                new_diagnosed = diagnosed.copy()
                new_diagnosed[comp_idx] = True
                new_beliefs = fault_beliefs.copy()
                _, cont_val = self._evaluate(
                    pos, new_beliefs, new_diagnosed, depth + 1, comp_positions
                )
                val = ev + cont_val
                diag_action = self.env.diagnose_action_start + diag_val
                if val > best_value:
                    best_value = val
                    best_action = diag_action

        self._cache[cache_key] = (best_action, best_value)
        return best_action, best_value

    def select_action(self) -> int:
        self._cache = {}
        pos = self.env._agent_pos
        comp_positions = self.env.get_component_positions()
        action, _ = self._evaluate(
            pos,
            self.belief.fault_beliefs.copy(),
            self.belief.diagnosed.copy(),
            0,
            comp_positions,
        )
        if action < 0:
            return 0
        return action

    def update(self, action: int, observation: int):
        if self.env.test_action_start <= action < self.env.diagnose_action_start:
            test_type = action - self.env.test_action_start
            comp_idx = self.env.component_at_position(self.env._agent_pos)
            if comp_idx is not None:
                accuracy = self.env.test_accuracies[test_type]
                self.belief.update_test(comp_idx, observation, accuracy)
        elif action >= self.env.diagnose_action_start:
            comp_idx = self.env.component_at_position(self.env._agent_pos)
            if comp_idx is not None:
                self.belief.mark_diagnosed(comp_idx)


class InspectionGreedyAgent:
    """Greedy agent: navigate to nearest undiagnosed component, diagnose based on prior."""

    def __init__(self, env):
        self.env = env
        self.belief = InspectionBeliefState(env.num_components, env.fault_prior)

    def reset(self):
        self.belief.reset()

    def select_action(self) -> int:
        pos = self.env._agent_pos
        comp_positions = self.env.get_component_positions()

        comp_idx = self.env.component_at_position(pos)
        if comp_idx is not None and not self.belief.diagnosed[comp_idx]:
            p_faulty = self.belief.fault_beliefs[comp_idx]
            if p_faulty > 0.5:
                return self.env.diagnose_action_start + 1
            else:
                return self.env.diagnose_action_start + 0

        best_dist = float('inf')
        best_comp = None
        for i in range(self.env.num_components):
            if self.belief.diagnosed[i]:
                continue
            cp = comp_positions[i]
            dist = abs(pos[0] - cp[0]) + abs(pos[1] - cp[1])
            if dist < best_dist:
                best_dist = dist
                best_comp = i

        if best_comp is None:
            return 0

        target = comp_positions[best_comp]
        if pos[0] > target[0]:
            return 0  # N
        elif pos[0] < target[0]:
            return 1  # S
        elif pos[1] < target[1]:
            return 2  # E
        elif pos[1] > target[1]:
            return 3  # W
        return 0

    def update(self, action: int, observation: int):
        if self.env.test_action_start <= action < self.env.diagnose_action_start:
            test_type = action - self.env.test_action_start
            comp_idx = self.env.component_at_position(self.env._agent_pos)
            if comp_idx is not None:
                accuracy = self.env.test_accuracies[test_type]
                self.belief.update_test(comp_idx, observation, accuracy)
        elif action >= self.env.diagnose_action_start:
            comp_idx = self.env.component_at_position(self.env._agent_pos)
            if comp_idx is not None:
                self.belief.mark_diagnosed(comp_idx)
