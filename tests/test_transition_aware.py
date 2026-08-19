"""DS-C tests for the transition-aware agents (design doc Section 8).

Three predeclared obligations from
docs/ideation/2026-08-19-destructive-sensing-design.md:

(a) The w=1 exact-equivalence mirror of tests/test_efe_pig_equivalence.py
    between TransitionAwareEFEAgent and TransitionAwarePlanningIGAgent on
    the destructive testbed (DS-C acceptance: exact agreement within 1e-12
    tie-breaking).
(b) A regression test reproducing the paper's Example ex:destructive
    ranking flip with the example's exact numbers (paper/full_paper_jair.tex):
    V_naive(a_D) = 2 - c, V_true(a_D) = 1 - c, flip on c in (1, 2).
(c) The delta = 0 reduction: with an identity kernel the transition-aware
    agents agree action-for-action with the state-preserving EFEAgent /
    PlanningInfoGainAgent on a belief grid.
"""

import numpy as np
import pytest

from rho_aif.agents.efe import EFEAgent
from rho_aif.agents.planning_infogain import PlanningInfoGainAgent
from rho_aif.agents.transition_aware import (
    TransitionAwareEFEAgent,
    TransitionAwarePlanningIGAgent,
)
from rho_aif.environments.destructive_testbed import (
    DestructiveTestbedEnv,
    OBS_READS_FAULTY,
    OBS_READS_HEALTHY,
    TEST,
)
from run_experiment import make_agent


# ---------------------------------------------------------------------------
# (a) w=1 equivalence between the two transition-aware agents
#     (mirror of tests/test_efe_pig_equivalence.py).
# ---------------------------------------------------------------------------


def test_ta_efe_matches_ta_pig_w1_on_random_beliefs_destructive():
    env = DestructiveTestbedEnv(
        accuracy=0.85, destruction_prob=0.2, alpha=5.0, test_cost=0.3
    )
    t_models = env.get_transition_models()
    efe = make_agent(
        TransitionAwareEFEAgent, env, transition_models=t_models, planning_horizon=3
    )
    pig = make_agent(
        TransitionAwarePlanningIGAgent,
        env,
        transition_models=t_models,
        planning_horizon=3,
        info_gain_weight=1.0,
    )
    rng = np.random.RandomState(0)
    for _ in range(100):
        b = rng.dirichlet(np.ones(3))
        efe.belief.belief = b.copy()
        pig.belief.belief = b.copy()
        assert efe.select_action() == pig.select_action()


def test_ta_efe_matches_ta_pig_w1_second_parameterization():
    # A second point of the E1 grid (design doc Section 4): low accuracy,
    # heavy destruction, symmetric rewards.
    env = DestructiveTestbedEnv(
        accuracy=0.7, destruction_prob=0.4, alpha=1.0, test_cost=0.05
    )
    t_models = env.get_transition_models()
    efe = make_agent(
        TransitionAwareEFEAgent, env, transition_models=t_models, planning_horizon=4
    )
    pig = make_agent(
        TransitionAwarePlanningIGAgent,
        env,
        transition_models=t_models,
        planning_horizon=4,
        info_gain_weight=1.0,
    )
    rng = np.random.RandomState(1)
    for _ in range(100):
        b = rng.dirichlet(np.ones(3))
        efe.belief.belief = b.copy()
        pig.belief.belief = b.copy()
        assert efe.select_action() == pig.select_action()


def test_ta_efe_matches_ta_pig_w1_at_initial_belief():
    env = DestructiveTestbedEnv(
        accuracy=0.85, destruction_prob=0.1, alpha=1.0, test_cost=0.1
    )
    t_models = env.get_transition_models()
    b0 = env.get_initial_belief()
    efe = make_agent(
        TransitionAwareEFEAgent,
        env,
        transition_models=t_models,
        planning_horizon=4,
        initial_belief=b0,
    )
    pig = make_agent(
        TransitionAwarePlanningIGAgent,
        env,
        transition_models=t_models,
        planning_horizon=4,
        info_gain_weight=1.0,
        initial_belief=b0,
    )
    assert efe.select_action() == pig.select_action()


# ---------------------------------------------------------------------------
# (b) Regression: the paper's Example ex:destructive ranking flip, with the
#     example's exact matrices and numbers.
# ---------------------------------------------------------------------------

