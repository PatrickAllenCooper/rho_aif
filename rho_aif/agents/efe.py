"""
EFE agent (rho-POMDP with rho = Expected Free Energy).

Selects actions by minimizing Expected Free Energy (EFE), which decomposes
into pragmatic value (goal alignment) and epistemic value (information gain)
without any tunable weight parameter. Uses recursive multi-step planning.

Supports multiple observation actions, each with its own observation model
and cost. The agent evaluates EFE for every observation action and every
commit action, selecting the global argmin.
"""

import numpy as np
from scipy.stats import entropy as scipy_entropy
from typing import List, Tuple, Union
from rho_aif.belief import BeliefState
from rho_aif.agents.base import BaseAgent
from rho_aif.audit import ActionAudit, DecisionAudit


class EFEAgent(BaseAgent):
    """
    rho-POMDP agent minimizing Expected Free Energy.

    For each observation action k:
      G(obs_k) = cost_k - info_gain_k + E_o[min_a G(a, posterior)]
    For each commit action i:
      G(commit_i) = -E_b[reward_i]

    The agent selects argmin over all actions.
    """

    def __init__(
        self,
        observation_models: Union[np.ndarray, List[np.ndarray]],
        env_config: dict,
        planning_horizon: int = 4,
        discount: float = 1.0,
        record_audit: bool = False,
    ):
        super().__init__(observation_models, env_config)
        self.planning_horizon = planning_horizon
        self.discount = discount
        self.record_audit = record_audit
        self.audit_log: List[DecisionAudit] = []

    def select_action(self) -> int:
        belief = self.belief.belief
        candidates = self._decision_candidates(belief) if self.record_audit else None
        best_action, _ = self._evaluate(belief, depth=0)
        if candidates is not None:
            for c in candidates:
                c.chosen = c.action == best_action
            self.audit_log.append(
                DecisionAudit(step=len(self.audit_log), candidates=candidates, chosen_action=best_action)
            )
        return best_action

    def _decision_candidates(self, belief: np.ndarray) -> List[ActionAudit]:
        """Top-level (depth-0) task/information decomposition, on the same
        ``ActionAudit`` schema as ``PlanningInfoGainAgent`` -- EFE minimizes
        G, so ``total_score = -G`` recovers exactly the Planning+IG(w=1)
        value, making the two families' audit records directly comparable."""
        candidates: List[ActionAudit] = []
        for i in range(self.num_commit_actions):
            expected_reward = float(np.dot(belief, self.commit_rewards[i]))
            candidates.append(
                ActionAudit(
                    action=self.num_observe_actions + i,
                    kind="commit",
                    sensing_cost=0.0,
                    info_gain_weight=1.0,
                    expected_info_gain=0.0,
                    weighted_info_gain=0.0,
                    expected_task_value=expected_reward,
                    total_score=expected_reward,
                )
            )
        for k in range(self.num_observe_actions):
            g, info_gain = self._efe_observe(k, belief, depth=0)
            total_score = -g
            candidates.append(
                ActionAudit(
                    action=k,
                    kind="observe",
                    sensing_cost=self.obs_costs[k],
                    info_gain_weight=1.0,
                    expected_info_gain=info_gain,
                    weighted_info_gain=info_gain,
                    expected_task_value=total_score - info_gain,
                    total_score=total_score,
                )
            )
        return candidates

    def _evaluate(self, belief: np.ndarray, depth: int):
        """
        Recursively evaluate EFE for all available actions at a given belief.
        Returns (best_action, best_G).
        """
        if depth >= self.planning_horizon:
            return self._best_commit_efe(belief)

        best_commit_action, best_commit_g = self._best_commit_efe(belief)

        best_obs_action = None
        best_obs_g = float("inf")
        for k in range(self.num_observe_actions):
            g, _ = self._efe_observe(k, belief, depth)
            # Strict improvement only; ties keep the lower action index so
            # EFE and Planning+IG(w=1) share a deterministic tie-break.
            if g < best_obs_g - 1e-12:
                best_obs_g = g
                best_obs_action = k

        if best_obs_action is not None and best_obs_g < best_commit_g - 1e-12:
            return best_obs_action, best_obs_g
        return best_commit_action, best_commit_g

    def _best_commit_efe(self, belief: np.ndarray):
        """Find the commit action with lowest EFE (highest expected reward)."""
        best_g = float("inf")
        best_action = self.num_observe_actions

        for i in range(self.num_commit_actions):
            expected_reward = float(np.dot(belief, self.commit_rewards[i]))
            g = -expected_reward
            if g < best_g:
                best_g = g
                best_action = self.num_observe_actions + i
        return best_action, best_g

    def _efe_observe(self, obs_action: int, belief: np.ndarray, depth: int) -> Tuple[float, float]:
        """
        Compute EFE for a specific observation action with recursive planning.

        G(obs_k) = cost_k - info_gain_k(belief) + E_o[min_a G(a, posterior, depth+1)]

        Returns (G, immediate one-step information gain in bits).
        """
        model = self.obs_models[obs_action]
        num_outcomes = model.shape[1]
        prior_entropy = scipy_entropy(belief, base=2)
        expected_posterior_entropy = 0.0
        expected_continuation = 0.0

        for obs_idx in range(num_outcomes):
            prob_obs = float(np.dot(belief, model[:, obs_idx]))
            if prob_obs < 1e-10:
                continue

            posterior = model[:, obs_idx] * belief
            posterior = posterior / posterior.sum()

            expected_posterior_entropy += prob_obs * scipy_entropy(posterior, base=2)

            _, continuation_g = self._evaluate(posterior, depth + 1)
            expected_continuation += prob_obs * continuation_g

        info_gain = prior_entropy - expected_posterior_entropy

        g = self.obs_costs[obs_action] - info_gain + self.discount * expected_continuation
        return g, info_gain
