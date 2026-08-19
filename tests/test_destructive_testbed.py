"""DS-B (E1) environment tests for DestructiveTestbedEnv.

Hand-computed posterior checks, destruction dynamics (absorbing state and
delta frequencies under seeded reset streams), observation-model
correctness, and determinism under env.reset(seed=...), per the predeclared
design in docs/ideation/2026-08-19-destructive-sensing-design.md
(Sections 4 E1 and 8 DS-B) and the timing convention of Example
ex:destructive in paper/full_paper_jair.tex (observation emitted from the
PRE-transition state, then the destruction kernel acts).
"""

import numpy as np
import pytest

from rho_aif.environments.destructive_testbed import (
    ACCEPT,
    DESTROYED,
    DestructiveTestbedEnv,
    FAULTY,
    HEALTHY,
    NULL_OBS,
    OBS_READS_FAULTY,
    OBS_READS_HEALTHY,
    REJECT,
    TEST,
)
from rho_aif.scoring import extract_true_state


class TestModelMatrices:
    def test_observation_model_matches_hand_written(self):
        # p = 0.7: healthy reads healthy w.p. 0.7, faulty reads faulty w.p.
        # 0.7, a destroyed unit reads uniformly (no residual signal).
        env = DestructiveTestbedEnv(accuracy=0.7)
        expected = np.array([
            [0.7, 0.3],
            [0.3, 0.7],
            [0.5, 0.5],
        ])
        assert np.allclose(env.get_observation_model(), expected)
        models = env.get_observation_models()
        assert len(models) == 1
        assert np.allclose(models[0], expected)

    def test_transition_kernel_matches_hand_written(self):
        # delta = 0.2: faulty destroyed w.p. 0.2, healthy w.p. delta/2 = 0.1,
        # destroyed absorbing. Rows are pre-transition states (T[s, s']).
        env = DestructiveTestbedEnv(destruction_prob=0.2)
        expected = np.array([
            [0.9, 0.0, 0.1],
            [0.0, 0.8, 0.2],
            [0.0, 0.0, 1.0],
        ])
        (t_test,) = env.get_transition_models()
        assert np.allclose(t_test, expected)
        assert np.allclose(t_test.sum(axis=1), 1.0)

    def test_transition_kernel_is_exact_identity_at_delta_zero(self):
        # The delta = 0 reduction (design doc T1 / DS-C acceptance) relies on
        # the kernel being the exact identity, not merely close to it.
        env = DestructiveTestbedEnv(destruction_prob=0.0)
        (t_test,) = env.get_transition_models()
        assert np.array_equal(t_test, np.eye(3))

    def test_commit_reward_matrix_alpha_asymmetry(self):
        # alpha = 5, R+ = 1: incorrect commits pay R- = -alpha * R+ = -5;
        # both commits pay -R+ on a destroyed unit (unit value lost; E1
        # amendment of Aug 19, 2026 in the design doc).
        env = DestructiveTestbedEnv(alpha=5.0, correct_reward=1.0)
        expected = np.array([
            [1.0, -5.0, -1.0],   # ACCEPT: correct on HEALTHY, lost unit -R+
            [-5.0, 1.0, -1.0],   # REJECT: correct on FAULTY, lost unit -R+
        ])
        assert np.allclose(env.get_commit_reward_matrix(), expected)

    def test_initial_belief_never_starts_destroyed(self):
        env = DestructiveTestbedEnv()
        assert np.allclose(env.get_initial_belief(), [0.5, 0.5, 0.0])
        for seed in range(50):
            _, info = env.reset(seed=seed)
            assert info["true_state"] in (HEALTHY, FAULTY)


