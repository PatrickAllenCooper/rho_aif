#!/usr/bin/env python3
"""
POMCP battery for RockSample.

Three products, one per CSV, following the repository's "one battery, one
table" rule:

  results/results_rocksample_pomcp_tuning.csv
      Configuration selection on TUNING_SEEDS, which are disjoint from every
      evaluation seed set. Run first and frozen before any evaluation number
      is looked at.
  results/results_rocksample_pomcp_budget.csv
      Simulation-budget scaling at the reduced protocol, the artifact behind
      the appendix's compute-versus-return statement.
  results/results_rocksample_pomcp_sensitivity.csv
      Rollout policy, discount, belief mode, subtree reuse, and leaf value,
      each varied one at a time from the frozen configuration.

Each POMCP row is accompanied by a standalone row for its own rollout policy,
so how much the search tree adds over the policy it rolls out with is visible
rather than implicit. On this domain the rollout carries most of the score.

Every comparison here is simulation-matched, not compute-matched. Per-decision
wall clock is recorded in mean_planning_ms so the compute gap is reported
rather than hidden.
"""

from __future__ import annotations

import argparse
import itertools
import os
import sys
import time
from typing import Dict, List, Optional, Sequence

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from rho_aif.agents.rocksample_pomcp import RockSamplePOMCPAgent
from rho_aif.stats import holm_bonferroni, seed_level_ttest, seed_means
from run_experiment import EXTENDED_SEEDS, SEEDS
from run_rocksample import (
    ROCKSAMPLE_CONFIGS,
    compute_rocksample_stats,
    make_rocksample_env,
)

# Disjoint from SEEDS and EXTENDED_SEEDS. Configuration is selected on these
# and frozen before the evaluation batteries run.
TUNING_SEEDS = [11, 22, 33]

# Abort a battery rather than silently overrun. Checked against a five-episode
# smoke run per instance before the real episodes start.
DEFAULT_TIME_CEILING_HOURS = 12.0


class _RolloutOnlyAgent:
    """The POMCP rollout policy run as a standalone agent, no search tree.

    Shares RockSamplePOMCPAgent's belief update and rollout policy exactly, so
    the companion row measures the rollout and nothing else.
    """

    def __init__(self, env, rollout_policy: str = "approach", seed: Optional[int] = None):
        if rollout_policy == "hindsight":
            # The hindsight policy reads the sampled quality vector, which a
            # standalone agent does not have and must not have.
            raise ValueError("hindsight is a tree ablation, not a standalone policy")
        self._inner = RockSamplePOMCPAgent(
            env,
            num_simulations=1,
            rollout_policy=rollout_policy,
            seed=seed,
            collect_diagnostics=False,
        )
        self.env = env
        self.rollout_policy = rollout_policy
        self.diagnostics_history: List[Dict] = []

    def reset(self):
        self._inner.reset()
        self.diagnostics_history = []

    def select_action(self) -> int:
        t0 = time.perf_counter()
        self._inner._ensure_rock_positions()
        action = self._inner._rollout_action(
            None,
            self.env._agent_pos,
            self._inner.belief.rock_sampled,
            self._inner.belief.rock_beliefs,
        )
        self.diagnostics_history.append(
            {"planning_ms": (time.perf_counter() - t0) * 1000.0, "max_tree_depth": 0}
        )
        return int(action)

    def update(self, action: int, observation: int):
        self._inner.update(action, observation)


def run_episode(agent, env, seed: int, max_steps: int) -> dict:
    obs, info = env.reset(seed=seed)
    agent.reset()
    total_reward = 0.0
    num_checks = 0
    truncated_flag = False

    for _ in range(max_steps):
        action = agent.select_action()
        obs, reward, terminated, truncated, info = env.step(action)
        total_reward += reward
        agent.update(action, obs)
        if env.NUM_MOVE_ACTIONS <= action < env.NUM_MOVE_ACTIONS + env.num_rocks:
            num_checks += 1
        if terminated or truncated:
            truncated_flag = bool(truncated) and not bool(terminated)
            break

    planning_ms = [d["planning_ms"] for d in agent.diagnostics_history]
    depths = [d.get("max_tree_depth", 0) for d in agent.diagnostics_history]
    return {
        "total_reward": total_reward,
        "good_sampled": info.get("total_good_sampled", 0),
        "bad_sampled": info.get("total_bad_sampled", 0),
        "steps": env._step_count,
        "checks": num_checks,
        "truncated": 1.0 if truncated_flag else 0.0,
        "planning_ms": float(np.mean(planning_ms)) if planning_ms else 0.0,
        "tree_depth": float(np.max(depths)) if depths else 0.0,
    }


