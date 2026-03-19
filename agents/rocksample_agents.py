"""
Agents for the RockSample interleaved observe-act POMDP.

Unlike observe-then-commit agents, these must handle state transitions
(agent movement) interleaved with observations (rock checks) and
terminal actions (sample, exit). Belief is maintained over K-bit
rock qualities while agent position is known.
"""

import numpy as np
from scipy.stats import entropy as scipy_entropy
from typing import List, Tuple
import math


class RockSampleBeliefState:
    """
    Factored belief over K independent rock qualities.

    Each rock's quality is tracked independently as P(good_k).
    Agent position is known and tracked externally.
    """

    def __init__(self, num_rocks: int):
        self.num_rocks = num_rocks
        self.rock_beliefs = np.full(num_rocks, 0.5)
        self.rock_sampled = np.zeros(num_rocks, dtype=bool)

    def reset(self):
        self.rock_beliefs = np.full(self.num_rocks, 0.5)
        self.rock_sampled = np.zeros(self.num_rocks, dtype=bool)

    def update_check(self, rock_idx: int, observation: int, accuracy: float):
        """Update belief about rock_idx given check observation."""
        if observation == 2:  # null
            return
        p_good = self.rock_beliefs[rock_idx]
        if observation == 1:  # good signal
            p_obs_given_good = accuracy
            p_obs_given_bad = 1.0 - accuracy
        else:  # bad signal
            p_obs_given_good = 1.0 - accuracy
            p_obs_given_bad = accuracy

        p_obs = p_good * p_obs_given_good + (1 - p_good) * p_obs_given_bad
        if p_obs > 1e-10:
            self.rock_beliefs[rock_idx] = (p_good * p_obs_given_good) / p_obs

    def mark_sampled(self, rock_idx: int):
        self.rock_sampled[rock_idx] = True
        self.rock_beliefs[rock_idx] = 0.5

    def entropy(self) -> float:
        """Total belief entropy over all unsampled rocks."""
        total = 0.0
        for k in range(self.num_rocks):
            if self.rock_sampled[k]:
                continue
            p = self.rock_beliefs[k]
            if 0 < p < 1:
                total += -p * math.log2(p) - (1 - p) * math.log2(1 - p)
        return total

    def expected_sample_reward(self, rock_idx: int, good_reward: float, bad_penalty: float) -> float:
        if self.rock_sampled[rock_idx]:
            return 0.0
        p = self.rock_beliefs[rock_idx]
        return p * good_reward + (1 - p) * bad_penalty


class RockSampleGreedyAgent:
    """
    Greedy heuristic agent for RockSample.

    Decision rule:
    1. If at a rock position and P(good) > threshold, sample it.
    2. Otherwise, check the most uncertain unsampled rock.
    3. If all rocks sampled or sufficiently explored, exit.
    4. Move toward the nearest valuable unsampled rock.
    """

    def __init__(self, env, sample_threshold: float = 0.7, check_threshold: float = 0.1):
        self.env = env
        self.belief = RockSampleBeliefState(env.num_rocks)
        self.sample_threshold = sample_threshold
        self.check_threshold = check_threshold

    def reset(self):
        self.belief.reset()

    def select_action(self) -> int:
        pos = self.env._agent_pos
        rock_positions = self.env.get_rock_positions()

        for k in range(self.env.num_rocks):
            if not self.belief.rock_sampled[k] and rock_positions[k] == pos:
                if self.belief.rock_beliefs[k] > self.sample_threshold:
                    return self.env.sample_action

        any_valuable = False
        for k in range(self.env.num_rocks):
            if not self.belief.rock_sampled[k] and self.belief.rock_beliefs[k] > 0.3:
                any_valuable = True
                break

        if not any_valuable:
            return self.env.exit_action

        best_check = None
        best_uncertainty = -1
        for k in range(self.env.num_rocks):
            if self.belief.rock_sampled[k]:
                continue
            p = self.belief.rock_beliefs[k]
            uncertainty = -abs(p - 0.5)
            if uncertainty > best_uncertainty:
                best_uncertainty = uncertainty
                best_check = k

        if best_check is not None:
            p = self.belief.rock_beliefs[best_check]
            if abs(p - 0.5) < (0.5 - self.check_threshold):
                return self.env.NUM_MOVE_ACTIONS + best_check

        best_rock = None
        best_value = -float("inf")
        for k in range(self.env.num_rocks):
            if self.belief.rock_sampled[k]:
                continue
            v = self.belief.expected_sample_reward(
                k, self.env.good_rock_reward, self.env.bad_rock_penalty
            )
            if v > best_value:
                best_value = v
                best_rock = k

        if best_rock is not None and best_value > 0:
            target = rock_positions[best_rock]
            return self._move_toward(pos, target)

        return self.env.exit_action

    def _move_toward(self, pos: Tuple[int, int], target: Tuple[int, int]) -> int:
        dr = target[0] - pos[0]
        dc = target[1] - pos[1]
        if abs(dr) >= abs(dc):
            return self.env.MOVE_S if dr > 0 else self.env.MOVE_N
        else:
            return self.env.MOVE_E if dc > 0 else self.env.MOVE_W

    def update(self, action: int, observation: int):
        """Update belief after observing the result of an action."""
        if self.env.NUM_MOVE_ACTIONS <= action < self.env.NUM_MOVE_ACTIONS + self.env.num_rocks:
            rock_idx = action - self.env.NUM_MOVE_ACTIONS
            accuracy = self.env.get_check_accuracy_at(
                self.env._agent_pos, rock_idx
            )
            self.belief.update_check(rock_idx, observation, accuracy)
        elif action == self.env.sample_action:
            for k in range(self.env.num_rocks):
                rp = self.env.get_rock_positions()[k]
                if rp == self.env._agent_pos and not self.belief.rock_sampled[k]:
                    self.belief.mark_sampled(k)
                    break


