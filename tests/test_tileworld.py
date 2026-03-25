"""Tests for the Tileworld environment."""

import unittest
import numpy as np
import pytest
from environments.tileworld import TileworldEnv
from agents.myopic import MyopicAgent
from agents.planning import PlanningAgent
from agents.info_gain import InformationGainAgent
from agents.efe import EFEAgent
from agents.epistemic_only import EpistemicOnlyAgent
from run_experiment import make_agent, run_episode


class TestTileworldInterface:
    def test_action_space(self):
        env = TileworldEnv(grid_size=4)
        assert env.action_space.n == 4 + 16  # 4 scans + 16 commit

    def test_action_space_6x6(self):
        env = TileworldEnv(grid_size=6)
        assert env.action_space.n == 6 + 36

    def test_observation_space(self):
        env = TileworldEnv(grid_size=4)
        assert env.observation_space.n == 3  # group_A, group_B, null

    def test_reset_returns_null_obs(self):
        env = TileworldEnv(grid_size=4)
        obs, info = env.reset(seed=42)
        assert obs == 2
        assert 0 <= info["target_cell"] < 16
        assert 0 <= info["target_row"] < 4
        assert 0 <= info["target_col"] < 4

    def test_reset_deterministic(self):
        env = TileworldEnv(grid_size=4)
        _, info_a = env.reset(seed=42)
        _, info_b = env.reset(seed=42)
        assert info_a["target_cell"] == info_b["target_cell"]

    def test_scan_returns_binary_obs(self):
        env = TileworldEnv(grid_size=4)
        env.reset(seed=42)
        obs, reward, term, trunc, info = env.step(0)
        assert obs in (0, 1)
        assert reward == pytest.approx(-1.0)
        assert term is False
        assert trunc is False

    def test_commit_correct(self):
        env = TileworldEnv(grid_size=4)
        env.reset(seed=42)
        target = env._target_cell
        action = env.num_scans + target
        _, reward, term, _, info = env.step(action)
        assert reward == pytest.approx(10.0)
        assert term is True
        assert info["correct"] is True

    def test_commit_incorrect(self):
        env = TileworldEnv(grid_size=4)
        env.reset(seed=42)
        wrong_cell = (env._target_cell + 1) % env.num_cells
        action = env.num_scans + wrong_cell
        _, reward, term, _, info = env.step(action)
        assert reward == pytest.approx(-50.0)
        assert term is True
        assert info["correct"] is False

    def test_scan_count_increments(self):
        env = TileworldEnv(grid_size=4)
        env.reset(seed=42)
        for i in range(3):
            _, _, _, _, info = env.step(i % env.num_scans)
            assert info["scan_count"] == i + 1


class TestTileworldObservationModels:
    def test_model_count_matches_scans(self):
        env = TileworldEnv(grid_size=4)
        models = env.get_observation_models()
        assert len(models) == env.num_scans

    def test_model_shape(self):
        env = TileworldEnv(grid_size=4)
        for model in env.get_observation_models():
            assert model.shape == (16, 2)

    def test_rows_sum_to_one(self):
        for gs in [4, 6, 8]:
            env = TileworldEnv(grid_size=gs)
            for model in env.get_observation_models():
                for row in model:
                    np.testing.assert_almost_equal(row.sum(), 1.0)

    def test_perfect_accuracy_partition(self):
        env = TileworldEnv(grid_size=4, scan_accuracy=1.0)
        models = env.get_observation_models()
        m0 = models[0]  # row bit 0: even rows vs odd rows
        for cell in range(16):
            row = cell // 4
            if row % 2 == 0:
                assert m0[cell, 0] == pytest.approx(1.0)
            else:
                assert m0[cell, 1] == pytest.approx(1.0)

    def test_partitions_cover_all_cells(self):
        env = TileworldEnv(grid_size=4)
        for k in range(env.num_scans):
            mask = env.get_scan_mask(k)
            assert mask.shape == (4, 4)
            assert mask.sum() > 0
            assert mask.sum() < 16

    @pytest.mark.parametrize("gs", [4, 6, 8])
    def test_scans_distinguish_all_cells(self, gs):
        """Each cell must have a unique fingerprint across all scans."""
        env = TileworldEnv(grid_size=gs)
        fingerprints = set()
        for cell in range(env.num_cells):
            row, col = env._cell_to_rc(cell)
            fp = tuple(env._scan_bit(k, row, col) for k in range(env.num_scans))
            fingerprints.add(fp)
        assert len(fingerprints) == env.num_cells

    def test_observation_costs_list(self):
        env = TileworldEnv(grid_size=4, scan_cost=2.5)
        costs = env.get_observation_costs()
        assert len(costs) == env.num_scans
        assert all(c == pytest.approx(2.5) for c in costs)

    def test_commit_reward_matrix_shape(self):
        env = TileworldEnv(grid_size=4)
        mat = env.get_commit_reward_matrix()
        assert mat.shape == (16, 16)
        assert mat[0, 0] == pytest.approx(10.0)
        assert mat[0, 1] == pytest.approx(-50.0)

    @pytest.mark.parametrize("gs", [4, 6, 8])
    def test_scan_count_correct(self, gs):
        env = TileworldEnv(grid_size=gs)
        import math
        expected = 2 * max(1, math.ceil(math.log2(gs)))
        assert env.num_scans == expected


