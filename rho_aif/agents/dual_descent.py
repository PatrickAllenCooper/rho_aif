"""
Online dual controller for the Planning+IG weight w.

Drives episodic sensing usage to a target budget B by projected dual updates:

    w ← max(0, w + lr_t * (B - U_episode))

with optional learning-rate decay lr_t = lr0 / (1 + decay * t) and a Polyak
time-average w_avg. Mirrors SAC automatic temperature tuning
(Haarnoja et al., 2018, arXiv:1812.05905). See
Guidance_Documents/price_of_information.md.
"""

from __future__ import annotations

from typing import List, Optional, Union

import numpy as np

from rho_aif.agents.planning_infogain import PlanningInfoGainAgent
from rho_aif.budget import dual_update


def dual_lr(lr0: float, t: int, decay: float = 0.0) -> float:
    """Learning rate at step t (0-indexed): lr0 / (1 + decay * t)."""
    if t < 0:
        raise ValueError("t must be nonnegative")
    if decay < 0:
        raise ValueError("decay must be nonnegative")
    return float(lr0) / (1.0 + float(decay) * float(t))


class DualWeightAgent(PlanningInfoGainAgent):
    """
    Planning+IG agent whose info_gain_weight is adapted online.

    Call ``end_episode(usage)`` once per finished episode with the realized
    sensing usage (count or cost). The weight trajectory is recorded in
    ``weight_history`` (post-update values) and ``usage_history``.
    ``avg_weight_history`` tracks the Polyak time-average ``w_avg``.
    """

    def __init__(
        self,
        observation_models: Union[np.ndarray, List[np.ndarray]],
        env_config: dict,
        budget: float,
        lr: float = 0.1,
        planning_horizon: int = 4,
        initial_weight: float = 1.0,
        discount: float = 1.0,
        min_weight: float = 0.0,
        max_weight: Optional[float] = None,
        lr_decay: float = 0.0,
    ):
        super().__init__(
            observation_models,
            env_config,
            planning_horizon=planning_horizon,
            info_gain_weight=float(initial_weight),
            discount=discount,
        )
        self.budget = float(budget)
        self.lr = float(lr)
        self.lr_decay = float(lr_decay)
        self.min_weight = float(min_weight)
        self.max_weight = None if max_weight is None else float(max_weight)
        self._n_updates = 0
        self._w_sum = float(self.info_gain_weight)
        self.weight_history: List[float] = [float(self.info_gain_weight)]
        self.avg_weight_history: List[float] = [float(self.info_gain_weight)]
        self.usage_history: List[float] = []
        self.lr_history: List[float] = []

    @property
    def weight(self) -> float:
        return float(self.info_gain_weight)

    @property
    def w_avg(self) -> float:
        """Polyak time-average of post-update weights (includes the initial weight)."""
        n = len(self.weight_history)
        return self._w_sum / n if n else float(self.info_gain_weight)

    def current_lr(self) -> float:
        return dual_lr(self.lr, self._n_updates, self.lr_decay)

    def end_episode(self, usage: float) -> float:
        """
        Apply one projected dual step from realized episode usage.

        Returns the updated weight.
        """
        u = float(usage)
        self.usage_history.append(u)
        lr_t = self.current_lr()
        self.lr_history.append(lr_t)
        new_w = dual_update(self.info_gain_weight, u, self.budget, lr_t)
        if new_w < self.min_weight:
            new_w = self.min_weight
        if self.max_weight is not None and new_w > self.max_weight:
            new_w = self.max_weight
        self.info_gain_weight = new_w
        self._n_updates += 1
        self.weight_history.append(new_w)
        self._w_sum += new_w
        self.avg_weight_history.append(self.w_avg)
        return new_w

    def reset_dual_state(self, weight: Optional[float] = None) -> None:
        """Reset dual histories; optionally set a new initial weight."""
        if weight is not None:
            self.info_gain_weight = float(weight)
        self._n_updates = 0
        self._w_sum = float(self.info_gain_weight)
        self.weight_history = [float(self.info_gain_weight)]
        self.avg_weight_history = [float(self.info_gain_weight)]
        self.usage_history = []
        self.lr_history = []
