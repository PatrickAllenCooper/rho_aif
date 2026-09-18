"""Regression test for the dual-control runner's seeding across a reward rescale.

The runner replaces the environment at the rescale point. Before 2026-09-17 the
replacement environment was never seeded, so two runs with the same declared
seed agreed before the rescale and diverged after it. Every episode is now
seeded by the documented rule, so the complete trajectory must repeat exactly.
"""
import sys
from pathlib import Path
from types import SimpleNamespace

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "experiments"))
import run_price_of_information as rpi  # noqa: E402

COLS = ["episode", "usage", "weight", "reward", "success"]


def _run(seed: int, variant: str = "decay") -> pd.DataFrame:
    df, _agent = rpi.run_dual_descent(
        n_episodes=8,
        budget=8.0,
        lr=0.5,
        lr_decay=0.5,
        rescale_at=3,
        rescale_factor=10.0,
        seed=seed,
        reset_window=20 if variant == "reset" else None,
        variant=variant,
        ref=SimpleNamespace(w_star=1.0),
        verbose=False,
    )
    return df[COLS].reset_index(drop=True)


def test_identical_seed_repeats_full_trajectory_across_rescale():
    a, b = _run(42), _run(42)
    assert a.shape == b.shape
    post = a["episode"] >= 3
    assert post.any(), "the run must span the rescale point"
    pd.testing.assert_frame_equal(a, b)


def test_reset_variant_also_repeats():
    pd.testing.assert_frame_equal(_run(7, "reset"), _run(7, "reset"))


def test_distinct_seeds_differ():
    a, b = _run(42), _run(43)
    assert not a[["usage", "reward"]].equals(b[["usage", "reward"]])
