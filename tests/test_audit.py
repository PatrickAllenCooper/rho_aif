"""Section 4.3: per-test value-of-information audit trail.

Verifies the optional, backward-compatible ``record_audit`` instrumentation
on ``PlanningInfoGainAgent``, ``EFEAgent``, and ``InspectionTreeSearchAgent``:
audit logging must not change action selection, and the selected action must
always maximize the recorded total score.
"""

import numpy as np
import pytest

from rho_aif.agents.efe import EFEAgent
from rho_aif.agents.planning_infogain import PlanningInfoGainAgent
from rho_aif.agents.inspection_agents import InspectionTreeSearchAgent
from rho_aif.benchmark import get_benchmark, get_obs_models, make_env_config
from rho_aif.environments.diagnosis import DiagnosisEnv
from rho_aif.environments.tiger import TigerEnv


def _otc_agents(env, agent_cls, **kwargs):
    obs_models = get_obs_models(env)
    config = make_env_config(env)
    plain = agent_cls(obs_models, config, record_audit=False, **kwargs)
    audited = agent_cls(obs_models, config, record_audit=True, **kwargs)
    return plain, audited


class TestPlanningInfoGainAudit:
    def test_audit_disabled_by_default(self):
        env = DiagnosisEnv(num_conditions=4)
        obs_models = get_obs_models(env)
        config = make_env_config(env)
        agent = PlanningInfoGainAgent(obs_models, config, planning_horizon=3, info_gain_weight=1.0)
        assert agent.record_audit is False
        agent.select_action()
        assert agent.audit_log == []

    def test_audit_logging_does_not_alter_actions_diagnosis(self):
        env = DiagnosisEnv(num_conditions=4)
        plain, audited = _otc_agents(
            env, PlanningInfoGainAgent, planning_horizon=3, info_gain_weight=3.0
        )
        rng = np.random.RandomState(1)
        for _ in range(50):
            b = rng.dirichlet(np.ones(4))
            plain.belief.belief = b.copy()
            audited.belief.belief = b.copy()
            assert plain.select_action() == audited.select_action()

    def test_selected_action_maximizes_recorded_total_score(self):
        env = DiagnosisEnv(num_conditions=4)
        _, audited = _otc_agents(
            env, PlanningInfoGainAgent, planning_horizon=3, info_gain_weight=3.0
        )
        rng = np.random.RandomState(2)
        for _ in range(50):
            b = rng.dirichlet(np.ones(4))
            audited.belief.belief = b.copy()
            audited.select_action()
        assert len(audited.audit_log) == 50
        for decision in audited.audit_log:
            chosen = decision.chosen_candidate()
            assert chosen.total_score >= decision.max_total_score() - 1e-9
            # Exactly one candidate marked chosen.
            assert sum(1 for c in decision.candidates if c.chosen) == 1

    def test_record_decomposes_additively(self):
        """total_score == expected_task_value + weighted_info_gain for observe
        candidates, and weighted_info_gain == info_gain_weight * expected_info_gain."""
        env = TigerEnv()
        _, audited = _otc_agents(env, PlanningInfoGainAgent, planning_horizon=4, info_gain_weight=2.5)
        audited.select_action()
        decision = audited.audit_log[0]
        for c in decision.candidates:
            assert c.weighted_info_gain == pytest.approx(c.info_gain_weight * c.expected_info_gain)
            assert c.total_score == pytest.approx(c.expected_task_value + c.weighted_info_gain)
            if c.kind == "commit":
                assert c.expected_info_gain == 0.0
                assert c.sensing_cost == 0.0


