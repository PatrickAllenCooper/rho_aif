"""Analysis fixtures cover mixtures and provenance, without real outcomes."""

import importlib.util
import json
from pathlib import Path
import sys

import numpy as np
import pytest


ROOT = Path(__file__).resolve().parents[1]


def load_script(name):
    if name in sys.modules:
        return sys.modules[name]
    spec = importlib.util.spec_from_file_location(name, ROOT / "experiments" / f"{name}.py")
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


study = load_script("run_real_sensor_study")
analysis = load_script("analyze_real_sensor_study")


@pytest.fixture
def archived_fixture(tmp_path, monkeypatch):
    monkeypatch.setattr(analysis, "OUT", tmp_path)
    model_path = tmp_path / "model.json"
    # Deliberately unsorted class order: the score must index by class ID.
    model_path.write_text(json.dumps({"classes": [2, 1]}))
    directory = tmp_path / "calibration"
    directory.mkdir()
    np.savez_compressed(directory / "rows.npz", y=np.array([1, 2]), batch=np.array([1, 1]),
                        row_id=np.array(["fixture:a", "fixture:b"]))
    (directory / "run_identity.json").write_text(json.dumps({"model_sha256": study.sha(model_path)}))
    metadata = {"rows_sha256": study.sha(directory / "rows.npz"),
                "run_identity_sha256": study.sha(directory / "run_identity.json"), "policies": []}
    for name, posterior, correct, usage in [
        ("p0", [[.2, .8], [.6, .4]], [1, 1], [1, 1]),
        ("p1", [[.9, .1], [.9, .1]], [0, 1], [2, 2]),
    ]:
        path = directory / f"{name}.npz"
        np.savez_compressed(path, posteriors=posterior, correctness=correct, usage=usage,
                            reward=np.asarray(correct) - .02 * np.asarray(usage))
        metadata["policies"].append({"name": name, "archive_sha256": study.sha(path)})
    (directory / "complete.json").write_text(json.dumps(metadata))
    return tmp_path


def test_episode_mixture_averages_component_scores_not_posterior_ensemble(archived_fixture):
    names, rows, values = analysis.load_partition("calibration")
    q = analysis.mixture_vector({"weights": {"p1": .5, "p0": .5}}, names)
    np.testing.assert_allclose(values["log_loss"], -np.log([[.8, .6], [.1, .9]]))
    np.testing.assert_allclose(values["brier"], [[.08, .32], [1.62, .02]])
    np.testing.assert_allclose(np.einsum("p,pn->n", q, values["correctness"]), [.5, 1])
    np.testing.assert_allclose(np.einsum("p,pn->n", q, values["usage"]), [1.5, 1.5])
    expected_log_score = np.einsum("p,pn->n", q, values["log_loss"])
    np.testing.assert_allclose(expected_log_score, -.5 * np.log([.08, .54]))
    # Averaging posterior predictions first is a different policy/estimand.
    assert not np.allclose(expected_log_score, -np.log([.45, .75]))


@pytest.mark.parametrize("relative_path,error", [
    ("calibration/p0.npz", "Trajectory hash"),
    ("calibration/rows.npz", "Row identities"),
    ("calibration/run_identity.json", "Row identities"),
    ("model.json", "Model identity"),
])
def test_analysis_rejects_changed_trajectory_row_or_model_identity(archived_fixture, relative_path, error):
    path = archived_fixture / relative_path
    path.write_bytes(path.read_bytes() + b"tampered")
    with pytest.raises(RuntimeError, match=error):
        analysis.load_partition("calibration")


@pytest.mark.parametrize("weights", [
    {"missing": 1}, {"p0": .8}, {"p0": -1, "p1": 2},
    {"p0": float("nan")}, {"p0": float("inf")}, {},
])
def test_invalid_selected_mixtures_fail_instead_of_silently_changing_estimand(weights):
    with pytest.raises(ValueError):
        analysis.mixture_vector({"weights": weights}, ["p0", "p1"])


def test_null_mixture_and_partial_bootstrap_failures_remain_visible():
    assert analysis.mixture_vector({"weights": None}, ["p0"]) is None
    report = analysis.interval([.1, .2, np.nan, np.inf])
    assert report["valid_replicates"] == 2 and report["failed_replicates"] == 2
    assert .1 <= report["lower"] <= report["upper"] <= .2
    unavailable = analysis.interval([np.nan, np.nan])
    assert unavailable == {"lower": None, "upper": None, "valid_replicates": 0, "failed_replicates": 2}


def test_original_unattainable_crossing_cannot_pass_from_successful_bootstrap_draws(monkeypatch, tmp_path):
    cfg = {"seed_bootstrap": 17, "bootstrap_replicates": 4, "targets": [2], "usage_margin": .5}
    monkeypatch.setattr(analysis, "config", lambda: cfg)
    monkeypatch.setattr(analysis, "OUT", tmp_path)
    calls = []

    def choose(names, usage, reward):
        calls.append(usage.copy())
        result = {f"{family}_B2": {"weights": {"p0": 1}}
                  for family in ("crossing", "weight_target", "weight_cap", "direct_target", "direct_cap", "cmi", "order")}
        if len(calls) == 1:
            result["crossing_B2"]["weights"] = None
        return result

    monkeypatch.setattr(analysis, "select_policies", choose)
    rows = {"batch": np.array([1, 1]), "y": np.array([1, 1])}
    values = {"usage": np.array([[2., 2.]]), "reward": np.array([[.96, .96]]), "correctness": np.array([[1., 1.]])}
    report = analysis.bootstrap_calibration(["p0"], rows, values, rows, values)
    assert report["2"]["usage_error_interval"]["failed_replicates"] == 0
    assert report["2"]["usage_error_interval"]["lower"] == 0
    assert report["2"]["usage_error_interval"]["upper"] == 0
    assert not report["2"]["usage_within_margin"]
