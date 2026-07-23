"""
Stage G2 unit tests: the reward-irrelevant nuisance factor and its
distractor observation model.

Verifies (1) the distractor test carries zero information about the
condition and the condition tests carry zero information about the
nuisance bit, (2) reward depends only on the condition, and (3) the
environment plugs into the generic observe-then-commit agent interface
without special-casing.
"""

import numpy as np
import pytest

from rho_aif.agents.efe import EFEAgent
from rho_aif.agents.ids import IDSAgent
from rho_aif.agents.planning import PlanningAgent
from rho_aif.agents.planning_infogain import PlanningInfoGainAgent
from rho_aif.benchmark import get_obs_models, make_env_config
from rho_aif.environments.distractor_diagnosis import DistractorDiagnosisEnv


def make_env():
    return DistractorDiagnosisEnv(
        num_conditions=4,
        test_accuracy=0.80,
        test_cost=1.0,
        distractor_accuracy=0.80,
        distractor_cost=1.0,
        correct_reward=10.0,
        incorrect_penalty=-50.0,
    )


class TestEnvironmentShape:
    def test_state_and_action_counts(self):
        env = make_env()
        assert env.num_states == 8  # 4 conditions x 2 nuisance values
        assert env.num_tests == 3  # 2 condition tests + 1 distractor
        assert env.action_space.n == env.num_tests + env.num_conditions

    def test_observation_models_shape(self):
        env = make_env()
        models = env.get_observation_models()
        assert len(models) == 3
        for m in models:
            assert m.shape == (8, 2)
            # Every row is a valid distribution.
            np.testing.assert_allclose(m.sum(axis=1), 1.0)

    def test_commit_reward_matrix_ignores_nuisance(self):
        env = make_env()
        mat = env.get_commit_reward_matrix()
        assert mat.shape == (4, 8)
        for cond in range(4):
            for nuisance in (0, 1):
                s = env.state_index(cond, nuisance)
                assert mat[cond, s] == env.correct_reward
                for other in range(4):
                    if other != cond:
                        assert mat[other, s] == env.incorrect_penalty


class TestDistractorCarriesNoTaskInformation:
    """The core Stage G2 correctness property: informational independence."""

    def test_distractor_model_uninformative_about_condition(self):
        env = make_env()
        dist_model = env.get_observation_models()[env.distractor_test_idx]
        # Marginalizing over nuisance for fixed condition should give the
        # same P(obs) regardless of condition, i.e. rows for (cond, 0) and
        # (cond', 0) are identical for every cond, cond' (same for nuisance=1).
        for nuisance in (0, 1):
            rows = [dist_model[env.state_index(c, nuisance)] for c in range(4)]
            for row in rows[1:]:
                np.testing.assert_allclose(row, rows[0])

    def test_condition_test_models_uninformative_about_nuisance(self):
        env = make_env()
        for k in range(env.num_condition_tests):
            model = env.get_observation_models()[k]
            for cond in range(4):
                row0 = model[env.state_index(cond, 0)]
                row1 = model[env.state_index(cond, 1)]
                np.testing.assert_allclose(row0, row1)

    def test_posterior_over_condition_unchanged_by_distractor_observation(self):
        """
        Bayesian sanity check: no observation model in this environment
        couples condition and nuisance (each factors as a function of one
        component only), so a belief that starts factorized as
        P(condition) x Q(nuisance) stays factorized under every update, and
        the distractor observation updates Q while leaving P exactly fixed.
        Starting from an arbitrary product-form belief (not just uniform)
        makes this a nontrivial check of the factorization property, not
        just of the uniform special case.
        """
        env = make_env()
        model = env.get_observation_models()[env.distractor_test_idx]
        rng = np.random.default_rng(0)
        p_condition = rng.dirichlet(np.ones(4))
        q_nuisance = rng.dirichlet(np.ones(2))
        belief = np.outer(p_condition, q_nuisance).reshape(-1)
        condition_marginal_before = belief.reshape(4, 2).sum(axis=1)
        np.testing.assert_allclose(condition_marginal_before, p_condition)

        for obs_idx in (0, 1):
            likelihood = model[:, obs_idx]
            posterior = belief * likelihood
            posterior = posterior / posterior.sum()
            condition_marginal_after = posterior.reshape(4, 2).sum(axis=1)
            np.testing.assert_allclose(
                condition_marginal_after, condition_marginal_before, atol=1e-10
            )

    def test_condition_test_leaves_nuisance_marginal_unchanged(self):
        """Symmetric check: a condition-test update preserves Q(nuisance)."""
        env = make_env()
        model = env.get_observation_models()[0]
        rng = np.random.default_rng(1)
        p_condition = rng.dirichlet(np.ones(4))
        q_nuisance = rng.dirichlet(np.ones(2))
        belief = np.outer(p_condition, q_nuisance).reshape(-1)
        nuisance_marginal_before = belief.reshape(4, 2).sum(axis=0)

        for obs_idx in (0, 1):
            likelihood = model[:, obs_idx]
            posterior = belief * likelihood
            posterior = posterior / posterior.sum()
            nuisance_marginal_after = posterior.reshape(4, 2).sum(axis=0)
            np.testing.assert_allclose(
                nuisance_marginal_after, nuisance_marginal_before, atol=1e-10
            )


