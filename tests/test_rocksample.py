"""Tests for the RockSample environment and agents."""

import numpy as np
import pytest
from rho_aif.environments.rocksample import RockSampleEnv
from rho_aif.agents.rocksample_agents import (
    RockSampleTreeSearchAgent,
    RockSampleGreedyAgent,
    RockSampleFlatMCAgent,
)


class TestRockSampleInterface:
    def test_action_space(self):
        env = RockSampleEnv(grid_size=5, num_rocks=3)
        assert env.action_space.n == 4 + 3 + 2  # move + check + sample + exit

    def test_observation_space(self):
        env = RockSampleEnv(grid_size=5, num_rocks=3)
        assert env.observation_space.n == 3

    def test_reset(self):
        env = RockSampleEnv(grid_size=5, num_rocks=3)
        obs, info = env.reset(seed=42)
        assert obs == 2  # null
        assert "agent_pos" in info
        assert "rock_positions" in info
        assert len(info["rock_positions"]) == 3

    def test_deterministic_reset(self):
        env = RockSampleEnv(grid_size=5, num_rocks=3)
        _, info1 = env.reset(seed=42)
        _, info2 = env.reset(seed=42)
        assert info1["rock_positions"] == info2["rock_positions"]
        np.testing.assert_array_equal(
            info1["rock_qualities"], info2["rock_qualities"]
        )

    def test_move_changes_position(self):
        env = RockSampleEnv(grid_size=5, num_rocks=2,
                            rock_positions=[(0, 0), (4, 4)])
        env.reset(seed=42)
        start = env._agent_pos
        env.step(env.MOVE_E)  # move east
        assert env._agent_pos[1] == min(start[1] + 1, 4)

    def test_boundary_clamping(self):
        env = RockSampleEnv(grid_size=5, num_rocks=2,
                            rock_positions=[(0, 0), (4, 4)])
        env.reset(seed=42)
        for _ in range(10):
            env.step(env.MOVE_N)  # keep moving north
        assert env._agent_pos[0] == 0

    def test_check_returns_binary(self):
        env = RockSampleEnv(grid_size=5, num_rocks=3)
        env.reset(seed=42)
        obs, _, _, _, _ = env.step(4)  # check rock 0
        assert obs in (0, 1)

    def test_sample_good_rock(self):
        env = RockSampleEnv(grid_size=5, num_rocks=2,
                            rock_positions=[(2, 0), (4, 4)])
        env.reset(seed=42)
        env._rock_qualities = np.array([1, 0])
        env._agent_pos = (2, 0)
        _, reward, _, _, _ = env.step(env.sample_action)
        assert reward == pytest.approx(10.0)

    def test_sample_bad_rock(self):
        env = RockSampleEnv(grid_size=5, num_rocks=2,
                            rock_positions=[(2, 0), (4, 4)])
        env.reset(seed=42)
        env._rock_qualities = np.array([0, 1])
        env._agent_pos = (2, 0)
        _, reward, _, _, _ = env.step(env.sample_action)
        assert reward == pytest.approx(-10.0)

    def test_sample_empty_cell(self):
        env = RockSampleEnv(grid_size=5, num_rocks=2,
                            rock_positions=[(0, 0), (4, 4)])
        env.reset(seed=42)
        env._agent_pos = (2, 2)
        _, reward, _, _, _ = env.step(env.sample_action)
        assert reward == pytest.approx(0.0)

    def test_exit_terminates(self):
        env = RockSampleEnv(grid_size=5, num_rocks=2)
        env.reset(seed=42)
        _, reward, terminated, _, _ = env.step(env.exit_action)
        assert terminated is True
        assert reward == pytest.approx(10.0)

    def test_max_steps_truncation(self):
        env = RockSampleEnv(grid_size=5, num_rocks=2, max_steps=3)
        env.reset(seed=42)
        for _ in range(2):
            _, _, _, truncated, _ = env.step(env.MOVE_E)
            assert truncated is False
        _, _, _, truncated, _ = env.step(env.MOVE_E)
        assert truncated is True

    def test_rock_cannot_be_sampled_twice(self):
        env = RockSampleEnv(grid_size=5, num_rocks=2,
                            rock_positions=[(2, 0), (4, 4)])
        env.reset(seed=42)
        env._rock_qualities = np.array([1, 0])
        env._agent_pos = (2, 0)
        _, r1, _, _, _ = env.step(env.sample_action)
        assert r1 == pytest.approx(10.0)
        _, r2, _, _, _ = env.step(env.sample_action)
        assert r2 == pytest.approx(0.0)


