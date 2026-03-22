"""
Agents for the RockSample interleaved observe-act POMDP.

Unlike observe-then-commit agents, these must handle state transitions
(agent movement) interleaved with observations (rock checks) and
terminal actions (sample, exit). Belief is maintained over K-bit
rock qualities while agent position is known.
"""

import numpy as np
import math
from typing import List, Tuple, Optional


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
        if observation == 2:
            return
        p_good = self.rock_beliefs[rock_idx]
        if observation == 1:
            p_obs_given_good = accuracy
            p_obs_given_bad = 1.0 - accuracy
        else:
            p_obs_given_good = 1.0 - accuracy
            p_obs_given_bad = accuracy

        p_obs = p_good * p_obs_given_good + (1 - p_good) * p_obs_given_bad
        if p_obs > 1e-10:
            self.rock_beliefs[rock_idx] = (p_good * p_obs_given_good) / p_obs

    def mark_sampled(self, rock_idx: int):
        self.rock_sampled[rock_idx] = True
        self.rock_beliefs[rock_idx] = 0.5

    def entropy(self) -> float:
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


def _update_belief_common(belief, env, action, observation):
    """Shared belief update logic for RockSample agents."""
    if env.NUM_MOVE_ACTIONS <= action < env.NUM_MOVE_ACTIONS + env.num_rocks:
        rock_idx = action - env.NUM_MOVE_ACTIONS
        accuracy = env.get_check_accuracy_at(env._agent_pos, rock_idx)
        belief.update_check(rock_idx, observation, accuracy)
    elif action == env.sample_action:
        for k in range(env.num_rocks):
            rp = env.get_rock_positions()[k]
            if rp == env._agent_pos and not belief.rock_sampled[k]:
                belief.mark_sampled(k)
                break


def _move_toward_common(env, pos: Tuple[int, int], target: Tuple[int, int]) -> int:
    """Shared movement logic for RockSample agents."""
    dr = target[0] - pos[0]
    dc = target[1] - pos[1]
    if abs(dr) >= abs(dc):
        return env.MOVE_S if dr > 0 else env.MOVE_N
    else:
        return env.MOVE_E if dc > 0 else env.MOVE_W


def _info_gain_for_rock(rock_belief: float, accuracy: float) -> float:
    """Expected information gain from checking a rock."""
    p = rock_belief
    if p < 1e-10 or p > 1 - 1e-10:
        return 0.0
    prior_h = -p * math.log(p) - (1 - p) * math.log(1 - p)
    post_h = 0.0
    for obs in [0, 1]:
        if obs == 1:
            p_obs = p * accuracy + (1 - p) * (1 - accuracy)
            p_post = (p * accuracy) / p_obs if p_obs > 1e-10 else p
        else:
            p_obs = p * (1 - accuracy) + (1 - p) * accuracy
            p_post = (p * (1 - accuracy)) / p_obs if p_obs > 1e-10 else p
        if 0 < p_post < 1:
            post_h += p_obs * (-p_post * math.log(p_post) - (1 - p_post) * math.log(1 - p_post))
    return prior_h - post_h


class RockSampleGreedyAgent:
    """
    Reward-only agent for RockSample (no epistemic drive).

    Makes decisions based solely on expected reward without deliberately
    seeking information. Moves to rocks with positive expected value and
    samples them.
    """

    def __init__(self, env, sample_threshold: float = 0.5):
        self.env = env
        self.belief = RockSampleBeliefState(env.num_rocks)
        self.sample_threshold = sample_threshold

    def reset(self):
        self.belief.reset()

    def select_action(self) -> int:
        pos = self.env._agent_pos
        rock_positions = self.env.get_rock_positions()

        for k in range(self.env.num_rocks):
            if not self.belief.rock_sampled[k] and rock_positions[k] == pos:
                ev = self.belief.expected_sample_reward(
                    k, self.env.good_rock_reward, self.env.bad_rock_penalty
                )
                if ev >= 0 and self.belief.rock_beliefs[k] >= self.sample_threshold:
                    return self.env.sample_action

        best_rock = None
        best_score = -float("inf")
        for k in range(self.env.num_rocks):
            if self.belief.rock_sampled[k]:
                continue
            p = self.belief.rock_beliefs[k]
            if p < 0.3:
                continue
            dist = abs(pos[0] - rock_positions[k][0]) + abs(pos[1] - rock_positions[k][1])
            score = p / max(1, dist)
            if score > best_score:
                best_score = score
                best_rock = k

        if best_rock is not None:
            target = rock_positions[best_rock]
            if target != pos:
                return _move_toward_common(self.env, pos, target)

        return self.env.exit_action

    def update(self, action: int, observation: int):
        _update_belief_common(self.belief, self.env, action, observation)


