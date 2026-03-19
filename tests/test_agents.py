"""Tests for agent action selection and EFE computation."""

import numpy as np
import pytest

from agents.myopic import MyopicAgent
from agents.info_gain import InformationGainAgent
from agents.efe import EFEAgent
from agents.planning import PlanningAgent


class TestMyopicAgent:
    def test_commits_immediately_when_confident(self, info_obs_model, info_config):
        agent = MyopicAgent(info_obs_model, info_config)
        agent.belief.reset(initial_belief=np.array([0.95, 0.05]))
        action = agent.select_action()
        assert action in (1, 2)

    def test_observes_or_commits_at_uniform(self, info_obs_model, info_config):
        """At uniform belief with symmetric rewards and low obs cost,
        myopic should find observing marginally worthwhile or commit."""
        agent = MyopicAgent(info_obs_model, info_config)
        action = agent.select_action()
        assert action in (0, 1, 2)

    def test_commit_action_matches_belief(self, info_obs_model, info_config):
        agent = MyopicAgent(info_obs_model, info_config)
        agent.belief.reset(initial_belief=np.array([0.9, 0.1]))
        action = agent.select_action()
        if action != 0:
            assert action == 1  # COMMIT_A since state 0 most likely


class TestInformationGainAgent:
    def test_observes_at_uniform_belief(self, info_obs_model, info_config):
        """Info gain agent should observe when belief is fully uncertain."""
        agent = InformationGainAgent(info_obs_model, info_config, info_gain_weight=1.0)
        action = agent.select_action()
        assert action == 0  # OBSERVE

    def test_commits_when_very_confident(self, info_obs_model, info_config):
        agent = InformationGainAgent(info_obs_model, info_config, info_gain_weight=1.0)
        agent.belief.reset(initial_belief=np.array([0.99, 0.01]))
        action = agent.select_action()
        assert action == 1  # COMMIT_A

    def test_higher_weight_increases_exploration(self, info_obs_model, info_config):
        """Higher info_gain_weight should make the agent explore more."""
        agent_low = InformationGainAgent(info_obs_model, info_config, info_gain_weight=0.1)
        agent_high = InformationGainAgent(info_obs_model, info_config, info_gain_weight=2.0)
        agent_low.belief.reset(initial_belief=np.array([0.8, 0.2]))
        agent_high.belief.reset(initial_belief=np.array([0.8, 0.2]))
        action_low = agent_low.select_action()
        action_high = agent_high.select_action()
        if action_low != 0:
            assert action_high == 0 or action_high == action_low

    def test_commit_direction_matches_belief(self, info_obs_model, info_config):
        agent = InformationGainAgent(info_obs_model, info_config, info_gain_weight=1.0)
        agent.belief.reset(initial_belief=np.array([0.01, 0.99]))
        action = agent.select_action()
        if action != 0:
            assert action == 2  # COMMIT_B


class TestEFEAgent:
    def test_observes_at_uniform_belief(self, info_obs_model, info_config):
        """EFE agent should observe when belief is maximally uncertain."""
        agent = EFEAgent(info_obs_model, info_config, planning_horizon=4)
        action = agent.select_action()
        assert action == 0  # OBSERVE

    def test_commits_when_very_confident(self, info_obs_model, info_config):
        agent = EFEAgent(info_obs_model, info_config, planning_horizon=4)
        agent.belief.reset(initial_belief=np.array([0.99, 0.01]))
        action = agent.select_action()
        assert action == 1  # COMMIT_A

    def test_no_epistemic_weight_parameter(self, info_obs_model, info_config):
        """EFE agent should not accept epistemic_weight as a parameter."""
        with pytest.raises(TypeError):
            EFEAgent(info_obs_model, info_config, epistemic_weight=0.5)

    def test_commit_direction_matches_belief(self, info_obs_model, info_config):
        agent = EFEAgent(info_obs_model, info_config, planning_horizon=4)
        agent.belief.reset(initial_belief=np.array([0.01, 0.99]))
        action = agent.select_action()
        if action != 0:
            assert action == 2  # COMMIT_B

    def test_explores_more_than_myopic(self, info_obs_model, info_config):
        """EFE agent should explore more than myopic at intermediate beliefs."""
        myopic = MyopicAgent(info_obs_model, info_config)
        vfe = EFEAgent(info_obs_model, info_config, planning_horizon=4)
        belief = np.array([0.75, 0.25])
        myopic.belief.reset(initial_belief=belief)
        vfe.belief.reset(initial_belief=belief)
        myopic_action = myopic.select_action()
        vfe_action = vfe.select_action()
        if myopic_action != 0:
            assert vfe_action == 0


