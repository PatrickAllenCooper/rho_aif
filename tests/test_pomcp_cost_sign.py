"""POMCPAgent must charge observation costs with the environment's sign.

The environments pay ``-cost`` per observation and every other planner
subtracts ``obs_costs``. POMCP maximizes return, so both its tree step and
its rollout must add ``-cost`` (ledger 9.17.57: the planner previously added
``+cost``, a sensing subsidy of twice the cost per observation).
"""
import numpy as np

from rho_aif.agents.pomcp import POMCPAgent, POMCPNode
from rho_aif.environments.tiger import TigerEnv


class _NoEarlyCommitRNG(np.random.RandomState):
    def random(self, *args, **kwargs):
        return 0.99


def _agent(listen_accuracy=0.5, listen_cost=1.0):
    from run_experiment import make_agent
    env = TigerEnv(listen_accuracy=listen_accuracy, listen_cost=listen_cost,
                   correct_reward=10.0, incorrect_penalty=-100.0)
    return make_agent(POMCPAgent, env, num_simulations=1, rollout_depth=1,
                      exploration_constant=5.0)


def test_environment_charges_negative_listen_cost():
    env = TigerEnv(listen_accuracy=0.85, listen_cost=1.0,
                   correct_reward=10.0, incorrect_penalty=-100.0)
    env.reset(seed=0)
    _, r, _, _, _ = env.step(0)
    assert r == -1.0


def test_tree_step_subtracts_observation_cost():
    a = _agent(listen_cost=1.0)
    node = POMCPNode()
    node.visit_count = 1
    state = 0
    ret = a._simulate(node, state, depth=0)
    assert ret == -1.0 + a._best_commit_reward(state)


def test_rollout_subtracts_observation_cost():
    a = _agent(listen_accuracy=0.5, listen_cost=1.0)
    a._rng = _NoEarlyCommitRNG(0)
    _, commit_r = a._best_commit_from_belief(a.belief.belief.copy())
    assert a._rollout(state=0, depth=0) == -1.0 + commit_r
