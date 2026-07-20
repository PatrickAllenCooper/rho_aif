"""Tests for Proposition 2 threshold computation."""

import numpy as np
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "experiments"))

from run_thresholds import (  # noqa: E402
    ENV_PARAMS,
    compute_row,
    i_max,
    w_thresh_lower,
    w_thresh_upper,
)


def test_tiger_threshold_nats_matches_reviewer_calculation():
    p = ENV_PARAMS["Tiger"]
    w = w_thresh_lower(p["p"], p["c"], p["R_plus"], p["R_minus"], base=np.e)
    # Reviewers: approximately -138.7
    assert w < -130
    assert w > -145


def test_diagnosis_threshold_nats():
    p = ENV_PARAMS["Diagnosis"]
    w = w_thresh_lower(p["p"], p["c"], p["R_plus"], p["R_minus"], base=np.e)
    assert w < -80
    assert w > -95


def test_old_table_values_are_incorrect():
    """Document that published -5.04 / -2.34 do not match the formula."""
    tiger = w_thresh_lower(0.85, 1.0, 10.0, -100.0, base=np.e)
    diag = w_thresh_lower(0.80, 1.0, 10.0, -50.0, base=np.e)
    assert abs(tiger - (-5.04)) > 50
    assert abs(diag - (-2.34)) > 50


def test_i_max_positive_and_below_ln2():
    I = i_max(0.85, base=np.e)
    assert 0 < I < np.log(2)


def test_upper_threshold_above_lower_when_finite():
    for name, params in ENV_PARAMS.items():
        row = compute_row(name, params)
        lo = row["w_thresh_lower_nats"]
        hi = row["w_thresh_upper_nats"]
        if np.isfinite(hi):
            assert hi >= 0
            # Lower is typically largely negative; upper should exceed lower.
            assert hi > lo


def test_w1_sufficient_on_high_asymmetry():
    for name in ("Tiger", "Diagnosis", "Tileworld"):
        row = compute_row(name, ENV_PARAMS[name])
        assert row["w1_sufficient_nats"] is True
