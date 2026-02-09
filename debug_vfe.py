#!/usr/bin/env python3
"""Debug VFE agent to find the issue."""

import numpy as np
from run_experiment import (
    MinimalInfoSeekingEnv, EnvConfig, VFEAgent, 
    MyopicAgent, InformationGainAgent, run_episode
)
import sys

np.random.seed(42)

# Create environment
config = EnvConfig()
env = MinimalInfoSeekingEnv(config)

print("Testing VFE agent with verbose output...")
print("=" * 80)

# Test single episode with VFE
vfe_agent = VFEAgent(env)
env.reset()
vfe_agent.reset()

print(f"True state: {env.true_state}")
print(f"Initial belief: {vfe_agent.belief.belief}")
print()

episode_count = 0
max_steps = 20  # Safety limit

while not env.done and episode_count < max_steps:
    episode_count += 1
    print(f"Step {episode_count}:")
    print(f"  Current belief: {vfe_agent.belief.belief}")
    print(f"  Current entropy: {vfe_agent.belief.entropy():.4f}")
    
    # Time the action selection
    import time
    start = time.time()
    action = vfe_agent.select_action()
    elapsed = time.time() - start
    
    print(f"  Action selected: {action.name} (took {elapsed:.4f}s)")
    
    if elapsed > 2.0:
        print(f"  WARNING: Action selection taking too long!")
        print(f"  Debugging EFE calculation...")
        commit_efe = vfe_agent._expected_free_energy_commit()
        print(f"    Commit EFE: {commit_efe:.4f}")
        sys.stdout.flush()
        observe_efe = vfe_agent._expected_free_energy_observe()
        print(f"    Observe EFE: {observe_efe:.4f}")
        break
    
    obs, reward, done = env.step(action)
    print(f"  Observation: {obs}, Reward: {reward:.2f}, Done: {done}")
    
    if not done:
        vfe_agent.update_belief(obs)
    
    print()
    sys.stdout.flush()

if episode_count >= max_steps:
    print("Reached maximum steps without termination")
else:
    print(f"Episode completed in {episode_count} steps")
    print(f"Total reward: {env.total_reward:.2f}")
    print(f"Success: {env.true_state == vfe_agent.belief.most_likely_state()}")

print("\n" + "=" * 80)
print("Now testing 10 full episodes to measure speed...")
print("=" * 80)

import time
start_time = time.time()

for i in range(10):
    result = run_episode(vfe_agent, env)
    elapsed = time.time() - start_time
    print(f"Episode {i+1}/10: {result.num_observations} obs, {result.success}, {elapsed:.2f}s total", flush=True)

print(f"\nAverage time per episode: {elapsed/10:.3f}s")
print("If this is slow, there's a performance issue with VFE agent.")
