"""Unit tests for proper scoring rules."""

import math
import numpy as np
import pytest

from rho_aif.scoring import (
    log_score,
    brier_score,
    factored_log_score,
    factored_brier_score,
    binary_belief_from_fault_prob,
    extract_true_state,
)


class TestLogScore:
    def test_certain_correct(self):
        assert log_score([0.0, 1.0], 1) == pytest.approx(0.0, abs=1e-9)

    def test_certain_wrong_is_very_negative(self):
        # Clamped by eps=1e-12
        assert log_score([1.0, 0.0], 1) == pytest.approx(math.log(1e-12))

    def test_uniform_two_state(self):
        assert log_score([0.5, 0.5], 0) == pytest.approx(math.log(0.5))

    def test_out_of_range(self):
        with pytest.raises(ValueError):
            log_score([0.5, 0.5], 2)


class TestBrierScore:
    def test_certain_correct(self):
        assert brier_score([0.0, 1.0], 1) == pytest.approx(0.0)

    def test_certain_wrong(self):
        # (1-0)^2 + (0-1)^2 = 2
        assert brier_score([1.0, 0.0], 1) == pytest.approx(2.0)

    def test_uniform_two_state(self):
        # (0.5-1)^2 + (0.5-0)^2 = 0.5
        assert brier_score([0.5, 0.5], 0) == pytest.approx(0.5)


class TestFactoredScores:
    def test_binary_belief(self):
        np.testing.assert_allclose(binary_belief_from_fault_prob(0.3), [0.7, 0.3])

    def test_factored_mean(self):
        # Two components both certain-correct
        ls = factored_log_score([0.0, 1.0], [0, 1])
        bs = factored_brier_score([0.0, 1.0], [0, 1])
        assert ls == pytest.approx(0.0, abs=1e-9)
        assert bs == pytest.approx(0.0)


class TestExtractTrueState:
    def test_from_info_keys(self):
        assert extract_true_state({"tiger_location": 1}) == 1
        assert extract_true_state({"best_arm": 2}) == 2
        assert extract_true_state({"true_condition": 3}) == 3

    def test_from_env_attr(self):
        class Fake:
            _true_state = 0

        assert extract_true_state({}, Fake()) == 0
