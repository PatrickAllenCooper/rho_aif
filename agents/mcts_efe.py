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
        "_obs_children",
    ]

    def __init__(self, belief: np.ndarray, parent=None, action: int = -1):
        self.belief = belief
        self.parent = parent
        self._obs_children = None
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
        belief = self.belief.belief

        best_commit_action, best_commit_value = self._best_commit_from_belief(belief)

        n_samples = min(self.num_simulations, 50)
        observe_values = np.zeros(self.num_observe_actions)
        for k in range(self.num_observe_actions):
            total = 0.0
            model = self.obs_models[k]
            predictive = belief @ model
            predictive = predictive / predictive.sum()
            for _ in range(n_samples):
                obs_idx = int(np.random.choice(len(predictive), p=predictive))
                posterior = model[:, obs_idx] * belief
                posterior = posterior / posterior.sum()
                v = -self.obs_costs[k] + self._multi_step_rollout(posterior, self.rollout_depth)
                total += v
            observe_values[k] = total / n_samples

        best_obs_k = int(np.argmax(observe_values))
        best_obs_value = observe_values[best_obs_k]

        if best_commit_value >= best_obs_value:
            return best_commit_action
        return best_obs_k

    def _tree_policy(self, node: MCTSNode) -> MCTSNode:
        """Select a leaf node using UCB1.

        For observation actions, after selecting an action via UCB1,
        samples an observation outcome proportional to the predictive
        distribution and descends into that child.
        """
        depth = 0
        while depth < self.planning_horizon:
            if node.is_terminal:
                return node

            if not node.children:
                self._expand(node)
                first_child = next(iter(node.children.values()))
                if first_child._obs_children is not None:
                    return self._sample_obs_child(first_child)
                return first_child

            if any(c.visit_count == 0 for c in node.children.values()):
                unvisited = [c for c in node.children.values() if c.visit_count == 0]
                chosen = unvisited[np.random.randint(len(unvisited))]
                if chosen._obs_children is not None:
                    return self._sample_obs_child(chosen)
                return chosen

            best = max(
                node.children.values(),
                key=lambda c: c.ucb1(self.exploration_constant),
            )
            if best._obs_children is not None:
                node = self._sample_obs_child(best)
            else:
                node = best
            depth += 1

        return node

    def _sample_obs_child(self, action_node: MCTSNode) -> MCTSNode:
        """Sample an observation outcome for an observation action node."""
        obs_children = action_node._obs_children
        probs = np.array([oc["prob"] for oc in obs_children.values()])
        probs = probs / probs.sum()
        idx = np.random.choice(len(probs), p=probs)
        key = list(obs_children.keys())[idx]
        action_node.visit_count += 1
        return obs_children[key]["node"]

    def _expand(self, node: MCTSNode):
        """Expand all possible actions from this node.

        For observation actions, creates a stochastic node: each simulation
        samples an observation outcome and descends into the corresponding
        child. All observation outcomes are pre-computed so information gain
        is correctly estimated across the full outcome distribution.
        """
        belief = node.belief

        for k in range(self.num_observe_actions):
            model = self.obs_models[k]
            num_outcomes = model.shape[1]
            obs_children = {}
            for obs_idx in range(num_outcomes):
                prob_obs = float(np.dot(belief, model[:, obs_idx]))
                if prob_obs < 1e-10:
                    continue
                posterior = model[:, obs_idx] * belief
                posterior = posterior / posterior.sum()
                obs_children[obs_idx] = {
                    "belief": posterior,
                    "prob": prob_obs,
                    "node": MCTSNode(belief=posterior, parent=node, action=k),
                }
            action_node = MCTSNode(belief=belief.copy(), parent=node, action=k)
            action_node._obs_children = obs_children
            node.children[k] = action_node

        for i in range(self.num_commit_actions):
            action_id = self.num_observe_actions + i
            child = MCTSNode(belief=belief.copy(), parent=node, action=action_id)
            child.is_terminal = True
            node.children[action_id] = child

    def _evaluate_leaf(self, node: MCTSNode) -> float:
        """Evaluate a leaf node using EFE heuristic + rollout."""
        if node.is_terminal:
            action_idx = node.action - self.num_observe_actions
            return float(np.dot(node.belief, self.commit_rewards[action_idx]))

        return self._efe_rollout(node.belief, self.rollout_depth)

    def _multi_step_rollout(self, belief: np.ndarray, depth: int) -> float:
        """Multi-step rollout that continues observing for the full depth.

        At each step, picks the observation with highest one-step EFE value.
        Returns the maximum of (commit-now, continue-observing) to correctly
        value both early and late commitment strategies.
        """
        best_commit = self._best_commit_value(belief)

        if depth <= 0 or np.max(belief) > 0.99:
            return best_commit

        best_k = 0
        best_v = float("-inf")
        for k in range(self.num_observe_actions):
            v = self._one_step_efe_value(k, belief)
            if v > best_v:
                best_v = v
                best_k = k

        model = self.obs_models[best_k]
        predictive = belief @ model
        predictive = predictive / predictive.sum()
        obs_idx = int(np.random.choice(len(predictive), p=predictive))
        posterior = model[:, obs_idx] * belief
        p_sum = posterior.sum()
        if p_sum < 1e-10:
            posterior = np.ones_like(belief) / len(belief)
        else:
            posterior = posterior / p_sum

        continue_value = -self.obs_costs[best_k] + self._multi_step_rollout(posterior, depth - 1)
        return max(best_commit, continue_value)

    def _efe_rollout(self, belief: np.ndarray, depth: int) -> float:
        """Leaf evaluation rollout for the tree search."""
        return self._multi_step_rollout(belief, depth)

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
