"""Select each solver's exploration constant on the disjoint tuning seeds and
evaluate the frozen selection on the canonical seeds.

Selection protocol (2026-09-17, ledger 9.17.45), replacing a comparison in
which each solver's best constant had been picked on the same five seeds the
significance test then reported. The rule below was written down in this file
before the selection was run. The canonical five-seed sweep it is read off had
already been run and inspected, so what the protocol removes is selection on
the reported seeds, not the authors' prior sight of them.

Selection (Stage 1): from results_pomcp_exploration_tuning.csv, run on tuning
seeds {11, 22, 33} disjoint from every evaluation seed, pick per environment
and per solver the configuration with the highest success rate, ties broken by
higher mean reward. POMCP's candidates are every swept constant and both
rollout policies. MCTS-EFE's candidates are its two swept constants.

Evaluation (Stage 2): read the selected configurations' rows from the
canonical-seed sweep, results_pomcp_exploration_sweep.csv (five seeds, 200
episodes each, fixed before any selection was made), and compare MCTS-EFE to
POMCP with a seed-level Welch t-test computed from each arm's seed-level mean
and standard error. Primary metric: success. Comparison family: success and
reward on all three environments, six tests, Holm-Bonferroni at alpha 0.05.

Writes results_pomcp_exploration_selected.csv, one row per environment and
metric, which is the producer of the corresponding manuscript sentences.
"""
from __future__ import annotations

import sys
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import stats

_ROOT = Path(__file__).resolve().parents[1]
RESULTS = _ROOT / "results"
TUNING = RESULTS / "results_pomcp_exploration_tuning.csv"
CANON = RESULTS / "results_pomcp_exploration_sweep.csv"
OUT = RESULTS / "results_pomcp_exploration_selected.csv"
ALPHA = 0.05


def select(tun: pd.DataFrame) -> dict:
    picks = {}
    for env, g in tun.groupby("env"):
        for agent, h in g.groupby("agent"):
            h = h.sort_values(["success", "reward"], ascending=[False, False])
            picks[(env, agent)] = str(h.iloc[0]["label"])
    return picks


def welch_from_aggregates(m_a, se_a, n_a, m_b, se_b, n_b):
    va, vb = se_a ** 2, se_b ** 2
    t = (m_a - m_b) / np.sqrt(va + vb)
    df = (va + vb) ** 2 / (va ** 2 / (n_a - 1) + vb ** 2 / (n_b - 1))
    p = 2.0 * stats.t.sf(abs(t), df)
    return float(t), float(df), float(p)


def holm(pvals):
    order = np.argsort(pvals)
    m = len(pvals)
    sig = [False] * m
    for rank, idx in enumerate(order):
        if pvals[idx] <= ALPHA / (m - rank):
            sig[idx] = True
        else:
            break
    return sig


def main():
    tun, canon = pd.read_csv(TUNING), pd.read_csv(CANON)
    picks = select(tun)
    rows = []
    for env in sorted(canon["env"].unique()):
        a = canon[(canon.env == env) & (canon.label == picks[(env, "MCTS-EFE")])].iloc[0]
        b = canon[(canon.env == env) & (canon.label == picks[(env, "POMCP")])].iloc[0]
        for metric in ("success", "reward"):
            se_col = f"se_{metric}_seed_level"
            t, df, p = welch_from_aggregates(a[metric], a[se_col], a["n_seeds"], b[metric], b[se_col], b["n_seeds"])
            rows.append(dict(env=env, metric=metric, label_efe=a["label"], label_pomcp=b["label"],
                             tuning_success_efe=float(tun[(tun.env == env) & (tun.label == a["label"])]["success"].iloc[0]),
                             tuning_success_pomcp=float(tun[(tun.env == env) & (tun.label == b["label"])]["success"].iloc[0]),
                             mean_efe=float(a[metric]), se_efe=float(a[se_col]), mean_pomcp=float(b[metric]), se_pomcp=float(b[se_col]),
                             diff=float(a[metric] - b[metric]), t_stat=t, df=df, p_seed_level=p, n_seeds=int(a["n_seeds"])))
    df = pd.DataFrame(rows)
    df["significant_hb_seed_level"] = holm(df["p_seed_level"].tolist())
    df["family_size"] = len(df)
    df["tuning_seeds"] = "11|22|33"
    df["selection_rule"] = "max success on tuning seeds, ties by reward"
    df.to_csv(OUT, index=False)
    print(df[["env", "metric", "label_efe", "label_pomcp", "mean_efe", "mean_pomcp", "diff", "p_seed_level", "significant_hb_seed_level"]].to_string(index=False))
    print(f"\nSaved {OUT}")


if __name__ == "__main__":
    main()
