"""Tests for DualWeightAgent online dual control of w."""

from __future__ import annotations

import numpy as np
import pytest

from rho_aif.agents.dual_descent import DualWeightAgent
from rho_aif.benchmark import make_env_config, get_obs_models, run_otc_episode
from rho_aif.budget import episode_sensing_usage, usage_value
from rho_aif.environments.tiger import TigerEnv


def _make_tiger_agent(budget: float = 2.0, lr: float = 0.2, w0: float = 1.0):
    env = TigerEnv()
    agent = DualWeightAgent(
        get_obs_models(env),
        make_env_config(env),
        budget=budget,
        lr=lr,
        planning_horizon=6,
        initial_weight=w0,
    )
    return agent, env


class TestDualWeightAgent:
    def test_update_decreases_when_over_budget(self):
        agent, _ = _make_tiger_agent(budget=1.0, lr=0.5, w0=2.0)
        new_w = agent.end_episode(usage=3.0)
        assert new_w == pytest.approx(1.0)
        assert agent.weight_history[-1] == pytest.approx(1.0)
        assert agent.usage_history[-1] == 3.0

    def test_update_increases_when_under_budget(self):
        agent, _ = _make_tiger_agent(budget=4.0, lr=0.5, w0=1.0)
        new_w = agent.end_episode(usage=0.0)
        assert new_w == pytest.approx(3.0)

    def test_projection_at_zero(self):
        agent, _ = _make_tiger_agent(budget=0.0, lr=10.0, w0=0.5)
        new_w = agent.end_episode(usage=5.0)
        assert new_w == 0.0

    def test_smoke_episode_loop(self):
        agent, env = _make_tiger_agent(budget=2.0, lr=0.1, w0=1.0)
        np.random.seed(42)
        for _ in range(5):
            result = run_otc_episode(agent, env)
            u = usage_value(episode_sensing_usage(result), "count")
            agent.end_episode(u)
        assert len(agent.usage_history) == 5
        assert len(agent.weight_history) == 6  # initial + 5 updates
        assert all(w >= 0.0 for w in agent.weight_history)
