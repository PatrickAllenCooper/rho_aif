import sys
from pathlib import Path
ROOT = Path('/Users/pat/code/rho_aif'); sys.path.insert(0, str(ROOT)); sys.path.insert(0, str(ROOT/'experiments'))
import numpy as np
from rho_aif.agents.planning_infogain import PlanningInfoGainAgent
from rho_aif.benchmark import get_benchmark, get_obs_models, make_env_config, run_otc_episode
cfg = get_benchmark('Tiger'); env = cfg.env_factory()
agent = PlanningInfoGainAgent(get_obs_models(env), make_env_config(env), planning_horizon=cfg.planning_horizon, info_gain_weight=0.0)
for label, seeds in [('heldout', [7,8,9,10,11]), ('calibration', [42,123,456,789,1024])]:
    wrong = 0; n = 0; rewards = []
    for s in seeds:
        for ep in range(100):
            res = run_otc_episode(agent, env, seed=int(s)*10_000+ep)
            n += 1; rewards.append(res['total_reward'])
            if not res.get('success', res.get('correct', True)): wrong += 1
    print(label, 'episodes', n, 'wrong commits', wrong, 'mean reward', np.mean(rewards), 'keys', sorted(res.keys())[:12])