def evaluate(
    make_agent,
    instance: str,
    label: str,
    num_episodes: int,
    seeds: Sequence[int],
    extra: Optional[dict] = None,
    time_ceiling_hours: float = DEFAULT_TIME_CEILING_HOURS,
):
    """Run one agent configuration and return (row, episode_results).

    A five-episode smoke run projects total wall clock before the full battery
    starts, and raises rather than overrunning the declared ceiling.
    """
    env = make_rocksample_env(instance)
    max_steps = env.max_steps

    t_smoke = time.time()
    np.random.seed(int(seeds[0]))
    smoke_agent = make_agent(env, int(seeds[0]))
    for ep_i in range(5):
        run_episode(smoke_agent, env, seed=int(seeds[0]) * 10000 + ep_i, max_steps=max_steps)
    per_ep = (time.time() - t_smoke) / 5.0
    projected_h = per_ep * num_episodes * len(seeds) / 3600.0
    if projected_h > time_ceiling_hours:
        raise RuntimeError(
            f"{instance} / {label}: projected {projected_h:.1f} h exceeds the "
            f"{time_ceiling_hours:.1f} h ceiling ({per_ep:.2f} s/episode). "
            "Lower num_episodes or raise --time-ceiling deliberately."
        )
    print(f"    smoke: {per_ep:.2f} s/ep, projected {projected_h:.2f} h", flush=True)

    t0 = time.time()
    episode_results = []
    for seed in seeds:
        np.random.seed(int(seed))
        agent = make_agent(env, int(seed))
        for ep_i in range(num_episodes):
            r = run_episode(agent, env, seed=int(seed) * 10000 + ep_i, max_steps=max_steps)
            r["seed"] = int(seed)
            episode_results.append(r)
    dt = time.time() - t0

    def col(key):
        return np.array([r[key] for r in episode_results], dtype=float)

    seed_reward_means = seed_means(episode_results, lambda r: r["total_reward"])
    seed_bad_means = seed_means(episode_results, lambda r: r["bad_sampled"])
    n_seeds = len(seed_reward_means)

    row = {
        "instance": instance,
        "agent": label,
        "mean_reward": float(np.mean(col("total_reward"))),
        "std_reward": float(np.std(col("total_reward"))),
        "se_reward_pooled": float(np.std(col("total_reward")) / np.sqrt(len(episode_results))),
        "se_reward_seed_level": (
            float(np.std(seed_reward_means, ddof=1) / np.sqrt(n_seeds))
            if n_seeds > 1 else float("nan")
        ),
        "mean_good": float(np.mean(col("good_sampled"))),
        "mean_bad": float(np.mean(col("bad_sampled"))),
        "se_bad_seed_level": (
            float(np.std(seed_bad_means, ddof=1) / np.sqrt(n_seeds))
            if n_seeds > 1 else float("nan")
        ),
        "mean_checks": float(np.mean(col("checks"))),
        "mean_steps": float(np.mean(col("steps"))),
        "truncation_rate": float(np.mean(col("truncated"))),
        "mean_planning_ms": float(np.mean(col("planning_ms"))),
        "mean_tree_depth": float(np.mean(col("tree_depth"))),
        "time_s": dt,
        "n_seeds": n_seeds,
        "episodes_per_seed": num_episodes,
        "seed_list": "|".join(str(s) for s in seeds),
    }
    row.update(extra or {})
    print(
        f"  {label:44s} reward={row['mean_reward']:+.2f} "
        f"+/-{row['se_reward_seed_level']:.2f}(seed) good={row['mean_good']:.2f} "
        f"bad={row['mean_bad']:.2f} checks={row['mean_checks']:.1f} "
        f"steps={row['mean_steps']:.1f} trunc={row['truncation_rate']:.2f} "
        f"ms/dec={row['mean_planning_ms']:.1f} ({dt:.0f}s)",
        flush=True,
    )
    return row, episode_results


def _checkpoint(rows: List[dict], path: str):
    os.makedirs(os.path.dirname(os.path.abspath(path)), exist_ok=True)
    pd.DataFrame(rows).to_csv(path, index=False)


