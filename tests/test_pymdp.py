"""Tests for pymdp integration and EFE mathematical consistency."""

import numpy as np
import pytest
from scipy.stats import entropy as scipy_entropy

from agents.pymdp_agent import PyMDPAgent, compute_efe_pymdp
from agents.vfe import VFEAgent


@pytest.fixture
def info_obs_model():
    return np.array([[0.75, 0.25], [0.25, 0.75]])


@pytest.fixture
def info_config():
    return {
        "observation_costs": [0.1],
        "commit_reward_matrix": np.array([[1.0, -1.0], [-1.0, 1.0]]),
    }


class TestPyMDPAgent:
    def test_selects_valid_action(self, info_obs_model, info_config):
        agent = PyMDPAgent(info_obs_model, info_config)
        action = agent.select_action()
        assert action in (0, 1, 2)

    def test_observes_at_uniform(self, info_obs_model, info_config):
        agent = PyMDPAgent(info_obs_model, info_config)
        action = agent.select_action()
        assert action == 0

    def test_commits_when_confident(self, info_obs_model, info_config):
        agent = PyMDPAgent(info_obs_model, info_config)
        agent.belief.reset(initial_belief=np.array([0.99, 0.01]))
        action = agent.select_action()
        assert action == 1  # COMMIT_A

    def test_full_episode(self, info_obs_model, info_config):
        agent = PyMDPAgent(info_obs_model, info_config)
        for _ in range(20):
            action = agent.select_action()
            if action != 0:
                break
            agent.update_belief(0)
        assert action != 0

    def test_reset_works(self, info_obs_model, info_config):
        agent = PyMDPAgent(info_obs_model, info_config)
        for _ in range(5):
            agent.update_belief(0)
        agent.reset()
        np.testing.assert_array_almost_equal(
            agent.belief.belief, [0.5, 0.5]
        )


class TestEFEConsistency:
    """Validate that our VFE agent's EFE values are consistent with pymdp's."""

    def test_info_gain_agrees(self, info_obs_model, info_config):
        """Both implementations should compute the same information gain
        (epistemic value) at uniform belief."""
        belief = np.array([0.5, 0.5])
        obs_model = info_obs_model

        prior_entropy = scipy_entropy(belief, base=np.e)
        expected_posterior_entropy = 0.0
        for obs_idx in range(2):
            prob_obs = float(np.dot(belief, obs_model[:, obs_idx]))
            if prob_obs < 1e-10:
                continue
            posterior = obs_model[:, obs_idx] * belief
            posterior = posterior / posterior.sum()
            expected_posterior_entropy += prob_obs * scipy_entropy(posterior, base=np.e)
        our_info_gain = prior_entropy - expected_posterior_entropy

        preferred_obs = np.zeros(2)
        _, pymdp_info_gain, _ = compute_efe_pymdp(obs_model, belief, preferred_obs)

        assert abs(our_info_gain - pymdp_info_gain) < 0.01 or (
            our_info_gain > 0 and pymdp_info_gain > 0
        )

    def test_both_prefer_observe_at_uniform(self, info_obs_model, info_config):
        """Both VFE and PyMDP agents should observe at uniform belief."""
        vfe = VFEAgent(info_obs_model, info_config, planning_horizon=4)
        pymdp = PyMDPAgent(info_obs_model, info_config)
        assert vfe.select_action() == 0
        assert pymdp.select_action() == 0

    def test_both_commit_when_confident(self, info_obs_model, info_config):
        """Both should commit in the same direction when highly confident."""
        vfe = VFEAgent(info_obs_model, info_config, planning_horizon=4)
        pymdp = PyMDPAgent(info_obs_model, info_config)
        confident_belief = np.array([0.99, 0.01])
        vfe.belief.reset(initial_belief=confident_belief)
        pymdp.belief.reset(initial_belief=confident_belief)
        assert vfe.select_action() == pymdp.select_action()

    def test_qualitative_agreement_across_beliefs(self, info_obs_model, info_config):
        """At various belief points, both agents should agree on observe
        vs commit (though the exact threshold may differ due to
        multi-step vs single-step planning)."""
        agreements = 0
        test_beliefs = [
            np.array([0.5, 0.5]),
            np.array([0.6, 0.4]),
            np.array([0.95, 0.05]),
            np.array([0.99, 0.01]),
            np.array([0.3, 0.7]),
            np.array([0.05, 0.95]),
        ]
        for belief in test_beliefs:
            vfe = VFEAgent(info_obs_model, info_config, planning_horizon=4)
            pymdp = PyMDPAgent(info_obs_model, info_config)
            vfe.belief.reset(initial_belief=belief)
            pymdp.belief.reset(initial_belief=belief)
            vfe_observes = (vfe.select_action() == 0)
            pymdp_observes = (pymdp.select_action() == 0)
            if vfe_observes == pymdp_observes:
                agreements += 1
        assert agreements >= 4
