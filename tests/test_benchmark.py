"""Tests for the public benchmark registry and runners."""

import numpy as np
import pytest

from rho_aif.benchmark import (
    BENCHMARKS,
    INSPECTION_CONFIGS,
    list_benchmarks,
    get_benchmark,
    make_otc_agent,
    make_inspection_agent,
    run_otc_episode,
    run_inspection_episode,
    run_benchmark,
    summarize_otc,
)


REQUIRED_ENVS = {
    "Tiger",
    "Diagnosis",
    "Bandit",
    "Tileworld-6x6",
    "Inspection-N8",
    "Inspection-N16",
}


class TestRegistry:
    def test_lists_required_envs(self):
        names = set(list_benchmarks())
        assert REQUIRED_ENVS.issubset(names)

    def test_get_benchmark(self):
        cfg = get_benchmark("Tiger")
        assert cfg.family == "observe_then_commit"
        assert cfg.planning_horizon == 6
        assert cfg.num_states == 2

    def test_unknown_raises(self):
        with pytest.raises(KeyError):
            get_benchmark("NotARealEnv")

    def test_inspection_configs_match(self):
        assert "Inspection-N8" in INSPECTION_CONFIGS
        assert INSPECTION_CONFIGS["Inspection-N8"]["num_components"] == 8
        assert INSPECTION_CONFIGS["Inspection-N16"]["num_components"] == 16

    def test_env_factories_construct(self):
        for name in REQUIRED_ENVS:
            env = BENCHMARKS[name].env_factory()
            assert env is not None
            obs, info = env.reset(seed=0)
            assert info is not None


class TestOTCEpisode:
    def test_efe_tiger_returns_scores(self):
        cfg = get_benchmark("Tiger")
        env = cfg.env_factory()
        agent = make_otc_agent("efe", env, cfg.planning_horizon)
        result = run_otc_episode(agent, env)
        assert "log_score" in result
        assert "brier_score" in result
        assert result["terminal_belief"] is not None
        assert result["true_state"] in (0, 1)
        assert np.isfinite(result["log_score"])
        assert 0.0 <= result["brier_score"] <= 2.0

    def test_summarize_otc(self):
        cfg = get_benchmark("Tiger")
        env = cfg.env_factory()
        agent = make_otc_agent("myopic", env, cfg.planning_horizon)
        results = [run_otc_episode(agent, env) for _ in range(5)]
        summary = summarize_otc(results, "myopic")
        assert summary["n_episodes"] == 5
        assert "mean_log_score" in summary
        assert "mean_brier" in summary


class TestInspectionEpisode:
    def test_efe_inspection_returns_scores(self):
        cfg = get_benchmark("Inspection-N8")
        env = cfg.env_factory()
        agent = make_inspection_agent("efe", env, cfg.tree_depth)
        result = run_inspection_episode(agent, env, seed=42)
        assert np.isfinite(result["log_score"])
        assert np.isfinite(result["brier_score"])
        assert result["fault_beliefs"].shape == (8,)


class TestRunBenchmarkSmoke:
    def test_tiger_efe_one_seed(self):
        summary = run_benchmark(
            "Tiger",
            agent_name="efe",
            episodes=5,
            seeds=[42],
            progress=False,
        )
        assert summary["environment"] == "Tiger"
        assert summary["n_episodes"] == 5
        assert "mean_log_score" in summary
        assert "mean_brier" in summary

    def test_inspection_greedy_one_seed(self):
        summary = run_benchmark(
            "Inspection-N8",
            agent_name="greedy",
            episodes=2,
            seeds=[42],
            progress=False,
        )
        assert summary["n_episodes"] == 2
        assert "accuracy" in summary
        assert "mean_log_score" in summary
