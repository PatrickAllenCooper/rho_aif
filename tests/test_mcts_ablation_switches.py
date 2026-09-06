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


def _one_simulation_root(a, seed=1, sims=1):
    a.reset()
    root = MCTSNode(belief=a.belief.belief.copy())
    a._expand(root)
    np.random.seed(seed)
    for _ in range(sims):
        a._simulate(root, depth=0)
    return root


def test_max_backup_takes_the_best_child_and_mean_backup_averages_sampled_returns():
    """Max backup must report the best child's value; mean backup must not.

    With enough simulations that a dominated child is visited, the two rules
    give different node values, which is the property the ablation switches.
    """
    env = _tiger()
    a_max = _make(MCTSEFEAgent, env, num_simulations=40, planning_horizon=2, rollout_depth=1, backup="max")
    a_mean = _make(MCTSEFEAgent, env, num_simulations=40, planning_horizon=2, rollout_depth=1, backup="mean")
    root_max = _one_simulation_root(a_max, sims=40)
    best_max = max(c.mean_value for c in root_max.children.values())
    assert root_max.mean_value == pytest.approx(best_max)

    root_mean = _one_simulation_root(a_mean, sims=40)
    best_mean = max(c.mean_value for c in root_mean.children.values())
    # Tiger's commit children carry -100 for the wrong door, so once forced
    # exploration visits one, the average over sampled returns is strictly
    # below the best child. That gap is exactly what max backup removes.
    assert root_mean.mean_value < best_mean - 1e-9
    assert root_mean.visit_count == root_max.visit_count == 40


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


def test_info_gain_rollout_actually_routes_through_the_informative_action():
    """The switch must change the rollout, not just the helper it calls.

    With an uninformative model at index 0 and Tiger's real model at index 1,
    the informed rollout must sample observations from index 1. Recording
    which action _sample_observation receives proves the rollout used it.
    """
    env = _tiger()
    seen = []

    def build(policy):
        p = _make(POMCPAgent, env, num_simulations=1, rollout_depth=4, rollout_policy=policy)
        informative = p.obs_models[0]
        flat = np.full_like(informative, 1.0 / informative.shape[1])
        p.obs_models = [flat, informative]
        p.num_observe_actions = 2
        p.obs_costs = np.array([p.obs_costs[0], p.obs_costs[0]])
        p.all_actions = list(range(p.num_observe_actions + p.num_commit_actions))
        real = p._sample_observation

        def spy(state, obs_action):
            seen.append(obs_action)
            return real(state, min(obs_action, 0)) if obs_action == 0 else real(state, 0)

        p._sample_observation = spy
        return p

    p = build("info_gain")
    p.reset()
    np.random.seed(0)
    p._rollout(state=0, depth=0)
    assert seen and set(seen) == {1}, f"informed rollout chose {set(seen)}, expected only the informative action"

    seen.clear()
    p2 = build("uniform")
    p2.reset()
    np.random.seed(0)
    p2._rollout(state=0, depth=0)
    assert seen, "uniform rollout took no observation"
    assert 0 in set(seen), "uniform rollout never sampled the uninformative action"
