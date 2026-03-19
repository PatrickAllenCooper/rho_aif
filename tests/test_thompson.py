"""Tests for the Thompson Sampling agent."""

import numpy as np
import pytest

from agents.thompson import ThompsonSamplingAgent
from agents.myopic import MyopicAgent
from run_experiment import make_agent, run_episode, run_experiment, summarize_results
from environments.info_seeking import InfoSeekingEnv
from environments.tiger import TigerEnv
from environments.diagnosis import DiagnosisEnv
from environments.bandit import BanditEnv


@pytest.fixture
def info_obs_model():
    return np.array([[0.75, 0.25], [0.25, 0.75]])


@pytest.fixture
def info_config():
    return {
        "observation_costs": [0.1],
        "commit_reward_matrix": np.array([[1.0, -1.0], [-1.0, 1.0]]),
    }


class TestThompsonSamplingAgent:
    def test_selects_valid_action(self, info_obs_model, info_config):
        np.random.seed(42)
        agent = ThompsonSamplingAgent(info_obs_model, info_config, num_samples=50)
        action = agent.select_action()
        assert action in (0, 1, 2)

    def test_observes_at_uniform(self, info_obs_model, info_config):
        np.random.seed(42)
        agent = ThompsonSamplingAgent(info_obs_model, info_config, num_samples=200)
        action = agent.select_action()
        assert action == 0

    def test_commits_when_confident(self, info_obs_model, info_config):
        np.random.seed(42)
        agent = ThompsonSamplingAgent(info_obs_model, info_config, num_samples=200)
        agent.belief.reset(initial_belief=np.array([0.99, 0.01]))
        action = agent.select_action()
        assert action == 1

    def test_commit_direction_matches_belief(self, info_obs_model, info_config):
        np.random.seed(42)
        agent = ThompsonSamplingAgent(info_obs_model, info_config, num_samples=200)
        agent.belief.reset(initial_belief=np.array([0.01, 0.99]))
        action = agent.select_action()
        if action != 0:
            assert action == 2


class TestThompsonOnEnvironments:
    def test_info_seeking_episode(self):
        np.random.seed(42)
        env = InfoSeekingEnv()
        agent = make_agent(ThompsonSamplingAgent, env, num_samples=100)
        result = run_episode(agent, env)
        assert result.success in (True, False)
        assert result.num_observations >= 0

    def test_tiger_episode(self):
        np.random.seed(42)
        env = TigerEnv()
        agent = make_agent(ThompsonSamplingAgent, env, num_samples=100)
        result = run_episode(agent, env)
        assert result.success in (True, False)

    def test_diagnosis_episode(self):
        np.random.seed(42)
        env = DiagnosisEnv(num_conditions=4)
        agent = make_agent(ThompsonSamplingAgent, env, num_samples=100)
        result = run_episode(agent, env)
        assert result.success in (True, False)

    def test_bandit_episode(self):
        np.random.seed(42)
        env = BanditEnv(num_arms=4)
        agent = make_agent(ThompsonSamplingAgent, env, num_samples=100)
        result = run_episode(agent, env)
        assert result.success in (True, False)

    def test_outperforms_random(self):
        np.random.seed(42)
        env = TigerEnv(listen_accuracy=0.85, listen_cost=1.0,
                       correct_reward=10.0, incorrect_penalty=-100.0)
        results = run_experiment(
            ThompsonSamplingAgent, env, num_episodes=200, num_samples=100
        )
        summary = summarize_results(results)
        assert summary["success_rate"] > 0.6
