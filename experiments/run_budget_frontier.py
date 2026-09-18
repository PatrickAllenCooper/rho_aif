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

Amendment, 2026-09-18 (ledger 9.17.46), made after the first results were
inspected and in response to a re-review, disclosed as such
-----------------------------------------------------------------------
(a) Reference. The reference was read by linear interpolation between the
    sampled frontier points at usage B and left blank when B lay outside
    the sampled usage range. Under the stated reference problem, maximize
    reward subject to expected usage at most B, any sampled reference
    policy using less than B stays feasible, so the reference is now the
    estimated feasible envelope
        V(B) = max sum_i q_i R_i  s.t.  q_i >= 0, sum_i q_i = 1,
                                        sum_i q_i U_i <= B,
    a linear program over the sampled (U_i, R_i) reference points whose
    solution mixes at most two of them (rho_aif.budget.feasible_envelope,
    shared with run_cpomdp_baseline.py and run_rocksample_cpomdp_reference.py
    since 9.17.47). Above the largest sampled usage the envelope is flat at
    the largest sampled reward, and it is defined at every budget at or above
    the smallest sampled usage (zero on all three committed frontiers). The
    interpolation is kept as a separate diagnostic column
    (frontier_interp_at_B) and is no longer the comparator.
(b) Two further policies, both selected on the calibration data only and
    evaluated on the held-out seeds: (4) the best target mixture, the
    reward-maximizing mixture over the calibration grid whose calibration
    usage equals B exactly (a linear program with an equality constraint,
    at most two support weights), which asks whether the selected crossing
    mixture is the best mixture that meets the target on the tested grid;
    and (5) the best feasible mixture, the same program with usage at most
    B, which is the family's estimated feasible envelope on the tested grid
    and reduces to the best feasible single member whenever the cap is
    slack. Neither policy is a claim about weights or mixtures the grid
    does not sample.
Existing policies and columns are unchanged, and the calibration stage is
deterministic under per-episode seeding, so the amended run reproduces every
previously reported number and adds rows and columns.
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
    feasible_envelope,
    lp_mixture,
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
    """Diagnostic only (amendment (a)): equal-usage linear interpolation between
    sampled frontier points, undefined outside the sampled usage range."""
    f = frontier[frontier["env"] == env_name].sort_values("usage")
    if f.empty or budget < f["usage"].min() or budget > f["usage"].max():
        return None
    return float(np.interp(budget, f["usage"].to_numpy(), f["reward"].to_numpy()))


def reference_envelope_at(env_name: str, budget: float, frontier: pd.DataFrame):
    """Amendment (a): the estimated feasible envelope of the sampled reference
    policies at budget B, max sum q_i R_i s.t. sum q_i U_i <= B. Defined at
    every budget at or above the smallest sampled usage, flat above the
    largest sampled usage. Returns (value, support string) or (None, '')."""
    f = frontier[frontier["env"] == env_name]
    if f.empty:
        return None, ""
    sol = feasible_envelope(f["usage"].to_numpy(dtype=float), f["reward"].to_numpy(dtype=float), budget)
    if sol is None:
        return None, ""
    q = sol["weights"]
    support = "|".join(f"lam={lam:.4g}:U={u:.3f}:R={r:.3f}:q={qq:.4f}"
                       for lam, u, r, qq in zip(f["lam"], f["usage"], f["reward"], q) if qq > 0)
    return sol["value"], support


