"""
Transition-aware EFE and Planning+IG agents (study stages DS-B/DS-C).

Implements agents 2 and 4 of the predeclared study design in
docs/ideation/2026-08-19-destructive-sensing-design.md (Section 5): the
corrected operator of formal target T1, evaluated recursively at horizon H
exactly like the state-preserving agents in rho_aif/agents/efe.py and
rho_aif/agents/planning_infogain.py.

Where the state-preserving agents score an observation action k with the
observation-only posterior b'_o(s) proportional to O_k(o|s) b(s), these
agents use the joint transition-observation posterior of the JAIR
manuscript's Delta_T definition (paper/full_paper_jair.tex, the paragraph
preceding Proposition prop:factored, and Example ex:destructive):

    b'_{o,T}(s') proportional to sum_s T_k(s'|s) O_k(o|s) b(s)

with two NORMATIVE conventions inherited from the paper:

  * Timing: the observation is emitted from the PRE-transition hidden
    state, so P(o) = sum_s O_k(o|s) b(s); only then does the kernel T_k
    advance the state.
  * Common support: the state-preserving posterior corresponds to the
    identity coupling s' = s. At T_k = I the joint posterior collapses to
    b'_o and both agents here reduce exactly -- same floats, same
    tie-breaks -- to EFEAgent / PlanningInfoGainAgent (verified in
    tests/test_transition_aware.py).

The epistemic term is the mutual information between the observation and
the POST-transition state, in bits (log2), matching the rest of the
codebase:

    IG_T,k(b) = H(T_k^T b) - E_o[ H(b'_{o,T}) ]

For a state-preserving kernel this equals ordinary information gain; for
the destructive drill of Example ex:destructive it is zero (the
post-transition state is known regardless of outcome), which is exactly
what prices the destructive test correctly and recovers V_true = 1 - c
where the naive operator reports V_naive = 2 - c.
"""

import numpy as np
from scipy.stats import entropy as scipy_entropy
from typing import List, Optional, Tuple, Union
from rho_aif.agents.base import BaseAgent


class _TransitionAwareBase(BaseAgent):
    """
    Shared plumbing for transition-aware agents: per-observation-action
    transition kernels T_k (convention T[s, s'] = P(s'|s, k), rows indexing
    the pre-transition state), joint-posterior computation, and the T_k
    belief update applied on step.
    """

    def __init__(
        self,
        observation_models: Union[np.ndarray, List[np.ndarray]],
        env_config: dict,
        transition_models: Optional[List[np.ndarray]] = None,
        initial_belief: Optional[np.ndarray] = None,
    ):
        super().__init__(observation_models, env_config)

        if transition_models is None:
            transition_models = [
                np.eye(self.num_states) for _ in range(self.num_observe_actions)
            ]
        if len(transition_models) != self.num_observe_actions:
            raise ValueError(
                f"Expected {self.num_observe_actions} transition models, "
                f"got {len(transition_models)}"
            )
        self.transition_models = [np.asarray(t, dtype=float) for t in transition_models]
        for t in self.transition_models:
            if t.shape != (self.num_states, self.num_states):
                raise ValueError(
                    f"Transition model must have shape "
                    f"({self.num_states}, {self.num_states}), got {t.shape}"
                )

        self._initial_belief = None if initial_belief is None else np.asarray(
            initial_belief, dtype=float
        )
        if self._initial_belief is not None:
            self.belief.reset(self._initial_belief)

    def reset(self) -> None:
        self.belief.reset(self._initial_belief)

    def update_belief(self, observation: int, obs_action: int = 0) -> None:
        """Belief update through the joint transition-observation kernel.

        Per the paper's timing convention, the likelihood O_k(o|s) weights
        the PRE-transition belief, and the kernel T_k then advances the
        weighted mass to the post-transition variable:

            b'_{o,T}(s') proportional to sum_s T_k(s'|s) O_k(o|s) b(s)
        """
        model_idx = obs_action if obs_action < self.num_observe_actions else 0
        posterior = self._joint_posterior(model_idx, self.belief.belief, observation)
        self.belief.belief = posterior
        self.belief.history.append(posterior.copy())

    def _joint_posterior(
        self, obs_action: int, belief: np.ndarray, obs_idx: int
    ) -> np.ndarray:
        """Normalized b'_{o,T} for one observation outcome."""
        likelihood = self.obs_models[obs_action][:, obs_idx]
        joint = self.transition_models[obs_action].T @ (likelihood * belief)
        norm = joint.sum()
        if norm > 0:
            return joint / norm
        return np.ones(self.num_states) / self.num_states

    def _predictive_prior(self, obs_action: int, belief: np.ndarray) -> np.ndarray:
        """Prior over the post-transition state, (T_k^T b)."""
        return self.transition_models[obs_action].T @ belief


