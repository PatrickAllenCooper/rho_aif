"""Read-only referee check: Table tab:pomcp protocol (c=10, 1000 sims, rollout_depth=H+3,
per-run planner seed) with the observation-cost sign as coded versus corrected.
Reduced protocol: 5 canonical seeds x 40 episodes."""
import sys; sys.path.insert(0,'/Users/pat/code/rho_aif')
import numpy as np, pandas as pd
from rho_aif.benchmark import get_benchmark, get_obs_models, make_env_config, run_otc_episode
from rho_aif.agents.pomcp import POMCPAgent
rows = []
for name in ['Tiger','Diagnosis','Bandit']:
    cfg = get_benchmark(name); env = cfg.env_factory(); om, conf = get_obs_models(env), make_env_config(env)
    depth = cfg.planning_horizon + 3
    for label, sign in [('as-coded(+cost)', +1.0), ('corrected(-cost)', -1.0)]:
        seed_u, seed_r, seed_s = [], [], []
        for s in [42,123,456,789,1024]:
            agent = POMCPAgent(om, conf, num_simulations=1000, exploration_constant=10.0, rollout_depth=depth, seed=s)
            agent.obs_costs = [sign*x for x in agent.obs_costs]
            us, rs, sc = [], [], []
            for ep in range(40):
                res = run_otc_episode(agent, env, seed=s*10000+ep)
                us.append(res['num_observations']); rs.append(res['total_reward']); sc.append(float(res['success']))
            seed_u.append(np.mean(us)); seed_r.append(np.mean(rs)); seed_s.append(np.mean(sc))
        rows.append(dict(env=name, H=cfg.planning_horizon, rollout_depth=depth, variant=label, usage=np.mean(seed_u), reward=np.mean(seed_r), reward_se=np.std(seed_r,ddof=1)/np.sqrt(5), success=np.mean(seed_s), success_se=np.std(seed_s,ddof=1)/np.sqrt(5)))
        print(rows[-1], flush=True)
pd.DataFrame(rows).to_csv('pomcp_sign_table.csv', index=False)
print(pd.DataFrame(rows).round(3).to_string())
