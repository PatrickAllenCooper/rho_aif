"""
POMCP (Partially Observable Monte-Carlo Planning) agent for observe-then-commit POMDPs.

Implements Silver and Veness (2010) adapted to the observe-then-commit structure:
- UCB1 tree policy for action selection during tree traversal
- Random rollout policy for leaf evaluation
- Particle-based belief representation at each tree node
- No state transitions during observation phase (state is fixed)
"""

import numpy as np
import math
from typing import List, Optional, Dict, Tuple
from rho_aif.agents.base import BaseAgent


class POMCPNode:
    """A node in the POMCP search tree."""
    __slots__ = ['visit_count', 'value_sum', 'children', 'obs_children', 'particles']

    def __init__(self):
        self.visit_count = 0
        self.value_sum = 0.0
        self.children: Dict[int, 'POMCPNode'] = {}
        self.obs_children: Dict[Tuple[int, int], 'POMCPNode'] = {}
        self.particles: List[int] = []

    @property
    def value(self):
        if self.visit_count == 0:
            return 0.0
        return self.value_sum / self.visit_count


class POMCPAgent(BaseAgent):
    """
    POMCP agent for observe-then-commit POMDPs.

    At each decision point, runs num_simulations Monte Carlo simulations
    through a search tree. Each simulation:
    1. Samples a hidden state from the current belief (particle)
    2. Traverses the tree using UCB1
    3. At a leaf, performs a random rollout
    4. Backpropagates the return

    This is a standard POMDP solver that handles exploration through
    its tree search mechanics rather than an explicit information gain bonus.
    """

    def __init__(
        self,
        observation_models,
        env_config: dict,
        num_simulations: int = 500,
        exploration_constant: float = 10.0,
        rollout_depth: int = 10,
        discount: float = 1.0,
        seed: int = 42,
        **kwargs,
    ):
        super().__init__(observation_models, env_config, **kwargs)
        self.num_simulations = num_simulations
        self.exploration_constant = exploration_constant
        self.rollout_depth = rollout_depth
        self.discount = discount
        self.all_actions = list(range(self.num_observe_actions + self.num_commit_actions))
        # Default preserves prior behavior (fixed internal stream across
        # runs); pass a per-run seed to vary the planner's own randomness
        # alongside the outer environment seed.
        self.seed = int(seed)
        self._rng = np.random.RandomState(self.seed)

    def select_action(self) -> int:
        root = POMCPNode()
        root.particles = self._sample_particles(self.belief.belief, self.num_simulations)

        for sim in range(self.num_simulations):
            state = root.particles[sim % len(root.particles)]
            self._simulate(root, state, 0)

        best_action = max(
            root.children.keys(),
            key=lambda a: root.children[a].value if root.children[a].visit_count > 0 else -float('inf')
        )
        return best_action

    def _simulate(self, node: POMCPNode, state: int, depth: int) -> float:
        if depth >= self.rollout_depth:
            return self._best_commit_reward(state)

        if node.visit_count == 0:
            node.visit_count = 1
            reward = self._rollout(state, depth)
            node.value_sum = reward
            return reward

        action = self._ucb_select(node)

        if action >= self.num_observe_actions:
            commit_idx = action - self.num_observe_actions
            reward = self.commit_rewards[commit_idx, state]
        else:
            obs_action_idx = action
            obs_cost = self.obs_costs[obs_action_idx]
            obs = self._sample_observation(state, obs_action_idx)

            key = (action, obs)
            if key not in node.obs_children:
                node.obs_children[key] = POMCPNode()

            child = node.obs_children[key]
            child.particles.append(state)

            reward = obs_cost + self.discount * self._simulate(child, state, depth + 1)

        if action not in node.children:
            node.children[action] = POMCPNode()
        action_node = node.children[action]
        action_node.visit_count += 1
        action_node.value_sum += reward

        node.visit_count += 1
        node.value_sum += reward

        return reward

    def _ucb_select(self, node: POMCPNode) -> int:
        best_action = None
        best_ucb = -float('inf')
        log_n = math.log(max(1, node.visit_count))

        for action in self.all_actions:
            if action not in node.children or node.children[action].visit_count == 0:
                return action

            child = node.children[action]
            exploitation = child.value
            exploration = self.exploration_constant * math.sqrt(log_n / child.visit_count)
            ucb = exploitation + exploration

            if ucb > best_ucb:
                best_ucb = ucb
                best_action = action

        return best_action if best_action is not None else self._rng.choice(self.all_actions)

    def _rollout(self, state: int, depth: int) -> float:
        total = 0.0
        gamma_power = 1.0
        b = self.belief.belief.copy()

        for d in range(depth, self.rollout_depth):
            if self._rng.random() < 0.3:
                _, commit_r = self._best_commit_from_belief(b)
                total += gamma_power * commit_r
                return total

            obs_action = self._rng.randint(0, self.num_observe_actions)
            obs = self._sample_observation(state, obs_action)

            total += gamma_power * self.obs_costs[obs_action]
            gamma_power *= self.discount

            likelihood = self.obs_models[obs_action][:, obs]
            b = b * likelihood
            norm = b.sum()
            if norm > 0:
                b /= norm

        _, commit_r = self._best_commit_from_belief(b)
        total += gamma_power * commit_r
        return total

    def _sample_observation(self, state: int, obs_action_idx: int) -> int:
        obs_probs = self.obs_models[obs_action_idx][state, :]
        return self._rng.choice(len(obs_probs), p=obs_probs)

    def _sample_particles(self, belief: np.ndarray, n: int) -> List[int]:
        return list(self._rng.choice(len(belief), size=n, p=belief))

    def _best_commit_reward(self, state: int) -> float:
        return float(np.max(self.commit_rewards[:, state]))
