"""apply_holm in run_rocksample.py corrects within (instance, metric)."""
import sys
from pathlib import Path

import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "experiments"))
from run_rocksample import apply_holm  # noqa: E402


def _frame(rows):
    return pd.DataFrame(rows, columns=["instance", "metric", "p_pooled", "p_seed_level"])


def test_families_are_instance_and_metric():
    df = _frame([
        ("A", "Reward", 0.01, 0.01), ("A", "Reward", 0.04, 0.04),
        ("A", "Bad", 0.01, 0.01),
        ("B", "Reward", 0.01, 0.30),
    ])
    out = apply_holm(df)
    # Family A/Reward has two tests: 0.01 <= 0.05/2 rejects, 0.04 <= 0.05/1 rejects.
    assert out["significant_hb_seed_level"].tolist() == [True, True, True, False]
    assert out["significant_hb_pooled"].tolist() == [True, True, True, True]


def test_larger_family_is_stricter():
    one = apply_holm(_frame([("A", "Bad", 0.02, 0.02), ("A", "Bad", 0.5, 0.5)]))
    three = apply_holm(_frame([("A", "Bad", 0.02, 0.02), ("A", "Bad", 0.5, 0.5), ("A", "Bad", 0.6, 0.6)]))
    assert bool(one["significant_hb_seed_level"].iloc[0]) is True
    assert bool(three["significant_hb_seed_level"].iloc[0]) is False


def test_committed_rocksample_flags_reproduce():
    root = Path(__file__).resolve().parents[1] / "results"
    for name in ("5x3", "7x4", "7x8", "11x11"):
        df = pd.read_csv(root / f"results_rocksample_{name}_stats.csv", float_precision="round_trip")
        out = apply_holm(df)
        assert out["significant_hb_seed_level"].tolist() == df["significant_hb_seed_level"].tolist()
        assert out["significant_hb_pooled"].tolist() == df["significant_hb_pooled"].tolist()
