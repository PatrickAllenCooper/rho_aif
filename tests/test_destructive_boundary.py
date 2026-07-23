"""Numerical verification of the destructive-sensing boundary example
(Section 4.4 of the review-response plan; the ``Example`` immediately after
Proposition~prop:factored in paper/paper.tex and paper/paper_arxiv.tex).

Two states, one destructive test action ``a_D`` (perfectly reveals the
pre-transition state but always transitions the hidden state to a fixed
depleted value afterward), one step. Confirms the naive state-preserving
EFE value, the correct Bellman value, the sign/ranking flip for cost
``c in (1, 2)``, and that the naive policy's realized value in the true
environment is strictly worse than not testing at all -- not merely a
mispriced tradeoff within the sign-flip window.
"""

import numpy as np
import pytest


def naive_value_of_drill(w: float, c: float) -> float:
    """Naive EFE value of a_D, assuming (incorrectly) that a_D preserves the
    hidden state, as Propositions 1-3.3's state-preserving assumption does.

    V_naive(a_D) = -c + w * I(b) + E_o[max_i r(Commit_i, o)]

    A perfect binary test at the uniform prior b=(0.5, 0.5) has I(b) = 1 bit,
    and whichever outcome o is observed, the naively "matching" commit action
    is scored as if it were still correct, giving continuation value 1.
    """
    info_gain_bits = 1.0
    continuation = 1.0
    return -c + w * info_gain_bits + continuation


def true_value_of_drill(c: float) -> float:
    """Correct Bellman value of a_D under the actual joint transition-
    observation kernel: the post-drill state is certainly 0 regardless of
    the observation, so the correct continuation value is max_i r(Commit_i, 0) = 1.
    """
    return -c + 1.0


def commit_value() -> float:
    """E_b[r(Commit_i, s)] for either commit action at b=(0.5, 0.5) with the
    symmetric two-state reward r(Commit_i, s) = +1 if i=s else -1."""
    return 0.0


def realized_value_of_naive_policy(c: float) -> float:
    """Expected reward actually received in the TRUE environment if the
    naive policy is followed: drill, then commit on the (now obsolete)
    revealed pre-drill state. Whichever action is chosen, the true
    post-drill state is 0, so only the Commit0 branch pays off."""
    # o=0 (prob 0.5): naive commits Commit0; true state is 0 -> reward +1.
    # o=1 (prob 0.5): naive commits Commit1; true state is 0 -> reward -1.
    return -c + 0.5 * 1.0 + 0.5 * (-1.0)


def correct_posterior_after_drill(o: int) -> np.ndarray:
    """b'_{o,T}(s') computed from the actual joint kernel P(s', o | s, a_D)
    = T(s'|s,a_D) * O(o|s,a_D), with T(0|s,a_D)=1 for all s (depleted) and
    O(o|s,a_D)=1{o=s} (perfect pre-transition observation)."""
    b = np.array([0.5, 0.5])
    obs_likelihood = np.array([1.0 if s == o else 0.0 for s in (0, 1)])
    joint_s0 = float(np.sum(1.0 * obs_likelihood * b))  # T(0|s,a_D) = 1 for all s
    joint_s1 = float(np.sum(0.0 * obs_likelihood * b))  # T(1|s,a_D) = 0 for all s
    evidence = joint_s0 + joint_s1
    return np.array([joint_s0, joint_s1]) / evidence


def naive_posterior_after_drill(o: int) -> np.ndarray:
    """b'_o computed under the (incorrect) state-preserving assumption:
    point mass at the revealed value o."""
    return np.array([1.0, 0.0]) if o == 0 else np.array([0.0, 1.0])


class TestDestructiveSensingBoundary:
    def test_naive_recommends_drilling_in_ranking_flip_range(self):
        for c in [1.1, 1.5, 1.9]:
            assert naive_value_of_drill(w=1.0, c=c) > commit_value()

    def test_true_bellman_recommends_committing_in_ranking_flip_range(self):
        for c in [1.1, 1.5, 1.9]:
            assert true_value_of_drill(c) < commit_value()

    def test_ranking_flip_boundary_is_c_in_one_two(self):
        # At c=1, the true value exactly ties immediate commit.
        assert true_value_of_drill(1.0) == pytest.approx(commit_value())
        # At c=2, the naive value exactly ties immediate commit.
        assert naive_value_of_drill(w=1.0, c=2.0) == pytest.approx(commit_value())
        # Inside (1, 2) both indifference points are strictly crossed with
        # opposite signs, i.e. a genuine ranking flip, not a boundary artifact.
        for c in [1.01, 1.5, 1.99]:
            naive_prefers_drill = naive_value_of_drill(w=1.0, c=c) > commit_value()
            true_prefers_drill = true_value_of_drill(c) > commit_value()
            assert naive_prefers_drill and not true_prefers_drill

    def test_naive_value_overestimates_true_value_by_exactly_one_bit(self):
        for c in [0.3, 1.0, 1.5, 1.9]:
            gap = naive_value_of_drill(w=1.0, c=c) - true_value_of_drill(c)
            assert gap == pytest.approx(1.0)

    def test_naive_policy_realized_value_is_strictly_worse_than_not_testing(self):
        """The failure is not confined to the sign-flip window: for every
        c > 0, actually following the naive policy underperforms simply
        committing immediately without ever drilling."""
        for c in [0.01, 0.3, 1.0, 1.5, 5.0]:
            realized = realized_value_of_naive_policy(c)
            assert realized < commit_value()
            assert realized == pytest.approx(-c)

    def test_correct_posterior_is_certain_depleted_state_for_both_outcomes(self):
        for o in (0, 1):
            posterior = correct_posterior_after_drill(o)
            assert posterior[0] == pytest.approx(1.0)
            assert posterior[1] == pytest.approx(0.0)

    def test_naive_posterior_disagrees_with_correct_posterior_when_o_equals_one(self):
        """The transition-observation coupling term is not merely nonzero
        but maximal here: the two posteriors have disjoint support when
        o=1, so D_KL[correct || naive] is undefined/infinite."""
        correct = correct_posterior_after_drill(o=1)
        naive = naive_posterior_after_drill(o=1)
        assert np.array_equal(correct, np.array([1.0, 0.0]))
        assert np.array_equal(naive, np.array([0.0, 1.0]))
        assert not np.any((correct > 0) & (naive > 0))

    def test_naive_posterior_agrees_with_correct_posterior_when_o_equals_zero(self):
        """A milder sanity check: when the revealed state happens to equal
        the depleted value, the naive and correct posteriors coincide by
        coincidence, not because the naive assumption was actually valid."""
        correct = correct_posterior_after_drill(o=0)
        naive = naive_posterior_after_drill(o=0)
        assert np.array_equal(correct, naive)