# Example ex:destructive setup (paper/full_paper_jair.tex): s in {0, 1},
# uniform prior b = (0.5, 0.5); commit reward r(Commit_i, s) = +1 if i = s
# else -1; one destructive drill a_D with cost c that perfectly reveals the
# PRE-transition state, O(o=s | s, a_D) = 1, and always depletes it
# afterward, T(s'=0 | s, a_D) = 1. Note the depleted condition here is the
# example's own state 0 (with live commit reward), not the testbed's
# zero-value DESTROYED state, so the agents are built from the example's
# matrices directly.

PAPER_OBS_MODELS = [np.eye(2)]
PAPER_TRANSITION_MODELS = [np.array([[1.0, 0.0], [1.0, 0.0]])]
PAPER_REWARDS = np.array([[1.0, -1.0], [-1.0, 1.0]])
PAPER_PRIOR = np.array([0.5, 0.5])
DRILL = 0  # the single observation action; commits are actions 1 and 2


def _paper_config(c: float) -> dict:
    return {
        "observation_costs": [c],
        "commit_reward_matrix": PAPER_REWARDS.copy(),
    }


def _paper_naive_agent(c: float) -> EFEAgent:
    agent = EFEAgent(
        [m.copy() for m in PAPER_OBS_MODELS], _paper_config(c), planning_horizon=2
    )
    agent.belief.belief = PAPER_PRIOR.copy()
    return agent


def _paper_aware_agent(c: float) -> TransitionAwareEFEAgent:
    agent = TransitionAwareEFEAgent(
        [m.copy() for m in PAPER_OBS_MODELS],
        _paper_config(c),
        transition_models=[t.copy() for t in PAPER_TRANSITION_MODELS],
        planning_horizon=2,
    )
    agent.belief.belief = PAPER_PRIOR.copy()
    return agent


