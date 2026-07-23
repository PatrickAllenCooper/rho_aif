"""
Online dual controller for the Planning+IG weight w.

Drives episodic sensing usage to a target budget B by projected dual updates:

    w ← max(0, w + lr_t * (B - U_episode))

with optional learning-rate decay lr_t = lr0 / (1 + decay * t) and a Polyak
time-average w_avg. Optionally resets the decay clock when a sustained
budget deviation is detected (shift-aware re-adaptation). Mirrors SAC
automatic temperature tuning (Haarnoja et al., 2018, arXiv:1812.05905).
See Guidance_Documents/price_of_information.md.
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

    When ``reset_window`` is set, a sustained budget deviation after the
    learning rate has decayed below half of ``lr0`` resets the decay clock
    (``_n_updates = 0``), restoring the step size for faster re-adaptation.
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
        reset_window: Optional[int] = None,
        reset_k: float = 3.0,
        reset_abs_floor: float = 0.5,
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
        self.reset_window = None if reset_window is None else int(reset_window)
        self.reset_k = float(reset_k)
        self.reset_abs_floor = float(reset_abs_floor)
        self._n_updates = 0
        self._w_sum = float(self.info_gain_weight)
        self._cooldown_remaining = 0
        self.weight_history: List[float] = [float(self.info_gain_weight)]
        self.avg_weight_history: List[float] = [float(self.info_gain_weight)]
        self.usage_history: List[float] = []
        self.lr_history: List[float] = []
        self.reset_events: List[int] = []

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

    def _maybe_reset_on_shift(self) -> bool:
        """
        Reset decay clock if recent usage persistently misses the budget.

        Returns True if a reset fired.
        """
        w = self.reset_window
        if w is None or w < 2:
            return False
        if self._cooldown_remaining > 0:
            self._cooldown_remaining -= 1
            return False
        if len(self.usage_history) < w:
            return False
        # Only reset once lr has meaningfully decayed (avoid initial convergence).
        if self.current_lr() >= 0.5 * self.lr:
            return False
        window = np.asarray(self.usage_history[-w:], dtype=float)
        mean_u = float(np.mean(window))
        if len(window) >= 2:
            se = float(np.std(window, ddof=1) / np.sqrt(len(window)))
        else:
            se = 0.0
        threshold = max(self.reset_k * se, self.reset_abs_floor)
        if abs(mean_u - self.budget) <= threshold:
            return False
        # Reset decay clock; do not clear histories.
        self._n_updates = 0
        self._cooldown_remaining = w
        # Episode index of the usage that triggered the reset (0-based).
        self.reset_events.append(len(self.usage_history) - 1)
        return True

    def end_episode(self, usage: float) -> float:
        """
        Apply one projected dual step from realized episode usage.

        Returns the updated weight.
        """
        u = float(usage)
        self.usage_history.append(u)
        self._maybe_reset_on_shift()
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
        self._cooldown_remaining = 0
        self.weight_history = [float(self.info_gain_weight)]
        self.avg_weight_history = [float(self.info_gain_weight)]
        self.usage_history = []
        self.lr_history = []
        self.reset_events = []
