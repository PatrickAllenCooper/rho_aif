#!/usr/bin/env python3
"""
w* atlas (Stage G of the full-paper plan): per-instance descriptive table of
the usage curve, the implicit EFE budget B_EFE = U(w=1), and crossing brackets
at two canonical budgets.

Reuses saved full-battery curves (results_price_usage_curves.csv and
results_price_interleaved_curves.csv). B_EFE comes from the saved implicit-
budget protocol for the OTC/inspection battery and is measured fresh at w=1
for the interleaved instances (not on their log grid).

Purely descriptive: no meta-model w*(R, gamma, |S|, H) is fit or claimed.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Dict, List

import numpy as np
import pandas as pd

_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT))
sys.path.insert(0, str(_ROOT / "experiments"))

from rho_aif.budget import (
    UsageCurvePoint,
    estimate_usage_curve,
    identifiable_budgets,
    solve_shadow_price_from_curve,
)

RESULTS = _ROOT / "results"
TABLES = _ROOT / "paper" / "tables"

CURVE_SOURCES = [
    RESULTS / "results_price_usage_curves.csv",
    RESULTS / "results_price_interleaved_curves.csv",
]
INTERLEAVED = ["RS[5,3]", "RS[7,4]", "Inspection-N16"]


def load_curves() -> Dict[str, List[UsageCurvePoint]]:
    curves: Dict[str, List[UsageCurvePoint]] = {}
    for path in CURVE_SOURCES:
        if not path.exists():
            raise SystemExit(f"Missing {path}; run the full battery first")
        df = pd.read_csv(path)
        for env, sub in df.groupby("env"):
            pts = [
                UsageCurvePoint(
                    w=float(r["w"]),
                    mean_usage=float(r["mean_usage"]),
                    se_usage=float(r["se_usage"]),
                    n_seeds=int(r["n_seeds"]),
                    per_seed_means=[],
                )
                for _, r in sub.sort_values("w").iterrows()
            ]
            curves[env] = pts
    return curves


def implicit_budgets(seeds, episodes_by_env) -> Dict[str, dict]:
    """B_EFE = U(w=1) with SE for every instance."""
    out: Dict[str, dict] = {}
    saved = RESULTS / "results_price_efe_implicit_budget.csv"
    if saved.exists():
        df = pd.read_csv(saved)
        for _, r in df.iterrows():
            out[str(r["env"])] = {
                "b_efe": float(r["implicit_budget"]),
                "b_efe_se": float(r["se"]),
            }
    # Fresh measurement for interleaved instances (w=1 is not on their grid).
    from run_price_of_information import _interleaved_configs

    configs = _interleaved_configs()
    for name in INTERLEAVED:
        if name in out:
            continue
        cfg = configs[name]
        ep = int(episodes_by_env.get(name, 50))
        print(f"  measuring B_EFE for {name} (ep={ep}) ...", flush=True)
        pts = estimate_usage_curve(
            cfg["env"],
            w_grid=[1.0],
            seeds=seeds,
            num_episodes=ep,
            planning_horizon=cfg["planning_horizon"],
            family=cfg["family"],
            tree_depth=cfg["tree_depth"],
            max_steps=cfg["max_steps"],
        )
        out[name] = {"b_efe": pts[0].mean_usage, "b_efe_se": pts[0].se_usage}
    return out


def fmt_bracket(res) -> str:
    if not res.bracketed:
        return "--"
    return f"({res.w_lo:.3g}, {res.w_hi:.3g}]"


def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--seeds", type=int, nargs="*", default=[42, 123, 456, 789, 1024])
    args = p.parse_args()

    curves = load_curves()
    befe = implicit_budgets(args.seeds, {"RS[7,4]": 30})

    rows = []
    for env in sorted(curves.keys()):
        curve = curves[env]
        u_floor = min(p.mean_usage for p in curve)
        u_max = max(p.mean_usage for p in curve)
        budgets = identifiable_budgets(curve, n_budgets=2, margin=0.15)
        solved = [
            solve_shadow_price_from_curve(curve, budget=float(B), tol=max(0.3, 0.1 * float(B)))
            for B in budgets
        ]
        row = {
            "env": env,
            "u_floor": u_floor,
            "u_max": u_max,
            "b_efe": befe.get(env, {}).get("b_efe", float("nan")),
            "b_efe_se": befe.get(env, {}).get("b_efe_se", float("nan")),
        }
        for i, (B, res) in enumerate(zip(budgets, solved), start=1):
            row[f"budget{i}"] = float(B)
            row[f"w_lo{i}"] = res.w_lo
            row[f"w_hi{i}"] = res.w_hi
            row[f"bracketed{i}"] = res.bracketed
        rows.append(row)
        print(
            f"  {env:16s} U in [{u_floor:.2f}, {u_max:.2f}]  "
            f"B_EFE={row['b_efe']:.2f}±{row['b_efe_se']:.2f}  "
            + "  ".join(
                f"B{i}={row[f'budget{i}']:.2f} w in ({row[f'w_lo{i}']:.3g}, {row[f'w_hi{i}']:.3g}]"
                for i in range(1, len(budgets) + 1)
            ),
            flush=True,
        )

    df = pd.DataFrame(rows)
    out_csv = RESULTS / "results_w_atlas.csv"
    df.to_csv(out_csv, index=False)
    print(f"Saved {out_csv}")

    # LaTeX appendix table (descriptive only).
    TABLES.mkdir(parents=True, exist_ok=True)
    lines = [
        "% Auto-generated by experiments/run_w_atlas.py -- do not edit by hand.",
        "\\begin{table}[t]",
        "\\centering",
        "\\caption{Atlas of operational sensing budgets across benchmark instances:",
        " usage range of the Planning+IG family, implicit EFE budget",
        " $B_{\\mathrm{EFE}} = U(w{=}1)$ (mean $\\pm$ SE over seeds), and crossing",
        " brackets $w^*(B)$ at two canonical budgets per instance. Brackets are",
        " set-valued (Definition PI-3); no closed-form meta-model is implied.}",
        "\\label{tab:w-atlas}",
        "\\small",
        "\\begin{tabular}{lcccc}",
        "\\toprule",
        "Instance & $[U_{\\min}, U_{\\max}]$ & $B_{\\mathrm{EFE}}$ & "
        "$B_1$: $w^*$ bracket & $B_2$: $w^*$ bracket \\\\",
        "\\midrule",
    ]
    for _, r in df.iterrows():
        b1 = (
            f"{r['budget1']:.1f}: $({r['w_lo1']:.3g}, {r['w_hi1']:.3g}]$"
            if r.get("bracketed1", False)
            else "--"
        )
        b2 = (
            f"{r['budget2']:.1f}: $({r['w_lo2']:.3g}, {r['w_hi2']:.3g}]$"
            if r.get("bracketed2", False)
            else "--"
        )
        env_tex = str(r["env"]).replace("[", "{[}").replace("]", "{]}")
        lines.append(
            f"{env_tex} & $[{r['u_floor']:.2f}, {r['u_max']:.2f}]$ & "
            f"${r['b_efe']:.2f} \\pm {r['b_efe_se']:.2f}$ & {b1} & {b2} \\\\"
        )
    lines += ["\\bottomrule", "\\end{tabular}", "\\end{table}", ""]
    out_tex = TABLES / "w_atlas.tex"
    out_tex.write_text("\n".join(lines))
    print(f"Saved {out_tex}")


if __name__ == "__main__":
    main()
