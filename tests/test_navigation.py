"""Tests for the Partially Observable Navigation environment."""

import numpy as np
import pytest
from environments.navigation import NavigationEnv
from agents.navigation_vfe import NavigationVFEAgent


class TestNavigationInterface:
    def test_action_space(self):
        env = NavigationEnv(grid_size=3)
        assert env.action_space.n == 4  # up, down, left, right

    def test_reset(self):
        env = NavigationEnv(grid_size=3)
        obs, info = env.reset(seed=42)
        assert obs == 3  # null
        assert "goal_pos" in info
        assert "agent_pos" in info
        assert info["agent_pos"] == (0, 0)

    def test_move_changes_position(self):
        env = NavigationEnv(grid_size=3)
        env.reset(seed=42)
        env.step(1)  # move down
        assert env._agent_pos == (1, 0)

    def test_boundary_clamp(self):
        env = NavigationEnv(grid_size=3)
        env.reset(seed=42)
        env.step(0)  # move up from (0,0)
        assert env._agent_pos == (0, 0)  # clamped

    def test_finding_goal_terminates(self):
        env = NavigationEnv(grid_size=3)
        env.reset(seed=42)
        env._goal_pos = (1, 0)
        obs, reward, term, trunc, info = env.step(1)  # move down to (1,0)
        assert term is True
        assert obs == 2  # found
        assert reward == pytest.approx(20.0)
        assert info["correct"] == True

    def test_max_steps_truncation(self):
        env = NavigationEnv(grid_size=3, max_steps=2)
        env.reset(seed=42)
        env._goal_pos = (2, 2)  # far corner
        env.step(1)  # step 1
        _, _, _, truncated, info = env.step(1)  # step 2
        assert truncated is True

    def test_proximity_signal(self):
        env = NavigationEnv(grid_size=4)
        env.reset(seed=42)
        env._goal_pos = (1, 0)
        observations = []
        for _ in range(100):
            obs = 1 if env.np_random.random() < env._warm_prob((0, 0), (1, 0)) else 0
            observations.append(obs)
        warm_rate = np.mean(observations)
        assert warm_rate > 0.5  # should be warmer than random when close


class TestNavigationObservationModel:
    def test_model_at_goal_is_certain(self):
        env = NavigationEnv(grid_size=3)
        env.reset(seed=42)
        goal_idx = env._pos_to_idx((1, 1))
        model = env.get_observation_model_at((1, 1))
        assert model[goal_idx, 1] == pytest.approx(1.0)  # warm with certainty

    def test_model_shape(self):
        env = NavigationEnv(grid_size=3)
        env.reset(seed=42)
        model = env.get_observation_model_at((0, 0))
        assert model.shape == (9, 2)

    def test_model_rows_sum_to_one(self):
        env = NavigationEnv(grid_size=3)
        env.reset(seed=42)
        model = env.get_observation_model_at((0, 0))
        for row in model:
            np.testing.assert_almost_equal(row.sum(), 1.0)


class TestNavigationVFEAgent:
    def test_selects_valid_action(self):
        env = NavigationEnv(grid_size=3, max_steps=10)
        env.reset(seed=42)
        env._goal_pos = (2, 2)
        agent = NavigationVFEAgent(env, planning_horizon=2)
        action = agent.select_action()
        assert action in (0, 1, 2, 3)

    def test_full_episode(self):
        env = NavigationEnv(grid_size=3, max_steps=15)
        env.reset(seed=42)
        agent = NavigationVFEAgent(env, planning_horizon=2)
        total_reward = 0.0
        for _ in range(15):
            action = agent.select_action()
            obs, reward, term, trunc, info = env.step(action)
            total_reward += reward
            if term or trunc:
                break
            agent.update_belief(obs, obs_action=action)
        assert True  # just verify it doesn't crash
