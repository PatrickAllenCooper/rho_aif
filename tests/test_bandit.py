"""Tests for the Multi-Armed Bandit with Hidden Structure environment."""

import numpy as np
import pytest
from environments.bandit import BanditEnv
from agents.myopic import MyopicAgent
from agents.vfe import VFEAgent
from run_experiment import make_agent, run_episode


class TestBanditInterface:
    def test_action_space(self):
        env = BanditEnv(num_arms=4)
        assert env.action_space.n == 8  # 4 inspect + 4 pull

    def test_reset(self):
        env = BanditEnv(num_arms=4)
        obs, info = env.reset(seed=42)
        assert obs == 2  # null
        assert 0 <= info["best_arm"] < 4

    def test_inspect(self):
        env = BanditEnv(num_arms=4)
        env.reset(seed=42)
        obs, reward, term, trunc, info = env.step(0)  # inspect arm 0
        assert obs in (0, 1)
        assert reward == pytest.approx(-0.5)
        assert term is False

    def test_pull_best(self):
        env = BanditEnv(num_arms=4)
        env.reset(seed=42)
        best = env._best_arm
        _, reward, term, _, info = env.step(4 + best)
        assert reward == pytest.approx(10.0)
        assert term is True
        assert info["correct"] == True

    def test_pull_non_best(self):
        env = BanditEnv(num_arms=4)
        env.reset(seed=42)
        wrong = (env._best_arm + 1) % 4
        _, reward, term, _, info = env.step(4 + wrong)
        assert reward == pytest.approx(1.0)
        assert term is True
        assert info["correct"] == False


class TestBanditObservationModels:
    def test_model_count(self):
        env = BanditEnv(num_arms=4)
        assert len(env.get_observation_models()) == 4

    def test_model_shape(self):
        env = BanditEnv(num_arms=4)
        for model in env.get_observation_models():
            assert model.shape == (4, 2)

    def test_model_rows_sum_to_one(self):
        env = BanditEnv(num_arms=4)
        for model in env.get_observation_models():
            for row in model:
                np.testing.assert_almost_equal(row.sum(), 1.0)


class TestBanditAgents:
    def test_vfe_episode_completes(self):
        env = BanditEnv(num_arms=4)
        agent = make_agent(VFEAgent, env, planning_horizon=3)
        result = run_episode(agent, env)
        assert result.success in (True, False)

    def test_vfe_inspects_at_uniform(self):
        env = BanditEnv(num_arms=4)
        agent = make_agent(VFEAgent, env, planning_horizon=3)
        action = agent.select_action()
        assert action < 4  # should inspect, not pull

    def test_myopic_episode_completes(self):
        env = BanditEnv(num_arms=4)
        agent = make_agent(MyopicAgent, env)
        result = run_episode(agent, env)
        assert result.success in (True, False)
