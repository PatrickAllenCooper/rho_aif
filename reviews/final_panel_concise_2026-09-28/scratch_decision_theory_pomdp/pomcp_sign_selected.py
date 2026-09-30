"""Read-only referee check: POMCP at the manuscript's selected configurations with the
observation cost sign as coded (+cost) versus corrected (-cost). Reduced protocol:
5 canonical seeds x 40 episodes, per-run planner seed = outer seed."""
import sys; sys.path.insert(0,'/Users/pat/code/rho_aif')
import numpy as np, pandas as pd
from rho_aif.benchmark import get_benchmark, get_obs_models, make_env_config, run_otc_episode
from rho_aif.agents.pomcp import POMCPAgent
configs = [('Tiger', 50.0, 'uniform', 500, 10), ('Tiger', 10.0, 'uniform', 1000, 10),
           ('Diagnosis', 5.0, 'info_gain', 200, 5), ('Diagnosis', 10.0, 'uniform', 1000, 10),
           ('Bandit', 10.0, 'uniform', 1000, 10)]
rows = []
for name, c, roll, sims, H in configs:
    cfg = get_benchmark(name); env = cfg.env_factory(); om, conf = get_obs_models(env), make_env_config(env)
    for label, sign in [('as-coded(+cost)', +1.0), ('corrected(-cost)', -1.0)]:
        seed_u, seed_r, seed_s = [], [], []
        for s in [42,123,456,789,1024]:
            agent = POMCPAgent(om, conf, num_simulations=sims, exploration_constant=c, rollout_depth=H, seed=s, rollout_policy=roll)
            agent.obs_costs = [sign*x for x in agent.obs_costs]
            us, rs, sc = [], [], []
            for ep in range(40):
                res = run_otc_episode(agent, env, seed=s*10000+ep)
                us.append(res['num_observations']); rs.append(res['total_reward']); sc.append(float(res['success']))
            seed_u.append(np.mean(us)); seed_r.append(np.mean(rs)); seed_s.append(np.mean(sc))
        rows.append(dict(env=name, c=c, rollout=roll, sims=sims, H=H, variant=label, usage=np.mean(seed_u), reward=np.mean(seed_r), reward_se=np.std(seed_r,ddof=1)/np.sqrt(5), success=np.mean(seed_s), success_se=np.std(seed_s,ddof=1)/np.sqrt(5)))
        print(rows[-1], flush=True)
pd.DataFrame(rows).to_csv('pomcp_sign_selected.csv', index=False)
