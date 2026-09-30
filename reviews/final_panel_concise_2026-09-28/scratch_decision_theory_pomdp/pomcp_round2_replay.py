"""Round-2 lineage replay: reproduce two POMCP(1000) rows of results_pomcp.csv
from the fixed simulator under run_pomcp.py's exact configuration."""
import sys, time
sys.path.insert(0, '.'); sys.path.insert(0, 'experiments')
from run_experiment import run_experiment_multi_seed, summarize_results, SEEDS
from rho_aif.agents.pomcp import POMCPAgent
from rho_aif.environments import TigerEnv, BanditEnv
envs = {
 "Tiger": (TigerEnv(listen_accuracy=0.85, listen_cost=1.0, correct_reward=10.0, incorrect_penalty=-100.0), 6),
 "Bandit": (BanditEnv(num_arms=4, inspect_accuracy=0.80, inspect_cost=0.5, correct_reward=10.0, small_reward=1.0), 2),
}
for name,(env,h) in envs.items():
    t0=time.time()
    raw = run_experiment_multi_seed(POMCPAgent, env, 1000, seeds=SEEDS, vary_agent_seed=True, num_simulations=1000, rollout_depth=h+3)
    s = summarize_results(raw)
    print(name, f"success={s['success_rate']:.4f} reward={s['mean_reward']:.4f} obs={s['mean_observations']:.4f} se_r={s['se_reward_seed_level']:.4f} se_s={s['se_success_seed_level']:.4f} ({time.time()-t0:.0f}s)", flush=True)