class RockSampleEFEAgent:
    """
    EFE-inspired agent for RockSample using one-step EFE heuristic.

    At each step, evaluates all available actions using a one-step
    lookahead that combines pragmatic value (expected reward) and
    epistemic value (expected information gain from checking).
    """

    def __init__(self, env, info_weight: float = 1.0):
        self.env = env
        self.belief = RockSampleBeliefState(env.num_rocks)
        self.info_weight = info_weight

    def reset(self):
        self.belief.reset()

    def select_action(self) -> int:
        pos = self.env._agent_pos
        rock_positions = self.env.get_rock_positions()
        best_action = self.env.exit_action
        best_value = self.env.exit_reward

        for k in range(self.env.num_rocks):
            if self.belief.rock_sampled[k]:
                continue
            if rock_positions[k] == pos:
                ev = self.belief.expected_sample_reward(
                    k, self.env.good_rock_reward, self.env.bad_rock_penalty
                )
                if ev > best_value:
                    best_value = ev
                    best_action = self.env.sample_action

        for k in range(self.env.num_rocks):
            if self.belief.rock_sampled[k]:
                continue
            accuracy = self.env.get_check_accuracy_at(pos, k)
            ig = self._expected_info_gain(k, accuracy)
            check_value = self.info_weight * ig
            if check_value > best_value:
                best_value = check_value
                best_action = self.env.NUM_MOVE_ACTIONS + k

        for move_action in range(self.env.NUM_MOVE_ACTIONS):
            new_pos = self.env._apply_move(move_action)
            if new_pos == pos:
                continue
            move_value = self._position_value(new_pos, rock_positions) + self.env.move_cost
            if move_value > best_value:
                best_value = move_value
                best_action = move_action

        return best_action

    def _expected_info_gain(self, rock_idx: int, accuracy: float) -> float:
        """Expected information gain from checking rock_idx at given accuracy."""
        p = self.belief.rock_beliefs[rock_idx]
        if p < 1e-10 or p > 1 - 1e-10:
            return 0.0

        prior_h = -p * math.log2(p) - (1 - p) * math.log2(1 - p)

        post_h = 0.0
        for obs in [0, 1]:
            if obs == 1:
                p_obs = p * accuracy + (1 - p) * (1 - accuracy)
            else:
                p_obs = p * (1 - accuracy) + (1 - p) * accuracy
            if p_obs < 1e-10:
                continue
            if obs == 1:
                p_post = (p * accuracy) / p_obs
            else:
                p_post = (p * (1 - accuracy)) / p_obs
            if 0 < p_post < 1:
                post_h += p_obs * (-p_post * math.log2(p_post) - (1 - p_post) * math.log2(1 - p_post))

        return prior_h - post_h

    def _position_value(self, pos: Tuple[int, int], rock_positions: list) -> float:
        """Heuristic value of being at a position."""
        value = 0.0
        for k in range(self.env.num_rocks):
            if self.belief.rock_sampled[k]:
                continue
            ev = self.belief.expected_sample_reward(
                k, self.env.good_rock_reward, self.env.bad_rock_penalty
            )
            if ev > 0:
                dist = abs(pos[0] - rock_positions[k][0]) + abs(pos[1] - rock_positions[k][1])
                value += ev / max(1, dist)
        return value

    def update(self, action: int, observation: int):
        if self.env.NUM_MOVE_ACTIONS <= action < self.env.NUM_MOVE_ACTIONS + self.env.num_rocks:
            rock_idx = action - self.env.NUM_MOVE_ACTIONS
            accuracy = self.env.get_check_accuracy_at(
                self.env._agent_pos, rock_idx
            )
            self.belief.update_check(rock_idx, observation, accuracy)
        elif action == self.env.sample_action:
            for k in range(self.env.num_rocks):
                rp = self.env.get_rock_positions()[k]
                if rp == self.env._agent_pos and not self.belief.rock_sampled[k]:
                    self.belief.mark_sampled(k)
                    break