class TestRockSampleCheckAccuracy:
    def test_close_check_is_accurate(self):
        env = RockSampleEnv(grid_size=5, num_rocks=1,
                            rock_positions=[(2, 2)],
                            check_base_accuracy=0.95)
        env.reset(seed=42)
        acc = env.get_check_accuracy_at((2, 2), 0)
        assert acc == pytest.approx(0.95)

    def test_far_check_is_less_accurate(self):
        env = RockSampleEnv(grid_size=10, num_rocks=1,
                            rock_positions=[(5, 5)],
                            half_efficiency_distance=4.0)
        env.reset(seed=42)
        acc_close = env.get_check_accuracy_at((5, 5), 0)
        acc_far = env.get_check_accuracy_at((0, 0), 0)
        assert acc_close > acc_far
        assert acc_far >= 0.5

    def test_accuracy_bounded(self):
        env = RockSampleEnv(grid_size=20, num_rocks=1,
                            rock_positions=[(0, 0)])
        env.reset(seed=42)
        for r in range(20):
            for c in range(20):
                acc = env.get_check_accuracy_at((r, c), 0)
                assert 0.5 <= acc <= env.check_base_accuracy


class TestRockSampleTreeSearch:
    @pytest.fixture
    def env(self):
        return RockSampleEnv(
            grid_size=5, num_rocks=2,
            rock_positions=[(2, 2), (3, 4)],
            move_cost=-0.5, max_steps=30,
        )

    def test_tree_search_returns_valid_action(self, env):
        env.reset(seed=42)
        agent = RockSampleTreeSearchAgent(env, info_weight=1.0, max_depth=2)
        agent.reset()
        action = agent.select_action()
        assert 0 <= action < env.num_actions

    def test_tree_search_planning_only(self, env):
        env.reset(seed=42)
        agent = RockSampleTreeSearchAgent(env, info_weight=0.0, max_depth=2)
        agent.reset()
        action = agent.select_action()
        assert 0 <= action < env.num_actions

    def test_tree_search_completes_episode(self, env):
        env.reset(seed=42)
        agent = RockSampleTreeSearchAgent(env, info_weight=1.0, max_depth=2)
        agent.reset()
        total_reward = 0.0
        for _ in range(30):
            action = agent.select_action()
            obs, reward, terminated, truncated, info = env.step(action)
            total_reward += reward
            agent.update(action, obs)
            if terminated or truncated:
                break
        assert terminated or truncated

    def test_efe_avoids_bad_rocks(self, env):
        """EFE agent should sample fewer bad rocks than greedy over many episodes."""
        np.random.seed(42)
        efe_bads, greedy_bads = 0, 0
        n_eps = 50
        for ep in range(n_eps):
            env.reset(seed=ep * 100)
            agent = RockSampleTreeSearchAgent(env, info_weight=1.0, max_depth=2)
            agent.reset()
            for _ in range(30):
                action = agent.select_action()
                obs, reward, terminated, truncated, info = env.step(action)
                agent.update(action, obs)
                if terminated or truncated:
                    break
            efe_bads += info.get("total_bad_sampled", 0)

            env.reset(seed=ep * 100)
            agent = RockSampleGreedyAgent(env)
            agent.reset()
            for _ in range(30):
                action = agent.select_action()
                obs, reward, terminated, truncated, info = env.step(action)
                agent.update(action, obs)
                if terminated or truncated:
                    break
            greedy_bads += info.get("total_bad_sampled", 0)

        assert efe_bads <= greedy_bads

    def test_efe_outperforms_planning_on_rs53(self):
        """EFE (w=1) should achieve higher reward than Planning (w=0) on RS[5,3]."""
        env = RockSampleEnv(
            grid_size=5, num_rocks=3,
            rock_positions=[(1, 2), (3, 1), (2, 4)],
            move_cost=-0.5, max_steps=60,
        )
        np.random.seed(42)
        n_eps = 30

        def run_agent(w):
            rewards = []
            for ep in range(n_eps):
                env.reset(seed=42 * 10000 + ep)
                agent = RockSampleTreeSearchAgent(env, info_weight=w, max_depth=3)
                agent.reset()
                total_reward = 0.0
                for _ in range(60):
                    action = agent.select_action()
                    obs, reward, terminated, truncated, info = env.step(action)
                    total_reward += reward
                    agent.update(action, obs)
                    if terminated or truncated:
                        break
                rewards.append(total_reward)
            return np.mean(rewards)

        efe_reward = run_agent(1.0)
        planning_reward = run_agent(0.0)
        assert efe_reward > planning_reward

    def test_pomcp_no_longer_exits_immediately(self):
        """Verify POMCP fix: agent should take more than 1 step."""
        env = RockSampleEnv(
            grid_size=5, num_rocks=3,
            rock_positions=[(1, 2), (3, 1), (2, 4)],
            move_cost=-0.5, max_steps=60,
        )
        env.reset(seed=42)
        agent = RockSampleFlatMCAgent(env, num_simulations=200)
        agent.reset()
        steps = 0
        for _ in range(60):
            action = agent.select_action()
            obs, reward, terminated, truncated, info = env.step(action)
            agent.update(action, obs)
            steps += 1
            if terminated or truncated:
                break
        assert steps > 1
