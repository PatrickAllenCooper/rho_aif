"""Read-only referee check: same-stream Diagnosis comparison of Planning+IG(w=0.316)
against the saved SARSOP lam=0 policy on fresh seeds with per-episode seeding.
Writes only to this scratch directory."""
import sys, time
sys.path.insert(0, '/Users/pat/code/rho_aif'); sys.path.insert(0, '/Users/pat/code/rho_aif/experiments')
import numpy as np, pandas as pd
from rho_aif.benchmark import get_benchmark, get_obs_models, make_env_config, run_otc_episode
from rho_aif.budget import _obs_costs_from_env
from run_sarsop_baseline import AlphaVectorAgent, parse_policy
from run_frontier_reference_heldout import POMDP_DIR, episode_seed
from run_budget_frontier import run_weight
seeds = [int(x) for x in sys.argv[1].split(',')]; n_ep = int(sys.argv[2]); tag = sys.argv[3]
cfg = get_benchmark('Diagnosis'); env = cfg.env_factory()
obs_models, config, costs = get_obs_models(env), make_env_config(env), _obs_costs_from_env(env)
alphas = parse_policy(POMDP_DIR / 'diagnosis_lam0.policy')
agent = AlphaVectorAgent(obs_models, config, alphas)
t0=time.time()
ref_u, ref_r = [], []
for s in seeds:
    su, sr = [], []
    for ep in range(n_ep):
        res = run_otc_episode(agent, env, seed=episode_seed(s, ep))
        su.append(res['num_observations']); sr.append(float(res['total_reward']))
    ref_u.append(np.mean(su)); ref_r.append(np.mean(sr))
print('ref done', time.time()-t0, flush=True)
fam_u, fam_r = run_weight(env, 0.316227766, cfg.planning_horizon, seeds, n_ep)
print('fam done', time.time()-t0, flush=True)
df = pd.DataFrame(dict(seed=seeds, ref_u=ref_u, ref_r=ref_r, fam_u=fam_u, fam_r=fam_r))
df['diff'] = df.fam_r - df.ref_r
print(df.to_string()); print('mean diff', df['diff'].mean(), 'se', df['diff'].std(ddof=1)/np.sqrt(len(df)))
df.to_csv(f'diag_check_{tag}.csv', index=False)