# ----------------------------------------------------------------------
# Stage 1: configuration selection on the tuning seeds
# ----------------------------------------------------------------------

# Configuration selection runs as a two-stage coordinate sweep rather than a
# full 90-cell grid, because the full grid costs roughly eight hours on the
# larger tuning instance and the two stages are close to separable in this
# domain. Stage A sweeps the two knobs that dominate behaviour, the rollout
# policy and the UCB1 exploration constant. Stage B sweeps the remaining two
# at Stage A's argmax. Both stages run only on TUNING_SEEDS.
TUNING_STAGE_A = {
    "rollout_policy": ["preferred", "approach", "random"],
    "exploration_constant": [1.0, 2.0, 5.0, 10.0, 20.0],
}
TUNING_STAGE_A_FIXED = {"planning_horizon": 15, "root_criterion": "value"}

TUNING_STAGE_B = {
    "planning_horizon": [10, 15, 25],
    "root_criterion": ["value", "visits"],
}

TUNING_INSTANCES = ["RS[5,3]", "RS[7,8]"]
TUNING_EPISODES = 50
TUNING_SIMULATIONS = 1024

TUNING_KEYS = ["exploration_constant", "planning_horizon", "root_criterion", "rollout_policy"]


def _tuning_score(df: pd.DataFrame) -> pd.Series:
    """Predeclared selection metric: mean over tuning instances of the
    within-instance min-max normalised mean reward.

    Normalising within instance first stops the larger instance's wider reward
    range from deciding the configuration on its own.
    """
    parts = []
    for instance, grp in df.groupby("instance"):
        per_cfg = grp.groupby(TUNING_KEYS)["mean_reward"].mean()
        span = per_cfg.max() - per_cfg.min()
        parts.append((per_cfg - per_cfg.min()) / span if span > 0 else per_cfg * 0.0)
    return sum(parts) / len(parts)


def _run_tuning_configs(configs, rows, out, episodes, stage_name):
    for cfg in configs:
        label = (
            f"POMCP c={cfg['exploration_constant']:g} H={cfg['planning_horizon']} "
            f"{cfg['root_criterion']} {cfg['rollout_policy']}"
        )
        for instance in TUNING_INSTANCES:
            row, _ = evaluate(
                lambda env, seed, cfg=cfg: RockSamplePOMCPAgent(
                    env, num_simulations=TUNING_SIMULATIONS, seed=seed, **cfg
                ),
                instance,
                label,
                episodes,
                TUNING_SEEDS,
                extra={"num_simulations": TUNING_SIMULATIONS, "stage": stage_name, **cfg},
                time_ceiling_hours=99.0,
            )
            rows.append(row)
            _checkpoint(rows, out)
    return rows


def run_tuning(out="results/results_rocksample_pomcp_tuning.csv", episodes=TUNING_EPISODES):
    """Select the POMCP configuration on seeds disjoint from every evaluation set.

    The rollout policy is swept here rather than fixed by hand. Silver and
    Veness's preferred-action heuristic is under-specified for this
    parameterisation, since it does not say whether to spend a check at long
    range or walk closer first, and both readings are functions of the
    simulated history alone. The choice therefore belongs in the predeclared
    tuning protocol rather than in an author's judgement after seeing
    evaluation-adjacent numbers.
    """
    rows: List[dict] = []

    stage_a = [
        dict(zip(TUNING_STAGE_A, combo), **TUNING_STAGE_A_FIXED)
        for combo in itertools.product(*TUNING_STAGE_A.values())
    ]
    print(f"Tuning stage A: {len(stage_a)} configurations x {len(TUNING_INSTANCES)} instances "
          f"x {episodes} episodes x {len(TUNING_SEEDS)} seeds", flush=True)
    rows = _run_tuning_configs(stage_a, rows, out, episodes, "tuning-A")

    score_a = _tuning_score(pd.DataFrame(rows)).sort_values(ascending=False)
    best_a = dict(zip(TUNING_KEYS, score_a.index[0]))
    print(f"\nStage A argmax: {best_a}", flush=True)

    stage_b = []
    for combo in itertools.product(*TUNING_STAGE_B.values()):
        cfg = dict(best_a)
        cfg.update(dict(zip(TUNING_STAGE_B, combo)))
        cfg["exploration_constant"] = float(cfg["exploration_constant"])
        cfg["planning_horizon"] = int(cfg["planning_horizon"])
        if cfg == best_a:
            continue
        stage_b.append(cfg)
    print(f"\nTuning stage B: {len(stage_b)} configurations", flush=True)
    rows = _run_tuning_configs(stage_b, rows, out, episodes, "tuning-B")

    df = pd.DataFrame(rows)
    _checkpoint(rows, out)
    score = _tuning_score(df).sort_values(ascending=False)
    print(f"\nTuning saved to {out}")
    print("\nSelection score (normalised mean reward across tuning instances), best first:")
    print(score.head(10).to_string())
    print(f"\nSelected configuration: {dict(zip(TUNING_KEYS, score.index[0]))}")
    return df


