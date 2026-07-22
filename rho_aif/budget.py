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
    """Outcome of bisection on U(w) - B."""

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
    if w_lo < 0:
        raise ValueError("w_lo must be nonnegative")
    if w_hi <= w_lo:
        raise ValueError("w_hi must exceed w_lo")
    if n_grid < 2:
        raise ValueError("n_grid must be at least 2")

    # Include 0 explicitly, then log-space the rest.
    if w_lo == 0.0:
        positive = np.logspace(
            np.log10(max(w_hi / (10 ** (n_grid - 1)), 1e-3)),
            np.log10(w_hi),
            num=n_grid - 1,
        )
        grid = np.concatenate([[0.0], positive])
    else:
        grid = np.logspace(np.log10(w_lo), np.log10(w_hi), num=n_grid)

    usages = []
    best_w, best_u, best_err = grid[0], None, float("inf")
    u_min, u_max = float("inf"), -float("inf")
    for w in grid:
        u = float(usage_fn(float(w)))
        usages.append(u)
        u_min = min(u_min, u)
        u_max = max(u_max, u)
        err = abs(u - budget)
        if err < best_err - 1e-12 or (abs(err - best_err) <= 1e-12 and w < best_w):
            best_w, best_u, best_err = float(w), u, err

    assert best_u is not None
    # Bracket: nearest grid neighbors around best_w
    idx = int(np.argmin(np.abs(grid - best_w)))
    lo_i = max(0, idx - 1)
    hi_i = min(len(grid) - 1, idx + 1)
    achievable = best_err <= tol or (u_min - tol <= budget <= u_max + tol)
    note = ""
    if budget < u_min - tol:
        note = "budget below observed U range; returning argmin U"
        achievable = False
    elif budget > u_max + tol:
        note = "budget above observed U range; returning argmax U"
        achievable = False

    return ShadowPriceResult(
        w_star=best_w,
        w_lo=float(grid[lo_i]),
        w_hi=float(grid[hi_i]),
        usage_at_star=best_u,
        usage_lo=float(min(usages[lo_i], usages[hi_i])),
        usage_hi=float(max(usages[lo_i], usages[hi_i])),
        budget=budget,
        usage_kind="",
        n_iters=len(grid),
        bracketed=achievable,
        achievable=achievable,
        note=note,
    )


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
) -> ShadowPriceResult:
    """
    Find w*(B) so that estimated usage U(w) is near budget B.

    Default method is grid search (robust to non-monotone U). Pass
    ``method='bisect'`` only when U is known monotone.
    """
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
