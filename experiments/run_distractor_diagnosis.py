#!/usr/bin/env python3
"""
Stage G2: distractor robustness (reward-irrelevant sensing).

Reviewer 8Evk's question: how poorly do these methods work in settings with
uncertainty over state components that happen to be unimportant? DiagnosisEnv
has no such component, so no existing experiment answers this. This script
sweeps the information-gain weight w on DistractorDiagnosisEnv (Guidance
Documents/full_paper_plan.md, Stage G2) and measures, per episode: reward,
total sensing usage, task-relevant test count, distractor test count, and
the distractor fraction of usage.

IDS (rho_aif.agents.ids.IDSAgent) is included: it consumes the same
observation-model / commit-reward-matrix interface as every other
observe-then-commit agent here, unmodified, so no special-casing was needed
to add it as a reward-aware contrast.

See Guidance_Documents/price_of_information.md for the Stage G2 writeup.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path
from typing import Dict, List, Sequence

_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT))

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from rho_aif.agents.efe import EFEAgent
from rho_aif.agents.ids import IDSAgent
from rho_aif.agents.planning import PlanningAgent
from rho_aif.agents.planning_infogain import PlanningInfoGainAgent
from rho_aif.benchmark import get_obs_models, make_env_config
from rho_aif.budget import make_log_w_grid
from rho_aif.environments.distractor_diagnosis import DistractorDiagnosisEnv

RESULTS = _ROOT / "results"
FIGURES = _ROOT / "figures"
SEEDS = [42, 123, 456, 789, 1024]


def make_distractor_diagnosis() -> DistractorDiagnosisEnv:
    """4-condition diagnosis + 1 reward-irrelevant binary nuisance factor."""
    return DistractorDiagnosisEnv(
        num_conditions=4,
        test_accuracy=0.80,
        test_cost=1.0,
        distractor_accuracy=0.80,
        distractor_cost=1.0,
        correct_reward=10.0,
        incorrect_penalty=-50.0,
    )


def run_distractor_episode(agent, env, max_steps: int = 200, seed=None) -> Dict[str, float]:
    """Like rho_aif.benchmark.run_otc_episode, plus a distractor-count split."""
    obs, info = env.reset(seed=seed)
    agent.reset()
    total_reward = 0.0
    task_tests = 0
    distractor_tests = 0

    for _ in range(max_steps):
        action = agent.select_action()
        obs, reward, terminated, truncated, info = env.step(action)
        total_reward += reward
        if terminated or truncated:
            n = task_tests + distractor_tests
            frac = distractor_tests / n if n > 0 else 0.0
            return {
                "total_reward": total_reward,
                "num_observations": n,
                "task_tests": task_tests,
                "distractor_tests": distractor_tests,
                "distractor_fraction": frac,
                "success": bool(info.get("correct", False)),
            }
        agent.update_belief(obs, obs_action=action)
        if info.get("is_distractor", False):
            distractor_tests += 1
        else:
            task_tests += 1

    n = task_tests + distractor_tests
    frac = distractor_tests / n if n > 0 else 0.0
    return {
        "total_reward": total_reward,
        "num_observations": n,
        "task_tests": task_tests,
        "distractor_tests": distractor_tests,
        "distractor_fraction": frac,
        "success": False,
    }


def _seed_level_stats(results_by_seed: Dict[int, List[dict]], key: str):
    """Per-seed means of `key`, then SE across those seed means (n=len(seeds)).
    Complements the pooled episode-level SE, which understates uncertainty
    since episodes within a seed share an agent instance / RNG stream."""
    seed_means = np.array([
        float(np.mean([r[key] for r in seed_results]))
        for seed_results in results_by_seed.values()
    ])
    n_seeds = len(seed_means)
    se = float(np.std(seed_means, ddof=1) / np.sqrt(n_seeds)) if n_seeds > 1 else float("nan")
    return float(np.mean(seed_means)), se, n_seeds


VARIANTS = (
    ("Planning+IG", False),
    ("Planning+IG (reward-relevant)", True),
)


def _run_cell(obs_models, config, env, planning_horizon, w, reward_relevant,
              seeds, num_episodes):
    """Run one (weight, variant) cell and return (row_fields, results_by_seed)."""
    results = []
    results_by_seed: Dict[int, List[dict]] = {}
    for seed in seeds:
        np.random.seed(int(seed))
        agent = PlanningInfoGainAgent(
            obs_models, config, planning_horizon=planning_horizon,
            info_gain_weight=w, reward_relevant_info=reward_relevant,
        )
        seed_results = []
        for _ep in range(num_episodes):
            r = run_distractor_episode(agent, env, seed=int(seed) * 10000 + _ep)
            r["seed"] = int(seed)
            seed_results.append(r)
        results_by_seed[int(seed)] = seed_results
        results.extend(seed_results)

    rewards = [r["total_reward"] for r in results]
    n_obs = [r["num_observations"] for r in results]
    task = [r["task_tests"] for r in results]
    dist = [r["distractor_tests"] for r in results]
    frac = [r["distractor_fraction"] for r in results]
    succ = [r["success"] for r in results]
    mean_frac_seed, se_frac_seed, n_seeds_ = _seed_level_stats(results_by_seed, "distractor_fraction")
    mean_reward_seed, se_reward_seed, _ = _seed_level_stats(results_by_seed, "total_reward")
    row = {
        "mean_reward": float(np.mean(rewards)),
        "se_reward": float(np.std(rewards) / np.sqrt(len(rewards))),
        "se_reward_seed_level": se_reward_seed,
        "mean_usage": float(np.mean(n_obs)),
        "se_usage": float(np.std(n_obs) / np.sqrt(len(n_obs))),
        "mean_task_tests": float(np.mean(task)),
        "mean_distractor_tests": float(np.mean(dist)),
        "mean_distractor_fraction": float(np.mean(frac)),
        "se_distractor_fraction": float(np.std(frac) / np.sqrt(len(frac))),
        "se_distractor_fraction_seed_level": se_frac_seed,
        "n_seeds": n_seeds_,
        "success_rate": float(np.mean(succ)),
        "reward_relevant": bool(reward_relevant),
        "episodes_per_seed": num_episodes,
        "seed_list": "|".join(str(s) for s in seeds),
    }
    return row, results


def _write_variant_stats(episodes_by_cell, w_grid,
                         out="results/results_distractor_diagnosis_stats.csv"):
    """Seed-level Welch tests between ordinary and reward-relevance-weighted
    Planning+IG at every swept weight, Holm-Bonferroni corrected over the
    family of (weight x metric) comparisons."""
    from rho_aif.stats import holm_bonferroni, seed_level_ttest

    metrics = [
        ("Reward", lambda r: r["total_reward"]),
        ("DistractorFraction", lambda r: r["distractor_fraction"]),
        ("DistractorTests", lambda r: r["distractor_tests"]),
        ("Usage", lambda r: r["num_observations"]),
        ("Success", lambda r: float(r["success"])),
    ]
    rows = []
    for w in w_grid:
        a = episodes_by_cell.get((float(w), False))
        b = episodes_by_cell.get((float(w), True))
        if a is None or b is None:
            continue
        for name, extract in metrics:
            out_t = seed_level_ttest(a, b, extract)
            rows.append({
                "w": float(w),
                "metric": name,
                "agent_a": "Planning+IG",
                "agent_b": "Planning+IG (reward-relevant)",
                "mean_a": float(np.mean([extract(r) for r in a])),
                "mean_b": float(np.mean([extract(r) for r in b])),
                "diff": float(np.mean([extract(r) for r in a]) - np.mean([extract(r) for r in b])),
                "n_seeds": out_t["n_seeds_a"],
                "p_seed_level": out_t["p_value"],
            })
    if not rows:
        return
    for r, sig in zip(rows, holm_bonferroni([r["p_seed_level"] for r in rows])):
        r["significant_hb_seed_level"] = sig
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    pd.DataFrame(rows).to_csv(out, index=False)
    print(f"Paired variant statistics saved to {out}", flush=True)


def run_sweep(
    seeds: Sequence[int] = SEEDS,
    num_episodes: int = 100,
    n_grid: int = 12,
    planning_horizon: int = 3,
) -> pd.DataFrame:
    env = make_distractor_diagnosis()
    obs_models = get_obs_models(env)
    config = make_env_config(env)

    # w = 5 is the weight the manuscript quotes for the tuned Planning+IG
    # comparison, so it is added explicitly rather than left between grid
    # points, and both variants are run there.
    w_grid = sorted(set(list(make_log_w_grid(0.0, 100.0, n_grid)) + [5.0]))
    rows: List[dict] = []
    episodes_by_cell: Dict[tuple, List[dict]] = {}

    print(
        f"\n=== Stage G2: distractor robustness on {type(env).__name__} "
        f"(4 conditions x 2-valued nuisance, {env.num_tests} tests) ===",
        flush=True,
    )
    print(
        "Both the ordinary and the reward-relevance-weighted Planning+IG are "
        "swept over the same weight grid, so the fix is reported as a paired "
        "curve rather than at a single weight.",
        flush=True,
    )

    for i, w in enumerate(w_grid):
        w = float(w)
        for label, relevant in VARIANTS:
            row, results = _run_cell(
                obs_models, config, env, planning_horizon, w, relevant,
                seeds, num_episodes,
            )
            row["agent"] = label
            row["w"] = w
            rows.append(row)
            episodes_by_cell[(w, relevant)] = results
            print(
                f"  [{i+1}/{len(w_grid)}] w={w:.4g} {'relevance-weighted' if relevant else 'ordinary':>18s}: "
                f"usage={row['mean_usage']:.2f} "
                f"(task={row['mean_task_tests']:.2f}, distractor={row['mean_distractor_tests']:.2f}, "
                f"frac={row['mean_distractor_fraction']:.3f}) reward={row['mean_reward']:+.2f} "
                f"success={row['success_rate']:.3f}",
                flush=True,
            )

    _write_variant_stats(episodes_by_cell, w_grid)

    # Fixed reference agents at the grid endpoints for context: reward-only
    # Planning (w=0, already in the grid), EFE (w=1, information-unit weight
    # under bits), and IDS as a reward-aware contrast that explicitly
    # discounts information about the optimal commit.
    #
    # Two further references close the loop on the manuscript's proposed fix.
    # "EFE (w=1, reward-relevant)" and "Plan+IG (w=5, reward-relevant)" score
    # information gain on the marginal over reward-equivalence classes of
    # hidden states rather than on the full state belief, which is derived
    # from the commit reward matrix alone (rho_aif.scoring). Belief dynamics
    # are unchanged: the continuation always propagates the full joint
    # posterior, and only the epistemic scoring term differs.
    for label, make_agent in (
        ("EFE (w=1)", lambda: EFEAgent(obs_models, config, planning_horizon=planning_horizon)),
        ("EFE (w=1, reward-relevant)",
         lambda: EFEAgent(obs_models, config, planning_horizon=planning_horizon,
                          reward_relevant_info=True)),
        ("Plan+IG (w=5)",
         lambda: PlanningInfoGainAgent(obs_models, config, planning_horizon=planning_horizon,
                                       info_gain_weight=5.0)),
        ("Plan+IG (w=5, reward-relevant)",
         lambda: PlanningInfoGainAgent(obs_models, config, planning_horizon=planning_horizon,
                                       info_gain_weight=5.0, reward_relevant_info=True)),
        ("IDS", lambda: IDSAgent(obs_models, config)),
    ):
        results = []
        results_by_seed: Dict[int, List[dict]] = {}
        for seed in seeds:
            np.random.seed(int(seed))
            agent = make_agent()
            seed_results = []
            for _ep in range(num_episodes):
                seed_results.append(run_distractor_episode(agent, env, seed=int(seed) * 10000 + _ep))
            results_by_seed[int(seed)] = seed_results
            results.extend(seed_results)
        rewards = [r["total_reward"] for r in results]
        n_obs = [r["num_observations"] for r in results]
        task = [r["task_tests"] for r in results]
        dist = [r["distractor_tests"] for r in results]
        frac = [r["distractor_fraction"] for r in results]
        succ = [r["success"] for r in results]
        mean_frac_seed, se_frac_seed, n_seeds_ = _seed_level_stats(results_by_seed, "distractor_fraction")
        mean_reward_seed, se_reward_seed, _ = _seed_level_stats(results_by_seed, "total_reward")
        row = {
            "agent": label,
            "w": float("nan"),
            "mean_reward": float(np.mean(rewards)),
            "se_reward": float(np.std(rewards) / np.sqrt(len(rewards))),
            "se_reward_seed_level": se_reward_seed,
            "mean_usage": float(np.mean(n_obs)),
            "se_usage": float(np.std(n_obs) / np.sqrt(len(n_obs))),
            "mean_task_tests": float(np.mean(task)),
            "mean_distractor_tests": float(np.mean(dist)),
            "mean_distractor_fraction": float(np.mean(frac)),
            "se_distractor_fraction": float(np.std(frac) / np.sqrt(len(frac))),
            "se_distractor_fraction_seed_level": se_frac_seed,
            "n_seeds": n_seeds_,
            "success_rate": float(np.mean(succ)),
        }
        rows.append(row)
        print(
            f"  [{label}] usage={row['mean_usage']:.2f} "
            f"(task={row['mean_task_tests']:.2f}, distractor={row['mean_distractor_tests']:.2f}, "
            f"frac={row['mean_distractor_fraction']:.3f}) reward={row['mean_reward']:+.2f} "
            f"success={row['success_rate']:.3f}",
            flush=True,
        )

    df = pd.DataFrame(rows)
    RESULTS.mkdir(exist_ok=True)
    df.to_csv(RESULTS / "results_distractor_diagnosis.csv", index=False)
    print(f"\nSaved {RESULTS / 'results_distractor_diagnosis.csv'}")
    return df


def plot_composition(df: pd.DataFrame, path: Path) -> None:
    """Left: usage composition of ordinary Planning+IG as w grows.
    Right: distractor fraction for ordinary and reward-relevance-weighted
    Planning+IG on the same weight grid, which is the paired evidence that
    the relevance weighting removes reward-irrelevant sensing entirely."""
    plain = df[(df["w"].notna()) & (df["agent"] == "Planning+IG")].sort_values("w")
    relevant = df[
        (df["w"].notna()) & (df["agent"] == "Planning+IG (reward-relevant)")
    ].sort_values("w")

    fig, axes = plt.subplots(1, 2, figsize=(10.5, 4.2))
    ax = axes[0]
    ax.bar(range(len(plain)), plain["mean_task_tests"],
           label="task-relevant tests", color="C0")
    ax.bar(range(len(plain)), plain["mean_distractor_tests"],
           bottom=plain["mean_task_tests"], label="distractor test", color="C3")
    ax.set_xticks(range(len(plain)))
    ax.set_xticklabels([f"{w:.3g}" for w in plain["w"]], rotation=45, fontsize=7)
    ax.set_xlabel("Info-gain weight w")
    ax.set_ylabel("Mean tests per episode")
    ax.set_title("Ordinary information gain: usage composition")
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3, axis="y")

    ax2 = axes[1]
    ax2.errorbar(plain["w"], plain["mean_distractor_fraction"],
                 yerr=plain["se_distractor_fraction_seed_level"],
                 marker="o", ms=4, capsize=3, color="C3",
                 label="ordinary information gain")
    if not relevant.empty:
        ax2.errorbar(relevant["w"], relevant["mean_distractor_fraction"],
                     yerr=relevant["se_distractor_fraction_seed_level"],
                     marker="s", ms=4, capsize=3, color="C2",
                     label="reward-relevance weighted")
    ax2.set_xscale("symlog", linthresh=0.1)
    ax2.set_xlabel("Info-gain weight w")
    ax2.set_ylabel("Distractor fraction of usage")
    ax2.set_title("Relevance weighting removes distractor spend")
    ax2.legend(fontsize=8)
    ax2.grid(True, alpha=0.3)
    ax2.set_ylim(-0.02, max(0.3, float(plain["mean_distractor_fraction"].max()) * 1.2))

    fig.tight_layout()
    FIGURES.mkdir(exist_ok=True)
    fig.savefig(path.with_suffix(".png"), dpi=150)
    fig.savefig(path.with_suffix(".pdf"))
    plt.close(fig)
    print(f"Saved {path.with_suffix('.png')} and {path.with_suffix('.pdf')}")


def main() -> None:
    df = run_sweep()
    plot_composition(df, FIGURES / "distractor_composition")

    def _frac(agent, w=None):
        sel = df[df["agent"] == agent]
        if w is not None:
            sel = sel[np.isclose(sel["w"], w)]
        return float(sel["mean_distractor_fraction"].iloc[0]) if not sel.empty else float("nan")

    print("\n=== Summary ===")
    print(f"Planning (w=0): distractor fraction {_frac('Planning+IG', 0.0):.3f}")
    print(f"EFE (w=1): distractor fraction {_frac('EFE (w=1)'):.3f}")
    print(f"IDS: distractor fraction {_frac('IDS'):.3f}")

    plain = df[(df["agent"] == "Planning+IG") & (df["w"] > 10)]
    rel = df[(df["agent"] == "Planning+IG (reward-relevant)") & (df["w"] > 10)]
    if not plain.empty:
        print(f"Ordinary Planning+IG at large w (w>10): distractor fraction up to "
              f"{plain['mean_distractor_fraction'].max():.3f}")
    if not rel.empty:
        print(f"Reward-relevance weighted at large w (w>10): distractor fraction up to "
              f"{rel['mean_distractor_fraction'].max():.3f}")
        merged = plain.merge(rel, on="w", suffixes=("_plain", "_rel"))
        for _, r in merged.iterrows():
            print(f"  w={r['w']:.4g}: reward {r['mean_reward_plain']:+.2f} -> "
                  f"{r['mean_reward_rel']:+.2f}, distractor tests "
                  f"{r['mean_distractor_tests_plain']:.2f} -> {r['mean_distractor_tests_rel']:.2f}")


if __name__ == "__main__":
    main()
