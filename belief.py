"""
Belief state representation and Bayesian updating for discrete POMDPs.
"""

import numpy as np
from scipy.stats import entropy as scipy_entropy
from typing import Optional, List


class BeliefState:
    """Probability distribution over hidden states with Bayesian updating."""

    def __init__(self, num_states: int = 2, initial_belief: Optional[np.ndarray] = None):
        self.num_states = num_states
        if initial_belief is not None:
            self.belief = initial_belief.copy()
        else:
            self.belief = np.ones(num_states) / num_states
        self.history: List[np.ndarray] = [self.belief.copy()]

    def update(self, observation: int, observation_model: np.ndarray) -> None:
        """
        Bayesian belief update: posterior proportional to likelihood * prior.

        Args:
            observation: Integer index of the observed signal.
            observation_model: P(obs | state) matrix, shape (num_states, num_obs).
        """
        likelihood = observation_model[:, observation]
        posterior = likelihood * self.belief
        norm = posterior.sum()
        if norm > 0:
            posterior /= norm
        else:
            posterior = np.ones(self.num_states) / self.num_states
        self.belief = posterior
        self.history.append(self.belief.copy())

    def entropy(self) -> float:
        """Shannon entropy of current belief in bits."""
        return float(scipy_entropy(self.belief, base=2))

    def most_likely_state(self) -> int:
        """Index of the most probable state."""
        return int(np.argmax(self.belief))

    def confidence(self) -> float:
        """Probability assigned to the most likely state."""
        return float(np.max(self.belief))

    def reset(self, initial_belief: Optional[np.ndarray] = None) -> None:
        """Reset to uniform or specified belief."""
        if initial_belief is not None:
            self.belief = initial_belief.copy()
        else:
            self.belief = np.ones(self.num_states) / self.num_states
        self.history = [self.belief.copy()]

    def copy(self) -> "BeliefState":
        """Return a copy of this belief state (without history)."""
        return BeliefState(self.num_states, self.belief.copy())
