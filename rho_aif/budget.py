"""
Sensing-budget utilities: usage accounting and shadow-price bisection.

Recasts the Planning+IG weight w as an operational shadow price of a sensing
budget B. See Guidance_Documents/price_of_information.md.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, Sequence, Union

import numpy as np


@dataclass
class SensingUsage:
    """Per-episode sensing accounting."""

    num_observations: int
    sensing_cost: float

    @property
    def count(self) -> float:
        return float(self.num_observations)

    @property
    def cost(self) -> float:
        return float(self.sensing_cost)


@dataclass
class ShadowPriceResult:
    """Outcome of bisection / grid / curve solve for U(w) - B."""

    w_star: float
    w_lo: float
    w_hi: float
    usage_at_star: float
    usage_lo: float
    usage_hi: float
    budget: float
    usage_kind: str
    n_iters: int
    bracketed: bool
    achievable: bool = True
    note: str = ""
    usage_se_at_star: float = float("nan")
    usage_se_lo: float = float("nan")
    usage_se_hi: float = float("nan")
    u_min: float = float("nan")
    u_max: float = float("nan")


@dataclass
class UsageCurvePoint:
    """One grid point of an estimated usage curve U(w)."""

    w: float
    mean_usage: float
    se_usage: float
    n_seeds: int
    per_seed_means: List[float]


def make_log_w_grid(w_lo: float, w_hi: float, n_grid: int) -> np.ndarray:
    """Log-spaced nonnegative weight grid; includes 0 when w_lo == 0."""
    if w_lo < 0:
        raise ValueError("w_lo must be nonnegative")
    if w_hi <= w_lo:
        raise ValueError("w_hi must exceed w_lo")
    if n_grid < 2:
        raise ValueError("n_grid must be at least 2")
    if w_lo == 0.0:
        positive = np.logspace(
            np.log10(max(w_hi / (10 ** (n_grid - 1)), 1e-3)),
            np.log10(w_hi),
            num=n_grid - 1,
        )
        return np.concatenate([[0.0], positive])
    return np.logspace(np.log10(w_lo), np.log10(w_hi), num=n_grid)


def episode_sensing_usage(
    result: Any,
    obs_costs: Optional[Sequence[float]] = None,
    usage_kind: str = "count",
) -> SensingUsage:
    """
    Extract sensing usage from an episode result.

    Accepts:
      - EpisodeResult-like objects with ``num_observations``
      - dicts from ``run_otc_episode`` (``num_observations``) or
        ``run_inspection_episode`` (``tests``)
    """
    if isinstance(result, dict):
        if "num_observations" in result:
            n = int(result["num_observations"])
        elif "tests" in result:
            n = int(result["tests"])
        else:
            raise KeyError(
                "Episode result must contain 'num_observations' or 'tests'"
            )
    else:
        n = int(result.num_observations)

    if obs_costs is None or len(obs_costs) == 0:
        unit_cost = 1.0
    else:
        # Homogeneous costs in OTC envs; use mean absolute cost as unit price.
        unit_cost = float(np.mean([abs(float(c)) for c in obs_costs]))
    sensing_cost = n * unit_cost
    return SensingUsage(num_observations=n, sensing_cost=sensing_cost)


def usage_value(usage: SensingUsage, usage_kind: str = "count") -> float:
    kind = usage_kind.lower()
    if kind == "count":
        return usage.count
    if kind == "cost":
        return usage.cost
    raise ValueError(f"Unknown usage_kind {usage_kind!r}; use 'count' or 'cost'")


def _obs_costs_from_env(env) -> List[float]:
    if hasattr(env, "get_observation_costs"):
        return list(env.get_observation_costs())
    if hasattr(env, "observation_cost"):
        return [float(env.observation_cost)]
    if hasattr(env, "test_costs"):
        return [abs(float(c)) for c in env.test_costs]
    return [1.0]


def estimate_usage(
    env,
    w: float,
    seeds: Sequence[int],
    num_episodes: int,
    planning_horizon: int = 4,
    usage_kind: str = "count",
    family: str = "observe_then_commit",
    tree_depth: Optional[int] = None,
    max_steps: int = 200,
) -> float:
    """
    Estimate mean sensing usage U(w) under Planning+IG (or inspection tree search).

    Multi-seed average of per-episode usage.
    """
    # Lazy imports avoid circular dependency through rho_aif.agents.__init__.
    from rho_aif.agents.planning_infogain import PlanningInfoGainAgent
    from rho_aif.benchmark import (
        get_obs_models,
        make_env_config,
        make_inspection_agent,
        run_inspection_episode,
        run_otc_episode,
    )

    costs = _obs_costs_from_env(env)
    usages: List[float] = []

    for seed in seeds:
        np.random.seed(int(seed))
        if family == "inspection":
            depth = tree_depth if tree_depth is not None else planning_horizon
            agent = make_inspection_agent("planning+ig", env, depth, info_weight=w)
            for ep in range(num_episodes):
                result = run_inspection_episode(agent, env, seed=int(seed) + ep)
                u = episode_sensing_usage(result, obs_costs=costs, usage_kind=usage_kind)
                usages.append(usage_value(u, usage_kind))
        else:
            obs_models = get_obs_models(env)
            config = make_env_config(env)
            agent = PlanningInfoGainAgent(
                obs_models,
                config,
                planning_horizon=planning_horizon,
                info_gain_weight=w,
            )
            for _ in range(num_episodes):
                result = run_otc_episode(agent, env, max_steps=max_steps)
                u = episode_sensing_usage(result, obs_costs=costs, usage_kind=usage_kind)
                usages.append(usage_value(u, usage_kind))

    return float(np.mean(usages)) if usages else 0.0


def estimate_usage_curve(
    env,
    w_grid: Sequence[float],
    seeds: Sequence[int],
    num_episodes: int,
    planning_horizon: int = 4,
    usage_kind: str = "count",
    family: str = "observe_then_commit",
    tree_depth: Optional[int] = None,
    max_steps: int = 200,
) -> List[UsageCurvePoint]:
    """
    Estimate U(w) on a weight grid with per-seed means and SE across seeds.

    Returns one ``UsageCurvePoint`` per grid weight. SE is the standard error
    of the per-seed means (nan when fewer than two seeds).
    """
    points: List[UsageCurvePoint] = []
    for w in w_grid:
        per_seed: List[float] = []
        for seed in seeds:
            u = estimate_usage(
                env,
                w=float(w),
                seeds=[int(seed)],
                num_episodes=num_episodes,
                planning_horizon=planning_horizon,
                usage_kind=usage_kind,
                family=family,
                tree_depth=tree_depth,
                max_steps=max_steps,
            )
            per_seed.append(float(u))
        mean_u = float(np.mean(per_seed)) if per_seed else 0.0
        if len(per_seed) >= 2:
            se = float(np.std(per_seed, ddof=1) / np.sqrt(len(per_seed)))
        else:
            se = float("nan")
        points.append(
            UsageCurvePoint(
                w=float(w),
                mean_usage=mean_u,
                se_usage=se,
                n_seeds=len(per_seed),
                per_seed_means=list(per_seed),
            )
        )
    return points


def usage_curve_to_arrays(curve: Sequence[UsageCurvePoint]):
    """Return (w, mean_U, se_U) arrays from a usage curve."""
    ws = np.asarray([p.w for p in curve], dtype=float)
    us = np.asarray([p.mean_usage for p in curve], dtype=float)
    ses = np.asarray([p.se_usage for p in curve], dtype=float)
    return ws, us, ses


def solve_shadow_price_from_curve(
    curve: Sequence[UsageCurvePoint],
    budget: float,
    tol: float = 0.05,
) -> ShadowPriceResult:
    """
    Solve w*(B) from a precomputed usage curve.

    Returns the grid point minimizing |U - B|, plus the **step bracket**:
    the last w with U below B and the first w with U at/above B (when such
    neighbors exist). Also reports SEs at those points and the curve's
    [U_min, U_max] range.
    """
    if not curve:
        raise ValueError("curve must be nonempty")
    ws, us, ses = usage_curve_to_arrays(curve)
    order = np.argsort(ws)
    ws, us, ses = ws[order], us[order], ses[order]

    u_min = float(np.min(us))
    u_max = float(np.max(us))
    errs = np.abs(us - budget)
    best_i = int(np.argmin(errs))
    # Tie-break toward smaller w
    ties = np.where(np.abs(errs - errs[best_i]) <= 1e-12)[0]
    best_i = int(ties[0])

    # Step bracket: last below budget, first at/above budget along sorted w.
    below = np.where(us < budget - tol)[0]
    above = np.where(us >= budget - tol)[0]
    if len(below) and len(above):
        lo_i = int(below[-1])
        # first above that is >= lo_i when possible
        above_after = above[above >= lo_i]
        hi_i = int(above_after[0]) if len(above_after) else int(above[0])
        if hi_i < lo_i:
            lo_i, hi_i = hi_i, lo_i
        bracketed = True
    else:
        lo_i = max(0, best_i - 1)
        hi_i = min(len(ws) - 1, best_i + 1)
        bracketed = False

    achievable = bool(errs[best_i] <= tol or (u_min - tol <= budget <= u_max + tol))
    note = ""
    if budget < u_min - tol:
        note = "budget below observed U range; returning argmin U"
        achievable = False
    elif budget > u_max + tol:
        note = "budget above observed U range; returning argmax U"
        achievable = False

    return ShadowPriceResult(
        w_star=float(ws[best_i]),
        w_lo=float(ws[lo_i]),
        w_hi=float(ws[hi_i]),
        usage_at_star=float(us[best_i]),
        usage_lo=float(us[lo_i]),
        usage_hi=float(us[hi_i]),
        budget=float(budget),
        usage_kind="",
        n_iters=len(ws),
        bracketed=bracketed,
        achievable=achievable,
        note=note,
        usage_se_at_star=float(ses[best_i]),
        usage_se_lo=float(ses[lo_i]),
        usage_se_hi=float(ses[hi_i]),
        u_min=u_min,
        u_max=u_max,
    )


def identifiable_budgets(
    curve: Sequence[UsageCurvePoint],
    n_budgets: int = 5,
    margin: float = 0.05,
) -> List[float]:
    """
    Place budgets strictly inside [U(0-ish), U_max] from a usage curve.

    Uses the minimum and maximum mean usages on the curve as the identifiable
    range, shrunk by ``margin`` of the span so endpoints are not selected.
    """
    if not curve:
        return []
    us = np.asarray([p.mean_usage for p in curve], dtype=float)
    u_lo = float(np.min(us))
    u_hi = float(np.max(us))
    span = u_hi - u_lo
    if span <= 1e-9:
        return [u_lo]
    lo = u_lo + margin * span
    hi = u_hi - margin * span
    if hi <= lo:
        return [0.5 * (u_lo + u_hi)]
    n = max(1, int(n_budgets))
    return [float(x) for x in np.linspace(lo, hi, n)]


def bisect_usage_fn(
    usage_fn: Callable[[float], float],
    budget: float,
    w_lo: float = 0.0,
    w_hi: float = 100.0,
    tol: float = 0.05,
    w_tol: float = 1e-3,
    max_iters: int = 40,
) -> ShadowPriceResult:
    """
    Bisection on a monotone usage oracle U(w).

    Prefer ``grid_solve_usage_fn`` when U may be non-monotone (discrete
    policy switches). Kept for synthetic monotone oracles in tests.
    """
    if w_lo < 0:
        raise ValueError("w_lo must be nonnegative")
    if w_hi <= w_lo:
        raise ValueError("w_hi must exceed w_lo")

    u_lo = float(usage_fn(w_lo))
    u_hi = float(usage_fn(w_hi))
    n_iters = 0

    if u_lo >= budget - tol:
        achievable = abs(u_lo - budget) <= tol
        return ShadowPriceResult(
            w_star=w_lo,
            w_lo=w_lo,
            w_hi=w_hi,
            usage_at_star=u_lo,
            usage_lo=u_lo,
            usage_hi=u_hi,
            budget=budget,
            usage_kind="",
            n_iters=0,
            bracketed=achievable,
            achievable=achievable,
            note="" if achievable else "U(w_lo) exceeds budget; need w<0 or a larger B",
        )

    expand = 0
    while u_hi < budget - tol and expand < 8:
        w_hi *= 2.0
        u_hi = float(usage_fn(w_hi))
        expand += 1
        n_iters += 1

    if u_hi < budget - tol:
        return ShadowPriceResult(
            w_star=w_hi,
            w_lo=w_lo,
            w_hi=w_hi,
            usage_at_star=u_hi,
            usage_lo=u_lo,
            usage_hi=u_hi,
            budget=budget,
            usage_kind="",
            n_iters=n_iters,
            bracketed=False,
            achievable=False,
            note="U(w_hi) below budget after expansion",
        )

    lo, hi = w_lo, w_hi
    ulo, uhi = u_lo, u_hi
    best_w, best_u = w_lo, u_lo
    best_err = abs(u_lo - budget)
    for cand_w, cand_u in ((w_lo, u_lo), (w_hi, u_hi)):
        err = abs(cand_u - budget)
        if err < best_err:
            best_w, best_u, best_err = cand_w, cand_u, err

    while n_iters < max_iters and (hi - lo) > w_tol:
        mid = 0.5 * (lo + hi)
        umid = float(usage_fn(mid))
        n_iters += 1
        err = abs(umid - budget)
        if err < best_err:
            best_w, best_u, best_err = mid, umid, err
        if err <= tol:
            return ShadowPriceResult(
                w_star=mid,
                w_lo=lo,
                w_hi=hi,
                usage_at_star=umid,
                usage_lo=ulo,
                usage_hi=uhi,
                budget=budget,
                usage_kind="",
                n_iters=n_iters,
                bracketed=True,
                achievable=True,
            )
        if umid < budget:
            lo, ulo = mid, umid
        else:
            hi, uhi = mid, umid

    return ShadowPriceResult(
        w_star=best_w,
        w_lo=lo,
        w_hi=hi,
        usage_at_star=best_u,
        usage_lo=ulo,
        usage_hi=uhi,
        budget=budget,
        usage_kind="",
        n_iters=n_iters,
        bracketed=(ulo - budget) * (uhi - budget) <= 0 or best_err <= tol,
        achievable=best_err <= max(tol, 0.5),
    )


def grid_solve_usage_fn(
    usage_fn: Callable[[float], float],
    budget: float,
    w_lo: float = 0.0,
    w_hi: float = 100.0,
    n_grid: int = 12,
    tol: float = 0.05,
) -> ShadowPriceResult:
    """
    Find w minimizing |U(w) - B| on a log-spaced grid.

    Robust when U is only roughly monotone (discrete policy switches make
    U a noisy step function that can locally decrease).
    """
    grid = make_log_w_grid(w_lo, w_hi, n_grid)
    # Build a thin UsageCurvePoint list (no SE) and reuse the step-bracket solver.
    curve = [
        UsageCurvePoint(
            w=float(w),
            mean_usage=float(usage_fn(float(w))),
            se_usage=float("nan"),
            n_seeds=0,
            per_seed_means=[],
        )
        for w in grid
    ]
    return solve_shadow_price_from_curve(curve, budget=budget, tol=tol)


def solve_shadow_price(
    env,
    budget: float,
    w_lo: float = 0.0,
    w_hi: float = 100.0,
    tol: float = 0.05,
    w_tol: float = 1e-3,
    max_iters: int = 40,
    seeds: Optional[Sequence[int]] = None,
    num_episodes: int = 50,
    planning_horizon: int = 4,
    usage_kind: str = "count",
    family: str = "observe_then_commit",
    tree_depth: Optional[int] = None,
    n_grid: int = 12,
    method: str = "grid",
    curve: Optional[Sequence[UsageCurvePoint]] = None,
) -> ShadowPriceResult:
    """
    Find w*(B) so that estimated usage U(w) is near budget B.

    Default method is grid search (robust to non-monotone U). Pass
    ``method='bisect'`` only when U is known monotone. Pass a precomputed
    ``curve`` to skip re-estimation (uses step-bracket solve).
    """
    if curve is not None:
        result = solve_shadow_price_from_curve(curve, budget=budget, tol=tol)
        result.usage_kind = usage_kind
        return result

    if seeds is None:
        seeds = [42, 123, 456]

    def usage_fn(w: float) -> float:
        return estimate_usage(
            env,
            w=w,
            seeds=seeds,
            num_episodes=num_episodes,
            planning_horizon=planning_horizon,
            usage_kind=usage_kind,
            family=family,
            tree_depth=tree_depth,
        )

    if method == "bisect":
        result = bisect_usage_fn(
            usage_fn,
            budget=budget,
            w_lo=w_lo,
            w_hi=w_hi,
            tol=tol,
            w_tol=w_tol,
            max_iters=max_iters,
        )
    elif method == "grid":
        result = grid_solve_usage_fn(
            usage_fn,
            budget=budget,
            w_lo=w_lo,
            w_hi=w_hi,
            n_grid=n_grid,
            tol=tol,
        )
    else:
        raise ValueError(f"Unknown method {method!r}; use 'grid' or 'bisect'")
    result.usage_kind = usage_kind
    return result


def dual_update(w: float, usage: float, budget: float, lr: float) -> float:
    """Projected dual step driving usage to budget when U increases with w."""
    return max(0.0, float(w) + float(lr) * (float(budget) - float(usage)))
