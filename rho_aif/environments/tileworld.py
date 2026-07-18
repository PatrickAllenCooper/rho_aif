"""
Tileworld environment as a Gymnasium env.

A spatial POMDP on an N x N grid with a hidden target tile. The agent
scans regions of the grid to locate the tile, then commits to collecting
at a specific cell. Scans use bit-level spatial partitions of row and
column indices, directly generalizing the Diagnosis environment's
partition structure to two dimensions.

Supports scaling analysis from 4x4 (16 states) to 8x8+ (64+ states)
and varying numbers of scan actions.
"""

import gymnasium as gym
from gymnasium import spaces
import numpy as np
from typing import Optional, Tuple, Dict, Any, List
import math


class TileworldEnv(gym.Env):
    """
    Tile Search POMDP on an N x N grid.

    Hidden state: target tile location (one of N^2 cells).

    Action layout:
      0..K-1        = scan action k (observation action)
      K..K+N^2-1    = collect at cell i (commit action)

    Scan actions partition the grid spatially using bit-level splits of
    the row and column indices. The first ceil(log2(N)) scans split by
    row bits; the remaining ceil(log2(N)) scans split by column bits.
    Each scan returns a noisy binary signal indicating which spatial
    partition the target tile belongs to.
    """

    metadata = {"render_modes": []}

    def __init__(
        self,
        grid_size: int = 6,
        scan_accuracy: float = 0.80,
        scan_cost: float = 1.0,
        correct_reward: float = 10.0,
        incorrect_penalty: float = -50.0,
        num_scans: Optional[int] = None,
        partition_mode: str = "bitwise",
        partition_seed: int = 0,
    ):
        super().__init__()

        self.grid_size = grid_size
        self.num_cells = grid_size * grid_size
        self.scan_accuracy = scan_accuracy
        self.scan_cost = scan_cost
        self.correct_reward = correct_reward
        self.incorrect_penalty = incorrect_penalty
        self.partition_mode = partition_mode

        self.num_row_bits = max(1, math.ceil(math.log2(grid_size))) if grid_size > 1 else 1
        self.num_col_bits = max(1, math.ceil(math.log2(grid_size))) if grid_size > 1 else 1
        self.num_scans = num_scans or (self.num_row_bits + self.num_col_bits)

        self._partition_assignments = self._build_partitions(partition_seed)

        self.action_space = spaces.Discrete(self.num_scans + self.num_cells)
        self.observation_space = spaces.Discrete(3)  # 0=group_A, 1=group_B, 2=null

        self._target_cell: Optional[int] = None
        self._scan_count = 0
        self._obs_models = self._build_observation_models()

    @property
    def observation_cost(self) -> float:
        return self.scan_cost

    @property
    def observation_accuracy(self) -> float:
        return self.scan_accuracy

    def _cell_to_rc(self, cell_idx: int) -> Tuple[int, int]:
        return (cell_idx // self.grid_size, cell_idx % self.grid_size)

    def _rc_to_cell(self, row: int, col: int) -> int:
        return row * self.grid_size + col

    def _build_partitions(self, partition_seed: int) -> np.ndarray:
        """Build partition assignment matrix: shape (num_scans, num_cells).

        Each row is a binary vector assigning cells to group 0 or 1.
        """
        assignments = np.zeros((self.num_scans, self.num_cells), dtype=int)

        if self.partition_mode == "bitwise":
            for scan_idx in range(self.num_scans):
                for cell in range(self.num_cells):
                    row, col = self._cell_to_rc(cell)
                    if scan_idx < self.num_row_bits:
                        assignments[scan_idx, cell] = (row >> scan_idx) & 1
                    else:
                        bit_idx = scan_idx - self.num_row_bits
                        assignments[scan_idx, cell] = (col >> bit_idx) & 1

        elif self.partition_mode == "random":
            rng = np.random.RandomState(partition_seed)
            for scan_idx in range(self.num_scans):
                perm = rng.permutation(self.num_cells)
                half = self.num_cells // 2
                assignments[scan_idx, perm[:half]] = 0
                assignments[scan_idx, perm[half:]] = 1

        elif self.partition_mode == "overlapping":
            rng = np.random.RandomState(partition_seed)
            for scan_idx in range(self.num_scans):
                w_row = rng.randn()
                w_col = rng.randn()
                threshold = rng.randn() * 0.5
                for cell in range(self.num_cells):
                    row, col = self._cell_to_rc(cell)
                    norm_r = row / max(self.grid_size - 1, 1)
                    norm_c = col / max(self.grid_size - 1, 1)
                    val = w_row * norm_r + w_col * norm_c
                    assignments[scan_idx, cell] = 1 if val > threshold else 0
        else:
            raise ValueError(f"Unknown partition_mode: {self.partition_mode}")

        return assignments

    def _build_observation_models(self) -> List[np.ndarray]:
        """Build one observation model per scan from partition assignments."""
        models = []
        acc = self.scan_accuracy

        for scan_idx in range(self.num_scans):
            model = np.zeros((self.num_cells, 2))
            for cell in range(self.num_cells):
                bit = self._partition_assignments[scan_idx, cell]
                if bit == 0:
                    model[cell] = [acc, 1.0 - acc]
                else:
                    model[cell] = [1.0 - acc, acc]
            models.append(model)

        return models

    def _scan_bit(self, scan_idx: int, row: int, col: int) -> int:
        """Determine which partition group a cell belongs to for a given scan."""
        cell = self._rc_to_cell(row, col)
        return int(self._partition_assignments[scan_idx, cell])

    def get_observation_models(self) -> List[np.ndarray]:
        return list(self._obs_models)

    def get_observation_model(self) -> np.ndarray:
        return self._obs_models[0]

    def get_observation_costs(self) -> List[float]:
        return [self.scan_cost] * self.num_scans

    def get_commit_reward_matrix(self) -> np.ndarray:
        """
        Shape (num_cells, num_cells). Row i = collect at cell i.
        R[i, j] = correct_reward if i == j, else incorrect_penalty.
        """
        mat = np.full((self.num_cells, self.num_cells), self.incorrect_penalty)
        np.fill_diagonal(mat, self.correct_reward)
        return mat

    def get_scan_mask(self, scan_idx: int) -> np.ndarray:
        """
        Return an (N, N) boolean array where True marks cells in group B
        (bit=1) for scan action scan_idx. Used by the renderer.
        """
        mask = np.zeros((self.grid_size, self.grid_size), dtype=bool)
        for r in range(self.grid_size):
            for c in range(self.grid_size):
                if self._scan_bit(scan_idx, r, c):
                    mask[r, c] = True
        return mask

    def get_scan_description(self, scan_idx: int) -> str:
        """Human-readable label for a scan action."""
        if scan_idx < self.num_row_bits:
            bit_idx = scan_idx
            group_a = [r for r in range(self.grid_size) if not (r >> bit_idx) & 1]
            group_b = [r for r in range(self.grid_size) if (r >> bit_idx) & 1]
            return f"Row scan {bit_idx}: rows {group_a} vs {group_b}"
        bit_idx = scan_idx - self.num_row_bits
        group_a = [c for c in range(self.grid_size) if not (c >> bit_idx) & 1]
        group_b = [c for c in range(self.grid_size) if (c >> bit_idx) & 1]
        return f"Col scan {bit_idx}: cols {group_a} vs {group_b}"

    def reset(
        self, *, seed: Optional[int] = None, options: Optional[Dict[str, Any]] = None
    ) -> Tuple[int, Dict[str, Any]]:
        super().reset(seed=seed)
        self._target_cell = int(self.np_random.integers(0, self.num_cells))
        self._scan_count = 0
        target_row, target_col = self._cell_to_rc(self._target_cell)
        return 2, {
            "target_cell": self._target_cell,
            "target_row": target_row,
            "target_col": target_col,
        }

    def step(self, action: int) -> Tuple[int, float, bool, bool, Dict[str, Any]]:
        if action < self.num_scans:
            obs = self._run_scan(action)
            self._scan_count += 1
            info = {
                "target_cell": self._target_cell,
                "scan_index": action,
                "scan_count": self._scan_count,
            }
            return obs, -self.scan_cost, False, False, info

        collected_cell = action - self.num_scans
        correct = collected_cell == self._target_cell
        reward = self.correct_reward if correct else self.incorrect_penalty
        info = {
            "target_cell": self._target_cell,
            "collected_cell": collected_cell,
            "correct": correct,
            "scan_count": self._scan_count,
            "total_reward": reward - self.scan_cost * self._scan_count,
        }
        return 2, reward, True, False, info

    def _run_scan(self, scan_idx: int) -> int:
        target_row, target_col = self._cell_to_rc(self._target_cell)
        bit = self._scan_bit(scan_idx, target_row, target_col)
        if self.np_random.random() < self.scan_accuracy:
            return bit
        return 1 - bit