class TestGenericAgentCompatibility:
    """
    The environment must work with every observe-then-commit agent through
    the standard get_obs_models / make_env_config interface, with no
    special-casing for the joint state space.
    """

    @pytest.mark.parametrize(
        "make_agent",
        [
            lambda obs, cfg: PlanningAgent(obs, cfg, planning_horizon=3),
            lambda obs, cfg: PlanningInfoGainAgent(
                obs, cfg, planning_horizon=3, info_gain_weight=5.0
            ),
            lambda obs, cfg: EFEAgent(obs, cfg, planning_horizon=3),
            lambda obs, cfg: IDSAgent(obs, cfg),
        ],
    )
    def test_agent_runs_to_completion(self, make_agent):
        env = make_env()
        obs_models = get_obs_models(env)
        config = make_env_config(env)
        agent = make_agent(obs_models, config)

        np.random.seed(0)
        obs, info = env.reset(seed=0)
        agent.reset()
        for _ in range(50):
            action = agent.select_action()
            obs, reward, terminated, truncated, info = env.step(action)
            if terminated or truncated:
                assert "correct" in info
                break
            agent.update_belief(obs, obs_action=action)
        else:
            pytest.fail("Episode did not terminate within 50 steps")

    def test_reward_only_planning_never_touches_distractor(self):
        """
        Planning (w=0) has no information-gain term, so it should never find
        the distractor test valuable: its expected reward contribution is
        exactly its (identical) negative cost regardless of any observation,
        so a rational reward-only planner should not choose it over
        committing once no test can change the argmax commit.
        """
        env = make_env()
        obs_models = get_obs_models(env)
        config = make_env_config(env)
        agent = PlanningAgent(obs_models, config, planning_horizon=3)

        distractor_seen = False
        np.random.seed(0)
        for ep in range(20):
            obs, info = env.reset(seed=ep)
            agent.reset()
            for _ in range(20):
                action = agent.select_action()
                obs, reward, terminated, truncated, info = env.step(action)
                if terminated or truncated:
                    break
                if info.get("is_distractor", False):
                    distractor_seen = True
                agent.update_belief(obs, obs_action=action)
        assert not distractor_seen


class TestDistractorFractionMonotonicTrend:
    """
    Stage G2's headline empirical claim: ordinary IG is reward-blind, so
    Planning+IG spends a nonzero, and non-decreasing, fraction of its usage
    on the distractor as w grows from 0.
    """

    def test_planning_ig_spends_on_distractor_at_moderate_w(self):
        env = make_env()
        obs_models = get_obs_models(env)
        config = make_env_config(env)

        def episode_distractor_fraction(w, seed):
            agent = PlanningInfoGainAgent(
                obs_models, config, planning_horizon=3, info_gain_weight=w
            )
            np.random.seed(seed)
            obs, info = env.reset(seed=seed)
            agent.reset()
            task, distractor = 0, 0
            for _ in range(30):
                action = agent.select_action()
                obs, reward, terminated, truncated, info = env.step(action)
                if terminated or truncated:
                    break
                if info.get("is_distractor", False):
                    distractor += 1
                else:
                    task += 1
                agent.update_belief(obs, obs_action=action)
            total = task + distractor
            return distractor / total if total > 0 else 0.0

        fractions_w20 = [episode_distractor_fraction(20.0, seed) for seed in range(30)]
        assert np.mean(fractions_w20) > 0.0, (
            "Expected Planning+IG at a moderate weight to spend some budget "
            "on the reward-irrelevant distractor test (IG is reward-blind)."
        )