class TestEFEAudit:
    def test_audit_logging_does_not_alter_actions_tiger(self):
        env = TigerEnv()
        plain, audited = _otc_agents(env, EFEAgent, planning_horizon=6)
        assert plain.select_action() == audited.select_action()

    def test_selected_action_maximizes_recorded_total_score(self):
        env = DiagnosisEnv(num_conditions=4)
        _, audited = _otc_agents(env, EFEAgent, planning_horizon=3)
        rng = np.random.RandomState(3)
        for _ in range(30):
            b = rng.dirichlet(np.ones(4))
            audited.belief.belief = b.copy()
            audited.select_action()
        for decision in audited.audit_log:
            chosen = decision.chosen_candidate()
            assert chosen.total_score >= decision.max_total_score() - 1e-9

    def test_efe_and_planning_ig_w1_share_audit_schema(self):
        """EFE's -G recovers exactly the Planning+IG(w=1) total_score at the
        chosen action, confirming the two families share one record format."""
        env = DiagnosisEnv(num_conditions=4)
        obs_models = get_obs_models(env)
        config = make_env_config(env)
        efe = EFEAgent(obs_models, config, planning_horizon=3, record_audit=True)
        pig = PlanningInfoGainAgent(
            obs_models, config, planning_horizon=3, info_gain_weight=1.0, record_audit=True
        )
        rng = np.random.RandomState(4)
        for _ in range(20):
            b = rng.dirichlet(np.ones(4))
            efe.belief.belief = b.copy()
            pig.belief.belief = b.copy()
            a_efe = efe.select_action()
            a_pig = pig.select_action()
            assert a_efe == a_pig
            efe_chosen = efe.audit_log[-1].chosen_candidate()
            pig_chosen = pig.audit_log[-1].chosen_candidate()
            assert efe_chosen.total_score == pytest.approx(pig_chosen.total_score, abs=1e-9)


class TestInspectionAudit:
    def _agent_on_component(self, env, agent):
        """Advance until the agent stands on an undiagnosed component's cell."""
        agent.reset()
        for _ in range(30):
            comp_idx = env.component_at_position(env._agent_pos)
            if comp_idx is not None and not agent.belief.diagnosed[comp_idx]:
                return
            action = agent.select_action()
            obs, _, terminated, truncated, _ = env.step(action)
            agent.update(action, obs)
            if terminated or truncated:
                env.reset(seed=123)
                agent.reset()

    def test_audit_disabled_by_default(self):
        cfg = get_benchmark("Inspection-N8")
        env = cfg.env_factory()
        env.reset(seed=7)
        agent = InspectionTreeSearchAgent(env, info_weight=1.0, max_depth=cfg.tree_depth)
        agent.select_action()
        assert agent.audit_log == []

    def test_audit_logging_does_not_alter_actions(self):
        cfg = get_benchmark("Inspection-N8")
        env = cfg.env_factory()
        env.reset(seed=7)
        plain = InspectionTreeSearchAgent(env, info_weight=2.0, max_depth=cfg.tree_depth)
        audited = InspectionTreeSearchAgent(env, info_weight=2.0, max_depth=cfg.tree_depth, record_audit=True)
        for _ in range(15):
            assert plain.select_action() == audited.select_action()
            action = audited.select_action()
            obs, _, terminated, truncated, _ = env.step(action)
            plain.update(action, obs)
            audited.update(action, obs)
            if terminated or truncated:
                break

    def test_selected_action_maximizes_recorded_total_score_when_on_component(self):
        cfg = get_benchmark("Inspection-N8")
        env = cfg.env_factory()
        env.reset(seed=7)
        agent = InspectionTreeSearchAgent(env, info_weight=2.0, max_depth=cfg.tree_depth, record_audit=True)
        self._agent_on_component(env, agent)
        agent.select_action()
        decision = agent.audit_log[-1]
        chosen = decision.chosen_candidate()
        assert chosen.total_score >= decision.max_total_score() - 1e-9
        kinds = {c.kind for c in decision.candidates}
        assert "observe" in kinds or "commit" in kinds

    def test_reward_only_planning_never_pays_weighted_info_gain(self):
        cfg = get_benchmark("Inspection-N8")
        env = cfg.env_factory()
        env.reset(seed=7)
        agent = InspectionTreeSearchAgent(env, info_weight=0.0, max_depth=cfg.tree_depth, record_audit=True)
        self._agent_on_component(env, agent)
        agent.select_action()
        decision = agent.audit_log[-1]
        for c in decision.candidates:
            assert c.weighted_info_gain == 0.0
