"""Tests for the MCTS-EFE agent."""

import numpy as np
import pytest

from agents.mcts_efe import MCTSEFEAgent
from run_experiment import make_agent, run_episode, run_experiment, summarize_results
from environments.info_seeking import InfoSeekingEnv
from environments.tiger import TigerEnv
from environments.diagnosis import DiagnosisEnv
from environments.bandit import BanditEnv
from environments.tileworld import TileworldEnv


@pytest.fixture
def info_obs_model():
    return np.array([[0.75, 0.25], [0.25, 0.75]])


@pytest.fixture
def info_config():
    return {
        "observation_costs": [0.1],
        "commit_reward_matrix": np.array([[1.0, -1.0], [-1.0, 1.0]]),
    }


class TestMCTSEFEAgent:
    def test_selects_valid_action(self, info_obs_model, info_config):
        np.random.seed(42)
        agent = MCTSEFEAgent(
            info_obs_model, info_config,
            num_simulations=50, planning_horizon=3,
        )
        action = agent.select_action()
        assert action in (0, 1, 2)

    def test_observes_at_uniform(self, info_obs_model, info_config):
        np.random.seed(42)
        agent = MCTSEFEAgent(
            info_obs_model, info_config,
            num_simulations=200, planning_horizon=4,
        )
        action = agent.select_action()
        assert action == 0

    def test_commits_when_confident(self, info_obs_model, info_config):
        np.random.seed(42)
        agent = MCTSEFEAgent(
            info_obs_model, info_config,
            num_simulations=200, planning_horizon=4,
        )
        agent.belief.reset(initial_belief=np.array([0.99, 0.01]))
        action = agent.select_action()
        assert action == 1


class TestMCTSOnEnvironments:
    def test_tiger_episode(self):
        np.random.seed(42)
        env = TigerEnv()
        agent = make_agent(MCTSEFEAgent, env,
                           num_simulations=100, planning_horizon=5)
        result = run_episode(agent, env)
        assert result.success in (True, False)
        assert result.num_observations >= 0

    def test_diagnosis_episode(self):
        np.random.seed(42)
        env = DiagnosisEnv(num_conditions=4)
        agent = make_agent(MCTSEFEAgent, env,
                           num_simulations=100, planning_horizon=4)
        result = run_episode(agent, env)
        assert result.success in (True, False)

    def test_bandit_episode(self):
        np.random.seed(42)
        env = BanditEnv(num_arms=4)
        agent = make_agent(MCTSEFEAgent, env,
                           num_simulations=100, planning_horizon=4)
        result = run_episode(agent, env)
        assert result.success in (True, False)

    def test_tileworld_episode(self):
        np.random.seed(42)
        env = TileworldEnv(grid_size=4)
        agent = make_agent(MCTSEFEAgent, env,
                           num_simulations=50, planning_horizon=3)
        result = run_episode(agent, env)
        assert result.success in (True, False)

    def test_higher_horizon_than_exact(self):
        """MCTS should handle H=5 on Tiger without blowup."""
        np.random.seed(42)
        env = TigerEnv(listen_accuracy=0.85, listen_cost=1.0,
                       correct_reward=10.0, incorrect_penalty=-100.0)
        agent = make_agent(MCTSEFEAgent, env,
                           num_simulations=200, planning_horizon=8)
        result = run_episode(agent, env)
        assert result.success in (True, False)
        assert result.num_observations >= 1

    def test_reasonable_performance_on_tiger(self):
        np.random.seed(42)
        env = TigerEnv(listen_accuracy=0.85, listen_cost=1.0,
                       correct_reward=10.0, incorrect_penalty=-100.0)
        results = run_experiment(
            MCTSEFEAgent, env, num_episodes=100,
            num_simulations=200, planning_horizon=6,
        )
        summary = summarize_results(results)
        assert summary["success_rate"] > 0.80
