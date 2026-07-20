"""Tests for seed-level statistical utilities."""

from dataclasses import dataclass

import numpy as np

from rho_aif.stats import (
    hierarchical_bootstrap_ci,
    seed_level_ttest,
    seed_means,
)


@dataclass
class FakeResult:
    seed: int
    total_reward: float


def test_seed_means_groups_correctly():
    results = [
        FakeResult(1, 1.0),
        FakeResult(1, 3.0),
        FakeResult(2, 10.0),
        FakeResult(2, 20.0),
    ]
    means = seed_means(results, lambda r: r.total_reward)
    assert len(means) == 2
    assert np.isclose(means[0], 2.0)
    assert np.isclose(means[1], 15.0)


def test_seed_level_ttest_runs():
    a = [FakeResult(s, 1.0 + 0.1 * i) for s in range(5) for i in range(10)]
    b = [FakeResult(s, 5.0 + 0.1 * i) for s in range(5) for i in range(10)]
    out = seed_level_ttest(a, b, lambda r: r.total_reward)
    assert out["n_seeds_a"] == 5
    assert out["p_value"] < 0.05


def test_hierarchical_bootstrap_ci_contains_mean():
    results = [FakeResult(s, float(s)) for s in range(5) for _ in range(20)]
    point, lo, hi = hierarchical_bootstrap_ci(
        results, lambda r: r.total_reward, n_bootstrap=500
    )
    assert lo <= point <= hi
