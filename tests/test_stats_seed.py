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


def test_paired_tost_matches_one_sample_t_and_unpaired_sign():
    """Paired TOST on shared-seed differences (ledger 9.17.45/46)."""
    import pytest
    from scipy import stats as st

    from rho_aif.stats import tost_equivalence_paired

    a = np.array([6.284, 6.496, 6.028, 5.982, 6.516])
    b = np.array([6.379, 6.553, 5.965, 5.954, 6.548])
    r = tost_equivalence_paired(a, b, margin=0.5)
    d = a - b
    se = d.std(ddof=1) / np.sqrt(d.size)
    p_lower = 1 - st.t.cdf((d.mean() + 0.5) / se, d.size - 1)
    p_upper = st.t.cdf((d.mean() - 0.5) / se, d.size - 1)
    assert r["degenerate"] is False
    assert r["p_tost"] == pytest.approx(max(p_lower, p_upper))
    assert r["equivalent"] is True


def test_paired_tost_degenerate_branch_uses_limiting_p_values():
    import pytest

    from rho_aif.stats import tost_equivalence_paired

    # Zero differences inside the margin: both one-sided nulls rejected.
    r = tost_equivalence_paired(np.array([1.0, 2.0, 3.0]), np.array([1.0, 2.0, 3.0]), margin=1.0)
    assert r["degenerate"] is True and r["p_tost"] == 0.0 and r["equivalent"] is True
    # Constant difference on the margin: not equivalent, p = 1, never p = 0 with equivalent = False.
    r = tost_equivalence_paired(np.array([2.0, 2.0]), np.array([0.0, 0.0]), margin=2.0)
    assert r["degenerate"] is True and r["p_tost"] == 1.0 and r["equivalent"] is False
    # Constant difference outside the margin.
    r = tost_equivalence_paired(np.array([2.0, 2.0]), np.array([0.0, 0.0]), margin=1.0)
    assert r["p_tost"] == 1.0 and r["equivalent"] is False
    # Constant difference strictly inside the margin.
    r = tost_equivalence_paired(np.array([2.0, 2.0]), np.array([1.5, 1.5]), margin=1.0)
    assert r["p_tost"] == 0.0 and r["equivalent"] is True
    # Undersized or nonfinite inputs are rejected rather than scored.
    with pytest.raises(ValueError):
        tost_equivalence_paired(np.array([1.0]), np.array([0.0]), margin=1.0)
    with pytest.raises(ValueError):
        tost_equivalence_paired(np.array([1.0, np.nan]), np.array([0.0, 0.0]), margin=1.0)
    with pytest.raises(ValueError):
        tost_equivalence_paired(np.array([1.0, 2.0]), np.array([0.0, 0.0]), margin=0.0)
