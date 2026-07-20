"""Proposition 1: EFE and Planning+IG(w=1) must agree on actions."""

import numpy as np

from rho_aif.agents.efe import EFEAgent
from rho_aif.agents.planning_infogain import PlanningInfoGainAgent
from rho_aif.environments.diagnosis import DiagnosisEnv
from rho_aif.environments.tiger import TigerEnv
from run_experiment import make_agent


def test_efe_matches_pig_w1_on_random_beliefs_diagnosis():
    env = DiagnosisEnv(num_conditions=4)
    efe = make_agent(EFEAgent, env, planning_horizon=3)
    pig = make_agent(
        PlanningInfoGainAgent, env, planning_horizon=3, info_gain_weight=1.0
    )
    rng = np.random.RandomState(0)
    for _ in range(100):
        b = rng.dirichlet(np.ones(4))
        efe.belief.belief = b.copy()
        pig.belief.belief = b.copy()
        assert efe.select_action() == pig.select_action()


def test_efe_matches_pig_w1_on_tiger_uniform():
    env = TigerEnv()
    efe = make_agent(EFEAgent, env, planning_horizon=6)
    pig = make_agent(
        PlanningInfoGainAgent, env, planning_horizon=6, info_gain_weight=1.0
    )
    assert efe.select_action() == pig.select_action()