class TestPaperExampleRegression:
    def test_naive_value_is_two_minus_c(self):
        # V_naive(a_D) = -c + 1 bit + 1 = 2 - c; EFE minimizes G = -V.
        # The state-preserving agent credits I(b) = 1 bit and a certain
        # correct commit after the (illusory) point-mass posterior.
        for c in [0.5, 1.1, 1.5, 1.9, 2.5]:
            naive = _paper_naive_agent(c)
            g, info_gain = naive._efe_observe(DRILL, PAPER_PRIOR.copy(), depth=0)
            assert info_gain == pytest.approx(1.0)  # one full illusory bit
            assert -g == pytest.approx(2.0 - c)

    def test_transition_aware_value_is_one_minus_c(self):
        # V_true(a_D) = -c + max_i r(Commit_i, 0) = 1 - c, with ZERO
        # epistemic value: the post-drill state is known to be depleted
        # regardless of the outcome (paper's transition-aware evaluation).
        for c in [0.5, 1.1, 1.5, 1.9, 2.5]:
            aware = _paper_aware_agent(c)
            g, info_gain = aware._efe_observe(DRILL, PAPER_PRIOR.copy(), depth=0)
            assert info_gain == pytest.approx(0.0)
            assert -g == pytest.approx(1.0 - c)

    def test_gap_is_exactly_one_bit_of_illusory_credit(self):
        # V_naive - V_true = (2 - c) - (1 - c) = 1 bit, for every cost.
        for c in [0.3, 1.0, 1.5, 1.9]:
            g_naive, _ = _paper_naive_agent(c)._efe_observe(
                DRILL, PAPER_PRIOR.copy(), depth=0
            )
            g_aware, _ = _paper_aware_agent(c)._efe_observe(
                DRILL, PAPER_PRIOR.copy(), depth=0
            )
            assert (-g_naive) - (-g_aware) == pytest.approx(1.0)

    def test_ranking_flip_for_cost_in_one_two(self):
        # For c in (1, 2): the state-preserving agent drills
        # (V_naive = 2 - c > 0 = commit value) while the transition-aware
        # agent commits immediately (V_true = 1 - c < 0) -- the paper's
        # full ranking flip.
        for c in [1.01, 1.1, 1.5, 1.9, 1.99]:
            naive = _paper_naive_agent(c)
            aware = _paper_aware_agent(c)
            assert naive.select_action() == DRILL
            assert aware.select_action() in (1, 2)  # a commit, not the drill

    def test_both_agents_agree_outside_the_flip_window(self):
        # c < 1: drilling is genuinely worth it (V_true = 1 - c > 0), so
        # both agents drill. c > 2: even the naive value is negative, so
        # both commit.
        naive, aware = _paper_naive_agent(0.5), _paper_aware_agent(0.5)
        assert naive.select_action() == DRILL
        assert aware.select_action() == DRILL

        naive, aware = _paper_naive_agent(2.5), _paper_aware_agent(2.5)
        assert naive.select_action() in (1, 2)
        assert aware.select_action() in (1, 2)

    def test_pig_w1_variants_reproduce_the_same_flip(self):
        # The additive-w formulation at w = 1 must tell the same story:
        # V_naive = 2 - c for the state-preserving Planning+IG,
        # V_true = 1 - c for the transition-aware one.
        c = 1.5
        pig_naive = PlanningInfoGainAgent(
            [m.copy() for m in PAPER_OBS_MODELS],
            _paper_config(c),
            planning_horizon=2,
            info_gain_weight=1.0,
        )
        pig_naive.belief.belief = PAPER_PRIOR.copy()
        v_naive, _ = pig_naive._expected_value_of_observe(
            DRILL, PAPER_PRIOR.copy(), depth=0
        )
        assert v_naive == pytest.approx(2.0 - c)
        assert pig_naive.select_action() == DRILL

        pig_aware = TransitionAwarePlanningIGAgent(
            [m.copy() for m in PAPER_OBS_MODELS],
            _paper_config(c),
            transition_models=[t.copy() for t in PAPER_TRANSITION_MODELS],
            planning_horizon=2,
            info_gain_weight=1.0,
        )
        pig_aware.belief.belief = PAPER_PRIOR.copy()
        v_aware, _ = pig_aware._expected_value_of_observe(
            DRILL, PAPER_PRIOR.copy(), depth=0
        )
        assert v_aware == pytest.approx(1.0 - c)
        assert pig_aware.select_action() in (1, 2)

    def test_joint_posterior_is_certain_depleted_for_both_outcomes(self):
        # b'_{o,T} = (1, 0) whichever outcome is observed; the naive update
        # after o = 1 is the disjoint point mass (0, 1) -- the maximal
        # coupling case of the paper's Delta_T discussion.
        aware = _paper_aware_agent(1.5)
        for o in (0, 1):
            aware.belief.belief = PAPER_PRIOR.copy()
            aware.update_belief(o, obs_action=DRILL)
            assert np.allclose(aware.belief.belief, [1.0, 0.0])

        naive = _paper_naive_agent(1.5)
        naive.update_belief(1, obs_action=DRILL)
        assert np.allclose(naive.belief.belief, [0.0, 1.0])


# ---------------------------------------------------------------------------
# (c) delta = 0 reduction: exact agreement with the state-preserving agents.
# ---------------------------------------------------------------------------


@pytest.mark.parametrize("accuracy,test_cost,alpha", [
    (0.85, 0.3, 5.0),
    (0.7, 0.1, 1.0),
])
def test_delta_zero_ta_efe_matches_state_preserving_efe(accuracy, test_cost, alpha):
    env = DestructiveTestbedEnv(
        accuracy=accuracy, destruction_prob=0.0, alpha=alpha, test_cost=test_cost
    )
    t_models = env.get_transition_models()
    assert np.array_equal(t_models[0], np.eye(3))

    sp = make_agent(EFEAgent, env, planning_horizon=3)
    ta = make_agent(
        TransitionAwareEFEAgent, env, transition_models=t_models, planning_horizon=3
    )
    rng = np.random.RandomState(7)
    for _ in range(100):
        b = rng.dirichlet(np.ones(3))
        sp.belief.belief = b.copy()
        ta.belief.belief = b.copy()
        assert sp.select_action() == ta.select_action()


