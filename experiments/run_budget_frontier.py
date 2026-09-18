"""Budget-frontier study: the calibrated family at externally chosen budgets.

Predeclared on 2026-09-17 (ledger 9.17.45) in response to a review finding
that the budgeted formulation had only been compared to a constrained
reference at the endogenous budget B_EFE = U(w=1). This script tests the
calibration procedure at budgets a designer would state, on held-out seeds.

Design, fixed before any result was inspected
---------------------------------------------
Domains: Tiger, Diagnosis, Bandit (the three core observe-then-commit
environments, where the near-optimal constrained reference exists).
Family: the receding-horizon Planning+IG agent at each environment's
benchmark horizon, usage counted in observation actions, the same protocol
as the shadow-price curves of the paper's budget section.

Stage A, calibration (canonical seeds {42, 123, 456, 789, 1024}, 100
episodes per seed): estimate U(w) and the mean reward R(w) on the 16-point
log grid make_log_w_grid(0, 100, 16). Everything selected below is selected
on this data only.

Budgets per domain, from the calibration curve's attainable range
[U_min, U_max]: three interior budgets at fractions 0.25, 0.5, and 0.75 of
the range; one gap budget at the midpoint of the largest jump between
consecutive grid usages, which no single tested weight attains; and one
unattainable budget at 0.5 U_min, which is declared unattainable and not
evaluated. Where the calibration curve is non-monotone the last-crossing
convention of Definition PI-3 applies and the row says so.

Policies, each selected on the calibration data: (1) the endpoint mixture of
Definition PI-3, playing w_hi with probability q and w_lo otherwise, drawn
afresh each episode; (2) the two bracket endpoints played alone; (3) the
best feasible single member, the grid weight with the highest calibration
reward among those with calibration usage at or below B (none if no grid
weight is feasible).

Stage B, evaluation on held-out seeds {7, 8, 9, 10, 11}, 100 episodes per
seed, disjoint from the calibration seeds. Metrics: mean reward and mean
usage with seed-level standard errors, the expected-usage error |usage - B|,
feasibility (held-out mean usage at or below B), and the reward gap to the
near-optimal constrained reference at usage B, read by linear interpolation
of the committed Lagrangian frontier (results_cpomdp_frontier.csv), which is
also the direct usage-penalty method for these domains.

An expected budget is not a per-episode cap. The mixture attains B in
expectation on the calibration seeds by construction and is tested here on
seeds it never saw.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Dict, List, Optional

import numpy as np
import pandas as pd

_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT))
sys.path.insert(0, str(_ROOT / "experiments"))

from rho_aif.agents.planning_infogain import PlanningInfoGainAgent  # noqa: E402
from rho_aif.benchmark import get_benchmark, get_obs_models, make_env_config, run_otc_episode  # noqa: E402
from rho_aif.budget import (  # noqa: E402
    UsageCurvePoint,
    _obs_costs_from_env,
    episode_sensing_usage,
    make_log_w_grid,
    solve_shadow_price_from_curve,
    usage_value,
)
from run_experiment import provenance_fields  # noqa: E402

RESULTS = _ROOT / "results"
ENVS = ["Tiger", "Diagnosis", "Bandit"]
CAL_SEEDS = [42, 123, 456, 789, 1024]
HELDOUT_SEEDS = [7, 8, 9, 10, 11]
FRACTIONS = [0.25, 0.5, 0.75]
UNATTAINABLE_FACTOR = 0.5


def episode_seed(seed: int, ep: int) -> int:
    return int(seed) * 10_000 + int(ep)


def run_weight(env, w: float, horizon: int, seeds: List[int], n_ep: int, mixture=None):
    """Per-seed mean usage and reward at weight w, or for a mixture (w_lo, w_hi, q)."""
    obs_models, config, costs = get_obs_models(env), make_env_config(env), _obs_costs_from_env(env)
    agents = {}
    for ww in ([w] if mixture is None else [mixture[0], mixture[1]]):
        agents[ww] = PlanningInfoGainAgent(obs_models, config, planning_horizon=horizon, info_gain_weight=float(ww))
    us, rs = [], []
    for s in seeds:
        rng = np.random.default_rng(int(s) + 1_000_003)  # mixture draws, independent of the env stream
        su, sr = [], []
        for ep in range(n_ep):
            if mixture is None:
                agent = agents[w]
            else:
                agent = agents[mixture[1]] if rng.random() < mixture[2] else agents[mixture[0]]
            res = run_otc_episode(agent, env, seed=episode_seed(s, ep))
            su.append(usage_value(episode_sensing_usage(res, obs_costs=costs, usage_kind="count"), "count"))
            sr.append(float(res["total_reward"]))
        us.append(float(np.mean(su))); rs.append(float(np.mean(sr)))
    return us, rs


def se(x: List[float]) -> float:
    return float(np.std(x, ddof=1) / np.sqrt(len(x))) if len(x) > 1 else float("nan")


def calibrate(env_name: str, n_ep: int, n_grid: int, seeds: List[int]) -> pd.DataFrame:
    cfg = get_benchmark(env_name); env = cfg.env_factory()
    rows = []
    for w in make_log_w_grid(0.0, 100.0, n_grid):
        us, rs = run_weight(env, float(w), cfg.planning_horizon, seeds, n_ep)
        rows.append(dict(env=env_name, w=float(w), usage=float(np.mean(us)), usage_se=se(us),
                         reward=float(np.mean(rs)), reward_se=se(rs), per_seed_usage="|".join(f"{u:.4f}" for u in us),
                         per_seed_reward="|".join(f"{r:.4f}" for r in rs)))
        print(f"  {env_name} w={w:.4g}: U={rows[-1]['usage']:.3f} R={rows[-1]['reward']:.3f}", flush=True)
    return pd.DataFrame(rows)


def choose_budgets(curve: pd.DataFrame) -> List[dict]:
    us = curve["usage"].to_numpy(); u_min, u_max = float(us.min()), float(us.max())
    out = [dict(kind=f"interior_{f:g}", budget=u_min + f * (u_max - u_min)) for f in FRACTIONS]
    jumps = np.abs(np.diff(us)); j = int(np.argmax(jumps))
    out.append(dict(kind="gap", budget=float((us[j] + us[j + 1]) / 2.0)))
    out.append(dict(kind="unattainable", budget=UNATTAINABLE_FACTOR * u_min))
    return out


def frontier_reward_at(env_name: str, budget: float, frontier: pd.DataFrame) -> Optional[float]:
    f = frontier[frontier["env"] == env_name].sort_values("usage")
    if f.empty or budget < f["usage"].min() or budget > f["usage"].max():
        return None
    return float(np.interp(budget, f["usage"].to_numpy(), f["reward"].to_numpy()))


def evaluate(env_name: str, curve: pd.DataFrame, n_ep: int, seeds: List[int], frontier: pd.DataFrame) -> List[dict]:
    cfg = get_benchmark(env_name); env = cfg.env_factory(); H = cfg.planning_horizon
    pts = [UsageCurvePoint(w=float(r.w), mean_usage=float(r.usage), se_usage=float(r.usage_se), n_seeds=len(CAL_SEEDS),
                           per_seed_means=[float(x) for x in str(r.per_seed_usage).split("|")]) for r in curve.itertuples()]
    monotone = bool(np.all(np.diff(curve["usage"].to_numpy()) >= -1e-12))
    rows = []
    for b in choose_budgets(curve):
        B = float(b["budget"]); base = dict(env=env_name, budget_kind=b["kind"], budget=B, curve_monotone=monotone,
                                            frontier_reward_at_B=frontier_reward_at(env_name, B, frontier))
        if b["kind"] == "unattainable":
            rows.append(dict(base, policy="declared_unattainable", note=f"B below U_min={curve['usage'].min():.3f}, not evaluated"))
            print(f"  {env_name} B={B:.3f} ({b['kind']}): declared unattainable", flush=True); continue
        sol = solve_shadow_price_from_curve(pts, budget=B)
        if not sol.bracketed:
            rows.append(dict(base, policy="no_bracket", note=sol.note)); continue
        q = (B - sol.usage_lo) / (sol.usage_hi - sol.usage_lo)
        # best feasible single member on calibration data
        feas = curve[curve["usage"] <= B]
        best_w = float(feas.sort_values("reward", ascending=False).iloc[0]["w"]) if not feas.empty else None
        policies = [("mixture", None, (sol.w_lo, sol.w_hi, q)), ("endpoint_lo", sol.w_lo, None), ("endpoint_hi", sol.w_hi, None)]
        if best_w is not None:
            policies.append(("best_feasible_member", best_w, None))
        for name, w, mix in policies:
            us, rs = run_weight(env, w if w is not None else 0.0, H, seeds, n_ep, mixture=mix)
            mu, mr = float(np.mean(us)), float(np.mean(rs))
            fr = base["frontier_reward_at_B"]
            rows.append(dict(base, policy=name, w_lo=sol.w_lo, w_hi=sol.w_hi, q=q if name == "mixture" else np.nan,
                             w=(w if w is not None else np.nan), heldout_usage=mu, heldout_usage_se=se(us),
                             heldout_reward=mr, heldout_reward_se=se(rs), usage_error=abs(mu - B),
                             feasible_in_expectation=bool(mu <= B + 1e-9),
                             gap_to_frontier=(mr - fr) if fr is not None else np.nan, note="",
                             per_seed_usage="|".join(f"{u:.4f}" for u in us),
                             per_seed_reward="|".join(f"{r:.4f}" for r in rs)))
            print(f"  {env_name} B={B:.3f} ({b['kind']}) {name:22s} U={mu:.3f} R={mr:.3f}", flush=True)
    return rows


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--envs", nargs="*", default=ENVS)
    p.add_argument("--episodes", type=int, default=100)
    p.add_argument("--grid", type=int, default=16)
    p.add_argument("--quick", action="store_true", help="smoke test on scratch paths: 2 seeds, 4 episodes, 6-point grid")
    a = p.parse_args()
    cal_seeds, ho_seeds, n_ep, n_grid = CAL_SEEDS, HELDOUT_SEEDS, a.episodes, a.grid
    out_curve, out_eval = RESULTS / "results_budget_frontier_curve.csv", RESULTS / "results_budget_frontier.csv"
    if a.quick:
        cal_seeds, ho_seeds, n_ep, n_grid = CAL_SEEDS[:2], HELDOUT_SEEDS[:2], 4, 6
        import os, tempfile
        tmp = Path(os.environ.get("TMPDIR", tempfile.gettempdir()))
        out_curve, out_eval = tmp / "bf_curve_quick.csv", tmp / "bf_quick.csv"
        print("QUICK MODE: scratch output", flush=True)
    frontier = pd.read_csv(RESULTS / "results_cpomdp_frontier.csv")
    curves, evals = [], []
    for env_name in a.envs:
        print(f"\n=== Stage A calibration: {env_name} ===", flush=True)
        c = calibrate(env_name, n_ep, n_grid, cal_seeds); curves.append(c)
        print(f"=== Stage B held-out evaluation: {env_name} ===", flush=True)
        evals.extend(evaluate(env_name, c, n_ep, ho_seeds, frontier))
    cdf, edf = pd.concat(curves, ignore_index=True), pd.DataFrame(evals)
    prov = provenance_fields(cal_seeds, n_ep)
    for k, v in prov.items():
        cdf[k] = v
    prov_h = provenance_fields(ho_seeds, n_ep)
    for k, v in prov_h.items():
        edf[k] = v
    cdf.to_csv(out_curve, index=False); edf.to_csv(out_eval, index=False)
    print(f"\nSaved {out_curve}\nSaved {out_eval}")


if __name__ == "__main__":
    main()