class TestHandComputedPosteriors:
    """Joint transition-observation posteriors b'_{o,T}(s') proportional to
    sum_s T(s'|s) O(o|s) b(s), computed from the env's own matrices and
    checked against hand arithmetic (DS-B acceptance)."""

    @staticmethod
    def _joint_posterior(env, belief, obs_idx):
        obs_model = env.get_observation_model()
        (t_test,) = env.get_transition_models()
        weighted = obs_model[:, obs_idx] * belief
        joint = t_test.T @ weighted
        return joint / joint.sum()

    def test_joint_posterior_reads_faulty(self):
        # p = 0.8, delta = 0.2, b = (0.5, 0.5, 0), o = OBS_READS_FAULTY.
        # Likelihood O[:, 1] = (1-p, p, 0.5) = (0.2, 0.8, 0.5).
        # Weighted mass l*b = (0.1, 0.4, 0.0); evidence P(o=1) = 0.5.
        # Advance through T^T:
        #   healthy':   0.9 * 0.1                       = 0.09
        #   faulty':    0.8 * 0.4                       = 0.32
        #   destroyed': 0.1 * 0.1 + 0.2 * 0.4 + 1 * 0.0 = 0.01 + 0.08 = 0.09
        # Normalize by 0.5 -> b'_{o,T} = (0.18, 0.64, 0.18).
        env = DestructiveTestbedEnv(accuracy=0.8, destruction_prob=0.2)
        belief = np.array([0.5, 0.5, 0.0])
        posterior = self._joint_posterior(env, belief, OBS_READS_FAULTY)
        assert np.allclose(posterior, [0.18, 0.64, 0.18])

    def test_joint_posterior_reads_healthy(self):
        # Same env, o = OBS_READS_HEALTHY.
        # Likelihood O[:, 0] = (p, 1-p, 0.5) = (0.8, 0.2, 0.5).
        # Weighted mass l*b = (0.4, 0.1, 0.0); evidence P(o=0) = 0.5.
        # Advance through T^T:
        #   healthy':   0.9 * 0.4                       = 0.36
        #   faulty':    0.8 * 0.1                       = 0.08
        #   destroyed': 0.1 * 0.4 + 0.2 * 0.1 + 1 * 0.0 = 0.04 + 0.02 = 0.06
        # Normalize by 0.5 -> b'_{o,T} = (0.72, 0.16, 0.12).
        env = DestructiveTestbedEnv(accuracy=0.8, destruction_prob=0.2)
        belief = np.array([0.5, 0.5, 0.0])
        posterior = self._joint_posterior(env, belief, OBS_READS_HEALTHY)
        assert np.allclose(posterior, [0.72, 0.16, 0.12])

    def test_joint_posterior_differs_from_observation_only_posterior(self):
        # The state-preserving update after o = OBS_READS_HEALTHY is
        # b'_o = (0.4, 0.1, 0) / 0.5 = (0.8, 0.2, 0): it puts zero mass on
        # DESTROYED, which is exactly the misrepresentation Delta_T measures.
        env = DestructiveTestbedEnv(accuracy=0.8, destruction_prob=0.2)
        belief = np.array([0.5, 0.5, 0.0])
        obs_model = env.get_observation_model()
        naive = obs_model[:, OBS_READS_HEALTHY] * belief
        naive = naive / naive.sum()
        assert np.allclose(naive, [0.8, 0.2, 0.0])
        joint = self._joint_posterior(env, belief, OBS_READS_HEALTHY)
        assert joint[DESTROYED] > 0.0
        assert not np.allclose(naive, joint)

    def test_joint_posterior_collapses_to_naive_at_delta_zero(self):
        # At delta = 0 the kernel is the identity, so the joint posterior
        # must equal the observation-only posterior exactly.
        env = DestructiveTestbedEnv(accuracy=0.8, destruction_prob=0.0)
        belief = np.array([0.5, 0.5, 0.0])
        obs_model = env.get_observation_model()
        for obs_idx in (OBS_READS_HEALTHY, OBS_READS_FAULTY):
            naive = obs_model[:, obs_idx] * belief
            naive = naive / naive.sum()
            assert np.array_equal(self._joint_posterior(env, belief, obs_idx), naive)


