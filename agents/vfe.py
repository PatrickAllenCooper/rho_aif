"""
Variational Free Energy agent (rho-POMDP with rho = Expected Free Energy).

Selects actions by minimizing Expected Free Energy (EFE), which decomposes
into pragmatic value (goal alignment) and epistemic value (information gain)
without any tunable weight parameter. Uses recursive multi-step planning.

The key distinction from InformationGainAgent:
  - No hand-tuned epistemic weight: both pragmatic and epistemic terms emerge
    from the same EFE objective.
  - Multi-step planning horizon: recursively evaluates observation sequences
    rather than one-step lookahead.
  - Pragmatic value uses log-preferences derived from the reward structure,
    not raw expected reward.
"""

import numpy as np
from scipy.stats import entropy as scipy_entropy
from belief import BeliefState
from agents.base import BaseAgent


class VFEAgent(BaseAgent):
    """
    rho-POMDP agent minimizing Expected Free Energy.

    G(a) = pragmatic_cost(a) - info_gain(a) + E[continuation(a)]

    For OBSERVE:  G = obs_cost - info_gain + E_o[min_a' G(a', posterior)]
    For COMMIT_X: G = -E_b[reward(X)]   (log-preferences proportional to reward)

    The agent recursively evaluates action sequences up to a planning horizon,
    choosing the action that minimizes total expected free energy. Information
    seeking emerges naturally: high belief entropy drives high info_gain,
    reducing G(observe) relative to G(commit), incentivizing exploration.
    As beliefs sharpen, info_gain decays and pragmatic commit value dominates.
    """

    def __init__(
        self,
        observation_model: np.ndarray,
        env_config: dict,
        planning_horizon: int = 4,
    ):
        super().__init__(observation_model, env_config)
        self.planning_horizon = planning_horizon

    def select_action(self) -> int:
        best_action, _ = self._evaluate(self.belief.belief, depth=0)
        return best_action

    def _evaluate(self, belief: np.ndarray, depth: int):
        """
        Recursively evaluate EFE for all available actions at a given belief.

        Returns (best_action, best_G).
        """
        if depth >= self.planning_horizon:
            return self._best_commit(belief)

        best_commit_action, best_commit_g = self._best_commit(belief)
        observe_g = self._efe_observe(belief, depth)

        if observe_g < best_commit_g:
            return 0, observe_g
        return best_commit_action, best_commit_g

    def _best_commit(self, belief: np.ndarray):
        """
        Find the commit action with lowest EFE (highest expected reward).

        Uses the commit reward matrix to compute expected reward for each
        commit action, then returns G = -expected_reward.
        """
        best_g = float("inf")
        best_action = 1

        for i in range(self.num_commit_actions):
            expected_reward = float(np.dot(belief, self.commit_rewards[i]))
            g = -expected_reward
            if g < best_g:
                best_g = g
                best_action = i + 1
        return best_action, best_g

    def _efe_observe(self, belief: np.ndarray, depth: int) -> float:
        """
        Compute EFE for the observe action with recursive planning.

        G(observe) = obs_cost - info_gain(belief) + E_o[min_a G(a, posterior, depth+1)]

        The info_gain term captures intrinsic epistemic value (uncertainty
        reduction valued for its own sake). The continuation term captures
        instrumental value (better decisions from better beliefs). Together
        they produce principled exploration without a tunable weight.
        """
        prior_entropy = scipy_entropy(belief, base=2)
        expected_posterior_entropy = 0.0
        expected_continuation = 0.0

        for obs_idx in range(self.num_obs):
            prob_obs = float(np.dot(belief, self.obs_model[:, obs_idx]))
            if prob_obs < 1e-10:
                continue

            posterior = self.obs_model[:, obs_idx] * belief
            posterior = posterior / posterior.sum()

            expected_posterior_entropy += prob_obs * scipy_entropy(posterior, base=2)

            _, continuation_g = self._evaluate(posterior, depth + 1)
            expected_continuation += prob_obs * continuation_g

        info_gain = prior_entropy - expected_posterior_entropy

        return self.config["observation_cost"] - info_gain + expected_continuation
