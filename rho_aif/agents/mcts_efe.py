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
from rho_aif.agents.base import BaseAgent
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
        exploration_constant: Optional[float] = None,
    ):
        super().__init__(observation_models, env_config)
        self.num_simulations = num_simulations
        self.planning_horizon = planning_horizon
        self.rollout_depth = rollout_depth
        # UCB1's exploration term must be commensurate with the value scale
        # or high-magnitude penalties (Tiger's -100) freeze exploration.
        # Default follows POMCP (Silver and Veness 2010): c = reward range.
        if exploration_constant is None:
            rewards = np.asarray(self.commit_rewards, dtype=float)
            exploration_constant = float(max(1.0, rewards.max() - rewards.min()))
        self.exploration_constant = exploration_constant

    def select_action(self) -> int:
        """Run num_simulations MCTS iterations from the root belief and
        return the root action with the highest visit count."""
        belief = self.belief.belief

        root = MCTSNode(belief=belief.copy())
        self._expand(root)

        for _ in range(self.num_simulations):
            self._simulate(root, depth=0)

        # Root action by estimated value. Commit children carry exact values
        # and observe children carry max-backup estimates, so the value
        # criterion is the consistent one (visit counts are distorted by the
        # range-scaled exploration term).
        best_child = max(
            root.children.values(),
            key=lambda c: (c.mean_value, c.visit_count),
        )
        return best_child.action

    def _simulate(self, node: MCTSNode, depth: int) -> float:
        """One MCTS iteration from a belief node: UCB1 selection over action
        children, exact per-node information gain as immediate reward for
        observation actions (so the tree optimizes the EFE objective), an
        EFE-greedy rollout at the frontier, and max-backup (Bellman-style)
        value propagation. Sampled-return averaging would contaminate branch
        values with the forced exploration of dominated commits, which the
        asymmetric penalties of observe-then-commit problems punish severely;
        backing up the max over action-children means estimates the value of
        acting optimally below this node instead."""
        if depth >= self.planning_horizon:
            value = self._efe_rollout(node.belief, self.rollout_depth)
            node.visit_count += 1
            node.total_value += value
            return value

        if not node.children:
            self._expand(node)
            value = self._efe_rollout(node.belief, self.rollout_depth)
            node.visit_count += 1
            node.total_value += value
            return value

        unvisited = [c for c in node.children.values() if c.visit_count == 0]
        if unvisited:
            chosen = unvisited[np.random.randint(len(unvisited))]
        else:
            chosen = max(
                node.children.values(),
                key=lambda c: c.ucb1(self.exploration_constant),
            )

        if not chosen.is_terminal:
            # Commit children hold their exact value from expansion and need
            # no further sampling; only observe children are refined.
            k = chosen.action
            info_gain = self._one_step_info_gain(k, node.belief)
            child = self._sample_obs_child(chosen)
            sampled = -self.obs_costs[k] + info_gain + self._simulate(child, depth + 1)
            chosen.visit_count += 1
            chosen.total_value += sampled

        node.visit_count += 1
        value = max(c.mean_value for c in node.children.values())
        node.total_value = value * node.visit_count
        return value

    def _one_step_info_gain(self, obs_action: int, belief: np.ndarray) -> float:
        """Exact expected information gain (bits) of one observation action."""
        model = self.obs_models[obs_action]
        num_outcomes = model.shape[1]
        prior_entropy = scipy_entropy(belief, base=2)
        expected_posterior_entropy = 0.0
        for obs_idx in range(num_outcomes):
            prob_obs = float(np.dot(belief, model[:, obs_idx]))
            if prob_obs < 1e-10:
                continue
            posterior = model[:, obs_idx] * belief
            posterior = posterior / posterior.sum()
            expected_posterior_entropy += prob_obs * scipy_entropy(posterior, base=2)
        return prior_entropy - expected_posterior_entropy

    def _sample_obs_child(self, action_node: MCTSNode) -> MCTSNode:
        """Sample an observation outcome for an observation action node."""
        obs_children = action_node._obs_children
        probs = np.array([oc["prob"] for oc in obs_children.values()])
        probs = probs / probs.sum()
        idx = np.random.choice(len(probs), p=probs)
        key = list(obs_children.keys())[idx]
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
            # Commit values are deterministic given the belief, so seed the
            # node with its exact value instead of leaving it to forced
            # first-visit exploration (whose single sample would carry the
            # same value anyway).
            child.visit_count = 1
            child.total_value = float(np.dot(belief, self.commit_rewards[i]))
            node.children[action_id] = child

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

        # The rollout must value observation steps under the same EFE
        # objective as the tree (cost plus information gain plus
        # continuation); omitting the epistemic term here systematically
        # biases frontier values toward early commitment.
        info_gain = self._one_step_info_gain(best_k, belief)
        continue_value = (
            -self.obs_costs[best_k]
            + info_gain
            + self._multi_step_rollout(posterior, depth - 1)
        )
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
