"""
Thompson Sampling agent for observe-then-commit POMDPs.

At each step, samples N hidden states from the current belief distribution,
determines the optimal action for each sample, and selects the majority-vote
action. For commit actions, the optimal action given a known state is the
commit with highest reward for that state. For observation actions, the agent
observes if the expected value of perfect information exceeds the observation
cost.
"""

import numpy as np
from scipy.stats import entropy as scipy_entropy
from typing import Union, List
from rho_aif.agents.base import BaseAgent


class ThompsonSamplingAgent(BaseAgent):
    """
    Thompson Sampling for observe-then-commit POMDPs.

    Each call to select_action():
      1. Draws N samples from the current belief distribution.
      2. For each sample, computes the optimal action assuming that
         sampled state is the true state.
      3. Returns the action with the most votes.

    The per-sample decision rule:
      - Compute the best commit reward for the sampled state.
      - For each observation action, compute the expected value of
        observing (EVSI) given the sampled state: the gain from
        resolving uncertainty about that state minus the cost.
      - If any observation's EVSI exceeds 0, choose the best one;
        otherwise commit.
    """

    def __init__(
        self,
        observation_models: Union[np.ndarray, List[np.ndarray]],
        env_config: dict,
        num_samples: int = 100,
    ):
        super().__init__(observation_models, env_config)
        self.num_samples = num_samples

    def select_action(self) -> int:
        belief = self.belief.belief
        n_actions = self.num_observe_actions + self.num_commit_actions
        votes = np.zeros(n_actions, dtype=int)

        sampled_states = np.random.choice(
            self.num_states, size=self.num_samples, p=belief
        )

        for s in sampled_states:
            action = self._optimal_action_for_state(s, belief)
            votes[action] += 1

        return int(np.argmax(votes))

    def _optimal_action_for_state(self, sampled_state: int, belief: np.ndarray) -> int:
        best_commit_action = self.num_observe_actions
        best_commit_reward = float("-inf")
        for i in range(self.num_commit_actions):
            r = self.commit_rewards[i, sampled_state]
            if r > best_commit_reward:
                best_commit_reward = r
                best_commit_action = self.num_observe_actions + i

        best_obs_action = None
        best_obs_value = float("-inf")
        for k in range(self.num_observe_actions):
            evsi = self._evsi_for_state(k, sampled_state, belief)
            value = evsi - self.obs_costs[k]
            if value > best_obs_value:
                best_obs_value = value
                best_obs_action = k

        if best_obs_value > 0:
            return best_obs_action
        return best_commit_action

    def _evsi_for_state(
        self, obs_action: int, sampled_state: int, belief: np.ndarray
    ) -> float:
        """
        Expected value of sample information for observation action k
        given that the true state is sampled_state.

        Computes how much better the agent can commit after observing,
        averaged over the observation distribution for that state.
        """
        model = self.obs_models[obs_action]
        num_outcomes = model.shape[1]

        current_best = float("-inf")
        for i in range(self.num_commit_actions):
            r = float(np.dot(belief, self.commit_rewards[i]))
            if r > current_best:
                current_best = r

        expected_post_value = 0.0
        for obs_idx in range(num_outcomes):
            prob_obs = model[sampled_state, obs_idx]
            if prob_obs < 1e-10:
                continue

            posterior = model[:, obs_idx] * belief
            p_sum = posterior.sum()
            if p_sum < 1e-10:
                continue
            posterior = posterior / p_sum

            post_best = float("-inf")
            for i in range(self.num_commit_actions):
                r = float(np.dot(posterior, self.commit_rewards[i]))
                if r > post_best:
                    post_best = r

            expected_post_value += prob_obs * post_best

        return expected_post_value - current_best