class TestTileworldScanDescriptions:
    def test_descriptions_exist(self):
        env = TileworldEnv(grid_size=6)
        for k in range(env.num_scans):
            desc = env.get_scan_description(k)
            assert isinstance(desc, str)
            assert len(desc) > 0

    def test_row_scan_label(self):
        env = TileworldEnv(grid_size=4)
        desc = env.get_scan_description(0)
        assert "Row scan" in desc

    def test_col_scan_label(self):
        env = TileworldEnv(grid_size=4)
        desc = env.get_scan_description(env.num_row_bits)
        assert "Col scan" in desc


class TestTileworldAgents:
    def test_myopic_episode_completes(self):
        np.random.seed(42)
        env = TileworldEnv(grid_size=4)
        agent = make_agent(MyopicAgent, env)
        result = run_episode(agent, env)
        assert result.success in (True, False)
        assert result.num_observations >= 0

    def test_efe_episode_completes(self):
        np.random.seed(42)
        env = TileworldEnv(grid_size=4)
        agent = make_agent(EFEAgent, env, planning_horizon=2)
        result = run_episode(agent, env)
        assert result.success in (True, False)
        assert result.num_observations >= 0

    def test_planning_episode_completes(self):
        np.random.seed(42)
        env = TileworldEnv(grid_size=4)
        agent = make_agent(PlanningAgent, env, planning_horizon=2)
        result = run_episode(agent, env)
        assert result.success in (True, False)

    def test_efe_observes_at_uniform(self):
        np.random.seed(42)
        env = TileworldEnv(grid_size=4)
        agent = make_agent(EFEAgent, env, planning_horizon=2)
        agent.reset()
        action = agent.select_action()
        assert action < env.num_scans

    def test_efe_outperforms_myopic(self):
        np.random.seed(42)
        env = TileworldEnv(grid_size=4)
        n_episodes = 100

        myopic_agent = make_agent(MyopicAgent, env)
        efe_agent = make_agent(EFEAgent, env, planning_horizon=2)

        myopic_success = sum(
            run_episode(myopic_agent, env).success for _ in range(n_episodes)
        )
        efe_success = sum(
            run_episode(efe_agent, env).success for _ in range(n_episodes)
        )
        assert efe_success > myopic_success

    def test_all_agents_run_on_6x6(self):
        np.random.seed(42)
        env = TileworldEnv(grid_size=6)
        for cls, kwargs in [
            (MyopicAgent, {}),
            (PlanningAgent, {"planning_horizon": 2}),
            (InformationGainAgent, {"info_gain_weight": 1.0}),
            (EFEAgent, {"planning_horizon": 2}),
        ]:
            agent = make_agent(cls, env, **kwargs)
            result = run_episode(agent, env)
            assert result.success in (True, False)


class TestPartitionModes(unittest.TestCase):

    def test_bitwise_default(self):
        env = TileworldEnv(grid_size=4, partition_mode="bitwise")
        assert env.partition_mode == "bitwise"
        assert env._partition_assignments.shape == (env.num_scans, env.num_cells)

    def test_random_mode_creates_valid_partitions(self):
        env = TileworldEnv(grid_size=6, partition_mode="random", partition_seed=42)
        for scan_idx in range(env.num_scans):
            assignments = env._partition_assignments[scan_idx]
            assert set(np.unique(assignments)) <= {0, 1}
            half = env.num_cells // 2
            assert np.sum(assignments == 0) == half
            assert np.sum(assignments == 1) == env.num_cells - half

    def test_overlapping_mode_creates_valid_partitions(self):
        env = TileworldEnv(grid_size=6, partition_mode="overlapping", partition_seed=42)
        for scan_idx in range(env.num_scans):
            assignments = env._partition_assignments[scan_idx]
            assert set(np.unique(assignments)) <= {0, 1}
        total_ones = env._partition_assignments.sum()
        assert total_ones > 0, "At least some cells should be in group 1"

    def test_random_differs_from_bitwise(self):
        env_bit = TileworldEnv(grid_size=6, partition_mode="bitwise")
        env_rnd = TileworldEnv(grid_size=6, partition_mode="random", partition_seed=42)
        assert not np.array_equal(
            env_bit._partition_assignments, env_rnd._partition_assignments
        )

    def test_observation_models_match_partitions(self):
        env = TileworldEnv(grid_size=4, partition_mode="random", partition_seed=99)
        models = env.get_observation_models()
        acc = env.scan_accuracy
        for scan_idx in range(env.num_scans):
            for cell in range(env.num_cells):
                bit = env._partition_assignments[scan_idx, cell]
                if bit == 0:
                    np.testing.assert_allclose(models[scan_idx][cell], [acc, 1 - acc])
                else:
                    np.testing.assert_allclose(models[scan_idx][cell], [1 - acc, acc])

    def test_random_seed_reproducibility(self):
        env1 = TileworldEnv(grid_size=6, partition_mode="random", partition_seed=42)
        env2 = TileworldEnv(grid_size=6, partition_mode="random", partition_seed=42)
        np.testing.assert_array_equal(
            env1._partition_assignments, env2._partition_assignments
        )

    def test_all_modes_run_episode(self):
        np.random.seed(42)
        for mode in ["bitwise", "random", "overlapping"]:
            env = TileworldEnv(grid_size=4, partition_mode=mode, partition_seed=42)
            agent = make_agent(EFEAgent, env, planning_horizon=2)
            result = run_episode(agent, env)
            assert result.success in (True, False)

    def test_invalid_mode_raises(self):
        with self.assertRaises(ValueError):
            TileworldEnv(grid_size=4, partition_mode="invalid")
