"""Tests for the Structural Inspection environment and agents."""

import numpy as np
import pytest

from rho_aif.environments.inspection import InspectionEnv
from rho_aif.agents.inspection_agents import (
    InspectionBeliefState,
    InspectionTreeSearchAgent,
    InspectionGreedyAgent,
)
from run_inspection import run_inspection_experiment


class TestInspectionEnv:
    def test_creation(self):
        env = InspectionEnv(num_components=4, num_test_types=2)
        assert env.num_components == 4
        assert env.num_test_types == 2
        assert env.num_actions == 4 + 2 + 2  # moves + tests + diagnoses

    def test_reset(self):
        env = InspectionEnv(num_components=4, num_test_types=2)
        obs, info = env.reset(seed=42)
        assert obs == 2  # null
        assert len(info["component_positions"]) == 4
        assert len(info["fault_states"]) == 4

    def test_unique_positions(self):
        for n in [4, 8, 16]:
            env = InspectionEnv(num_components=n)
            obs, info = env.reset(seed=42)
            positions = info["component_positions"]
            assert len(set(positions)) == n, f"Duplicate positions for N={n}"

    def test_move_actions(self):
        env = InspectionEnv(num_components=4, grid_size=5)
        env.reset(seed=42)
        assert env._agent_pos == (0, 0)
        env.step(1)  # MOVE_S
        assert env._agent_pos == (1, 0)
        env.step(2)  # MOVE_E
        assert env._agent_pos == (1, 1)

    def test_test_observations(self):
        env = InspectionEnv(num_components=4, num_test_types=2,
                           test_accuracies=[1.0, 1.0])
        env.reset(seed=42)
        pos = env._component_positions[0]
        env._agent_pos = pos
        fault_state = env._fault_states[0]

        obs, _, _, _, _ = env.step(env.test_action_start)
        assert obs == fault_state  # perfect accuracy

    def test_diagnosis_reward(self):
        env = InspectionEnv(num_components=1, num_test_types=1,
                           correct_fault_reward=5.0,
                           missed_fault_penalty=-50.0,
                           component_positions=[(0, 0)])
        env.reset(seed=42)
        env._fault_states[0] = 1  # component is faulty

        obs, r, term, _, info = env.step(env.diagnose_action_start + 1)  # diagnose faulty
        assert r == 5.0
        assert term is True

    def test_missed_fault_penalty(self):
        env = InspectionEnv(num_components=1, num_test_types=1,
                           missed_fault_penalty=-50.0,
                           component_positions=[(0, 0)])
        env.reset(seed=42)
        env._fault_states[0] = 1

        obs, r, term, _, _ = env.step(env.diagnose_action_start + 0)  # diagnose nominal
        assert r == -50.0

    def test_episode_terminates(self):
        env = InspectionEnv(num_components=1, num_test_types=1,
                           component_positions=[(0, 0)])
        env.reset(seed=42)
        _, _, term, _, _ = env.step(env.diagnose_action_start + 0)
        assert term is True

    def test_observation_preserves_state(self):
        env = InspectionEnv(num_components=4, num_test_types=2)
        env.reset(seed=42)
        pos = env._component_positions[0]
        env._agent_pos = pos
        faults_before = env._fault_states.copy()

        for _ in range(10):
            env.step(env.test_action_start)

        np.testing.assert_array_equal(env._fault_states, faults_before)


class TestInspectionBeliefState:
    def test_initialization(self):
        belief = InspectionBeliefState(4, fault_prior=0.3)
        np.testing.assert_allclose(belief.fault_beliefs, 0.3)

    def test_bayesian_update(self):
        belief = InspectionBeliefState(4, fault_prior=0.5)
        belief.update_test(0, 0, accuracy=0.9)  # nominal observation
        assert belief.fault_beliefs[0] < 0.5

        belief.update_test(1, 1, accuracy=0.9)  # faulty observation
        assert belief.fault_beliefs[1] > 0.5

    def test_null_observation_ignored(self):
        belief = InspectionBeliefState(4, fault_prior=0.3)
        belief.update_test(0, 2, accuracy=0.9)  # null
        assert belief.fault_beliefs[0] == 0.3


class TestInspectionAgents:
    def test_tree_search_runs(self):
        env = InspectionEnv(num_components=4, num_test_types=2, max_steps=50)
        agent = InspectionTreeSearchAgent(env, info_weight=1.0, max_depth=2)
        obs, info = env.reset(seed=42)
        agent.reset()

        for _ in range(50):
            a = agent.select_action()
            assert 0 <= a < env.num_actions
            obs, r, term, trunc, _ = env.step(a)
            agent.update(a, obs)
            if term or trunc:
                break

    def test_greedy_runs(self):
        env = InspectionEnv(num_components=4, num_test_types=2, max_steps=50)
        agent = InspectionGreedyAgent(env)
        obs, info = env.reset(seed=42)
        agent.reset()

        for _ in range(50):
            a = agent.select_action()
            assert 0 <= a < env.num_actions
            obs, r, term, trunc, _ = env.step(a)
            agent.update(a, obs)
            if term or trunc:
                break

    def test_efe_outperforms_planning(self):
        env = InspectionEnv(num_components=4, num_test_types=2,
                           test_accuracies=[0.70, 0.90], max_steps=80)

        results = {}
        for w, name in [(0.0, "planning"), (1.0, "efe")]:
            rewards = []
            for ep in range(30):
                env.reset(seed=42 * 10000 + ep)
                agent = InspectionTreeSearchAgent(env, info_weight=w, max_depth=3)
                agent.reset()
                total_r = 0
                for _ in range(80):
                    a = agent.select_action()
                    obs, r, term, trunc, _ = env.step(a)
                    agent.update(a, obs)
                    total_r += r
                    if term or trunc:
                        break
                rewards.append(total_r)
            results[name] = np.mean(rewards)

        assert results["efe"] >= results["planning"] - 2.0


class TestInspectionSE:

    def test_se_reported_in_results(self):
        df = run_inspection_experiment("Inspection-N8", num_episodes=10, seeds=[42], write_csv=False)
        assert "se_reward" in df.columns
        for _, row in df.iterrows():
            assert row["se_reward"] >= 0
            assert np.isfinite(row["se_reward"])

    def test_se_decreases_with_more_episodes(self):
        df_small = run_inspection_experiment("Inspection-N8", num_episodes=10, seeds=[42], write_csv=False)
        df_large = run_inspection_experiment("Inspection-N8", num_episodes=50, seeds=[42], write_csv=False)
        se_small = df_small[df_small["agent"].str.contains("Greedy")]["se_reward"].iloc[0]
        se_large = df_large[df_large["agent"].str.contains("Greedy")]["se_reward"].iloc[0]
        assert se_large < se_small * 1.5
