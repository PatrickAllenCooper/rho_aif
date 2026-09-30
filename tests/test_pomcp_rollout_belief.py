"""POMCPAgent rollouts start from the belief of the simulated history.

A leaf reached by an observe action must be rolled out from the posterior
after that observation (ledger 9.17.57). The legacy ``rollout_belief="root"``
mode started every rollout from the root belief.
"""
import numpy as np
import pytest

from rho_aif.agents.pomcp import POMCPAgent, POMCPNode
from rho_aif.environments.tiger import TigerEnv


def _agent(**kw):
    from run_experiment import make_agent
    env = TigerEnv(listen_accuracy=0.85, listen_cost=1.0,
                   correct_reward=10.0, incorrect_penalty=-100.0)
    return make_agent(POMCPAgent, env, num_simulations=1, rollout_depth=3,
                      exploration_constant=5.0, **kw)


def _captured_rollout_belief(agent):
    seen = {}

    def fake_rollout(state, depth, belief=None):
        seen["belief"] = np.array(belief, dtype=float)
        seen["depth"] = depth
        return 0.0

    agent._rollout = fake_rollout
    node = POMCPNode()
    node.visit_count = 1
    agent._rng = np.random.RandomState(0)
    agent._simulate(node, 0, depth=0)
    return seen


def test_rollout_starts_from_path_posterior():
    a = _agent()
    root = a.belief.belief.copy()
    seen = _captured_rollout_belief(a)
    assert seen["depth"] == 1
    posteriors = []
    for o in range(a.obs_models[0].shape[1]):
        p = root * a.obs_models[0][:, o]
        posteriors.append(p / p.sum())
    assert any(np.allclose(seen["belief"], p) for p in posteriors)
    assert not np.allclose(seen["belief"], root)


def test_root_mode_keeps_legacy_behavior():
    a = _agent(rollout_belief="root")
    root = a.belief.belief.copy()
    seen = _captured_rollout_belief(a)
    assert np.allclose(seen["belief"], root)


def test_rejects_unknown_rollout_belief():
    with pytest.raises(ValueError):
        _agent(rollout_belief="bogus")
