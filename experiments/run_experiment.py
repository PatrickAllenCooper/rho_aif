#!/usr/bin/env python3
"""
Run epistemic foraging experiments across environments and agents.

Compares Myopic, Information Gain, and EFE agents on discrete POMDP
environments, measuring belief convergence, sample efficiency, and
policy quality.
"""

import numpy as np
import pandas as pd
from scipy import stats
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Type

import time

SEEDS = [42, 123, 456, 789, 1024, 2048, 3141, 4096, 5555, 6789]

from rho_aif.environments.info_seeking import InfoSeekingEnv
from rho_aif.environments.tiger import TigerEnv
from rho_aif.environments.diagnosis import DiagnosisEnv
from rho_aif.environments.bandit import BanditEnv
from rho_aif.environments.navigation import NavigationEnv
from rho_aif.agents.base import BaseAgent
from rho_aif.agents.myopic import MyopicAgent
from rho_aif.agents.info_gain import InformationGainAgent
from rho_aif.agents.efe import EFEAgent
from rho_aif.agents.planning import PlanningAgent
from rho_aif.agents.navigation_efe import NavigationEFEAgent
from rho_aif.agents.navigation_baselines import NavigationMyopicAgent, NavigationInfoGainAgent
from rho_aif.agents.pymdp_agent import PyMDPAgent
from rho_aif.agents.planning_infogain import PlanningInfoGainAgent
from rho_aif.agents.epistemic_only import EpistemicOnlyAgent
from rho_aif.agents.thompson import ThompsonSamplingAgent


@dataclass
class EpisodeResult:
    agent_name: str
    num_observations: int
    final_belief_entropy: float
    final_confidence: float
    success: bool
    total_reward: float
    belief_history: List[np.ndarray] = field(default_factory=list)
    seed: Optional[int] = None


def make_env_config(env) -> dict:
    """Extract agent-facing config from any environment."""
    if hasattr(env, "get_observation_costs"):
        costs = env.get_observation_costs()
    else:
        costs = [env.observation_cost]
    return {
        "observation_costs": costs,
        "commit_reward_matrix": env.get_commit_reward_matrix(),
    }


def get_obs_models(env):
    """Get observation models from an environment (single or multi)."""
    if hasattr(env, "get_observation_models"):
        return env.get_observation_models()
    return [env.get_observation_model()]


def make_agent(
    agent_class: Type[BaseAgent],
    env,
    **kwargs,
) -> BaseAgent:
    obs_models = get_obs_models(env)
    config = make_env_config(env)
    return agent_class(obs_models, config, **kwargs)


def run_episode(agent: BaseAgent, env, max_steps: int = 200) -> EpisodeResult:
    obs, info = env.reset()
    agent.reset()
    total_reward = 0.0
    observation_count = 0

    for _ in range(max_steps):
        action = agent.select_action()
        obs, reward, terminated, truncated, info = env.step(action)
        total_reward += reward

        if terminated:
            return EpisodeResult(
                agent_name=agent.__class__.__name__,
                num_observations=observation_count,
                final_belief_entropy=agent.belief.entropy(),
                final_confidence=agent.belief.confidence(),
                success=info.get("correct", False),
                total_reward=total_reward,
                belief_history=[b.copy() for b in agent.belief.history],
            )

        agent.update_belief(obs, obs_action=action)
        observation_count += 1

    return EpisodeResult(
        agent_name=agent.__class__.__name__,
        num_observations=observation_count,
        final_belief_entropy=agent.belief.entropy(),
        final_confidence=agent.belief.confidence(),
        success=False,
        total_reward=total_reward,
    )


