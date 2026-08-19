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


def run_sweep(
    seeds: Sequence[int] = SEEDS,
    num_episodes: int = 100,
    n_grid: int = 12,
    planning_horizon: int = 3,
) -> pd.DataFrame:
    env = make_distractor_diagnosis()
    obs_models = get_obs_models(env)
    config = make_env_config(env)

    w_grid = make_log_w_grid(0.0, 100.0, n_grid)
    rows: List[dict] = []

    print(
        f"\n=== Stage G2: distractor robustness on {type(env).__name__} "
        f"(4 conditions x 2-valued nuisance, {env.num_tests} tests) ===",
        flush=True,
    )

    for i, w in enumerate(w_grid):
        w = float(w)
        results = []
        for seed in seeds:
            np.random.seed(int(seed))
            agent = PlanningInfoGainAgent(
                obs_models, config, planning_horizon=planning_horizon, info_gain_weight=w
            )
            for _ep in range(num_episodes):
                results.append(run_distractor_episode(agent, env, seed=int(seed) * 10000 + _ep))
        rewards = [r["total_reward"] for r in results]
        n_obs = [r["num_observations"] for r in results]
        task = [r["task_tests"] for r in results]
        dist = [r["distractor_tests"] for r in results]
        frac = [r["distractor_fraction"] for r in results]
        succ = [r["success"] for r in results]
        row = {
            "agent": "Planning+IG",
            "w": w,
            "mean_reward": float(np.mean(rewards)),
            "se_reward": float(np.std(rewards) / np.sqrt(len(rewards))),
            "mean_usage": float(np.mean(n_obs)),
            "se_usage": float(np.std(n_obs) / np.sqrt(len(n_obs))),
            "mean_task_tests": float(np.mean(task)),
            "mean_distractor_tests": float(np.mean(dist)),
            "mean_distractor_fraction": float(np.mean(frac)),
            "se_distractor_fraction": float(np.std(frac) / np.sqrt(len(frac))),
            "success_rate": float(np.mean(succ)),
        }
        rows.append(row)
        print(
            f"  [{i+1}/{len(w_grid)}] w={w:.4g}: usage={row['mean_usage']:.2f} "
            f"(task={row['mean_task_tests']:.2f}, distractor={row['mean_distractor_tests']:.2f}, "
            f"frac={row['mean_distractor_fraction']:.3f}) reward={row['mean_reward']:+.2f} "
            f"success={row['success_rate']:.3f}",
            flush=True,
        )

    # Fixed reference agents at the grid endpoints for context: reward-only
    # Planning (w=0, already in the grid), EFE (w=1, information-unit weight
    # under bits), and IDS as a reward-aware contrast that explicitly
    # discounts information about the optimal commit.
    for label, make_agent in (
        ("EFE (w=1)", lambda: EFEAgent(obs_models, config, planning_horizon=planning_horizon)),
        ("IDS", lambda: IDSAgent(obs_models, config)),
    ):
        results = []
        for seed in seeds:
            np.random.seed(int(seed))
            agent = make_agent()
            for _ep in range(num_episodes):
                results.append(run_distractor_episode(agent, env, seed=int(seed) * 10000 + _ep))
        rewards = [r["total_reward"] for r in results]
        n_obs = [r["num_observations"] for r in results]
        task = [r["task_tests"] for r in results]
        dist = [r["distractor_tests"] for r in results]
        frac = [r["distractor_fraction"] for r in results]
        succ = [r["success"] for r in results]
        row = {
            "agent": label,
            "w": float("nan"),
            "mean_reward": float(np.mean(rewards)),
            "se_reward": float(np.std(rewards) / np.sqrt(len(rewards))),
            "mean_usage": float(np.mean(n_obs)),
            "se_usage": float(np.std(n_obs) / np.sqrt(len(n_obs))),
            "mean_task_tests": float(np.mean(task)),
            "mean_distractor_tests": float(np.mean(dist)),
            "mean_distractor_fraction": float(np.mean(frac)),
            "se_distractor_fraction": float(np.std(frac) / np.sqrt(len(frac))),
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
    """Stacked usage figure: task tests vs. distractor tests as w grows."""
    sweep = df[df["w"].notna()].sort_values("w")

    fig, axes = plt.subplots(1, 2, figsize=(10.5, 4.2))
    ax = axes[0]
    ax.bar(
        range(len(sweep)),
        sweep["mean_task_tests"],
        label="task-relevant tests",
        color="C0",
    )
    ax.bar(
        range(len(sweep)),
        sweep["mean_distractor_tests"],
        bottom=sweep["mean_task_tests"],
        label="distractor test",
        color="C3",
    )
    ax.set_xticks(range(len(sweep)))
    ax.set_xticklabels([f"{w:.3g}" for w in sweep["w"]], rotation=45, fontsize=7)
    ax.set_xlabel("Info-gain weight w")
    ax.set_ylabel("Mean tests per episode")
    ax.set_title("Sensing usage composition")
    ax.legend(fontsize=8)
    ax.grid(True, alpha=0.3, axis="y")

    ax2 = axes[1]
    ax2.errorbar(
        sweep["w"],
        sweep["mean_distractor_fraction"],
        yerr=sweep["se_distractor_fraction"],
        marker="o",
        ms=4,
        capsize=3,
        color="C3",
    )
    ax2.set_xscale("symlog", linthresh=0.1)
    ax2.set_xlabel("Info-gain weight w")
    ax2.set_ylabel("Distractor fraction of usage")
    ax2.set_title("Reward-blind IG spends budget on the distractor")
    ax2.grid(True, alpha=0.3)
    ax2.set_ylim(-0.02, max(0.3, sweep["mean_distractor_fraction"].max() * 1.2))

    fig.tight_layout()
    FIGURES.mkdir(exist_ok=True)
    fig.savefig(path.with_suffix(".png"), dpi=150)
    fig.savefig(path.with_suffix(".pdf"))
    plt.close(fig)
    print(f"Saved {path.with_suffix('.png')} and {path.with_suffix('.pdf')}")


def main() -> None:
    df = run_sweep()
    plot_composition(df, FIGURES / "distractor_composition")

    at_w1 = df[df["agent"] == "EFE (w=1)"].iloc[0]
    at_w0 = df[(df["agent"] == "Planning+IG") & (df["w"] == 0.0)]
    ids_row = df[df["agent"] == "IDS"].iloc[0]
    print("\n=== Summary ===")
    print(
        f"Planning (w=0): distractor fraction "
        f"{(at_w0['mean_distractor_fraction'].iloc[0] if not at_w0.empty else float('nan')):.3f}"
    )
    print(f"EFE (w=1): distractor fraction {at_w1['mean_distractor_fraction']:.3f}")
    print(f"IDS: distractor fraction {ids_row['mean_distractor_fraction']:.3f}")
    high_w = df[(df["agent"] == "Planning+IG") & (df["w"] > 10)]
    if not high_w.empty:
        print(
            f"Planning+IG at large w (w>10): distractor fraction up to "
            f"{high_w['mean_distractor_fraction'].max():.3f}"
        )


if __name__ == "__main__":
    main()
