"""
Multi-step planning agent with information gain bonus (rho-POMDP with rho = w * I(b), H > 1).

Combines the recursive tree-search structure of PlanningAgent with an additive
information gain bonus at each observation step. This is the critical
apples-to-apples baseline: same planning depth as the EFE agent, same epistemic
bonus concept as InfoGainAgent, but as an additive weighted term rather than
EFE's joint objective.

Action evaluation (maximizing expected reward + weighted info gain):
  V(obs_k, b, d) = -cost_k + w * I_k(b) + E_o[max_a V(a, posterior, d+1)]
  V(commit_i, b, d) = E_b[reward_i]
"""

import numpy as np
from scipy.stats import entropy as scipy_entropy
from typing import List, Tuple, Union
from rho_aif.agents.base import BaseAgent
from rho_aif.audit import ActionAudit, DecisionAudit


class PlanningInfoGainAgent(BaseAgent):
    """
    Multi-step planning with additive information gain bonus.

    At each recursive step, the value of an observation action includes
    both the expected downstream reward AND a weighted information gain
    term. Isolates whether the EFE agent's advantage is just "IG + deeper search."
    """

    def __init__(
        self,
        observation_models: Union[np.ndarray, List[np.ndarray]],
        env_config: dict,
        planning_horizon: int = 4,
        info_gain_weight: float = 1.0,
        discount: float = 1.0,
        record_audit: bool = False,
    ):
        super().__init__(observation_models, env_config)
        self.planning_horizon = planning_horizon
        self.info_gain_weight = info_gain_weight
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
        """Top-level (depth-0) task/information decomposition of every candidate action."""
        candidates: List[ActionAudit] = []
        for i in range(self.num_commit_actions):
            value = float(np.dot(belief, self.commit_rewards[i]))
            candidates.append(
                ActionAudit(
                    action=self.num_observe_actions + i,
                    kind="commit",
                    sensing_cost=0.0,
                    info_gain_weight=self.info_gain_weight,
                    expected_info_gain=0.0,
                    weighted_info_gain=0.0,
                    expected_task_value=value,
                    total_score=value,
                )
            )
        for k in range(self.num_observe_actions):
            total_score, info_gain = self._expected_value_of_observe(k, belief, depth=0)
            weighted_ig = self.info_gain_weight * info_gain
            candidates.append(
                ActionAudit(
                    action=k,
                    kind="observe",
                    sensing_cost=self.obs_costs[k],
                    info_gain_weight=self.info_gain_weight,
                    expected_info_gain=info_gain,
                    weighted_info_gain=weighted_ig,
                    expected_task_value=total_score - weighted_ig,
                    total_score=total_score,
                )
            )
        return candidates

    def _evaluate(self, belief: np.ndarray, depth: int):
        if depth >= self.planning_horizon:
            return self._best_commit_from_belief(belief)

        best_commit_action, best_commit_value = self._best_commit_from_belief(belief)

        best_obs_action = None
        best_obs_value = -float("inf")
        for k in range(self.num_observe_actions):
            v, _ = self._expected_value_of_observe(k, belief, depth)
            # Strict improvement only; ties keep the lower action index so
            # Planning+IG(w=1) matches EFE's deterministic tie-break.
            if v > best_obs_value + 1e-12:
                best_obs_value = v
                best_obs_action = k

        if best_obs_action is not None and best_obs_value > best_commit_value + 1e-12:
            return best_obs_action, best_obs_value
        return best_commit_action, best_commit_value

    def _expected_value_of_observe(
        self, obs_action: int, belief: np.ndarray, depth: int
    ) -> Tuple[float, float]:
        """Return (total_score, immediate one-step information gain in bits)."""
        model = self.obs_models[obs_action]
        num_outcomes = model.shape[1]
        prior_entropy = scipy_entropy(belief, base=2)
        expected_posterior_entropy = 0.0
        expected_value = -self.obs_costs[obs_action]

        for obs_idx in range(num_outcomes):
            prob_obs = float(np.dot(belief, model[:, obs_idx]))
            if prob_obs < 1e-10:
                continue

            posterior = model[:, obs_idx] * belief
            posterior = posterior / posterior.sum()

            expected_posterior_entropy += prob_obs * scipy_entropy(posterior, base=2)

            _, continuation_value = self._evaluate(posterior, depth + 1)
            expected_value += prob_obs * self.discount * continuation_value

        info_gain = prior_entropy - expected_posterior_entropy
        expected_value += self.info_gain_weight * info_gain

        return expected_value, info_gain