class RockSampleEFEAgent:
    """
    EFE agent for RockSample with deliberate information gathering.

    Explicitly values information: moves toward uncertain rocks, checks
    them to determine quality, then samples only those confirmed good.
    """

    def __init__(self, env, info_weight: float = 1.0, confidence_threshold: float = 0.75):
        self.env = env
        self.belief = RockSampleBeliefState(env.num_rocks)
        self.info_weight = info_weight
        self.confidence_threshold = confidence_threshold

    def reset(self):
        self.belief.reset()

    def _rock_is_resolved(self, k: int) -> bool:
        if self.belief.rock_sampled[k]:
            return True
        p = self.belief.rock_beliefs[k]
        return p > self.confidence_threshold or p < (1 - self.confidence_threshold)

    def _unresolved_rocks(self):
        return [k for k in range(self.env.num_rocks)
                if not self.belief.rock_sampled[k] and not self._rock_is_resolved(k)]

    def select_action(self) -> int:
        pos = self.env._agent_pos
        rock_positions = self.env.get_rock_positions()

        for k in range(self.env.num_rocks):
            if not self.belief.rock_sampled[k] and rock_positions[k] == pos:
                if self.belief.rock_beliefs[k] > self.confidence_threshold:
                    return self.env.sample_action

        unresolved = self._unresolved_rocks()

        if not unresolved:
            good_unsampled = [k for k in range(self.env.num_rocks)
                              if not self.belief.rock_sampled[k]
                              and self.belief.rock_beliefs[k] > self.confidence_threshold]
            if good_unsampled:
                closest = min(good_unsampled,
                              key=lambda k: abs(pos[0]-rock_positions[k][0]) + abs(pos[1]-rock_positions[k][1]))
                return _move_toward_common(self.env, pos, rock_positions[closest])
            return self.env.exit_action

        best_check_k = None
        best_check_score = -float("inf")
        for k in unresolved:
            accuracy = self.env.get_check_accuracy_at(pos, k)
            ig = _info_gain_for_rock(self.belief.rock_beliefs[k], accuracy)
            p = self.belief.rock_beliefs[k]
            potential = self.env.good_rock_reward * p
            score = self.info_weight * ig + 0.1 * potential
            if score > best_check_score:
                best_check_score = score
                best_check_k = k

        if best_check_k is not None:
            accuracy = self.env.get_check_accuracy_at(pos, best_check_k)
            if accuracy >= 0.6:
                return self.env.NUM_MOVE_ACTIONS + best_check_k
            return _move_toward_common(self.env, pos, rock_positions[best_check_k])

        return self.env.exit_action

    def update(self, action: int, observation: int):
        _update_belief_common(self.belief, self.env, action, observation)