def frozen_config(tuning_csv="results/results_rocksample_pomcp_tuning.csv") -> dict:
    """Read the frozen configuration back off the tuning CSV.

    Reading it from disk rather than hardcoding it keeps every evaluation
    battery traceable to the artifact that selected it.
    """
    df = pd.read_csv(tuning_csv)
    best = _tuning_score(df).sort_values(ascending=False).index[0]
    cfg = dict(zip(TUNING_KEYS, best))
    return {
        "exploration_constant": float(cfg["exploration_constant"]),
        "planning_horizon": int(cfg["planning_horizon"]),
        "root_criterion": str(cfg["root_criterion"]),
        "rollout_policy": str(cfg["rollout_policy"]),
    }


# ----------------------------------------------------------------------
# Stage 2: simulation-budget scaling
# ----------------------------------------------------------------------

BUDGET_PROTOCOL = {
    "RS[5,3]": {"num_episodes": 100, "seeds": SEEDS, "budgets": [256, 1024, 4096, 16384]},
    "RS[7,4]": {"num_episodes": 100, "seeds": SEEDS, "budgets": [256, 1024, 4096, 16384]},
    "RS[7,8]": {"num_episodes": 100, "seeds": SEEDS, "budgets": [256, 1024, 4096]},
    "RS[11,11]": {"num_episodes": 100, "seeds": SEEDS, "budgets": [256, 1024, 4096]},
}



def _write_stats(episodes_by_instance: Dict[str, Dict[str, List[dict]]], csv_path: str):
    """Pairwise seed-level Welch tests per instance, Holm-Bonferroni corrected
    within instance, matching compute_rocksample_stats' convention so the POMCP
    battery carries the same uncertainty reporting as every other RockSample
    table.

    Asserts the episode results actually arrived. The failure mode this guards
    against is silent: statistics get computed in memory and then dropped
    before reaching disk, which happened independently in six scripts here.
    """
    frames = []
    for instance, by_agent in episodes_by_instance.items():
        assert by_agent, f"no episode results retained for {instance}"
        for label, eps in by_agent.items():
            assert eps and "seed" in eps[0], f"episode results for {label} lack seed tags"
        frames.append(compute_rocksample_stats(by_agent, instance))
    if not frames:
        return
    stats_csv = csv_path.replace(".csv", "_stats.csv")
    os.makedirs(os.path.dirname(os.path.abspath(stats_csv)), exist_ok=True)
    pd.concat(frames, ignore_index=True).to_csv(stats_csv, index=False)
    print(f"Statistics saved to {stats_csv}", flush=True)


def run_budget_sweep(out="results/results_rocksample_pomcp_budget.csv", cfg=None,
                     time_ceiling_hours=DEFAULT_TIME_CEILING_HOURS):
    cfg = cfg or frozen_config()
    print(f"Frozen configuration: {cfg}", flush=True)
    rows: List[dict] = []
    # Episode-level results are retained per instance so the companion
    # statistics file can be written. Dropping them here is the exact
    # "computed then discarded" defect that recurred across six scripts in
    # this repository, so it is guarded by an assertion below.
    episodes_by_instance: Dict[str, Dict[str, List[dict]]] = {}

    for instance, proto in BUDGET_PROTOCOL.items():
        print(f"\n{instance}", flush=True)
        episodes_by_instance.setdefault(instance, {})
        row, eps = evaluate(
            lambda env, seed: _RolloutOnlyAgent(
                env, rollout_policy=cfg["rollout_policy"], seed=seed
            ),
            instance,
            f"Rollout only ({cfg['rollout_policy']})",
            proto["num_episodes"],
            proto["seeds"],
            extra={"num_simulations": 0, "stage": "budget", **cfg},
            time_ceiling_hours=time_ceiling_hours,
        )
        rows.append(row)
        episodes_by_instance[instance][row["agent"]] = eps
        _checkpoint(rows, out)

        for n_sims in proto["budgets"]:
            row, eps = evaluate(
                lambda env, seed, n=n_sims: RockSamplePOMCPAgent(
                    env, num_simulations=n, seed=seed, **cfg
                ),
                instance,
                f"POMCP ({n_sims} sims)",
                proto["num_episodes"],
                proto["seeds"],
                extra={"num_simulations": n_sims, "stage": "budget", **cfg},
                time_ceiling_hours=time_ceiling_hours,
            )
            rows.append(row)
            episodes_by_instance[instance][row["agent"]] = eps
            _checkpoint(rows, out)

    _write_stats(episodes_by_instance, out)
    print(f"\nBudget sweep saved to {out}")
    return pd.DataFrame(rows)


