"""Training-only numerical audit of a frozen model, without policy replay."""
from __future__ import annotations

import json
from pathlib import Path
import sys
import warnings

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "experiments"))
sys.path.insert(0, str(ROOT))

import numpy as np
from sklearn.metrics.pairwise import euclidean_distances
from threadpoolctl import threadpool_limits

from run_real_sensor_study import OUT, RAW, PREPARED, now, parse_archive, sha, stamp
from rho_aif.real_sensor import SensorModel


def captured(operation):
    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always", RuntimeWarning)
        value = operation()
    return value, [str(item.message) for item in caught]


def main():
    X, labels, _, ids, _, _ = parse_archive(RAW)
    with np.load(PREPARED) as prepared:
        train = prepared["split"] == "train"
    # No calibration/evaluation feature is used below this point.
    X, labels, ids = X[train], labels[train], ids[train]
    model = SensorModel.from_dict(json.loads((OUT / "model.json").read_text()))
    assert ids.tolist() == model.provenance["training_row_ids"]
    report = {"started_utc": now(), "scope": "Training rows only. No policy replay or model refit.",
              "n_train": len(X), "model_sha256": sha(OUT / "model.json"),
              "raw_sha256": sha(RAW), "provenance": stamp(), "sensors": [],
              "primary_sources": [
                  "https://numpy.org/doc/stable/release/2.3.1-notes.html",
                  "https://github.com/numpy/numpy/issues/29820",
              ], "identity_controls": []}
    category_arrays = []
    with threadpool_limits(limits=1):
        for size in (2, 14, 15, 16, 64):
            identity = np.eye(size)
            product, caught = captured(lambda: identity @ identity)
            assert np.array_equal(product, identity)
            report["identity_controls"].append({"size": size, "exact_identity": True,
                                                 "warnings": caught})
        for sensor in range(model.n_sensors):
            block = X[:, sensor * 8:(sensor + 1) * 8]
            standard = (block - model.scaler_mean[sensor]) / model.scaler_scale[sensor]
            centers = model.centers[sensor]
            independent = np.einsum("ij,kj->ik", standard, centers, optimize=False)
            product, product_warnings = captured(lambda: standard @ centers.T)
            broadcast_distances = np.square(standard[:, None, :] - centers[None, :, :]).sum(axis=2)
            sklearn_distances, distance_warnings = captured(
                lambda: euclidean_distances(standard, centers, squared=True)
            )
            categories = np.argmin(broadcast_distances, axis=1)
            category_arrays.append(categories)
            squared_residual = broadcast_distances[np.arange(len(X)), categories]
            inertia_independent = np.sum(squared_residual)
            inertia_blas, inertia_warnings = captured(lambda: squared_residual @ np.ones(len(X)))
            assert np.isfinite(product).all() and np.isfinite(sklearn_distances).all()
            assert np.allclose(product, independent, rtol=1e-12, atol=1e-12)
            assert np.allclose(sklearn_distances, broadcast_distances, rtol=1e-10, atol=1e-10)
            assert np.array_equal(categories, np.argmin(sklearn_distances, axis=1))
            assert np.isclose(inertia_blas, inertia_independent, rtol=1e-12, atol=1e-12)
            assert np.abs(standard).max() <= np.sqrt(len(X)) + 1e-10
            for class_index, label in enumerate(model.classes):
                counts = np.bincount(categories[labels == label], minlength=model.n_categories)
                expected = (counts + 1.0) / (np.count_nonzero(labels == label) + model.n_categories)
                assert np.array_equal(expected, model.likelihood[sensor, class_index])
            report["sensors"].append({
                "sensor": sensor, "raw_abs_max": float(np.abs(block).max()),
                "standardized_abs_max": float(np.abs(standard).max()),
                "center_abs_max": float(np.abs(centers).max()),
                "product_abs_max": float(np.abs(independent).max()),
                "blas_vs_independent_max_abs_error": float(np.abs(product - independent).max()),
                "distance_max_abs_error": float(np.abs(sklearn_distances - broadcast_distances).max()),
                "centroid_assignment_mismatches": int(np.count_nonzero(categories != np.argmin(sklearn_distances, axis=1))),
                "independent_inertia": float(inertia_independent),
                "inertia_abs_error": float(np.abs(inertia_blas - inertia_independent)),
                "cluster_counts": np.bincount(categories, minlength=model.n_categories).tolist(),
                "product_warnings": product_warnings, "distance_warnings": distance_warnings,
                "inertia_warnings": inertia_warnings,
            })
    encoded = np.column_stack(category_arrays)
    assert np.array_equal(encoded, model.encode(X))
    report["finished_utc"] = now()
    report["checks_passed"] = True
    report["warning_count"] = sum(len(row[k]) for row in report["sensors"]
                                  for k in ("product_warnings", "distance_warnings", "inertia_warnings"))
    destination = Path(__file__).with_name("training_numerics_audit.json")
    destination.write_text(json.dumps(report, indent=2, allow_nan=False) + "\n")
    print(json.dumps({"path": str(destination), "checks_passed": True,
                      "warning_count": report["warning_count"],
                      "standardized_abs_max": max(row["standardized_abs_max"] for row in report["sensors"]),
                      "product_max_abs_error": max(row["blas_vs_independent_max_abs_error"] for row in report["sensors"]),
                      "distance_max_abs_error": max(row["distance_max_abs_error"] for row in report["sensors"])}))


if __name__ == "__main__":
    main()
