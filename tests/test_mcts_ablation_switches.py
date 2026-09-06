"""The ablation switches added for the confirmation-round experiments.

MCTSEFEAgent(backup=, in_tree_info_gain=) and POMCPAgent(rollout_policy=)
must (a) default to the manuscript's configuration, (b) reject bad values,
(c) run end to end, and (d) do what they say: mean backup averages sampled
returns, the no-IG switch zeroes the in-tree epistemic reward, and the
information-gain rollout picks the most informative observation action.
"""
import numpy as np
import pytest

from rho_aif.agents.mcts_efe import MCTSEFEAgent, MCTSNode
from rho_aif.agents.pomcp import POMCPAgent
from rho_aif.environments.tiger import TigerEnv


def _tiger():
    return TigerEnv(listen_accuracy=0.85, listen_cost=1.0, correct_reward=10.0, incorrect_penalty=-100.0)


def _obs_models(env):
    return env.get_observation_models() if hasattr(env, "get_observation_models") else env.observation_models


def _make(cls, env, **kw):
    from run_experiment import make_agent
    return make_agent(cls, env, **kw)


def test_defaults_are_the_manuscript_configuration():
    env = _tiger()
    a = _make(MCTSEFEAgent, env, num_simulations=20, planning_horizon=3, rollout_depth=2)
    assert a.backup == "max" and a.in_tree_info_gain is True
    p = _make(POMCPAgent, env, num_simulations=20, rollout_depth=4, exploration_constant=5.0)
    assert p.rollout_policy == "uniform"


def test_bad_switch_values_are_rejected():
    env = _tiger()
    with pytest.raises(ValueError):
        _make(MCTSEFEAgent, env, backup="median")
    with pytest.raises(ValueError):
        _make(POMCPAgent, env, rollout_policy="oracle")


@pytest.mark.parametrize("backup,ig", [("max", True), ("mean", True), ("max", False), ("mean", False)])
def test_every_variant_runs_an_episode(backup, ig):
    env = _tiger()
    np.random.seed(0)
    a = _make(MCTSEFEAgent, env, num_simulations=30, planning_horizon=3, rollout_depth=2,
              backup=backup, in_tree_info_gain=ig)
    env.reset(seed=0)
    a.reset()
    for _ in range(10):
        act = a.select_action()
        assert 0 <= act < a.num_observe_actions + a.num_commit_actions
        obs, r, done, trunc, info = env.step(act)
        if done or trunc:
            break
        a.update_belief(obs, obs_action=act)


def _one_simulation_root(a, seed=1):
    a.reset()
    root = MCTSNode(belief=a.belief.belief.copy())
    a._expand(root)
    np.random.seed(seed)
    a._simulate(root, depth=0)
    return root


def test_max_backup_takes_the_best_child_and_mean_backup_averages_the_sampled_return():
    env = _tiger()
    a_max = _make(MCTSEFEAgent, env, num_simulations=1, planning_horizon=2, rollout_depth=1, backup="max")
    a_mean = _make(MCTSEFEAgent, env, num_simulations=1, planning_horizon=2, rollout_depth=1, backup="mean")
    root_max = _one_simulation_root(a_max)
    assert root_max.mean_value == pytest.approx(max(c.mean_value for c in root_max.children.values()))
    root_mean = _one_simulation_root(a_mean)
    # One simulation visited exactly one child (the same one under both
    # agents, same seed); with mean backup the root carries that child's
    # sampled return, not the best child's value.
    visited = [c for c in root_mean.children.values() if not c.is_terminal and c.visit_count > 0]
    if visited:
        assert root_mean.mean_value == pytest.approx(visited[0].mean_value)
        assert root_mean.mean_value <= max(c.mean_value for c in root_mean.children.values()) + 1e-12
    assert root_mean.visit_count == root_max.visit_count == 1


def test_no_tree_ig_removes_the_epistemic_reward_from_observe_edges():
    env = _tiger()
    with_ig = _make(MCTSEFEAgent, env, num_simulations=1, planning_horizon=1, rollout_depth=0, in_tree_info_gain=True)
    without = _make(MCTSEFEAgent, env, num_simulations=1, planning_horizon=1, rollout_depth=0, in_tree_info_gain=False)
    vals = []
    for a in (with_ig, without):
        a.reset()
        root = MCTSNode(belief=a.belief.belief.copy())
        a._expand(root)
        np.random.seed(2)
        a._simulate(root, depth=0)
        listen = root.children[0]
        vals.append(listen.mean_value)
    # Same sampled outcome (same seed), same cost and continuation, so the
    # difference is exactly the one-step information gain of listening.
    ig = with_ig._one_step_info_gain(0, with_ig.belief.belief)
    assert ig > 0
    assert vals[0] - vals[1] == pytest.approx(ig, abs=1e-9)


def test_info_gain_rollout_picks_the_informative_observation():
    # Two observation actions: index 1 is the Tiger listen model, index 0 is
    # uninformative (identical rows). The informed rollout must pick 1.
    env = _tiger()
    p = _make(POMCPAgent, env, num_simulations=5, rollout_depth=3, rollout_policy="info_gain")
    informative = p.obs_models[0]
    flat = np.full_like(informative, 1.0 / informative.shape[1])
    p.obs_models = [flat, informative]
    p.num_observe_actions = 2
    b = np.array([0.5, 0.5])
    assert p._max_info_gain_action(b) == 1
    assert p._one_step_info_gain(0, b) == pytest.approx(0.0, abs=1e-12)
    assert p._one_step_info_gain(1, b) > 0
