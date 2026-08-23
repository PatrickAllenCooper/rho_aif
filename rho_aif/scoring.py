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


def reward_equivalence_classes(commit_reward_matrix: ArrayLike) -> np.ndarray:
    """Partition hidden states into reward-equivalence classes.

    Two states are reward-equivalent when every commit action pays the same in
    both, so no belief mass moved between them can ever change which commit
    action is optimal. The partition is derived from the commit reward matrix
    alone, which is the only relevance signal an observe-then-commit agent
    legitimately holds (see rho_aif.benchmark.make_env_config, which passes
    agents only the observation costs and this matrix).

    Parameters
    ----------
    commit_reward_matrix
        Array of shape (num_commit_actions, num_states).

    Returns
    -------
    Integer array of shape (num_states,) mapping each state to its class index.
    On an environment where no two states are reward-equivalent this is a
    permutation of range(num_states), and information gain computed on the
    class marginal reduces exactly to ordinary state information gain.
    """
    matrix = np.asarray(commit_reward_matrix, dtype=float)
    if matrix.ndim != 2:
        raise ValueError("commit_reward_matrix must be 2-D (actions x states)")
    _, class_of_state = np.unique(matrix.T, axis=0, return_inverse=True)
    return np.asarray(class_of_state, dtype=int).ravel()


def reward_relevant_marginal(
    belief: ArrayLike, class_of_state: ArrayLike, num_classes: int
) -> np.ndarray:
    """Marginalise a state belief onto reward-equivalence classes."""
    b = np.asarray(belief, dtype=float)
    return np.bincount(
        np.asarray(class_of_state, dtype=int), weights=b, minlength=num_classes
    )