# ----------------------------------------------------------------------
# Stage 3: sensitivity to the design choices that are not free
# ----------------------------------------------------------------------

SENSITIVITY_INSTANCE = "RS[5,3]"
SENSITIVITY_EPISODES = 100
SENSITIVITY_SIMULATIONS = 2048


def run_sensitivity(out="results/results_rocksample_pomcp_sensitivity.csv", cfg=None,
                    time_ceiling_hours=DEFAULT_TIME_CEILING_HOURS):
    cfg = cfg or frozen_config()
    variants = [("frozen", {})]
    variants += [(f"rollout={p}", {"rollout_policy": p})
                 for p in ("preferred", "approach", "random", "hindsight")
                 if p != cfg["rollout_policy"]]
    variants += [
        ("discount=0.95", {"discount": 0.95}),
        ("discount=0.99", {"discount": 0.99}),
        ("belief=particle", {"belief_mode": "particle"}),
        ("reuse_subtree", {"reuse_subtree": True}),
        ("leaf=zero", {"leaf_value": "zero"}),
        ("leaf=greedy_belief", {"leaf_value": "greedy_belief"}),
        ("no_budget_aware_horizon", {"budget_aware_horizon": False}),
    ]

    rows: List[dict] = []
    episodes: Dict[str, List[dict]] = {}
    for label, override in variants:
        merged = dict(cfg)
        merged.update(override)
        row, eps = evaluate(
            lambda env, seed, m=merged: RockSamplePOMCPAgent(
                env, num_simulations=SENSITIVITY_SIMULATIONS, seed=seed, **m
            ),
            SENSITIVITY_INSTANCE,
            f"POMCP [{label}]",
            SENSITIVITY_EPISODES,
            SEEDS,
            extra={"num_simulations": SENSITIVITY_SIMULATIONS, "stage": "sensitivity",
                   "variant": label, **merged},
            time_ceiling_hours=time_ceiling_hours,
        )
        rows.append(row)
        episodes[row["agent"]] = eps
        _checkpoint(rows, out)

    for policy in ("preferred", "approach", "random"):
        row, eps = evaluate(
            lambda env, seed, p=policy: _RolloutOnlyAgent(env, rollout_policy=p, seed=seed),
            SENSITIVITY_INSTANCE,
            f"Rollout only ({policy})",
            SENSITIVITY_EPISODES,
            SEEDS,
            extra={"num_simulations": 0, "stage": "sensitivity",
                   "variant": f"rollout-only-{policy}", "rollout_policy": policy},
            time_ceiling_hours=time_ceiling_hours,
        )
        rows.append(row)
        episodes[row["agent"]] = eps
        _checkpoint(rows, out)

    _write_stats({SENSITIVITY_INSTANCE: episodes}, out)
    print(f"\nSensitivity saved to {out}")
    return pd.DataFrame(rows)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("stage", choices=["tuning", "budget", "sensitivity", "all"])
    parser.add_argument("--episodes", type=int, default=None)
    parser.add_argument("--time-ceiling", type=float, default=DEFAULT_TIME_CEILING_HOURS)
    args = parser.parse_args()

    if args.stage in ("tuning", "all"):
        run_tuning(episodes=args.episodes or TUNING_EPISODES)
    if args.stage in ("budget", "all"):
        run_budget_sweep(time_ceiling_hours=args.time_ceiling)
    if args.stage in ("sensitivity", "all"):
        run_sensitivity(time_ceiling_hours=args.time_ceiling)
