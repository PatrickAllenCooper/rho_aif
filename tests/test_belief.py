"""Tests for belief state representation and Bayesian updating."""

import numpy as np
import pytest
from rho_aif.belief import BeliefState


class TestBeliefInitialization:
    def test_uniform_prior(self):
        b = BeliefState(num_states=2)
        np.testing.assert_array_almost_equal(b.belief, [0.5, 0.5])

    def test_custom_prior(self):
        b = BeliefState(num_states=2, initial_belief=np.array([0.7, 0.3]))
        np.testing.assert_array_almost_equal(b.belief, [0.7, 0.3])

    def test_three_states(self):
        b = BeliefState(num_states=3)
        np.testing.assert_array_almost_equal(b.belief, [1 / 3, 1 / 3, 1 / 3])

    def test_history_initialized(self):
        b = BeliefState(num_states=2)
        assert len(b.history) == 1
        np.testing.assert_array_almost_equal(b.history[0], [0.5, 0.5])


class TestBayesianUpdate:
    def test_update_with_correct_signal(self):
        obs_model = np.array([[0.75, 0.25], [0.25, 0.75]])
        b = BeliefState(num_states=2)
        b.update(0, obs_model)  # SIGNAL_A
        assert b.belief[0] > 0.5
        np.testing.assert_almost_equal(b.belief[0], 0.75)

    def test_update_with_opposing_signal(self):
        obs_model = np.array([[0.75, 0.25], [0.25, 0.75]])
        b = BeliefState(num_states=2)
        b.update(1, obs_model)  # SIGNAL_B
        assert b.belief[1] > 0.5
        np.testing.assert_almost_equal(b.belief[1], 0.75)

    def test_consecutive_same_signals_increase_confidence(self):
        obs_model = np.array([[0.75, 0.25], [0.25, 0.75]])
        b = BeliefState(num_states=2)
        b.update(0, obs_model)
        conf_after_1 = b.confidence()
        b.update(0, obs_model)
        conf_after_2 = b.confidence()
        assert conf_after_2 > conf_after_1

    def test_opposing_signals_return_toward_uniform(self):
        obs_model = np.array([[0.75, 0.25], [0.25, 0.75]])
        b = BeliefState(num_states=2)
        b.update(0, obs_model)
        b.update(1, obs_model)
        np.testing.assert_array_almost_equal(b.belief, [0.5, 0.5])

    def test_history_grows_with_updates(self):
        obs_model = np.array([[0.75, 0.25], [0.25, 0.75]])
        b = BeliefState(num_states=2)
        b.update(0, obs_model)
        b.update(0, obs_model)
        assert len(b.history) == 3

    def test_beliefs_sum_to_one(self):
        obs_model = np.array([[0.85, 0.15], [0.15, 0.85]])
        b = BeliefState(num_states=2, initial_belief=np.array([0.3, 0.7]))
        for _ in range(10):
            b.update(0, obs_model)
        np.testing.assert_almost_equal(b.belief.sum(), 1.0)

    def test_convergence_under_repeated_evidence(self):
        """Many consistent signals should drive belief close to certainty."""
        obs_model = np.array([[0.85, 0.15], [0.15, 0.85]])
        b = BeliefState(num_states=2)
        for _ in range(20):
            b.update(0, obs_model)
        assert b.belief[0] > 0.999


class TestBeliefProperties:
    def test_entropy_uniform(self):
        b = BeliefState(num_states=2)
        np.testing.assert_almost_equal(b.entropy(), 1.0)

    def test_entropy_certain(self):
        b = BeliefState(num_states=2, initial_belief=np.array([1.0, 0.0]))
        np.testing.assert_almost_equal(b.entropy(), 0.0)

    def test_entropy_decreases_with_evidence(self):
        obs_model = np.array([[0.75, 0.25], [0.25, 0.75]])
        b = BeliefState(num_states=2)
        h0 = b.entropy()
        b.update(0, obs_model)
        assert b.entropy() < h0

    def test_most_likely_state(self):
        b = BeliefState(num_states=2, initial_belief=np.array([0.3, 0.7]))
        assert b.most_likely_state() == 1

    def test_confidence(self):
        b = BeliefState(num_states=2, initial_belief=np.array([0.3, 0.7]))
        np.testing.assert_almost_equal(b.confidence(), 0.7)

    def test_copy_is_independent(self):
        b = BeliefState(num_states=2)
        c = b.copy()
        obs_model = np.array([[0.75, 0.25], [0.25, 0.75]])
        c.update(0, obs_model)
        np.testing.assert_array_almost_equal(b.belief, [0.5, 0.5])
        assert c.belief[0] > 0.5


class TestBeliefReset:
    def test_reset_to_uniform(self):
        obs_model = np.array([[0.75, 0.25], [0.25, 0.75]])
        b = BeliefState(num_states=2)
        b.update(0, obs_model)
        b.reset()
        np.testing.assert_array_almost_equal(b.belief, [0.5, 0.5])
        assert len(b.history) == 1

    def test_reset_to_custom(self):
        b = BeliefState(num_states=2)
        b.reset(initial_belief=np.array([0.8, 0.2]))
        np.testing.assert_array_almost_equal(b.belief, [0.8, 0.2])
