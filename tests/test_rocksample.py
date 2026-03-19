"""Tests for the RockSample environment."""

import numpy as np
import pytest
from environments.rocksample import RockSampleEnv


class TestRockSampleInterface:
    def test_action_space(self):
        env = RockSampleEnv(grid_size=5, num_rocks=3)
        assert env.action_space.n == 4 + 3 + 2  # move + check + sample + exit

    def test_observation_space(self):
        env = RockSampleEnv(grid_size=5, num_rocks=3)
        assert env.observation_space.n == 3

    def test_reset(self):
        env = RockSampleEnv(grid_size=5, num_rocks=3)
        obs, info = env.reset(seed=42)
        assert obs == 2  # null
        assert "agent_pos" in info
        assert "rock_positions" in info
        assert len(info["rock_positions"]) == 3

    def test_deterministic_reset(self):
        env = RockSampleEnv(grid_size=5, num_rocks=3)
        _, info1 = env.reset(seed=42)
        _, info2 = env.reset(seed=42)
        assert info1["rock_positions"] == info2["rock_positions"]
        np.testing.assert_array_equal(
            info1["rock_qualities"], info2["rock_qualities"]
        )

    def test_move_changes_position(self):
        env = RockSampleEnv(grid_size=5, num_rocks=2,
                            rock_positions=[(0, 0), (4, 4)])
        env.reset(seed=42)
        start = env._agent_pos
        env.step(env.MOVE_E)  # move east
        assert env._agent_pos[1] == min(start[1] + 1, 4)

    def test_boundary_clamping(self):
        env = RockSampleEnv(grid_size=5, num_rocks=2,
                            rock_positions=[(0, 0), (4, 4)])
        env.reset(seed=42)
        for _ in range(10):
            env.step(env.MOVE_N)  # keep moving north
        assert env._agent_pos[0] == 0

    def test_check_returns_binary(self):
        env = RockSampleEnv(grid_size=5, num_rocks=3)
        env.reset(seed=42)
        obs, _, _, _, _ = env.step(4)  # check rock 0
        assert obs in (0, 1)

    def test_sample_good_rock(self):
        env = RockSampleEnv(grid_size=5, num_rocks=2,
                            rock_positions=[(2, 0), (4, 4)])
        env.reset(seed=42)
        env._rock_qualities = np.array([1, 0])
        env._agent_pos = (2, 0)
        _, reward, _, _, _ = env.step(env.sample_action)
        assert reward == pytest.approx(10.0)

    def test_sample_bad_rock(self):
        env = RockSampleEnv(grid_size=5, num_rocks=2,
                            rock_positions=[(2, 0), (4, 4)])
        env.reset(seed=42)
        env._rock_qualities = np.array([0, 1])
        env._agent_pos = (2, 0)
        _, reward, _, _, _ = env.step(env.sample_action)
        assert reward == pytest.approx(-10.0)

    def test_sample_empty_cell(self):
        env = RockSampleEnv(grid_size=5, num_rocks=2,
                            rock_positions=[(0, 0), (4, 4)])
        env.reset(seed=42)
        env._agent_pos = (2, 2)
        _, reward, _, _, _ = env.step(env.sample_action)
        assert reward == pytest.approx(0.0)

    def test_exit_terminates(self):
        env = RockSampleEnv(grid_size=5, num_rocks=2)
        env.reset(seed=42)
        _, reward, terminated, _, _ = env.step(env.exit_action)
        assert terminated is True
        assert reward == pytest.approx(10.0)

    def test_max_steps_truncation(self):
        env = RockSampleEnv(grid_size=5, num_rocks=2, max_steps=3)
        env.reset(seed=42)
        for _ in range(2):
            _, _, _, truncated, _ = env.step(env.MOVE_E)
            assert truncated is False
        _, _, _, truncated, _ = env.step(env.MOVE_E)
        assert truncated is True

    def test_rock_cannot_be_sampled_twice(self):
        env = RockSampleEnv(grid_size=5, num_rocks=2,
                            rock_positions=[(2, 0), (4, 4)])
        env.reset(seed=42)
        env._rock_qualities = np.array([1, 0])
        env._agent_pos = (2, 0)
        _, r1, _, _, _ = env.step(env.sample_action)
        assert r1 == pytest.approx(10.0)
        _, r2, _, _, _ = env.step(env.sample_action)
        assert r2 == pytest.approx(0.0)


class TestRockSampleCheckAccuracy:
    def test_close_check_is_accurate(self):
        env = RockSampleEnv(grid_size=5, num_rocks=1,
                            rock_positions=[(2, 2)],
                            check_base_accuracy=0.95)
        env.reset(seed=42)
        acc = env.get_check_accuracy_at((2, 2), 0)
        assert acc == pytest.approx(0.95)

    def test_far_check_is_less_accurate(self):
        env = RockSampleEnv(grid_size=10, num_rocks=1,
                            rock_positions=[(5, 5)],
                            half_efficiency_distance=4.0)
        env.reset(seed=42)
        acc_close = env.get_check_accuracy_at((5, 5), 0)
        acc_far = env.get_check_accuracy_at((0, 0), 0)
        assert acc_close > acc_far
        assert acc_far >= 0.5

    def test_accuracy_bounded(self):
        env = RockSampleEnv(grid_size=20, num_rocks=1,
                            rock_positions=[(0, 0)])
        env.reset(seed=42)
        for r in range(20):
            for c in range(20):
                acc = env.get_check_accuracy_at((r, c), 0)
                assert 0.5 <= acc <= env.check_base_accuracy
