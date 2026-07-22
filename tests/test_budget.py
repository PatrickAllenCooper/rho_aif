"""Tests for sensing-budget accounting and shadow-price bisection."""

from __future__ import annotations

import numpy as np
import pytest

from rho_aif.budget import (
    SensingUsage,
    UsageCurvePoint,
    bisect_usage_fn,
    dual_update,
    episode_sensing_usage,
    estimate_usage_curve,
    grid_solve_usage_fn,
    identifiable_budgets,
    make_log_w_grid,
    solve_shadow_price,
    solve_shadow_price_from_curve,
    usage_value,
)
from rho_aif.environments.diagnosis import DiagnosisEnv
from rho_aif.environments.tiger import TigerEnv


class TestEpisodeSensingUsage:
    def test_from_dict_otc(self):
        u = episode_sensing_usage({"num_observations": 3}, obs_costs=[1.0])
        assert u.num_observations == 3
        assert u.sensing_cost == pytest.approx(3.0)

    def test_from_dict_inspection_tests(self):
        u = episode_sensing_usage({"tests": 5}, obs_costs=[0.5, 2.0])
        assert u.num_observations == 5
        assert u.sensing_cost == pytest.approx(5.0 * 1.25)

    def test_from_object(self):
        class R:
            num_observations = 2

        u = episode_sensing_usage(R(), obs_costs=[2.0])
        assert usage_value(u, "count") == 2.0
        assert usage_value(u, "cost") == 4.0

    def test_unknown_usage_kind(self):
        with pytest.raises(ValueError):
            usage_value(SensingUsage(1, 1.0), "tokens")


class TestBisectUsageFn:
    def test_smooth_monotone(self):
        # U(w) = 2 * (1 - exp(-w)); target B=1 => w = -log(0.5) ≈ 0.693
        def U(w):
            return 2.0 * (1.0 - np.exp(-w))

        res = bisect_usage_fn(U, budget=1.0, w_lo=0.0, w_hi=5.0, tol=0.02, w_tol=1e-4)
        assert abs(res.usage_at_star - 1.0) <= 0.02
        assert abs(res.w_star - np.log(2.0)) < 0.05

    def test_step_function_brackets(self):
        def U(w):
            if w < 1.0:
                return 0.0
            if w < 3.0:
                return 1.0
            return 2.0

        res = bisect_usage_fn(U, budget=1.0, w_lo=0.0, w_hi=4.0, tol=0.01, w_tol=1e-3)
        assert res.usage_lo <= 1.0 <= res.usage_hi or abs(res.usage_at_star - 1.0) <= 0.01
        assert 0.0 <= res.w_lo <= res.w_star <= res.w_hi

    def test_dual_update_sign_and_projection(self):
        # Over budget => decrease w
        assert dual_update(2.0, usage=3.0, budget=1.0, lr=0.5) == pytest.approx(1.0)
        # Under budget => increase w
        assert dual_update(1.0, usage=0.0, budget=2.0, lr=0.25) == pytest.approx(1.5)
        # Projection at 0
        assert dual_update(0.1, usage=5.0, budget=0.0, lr=1.0) == 0.0


class TestGridSolve:
    def test_picks_closest_on_nonmonotone(self):
        # Deliberately non-monotone: U(1)=2, U(2)=4, U(4)=3
        def U(w):
            if w < 0.5:
                return 0.0
            if w < 1.5:
                return 2.0
            if w < 3.0:
                return 4.0
            return 3.0

        res = grid_solve_usage_fn(U, budget=3.0, w_lo=0.0, w_hi=8.0, n_grid=10, tol=0.1)
        assert abs(res.usage_at_star - 3.0) <= 0.1 or abs(res.usage_at_star - 4.0) <= 0.1
        assert res.w_star >= 0.0