class TestPlanningAgent:
    """Multi-step reward-only agent -- controls for planning depth vs EFE."""

    def test_observes_at_uniform_on_tiger(self, tiger_obs_model, tiger_config):
        """With multi-step planning on Tiger, the agent should see that
        observing first leads to higher expected reward."""
        agent = PlanningAgent(tiger_obs_model, tiger_config, planning_horizon=6)
        action = agent.select_action()
        assert action == 0  # LISTEN

    def test_commits_when_very_confident(self, info_obs_model, info_config):
        agent = PlanningAgent(info_obs_model, info_config, planning_horizon=4)
        agent.belief.reset(initial_belief=np.array([0.99, 0.01]))
        action = agent.select_action()
        assert action == 1  # COMMIT_A

    def test_same_horizon_as_vfe(self, info_obs_model, info_config):
        """PlanningAgent accepts the same planning_horizon parameter as EFE."""
        for h in [2, 4, 6]:
            agent = PlanningAgent(info_obs_model, info_config, planning_horizon=h)
            assert agent.planning_horizon == h

    def test_no_epistemic_weight(self, info_obs_model, info_config):
        """PlanningAgent should not accept epistemic_weight."""
        with pytest.raises(TypeError):
            PlanningAgent(info_obs_model, info_config, epistemic_weight=0.5)

    def test_commit_direction_matches_belief(self, info_obs_model, info_config):
        agent = PlanningAgent(info_obs_model, info_config, planning_horizon=4)
        agent.belief.reset(initial_belief=np.array([0.01, 0.99]))
        action = agent.select_action()
        if action != 0:
            assert action == 2  # COMMIT_B

    def test_explores_less_than_vfe_on_tiger(self, tiger_obs_model, tiger_config):
        """At intermediate belief on Tiger, PlanningAgent should commit
        sooner than EFE because it lacks intrinsic epistemic value."""
        planning = PlanningAgent(tiger_obs_model, tiger_config, planning_horizon=6)
        vfe = EFEAgent(tiger_obs_model, tiger_config, planning_horizon=6)
        belief = np.array([0.85, 0.15])
        planning.belief.reset(initial_belief=belief)
        vfe.belief.reset(initial_belief=belief)
        planning_action = planning.select_action()
        vfe_action = vfe.select_action()
        if planning_action != 0:
            assert vfe_action == 0


class TestEFEOnTiger:
    """EFE agent behavior on the Tiger problem specifically."""

    def test_observes_at_uniform(self, tiger_obs_model, tiger_config):
        agent = EFEAgent(tiger_obs_model, tiger_config, planning_horizon=6)
        action = agent.select_action()
        assert action == 0  # LISTEN

    def test_still_observes_after_one_listen(self, tiger_obs_model, tiger_config):
        """With +10/-100 asymmetry, one observation is not enough."""
        agent = EFEAgent(tiger_obs_model, tiger_config, planning_horizon=6)
        agent.belief.reset(initial_belief=np.array([0.85, 0.15]))
        action = agent.select_action()
        assert action == 0  # LISTEN

    def test_commits_when_highly_confident(self, tiger_obs_model, tiger_config):
        agent = EFEAgent(tiger_obs_model, tiger_config, planning_horizon=6)
        agent.belief.reset(initial_belief=np.array([0.995, 0.005]))
        action = agent.select_action()
        assert action != 0


class TestAgentBeliefIntegration:
    """Test that agents properly update beliefs and adapt behavior."""

    def test_belief_updates_change_action(self, info_obs_model, info_config):
        agent = EFEAgent(info_obs_model, info_config, planning_horizon=4)
        assert agent.select_action() == 0  # Should observe initially
        for _ in range(10):
            agent.update_belief(0)
        assert agent.select_action() != 0  # Should commit after many updates

    def test_reset_restores_initial_behavior(self, info_obs_model, info_config):
        agent = EFEAgent(info_obs_model, info_config, planning_horizon=4)
        initial_action = agent.select_action()
        for _ in range(5):
            agent.update_belief(0)
        agent.reset()
        assert agent.select_action() == initial_action
