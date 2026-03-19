"""Tests for model misspecification robustness experiment."""

import numpy as np
import pytest
from environments.tiger import TigerEnv
from environments.diagnosis import DiagnosisEnv
from agents.efe import EFEAgent
from agents.planning import PlanningAgent
from run_model_misspec import make_misspec_agent
from run_experiment import run_episode


class TestMisspecAgentConstruction:
    """Verify that misspecified agents are built correctly."""

    def test_correct_specification_matches_original(self):
        env = TigerEnv(listen_accuracy=0.85)
        true_model = env.get_observation_models()[0]

        agent = make_misspec_agent(EFEAgent, env, 0.85, 0.85, planning_horizon=2)
        np.testing.assert_allclose(agent.obs_models[0], true_model, atol=1e-10)

    def test_misspecified_model_differs(self):
        env = TigerEnv(listen_accuracy=0.85)
        agent = make_misspec_agent(EFEAgent, env, 0.85, 0.70, planning_horizon=2)
        expected = np.array([[0.70, 0.30], [0.30, 0.70]])
        np.testing.assert_allclose(agent.obs_models[0], expected, atol=1e-10)

    def test_misspec_model_rows_sum_to_one(self):
        env = DiagnosisEnv(num_conditions=4, test_accuracy=0.80)
        agent = make_misspec_agent(EFEAgent, env, 0.80, 0.65, planning_horizon=2)
        for model in agent.obs_models:
            row_sums = model.sum(axis=1)
            np.testing.assert_allclose(row_sums, 1.0, atol=1e-10)

    def test_overestimated_accuracy(self):
        env = TigerEnv(listen_accuracy=0.85)
        agent = make_misspec_agent(EFEAgent, env, 0.85, 0.95, planning_horizon=2)
        expected = np.array([[0.95, 0.05], [0.05, 0.95]])
        np.testing.assert_allclose(agent.obs_models[0], expected, atol=1e-10)

    def test_diagnosis_multiple_models(self):
        env = DiagnosisEnv(num_conditions=4, test_accuracy=0.80)
        agent = make_misspec_agent(EFEAgent, env, 0.80, 0.90, planning_horizon=2)
        assert len(agent.obs_models) == 2
        for model in agent.obs_models:
            assert model.shape == (4, 2)
            for s in range(4):
                assert abs(np.max(model[s]) - 0.90) < 1e-10


class TestMisspecAgentBehavior:
    """Verify that misspecified agents still produce valid behavior."""

    def test_misspec_efe_runs_episode(self):
        env = TigerEnv(listen_accuracy=0.85)
        agent = make_misspec_agent(EFEAgent, env, 0.85, 0.70, planning_horizon=2)
        result = run_episode(agent, env)
        assert result.total_reward != 0

    def test_misspec_planning_runs_episode(self):
        env = TigerEnv(listen_accuracy=0.85)
        agent = make_misspec_agent(PlanningAgent, env, 0.85, 0.70, planning_horizon=2)
        result = run_episode(agent, env)
        assert result.total_reward != 0

    def test_overconfident_agent_observes_less(self):
        """Agent overestimating accuracy should observe fewer times on average."""
        np.random.seed(42)
        env = TigerEnv(listen_accuracy=0.85)

        correct_agent = make_misspec_agent(EFEAgent, env, 0.85, 0.85, planning_horizon=3)
        overconf_agent = make_misspec_agent(EFEAgent, env, 0.85, 0.99, planning_horizon=3)

        n = 100
        correct_obs = []
        overconf_obs = []
        for _ in range(n):
            r = run_episode(correct_agent, env)
            correct_obs.append(r.num_observations)
        for _ in range(n):
            r = run_episode(overconf_agent, env)
            overconf_obs.append(r.num_observations)

        assert np.mean(overconf_obs) < np.mean(correct_obs)