class RockSamplePlanningIGAgent:
    """
    Planning+IG agent for RockSample with tunable information weight.

    Uses the same factored belief and decision structure as EFE but with an
    explicit weight parameter w. Enables direct comparison with EFE (w=1)
    at per-environment tuned weights.
    """

    def __init__(self, env, info_weight: float = 5.0, confidence_threshold: float = 0.75):
        self.env = env
        self.belief = RockSampleBeliefState(env.num_rocks)
        self.info_weight = info_weight
        self.confidence_threshold = confidence_threshold

    def reset(self):
        self.belief.reset()

    def _rock_is_resolved(self, k: int) -> bool:
        if self.belief.rock_sampled[k]:
            return True
        p = self.belief.rock_beliefs[k]
        return p > self.confidence_threshold or p < (1 - self.confidence_threshold)

    def select_action(self) -> int:
        pos = self.env._agent_pos
        rock_positions = self.env.get_rock_positions()

        for k in range(self.env.num_rocks):
            if not self.belief.rock_sampled[k] and rock_positions[k] == pos:
                if self.belief.rock_beliefs[k] > self.confidence_threshold:
                    return self.env.sample_action

        unresolved = [k for k in range(self.env.num_rocks)
                      if not self.belief.rock_sampled[k] and not self._rock_is_resolved(k)]

        if not unresolved:
            good_unsampled = [k for k in range(self.env.num_rocks)
                              if not self.belief.rock_sampled[k]
                              and self.belief.rock_beliefs[k] > self.confidence_threshold]
            if good_unsampled:
                closest = min(good_unsampled,
                              key=lambda k: abs(pos[0]-rock_positions[k][0]) + abs(pos[1]-rock_positions[k][1]))
                return _move_toward_common(self.env, pos, rock_positions[closest])
            return self.env.exit_action

        best_check_k = None
        best_check_score = -float("inf")
        for k in unresolved:
            accuracy = self.env.get_check_accuracy_at(pos, k)
            ig = _info_gain_for_rock(self.belief.rock_beliefs[k], accuracy)
            p = self.belief.rock_beliefs[k]
            potential = self.env.good_rock_reward * p
            score = self.info_weight * ig + 0.1 * potential
            if score > best_check_score:
                best_check_score = score
                best_check_k = k

        if best_check_k is not None:
            accuracy = self.env.get_check_accuracy_at(pos, best_check_k)
            if accuracy >= 0.6:
                return self.env.NUM_MOVE_ACTIONS + best_check_k
            return _move_toward_common(self.env, pos, rock_positions[best_check_k])

        return self.env.exit_action

    def update(self, action: int, observation: int):
        _update_belief_common(self.belief, self.env, action, observation)


class RockSamplePOMCPAgent:
    """
    POMCP-style agent for RockSample with Monte Carlo rollouts.

    Uses sampled rock qualities from the factored belief to evaluate actions
    via forward simulation. Provides a stronger baseline than greedy by
    implicitly valuing future reward through random rollouts.
    """

    def __init__(self, env, num_simulations: int = 1000, rollout_depth: int = 15):
        self.env = env
        self.belief = RockSampleBeliefState(env.num_rocks)
        self.num_simulations = num_simulations
        self.rollout_depth = rollout_depth

    def reset(self):
        self.belief.reset()

    def select_action(self) -> int:
        pos = self.env._agent_pos
        rock_positions = self.env.get_rock_positions()
        num_actions = self.env.num_actions
        action_values = np.zeros(num_actions)
        action_counts = np.zeros(num_actions)

        sims_per_action = max(1, self.num_simulations // num_actions)

        for a in range(num_actions):
            for _ in range(sims_per_action):
                rock_quals = np.array([
                    1 if np.random.random() < self.belief.rock_beliefs[k] else 0
                    for k in range(self.env.num_rocks)
                ])
                value = self._simulate_rollout(pos, rock_quals, a, rock_positions)
                action_values[a] += value
                action_counts[a] += 1

        mean_values = np.where(action_counts > 0, action_values / action_counts, -np.inf)
        return int(np.argmax(mean_values))

    def _simulate_rollout(self, pos, rock_quals, first_action, rock_positions):
        sim_pos = pos
        sim_sampled = self.belief.rock_sampled.copy()
        total_reward = 0.0

        action = first_action
        for step in range(self.rollout_depth):
            if action < self.env.NUM_MOVE_ACTIONS:
                r, c = sim_pos
                if action == 0: r = max(0, r - 1)
                elif action == 1: r = min(self.env.grid_size - 1, r + 1)
                elif action == 2: c = min(self.env.grid_size - 1, c + 1)
                elif action == 3: c = max(0, c - 1)
                sim_pos = (r, c)
                total_reward += self.env.move_cost
            elif action < self.env.NUM_MOVE_ACTIONS + self.env.num_rocks:
                pass
            elif action == self.env.sample_action:
                for k in range(self.env.num_rocks):
                    if rock_positions[k] == sim_pos and not sim_sampled[k]:
                        sim_sampled[k] = True
                        if rock_quals[k] == 1:
                            total_reward += self.env.good_rock_reward
                        else:
                            total_reward += self.env.bad_rock_penalty
                        break
            elif action == self.env.exit_action:
                total_reward += self.env.exit_reward
                return total_reward

            action = np.random.randint(0, self.env.num_actions)

        return total_reward

    def update(self, action: int, observation: int):
        _update_belief_common(self.belief, self.env, action, observation)
