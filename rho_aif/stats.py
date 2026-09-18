"""
Statistical analysis utilities for experiment reporting.

Provides bootstrap confidence intervals, effect sizes, and
multiple-comparison correction for rigorous reporting.
"""

import math

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
    Apply the Holm-Bonferroni step-down correction for multiple comparisons.

    Returns a list of booleans indicating significance after correction.

    NaN p-values are excluded from the family rather than ranked with it. A NaN
    arises when a test is undefined, which here means both arms had zero
    variance and identical means, so the comparison carries no evidence either
    way. Ranking NaN inside the family was a real defect: NaN fails the
    ``p <= alpha/(n-rank)`` test, and the step-down breaks on the first
    failure, so a NaN landing early in the sort order silently marked every
    comparison after it non-significant regardless of its p-value. Where NaN
    sorted was an artifact of Python's sort stability, so the number of
    suppressed comparisons varied with input order. Excluded entries are
    reported as not significant, which is correct, and they no longer inflate
    the family size ``n`` either.
    """
    n = len(p_values)
    significant = [False] * n

    valid = [
        (i, float(p)) for i, p in enumerate(p_values)
        if p is not None and not math.isnan(float(p))
    ]
    m = len(valid)
    if m == 0:
        return significant

    for rank, (orig_idx, p) in enumerate(sorted(valid, key=lambda x: x[1])):
        adjusted_alpha = alpha / (m - rank)
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
    # Welch (unequal-variance) t-test, matching tost_equivalence and the
    # manuscript's declared methodology.
    t_stat, p_val = ttest_ind(vals_a, vals_b, equal_var=False)

    return {
        "mean_a": mean_a, "ci_a": (ci_a_lo, ci_a_hi),
        "mean_b": mean_b, "ci_b": (ci_b_lo, ci_b_hi),
        "cohens_d": d,
        "t_stat": float(t_stat),
        "p_value": float(p_val),
    }


def seed_means(
    results: List,
    metric_fn,
    seed_attr: str = "seed",
) -> np.ndarray:
    """
    Collapse episode-level results to per-seed means.

    Each result must expose ``seed_attr`` (default ``seed``). Returns an
    array of length n_seeds for hierarchical / seed-level inference.
    """
    by_seed: Dict[object, List[float]] = {}
    for r in results:
        if isinstance(r, dict):
            seed = r[seed_attr]
            val = metric_fn(r)
        else:
            seed = getattr(r, seed_attr)
            val = metric_fn(r)
        by_seed.setdefault(seed, []).append(float(val))

    # Sort numerically when every seed label is numeric (string sorting puts
    # 1024 before 123 before 42, silently misaligning any array zipped
    # against the nominal seed list); fall back to string order otherwise.
    def _sort_key(item):
        key = item[0]
        if isinstance(key, (int, float)) and not isinstance(key, bool):
            return (0, float(key))
        return (1, str(key))

    return np.array([np.mean(v) for _, v in sorted(by_seed.items(), key=_sort_key)])


def seed_level_ttest(
    results_a: List,
    results_b: List,
    metric_fn,
    seed_attr: str = "seed",
) -> Dict:
    """
    Two-sample t-test on per-seed means (n = number of seeds).

    Complements pooled episode-level t-tests, which inflate degrees of
    freedom when episodes within a seed are dependent.
    """
    from scipy.stats import ttest_ind

    means_a = seed_means(results_a, metric_fn, seed_attr=seed_attr)
    means_b = seed_means(results_b, metric_fn, seed_attr=seed_attr)
    # Welch (unequal-variance) t-test on per-seed means, consistent with
    # tost_equivalence and the manuscript's declared methodology.
    t_stat, p_val = ttest_ind(means_a, means_b, equal_var=False)
    return {
        "n_seeds_a": int(len(means_a)),
        "n_seeds_b": int(len(means_b)),
        "mean_of_seed_means_a": float(np.mean(means_a)),
        "mean_of_seed_means_b": float(np.mean(means_b)),
        "seed_means_a": means_a.tolist(),
        "seed_means_b": means_b.tolist(),
        "t_stat": float(t_stat),
        "p_value": float(p_val),
        "cohens_d": cohens_d(means_a, means_b),
    }


def tost_equivalence(
    means_a: np.ndarray,
    means_b: np.ndarray,
    margin: float,
    alpha: float = 0.05,
) -> Dict:
    """
    Two one-sided tests (TOST) for equivalence within a predeclared margin.

    Tests the pair of one-sided hypotheses
        H0_lower: mean(a) - mean(b) <= -margin
        H0_upper: mean(a) - mean(b) >= +margin
    against the equivalence alternative -margin < mean(a) - mean(b) < margin,
    using Welch's t (unequal variance) on ``means_a``/``means_b`` -- pass
    per-seed means, not pooled episode-level values, so degrees of freedom
    reflect the number of independent seeds. Rejecting both one-sided
    nulls at level ``alpha`` (``p_tost < alpha``) supports equivalence;
    this is equivalent to the (1 - 2*alpha) two-sided CI of the mean
    difference lying entirely inside (-margin, +margin) (Schuirmann, 1987).

    The margin must be declared before inspecting these two samples for
    the test to carry its usual interpretation; this function does not
    choose or validate the margin.
    """
    from scipy.stats import t as tdist

    a = np.asarray(means_a, dtype=float)
    b = np.asarray(means_b, dtype=float)
    n_a, n_b = len(a), len(b)
    if n_a < 2 or n_b < 2:
        raise ValueError("tost_equivalence requires at least 2 samples per group")
    diff = float(np.mean(a) - np.mean(b))
    var_a, var_b = np.var(a, ddof=1), np.var(b, ddof=1)
    se = float(np.sqrt(var_a / n_a + var_b / n_b))
    if se < 1e-12:
        df = float(n_a + n_b - 2)
    else:
        df = float(
            (var_a / n_a + var_b / n_b) ** 2
            / ((var_a / n_a) ** 2 / (n_a - 1) + (var_b / n_b) ** 2 / (n_b - 1))
        )

    if se < 1e-12:
        p_lower = 0.0 if diff > -margin else 1.0
        p_upper = 0.0 if diff < margin else 1.0
    else:
        t_lower = (diff + margin) / se
        t_upper = (diff - margin) / se
        p_lower = float(tdist.sf(t_lower, df))
        p_upper = float(tdist.cdf(t_upper, df))
    p_tost = max(p_lower, p_upper)

    ci_conf = 1.0 - 2.0 * alpha
    tcrit = float(tdist.ppf(1.0 - alpha, df))
    ci_lo = diff - tcrit * se
    ci_hi = diff + tcrit * se

    return {
        "diff": diff,
        "se": se,
        "df": df,
        "margin": float(margin),
        "alpha": float(alpha),
        "n_a": int(n_a),
        "n_b": int(n_b),
        "p_lower": p_lower,
        "p_upper": p_upper,
        "p_tost": float(p_tost),
        "equivalent": bool(p_tost < alpha),
        "ci_conf": float(ci_conf),
        "ci": (float(ci_lo), float(ci_hi)),
    }


def hierarchical_bootstrap_ci(
    results: List,
    metric_fn,
    seed_attr: str = "seed",
    n_bootstrap: int = 10000,
    confidence: float = 0.95,
    seed: int = 42,
) -> tuple:
    """
    Hierarchical bootstrap: resample seeds, then resample episodes within seed.

    Returns (point_estimate, ci_lower, ci_upper) for the grand mean.
    """
    by_seed: Dict[object, np.ndarray] = {}
    for r in results:
        if isinstance(r, dict):
            s = r[seed_attr]
            val = metric_fn(r)
        else:
            s = getattr(r, seed_attr)
            val = metric_fn(r)
        by_seed.setdefault(s, []).append(float(val))
    seed_keys = list(by_seed.keys())
    arrays = {s: np.asarray(by_seed[s], dtype=float) for s in seed_keys}
    point = float(np.mean([np.mean(arrays[s]) for s in seed_keys]))

    rng = np.random.RandomState(seed)
    n_seeds = len(seed_keys)
    boot = np.empty(n_bootstrap)
    for b in range(n_bootstrap):
        chosen = rng.randint(0, n_seeds, size=n_seeds)
        means = []
        for idx in chosen:
            arr = arrays[seed_keys[idx]]
            draws = arr[rng.randint(0, len(arr), size=len(arr))]
            means.append(np.mean(draws))
        boot[b] = np.mean(means)

    alpha = 1.0 - confidence
    return (
        point,
        float(np.percentile(boot, 100 * alpha / 2)),
        float(np.percentile(boot, 100 * (1 - alpha / 2))),
    )

def tost_equivalence_paired(
    means_a: np.ndarray,
    means_b: np.ndarray,
    margin: float,
    alpha: float = 0.05,
) -> Dict:
    """Paired TOST on per-seed differences d_i = a_i - b_i (one-sample t on d).

    The sensitivity companion to tost_equivalence for designs that share a
    seed list. When the two arms share randomness the paired analysis is the
    sharper one; when they do not, the unpaired Welch form is the conservative
    one. Reporting both shows which way the shared-seed covariance cuts
    (ledger 9.17.45).
    """
    from scipy import stats as _st

    a = np.asarray(means_a, dtype=float)
    b = np.asarray(means_b, dtype=float)
    if a.shape != b.shape:
        raise ValueError("paired TOST needs equal-length per-seed arrays")
    d = a - b
    n = int(d.size)
    diff = float(np.mean(d))
    sd = float(np.std(d, ddof=1)) if n > 1 else float("nan")
    se = sd / np.sqrt(n) if n > 1 else float("nan")
    df = n - 1
    if not np.isfinite(se) or se == 0.0:
        # Identical trajectories (e.g. Tiger): a zero difference with zero
        # spread is inside any positive margin, so both one-sided nulls are
        # rejected trivially. Report p = 0 and flag the degenerate variance.
        return dict(diff=diff, se=0.0, df=df, p_lower=0.0, p_upper=0.0,
                    p_tost=0.0, equivalent=bool(abs(diff) < margin), degenerate=True)
    t_lower = (diff + margin) / se   # H0: diff <= -margin
    t_upper = (diff - margin) / se   # H0: diff >= +margin
    p_lower = float(1.0 - _st.t.cdf(t_lower, df))
    p_upper = float(_st.t.cdf(t_upper, df))
    p_tost = max(p_lower, p_upper)
    return dict(diff=diff, se=se, df=df, p_lower=p_lower, p_upper=p_upper,
                p_tost=p_tost, equivalent=bool(p_tost < alpha), degenerate=False)
