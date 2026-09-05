"""The summary JSON's shadow-staircase verdict must derive from the usage-curve CSV.

Regression test for a fossil. From 2026-08 to 2026-09-05 the price-of-information
summary carried a verdict string saying Tiger and Diagnosis were non-monotone
while results_price_usage_curves.csv and Section 6.6 said they were
nondecreasing, because the producer merged prior verdict keys forward and no
longer computed this one. The verdict is now a pure function of the CSV.
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from run_price_of_information import staircase_verdict

ROOT = Path(__file__).resolve().parents[1]


def _curve(env, usages):
    return pd.DataFrame({
        "env": env, "w": np.arange(len(usages), dtype=float),
        "mean_usage": usages, "se_usage": 0.1, "n_seeds": 5,
    })


def test_monotone_and_non_monotone_envs_are_named_correctly():
    df = pd.concat([_curve("A", [1, 2, 2, 3]), _curve("B", [3, 2, 4, 4])], ignore_index=True)
    s = staircase_verdict(df)
    assert s.startswith("PARTIAL")
    assert "A nondecreasing" in s
    assert "B locally non-monotone" in s
    assert "\u2014" not in s


def test_all_monotone_gives_hold():
    df = pd.concat([_curve("A", [1, 2, 2]), _curve("B", [0, 0, 5])], ignore_index=True)
    assert staircase_verdict(df).startswith("HOLD")


def test_grid_order_not_row_order_decides_monotonicity():
    df = _curve("A", [3, 1, 2]).iloc[::-1].reset_index(drop=True)
    assert "A locally non-monotone" in staircase_verdict(df)


def test_committed_summary_agrees_with_committed_usage_curves():
    curve_path = ROOT / "results" / "results_price_usage_curves.csv"
    summary_path = ROOT / "results" / "results_price_of_information_summary.json"
    if not (curve_path.exists() and summary_path.exists()):
        pytest.skip("canonical artifacts not present")
    expected = staircase_verdict(pd.read_csv(curve_path))
    with open(summary_path) as f:
        actual = json.load(f)["verdict"]["shadow_staircases"]
    assert actual == expected
