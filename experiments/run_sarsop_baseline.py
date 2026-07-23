#!/usr/bin/env python3
"""
SARSOP baseline for the observe-then-commit suite (Stage F of the full-paper plan).

Exports each discrete OTC benchmark (Tiger, Diagnosis, Bandit) to Cassandra
.pomdp format, solves it with the APPL SARSOP solver (pomdpsol; build with
tools/build_sarsop.sh), and evaluates the resulting alpha-vector policy inside
the project's own simulators via run_otc_episode, so all agents face identical
episode mechanics and metrics.

Comparison agents: EFE (w=1) and Planning+IG at a usage-matched weight taken
from the saved shadow-price usage curves.

Model note: SARSOP solves the discounted infinite-horizon POMDP; we use
discount 0.999 with an absorbing post-commit state. Episodes here are
undiscounted and last ~4-15 steps, so the distortion is negligible.
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import List, Optional, Sequence, Tuple

import numpy as np
import pandas as pd

_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(_ROOT))

from rho_aif.agents.base import BaseAgent
from rho_aif.benchmark import (
    get_benchmark,
    get_obs_models,
    make_env_config,
    make_otc_agent,
    run_otc_episode,
)
from rho_aif.budget import crossing_bracket, UsageCurvePoint

RESULTS = _ROOT / "results"
POMDP_DIR = RESULTS / "sarsop_models"
DEFAULT_POMDPSOL = _ROOT / "tools" / "sarsop" / "src" / "pomdpsol"

ENVS = ["Tiger", "Diagnosis", "Bandit"]


# ---------------------------------------------------------------------------
# Export to Cassandra .pomdp
# ---------------------------------------------------------------------------

def write_pomdp_file(env, path: Path, discount: float = 0.999) -> dict:
    """
    Generic exporter for the discrete OTC family.

    States: the env's hidden states plus an absorbing 'done' state.
    Actions: K observation actions then N commit actions (env layout order).
    Observations: outcome indices padded to the widest model, plus 'onull'.
    """
    obs_models = get_obs_models(env)
    config = make_env_config(env)
    commit = np.asarray(config["commit_reward_matrix"], dtype=float)
    costs = [float(c) for c in config["observation_costs"]]

    n = obs_models[0].shape[0]  # hidden states
    n_commit = commit.shape[0]
    k = len(obs_models)
    m = max(mod.shape[1] for mod in obs_models)  # widest outcome set

    states = [f"s{i}" for i in range(n)] + ["done"]
    actions = [f"obs{j}" for j in range(k)] + [f"commit{i}" for i in range(n_commit)]
    observations = [f"o{j}" for j in range(m)] + ["onull"]

    lines: List[str] = []
    lines.append(f"discount: {discount}")
    lines.append("values: reward")
    lines.append("states: " + " ".join(states))
    lines.append("actions: " + " ".join(actions))
    lines.append("observations: " + " ".join(observations))
    start = [1.0 / n] * n + [0.0]
    lines.append("start: " + " ".join(f"{p:.10f}" for p in start))
    lines.append("")

    # Transitions: observation actions keep the state; commits absorb.
    for j in range(k):
        lines.append(f"T: obs{j} identity")
    for i in range(n_commit):
        for s in states:
            lines.append(f"T: commit{i} : {s} : done 1.0")
    lines.append("")

    # Observations: model row for obs actions from hidden states; null else.
    for j, model in enumerate(obs_models):
        for s in range(n):
            row = model[s]
            for o in range(model.shape[1]):
                if row[o] > 0:
                    lines.append(f"O: obs{j} : s{s} : o{o} {row[o]:.10f}")
        lines.append(f"O: obs{j} : done : onull 1.0")
    for i in range(n_commit):
        lines.append(f"O: commit{i} : * : onull 1.0")
    lines.append("")

    # Rewards: obs cost from hidden states; commit payoff by true state.
    for j in range(k):
        for s in range(n):
            lines.append(f"R: obs{j} : s{s} : * : * {-costs[j]:.10f}")
    for i in range(n_commit):
        for s in range(n):
            lines.append(f"R: commit{i} : s{s} : * : * {commit[i, s]:.10f}")
    lines.append("")

    path.write_text("\n".join(lines))
    return {"n_states": n, "n_commit": n_commit, "n_obs_actions": k, "n_outcomes": m}


def solve_sarsop(
    pomdp_path: Path,
    policy_path: Path,
    pomdpsol: Path,
    precision: float = 1e-3,
    timeout_s: int = 120,
) -> str:
    cmd = [
        str(pomdpsol),
        str(pomdp_path),
        "--precision", str(precision),
        "--timeout", str(timeout_s),
        "--output", str(policy_path),
    ]
    out = subprocess.run(cmd, capture_output=True, text=True, timeout=timeout_s + 60)
    if out.returncode != 0:
        raise RuntimeError(f"pomdpsol failed: {out.stdout}\n{out.stderr}")
    return out.stdout


def parse_policy(policy_path: Path) -> List[Tuple[int, np.ndarray]]:
    """Return [(action_index, alpha_vector_over_all_states), ...]."""
    root = ET.parse(policy_path).getroot()
    alphas = []
    for vec in root.iter("Vector"):
        action = int(vec.attrib["action"])
        values = np.array([float(x) for x in vec.text.split()])
        alphas.append((action, values))
    if not alphas:
        raise ValueError(f"No alpha vectors parsed from {policy_path}")
    return alphas


# ---------------------------------------------------------------------------
# Alpha-vector policy agent (plugs into run_otc_episode)
# ---------------------------------------------------------------------------

class AlphaVectorAgent(BaseAgent):
    """Executes a SARSOP alpha-vector policy with exact belief tracking."""

    def __init__(self, obs_models, env_config, alphas: List[Tuple[int, np.ndarray]]):
        super().__init__(obs_models, env_config)
        # Alpha vectors include the absorbing 'done' state; belief mass on
        # done is zero while the episode is live, so truncate.
        self.alphas = [(a, v[: self.num_states]) for a, v in alphas]

    def select_action(self) -> int:
        b = self.belief.belief
        best_action, best_val = 0, -float("inf")
        for action, vec in self.alphas:
            val = float(np.dot(vec, b))
            if val > best_val:
                best_val = val
                best_action = action
        return best_action


# ---------------------------------------------------------------------------
# Evaluation
# ---------------------------------------------------------------------------

def evaluate_agent(make_agent, env, seeds: Sequence[int], num_episodes: int) -> dict:
    per_seed_reward, per_seed_usage, per_seed_success = [], [], []
    for seed in seeds:
        np.random.seed(int(seed))
        env.reset(seed=int(seed))
        agent = make_agent()
        rewards, usages, succ = [], [], []
        for _ in range(num_episodes):
            r = run_otc_episode(agent, env)
            rewards.append(r["total_reward"])
            usages.append(r["num_observations"])
            succ.append(float(r["success"]))
        per_seed_reward.append(float(np.mean(rewards)))
        per_seed_usage.append(float(np.mean(usages)))
        per_seed_success.append(float(np.mean(succ)))

    def mse(xs):
        arr = np.asarray(xs)
        se = float(arr.std(ddof=1) / np.sqrt(len(arr))) if len(arr) > 1 else 0.0
        return float(arr.mean()), se

    r_m, r_se = mse(per_seed_reward)
    u_m, u_se = mse(per_seed_usage)
    s_m, _ = mse(per_seed_success)
    return {
        "reward": r_m, "reward_se": r_se,
        "usage": u_m, "usage_se": u_se,
        "success": s_m,
    }


def matched_weight_from_curves(env_name: str, target_usage: float) -> Optional[float]:
    """Usage-matched w for Planning+IG from the saved full-battery curves."""
    path = RESULTS / "results_price_usage_curves.csv"
    if not path.exists():
        return None
    df = pd.read_csv(path)
    sub = df[df["env"] == env_name].sort_values("w")
    if sub.empty:
        return None
    pts = [
        UsageCurvePoint(
            w=float(r["w"]),
            mean_usage=float(r["mean_usage"]),
            se_usage=float(r["se_usage"]),
            n_seeds=int(r["n_seeds"]),
            per_seed_means=[],
        )
        for _, r in sub.iterrows()
    ]
    br = crossing_bracket(pts, budget=float(target_usage))
    if br.bracketed:
        return float(br.w_hi)
    # Target below the floor or above the ceiling: nearest endpoint.
    if target_usage <= pts[0].mean_usage:
        return float(pts[0].w)
    return float(pts[-1].w)


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--pomdpsol", default=str(DEFAULT_POMDPSOL))
    p.add_argument("--precision", type=float, default=1e-3)
    p.add_argument("--seeds", type=int, nargs="*", default=[42, 123, 456, 789, 1024])
    p.add_argument("--episodes", type=int, default=500)
    p.add_argument("--envs", nargs="*", default=ENVS)
    args = p.parse_args()

    pomdpsol = Path(args.pomdpsol)
    if not pomdpsol.exists():
        raise SystemExit(
            f"pomdpsol not found at {pomdpsol}; run tools/build_sarsop.sh first"
        )
    POMDP_DIR.mkdir(parents=True, exist_ok=True)

    rows = []
    summary = {}
    for name in args.envs:
        cfg = get_benchmark(name)
        env = cfg.env_factory()
        pomdp_path = POMDP_DIR / f"{name.lower()}.pomdp"
        policy_path = POMDP_DIR / f"{name.lower()}.policy"

        info = write_pomdp_file(env, pomdp_path)
        print(f"\n=== {name}: exported {info} ===", flush=True)
        log = solve_sarsop(pomdp_path, policy_path, pomdpsol, precision=args.precision)
        tail = [ln for ln in log.strip().splitlines() if ln.strip()][-6:]
        print("\n".join(f"  {ln}" for ln in tail), flush=True)
        alphas = parse_policy(policy_path)
        print(f"  {len(alphas)} alpha vectors", flush=True)

        obs_models = get_obs_models(env)
        config = make_env_config(env)

        agents = {
            "SARSOP": lambda: AlphaVectorAgent(obs_models, config, alphas),
            "EFE (w=1)": lambda: make_otc_agent(
                "efe", env, planning_horizon=cfg.planning_horizon
            ),
        }
        results = {}
        for label, make_agent in agents.items():
            results[label] = evaluate_agent(make_agent, env, args.seeds, args.episodes)
            r = results[label]
            print(
                f"  {label:24s} reward {r['reward']:8.3f}±{r['reward_se']:.3f}  "
                f"usage {r['usage']:6.3f}±{r['usage_se']:.3f}  "
                f"success {r['success']:.3f}",
                flush=True,
            )

        # Usage-matched Planning+IG: weight whose usage curve crosses SARSOP's usage.
        w_match = matched_weight_from_curves(name, results["SARSOP"]["usage"])
        if w_match is not None:
            label = f"Planning+IG (w={w_match:.3g})"
            make_pig = lambda: make_otc_agent(
                "planning+ig", env, planning_horizon=cfg.planning_horizon,
                info_weight=float(w_match),
            )
            results[label] = evaluate_agent(make_pig, env, args.seeds, args.episodes)
            r = results[label]
            print(
                f"  {label:24s} reward {r['reward']:8.3f}±{r['reward_se']:.3f}  "
                f"usage {r['usage']:6.3f}±{r['usage_se']:.3f}  "
                f"success {r['success']:.3f}",
                flush=True,
            )

        for label, r in results.items():
            rows.append({"env": name, "agent": label, **r})
        summary[name] = {k: v for k, v in results.items()}

    df = pd.DataFrame(rows)
    out_csv = RESULTS / "results_sarsop_baseline.csv"
    df.to_csv(out_csv, index=False)
    print(f"\nSaved {out_csv}")
    with open(RESULTS / "results_sarsop_baseline.json", "w") as f:
        json.dump(summary, f, indent=2)
    print(df.to_string(index=False))


if __name__ == "__main__":
    main()
