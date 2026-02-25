"""Tests for Gymnasium-wrapped POMDP environments."""

import numpy as np
import pytest
from gymnasium import spaces

from environments.info_seeking import InfoSeekingEnv, OBSERVE, COMMIT_A, COMMIT_B, SIGNAL_A, SIGNAL_B, NULL_OBS
from environments.tiger import TigerEnv, LISTEN, OPEN_LEFT, OPEN_RIGHT, HEAR_LEFT, HEAR_RIGHT
from environments.tiger import NULL_OBS as TIGER_NULL


class TestInfoSeekingGymInterface:
    def test_spaces(self, info_env):
        assert isinstance(info_env.action_space, spaces.Discrete)
        assert isinstance(info_env.observation_space, spaces.Discrete)
        assert info_env.action_space.n == 3
        assert info_env.observation_space.n == 3

    def test_reset_signature(self, info_env):
        obs, info = info_env.reset(seed=42)
        assert isinstance(obs, (int, np.integer))
        assert isinstance(info, dict)
        assert obs == NULL_OBS

    def test_step_observe_signature(self, info_env):
        info_env.reset(seed=42)
        obs, reward, terminated, truncated, info = info_env.step(OBSERVE)
        assert obs in (SIGNAL_A, SIGNAL_B)
        assert reward == pytest.approx(-0.1)
        assert terminated is False
        assert truncated is False

    def test_step_commit_terminates(self, info_env):
        info_env.reset(seed=42)
        obs, reward, terminated, truncated, info = info_env.step(COMMIT_A)
        assert terminated is True
        assert truncated is False
        assert obs == NULL_OBS
        assert reward in (1.0, -1.0)

    def test_correct_commit_reward(self, info_env):
        info_env.reset(seed=42)
        true_state = info_env._true_state
        correct_action = COMMIT_A if true_state == 0 else COMMIT_B
        _, reward, _, _, info = info_env.step(correct_action)
        assert reward == pytest.approx(1.0)
        assert info["correct"] == True

    def test_incorrect_commit_penalty(self, info_env):
        info_env.reset(seed=42)
        true_state = info_env._true_state
        wrong_action = COMMIT_B if true_state == 0 else COMMIT_A
        _, reward, _, _, info = info_env.step(wrong_action)
        assert reward == pytest.approx(-1.0)
        assert info["correct"] == False

    def test_seed_reproducibility(self):
        env1 = InfoSeekingEnv()
        env2 = InfoSeekingEnv()
        obs1, info1 = env1.reset(seed=123)
        obs2, info2 = env2.reset(seed=123)
        assert info1["true_state"] == info2["true_state"]


class TestInfoSeekingObservationModel:
    def test_observation_model_shape(self, info_env):
        model = info_env.get_observation_model()
        assert model.shape == (2, 2)

    def test_observation_model_rows_sum_to_one(self, info_env):
        model = info_env.get_observation_model()
        for row in model:
            np.testing.assert_almost_equal(row.sum(), 1.0)

    def test_observation_model_accuracy(self, info_env):
        model = info_env.get_observation_model()
        assert model[0, 0] == pytest.approx(0.75)
        assert model[1, 1] == pytest.approx(0.75)

    def test_observation_statistics(self, info_env):
        """Over many observations, signal frequencies should match the model."""
        info_env.reset(seed=42)
        true_state = info_env._true_state
        counts = {SIGNAL_A: 0, SIGNAL_B: 0}
        n = 5000
        for _ in range(n):
            obs = info_env._generate_observation()
            counts[obs] += 1

        expected_correct = SIGNAL_A if true_state == 0 else SIGNAL_B
        accuracy = counts[expected_correct] / n
        assert abs(accuracy - 0.75) < 0.03


class TestTigerGymInterface:
    def test_spaces(self, tiger_env):
        assert tiger_env.action_space.n == 3
        assert tiger_env.observation_space.n == 3

    def test_reset(self, tiger_env):
        obs, info = tiger_env.reset(seed=42)
        assert obs == TIGER_NULL
        assert "tiger_location" in info
        assert info["tiger_location"] in (0, 1)

    def test_listen(self, tiger_env):
        tiger_env.reset(seed=42)
        obs, reward, terminated, truncated, info = tiger_env.step(LISTEN)
        assert obs in (HEAR_LEFT, HEAR_RIGHT)
        assert reward == pytest.approx(-1.0)
        assert terminated is False

    def test_open_correct_door(self, tiger_env):
        tiger_env.reset(seed=42)
        tiger_loc = tiger_env._tiger_location
        safe_door = OPEN_RIGHT if tiger_loc == 0 else OPEN_LEFT
        _, reward, terminated, _, info = tiger_env.step(safe_door)
        assert reward == pytest.approx(10.0)
        assert terminated is True
        assert info["correct"] is True

    def test_open_wrong_door(self, tiger_env):
        tiger_env.reset(seed=42)
        tiger_loc = tiger_env._tiger_location
        bad_door = OPEN_LEFT if tiger_loc == 0 else OPEN_RIGHT
        _, reward, terminated, _, info = tiger_env.step(bad_door)
        assert reward == pytest.approx(-100.0)
        assert terminated is True
        assert info["correct"] is False

    def test_listen_count_increments(self, tiger_env):
        tiger_env.reset(seed=42)
        for i in range(5):
            _, _, _, _, info = tiger_env.step(LISTEN)
            assert info["listen_count"] == i + 1


class TestTigerObservationModel:
    def test_shape(self, tiger_env):
        model = tiger_env.get_observation_model()
        assert model.shape == (2, 2)

    def test_rows_sum_to_one(self, tiger_env):
        model = tiger_env.get_observation_model()
        for row in model:
            np.testing.assert_almost_equal(row.sum(), 1.0)

    def test_accuracy(self, tiger_env):
        model = tiger_env.get_observation_model()
        assert model[0, 0] == pytest.approx(0.85)
        assert model[1, 1] == pytest.approx(0.85)
