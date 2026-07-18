"""
Epistemic-only agent: ablation of EFE that removes the pragmatic (reward) term
from observation action evaluation, retaining only information gain plus
recursive continuation.

This ablation tests whether EFE's advantage comes from the epistemic term
alone or from its specific combination with the pragmatic term.

Action evaluation (minimizing epistemic EFE only):
  G(obs_k, b, d) = c_k - I_k(b) + E_o[min_a G(a, posterior, d+1)]
  G(commit_i, b, d) = 0   (no reward consideration for comparing against observe)

At the leaf (depth >= H), the agent commits to the most-likely state.
"""

import numpy as np
from scipy.stats import entropy as scipy_entropy
from typing import Union, List
from rho_aif.agents.base import BaseAgent


class EpistemicOnlyAgent(BaseAgent):
    """
    Ablation: recursive planning using only information gain, no reward signal.

    Observation actions are evaluated by their epistemic value (information
    gain + recursive continuation). Commit actions have G = 0 (the agent
    commits only when no observation action offers positive information gain).
    When committing, selects the highest-probability state.
    """

    def __init__(
        self,
        observation_models: Union[np.ndarray, List[np.ndarray]],
        env_config: dict,
        planning_horizon: int = 4,
    ):
        super().__init__(observation_models, env_config)
        self.planning_horizon = planning_horizon

    def select_action(self) -> int:
        best_action, _ = self._evaluate(self.belief.belief, depth=0)
        return best_action

    def _evaluate(self, belief: np.ndarray, depth: int):
        if depth >= self.planning_horizon:
            return self._best_commit_from_belief(belief)

        best_commit_action, _ = self._best_commit_from_belief(belief)
        best_commit_g = 0.0

        best_obs_action = None
        best_obs_g = float("inf")
        for k in range(self.num_observe_actions):
            g = self._efe_observe(k, belief, depth)
            if g < best_obs_g:
                best_obs_g = g
                best_obs_action = k

        if best_obs_g < best_commit_g:
            return best_obs_action, best_obs_g
        return best_commit_action, best_commit_g

    def _efe_observe(self, obs_action: int, belief: np.ndarray, depth: int) -> float:
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
        return self.obs_costs[obs_action] - info_gain + expected_continuation
