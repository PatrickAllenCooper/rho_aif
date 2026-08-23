"""Tests for reward-relevance-weighted information gain.

The manuscript describes this variant as the principled fix for the
DistractorDiagnosis failure, where an information-gain agent spends sensing
budget on a test that is informative about a hidden factor no commit action
pays for. The variant scores information gain on the marginal over
reward-equivalence classes of hidden states, derived from the commit reward
matrix alone.

Two invariants matter most. On an environment where no two states are
reward-equivalent the variant must reduce exactly to ordinary information
gain, and belief dynamics must be untouched in every case, since only the
epistemic scoring term changes.
"""

import numpy as np
import pytest
from scipy.stats import entropy as scipy_entropy

from rho_aif.agents.efe import EFEAgent
from rho_aif.agents.planning_infogain import PlanningInfoGainAgent
from rho_aif.benchmark import get_obs_models, make_env_config
from rho_aif.environments.diagnosis import DiagnosisEnv
from rho_aif.environments.distractor_diagnosis import DistractorDiagnosisEnv
from rho_aif.scoring import reward_equivalence_classes, reward_relevant_marginal


class TestPartition:
    def test_distractor_partition_collapses_the_nuisance_bit(self):
        """State index is condition * 2 + nuisance, and the commit reward
        matrix has identical columns 2c and 2c+1, so the partition must
        recover the four conditions and drop the nuisance bit."""
        env = DistractorDiagnosisEnv()
        config = make_env_config(env)
        classes = reward_equivalence_classes(config["commit_reward_matrix"])
        assert len(classes) == config["commit_reward_matrix"].shape[1]
        for condition in range(env.num_conditions):
            assert classes[2 * condition] == classes[2 * condition + 1]
        assert len(set(classes.tolist())) == env.num_conditions

    def test_no_reward_equivalent_states_gives_a_permutation(self):
        env = DiagnosisEnv()
        config = make_env_config(env)
        classes = reward_equivalence_classes(config["commit_reward_matrix"])
        assert sorted(classes.tolist()) == list(range(len(classes)))

    def test_marginal_sums_belief_within_class(self):
        matrix = np.array([[1.0, 1.0, 0.0, 0.0], [2.0, 2.0, 5.0, 5.0]])
        classes = reward_equivalence_classes(matrix)
        belief = np.array([0.1, 0.2, 0.3, 0.4])
        marginal = reward_relevant_marginal(belief, classes, int(classes.max()) + 1)
        assert marginal.sum() == pytest.approx(1.0)
        assert sorted(marginal.tolist()) == pytest.approx([0.3, 0.7])

    def test_rejects_non_matrix_input(self):
        with pytest.raises(ValueError):
            reward_equivalence_classes(np.array([1.0, 2.0, 3.0]))


class TestScoringTerm:
    def test_entropy_ignores_within_class_uncertainty(self):
        env = DistractorDiagnosisEnv()
        config = make_env_config(env)
        obs_models = get_obs_models(env)
        agent = EFEAgent(obs_models, config, planning_horizon=2, reward_relevant_info=True)

        # All mass on one condition, split evenly across its nuisance bit.
        belief = np.zeros(config["commit_reward_matrix"].shape[1])
        belief[0] = belief[1] = 0.5
        assert agent._info_entropy(belief) == pytest.approx(0.0, abs=1e-12)
        # Ordinary state entropy sees a full bit of uncertainty here.
        assert scipy_entropy(belief, base=2) == pytest.approx(1.0)

    def test_reduces_to_ordinary_info_gain_without_equivalent_states(self):
        env = DiagnosisEnv()
        config = make_env_config(env)
        obs_models = get_obs_models(env)
        plain = EFEAgent(obs_models, config, planning_horizon=3)
        relevant = EFEAgent(obs_models, config, planning_horizon=3, reward_relevant_info=True)
        rng = np.random.RandomState(0)
        for _ in range(20):
            belief = rng.dirichlet(np.ones(config["commit_reward_matrix"].shape[1]))
            assert relevant._info_entropy(belief) == pytest.approx(
                plain._info_entropy(belief), abs=1e-12
            )

    def test_default_is_off(self):
        env = DistractorDiagnosisEnv()
        config = make_env_config(env)
        obs_models = get_obs_models(env)
        for agent in (
            EFEAgent(obs_models, config, planning_horizon=2),
            PlanningInfoGainAgent(obs_models, config, planning_horizon=2, info_gain_weight=5.0),
        ):
            assert agent.reward_relevant_info is False
            belief = np.full(config["commit_reward_matrix"].shape[1], 0.125)
            assert agent._info_entropy(belief) == pytest.approx(
                scipy_entropy(belief, base=2)
            )


class TestBeliefDynamicsUnchanged:
    def test_continuation_posterior_is_the_full_joint(self):
        """Only the scoring term differs. The posterior propagated into the
        continuation must remain the full joint state posterior, so the two
        variants track identical beliefs given identical observations."""
        env = DistractorDiagnosisEnv()
        config = make_env_config(env)
        obs_models = get_obs_models(env)
        plain = EFEAgent(obs_models, config, planning_horizon=3)
        relevant = EFEAgent(obs_models, config, planning_horizon=3, reward_relevant_info=True)

        rng = np.random.RandomState(3)
        for _ in range(15):
            obs_action = int(rng.randint(0, plain.num_observe_actions))
            observation = int(rng.randint(0, plain.num_obs))
            plain.update_belief(observation, obs_action)
            relevant.update_belief(observation, obs_action)
            np.testing.assert_allclose(
                plain.belief.belief, relevant.belief.belief, atol=1e-12
            )

    def test_distractor_test_earns_no_information_credit(self):
        """The substantive assertion.

        On DistractorDiagnosis the distractor test is informative only about
        the reward-irrelevant nuisance bit. Under ordinary scoring it earns a
        positive information-gain credit, which is exactly the failure the
        manuscript reports. Under relevance weighting it must earn none, and
        its expected free energy must rise by the full amount of that credit.
        """
        env = DistractorDiagnosisEnv()
        config = make_env_config(env)
        obs_models = get_obs_models(env)
        plain = EFEAgent(obs_models, config, planning_horizon=3)
        relevant = EFEAgent(obs_models, config, planning_horizon=3, reward_relevant_info=True)

        belief = np.full(config["commit_reward_matrix"].shape[1], 0.125)
        k = env.distractor_test_idx
        g_plain, ig_plain = plain._efe_observe(k, belief, 0)
        g_relevant, ig_relevant = relevant._efe_observe(k, belief, 0)

        assert ig_plain > 0.05
        assert ig_relevant == pytest.approx(0.0, abs=1e-12)
        assert g_relevant == pytest.approx(g_plain + ig_plain, abs=1e-9)

        # A task test, by contrast, must score identically under both.
        task = 0 if k != 0 else 1
        assert relevant._efe_observe(task, belief, 0)[1] == pytest.approx(
            plain._efe_observe(task, belief, 0)[1], abs=1e-12
        )

    def test_planning_infogain_accepts_the_flag(self):
        env = DistractorDiagnosisEnv()
        config = make_env_config(env)
        obs_models = get_obs_models(env)
        agent = PlanningInfoGainAgent(
            obs_models, config, planning_horizon=3, info_gain_weight=5.0,
            reward_relevant_info=True,
        )
        assert agent.reward_relevant_info is True
        action = agent.select_action()
        assert 0 <= action < agent.num_observe_actions + agent.num_commit_actions
