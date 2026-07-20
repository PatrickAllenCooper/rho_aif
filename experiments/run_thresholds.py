#!/usr/bin/env python3
"""
Compute Proposition 2 observation thresholds from environment parameters.

Uses the published formula (nats and bits) so Table alpha_eta is reproducible:

    w*_thresh = [c - (p - 1/2)(R+ - R-)] / I_max

where I_max = H(1/2) - H(p) for a binary observation under a uniform prior.

Also computes the H=2 over-observation upper threshold: the weight above which
a second observation is preferred at the post-first-observation belief even
when its instrumental value of information is below cost.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT))

import numpy as np
import pandas as pd
from scipy.stats import entropy as scipy_entropy


ENV_PARAMS = {
    "Testbed": {
        "p": 0.75,
        "c": 0.1,
        "R_plus": 1.0,
        "R_minus": -1.0,
        "w_ret": 0.5,
    },
    "Tiger": {
        "p": 0.85,
        "c": 1.0,
        "R_plus": 10.0,
        "R_minus": -100.0,
        "w_ret": 1.0,
    },
    "Diagnosis": {
        "p": 0.80,
        "c": 1.0,
        "R_plus": 10.0,
        "R_minus": -50.0,
        "w_ret": 0.5,
        "note": "Two-state reduction of Diagnosis (N=2 equivalent accuracy/cost)",
    },
    "Tileworld": {
        "p": 0.80,
        "c": 1.0,
        "R_plus": 10.0,
        "R_minus": -50.0,
        "w_ret": 0.5,
        "note": "Two-state reduction matching Diagnosis reward scale",
    },
}


def binary_entropy(p: float, base: float) -> float:
    p = float(np.clip(p, 1e-12, 1.0 - 1e-12))
    return float(scipy_entropy([p, 1.0 - p], base=base))


def i_max(p: float, base: float) -> float:
    """Expected information gain from one binary observation at uniform prior."""
    return binary_entropy(0.5, base) - binary_entropy(p, base)


def w_thresh_lower(p: float, c: float, R_plus: float, R_minus: float, base: float) -> float:
    """
    Minimum weight at which observing once beats immediate commit (H=1).

    Negative values mean any nonnegative weight (including w=1) induces observation.
    """
    I = i_max(p, base)
    if I <= 0:
        return float("inf")
    num = c - (p - 0.5) * (R_plus - R_minus)
    return float(num / I)


def posterior_after_correct_obs(p: float) -> float:
    """Posterior mass on the true state after one correct-leaning observation."""
    # Uniform prior, likelihood p for matching obs: posterior = p / (p + (1-p)) = p
    return p


def instrumental_voi_second_obs(p: float, R_plus: float, R_minus: float) -> float:
    """
    Instrumental value of a second observation at belief (p, 1-p).

    Commit-now value: p R+ + (1-p) R-.
    After a second obs with accuracy p, expected commit value is computed by
    enumerating the two observation outcomes.
    """
    b = np.array([p, 1.0 - p])
    commit_now = p * R_plus + (1.0 - p) * R_minus

    # Observation model: P(o|s). o=0 favors state 0.
    # P(o=0|s=0)=p, P(o=0|s=1)=1-p
    expected_commit_after = 0.0
    for o, lik in enumerate([np.array([p, 1.0 - p]), np.array([1.0 - p, p])]):
        p_o = float(np.dot(b, lik))
        if p_o < 1e-12:
            continue
        post = b * lik
        post = post / post.sum()
        # Best commit: commit to argmax posterior
        q = float(post.max())
        commit_after = q * R_plus + (1.0 - q) * R_minus
        expected_commit_after += p_o * commit_after

    return float(expected_commit_after - commit_now)


def i_at_belief(p_belief: float, p_acc: float, base: float) -> float:
    """Expected IG of one binary obs at belief (p_belief, 1-p_belief)."""
    b = np.array([p_belief, 1.0 - p_belief])
    H_prior = float(scipy_entropy(b, base=base))
    H_post = 0.0
    for lik in (np.array([p_acc, 1.0 - p_acc]), np.array([1.0 - p_acc, p_acc])):
        p_o = float(np.dot(b, lik))
        if p_o < 1e-12:
            continue
        post = b * lik
        post = post / post.sum()
        H_post += p_o * float(scipy_entropy(post, base=base))
    return H_prior - H_post


def w_thresh_upper(p: float, c: float, R_plus: float, R_minus: float, base: float) -> float:
    """
    Weight above which a second observation is preferred at the post-first-obs
    belief (over-observation relative to instrumental reward).

    If VoI >= c, even w=0 takes the second observation (upper = 0).
    If I=0, no finite weight helps.
    """
    voi = instrumental_voi_second_obs(p, R_plus, R_minus)
    I = i_at_belief(p, p, base)
    if I <= 1e-12:
        return float("inf")
    if voi >= c:
        return 0.0
    return float((c - voi) / I)


def compute_row(name: str, params: dict) -> dict:
    p, c = params["p"], params["c"]
    Rp, Rm = params["R_plus"], params["R_minus"]
    alpha = abs(Rm) / Rp

    row = {
        "environment": name,
        "p": p,
        "c": c,
        "R_plus": Rp,
        "R_minus": Rm,
        "alpha": alpha,
        "w_ret": params.get("w_ret"),
    }
    for unit, base in (("nats", np.e), ("bits", 2.0)):
        I = i_max(p, base)
        w_lo = w_thresh_lower(p, c, Rp, Rm, base)
        w_hi = w_thresh_upper(p, c, Rp, Rm, base)
        row[f"I_max_{unit}"] = I
        row[f"eta_{unit}"] = I / c if c > 0 else float("inf")
        row[f"w_thresh_lower_{unit}"] = w_lo
        row[f"w_thresh_upper_{unit}"] = w_hi
        row[f"w1_in_interval_{unit}"] = bool(w_lo < 1.0 < w_hi) if np.isfinite(w_hi) else (w_lo < 1.0)
        row[f"w1_sufficient_{unit}"] = w_lo < 1.0
    return row


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("results/results_thresholds.csv"),
    )
    parser.add_argument(
        "--json-output",
        type=Path,
        default=Path("results/results_thresholds.json"),
    )
    args = parser.parse_args()

    rows = [compute_row(name, params) for name, params in ENV_PARAMS.items()]
    df = pd.DataFrame(rows)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(args.output, index=False)
    args.json_output.write_text(json.dumps(rows, indent=2))

    print("Proposition 2 thresholds (nats; matches paper formula with ln 2):")
    print(
        f"{'Env':12s} {'alpha':>7s} {'eta':>7s} {'w_lo':>10s} {'w_hi':>10s} "
        f"{'w=1 ok':>8s} {'w_ret':>6s}"
    )
    for r in rows:
        print(
            f"{r['environment']:12s} {r['alpha']:7.2f} {r['eta_nats']:7.3f} "
            f"{r['w_thresh_lower_nats']:10.2f} {r['w_thresh_upper_nats']:10.2f} "
            f"{str(r['w1_sufficient_nats']):>8s} {r['w_ret']:6.1f}"
        )
    print(f"\nWrote {args.output}")
    print(
        "Note: prior table values (Tiger -5.04, Diagnosis -2.34) do not match "
        "the stated formula; corrected values are ~-138.7 and ~-88.2 in nats."
    )


if __name__ == "__main__":
    main()
