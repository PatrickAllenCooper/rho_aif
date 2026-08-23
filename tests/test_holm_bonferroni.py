"""Tests for the Holm-Bonferroni step-down correction.

This function had no test coverage, which is how a NaN-handling defect
survived in it while roughly ten call sites fed it unfiltered p-value lists.
A NaN failed the step-down threshold and hit the `break`, so every comparison
sorting after it was silently marked non-significant regardless of its own
p-value, and where the NaN landed depended on Python's sort stability.
"""

import math

import numpy as np
import pytest

from rho_aif.stats import holm_bonferroni


class TestHolmBonferroniBasics:
    def test_empty_family(self):
        assert holm_bonferroni([]) == []

    def test_single_significant(self):
        assert holm_bonferroni([0.01]) == [True]

    def test_single_not_significant(self):
        assert holm_bonferroni([0.20]) == [False]

    def test_step_down_thresholds(self):
        """With n=3 the thresholds are alpha/3, alpha/2, alpha in sorted order,
        so 0.0167, 0.025, and 0.05."""
        assert holm_bonferroni([0.01, 0.02, 0.04]) == [True, True, True]
        assert holm_bonferroni([0.02, 0.03, 0.04]) == [False, False, False]
        assert holm_bonferroni([0.01, 0.03, 0.04]) == [True, False, False]

    def test_stops_at_first_failure_in_sorted_order(self):
        """Holm is step-down. A failure blocks every LARGER p-value, so the
        blocking is by rank, not by position in the input list."""
        assert holm_bonferroni([0.001, 0.9, 0.002]) == [True, False, True]
        # 0.03 fails at rank 1 (threshold 0.025), so 0.04 at rank 2 is blocked
        # even though 0.04 alone would clear the rank-2 threshold of 0.05.
        assert holm_bonferroni([0.001, 0.03, 0.04]) == [True, False, False]

    def test_order_independence(self):
        p = [0.001, 0.02, 0.9, 0.04]
        out = holm_bonferroni(p)
        perm = [2, 0, 3, 1]
        permuted = holm_bonferroni([p[i] for i in perm])
        assert [permuted[perm.index(i)] for i in range(len(p))] == out

    def test_more_conservative_than_uncorrected(self):
        p = [0.03, 0.04, 0.045]
        assert all(x <= 0.05 for x in p)
        assert holm_bonferroni(p) == [False, False, False]


class TestNaNHandling:
    """The defect this file exists for."""

    def test_leading_nan_does_not_truncate_the_family(self):
        nan = float("nan")
        out = holm_bonferroni([nan, 1e-12, 1e-10, 1e-8])
        assert out[0] is False
        assert out[1:] == [True, True, True]

    def test_nan_marked_not_significant(self):
        out = holm_bonferroni([float("nan"), 0.001])
        assert out == [False, True]

    def test_nan_excluded_from_family_size(self):
        """A NaN must not inflate n, which would make the correction stricter
        than the number of real tests warrants."""
        nan = float("nan")
        with_nans = holm_bonferroni([0.02, 0.03, nan, nan, nan, nan])
        without = holm_bonferroni([0.02, 0.03])
        assert with_nans[:2] == without

    def test_all_nan(self):
        assert holm_bonferroni([float("nan")] * 4) == [False] * 4

    def test_numpy_nan_accepted(self):
        out = holm_bonferroni([np.nan, 1e-9])
        assert out == [False, True]

    def test_none_treated_as_undefined(self):
        out = holm_bonferroni([None, 1e-9])
        assert out == [False, True]

    def test_nan_position_does_not_change_the_verdicts(self):
        """The original defect made the outcome depend on where NaN sorted."""
        nan = float("nan")
        real = [1e-12, 1e-10, 1e-8, 0.9]
        for pos in range(len(real) + 1):
            family = real[:pos] + [nan] + real[pos:]
            out = holm_bonferroni(family)
            assert out[pos] is False
            recovered = out[:pos] + out[pos + 1:]
            assert recovered == [True, True, True, False], (pos, out)


class TestRegressionAgainstZeroVariance:
    def test_zero_variance_pair_does_not_suppress_a_real_effect(self):
        """The concrete trigger: two agents that both return a constant value
        give a Welch t-test a NaN p-value. Before the fix, that NaN could
        suppress a genuinely significant comparison elsewhere in the table."""
        from scipy.stats import ttest_ind

        constant = ttest_ind(np.full(50, 9.5), np.full(50, 9.5), equal_var=False).pvalue
        assert math.isnan(constant)

        strong = ttest_ind(np.zeros(50), np.ones(50), equal_var=False).pvalue
        out = holm_bonferroni([constant, strong])
        assert out == [False, True]