class TestDestructionDynamics:
    def test_destruction_frequency_on_faulty_units(self):
        # Force a faulty unit each episode via seeded resets and count how
        # often one test destroys it. delta = 0.2, n = 4000: binomial sd is
        # sqrt(0.2 * 0.8 / 4000) ~ 0.0063, so a 0.025 tolerance is ~4 sd.
        # Deterministic given the seed stream, so this cannot flake.
        env = DestructiveTestbedEnv(destruction_prob=0.2)
        n = 4000
        destroyed = 0
        for i in range(n):
            env.reset(seed=i, options={"true_state": FAULTY})
            _, _, _, _, info = env.step(TEST)
            destroyed += int(info["destroyed_this_step"])
        assert abs(destroyed / n - 0.2) < 0.025

    def test_destruction_frequency_on_healthy_units_is_half_delta(self):
        # Healthy units are destroyed w.p. delta/2 = 0.1 (design doc E1).
        # sd = sqrt(0.1 * 0.9 / 4000) ~ 0.0047; tolerance 0.02 is ~4 sd.
        env = DestructiveTestbedEnv(destruction_prob=0.2)
        n = 4000
        destroyed = 0
        for i in range(n):
            env.reset(seed=i, options={"true_state": HEALTHY})
            _, _, _, _, info = env.step(TEST)
            destroyed += int(info["destroyed_this_step"])
        assert abs(destroyed / n - 0.1) < 0.02

    def test_no_destruction_at_delta_zero(self):
        env = DestructiveTestbedEnv(destruction_prob=0.0)
        for i in range(200):
            env.reset(seed=i)
            for _ in range(5):
                _, _, _, _, info = env.step(TEST)
                assert not info["destroyed_this_step"]
                assert info["true_state"] in (HEALTHY, FAULTY)

    def test_destroyed_state_is_absorbing(self):
        env = DestructiveTestbedEnv(destruction_prob=0.4)
        env.reset(seed=0, options={"true_state": DESTROYED})
        for _ in range(50):
            obs, reward, terminated, _, info = env.step(TEST)
            assert info["true_state"] == DESTROYED
            assert info["pre_transition_state"] == DESTROYED
            assert not info["destroyed_this_step"]  # was already destroyed
            assert obs in (OBS_READS_HEALTHY, OBS_READS_FAULTY)
            assert not terminated

    def test_commits_on_destroyed_unit_pay_zero_and_are_incorrect(self):
        for action in (ACCEPT, REJECT):
            env = DestructiveTestbedEnv(alpha=10.0)
            env.reset(seed=0, options={"true_state": DESTROYED})
            obs, reward, terminated, _, info = env.step(action)
            assert terminated
            assert reward == 0.0
            assert info["correct"] is False
            assert obs == NULL_OBS

    def test_observation_emitted_from_pre_transition_state(self):
        # NORMATIVE timing check (Example ex:destructive convention): with a
        # perfect test (p = 1) and certain destruction on faulty (delta = 1),
        # the reading must still say FAULTY -- it describes the
        # pre-transition state -- even though the post-transition state is
        # DESTROYED on the very same step.
        env = DestructiveTestbedEnv(accuracy=1.0, destruction_prob=1.0)
        for i in range(50):
            env.reset(seed=i, options={"true_state": FAULTY})
            obs, _, _, _, info = env.step(TEST)
            assert obs == OBS_READS_FAULTY
            assert info["pre_transition_state"] == FAULTY
            assert info["true_state"] == DESTROYED
            assert info["destroyed_this_step"]


class TestGymInterface:
    def test_reset_seed_determinism(self):
        # Same seed => identical initial state and identical
        # observation/reward/info streams under the same action script.
        script = [TEST, TEST, TEST, TEST, ACCEPT]
        traces = []
        for _ in range(2):
            env = DestructiveTestbedEnv(accuracy=0.7, destruction_prob=0.3)
            obs, info = env.reset(seed=1024)
            trace = [(obs, info["true_state"])]
            for action in script:
                obs, reward, terminated, truncated, info = env.step(action)
                trace.append((obs, reward, terminated, truncated, tuple(sorted(info.items()))))
            traces.append(trace)
        assert traces[0] == traces[1]

    def test_reset_returns_null_obs_and_true_state_key(self):
        env = DestructiveTestbedEnv()
        obs, info = env.reset(seed=42)
        assert obs == NULL_OBS
        assert "true_state" in info

    def test_test_step_costs_and_counts(self):
        env = DestructiveTestbedEnv(test_cost=0.3)
        env.reset(seed=42)
        _, reward, terminated, _, info = env.step(TEST)
        assert reward == pytest.approx(-0.3)
        assert not terminated
        assert info["test_count"] == 1
        assert info["test_cost_paid"] == pytest.approx(0.3)

    def test_commit_rewards_and_correct_flag(self):
        # ACCEPT is correct on HEALTHY (+R+), REJECT is incorrect on
        # HEALTHY (R- = -alpha * R+ = -5).
        env = DestructiveTestbedEnv(alpha=5.0, correct_reward=1.0)
        env.reset(seed=0, options={"true_state": HEALTHY})
        _, reward, terminated, _, info = env.step(ACCEPT)
        assert terminated
        assert reward == pytest.approx(1.0)
        assert info["correct"] is True

        env.reset(seed=0, options={"true_state": HEALTHY})
        _, reward, terminated, _, info = env.step(REJECT)
        assert reward == pytest.approx(-5.0)
        assert info["correct"] is False

    def test_total_reward_accounts_for_test_costs(self):
        env = DestructiveTestbedEnv(destruction_prob=0.0, test_cost=0.5)
        env.reset(seed=0, options={"true_state": FAULTY})
        env.step(TEST)
        env.step(TEST)
        _, reward, _, _, info = env.step(REJECT)
        assert reward == pytest.approx(1.0)
        assert info["total_reward"] == pytest.approx(1.0 - 2 * 0.5)

    def test_scoring_extract_true_state_works(self):
        # run_experiment scoring pulls the hidden state via TRUE_STATE_KEYS;
        # the info dict must expose it under a supported key.
        env = DestructiveTestbedEnv()
        env.reset(seed=0, options={"true_state": FAULTY})
        _, _, _, _, info = env.step(REJECT)
        assert extract_true_state(info, env) == FAULTY