@pytest.mark.parametrize("accuracy,test_cost,alpha", [
    (0.85, 0.3, 5.0),
    (0.7, 0.1, 1.0),
])
def test_delta_zero_ta_pig_matches_state_preserving_pig(accuracy, test_cost, alpha):
    env = DestructiveTestbedEnv(
        accuracy=accuracy, destruction_prob=0.0, alpha=alpha, test_cost=test_cost
    )
    t_models = env.get_transition_models()

    sp = make_agent(
        PlanningInfoGainAgent, env, planning_horizon=3, info_gain_weight=1.0
    )
    ta = make_agent(
        TransitionAwarePlanningIGAgent,
        env,
        transition_models=t_models,
        planning_horizon=3,
        info_gain_weight=1.0,
    )
    rng = np.random.RandomState(11)
    for _ in range(100):
        b = rng.dirichlet(np.ones(3))
        sp.belief.belief = b.copy()
        ta.belief.belief = b.copy()
        assert sp.select_action() == ta.select_action()


def test_delta_zero_update_belief_matches_observation_only_update():
    # The T_k belief update must collapse to the standard Bayesian update
    # when the kernel is the identity.
    env = DestructiveTestbedEnv(accuracy=0.8, destruction_prob=0.0)
    ta = make_agent(
        TransitionAwareEFEAgent, env, transition_models=env.get_transition_models()
    )
    sp = make_agent(EFEAgent, env)
    b = np.array([0.5, 0.5, 0.0])
    for obs in (OBS_READS_HEALTHY, OBS_READS_FAULTY):
        ta.belief.belief = b.copy()
        sp.belief.belief = b.copy()
        ta.update_belief(obs, obs_action=TEST)
        sp.update_belief(obs, obs_action=TEST)
        assert np.array_equal(ta.belief.belief, sp.belief.belief)


def test_default_transition_models_are_identity():
    # Omitting transition_models must behave exactly like the
    # state-preserving agent (identity kernel default).
    env = DestructiveTestbedEnv(accuracy=0.85, destruction_prob=0.2, test_cost=0.3)
    sp = make_agent(EFEAgent, env, planning_horizon=3)
    ta = make_agent(TransitionAwareEFEAgent, env, planning_horizon=3)
    rng = np.random.RandomState(3)
    for _ in range(50):
        b = rng.dirichlet(np.ones(3))
        sp.belief.belief = b.copy()
        ta.belief.belief = b.copy()
        assert sp.select_action() == ta.select_action()


# ---------------------------------------------------------------------------
# Agent belief updates under destruction (hand-computed, via update_belief).
# ---------------------------------------------------------------------------


def test_update_belief_hand_computed_under_destruction():
    # Same arithmetic as tests/test_destructive_testbed.py's posterior
    # checks, exercised through the agent's own update path:
    # p = 0.8, delta = 0.2, b = (0.5, 0.5, 0), o = OBS_READS_FAULTY
    #   -> b'_{o,T} = (0.18, 0.64, 0.18).
    env = DestructiveTestbedEnv(accuracy=0.8, destruction_prob=0.2)
    agent = make_agent(
        TransitionAwareEFEAgent,
        env,
        transition_models=env.get_transition_models(),
        initial_belief=env.get_initial_belief(),
    )
    agent.update_belief(OBS_READS_FAULTY, obs_action=TEST)
    assert np.allclose(agent.belief.belief, [0.18, 0.64, 0.18])

    # And o = OBS_READS_HEALTHY from the prior -> (0.72, 0.16, 0.12).
    agent.reset()
    assert np.allclose(agent.belief.belief, [0.5, 0.5, 0.0])
    agent.update_belief(OBS_READS_HEALTHY, obs_action=TEST)
    assert np.allclose(agent.belief.belief, [0.72, 0.16, 0.12])


def test_episode_smoke_transition_aware_on_testbed():
    # End-to-end: the transition-aware agent runs a seeded episode on the
    # testbed and terminates with a commit within the step budget.
    env = DestructiveTestbedEnv(
        accuracy=0.85, destruction_prob=0.1, alpha=1.0, test_cost=0.1
    )
    agent = make_agent(
        TransitionAwareEFEAgent,
        env,
        transition_models=env.get_transition_models(),
        planning_horizon=3,
        initial_belief=env.get_initial_belief(),
    )
    obs, info = env.reset(seed=42)
    agent.reset()
    terminated = False
    for _ in range(50):
        action = agent.select_action()
        obs, reward, terminated, _, info = env.step(action)
        if terminated:
            break
        agent.update_belief(obs, obs_action=action)
    assert terminated
    assert "correct" in info