class TestSolveShadowPriceSmoke:
    def test_diagnosis_near_budget(self):
        env = DiagnosisEnv(
            num_conditions=4,
            test_accuracy=0.80,
            correct_reward=10.0,
            incorrect_penalty=-50.0,
            test_cost=1.0,
        )
        # U(0)≈5; target above instrumental baseline.
        res = solve_shadow_price(
            env,
            budget=8.0,
            w_lo=0.0,
            w_hi=50.0,
            tol=1.5,
            seeds=[42],
            num_episodes=25,
            planning_horizon=3,
            usage_kind="count",
            n_grid=8,
            method="grid",
        )
        assert res.w_star >= 0.0
        assert res.achievable
        assert abs(res.usage_at_star - 8.0) <= 2.0

    def test_tiger_low_budget_unachievable(self):
        """Tiger listens even at w=0 (instrumental VoI); B=0.5 is unachievable."""
        env = TigerEnv(
            listen_accuracy=0.85,
            listen_cost=1.0,
            correct_reward=10.0,
            incorrect_penalty=-100.0,
        )
        res = solve_shadow_price(
            env,
            budget=0.5,
            w_lo=0.0,
            w_hi=10.0,
            tol=0.2,
            seeds=[42],
            num_episodes=20,
            planning_horizon=6,
            usage_kind="count",
            n_grid=6,
            method="grid",
        )
        assert res.usage_at_star > 0.5
        assert not res.achievable


class TestUsageCurveAndBrackets:
    def test_make_log_w_grid_includes_zero(self):
        grid = make_log_w_grid(0.0, 100.0, n_grid=8)
        assert grid[0] == 0.0
        assert len(grid) == 8
        assert grid[-1] == pytest.approx(100.0)

    def test_step_bracket_from_staircase_curve(self):
        # Synthetic monotone staircase: U=0 for w<1, U=2 for 1<=w<3, U=4 for w>=3
        curve = [
            UsageCurvePoint(0.0, 0.0, 0.1, 3, [0.0, 0.0, 0.0]),
            UsageCurvePoint(0.5, 0.0, 0.1, 3, [0.0, 0.0, 0.0]),
            UsageCurvePoint(1.0, 2.0, 0.2, 3, [2.0, 2.0, 2.0]),
            UsageCurvePoint(2.0, 2.0, 0.2, 3, [2.0, 2.0, 2.0]),
            UsageCurvePoint(3.0, 4.0, 0.3, 3, [4.0, 4.0, 4.0]),
            UsageCurvePoint(5.0, 4.0, 0.3, 3, [4.0, 4.0, 4.0]),
        ]
        res = solve_shadow_price_from_curve(curve, budget=2.0, tol=0.05)
        assert res.achievable
        assert res.bracketed
        assert res.w_lo <= 1.0
        assert res.w_hi >= 1.0
        assert abs(res.usage_at_star - 2.0) <= 0.05
        assert res.u_min == pytest.approx(0.0)
        assert res.u_max == pytest.approx(4.0)

    def test_identifiable_budgets_inside_range(self):
        curve = [
            UsageCurvePoint(0.0, 5.0, 0.1, 2, [5.0, 5.0]),
            UsageCurvePoint(1.0, 8.0, 0.1, 2, [8.0, 8.0]),
            UsageCurvePoint(10.0, 12.0, 0.1, 2, [12.0, 12.0]),
        ]
        budgets = identifiable_budgets(curve, n_budgets=3, margin=0.1)
        assert len(budgets) == 3
        assert min(budgets) > 5.0
        assert max(budgets) < 12.0

    def test_estimate_usage_curve_shape(self):
        env = DiagnosisEnv(
            num_conditions=4,
            test_accuracy=0.80,
            correct_reward=10.0,
            incorrect_penalty=-50.0,
            test_cost=1.0,
        )
        curve = estimate_usage_curve(
            env,
            w_grid=[0.0, 1.0],
            seeds=[42, 123],
            num_episodes=8,
            planning_horizon=3,
        )
        assert len(curve) == 2
        assert curve[0].n_seeds == 2
        assert len(curve[0].per_seed_means) == 2
        assert curve[0].se_usage >= 0.0 or np.isnan(curve[0].se_usage)
        # With 2 seeds SE should be finite
        assert np.isfinite(curve[0].se_usage)
