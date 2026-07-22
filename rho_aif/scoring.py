"""Proper scoring rules for terminal beliefs against the true hidden state.

Under log scoring, Expected Free Energy at w=1 is the theoretically correct
belief reporter (Bernardo 1979). These metrics are the benchmark differentiator
alongside cumulative reward.
"""

from __future__ import annotations

import numpy as np
from typing import Sequence, Union

ArrayLike = Union[np.ndarray, Sequence[float]]


def log_score(belief: ArrayLike, true_state: int, eps: float = 1e-12) -> float:
    """Logarithmic score of a categorical belief: log p(true_state).

    Higher (less negative) is better. Returned in nats (natural log).
    """
    p = np.asarray(belief, dtype=float)
    if true_state < 0 or true_state >= len(p):
        raise ValueError(f"true_state {true_state} out of range for belief of length {len(p)}")
    return float(np.log(max(float(p[true_state]), eps)))


def brier_score(belief: ArrayLike, true_state: int) -> float:
    """Brier score of a categorical belief: sum_i (p_i - 1[i=true])^2.

    Lower is better. Range is [0, 2] for any number of classes.
    """
    p = np.asarray(belief, dtype=float)
    if true_state < 0 or true_state >= len(p):
        raise ValueError(f"true_state {true_state} out of range for belief of length {len(p)}")
    one_hot = np.zeros_like(p)
    one_hot[true_state] = 1.0
    return float(np.sum((p - one_hot) ** 2))


def binary_belief_from_fault_prob(p_faulty: float) -> np.ndarray:
    """Map P(faulty) to a two-state belief [P(nominal), P(faulty)]."""
    p = float(np.clip(p_faulty, 0.0, 1.0))
    return np.array([1.0 - p, p], dtype=float)


def factored_log_score(fault_beliefs: ArrayLike, true_faults: ArrayLike) -> float:
    """Mean log score across independent binary component beliefs."""
    beliefs = np.asarray(fault_beliefs, dtype=float)
    truths = np.asarray(true_faults, dtype=int)
    if beliefs.shape != truths.shape:
        raise ValueError("fault_beliefs and true_faults must have the same shape")
    scores = [
        log_score(binary_belief_from_fault_prob(p), int(t))
        for p, t in zip(beliefs, truths)
    ]
    return float(np.mean(scores)) if scores else 0.0


def factored_brier_score(fault_beliefs: ArrayLike, true_faults: ArrayLike) -> float:
    """Mean Brier score across independent binary component beliefs."""
    beliefs = np.asarray(fault_beliefs, dtype=float)
    truths = np.asarray(true_faults, dtype=int)
    if beliefs.shape != truths.shape:
        raise ValueError("fault_beliefs and true_faults must have the same shape")
    scores = [
        brier_score(binary_belief_from_fault_prob(p), int(t))
        for p, t in zip(beliefs, truths)
    ]
    return float(np.mean(scores)) if scores else 0.0


TRUE_STATE_KEYS = (
    "true_state",
    "true_condition",
    "tiger_location",
    "best_arm",
    "target_cell",
)


def extract_true_state(info: dict, env=None) -> int:
    """Pull the true hidden state index from a Gymnasium info dict or env fields."""
    for key in TRUE_STATE_KEYS:
        if key in info and info[key] is not None:
            return int(info[key])
    # Navigation stores the goal as a (row, col) pair.
    if "goal_pos" in info and info["goal_pos"] is not None and env is not None:
        if hasattr(env, "_pos_to_idx"):
            return int(env._pos_to_idx(tuple(info["goal_pos"])))
    if env is not None:
        for attr in (
            "_true_state",
            "_true_condition",
            "_tiger_location",
            "_best_arm",
            "_target_cell",
        ):
            val = getattr(env, attr, None)
            if val is not None:
                return int(val)
        if getattr(env, "_goal_pos", None) is not None and hasattr(env, "_pos_to_idx"):
            return int(env._pos_to_idx(tuple(env._goal_pos)))
    raise KeyError("Could not determine true hidden state from info or env")
