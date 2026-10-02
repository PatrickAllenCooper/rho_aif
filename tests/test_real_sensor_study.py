"""Independent study-integrity tests using artificial rows, never UCI outcomes."""

import importlib.util
from pathlib import Path
import sys
import zipfile

import numpy as np
import pytest


ROOT = Path(__file__).resolve().parents[1]


def load_script(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "experiments" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


study = load_script("run_real_sensor_study")
analysis = load_script("analyze_real_sensor_study")


def tiny_archive(path, altered=None):
    """The feature index, not token position, defines a descriptor."""
    with zipfile.ZipFile(path, "w") as archive:
        for batch in range(1, 11):
            tokens = [f"{i}:{1000 * batch + i}" for i in range(128, 0, -1)]
            if batch == 1 and altered is not None:
                tokens = altered(tokens)
            archive.writestr(f"Dataset/batch{batch}.dat", "\n1 " + " ".join(tokens) + "\n")
        archive.writestr("README.txt", "Artificial fixture, not source data.")


def test_parser_preserves_indices_original_lines_and_source_hashes(tmp_path):
    archive = tmp_path / "tiny.zip"
    tiny_archive(archive)
    X, y, batches, ids, hashes, readmes = study.parse_archive(archive)
    np.testing.assert_array_equal(X[0, :9], np.arange(1001, 1010))
    assert X[0, 127] == 1128
    np.testing.assert_array_equal(batches, np.arange(1, 11))
    np.testing.assert_array_equal(y, np.ones(10))
    assert ids[0].endswith("batch1:2")
    assert len(hashes) == 10 and all(len(value) == 64 for value in hashes.values())
    assert "README.txt" in readmes


@pytest.mark.parametrize("altered", [lambda t: t[:-1], lambda t: t + [t[0]]])
def test_parser_rejects_missing_or_duplicate_feature_indices(tmp_path, altered):
    archive = tmp_path / "bad.zip"
    tiny_archive(archive, altered)
    with pytest.raises(ValueError):
        study.parse_archive(archive)


def test_split_is_deterministic_and_obeys_stratum_floor_counts():
    batch = np.repeat([1, 2], 30)
    y = np.tile(np.repeat([1, 2, 3], 10), 2)
    X = np.arange(60 * 3, dtype=float).reshape(60, 3)
    a, hashes, integrity = study.split_rows(X, y, batch, 20261001)
    b, _, _ = study.split_rows(X, y, batch, 20261001)
    np.testing.assert_array_equal(a, b)
    assert len(set(hashes)) == 60
    assert integrity["early_duplicate_groups"] == 0
    for period in (1, 2):
        for label in (1, 2, 3):
            mask = (batch == period) & (y == label)
            assert {p: int(np.sum(a[mask] == p)) for p in ("train", "calibration", "test")} == {
                "train": 6, "calibration": 2, "test": 2,
            }


def test_duplicate_groups_cross_batches_and_labels_without_leakage():
    X = np.arange(24, dtype=float).reshape(8, 3)
    X[1] = X[0]  # exact duplicate with another class, within the early window
    X[2] = X[0]  # same group across early batches
    X[6] = X[0]  # exact later-period overlap must be separately flagged
    y = np.array([1, 2, 1, 1, 2, 2, 1, 2])
    batch = np.array([1, 1, 2, 2, 3, 6, 7, 8])
    split, hashes, integrity = study.split_rows(X, y, batch, 20261001)
    assert len(set(split[:3])) == 1
    assert hashes[0] == hashes[1] == hashes[2] == hashes[6]
    assert split[6] == "shift_overlap" and split[7] == "shift"
    assert integrity["early_duplicate_groups"] == 1
    assert integrity["early_duplicate_extra_rows"] == 2
    assert integrity["conflicting_label_groups"] == 1
    assert integrity["later_overlap_rows"] == 1
    partitions = {p: set(hashes[(split == p)]) for p in ("train", "calibration", "test")}
    assert not (partitions["train"] & partitions["calibration"])
    assert not (partitions["train"] & partitions["test"])
    assert not (partitions["calibration"] & partitions["test"])


def test_crossing_uses_last_upward_crossing_and_exact_mean():
    usage = np.array([0.0, 6.0, 1.0, 5.0])
    q, bracket = study.crossing_weights(usage, [0.0, 1.0, 2.0, 3.0], 3.0)
    np.testing.assert_allclose(q, [0, 0, .5, .5])
    assert bracket["w_lo"] == 2 and bracket["w_hi"] == 3
    assert q @ usage == pytest.approx(3)


@pytest.mark.parametrize("usage,budget", [([3, 4, 5], 2), ([0, 1, 2], 3), ([0, 4, 1], 2), ([2, 2, 4], 2)])
def test_unbracketed_targets_are_preserved_as_failures(usage, budget):
    q, bracket = study.crossing_weights(np.asarray(usage), [0, 1, 2], budget)
    assert q is None
    assert bracket["budget"] == budget
    assert not bracket["bracketed"]


def synthetic_candidate_means():
    cfg = study.config()
    names = [p.name for p in study.policy_grid()]
    usage = np.zeros(len(names))
    for prefix, count in (("w", len(cfg["weights"])), ("d", len(cfg["penalties"]))):
        indices = [i for i, name in enumerate(names) if name.startswith(prefix)]
        usage[indices] = np.linspace(0, 16, count)
    for b in cfg["targets"]:
        usage[names.index(f"cmi{b}")] = b
        usage[names.index(f"order{b}")] = b
    usage[names.index("all")] = 16
    # Every sensor is unhelpful under these artificial means. Equality must
    # spend the target, while the cap optimum should leave it entirely slack.
    reward = 1.0 - .02 * usage
    return names, usage, reward


def test_selected_equality_and_cap_references_answer_different_questions():
    names, usage, reward = synthetic_candidate_means()
    selected = study.select_policies(names, usage, reward)
    for b in (2, 4, 8):
        for family in ("crossing", "weight_target", "direct_target", "cmi", "order"):
            q = analysis.mixture_vector(selected[f"{family}_B{b}"], names)
            assert q.sum() == pytest.approx(1)
            assert np.count_nonzero(q) <= 2
            assert q @ usage == pytest.approx(b)
        for family in ("weight_cap", "direct_cap"):
            q = analysis.mixture_vector(selected[f"{family}_B{b}"], names)
            assert q @ usage == pytest.approx(0)
            assert q @ reward == pytest.approx(1)
    assert selected["anchor_w00"]["weights"] == {"w00": 1.0}


def test_stratified_bootstrap_preserves_stratum_mass_and_policy_pairing():
    batch = np.array([1, 1, 1, 2, 2, 2])
    labels = np.array([1, 1, 2, 1, 2, 2])
    strata = analysis.strata_indices(batch, labels)
    weights = analysis.resample_weights(np.random.default_rng(17), strata, len(batch))
    assert weights.sum() == pytest.approx(1)
    for ids in strata:
        assert weights[ids].sum() == pytest.approx(len(ids) / len(batch))
    # Identical per-case outcomes retain zero paired difference under every
    # shared resample, regardless of their marginal variation across cases.
    outcome = np.array([0, 1, 0, 1, 1, 0])
    assert (outcome - outcome) @ weights == 0


def test_bootstrap_reselects_each_calibration_sample_and_tracks_failures(monkeypatch, tmp_path):
    cfg = dict(study.config(), bootstrap_replicates=16)
    monkeypatch.setattr(analysis, "config", lambda: cfg)
    monkeypatch.setattr(analysis, "OUT", tmp_path)
    names, mean_usage, _ = synthetic_candidate_means()
    cal_usage = np.maximum(0, mean_usage[:, None] + np.array([-.7, -.2, .2, .7]))
    cal_correct = np.tile(np.array([0, 1, 1, 1]), (len(names), 1))
    cal = {"usage": cal_usage, "correctness": cal_correct, "reward": cal_correct - .02 * cal_usage}
    rows = {"batch": np.ones(4, dtype=int), "y": np.ones(4, dtype=int)}
    calls = []

    def reselect(candidate_names, usage, reward):
        calls.append(usage.copy())
        selected = study.select_policies(candidate_names, usage, reward)
        # A deliberate infeasible calibration draw must remain a counted
        # failure, never an omitted target or an H1 success.
        if len(calls) == 2:  # original selection precedes the bootstrap loop
            selected["crossing_B2"]["weights"] = None
        return selected

    monkeypatch.setattr(analysis, "select_policies", reselect)
    report = analysis.bootstrap_calibration(names, rows, cal, rows, cal)
    assert len(calls) == cfg["bootstrap_replicates"] + 1
    np.testing.assert_allclose(calls[0], cal_usage.mean(axis=1))
    assert len({tuple(np.round(c, 9)) for c in calls}) > 1
    assert set(report) == {"2", "4", "8"}
    assert report["2"]["usage_error_interval"]["failed_replicates"] == 1
    assert not report["2"]["usage_within_margin"]
    assert report["2"]["comparisons"]["direct_target"]["correctness"]["failed_replicates"] == 1
    assert (tmp_path / "bootstrap.npz").exists()


def test_frozen_grid_matches_predeclared_formula():
    cfg = study.config()
    np.testing.assert_array_equal(cfg["weights"], sorted(set([0, np.log(2), 1] + list(2.0 ** np.arange(-8, 9)))))
    np.testing.assert_array_equal(cfg["penalties"], sorted(set([0, -.02] + [s * 2.0 ** k for s in [-1, 1] for k in range(-10, 2)])))
    assert cfg["targets"] == [2, 4, 8]
    assert cfg["base_cost"] == .02 and cfg["bootstrap_replicates"] == 2000
