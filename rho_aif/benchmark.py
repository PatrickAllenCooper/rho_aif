"""Canonical benchmark registry for information-gathering planning.

Named configs expose the evaluation protocol used in the accompanying paper
so pip users can reproduce baselines without cloning the repository.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Optional, Sequence

import numpy as np

from rho_aif.environments.tiger import TigerEnv
from rho_aif.environments.diagnosis import DiagnosisEnv
from rho_aif.environments.bandit import BanditEnv
from rho_aif.environments.tileworld import TileworldEnv
from rho_aif.environments.inspection import InspectionEnv
from rho_aif.agents.myopic import MyopicAgent
from rho_aif.agents.planning import PlanningAgent
from rho_aif.agents.efe import EFEAgent
from rho_aif.agents.planning_infogain import PlanningInfoGainAgent
from rho_aif.agents.info_gain import InformationGainAgent
from rho_aif.agents.thompson import ThompsonSamplingAgent
from rho_aif.agents.inspection_agents import (
    InspectionTreeSearchAgent,
    InspectionGreedyAgent,
)
from rho_aif.scoring import (
    log_score,
    brier_score,
    extract_true_state,
    factored_log_score,
    factored_brier_score,
)

BENCHMARK_SEEDS = [42, 123, 456, 789, 1024]

INSPECTION_CONFIGS: Dict[str, Dict[str, Any]] = {
    "Inspection-N8": {
        "num_components": 8,
        "num_test_types": 2,
        "test_accuracies": [0.70, 0.90],
        "test_costs": [-0.5, -2.0],
        "fault_prior": 0.3,
        "correct_nominal_reward": 2.0,
        "correct_fault_reward": 5.0,
        "missed_fault_penalty": -50.0,
        "false_alarm_penalty": -5.0,
        "move_cost": -0.5,
        "tree_depth": 3,
        "max_steps": 200,
    },
    "Inspection-N16": {
        "num_components": 16,
        "num_test_types": 2,
        "test_accuracies": [0.70, 0.90],
        "test_costs": [-0.5, -2.0],
        "fault_prior": 0.3,
        "correct_nominal_reward": 2.0,
        "correct_fault_reward": 5.0,
        "missed_fault_penalty": -50.0,
        "false_alarm_penalty": -5.0,
        "move_cost": -0.5,
        "tree_depth": 2,
        "max_steps": 400,
    },
}


@dataclass(frozen=True)
class BenchmarkConfig:
    """Named evaluation protocol for one benchmark environment."""

    name: str
    family: str  # "observe_then_commit" or "inspection"
    env_factory: Callable[[], Any]
    planning_horizon: int
    episodes_per_seed: int = 1000
    seeds: Sequence[int] = field(default_factory=lambda: list(BENCHMARK_SEEDS))
    default_agent: str = "efe"
    description: str = ""
    num_states: Optional[int] = None
    tree_depth: Optional[int] = None  # inspection only


def _make_tiger():
    return TigerEnv(
        listen_accuracy=0.85,
        listen_cost=1.0,
        correct_reward=10.0,
        incorrect_penalty=-100.0,
    )


def _make_diagnosis():
    return DiagnosisEnv()


def _make_bandit():
    return BanditEnv()


def _make_tileworld():
    return TileworldEnv(grid_size=6)


def _make_inspection(config_name: str):
    cfg = INSPECTION_CONFIGS[config_name]
    return InspectionEnv(
        num_components=cfg["num_components"],
        num_test_types=cfg["num_test_types"],
        test_accuracies=cfg["test_accuracies"],
        test_costs=cfg["test_costs"],
        fault_prior=cfg["fault_prior"],
        correct_nominal_reward=cfg["correct_nominal_reward"],
        correct_fault_reward=cfg["correct_fault_reward"],
        missed_fault_penalty=cfg["missed_fault_penalty"],
        false_alarm_penalty=cfg["false_alarm_penalty"],
        move_cost=cfg["move_cost"],
        max_steps=cfg["max_steps"],
    )


BENCHMARKS: Dict[str, BenchmarkConfig] = {
    "Tiger": BenchmarkConfig(
        name="Tiger",
        family="observe_then_commit",
        env_factory=_make_tiger,
        planning_horizon=6,
        num_states=2,
        description="Classic two-state listen-or-open POMDP",
    ),
    "Diagnosis": BenchmarkConfig(
        name="Diagnosis",
        family="observe_then_commit",
        env_factory=_make_diagnosis,
        planning_horizon=3,
        num_states=4,
        description="Multi-test medical diagnosis (observe-then-commit)",
    ),
    "Bandit": BenchmarkConfig(
        name="Bandit",
        family="observe_then_commit",
        env_factory=_make_bandit,
        planning_horizon=2,
        num_states=4,
        description="Structured bandit with inspect-then-pull",
    ),
    "Tileworld-6x6": BenchmarkConfig(
        name="Tileworld-6x6",
        family="observe_then_commit",
        env_factory=_make_tileworld,
        planning_horizon=2,
        episodes_per_seed=500,
        num_states=36,
        description="Spatial scan-then-collect on a 6x6 grid",
    ),
    "Inspection-N8": BenchmarkConfig(
        name="Inspection-N8",
        family="inspection",
        env_factory=lambda: _make_inspection("Inspection-N8"),
        planning_horizon=3,
        episodes_per_seed=500,
        num_states=256,
        tree_depth=3,
        description="Structural Inspection with 8 components (|S|=256)",
    ),
    "Inspection-N16": BenchmarkConfig(
        name="Inspection-N16",
        family="inspection",
        env_factory=lambda: _make_inspection("Inspection-N16"),
        planning_horizon=2,
        episodes_per_seed=200,
        num_states=65536,
        tree_depth=2,
        description="Structural Inspection with 16 components (|S|=65,536)",
    ),
}


def list_benchmarks() -> List[str]:
    return list(BENCHMARKS.keys())


def get_benchmark(name: str) -> BenchmarkConfig:
    if name not in BENCHMARKS:
        known = ", ".join(list_benchmarks())
        raise KeyError(f"Unknown benchmark {name!r}. Known: {known}")
    return BENCHMARKS[name]


def make_env_config(env) -> dict:
    if hasattr(env, "get_observation_costs"):
        costs = env.get_observation_costs()
    else:
        costs = [env.observation_cost]
    return {
        "observation_costs": costs,
        "commit_reward_matrix": env.get_commit_reward_matrix(),
    }


def get_obs_models(env):
    if hasattr(env, "get_observation_models"):
        return env.get_observation_models()
    return [env.get_observation_model()]


def make_otc_agent(agent_name: str, env, planning_horizon: int, info_weight: float = 1.0):
    """Construct a standard observe-then-commit agent by short name."""
    obs_models = get_obs_models(env)
    config = make_env_config(env)
    key = agent_name.lower().replace("_", "-").replace(" ", "")
    if key in ("efe", "efeagent"):
        return EFEAgent(obs_models, config, planning_horizon=planning_horizon)
    if key in ("planning", "planningagent"):
        return PlanningAgent(obs_models, config, planning_horizon=planning_horizon)
    if key in ("myopic", "myopicagent"):
        return MyopicAgent(obs_models, config)
    if key in ("planning+ig", "planningig", "plan+ig", "planninginfogain"):
        return PlanningInfoGainAgent(
            obs_models, config, planning_horizon=planning_horizon, info_gain_weight=info_weight
        )
    if key in ("infogain", "informationgain", "ig"):
        return InformationGainAgent(obs_models, config, info_gain_weight=info_weight)
    if key in ("thompson", "thompsonsampling"):
        return ThompsonSamplingAgent(obs_models, config, num_samples=100)
    raise ValueError(
        f"Unknown observe-then-commit agent {agent_name!r}. "
        "Try: efe, planning, myopic, planning+ig, infogain, thompson"
    )


def make_inspection_agent(agent_name: str, env, tree_depth: int, info_weight: float = 1.0):
    key = agent_name.lower().replace("_", "-").replace(" ", "")
    if key in ("efe", "efeagent", "efew=1"):
        return InspectionTreeSearchAgent(env, info_weight=1.0, max_depth=tree_depth)
    if key in ("planning", "planningagent"):
        return InspectionTreeSearchAgent(env, info_weight=0.0, max_depth=tree_depth)
    if key in ("planning+ig", "plan+ig", "planningig"):
        return InspectionTreeSearchAgent(env, info_weight=info_weight, max_depth=tree_depth)
    if key in ("greedy", "greedyagent"):
        return InspectionGreedyAgent(env)
    raise ValueError(
        f"Unknown inspection agent {agent_name!r}. Try: efe, planning, planning+ig, greedy"
    )


def run_otc_episode(
    agent, env, max_steps: int = 200, seed: Optional[int] = None
) -> Dict[str, Any]:
    obs, info = env.reset(seed=seed)
    agent.reset()
    total_reward = 0.0
    observation_count = 0
    sensing_cost = 0.0
    true_state = None

    for _ in range(max_steps):
        action = agent.select_action()
        obs, reward, terminated, truncated, info = env.step(action)
        total_reward += reward
        if terminated or truncated:
            true_state = extract_true_state(info, env)
            belief = agent.belief.belief.copy()
            return {
                "total_reward": total_reward,
                "num_observations": observation_count,
                "sensing_cost": sensing_cost,
                "success": bool(info.get("correct", False)),
                "final_belief_entropy": agent.belief.entropy(),
                "final_confidence": agent.belief.confidence(),
                "true_state": true_state,
                "terminal_belief": belief,
                "log_score": log_score(belief, true_state),
                "brier_score": brier_score(belief, true_state),
            }
        agent.update_belief(obs, obs_action=action)
        observation_count += 1
        # Observation steps in OTC environments carry a pure sensing cost.
        sensing_cost += -reward

    true_state = extract_true_state(info, env) if info else extract_true_state({}, env)
    belief = agent.belief.belief.copy()
    return {
        "total_reward": total_reward,
        "num_observations": observation_count,
        "sensing_cost": sensing_cost,
        "success": False,
        "final_belief_entropy": agent.belief.entropy(),
        "final_confidence": agent.belief.confidence(),
        "true_state": true_state,
        "terminal_belief": belief,
        "log_score": log_score(belief, true_state),
        "brier_score": brier_score(belief, true_state),
    }


def run_inspection_episode(agent, env, seed: Optional[int] = None) -> Dict[str, Any]:
    obs, info = env.reset(seed=seed)
    agent.reset()
    total_reward = 0.0
    num_tests = 0

    for _ in range(env.max_steps):
        action = agent.select_action()
        obs, reward, terminated, truncated, info = env.step(action)
        total_reward += reward
        agent.update(action, obs)
        if env.test_action_start <= action < env.diagnose_action_start:
            num_tests += 1
        if terminated or truncated:
            break

    true_faults = env._fault_states.copy()
    fault_beliefs = agent.belief.fault_beliefs.copy()
    nc = env.num_components
    corrects = info.get("total_correct", 0)
    return {
        "total_reward": total_reward,
        "correct": corrects,
        "missed": info.get("total_missed", 0),
        "false_alarm": info.get("total_false_alarm", 0),
        "components_diagnosed": info.get("components_diagnosed", 0),
        "all_diagnosed": info.get("all_diagnosed", False),
        "tests": num_tests,
        "steps": env._step_count,
        "accuracy": corrects / nc if nc > 0 else 0.0,
        "log_score": factored_log_score(fault_beliefs, true_faults),
        "brier_score": factored_brier_score(fault_beliefs, true_faults),
        "fault_beliefs": fault_beliefs,
        "true_faults": true_faults,
    }


def summarize_otc(results: List[Dict[str, Any]], agent_name: str) -> Dict[str, Any]:
    return {
        "agent": agent_name,
        "mean_observations": float(np.mean([r["num_observations"] for r in results])),
        "success_rate": float(np.mean([r["success"] for r in results])),
        "mean_reward": float(np.mean([r["total_reward"] for r in results])),
        "std_reward": float(np.std([r["total_reward"] for r in results])),
        "mean_log_score": float(np.mean([r["log_score"] for r in results])),
        "mean_brier": float(np.mean([r["brier_score"] for r in results])),
        "mean_final_entropy": float(np.mean([r["final_belief_entropy"] for r in results])),
        "n_episodes": len(results),
    }


def summarize_inspection(results: List[Dict[str, Any]], agent_name: str, num_components: int) -> Dict[str, Any]:
    rewards = [r["total_reward"] for r in results]
    return {
        "agent": agent_name,
        "mean_reward": float(np.mean(rewards)),
        "std_reward": float(np.std(rewards)),
        "se_reward": float(np.std(rewards) / np.sqrt(len(rewards))),
        "accuracy": float(np.mean([r["correct"] for r in results]) / num_components),
        "mean_correct": float(np.mean([r["correct"] for r in results])),
        "mean_missed": float(np.mean([r["missed"] for r in results])),
        "mean_false_alarm": float(np.mean([r["false_alarm"] for r in results])),
        "mean_tests": float(np.mean([r["tests"] for r in results])),
        "completion_rate": float(np.mean([r["all_diagnosed"] for r in results])),
        "mean_steps": float(np.mean([r["steps"] for r in results])),
        "mean_log_score": float(np.mean([r["log_score"] for r in results])),
        "mean_brier": float(np.mean([r["brier_score"] for r in results])),
        "n_episodes": len(results),
    }


def run_benchmark(
    env_name: str,
    agent_name: str = "efe",
    episodes: Optional[int] = None,
    seeds: Optional[Sequence[int]] = None,
    info_weight: float = 5.0,
    progress: bool = True,
) -> Dict[str, Any]:
    """Run the canonical protocol for one (environment, agent) pair."""
    cfg = get_benchmark(env_name)
    seed_list = list(seeds) if seeds is not None else list(cfg.seeds)
    n_ep = episodes if episodes is not None else cfg.episodes_per_seed
    env = cfg.env_factory()

    episode_results: List[Dict[str, Any]] = []
    if cfg.family == "observe_then_commit":
        for seed in seed_list:
            np.random.seed(seed)
            agent = make_otc_agent(agent_name, env, cfg.planning_horizon, info_weight=info_weight)
            for ep_i in range(n_ep):
                episode_results.append(
                    run_otc_episode(agent, env, seed=seed * 10000 + ep_i)
                )
                if progress and (ep_i + 1) % max(1, n_ep // 10) == 0:
                    print(f"    seed={seed} {ep_i + 1}/{n_ep}", flush=True)
        summary = summarize_otc(episode_results, agent_name)
    else:
        depth = cfg.tree_depth or cfg.planning_horizon
        for seed in seed_list:
            np.random.seed(seed)
            agent = make_inspection_agent(agent_name, env, depth, info_weight=info_weight)
            for ep_i in range(n_ep):
                episode_results.append(
                    run_inspection_episode(agent, env, seed=seed * 10000 + ep_i)
                )
                if progress and (ep_i + 1) % max(1, n_ep // 10) == 0:
                    print(f"    seed={seed} {ep_i + 1}/{n_ep}", flush=True)
        summary = summarize_inspection(
            episode_results, agent_name, env.num_components
        )

    summary["environment"] = env_name
    summary["seeds"] = seed_list
    summary["episodes_per_seed"] = n_ep
    return summary
