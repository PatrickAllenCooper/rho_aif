"""Shared fixtures for the test suite."""

import sys
import os
import pytest
import numpy as np

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from environments.info_seeking import InfoSeekingEnv
from environments.tiger import TigerEnv
from belief import BeliefState


@pytest.fixture
def info_env():
    return InfoSeekingEnv(
        observation_accuracy=0.75,
        observation_cost=0.1,
        correct_reward=1.0,
        incorrect_penalty=-1.0,
    )


@pytest.fixture
def tiger_env():
    return TigerEnv(
        listen_accuracy=0.85,
        listen_cost=1.0,
        correct_reward=10.0,
        incorrect_penalty=-100.0,
    )


@pytest.fixture
def info_config():
    return {
        "observation_costs": [0.1],
        "commit_reward_matrix": np.array([
            [1.0, -1.0],
            [-1.0, 1.0],
        ]),
    }


@pytest.fixture
def tiger_config():
    return {
        "observation_costs": [1.0],
        "commit_reward_matrix": np.array([
            [-100.0, 10.0],
            [10.0, -100.0],
        ]),
    }


@pytest.fixture
def info_obs_model():
    return [np.array([[0.75, 0.25], [0.25, 0.75]])]


@pytest.fixture
def tiger_obs_model():
    return [np.array([[0.85, 0.15], [0.15, 0.85]])]


@pytest.fixture
def uniform_belief():
    return BeliefState(num_states=2)


@pytest.fixture
def confident_belief():
    """Belief strongly favoring state 0."""
    return BeliefState(num_states=2, initial_belief=np.array([0.9, 0.1]))
