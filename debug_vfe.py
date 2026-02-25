#!/usr/bin/env python3
"""Debug and profile VFE agent behavior step-by-step."""

import sys
import time
import numpy as np

from environments.info_seeking import InfoSeekingEnv
from environments.tiger import TigerEnv
from agents.vfe import VFEAgent
from run_experiment import make_agent, run_episode


def debug_episode(env, agent_kwargs=None, label=""):
    agent_kwargs = agent_kwargs or {}
    agent = make_agent(VFEAgent, env, **agent_kwargs)
    obs, info = env.reset(seed=42)
    agent.reset()

    print(f"{'=' * 60}")
    print(f"VFE Debug: {label}")
    print(f"{'=' * 60}")
    print(f"True state: {info}")
    print(f"Initial belief: {agent.belief.belief}")
    print()

    total_reward = 0.0
    for step in range(30):
        t0 = time.time()
        action = agent.select_action()
        dt = time.time() - t0

        print(f"Step {step + 1}:")
        print(f"  Belief: {agent.belief.belief}  (H={agent.belief.entropy():.3f})")
        print(f"  Action: {action}  ({dt:.4f}s)")

        obs, reward, terminated, truncated, info = env.step(action)
        total_reward += reward
        print(f"  Obs: {obs}  Reward: {reward:+.1f}")

        if terminated:
            print(f"\nEpisode done. Total reward: {total_reward:+.1f}")
            print(f"Correct: {info.get('correct', 'N/A')}")
            return
        agent.update_belief(obs)
        print()


if __name__ == "__main__":
    debug_episode(InfoSeekingEnv(), {"planning_horizon": 4}, "Info-Seeking")
    print("\n\n")
    debug_episode(TigerEnv(), {"planning_horizon": 6}, "Tiger Problem")
