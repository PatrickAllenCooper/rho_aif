"""
Statistical analysis utilities for experiment reporting.

Provides bootstrap confidence intervals, effect sizes, and
multiple-comparison correction for rigorous reporting.
"""

import numpy as np
from typing import List, Tuple, Dict


def bootstrap_ci(
    data: np.ndarray,
    statistic=np.mean,
    n_bootstrap: int = 10000,
    confidence: float = 0.95,
    seed: int = 42,
) -> Tuple[float, float, float]:
    """
    Compute bootstrap confidence interval for a statistic.

    Returns (point_estimate, ci_lower, ci_upper).
    """
    rng = np.random.RandomState(seed)
    n = len(data)
    point = float(statistic(data))
    boot_stats = np.array([
        statistic(data[rng.randint(0, n, size=n)])
        for _ in range(n_bootstrap)
    ])
    alpha = 1.0 - confidence
    ci_lower = float(np.percentile(boot_stats, 100 * alpha / 2))
    ci_upper = float(np.percentile(boot_stats, 100 * (1 - alpha / 2)))
    return point, ci_lower, ci_upper


def cohens_d(group1: np.ndarray, group2: np.ndarray) -> float:
    """Compute Cohen's d effect size between two groups."""
    n1, n2 = len(group1), len(group2)
    var1, var2 = np.var(group1, ddof=1), np.var(group2, ddof=1)
    pooled_std = np.sqrt(((n1 - 1) * var1 + (n2 - 1) * var2) / (n1 + n2 - 2))
    if pooled_std < 1e-10:
        return 0.0
    return float((np.mean(group1) - np.mean(group2)) / pooled_std)


def holm_bonferroni(p_values: List[float], alpha: float = 0.05) -> List[bool]:
    """
    Apply Holm-Bonferroni correction for multiple comparisons.

    Returns list of booleans indicating significance after correction.
    """
    n = len(p_values)
    indexed = sorted(enumerate(p_values), key=lambda x: x[1])
    significant = [False] * n

    for rank, (orig_idx, p) in enumerate(indexed):
        adjusted_alpha = alpha / (n - rank)
        if p <= adjusted_alpha:
            significant[orig_idx] = True
        else:
            break

    return significant


def compute_comparison_stats(
    results_a: List,
    results_b: List,
    metric_fn,
) -> Dict:
    """
    Compute full comparison statistics between two result sets.

    Returns dict with point estimates, CIs, effect size, and p-value.
    """
    from scipy.stats import ttest_ind

    vals_a = np.array([metric_fn(r) for r in results_a])
    vals_b = np.array([metric_fn(r) for r in results_b])

    mean_a, ci_a_lo, ci_a_hi = bootstrap_ci(vals_a)
    mean_b, ci_b_lo, ci_b_hi = bootstrap_ci(vals_b)

    d = cohens_d(vals_a, vals_b)
    t_stat, p_val = ttest_ind(vals_a, vals_b)

    return {
        "mean_a": mean_a, "ci_a": (ci_a_lo, ci_a_hi),
        "mean_b": mean_b, "ci_b": (ci_b_lo, ci_b_hi),
        "cohens_d": d,
        "t_stat": float(t_stat),
        "p_value": float(p_val),
    }
