"""Integration tests: full episodes and statistical properties."""

import numpy as np
import pytest

from environments.info_seeking import InfoSeekingEnv
from environments.tiger import TigerEnv
from agents.myopic import MyopicAgent
from agents.info_gain import InformationGainAgent
from agents.vfe import VFEAgent
from agents.planning import PlanningAgent
from run_experiment import make_agent, run_episode, run_experiment, summarize_results


class TestFullEpisodes:
    """Verify that full episodes run without errors."""

    @pytest.mark.parametrize("AgentClass", [MyopicAgent, InformationGainAgent, VFEAgent, PlanningAgent])
    def test_info_seeking_episode_completes(self, info_env, AgentClass):
        kwargs = {}
        if AgentClass == InformationGainAgent:
            kwargs["info_gain_weight"] = 1.0
        if AgentClass in (VFEAgent, PlanningAgent):
            kwargs["planning_horizon"] = 3
        agent = make_agent(AgentClass, info_env, **kwargs)
        result = run_episode(agent, info_env)
        assert result.num_observations >= 0
        assert result.success in (True, False)
        assert result.total_reward != 0.0

    @pytest.mark.parametrize("AgentClass", [MyopicAgent, InformationGainAgent, VFEAgent, PlanningAgent])
    def test_tiger_episode_completes(self, tiger_env, AgentClass):
        kwargs = {}
        if AgentClass == InformationGainAgent:
            kwargs["info_gain_weight"] = 1.0
        if AgentClass in (VFEAgent, PlanningAgent):
            kwargs["planning_horizon"] = 4
        agent = make_agent(AgentClass, tiger_env, **kwargs)
        result = run_episode(agent, tiger_env)
        assert result.num_observations >= 0
        assert result.success in (True, False)


class TestStatisticalProperties:
    """Statistical properties over batches of episodes."""

    def test_info_seeking_myopic_baseline(self, info_env):
        """Myopic agent on info-seeking should succeed around 75%."""
        results = run_experiment(MyopicAgent, info_env, num_episodes=200)
        summary = summarize_results(results)
        assert 0.60 < summary["success_rate"] < 0.90

    def test_info_gain_outperforms_myopic(self, info_env):
        """Info gain agent should have higher success rate than myopic."""
        np.random.seed(42)
        myopic = run_experiment(MyopicAgent, info_env, num_episodes=300)
        ig = run_experiment(InformationGainAgent, info_env, num_episodes=300, info_gain_weight=1.0)
        m_succ = np.mean([r.success for r in myopic])
        ig_succ = np.mean([r.success for r in ig])
        assert ig_succ > m_succ

    def test_vfe_explores_more_than_myopic(self, info_env):
        """VFE agent should make more observations than myopic."""
        np.random.seed(42)
        myopic = run_experiment(MyopicAgent, info_env, num_episodes=200)
        vfe = run_experiment(VFEAgent, info_env, num_episodes=200, planning_horizon=3)
        m_obs = np.mean([r.num_observations for r in myopic])
        v_obs = np.mean([r.num_observations for r in vfe])
        assert v_obs > m_obs

    def test_tiger_vfe_listens_before_opening(self, tiger_env):
        """VFE agent on Tiger should listen multiple times before opening."""
        results = run_experiment(VFEAgent, tiger_env, num_episodes=100, planning_horizon=4)
        mean_obs = np.mean([r.num_observations for r in results])
        assert mean_obs >= 2.0


class TestReproducibility:
    def test_deterministic_with_seeded_env(self):
        """Episodes with identically seeded environments produce same results."""
        def run_seeded(seed):
            env = InfoSeekingEnv()
            agent = make_agent(MyopicAgent, env)
            env.reset(seed=seed)
            agent.reset()
            result = run_episode(agent, env)
            return result.total_reward, result.num_observations, result.success

        r1 = run_seeded(42)
        r2 = run_seeded(42)
        assert r1 == r2


class TestSummarizeResults:
    def test_summary_keys(self, info_env):
        results = run_experiment(MyopicAgent, info_env, num_episodes=10)
        summary = summarize_results(results)
        expected_keys = [
            "agent", "mean_observations", "std_observations",
            "mean_final_entropy", "mean_confidence",
            "success_rate", "mean_reward", "std_reward",
        ]
        for key in expected_keys:
            assert key in summary

    def test_success_rate_bounded(self, info_env):
        results = run_experiment(MyopicAgent, info_env, num_episodes=50)
        summary = summarize_results(results)
        assert 0.0 <= summary["success_rate"] <= 1.0
