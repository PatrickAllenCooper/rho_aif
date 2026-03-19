"""
MCTS agent using EFE as the leaf heuristic.

Replaces the exact tree search (O(K * |O|^H)) with Monte Carlo Tree Search
that uses one-step EFE as the leaf evaluation function. This enables
scaling to higher horizons (H=5+) without exponential blowup.

Tree policy: UCB1 adapted for belief trees.
Leaf evaluation: one-step EFE (pragmatic + epistemic value).
Rollout: EFE-greedy policy for K steps.
"""

import numpy as np
from scipy.stats import entropy as scipy_entropy
from typing import Union, List, Optional
from agents.base import BaseAgent
import math


class MCTSNode:
    """A node in the MCTS belief tree."""

    __slots__ = [
        "belief", "parent", "action", "children",
        "visit_count", "total_value", "is_terminal",
    ]

    def __init__(self, belief: np.ndarray, parent=None, action: int = -1):
        self.belief = belief
        self.parent = parent
        self.action = action
        self.children = {}
        self.visit_count = 0
        self.total_value = 0.0
        self.is_terminal = False

    @property
    def mean_value(self):
        if self.visit_count == 0:
            return 0.0
        return self.total_value / self.visit_count

    def ucb1(self, exploration_constant: float = 1.414) -> float:
        if self.visit_count == 0:
            return float("inf")
        exploitation = self.mean_value
        exploration = exploration_constant * math.sqrt(
            math.log(self.parent.visit_count) / self.visit_count
        )
        return exploitation + exploration


class MCTSEFEAgent(BaseAgent):
    """
    MCTS agent with EFE leaf heuristic for observe-then-commit POMDPs.

    Uses UCB1 tree policy to select actions in the belief tree, and
    evaluates leaf nodes using one-step EFE computation. This avoids
    the exponential cost of exact tree search while preserving the
    EFE objective's epistemic-pragmatic balance.
    """

    def __init__(
        self,
        observation_models: Union[np.ndarray, List[np.ndarray]],
        env_config: dict,
        num_simulations: int = 200,
        planning_horizon: int = 5,
        rollout_depth: int = 3,
        exploration_constant: float = 1.414,
    ):
        super().__init__(observation_models, env_config)
        self.num_simulations = num_simulations
        self.planning_horizon = planning_horizon
        self.rollout_depth = rollout_depth
        self.exploration_constant = exploration_constant

    def select_action(self) -> int:
        root = MCTSNode(belief=self.belief.belief.copy())
        root.visit_count = 1

        for _ in range(self.num_simulations):
            node = self._tree_policy(root)
            value = self._evaluate_leaf(node)
            self._backpropagate(node, value)

        best_action = max(
            root.children.values(),
            key=lambda c: c.visit_count,
        ).action
        return best_action

    def _tree_policy(self, node: MCTSNode) -> MCTSNode:
        """Select a leaf node using UCB1."""
        depth = 0
        while depth < self.planning_horizon:
            if node.is_terminal:
                return node

            if not node.children:
                self._expand(node)
                first_child = next(iter(node.children.values()))
                return first_child

            if any(c.visit_count == 0 for c in node.children.values()):
                unvisited = [c for c in node.children.values() if c.visit_count == 0]
                return unvisited[np.random.randint(len(unvisited))]

            node = max(
                node.children.values(),
                key=lambda c: c.ucb1(self.exploration_constant),
            )
            depth += 1

        return node

    def _expand(self, node: MCTSNode):
        """Expand all possible actions from this node."""
        belief = node.belief

        for k in range(self.num_observe_actions):
            model = self.obs_models[k]
            num_outcomes = model.shape[1]
            obs_idx = self._sample_observation(belief, model)

            posterior = model[:, obs_idx] * belief
            p_sum = posterior.sum()
            if p_sum < 1e-10:
                posterior = np.ones_like(belief) / len(belief)
            else:
                posterior = posterior / p_sum

            child = MCTSNode(belief=posterior, parent=node, action=k)
            node.children[k] = child

        for i in range(self.num_commit_actions):
            action_id = self.num_observe_actions + i
            child = MCTSNode(belief=belief.copy(), parent=node, action=action_id)
            child.is_terminal = True
            node.children[action_id] = child

    def _sample_observation(self, belief: np.ndarray, model: np.ndarray) -> int:
        """Sample an observation from the predictive distribution."""
        predictive = belief @ model
        predictive = predictive / predictive.sum()
        return int(np.random.choice(len(predictive), p=predictive))

    def _evaluate_leaf(self, node: MCTSNode) -> float:
        """Evaluate a leaf node using EFE heuristic + rollout."""
        if node.is_terminal:
            action_idx = node.action - self.num_observe_actions
            return float(np.dot(node.belief, self.commit_rewards[action_idx]))

        return self._efe_rollout(node.belief, self.rollout_depth)

    def _efe_rollout(self, belief: np.ndarray, depth: int) -> float:
        """Greedy EFE rollout for estimating leaf value."""
        if depth <= 0:
            return self._best_commit_value(belief)

        best_commit = self._best_commit_value(belief)
        best_obs_value = float("-inf")

        for k in range(self.num_observe_actions):
            v = self._one_step_efe_value(k, belief)
            if v > best_obs_value:
                best_obs_value = v

        if best_obs_value <= best_commit:
            return best_commit

        best_k = 0
        best_v = float("-inf")
        for k in range(self.num_observe_actions):
            v = self._one_step_efe_value(k, belief)
            if v > best_v:
                best_v = v
                best_k = k

        model = self.obs_models[best_k]
        obs_idx = self._sample_observation(belief, model)
        posterior = model[:, obs_idx] * belief
        p_sum = posterior.sum()
        if p_sum < 1e-10:
            posterior = np.ones_like(belief) / len(belief)
        else:
            posterior = posterior / p_sum

        return -self.obs_costs[best_k] + self._efe_rollout(posterior, depth - 1)

    def _one_step_efe_value(self, obs_action: int, belief: np.ndarray) -> float:
        """One-step EFE value V = -G = -cost + IG + E[best_commit_after]."""
        model = self.obs_models[obs_action]
        num_outcomes = model.shape[1]
        prior_entropy = scipy_entropy(belief, base=2)
        expected_posterior_entropy = 0.0
        expected_commit_value = 0.0

        for obs_idx in range(num_outcomes):
            prob_obs = float(np.dot(belief, model[:, obs_idx]))
            if prob_obs < 1e-10:
                continue

            posterior = model[:, obs_idx] * belief
            posterior = posterior / posterior.sum()
            expected_posterior_entropy += prob_obs * scipy_entropy(posterior, base=2)
            expected_commit_value += prob_obs * self._best_commit_value(posterior)

        info_gain = prior_entropy - expected_posterior_entropy
        return -self.obs_costs[obs_action] + info_gain + expected_commit_value

    def _best_commit_value(self, belief: np.ndarray) -> float:
        """Best expected reward from committing at this belief."""
        best = float("-inf")
        for i in range(self.num_commit_actions):
            v = float(np.dot(belief, self.commit_rewards[i]))
            if v > best:
                best = v
        return best

    def _backpropagate(self, node: MCTSNode, value: float):
        """Propagate value up the tree."""
        while node is not None:
            node.visit_count += 1
            node.total_value += value
            node = node.parent