def run_experiment(
    agent_class: Type[BaseAgent],
    env,
    num_episodes: int = 1000,
    **agent_kwargs,
) -> List[EpisodeResult]:
    agent = make_agent(agent_class, env, **agent_kwargs)
    results = []
    log_interval = max(1, num_episodes // 10)

    for i in range(num_episodes):
        result = run_episode(agent, env)
        results.append(result)
        if (i + 1) % log_interval == 0:
            pct = ((i + 1) / num_episodes) * 100
            print(f"    {i+1}/{num_episodes} ({pct:.0f}%)", flush=True)

    return results


def summarize_results(results: List[EpisodeResult]) -> Dict:
    return {
        "agent": results[0].agent_name,
        "mean_observations": np.mean([r.num_observations for r in results]),
        "std_observations": np.std([r.num_observations for r in results]),
        "mean_final_entropy": np.mean([r.final_belief_entropy for r in results]),
        "mean_confidence": np.mean([r.final_confidence for r in results]),
        "success_rate": np.mean([r.success for r in results]),
        "mean_reward": np.mean([r.total_reward for r in results]),
        "std_reward": np.std([r.total_reward for r in results]),
    }


def run_experiment_multi_seed(
    agent_class: Type[BaseAgent],
    env,
    num_episodes: int = 1000,
    seeds: List[int] = None,
    **agent_kwargs,
) -> List[EpisodeResult]:
    """Run experiment across multiple seeds, concatenating all results."""
    if seeds is None:
        seeds = SEEDS
    all_results = []
    for seed in seeds:
        np.random.seed(seed)
        results = run_experiment(agent_class, env, num_episodes, **agent_kwargs)
        for r in results:
            r.seed = seed
        all_results.extend(results)
    return all_results


def summarize_multi_seed(
    agent_class: Type[BaseAgent],
    env,
    num_episodes: int = 1000,
    seeds: List[int] = None,
    **agent_kwargs,
) -> Dict:
    """Run across multiple seeds and return per-seed summary statistics."""
    if seeds is None:
        seeds = SEEDS
    per_seed = []
    for seed in seeds:
        np.random.seed(seed)
        results = run_experiment(agent_class, env, num_episodes, **agent_kwargs)
        per_seed.append(summarize_results(results))

    keys = ["mean_observations", "success_rate", "mean_reward"]
    agg = {"agent": per_seed[0]["agent"], "n_seeds": len(seeds)}
    for k in keys:
        vals = [s[k] for s in per_seed]
        agg[f"{k}_mean"] = np.mean(vals)
        agg[f"{k}_std"] = np.std(vals)
    return agg


def print_statistical_comparison(
    name_a: str,
    name_b: str,
    results_a: List[EpisodeResult],
    results_b: List[EpisodeResult],
):
    for metric_name, extractor in [
        ("Observations", lambda r: r.num_observations),
        ("Reward", lambda r: r.total_reward),
    ]:
        vals_a = [extractor(r) for r in results_a]
        vals_b = [extractor(r) for r in results_b]
        t_stat, p_val = stats.ttest_ind(vals_a, vals_b)
        sig = "***" if p_val < 0.001 else "**" if p_val < 0.01 else "*" if p_val < 0.05 else "n.s."
        print(f"  {metric_name:12s}: {name_a} vs {name_b}  t={t_stat:+.3f}  p={p_val:.6f}  {sig}")


def compute_full_statistics(
    all_raw: Dict[str, List[EpisodeResult]],
    env_name: str = "",
) -> pd.DataFrame:
    """Compute comprehensive statistics with Holm-Bonferroni correction.

    Returns a DataFrame with pairwise comparisons including corrected p-values,
    bootstrap CIs, and Cohen's d effect sizes.
    """
    from rho_aif.stats import bootstrap_ci, cohens_d, holm_bonferroni

    labels = list(all_raw.keys())
    rows = []
    raw_p_values = []

    for metric_name, extractor in [
        ("Reward", lambda r: r.total_reward),
        ("Success", lambda r: float(r.success)),
        ("Observations", lambda r: r.num_observations),
    ]:
        pairs = []
        for i in range(len(labels)):
            for j in range(i + 1, len(labels)):
                vals_a = np.array([extractor(r) for r in all_raw[labels[i]]])
                vals_b = np.array([extractor(r) for r in all_raw[labels[j]]])

                mean_a, ci_a_lo, ci_a_hi = bootstrap_ci(vals_a)
                mean_b, ci_b_lo, ci_b_hi = bootstrap_ci(vals_b)

                d = cohens_d(vals_a, vals_b)
                t_stat, p_val = stats.ttest_ind(vals_a, vals_b)
                if np.isnan(p_val):
                    p_val = 1.0

                pairs.append({
                    "env": env_name,
                    "metric": metric_name,
                    "agent_a": labels[i],
                    "agent_b": labels[j],
                    "mean_a": mean_a,
                    "ci_a": f"[{ci_a_lo:.3f}, {ci_a_hi:.3f}]",
                    "mean_b": mean_b,
                    "ci_b": f"[{ci_b_lo:.3f}, {ci_b_hi:.3f}]",
                    "diff": mean_a - mean_b,
                    "cohens_d": d,
                    "t_stat": t_stat,
                    "p_raw": p_val,
                })
                raw_p_values.append(p_val)

        rows.extend(pairs)

    p_list = [r["p_raw"] for r in rows]
    significant = holm_bonferroni(p_list)
    for r, sig in zip(rows, significant):
        r["significant_hb"] = sig

    df = pd.DataFrame(rows)
    return df


def tune_info_gain_weight(
    env,
    candidate_weights: List[float] = None,
    tune_episodes: int = 200,
    metric: str = "success_rate",
) -> float:
    """Find the best info_gain_weight for InformationGainAgent on a given env.

    Runs a grid search over candidate weights using a smaller number of
    tuning episodes, returning the weight that maximizes the chosen metric.
    """
    if candidate_weights is None:
        candidate_weights = [0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 20.0, 50.0, 100.0]

    best_weight = 1.0
    best_score = -float("inf")

    for w in candidate_weights:
        results = run_experiment(
            InformationGainAgent, env, tune_episodes, info_gain_weight=w
        )
        summary = summarize_results(results)
        score = summary[metric]
        if score > best_score:
            best_score = score
            best_weight = w

    return best_weight


def run_info_seeking_experiment(num_episodes: int = 1000, seeds: List[int] = None):
    """Run the full experiment on the two-state info-seeking environment."""
    if seeds is None:
        seeds = SEEDS

    env = InfoSeekingEnv(
        observation_accuracy=0.75,
        observation_cost=0.1,
        correct_reward=1.0,
        incorrect_penalty=-1.0,
    )

    print("=" * 72)
    print("INFO-SEEKING TESTBED EXPERIMENT")
    print("=" * 72)
    print(f"  Episodes per seed: {num_episodes}, Seeds: {seeds}")
    print(f"  Accuracy: {env.observation_accuracy}")
    print(f"  Obs cost: {env.observation_cost}")
    print(f"  Rewards:  +{env.correct_reward} / {env.incorrect_penalty}")
    print()

    np.random.seed(seeds[0])
    print("Tuning InfoGain weight...")
    best_w = tune_info_gain_weight(env, tune_episodes=200)
    print(f"  Best InfoGain weight: {best_w}\n")

    horizon = 4
    best_w_plan = tune_info_gain_weight(env, tune_episodes=200)
    print(f"  Best Planning+IG weight: {best_w_plan}\n")

    agent_configs = [
        ("Myopic", MyopicAgent, {}),
        ("Planning", PlanningAgent, {"planning_horizon": horizon}),
        ("InfoGain", InformationGainAgent, {"info_gain_weight": 1.0}),
        ("InfoGain-Tuned", InformationGainAgent, {"info_gain_weight": best_w}),
        ("Planning+IG", PlanningInfoGainAgent, {"planning_horizon": horizon, "info_gain_weight": best_w_plan}),
        ("EpistemicOnly", EpistemicOnlyAgent, {"planning_horizon": horizon}),
        ("EFE", EFEAgent, {"planning_horizon": horizon}),
        ("Thompson", ThompsonSamplingAgent, {"num_samples": 100}),
        ("PyMDP-AIF", PyMDPAgent, {}),
    ]

    all_results = {}
    all_raw = {}

    for label, agent_class, kwargs in agent_configs:
        print(f"Running {label} ({len(seeds)} seeds)...")
        raw = run_experiment_multi_seed(agent_class, env, num_episodes, seeds=seeds, **kwargs)
        all_raw[label] = raw
        all_results[label] = summarize_results(raw)
        s = all_results[label]
        print(
            f"  -> obs={s['mean_observations']:.2f}  "
            f"success={s['success_rate']:.1%}  "
            f"reward={s['mean_reward']:+.3f}\n"
        )

    print("-" * 72)
    print("STATISTICAL COMPARISONS")
    print("-" * 72)
    labels = list(all_raw.keys())
    for i in range(len(labels)):
        for j in range(i + 1, len(labels)):
            print_statistical_comparison(
                labels[i], labels[j], all_raw[labels[i]], all_raw[labels[j]]
            )
    print()

    summary_df = pd.DataFrame(all_results).T
    summary_df.to_csv("results/results_summary.csv")
    print("Results saved to results/results_summary.csv")

    stats_df = compute_full_statistics(all_raw, env_name="InfoSeeking")
    stats_df.to_csv("results/results_summary_stats.csv", index=False)
    print("Full statistics saved to results/results_summary_stats.csv")

    return all_results, all_raw


def run_tiger_experiment(num_episodes: int = 1000, seeds: List[int] = None):
    """Run the full experiment on the Tiger problem."""
    if seeds is None:
        seeds = SEEDS

    env = TigerEnv(
        listen_accuracy=0.85,
        listen_cost=1.0,
        correct_reward=10.0,
        incorrect_penalty=-100.0,
    )

    print("=" * 72)
    print("TIGER PROBLEM EXPERIMENT")
    print("=" * 72)
    print(f"  Episodes per seed: {num_episodes}, Seeds: {seeds}")
    print(f"  Accuracy:  {env.listen_accuracy}")
    print(f"  Listen cost: {env.listen_cost}")
    print(f"  Rewards:   +{env.correct_reward} / {env.incorrect_penalty}")
    print()

    np.random.seed(seeds[0])
    print("Tuning InfoGain weight...")
    best_w = tune_info_gain_weight(env, tune_episodes=200)
    print(f"  Best InfoGain weight: {best_w}\n")

    horizon = 6
    best_w_plan = tune_info_gain_weight(env, tune_episodes=200)
    print(f"  Best Planning+IG weight: {best_w_plan}\n")

    agent_configs = [
        ("Myopic", MyopicAgent, {}),
        ("Planning", PlanningAgent, {"planning_horizon": horizon}),
        ("InfoGain", InformationGainAgent, {"info_gain_weight": 1.0}),
        ("InfoGain-Tuned", InformationGainAgent, {"info_gain_weight": best_w}),
        ("Planning+IG", PlanningInfoGainAgent, {"planning_horizon": horizon, "info_gain_weight": best_w_plan}),
        ("EpistemicOnly", EpistemicOnlyAgent, {"planning_horizon": horizon}),
        ("EFE", EFEAgent, {"planning_horizon": horizon}),
        ("Thompson", ThompsonSamplingAgent, {"num_samples": 100}),
        ("PyMDP-AIF", PyMDPAgent, {}),
    ]

    all_results = {}
    all_raw = {}

    for label, agent_class, kwargs in agent_configs:
        print(f"Running {label} ({len(seeds)} seeds)...")
        raw = run_experiment_multi_seed(agent_class, env, num_episodes, seeds=seeds, **kwargs)
        all_raw[label] = raw
        all_results[label] = summarize_results(raw)
        s = all_results[label]
        print(
            f"  -> obs={s['mean_observations']:.2f}  "
            f"success={s['success_rate']:.1%}  "
            f"reward={s['mean_reward']:+.3f}\n"
        )

    print("-" * 72)
    print("STATISTICAL COMPARISONS")
    print("-" * 72)
    labels = list(all_raw.keys())
    for i in range(len(labels)):
        for j in range(i + 1, len(labels)):
            print_statistical_comparison(
                labels[i], labels[j], all_raw[labels[i]], all_raw[labels[j]]
            )
    print()

    summary_df = pd.DataFrame(all_results).T
    summary_df.to_csv("results/results_tiger.csv")
    print("Results saved to results/results_tiger.csv")

    stats_df = compute_full_statistics(all_raw, env_name="Tiger")
    stats_df.to_csv("results/results_tiger_stats.csv", index=False)
    print("Full statistics saved to results/results_tiger_stats.csv")

    return all_results, all_raw


def run_generic_experiment(env, label: str, agent_configs, num_episodes: int = 1000,
                           csv_name: str = None, seeds: List[int] = None):
    """Run a standard experiment with multiple agents on a given environment."""
    if seeds is None:
        seeds = SEEDS
    print("=" * 72)
    print(f"{label}")
    print("=" * 72)
    print(f"  Episodes per seed: {num_episodes}, Seeds: {seeds}")
    print()

    all_results = {}
    all_raw = {}

    for agent_label, agent_class, kwargs, make_fn in agent_configs:
        print(f"Running {agent_label} ({len(seeds)} seeds)...")
        t0 = time.time()
        results = []
        for seed in seeds:
            np.random.seed(seed)
            if make_fn:
                agent = make_fn()
            else:
                agent = make_agent(agent_class, env, **kwargs)
            for i in range(num_episodes):
                result = run_episode(agent, env)
                results.append(result)
        dt = time.time() - t0
        all_raw[agent_label] = results
        all_results[agent_label] = summarize_results(results)
        all_results[agent_label]["time_s"] = dt
        s = all_results[agent_label]
        print(
            f"  -> obs={s['mean_observations']:.2f}  "
            f"success={s['success_rate']:.1%}  "
            f"reward={s['mean_reward']:+.3f}  "
            f"({dt:.1f}s)\n"
        )

    print("-" * 72)
    print("STATISTICAL COMPARISONS")
    print("-" * 72)
    labels = list(all_raw.keys())
    for i in range(len(labels)):
        for j in range(i + 1, len(labels)):
            print_statistical_comparison(
                labels[i], labels[j], all_raw[labels[i]], all_raw[labels[j]]
            )
    print()

    if csv_name:
        summary_df = pd.DataFrame(all_results).T
        summary_df.to_csv(csv_name)
        print(f"Results saved to {csv_name}")

        stats_df = compute_full_statistics(all_raw, env_name=label)
        stats_csv = csv_name.replace(".csv", "_stats.csv")
        stats_df.to_csv(stats_csv, index=False)
        print(f"Full statistics saved to {stats_csv}")

        efe_comparisons = stats_df[
            (stats_df["metric"] == "Reward")
            & ((stats_df["agent_a"] == "EFE") | (stats_df["agent_b"] == "EFE"))
        ]
        if not efe_comparisons.empty:
            print("\n  EFE Reward comparisons (Holm-Bonferroni corrected):")
            for _, row in efe_comparisons.iterrows():
                other = row["agent_b"] if row["agent_a"] == "EFE" else row["agent_a"]
                sig_mark = "*" if row["significant_hb"] else "n.s."
                print(
                    f"    vs {other:15s}: d={row['cohens_d']:+.3f}  "
                    f"p_raw={row['p_raw']:.6f}  HB={sig_mark}"
                )
        print()

    return all_results, all_raw


def run_diagnosis_experiment(num_conditions: int = 4, num_episodes: int = 1000, seeds: List[int] = None):
    if seeds is None:
        seeds = SEEDS
    np.random.seed(seeds[0])
    env = DiagnosisEnv(num_conditions=num_conditions, test_accuracy=0.80, test_cost=1.0,
                       correct_reward=10.0, incorrect_penalty=-50.0)
    print(f"Tuning InfoGain weight for Diagnosis N={num_conditions}...")
    best_w = tune_info_gain_weight(env, tune_episodes=200)
    print(f"  Best InfoGain weight: {best_w}\n")
    best_w_plan = tune_info_gain_weight(env, tune_episodes=200)
    print(f"  Best Planning+IG weight: {best_w_plan}\n")
    horizon = 3
    configs = [
        ("Myopic", MyopicAgent, {}, None),
        ("Planning", PlanningAgent, {"planning_horizon": horizon}, None),
        ("InfoGain", InformationGainAgent, {"info_gain_weight": 1.0}, None),
        ("InfoGain-Tuned", InformationGainAgent, {"info_gain_weight": best_w}, None),
        ("Planning+IG", PlanningInfoGainAgent, {"planning_horizon": horizon, "info_gain_weight": best_w_plan}, None),
        ("EpistemicOnly", EpistemicOnlyAgent, {"planning_horizon": horizon}, None),
        ("EFE", EFEAgent, {"planning_horizon": horizon}, None),
        ("Thompson", ThompsonSamplingAgent, {"num_samples": 100}, None),
    ]
    return run_generic_experiment(
        env, f"DIAGNOSIS EXPERIMENT (N={num_conditions})", configs,
        num_episodes, f"results/results_diagnosis_n{num_conditions}.csv", seeds=seeds
    )


def run_bandit_experiment(num_arms: int = 4, num_episodes: int = 1000, seeds: List[int] = None):
    if seeds is None:
        seeds = SEEDS
    np.random.seed(seeds[0])
    env = BanditEnv(num_arms=num_arms, inspect_accuracy=0.80, inspect_cost=0.5,
                    correct_reward=10.0, small_reward=1.0)
    print(f"Tuning InfoGain weight for Bandit K={num_arms}...")
    best_w = tune_info_gain_weight(env, tune_episodes=200)
    print(f"  Best InfoGain weight: {best_w}\n")
    best_w_plan = tune_info_gain_weight(env, tune_episodes=200)
    print(f"  Best Planning+IG weight: {best_w_plan}\n")
    horizon = 2
    configs = [
        ("Myopic", MyopicAgent, {}, None),
        ("Planning", PlanningAgent, {"planning_horizon": horizon}, None),
        ("InfoGain", InformationGainAgent, {"info_gain_weight": 1.0}, None),
        ("InfoGain-Tuned", InformationGainAgent, {"info_gain_weight": best_w}, None),
        ("Planning+IG", PlanningInfoGainAgent, {"planning_horizon": horizon, "info_gain_weight": best_w_plan}, None),
        ("EpistemicOnly", EpistemicOnlyAgent, {"planning_horizon": horizon}, None),
        ("EFE", EFEAgent, {"planning_horizon": horizon}, None),
        ("Thompson", ThompsonSamplingAgent, {"num_samples": 100}, None),
    ]
    return run_generic_experiment(
        env, f"BANDIT EXPERIMENT (K={num_arms})", configs,
        num_episodes, "results/results_bandit.csv", seeds=seeds
    )


def run_navigation_experiment(
    grid_size: int = 3,
    num_episodes: int = 500,
    seeds: List[int] = None,
    max_steps: Optional[int] = None,
    planning_horizon: int = 2,
    output_csv: str = "results/results_navigation.csv",
):
    """Partially observable grid navigation. Default max_steps matches prior runs (2 n^2)."""
    if seeds is None:
        seeds = SEEDS
    if max_steps is None:
        max_steps = grid_size * grid_size * 2
    env = NavigationEnv(grid_size=grid_size, max_steps=max_steps)

    def make_nav_myopic():
        return NavigationMyopicAgent(env)

    def make_nav_infogain():
        return NavigationInfoGainAgent(env, info_gain_weight=1.0)

    def make_nav_efe():
        return NavigationEFEAgent(env, planning_horizon=planning_horizon)

    configs = [
        ("NavMyopic", None, {}, make_nav_myopic),
        ("NavInfoGain", None, {}, make_nav_infogain),
        ("NavEFE", None, {}, make_nav_efe),
    ]
    return run_generic_experiment(
        env,
        f"NAVIGATION EXPERIMENT ({grid_size}x{grid_size})",
        configs,
        num_episodes,
        output_csv,
        seeds=seeds,
    )


def run_navigation_scaling(
    grid_sizes: tuple = (3, 5, 7),
    num_episodes: int = 150,
    seeds: List[int] = None,
    output_csv: str = "results/results_navigation_scaling.csv",
):
    """
    Navigation across grid sizes with a more generous step budget (3 n^2) and deeper
    EFE planning on larger grids. Writes one CSV row per (grid_size, agent).
    Default seeds are five (matches multi-seed convention in the paper); pass SEEDS for all ten.
    """
    if seeds is None:
        seeds = [42, 123, 456, 789, 1024]
    print("=" * 72)
    print("NAVIGATION SCALING (multiple grid sizes)")
    print("=" * 72)
    rows = []
    for gs in grid_sizes:
        max_steps = 3 * gs * gs
        # Depth 3 on large grids makes NavEFE prohibitively slow; step budget is the main scaling knob.
        planning_horizon = 2
        env = NavigationEnv(grid_size=gs, max_steps=max_steps)

        def make_nav_myopic():
            return NavigationMyopicAgent(env)

        def make_nav_infogain():
            return NavigationInfoGainAgent(env, info_gain_weight=1.0)

        def make_nav_efe():
            return NavigationEFEAgent(env, planning_horizon=planning_horizon)

        configs = [
            ("NavMyopic", make_nav_myopic),
            ("NavInfoGain", make_nav_infogain),
            ("NavEFE", make_nav_efe),
        ]
        print(f"\n--- Grid {gs}x{gs} (|S|={gs * gs}), max_steps={max_steps}, EFE H={planning_horizon} ---")
        for agent_label, make_fn in configs:
            t0 = time.time()
            results = []
            for seed in seeds:
                np.random.seed(seed)
                agent = make_fn()
                for _ in range(num_episodes):
                    results.append(run_episode(agent, env))
            dt = time.time() - t0
            s = summarize_results(results)
            row = {
                "grid_size": gs,
                "num_states": gs * gs,
                "max_steps": max_steps,
                "efe_planning_horizon": planning_horizon,
                "agent": agent_label,
                "mean_observations": s["mean_observations"],
                "std_observations": s["std_observations"],
                "success_rate": s["success_rate"],
                "mean_reward": s["mean_reward"],
                "std_reward": s["std_reward"],
                "time_s": dt,
            }
            rows.append(row)
            print(
                f"  {agent_label:12s} success={s['success_rate']:.1%} "
                f"reward={s['mean_reward']:+.2f} obs={s['mean_observations']:.1f} ({dt:.1f}s)"
            )
    df = pd.DataFrame(rows)
    df.to_csv(output_csv, index=False)
    print(f"\nSaved {output_csv}")
    return df


def run_scaling_analysis(seeds: List[int] = None):
    """Run the Diagnosis env at N=2,4,8,16 and report scaling curves."""
    print("=" * 72)
    print("SCALING ANALYSIS: DIAGNOSIS N=2,4,8,16")
    print("=" * 72)
    print()

    if seeds is None:
        seeds = SEEDS

    scaling_data = []
    for n in [2, 4, 8, 16]:
        print(f"--- N = {n} ---")
        env = DiagnosisEnv(num_conditions=n, test_accuracy=0.80, test_cost=1.0,
                           correct_reward=10.0, incorrect_penalty=-50.0)
        horizon = 2
        episodes = 500

        for agent_label, agent_class, kwargs in [
            ("Myopic", MyopicAgent, {}),
            ("Planning", PlanningAgent, {"planning_horizon": horizon}),
            ("InfoGain", InformationGainAgent, {"info_gain_weight": 1.0}),
            ("EFE", EFEAgent, {"planning_horizon": horizon}),
        ]:
            t0 = time.time()
            results = []
            for seed in seeds:
                np.random.seed(seed)
                agent = make_agent(agent_class, env, **kwargs)
                for _ in range(episodes):
                    results.append(run_episode(agent, env))
            dt = time.time() - t0
            s = summarize_results(results)
            s["N"] = n
            s["time_s"] = dt
            scaling_data.append(s)
            print(
                f"  {agent_label:10s}: obs={s['mean_observations']:.2f}  "
                f"success={s['success_rate']:.1%}  "
                f"reward={s['mean_reward']:+.3f}  "
                f"({dt:.1f}s)"
            )
        print()

    df = pd.DataFrame(scaling_data)
    df.to_csv("results/results_scaling.csv", index=False)
    print("Scaling results saved to results/results_scaling.csv")
    return df


if __name__ == "__main__":
    import sys

    cmd = sys.argv[1] if len(sys.argv) > 1 else "info"
    if cmd == "tiger":
        run_tiger_experiment()
    elif cmd == "diagnosis":
        run_diagnosis_experiment()
    elif cmd == "bandit":
        run_bandit_experiment()
    elif cmd == "navigation":
        run_navigation_experiment()
    elif cmd == "navigation-scaling":
        run_navigation_scaling()
    elif cmd == "scaling":
        run_scaling_analysis()
    elif cmd == "phase2":
        run_diagnosis_experiment()
        print("\n\n")
        run_bandit_experiment()
        print("\n\n")
        run_navigation_experiment()
    elif cmd == "all":
        run_info_seeking_experiment()
        print("\n\n")
        run_tiger_experiment()
        print("\n\n")
        run_diagnosis_experiment()
        print("\n\n")
        run_bandit_experiment()
        print("\n\n")
        run_navigation_experiment()
    else:
        run_info_seeking_experiment()
