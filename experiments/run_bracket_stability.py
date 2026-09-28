#!/usr/bin/env python3
"""
Seed-bootstrap stability of the shadow-price crossing brackets.

The staircase battery (``run_price_of_information.py --only curves``) reports,
for each identifiable budget, the grid bracket (w_lo, w_hi] in which the
estimated usage curve last crosses the budget, together with the standard
error of usage at the selected grid point. That SE describes usage at a fixed
weight. It does not describe how often a fresh five-seed sample would select
the same bracket. This script measures that.

Protocol (predeclared 2026-09-28, ledger 9.17.50, before any output was seen):

1. Re-estimate the five staircase usage curves under the producer's exact
   full-mode settings (seeds {42, 123, 456, 789, 1024}, 100 episodes per
   (w, seed) cell, 40 on Tileworld-6x6 and 30 on Inspection-N8, grids of 16,
   10 on Tileworld-6x6 and 8 on Inspection-N8) and persist the per-seed means.
   Assert that the recomputed per-weight means reproduce the committed
   ``results_price_usage_curves.csv`` to 1e-9. A mismatch aborts the run.
2. For each committed budget in ``results_price_shadow_curves.csv``, draw
   2000 bootstrap resamples of the five seed indices with replacement, jointly
   across all weights (a seed's episode stream is shared across weights), and
   rerun the same solver, ``solve_shadow_price_from_curve``.
3. Report, per budget: the fraction of resamples selecting the reported
   bracket, the fraction producing any bracket, the number of distinct
   brackets, and the smallest set of brackets covering at least 90 percent of
   resamples. The outputs are descriptive. No pass threshold is declared.

Bootstrap RNG seed 20260928.

Outputs:
  results/results_price_usage_curves_per_seed.csv
  results/results_price_bracket_stability.csv
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT))
sys.path.insert(0, str(_ROOT / "experiments"))

import numpy as np
import pandas as pd

from rho_aif.benchmark import get_benchmark
from rho_aif.budget import (
    UsageCurvePoint,
    estimate_usage_curve,
    make_log_w_grid,
    solve_shadow_price_from_curve,
)
from run_experiment import provenance_fields

RESULTS = _ROOT / "results"
SEEDS = [42, 123, 456, 789, 1024]
ENVS = ["Tiger", "Diagnosis", "Bandit", "Tileworld-6x6", "Inspection-N8"]
EPISODES = {"Tileworld-6x6": 40, "Inspection-N8": 30}
GRID = {"Tileworld-6x6": 10, "Inspection-N8": 8}
DEFAULT_EPISODES = 100
DEFAULT_GRID = 16
N_BOOT = 2000
BOOT_SEED = 20260928
COVER = 0.90


def per_seed_curve(name: str) -> pd.DataFrame:
    cfg = get_benchmark(name)
    env = cfg.env_factory()
    ep = EPISODES.get(name, DEFAULT_EPISODES)
    w_grid = make_log_w_grid(0.0, 100.0, GRID.get(name, DEFAULT_GRID))
    rows = []
    for w in w_grid:
        (pt,) = estimate_usage_curve(
            env,
            w_grid=[float(w)],
            seeds=SEEDS,
            num_episodes=ep,
            planning_horizon=cfg.planning_horizon,
            usage_kind="count",
            family=cfg.family,
            tree_depth=cfg.tree_depth,
        )
        for seed, u in zip(SEEDS, pt.per_seed_means):
            rows.append({"env": name, "w": pt.w, "seed": seed, "usage": u})
        print(f"  {name} w={pt.w:.4g} U={pt.mean_usage:.4f}", flush=True)
    df = pd.DataFrame(rows)
    df["episodes_per_seed"] = ep
    return df


def check_reproduction(per_seed: pd.DataFrame) -> None:
    committed = pd.read_csv(RESULTS / "results_price_usage_curves.csv")
    fresh = per_seed.groupby(["env", "w"], sort=False)["usage"].mean().reset_index()
    for df in (committed, fresh):
        df["w_key"] = df["w"].map(lambda w: f"{w:.10g}")
    merged = committed.merge(fresh.drop(columns="w"), on=["env", "w_key"], how="outer", indicator=True)
    if (merged["_merge"] != "both").any():
        raise SystemExit(f"grid mismatch against committed curves:\n{merged[merged['_merge'] != 'both']}")
    diff = (merged["mean_usage"] - merged["usage"]).abs().max()
    if diff > 1e-9:
        raise SystemExit(f"per-seed curves do not reproduce committed means (max |diff| = {diff})")
    print(f"reproduction check passed, max |diff| = {diff:.3g}", flush=True)


def curve_from_matrix(ws: np.ndarray, mat: np.ndarray) -> list:
    means = mat.mean(axis=1)
    ses = mat.std(axis=1, ddof=1) / np.sqrt(mat.shape[1])
    return [
        UsageCurvePoint(w=float(w), mean_usage=float(m), se_usage=float(s),
                        n_seeds=mat.shape[1], per_seed_means=list(map(float, r)))
        for w, m, s, r in zip(ws, means, ses, mat)
    ]


def bracket_key(res) -> str:
    if not res.bracketed:
        return "none"
    return f"({res.w_lo:.6g}, {res.w_hi:.6g}]"


def stability(per_seed: pd.DataFrame) -> pd.DataFrame:
    prices = pd.read_csv(RESULTS / "results_price_shadow_curves.csv")
    rng = np.random.default_rng(BOOT_SEED)
    out = []
    counts_rows = []
    for name in ENVS:
        sub = per_seed[per_seed["env"] == name]
        mat_df = sub.pivot(index="w", columns="seed", values="usage")[SEEDS].sort_index()
        ws = mat_df.index.to_numpy(dtype=float)
        mat = mat_df.to_numpy(dtype=float)
        idx = rng.integers(0, len(SEEDS), size=(N_BOOT, len(SEEDS)))
        for _, row in prices[prices["env"] == name].iterrows():
            B = float(row["budget"])
            tol = max(0.3, 0.1 * B)
            point = solve_shadow_price_from_curve(curve_from_matrix(ws, mat), budget=B, tol=tol)
            reported = bracket_key(point)
            if bool(point.bracketed) != bool(row["bracketed"]) or point.bracketed and not (
                np.isclose(point.w_lo, row["w_lo"]) and np.isclose(point.w_hi, row["w_hi"])
            ):
                raise SystemExit(f"{name} B={B}: recomputed bracket {reported} differs from committed row")
            keys = [
                bracket_key(solve_shadow_price_from_curve(curve_from_matrix(ws, mat[:, b]), budget=B, tol=tol))
                for b in idx
            ]
            counts = pd.Series(keys).value_counts()
            counts_rows.extend(
                {"env": name, "budget": B, "bracket": k, "count": int(c), "n_boot": N_BOOT}
                for k, c in counts.items()
            )
            freqs = counts / N_BOOT
            cum = freqs.cumsum()
            cover_set = list(freqs.index[: int(np.searchsorted(cum.to_numpy(), COVER) + 1)])
            out.append({
                "env": name,
                "budget": B,
                "reported_bracket": reported,
                "frac_reported": float(freqs.get(reported, 0.0)),
                "frac_bracketed": float(1.0 - freqs.get("none", 0.0)),
                "n_distinct": int(len(counts)),
                "modal_bracket": counts.index[0],
                "frac_modal": float(freqs.iloc[0]),
                "cover90_set": " | ".join(cover_set),
                "cover90_size": len(cover_set),
                "n_boot": N_BOOT,
                "boot_seed": BOOT_SEED,
            })
            print(f"  {name} B={B:.3f} reported={reported} agree={freqs.get(reported, 0.0):.3f} "
                  f"distinct={len(counts)} cover90={len(cover_set)}", flush=True)
    return pd.DataFrame(out), pd.DataFrame(counts_rows)


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    p.add_argument("--from-per-seed", action="store_true",
                   help="skip episode reruns and bootstrap the committed per-seed CSV")
    args = p.parse_args()
    RESULTS.mkdir(exist_ok=True)
    per_seed_path = RESULTS / "results_price_usage_curves_per_seed.csv"
    if args.from_per_seed:
        per_seed = pd.read_csv(per_seed_path)
    else:
        frames = []
        for name in ENVS:
            print(f"=== {name} ===", flush=True)
            frames.append(per_seed_curve(name))
            pd.concat(frames).to_csv(per_seed_path, index=False)
        per_seed = pd.concat(frames, ignore_index=True)
        prov = provenance_fields(SEEDS, DEFAULT_EPISODES)
        for k in ("git_sha", "generated_utc"):
            per_seed[k] = prov[k]
        per_seed.to_csv(per_seed_path, index=False)
    check_reproduction(per_seed)
    df, counts = stability(per_seed)
    df.to_csv(RESULTS / "results_price_bracket_stability.csv", index=False)
    counts.to_csv(RESULTS / "results_price_bracket_stability_counts.csv", index=False)
    print(df.to_string(index=False))


if __name__ == "__main__":
    main()