class TransitionAwareEFEAgent(_TransitionAwareBase):
    """
    rho-POMDP agent minimizing transition-aware Expected Free Energy
    (design doc Section 5, agent 2; the T1 corrected operator).

    For each observation action k with transition kernel T_k:
      G(obs_k) = cost_k - IG_T,k(b) + E_o[min_a G(a, b'_{o,T})]
    For each commit action i:
      G(commit_i) = -E_b[reward_i]

    The agent selects argmin over all actions. At T_k = I this is exactly
    EFEAgent (same arithmetic, same tie-breaks).
    """

    def __init__(
        self,
        observation_models: Union[np.ndarray, List[np.ndarray]],
        env_config: dict,
        transition_models: Optional[List[np.ndarray]] = None,
        planning_horizon: int = 4,
        discount: float = 1.0,
        initial_belief: Optional[np.ndarray] = None,
    ):
        super().__init__(
            observation_models, env_config, transition_models, initial_belief
        )
        self.planning_horizon = planning_horizon
        self.discount = discount

    def select_action(self) -> int:
        best_action, _ = self._evaluate(self.belief.belief, depth=0)
        return best_action

    def _evaluate(self, belief: np.ndarray, depth: int):
        """
        Recursively evaluate transition-aware EFE for all actions at a belief.
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
            # transition-aware EFE and Planning+IG(w=1) share a
            # deterministic tie-break (mirrors efe.py).
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
        Transition-aware EFE for one observation action with recursive planning.

        G(obs_k) = cost_k - IG_T,k(b) + E_o[min_a G(a, b'_{o,T}, depth+1)]

        P(o) is computed from the pre-transition belief (the paper's timing
        convention); both the epistemic term and the continuation propagate
        through the joint posterior b'_{o,T}.

        Returns (G, immediate one-step transition-aware info gain in bits).
        """
        model = self.obs_models[obs_action]
        num_outcomes = model.shape[1]
        prior_entropy = scipy_entropy(self._predictive_prior(obs_action, belief), base=2)
        expected_posterior_entropy = 0.0
        expected_continuation = 0.0

        for obs_idx in range(num_outcomes):
            prob_obs = float(np.dot(belief, model[:, obs_idx]))
            if prob_obs < 1e-10:
                continue

            posterior = self._joint_posterior(obs_action, belief, obs_idx)

            expected_posterior_entropy += prob_obs * scipy_entropy(posterior, base=2)

            _, continuation_g = self._evaluate(posterior, depth + 1)
            expected_continuation += prob_obs * continuation_g

        info_gain = prior_entropy - expected_posterior_entropy

        g = self.obs_costs[obs_action] - info_gain + self.discount * expected_continuation
        return g, info_gain


class TransitionAwarePlanningIGAgent(_TransitionAwareBase):
    """
    Multi-step planning with additive transition-aware information gain
    bonus (design doc Section 5, agent 4; rho = w * IG_T(b), H > 1).

    Action evaluation (maximizing expected reward + weighted info gain):
      V(obs_k, b, d) = -cost_k + w * IG_T,k(b) + E_o[max_a V(a, b'_{o,T}, d+1)]
      V(commit_i, b, d) = E_b[reward_i]

    At w = 1 this is the exact negation of TransitionAwareEFEAgent (same
    tie-breaks), mirroring the EFE / Planning+IG(w=1) equivalence of
    tests/test_efe_pig_equivalence.py; at T_k = I it is exactly
    PlanningInfoGainAgent.
    """

    def __init__(
        self,
        observation_models: Union[np.ndarray, List[np.ndarray]],
        env_config: dict,
        transition_models: Optional[List[np.ndarray]] = None,
        planning_horizon: int = 4,
        info_gain_weight: float = 1.0,
        discount: float = 1.0,
        initial_belief: Optional[np.ndarray] = None,
    ):
        super().__init__(
            observation_models, env_config, transition_models, initial_belief
        )
        self.planning_horizon = planning_horizon
        self.info_gain_weight = info_gain_weight
        self.discount = discount

    def select_action(self) -> int:
        best_action, _ = self._evaluate(self.belief.belief, depth=0)
        return best_action

    def _evaluate(self, belief: np.ndarray, depth: int):
        if depth >= self.planning_horizon:
            return self._best_commit_from_belief(belief)

        best_commit_action, best_commit_value = self._best_commit_from_belief(belief)

        best_obs_action = None
        best_obs_value = -float("inf")
        for k in range(self.num_observe_actions):
            v, _ = self._expected_value_of_observe(k, belief, depth)
            # Strict improvement only; ties keep the lower action index so
            # Planning+IG(w=1) matches transition-aware EFE's deterministic
            # tie-break (mirrors planning_infogain.py).
            if v > best_obs_value + 1e-12:
                best_obs_value = v
                best_obs_action = k

        if best_obs_action is not None and best_obs_value > best_commit_value + 1e-12:
            return best_obs_action, best_obs_value
        return best_commit_action, best_commit_value

    def _expected_value_of_observe(
        self, obs_action: int, belief: np.ndarray, depth: int
    ) -> Tuple[float, float]:
        """Return (total_score, immediate one-step transition-aware
        information gain in bits), with P(o) from the pre-transition belief
        and belief propagation through the joint posterior b'_{o,T}."""
        model = self.obs_models[obs_action]
        num_outcomes = model.shape[1]
        prior_entropy = scipy_entropy(self._predictive_prior(obs_action, belief), base=2)
        expected_posterior_entropy = 0.0
        expected_value = -self.obs_costs[obs_action]

        for obs_idx in range(num_outcomes):
            prob_obs = float(np.dot(belief, model[:, obs_idx]))
            if prob_obs < 1e-10:
                continue

            posterior = self._joint_posterior(obs_action, belief, obs_idx)

            expected_posterior_entropy += prob_obs * scipy_entropy(posterior, base=2)

            _, continuation_value = self._evaluate(posterior, depth + 1)
            expected_value += prob_obs * self.discount * continuation_value

        info_gain = prior_entropy - expected_posterior_entropy
        expected_value += self.info_gain_weight * info_gain

        return expected_value, info_gain