def grid_lp_mixture(curve: pd.DataFrame, budget: float, equality: bool):
    """Amendment (b): reward-maximizing mixture over the calibration grid with
    calibration usage equal to (best target mixture) or at most (best feasible
    mixture) the budget. Returns dict(w_a, w_b, q_b, cal_reward, cal_usage) with
    w_b == w_a and q_b == 0 when a single grid weight is optimal, or None."""
    W = curve["w"].to_numpy(dtype=float); U = curve["usage"].to_numpy(dtype=float); R = curve["reward"].to_numpy(dtype=float)
    sol = lp_mixture(U, R, budget, equality=equality)
    if sol is None:
        return None
    q = sol["weights"]; idx = sol["support"]  # at most two, asserted in lp_mixture
    if len(idx) == 1:
        return dict(w_a=float(W[idx[0]]), w_b=float(W[idx[0]]), q_b=0.0, cal_reward=float(R[idx[0]]), cal_usage=float(U[idx[0]]))
    a, b = sorted(idx, key=lambda i: W[i])
    return dict(w_a=float(W[a]), w_b=float(W[b]), q_b=float(q[b]), cal_reward=float(R[a] * q[a] + R[b] * q[b]),
                cal_usage=float(U[a] * q[a] + U[b] * q[b]))


def evaluate(env_name: str, curve: pd.DataFrame, n_ep: int, seeds: List[int], frontier: pd.DataFrame) -> List[dict]:
    cfg = get_benchmark(env_name); env = cfg.env_factory(); H = cfg.planning_horizon
    pts = [UsageCurvePoint(w=float(r.w), mean_usage=float(r.usage), se_usage=float(r.usage_se), n_seeds=len(CAL_SEEDS),
                           per_seed_means=[float(x) for x in str(r.per_seed_usage).split("|")]) for r in curve.itertuples()]
    monotone = bool(np.all(np.diff(curve["usage"].to_numpy()) >= -1e-12))
    rows = []
    for b in choose_budgets(curve):
        B = float(b["budget"])
        ref_val, ref_support = reference_envelope_at(env_name, B, frontier)
        base = dict(env=env_name, budget_kind=b["kind"], budget=B, curve_monotone=monotone,
                    reference_envelope_at_B=(ref_val if ref_val is not None else np.nan),
                    reference_envelope_support=ref_support,
                    frontier_interp_at_B=frontier_reward_at(env_name, B, frontier))
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
        policies = [("mixture", None, (sol.w_lo, sol.w_hi, q), ""), ("endpoint_lo", sol.w_lo, None, ""), ("endpoint_hi", sol.w_hi, None, "")]
        if best_w is not None:
            policies.append(("best_feasible_member", best_w, None, ""))
        # Amendment (b): LP-selected mixtures over the calibration grid.
        for name, equality in (("best_target_mixture", True), ("best_feasible_mixture", False)):
            lp = grid_lp_mixture(curve, B, equality=equality)
            if lp is None:
                rows.append(dict(base, policy=name, note="no calibration-grid mixture meets this budget")); continue
            note = f"support w={lp['w_a']:.4g},{lp['w_b']:.4g} q_b={lp['q_b']:.4f} cal_reward={lp['cal_reward']:.4f} cal_usage={lp['cal_usage']:.4f}"
            if lp["q_b"] == 0.0:
                policies.append((name, lp["w_a"], None, note))
            else:
                policies.append((name, None, (lp["w_a"], lp["w_b"], lp["q_b"]), note))
        for name, w, mix, note in policies:
            us, rs = run_weight(env, w if w is not None else 0.0, H, seeds, n_ep, mixture=mix)
            mu, mr = float(np.mean(us)), float(np.mean(rs))
            fr, fi = base["reference_envelope_at_B"], base["frontier_interp_at_B"]
            rows.append(dict(base, policy=name, w_lo=(mix[0] if mix is not None else sol.w_lo), w_hi=(mix[1] if mix is not None else sol.w_hi),
                             q=(mix[2] if mix is not None else np.nan),
                             w=(w if w is not None else np.nan), heldout_usage=mu, heldout_usage_se=se(us),
                             heldout_reward=mr, heldout_reward_se=se(rs), usage_error=abs(mu - B),
                             feasible_in_expectation=bool(mu <= B + 1e-9),
                             gap_to_reference=(mr - fr) if not np.isnan(fr) else np.nan,
                             gap_to_frontier_interp=(mr - fi) if fi is not None else np.nan, note=note,
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
