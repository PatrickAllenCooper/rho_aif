"""Tests for the observe-then-commit IDS agent."""

import numpy as np

from rho_aif.agents.ids import IDSAgent
from rho_aif.environments.diagnosis import DiagnosisEnv
from rho_aif.environments.tiger import TigerEnv
from run_experiment import make_agent, run_episode


def test_ids_selects_valid_action_on_tiger():
    env = TigerEnv()
    agent = make_agent(IDSAgent, env)
    agent.reset()
    action = agent.select_action()
    assert 0 <= action < env.action_space.n


def test_ids_can_observe_under_uncertainty():
    env = TigerEnv()
    agent = make_agent(IDSAgent, env)
    agent.reset()
    # Uniform prior: should typically listen
    action = agent.select_action()
    assert action == 0  # listen / observe


def test_ids_commits_when_confident():
    env = TigerEnv()
    agent = make_agent(IDSAgent, env)
    agent.reset()
    agent.belief.belief = np.array([0.999, 0.001])
    action = agent.select_action()
    assert action != 0  # should commit, not listen


def test_ids_completes_episode():
    env = DiagnosisEnv(num_conditions=4)
    agent = make_agent(IDSAgent, env)
    result = run_episode(agent, env)
    assert isinstance(result.success, (bool, np.bool_))
    assert result.num_observations >= 0


def test_optimal_commit_distribution_sums_to_one():
    env = TigerEnv()
    agent = make_agent(IDSAgent, env)
    p = agent._optimal_commit_distribution(np.array([0.5, 0.5]))
    assert np.isclose(p.sum(), 1.0)
    assert p.shape == (2,)
