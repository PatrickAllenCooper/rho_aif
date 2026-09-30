"""Read-only referee check: does the OTC POMCP simulator add or subtract observation cost?"""
import sys; sys.path.insert(0,'/Users/pat/code/rho_aif')
import numpy as np
from rho_aif.benchmark import get_benchmark, get_obs_models, make_env_config, run_otc_episode
from rho_aif.agents.pomcp import POMCPAgent
for name in ['Tiger','Bandit']:
    cfg = get_benchmark(name); env = cfg.env_factory()
    om, conf = get_obs_models(env), make_env_config(env)
    print(name, 'obs costs in config:', conf['observation_costs'])
    for label, sign in [('as-coded', +1.0), ('negated', -1.0)]:
        agent = POMCPAgent(om, conf, num_simulations=500, seed=42)
        agent.obs_costs = [sign*c for c in agent.obs_costs]
        us, rs, sc = [], [], []
        for ep in range(60):
            res = run_otc_episode(agent, env, seed=70000+ep)
            us.append(res['num_observations']); rs.append(res['total_reward']); sc.append(float(res['success']))
        print(f'  {label:9s} usage {np.mean(us):.2f} reward {np.mean(rs):.2f} success {np.mean(sc):.2f}')
