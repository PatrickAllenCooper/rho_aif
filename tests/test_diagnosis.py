"""Tests for the Sequential Diagnosis environment."""

import numpy as np
import pytest
from rho_aif.environments.diagnosis import DiagnosisEnv
from rho_aif.agents.myopic import MyopicAgent
from rho_aif.agents.efe import EFEAgent
from run_experiment import make_agent, run_episode, run_experiment, summarize_results


class TestDiagnosisInterface:
    def test_action_space(self):
        env = DiagnosisEnv(num_conditions=4)
        assert env.action_space.n == 2 + 4  # 2 tests + 4 diagnoses

    def test_reset(self):
        env = DiagnosisEnv(num_conditions=4)
        obs, info = env.reset(seed=42)
        assert obs == 2  # null obs
        assert 0 <= info["true_condition"] < 4

    def test_run_test(self):
        env = DiagnosisEnv(num_conditions=4)
        env.reset(seed=42)
        obs, reward, term, trunc, info = env.step(0)  # run test 0
        assert obs in (0, 1)
        assert reward == pytest.approx(-1.0)
        assert term is False

    def test_diagnose_correct(self):
        env = DiagnosisEnv(num_conditions=4)
        env.reset(seed=42)
        true_cond = env._true_condition
        action = env.num_tests + true_cond
        _, reward, term, _, info = env.step(action)
        assert reward == pytest.approx(10.0)
        assert term is True
        assert info["correct"] == True

    def test_diagnose_incorrect(self):
        env = DiagnosisEnv(num_conditions=4)
        env.reset(seed=42)
        wrong_cond = (env._true_condition + 1) % 4
        action = env.num_tests + wrong_cond
        _, reward, term, _, info = env.step(action)
        assert reward == pytest.approx(-50.0)
        assert term is True
        assert info["correct"] == False


class TestDiagnosisObservationModels:
    def test_model_count_matches_tests(self):
        env = DiagnosisEnv(num_conditions=8)
        models = env.get_observation_models()
        assert len(models) == 3  # ceil(log2(8))

    def test_model_rows_sum_to_one(self):
        env = DiagnosisEnv(num_conditions=4)
        for model in env.get_observation_models():
            for row in model:
                np.testing.assert_almost_equal(row.sum(), 1.0)

    def test_binary_partitioning(self):
        env = DiagnosisEnv(num_conditions=4, test_accuracy=1.0)
        models = env.get_observation_models()
        m0 = models[0]  # bit 0: conditions 0,2 vs 1,3
        assert m0[0, 0] == pytest.approx(1.0)  # cond 0, bit 0 = 0 -> group A
        assert m0[1, 1] == pytest.approx(1.0)  # cond 1, bit 0 = 1 -> group B

    @pytest.mark.parametrize("n", [2, 4, 8, 16])
    def test_scaling_model_shapes(self, n):
        env = DiagnosisEnv(num_conditions=n)
        for model in env.get_observation_models():
            assert model.shape == (n, 2)


class TestDiagnosisAgents:
    def test_efe_episode_completes(self):
        env = DiagnosisEnv(num_conditions=4)
        agent = make_agent(EFEAgent, env, planning_horizon=3)
        result = run_episode(agent, env)
        assert result.success in (True, False)
        assert result.num_observations >= 0

    def test_efe_observes_at_uniform(self):
        env = DiagnosisEnv(num_conditions=4)
        agent = make_agent(EFEAgent, env, planning_horizon=3)
        action = agent.select_action()
        assert action < env.num_tests  # should run a test, not diagnose

    def test_myopic_episode_completes(self):
        env = DiagnosisEnv(num_conditions=4)
        agent = make_agent(MyopicAgent, env)
        result = run_episode(agent, env)
        assert result.success in (True, False)
