"""Learned categorical sensor models and deterministic actual-record replay.

This module never generates observations from its fitted likelihoods. A replay
reveals a category from the supplied record, once per sensor. The runner owns
data splits, calibration, mixture selection, and inference. The model's
conditional-independence assumption is a modeling approximation, not an
assertion about the physical sensors.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass, field
from time import perf_counter
from typing import Any, Dict, List, Optional, Sequence, Tuple

import numpy as np


RELATIVE_TOLERANCE = 1e-12


def _entropy_bits(probabilities: np.ndarray, axis: int = -1) -> np.ndarray:
    """Entropy with the exact convention 0 log(0) = 0."""
    return -np.sum(
        probabilities * np.log2(np.where(probabilities > 0, probabilities, 1.0)),
        axis=axis,
    )


def _finite_matrix(values: np.ndarray, name: str) -> np.ndarray:
    values = np.asarray(values, dtype=float)
    if values.ndim != 2 or not np.all(np.isfinite(values)):
        raise ValueError(f"{name} must be a finite two-dimensional matrix")
    return values


def _choose_sensor(
    scores: np.ndarray,
    candidates: np.ndarray,
    stop_values: Optional[np.ndarray] = None,
) -> np.ndarray:
    """Global relative tie rule fixed in the experiment protocol.

    Candidate columns must be in ascending sensor order. Stop wins when the
    maximum score is at most stop + tolerance. Otherwise choose the lowest
    sensor within tolerance of the global maximum, rather than using a chain
    of pairwise comparisons (which can give a different near-tie result).
    """
    best = scores.max(axis=1)
    scale = np.abs(scores).max(axis=1)
    if stop_values is not None:
        scale = np.maximum(scale, np.abs(stop_values))
    tolerance = RELATIVE_TOLERANCE * scale
    tied = scores >= best[:, None] - tolerance[:, None]
    selected = candidates[np.arange(len(scores)), np.argmax(tied, axis=1)]
    if stop_values is not None:
        selected = np.where(best > stop_values + tolerance, selected, -1)
    return selected


@dataclass
class SensorModel:
    """P(class), P(category | class, sensor), and optional frozen quantizers.

    Likelihood axes are (sensor, class, category). Class ordering is explicitly
    stored, while terminal ties choose the lowest class ID. Quantizer arrays have
    axes (sensor, descriptor) and (sensor, category, descriptor).
    """

    classes: np.ndarray
    prior: np.ndarray
    likelihood: np.ndarray
    scaler_mean: Optional[np.ndarray] = None
    scaler_scale: Optional[np.ndarray] = None
    centers: Optional[np.ndarray] = None
    provenance: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        self.classes = np.asarray(self.classes).copy()
        self.prior = np.asarray(self.prior, dtype=float).copy()
        self.likelihood = np.asarray(self.likelihood, dtype=float).copy()
        if self.classes.ndim != 1 or self.classes.size < 2:
            raise ValueError("classes must contain at least two distinct labels")
        if len(np.unique(self.classes)) != len(self.classes):
            raise ValueError("class labels must be distinct")
        if self.prior.shape != (len(self.classes),):
            raise ValueError("prior shape does not match classes")
        if self.likelihood.ndim != 3 or self.likelihood.shape[1] != len(self.classes):
            raise ValueError("likelihood must have axes (sensor, class, category)")
        if self.n_sensors < 1 or self.n_categories < 1:
            raise ValueError("at least one sensor and category are required")
        for name, array in [("prior", self.prior), ("likelihood", self.likelihood)]:
            if not np.all(np.isfinite(array)) or np.any(array < 0):
                raise ValueError(f"{name} must have finite nonnegative probabilities")
            if not np.allclose(array.sum(axis=-1), 1.0, rtol=0, atol=1e-12):
                raise ValueError(f"{name} probabilities must sum to one")
        supplied = [self.scaler_mean is not None, self.scaler_scale is not None, self.centers is not None]
        if any(supplied) and not all(supplied):
            raise ValueError("supply all quantizer arrays together")
        if all(supplied):
            self.scaler_mean = np.asarray(self.scaler_mean, dtype=float).copy()
            self.scaler_scale = np.asarray(self.scaler_scale, dtype=float).copy()
            self.centers = np.asarray(self.centers, dtype=float).copy()
            if self.scaler_mean.ndim != 2 or self.scaler_mean.shape[0] != self.n_sensors:
                raise ValueError("invalid scaler mean shape")
            if self.scaler_scale.shape != self.scaler_mean.shape:
                raise ValueError("scaler mean and scale shapes differ")
            if self.centers.shape != (self.n_sensors, self.n_categories, self.scaler_mean.shape[1]):
                raise ValueError("invalid centroid shape")
            if not all(np.all(np.isfinite(x)) for x in [self.scaler_mean, self.scaler_scale, self.centers]):
                raise ValueError("quantizer parameters must be finite")
            if np.any(self.scaler_scale <= 0):
                raise ValueError("scaler scales must be positive")

    @property
    def n_sensors(self) -> int:
        return self.likelihood.shape[0]

    @property
    def n_categories(self) -> int:
        return self.likelihood.shape[2]

    def encode(self, features: np.ndarray) -> np.ndarray:
        """Apply frozen per-sensor transforms, without fitting or updating them."""
        if self.centers is None:
            raise ValueError("this hand-specified model has no fitted quantizers")
        features = _finite_matrix(features, "features")
        descriptor_count = self.scaler_mean.shape[1]
        if features.shape[1] != self.n_sensors * descriptor_count:
            raise ValueError("feature width does not match contiguous sensor blocks")
        encoded = np.empty((len(features), self.n_sensors), dtype=np.int16)
        for sensor in range(self.n_sensors):
            block = features[:, sensor * descriptor_count : (sensor + 1) * descriptor_count]
            standardized = (block - self.scaler_mean[sensor]) / self.scaler_scale[sensor]
            squared_distance = np.sum(
                (standardized[:, None, :] - self.centers[sensor][None, :, :]) ** 2,
                axis=2,
            )
            encoded[:, sensor] = np.argmin(squared_distance, axis=1)
        return encoded

    def to_dict(self) -> Dict[str, Any]:
        """JSON-ready complete parameters, including model-fitting provenance."""
        return {
            "classes": self.classes.tolist(),
            "prior": self.prior.tolist(),
            "likelihood": self.likelihood.tolist(),
            "scaler_mean": None if self.scaler_mean is None else self.scaler_mean.tolist(),
            "scaler_scale": None if self.scaler_scale is None else self.scaler_scale.tolist(),
            "centers": None if self.centers is None else self.centers.tolist(),
            "provenance": self.provenance,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SensorModel":
        return cls(**data)


def fit_sensor_model(
    X_train: np.ndarray,
    y_train: Sequence,
    *,
    classes: Optional[Sequence] = None,
    n_sensors: int = 16,
    features_per_sensor: int = 8,
    n_categories: int = 8,
    alpha: float = 1.0,
    seed: int = 20261001,
    row_ids: Optional[Sequence[str]] = None,
) -> SensorModel:
    """Fit only on supplied training rows using one CPU thread per library.

    Caller-owned splits are deliberate: calibration and evaluation arrays are
    not accepted by this function. All transforms and likelihood counts use
    the same training rows. Optional row IDs make that provenance auditable.
    """
    import sklearn
    from sklearn.cluster import KMeans
    from sklearn.preprocessing import StandardScaler
    from threadpoolctl import threadpool_limits

    started = perf_counter()
    X_train = _finite_matrix(X_train, "X_train")
    y_train = np.asarray(y_train)
    if n_sensors < 1 or features_per_sensor < 1 or n_categories < 1:
        raise ValueError("sensor, descriptor and category counts must be positive")
    if X_train.shape[1] != n_sensors * features_per_sensor:
        raise ValueError("training feature width does not match sensor blocks")
    if y_train.shape != (len(X_train),) or len(X_train) < n_categories:
        raise ValueError("training labels must align and rows must cover the category count")
    if not np.isfinite(alpha) or alpha <= 0:
        raise ValueError("additive smoothing alpha must be finite and positive")
    classes_array = np.unique(y_train) if classes is None else np.asarray(classes)
    if classes_array.ndim != 1 or len(classes_array) < 2 or len(np.unique(classes_array)) != len(classes_array):
        raise ValueError("classes must contain at least two distinct labels")
    if not np.all(np.isin(y_train, classes_array)):
        raise ValueError("training labels contain an undeclared class")
    ids = None if row_ids is None else [str(x) for x in row_ids]
    if ids is not None and (len(ids) != len(X_train) or len(set(ids)) != len(ids)):
        raise ValueError("training row IDs must be aligned and unique")

    means = np.empty((n_sensors, features_per_sensor))
    scales = np.empty_like(means)
    centers = np.empty((n_sensors, n_categories, features_per_sensor))
    encoded = np.empty((len(X_train), n_sensors), dtype=np.int16)
    with threadpool_limits(limits=1):
        for sensor in range(n_sensors):
            block = X_train[:, sensor * features_per_sensor : (sensor + 1) * features_per_sensor]
            scaler = StandardScaler().fit(block)
            standardized = scaler.transform(block)
            clusterer = KMeans(
                n_clusters=n_categories, n_init=10, max_iter=300,
                random_state=seed + sensor, algorithm="lloyd",
            ).fit(standardized)
            means[sensor] = scaler.mean_
            scales[sensor] = scaler.scale_
            centers[sensor] = clusterer.cluster_centers_
            # Use exactly the same distance/tie convention as future encode().
            distances = np.sum((standardized[:, None, :] - centers[sensor][None, :, :]) ** 2, axis=2)
            encoded[:, sensor] = np.argmin(distances, axis=1)

    class_counts = np.array([np.count_nonzero(y_train == label) for label in classes_array])
    prior = (class_counts + alpha) / (len(y_train) + alpha * len(classes_array))
    likelihood = np.empty((n_sensors, len(classes_array), n_categories))
    for sensor in range(n_sensors):
        for class_index, label in enumerate(classes_array):
            counts = np.bincount(encoded[y_train == label, sensor], minlength=n_categories)
            likelihood[sensor, class_index] = (counts + alpha) / (class_counts[class_index] + alpha * n_categories)
    return SensorModel(
        classes_array, prior, likelihood, means, scales, centers,
        provenance={
            "n_train": len(X_train), "training_row_ids": ids,
            "class_counts": class_counts.tolist(), "seed": int(seed), "alpha": float(alpha),
            "n_sensors": int(n_sensors), "features_per_sensor": int(features_per_sensor),
            "n_categories": int(n_categories), "kmeans_n_init": 10,
            "kmeans_max_iter": 300, "kmeans_algorithm": "lloyd", "library_threads": 1,
            "numpy_version": np.__version__, "sklearn_version": sklearn.__version__,
            "fit_elapsed_seconds": perf_counter() - started,
        },
    )


def observation_values(
    model: SensorModel,
    beliefs: np.ndarray,
    sensors: Optional[np.ndarray] = None,
) -> Tuple[np.ndarray, np.ndarray]:
    """Return exact one-observation information and terminal accuracy values.

    Inputs are N beliefs and optionally an N by M matrix of sensor indices.
    Outputs have axes (case, candidate sensor). No observed record is read.
    """
    beliefs = _finite_matrix(beliefs, "beliefs")
    if beliefs.shape[1] != len(model.classes) or np.any(beliefs < 0):
        raise ValueError("belief shape/probabilities do not match the model")
    if not np.allclose(beliefs.sum(axis=1), 1, rtol=0, atol=1e-12):
        raise ValueError("belief probabilities must sum to one")
    if sensors is None:
        sensors = np.broadcast_to(np.arange(model.n_sensors), (len(beliefs), model.n_sensors))
    sensors = np.asarray(sensors)
    if (sensors.ndim != 2 or sensors.shape[0] != len(beliefs)
            or not np.issubdtype(sensors.dtype, np.integer)
            or np.any(sensors < 0) or np.any(sensors >= model.n_sensors)):
        raise ValueError("candidate sensors must be aligned integer indices")
    likelihoods = model.likelihood[sensors]
    joint = beliefs[:, None, :, None] * likelihoods
    predicted = joint.sum(axis=2)
    information = _entropy_bits(predicted) - np.sum(
        beliefs[:, None, :] * _entropy_bits(likelihoods), axis=2,
    )
    # Exact mutual information is nonnegative. Only roundoff is clipped.
    if np.any(information < -1e-12):
        raise ArithmeticError("computed materially negative mutual information")
    information = np.maximum(information, 0.0)
    # E_z max_y posterior(y|z) = sum_z max_y joint(y,z), including zero-mass z.
    terminal_accuracy = joint.max(axis=2).sum(axis=2)
    return information, terminal_accuracy


def prior_sensor_order(model: SensorModel) -> np.ndarray:
    """Training-model prior mutual information, then ascending sensor index."""
    information, _ = observation_values(model, model.prior[None, :])
    remaining = list(range(model.n_sensors))
    ordered = []
    while remaining:
        best = int(_choose_sensor(information[:, remaining], np.asarray([remaining]))[0])
        ordered.append(best)
        remaining.remove(best)
    return np.asarray(ordered, dtype=int)


@dataclass(frozen=True)
class SensorPolicy:
    name: str
    kind: str = "weight"
    weight: float = 0.0
    penalty: float = 0.0
    count: Optional[int] = None
    order: Optional[Sequence[int]] = None

    def validate(self, n_sensors: int) -> None:
        if not self.name or self.kind not in {"weight", "direct", "fixed_cmi", "fixed_order", "zero", "all"}:
            raise ValueError("policy needs a name and a supported kind")
        if not np.isfinite(self.weight) or self.weight < 0 or not np.isfinite(self.penalty):
            raise ValueError("weight must be nonnegative and policy parameters finite")
        if self.kind != "weight" and self.weight != 0:
            raise ValueError("only weight policies accept a nonzero weight")
        if self.kind != "direct" and self.penalty != 0:
            raise ValueError("only direct policies accept a nonzero penalty")
        if self.kind in {"fixed_cmi", "fixed_order"}:
            if not isinstance(self.count, (int, np.integer)) or not 0 <= self.count <= n_sensors:
                raise ValueError("fixed-count policies need an integer count within the sensor range")
        elif self.count is not None:
            raise ValueError("only fixed-count policies accept count")
        if self.order is not None:
            order = np.asarray(self.order)
            if (self.kind != "fixed_order" or order.shape != (n_sensors,)
                    or not np.issubdtype(order.dtype, np.integer)
                    or not np.array_equal(np.sort(order), np.arange(n_sensors))):
                raise ValueError("fixed order must be a permutation of all sensor indices")


@dataclass
class ReplayResult:
    policy: SensorPolicy
    classes: np.ndarray
    row_ids: List[str]
    batches: np.ndarray
    true_labels: np.ndarray
    predictions: np.ndarray
    posteriors: np.ndarray
    correctness: np.ndarray
    usage: np.ndarray
    reward: np.ndarray
    acquisition_order: np.ndarray
    observations: np.ndarray
    candidate_evaluations: np.ndarray
    elapsed_seconds: float

    @property
    def order(self) -> np.ndarray:
        """Padded ordered sensor paths, also exposed under the descriptive name."""
        return self.acquisition_order

    @property
    def log_loss(self) -> np.ndarray:
        true_indices = np.argmax(self.true_labels[:, None] == self.classes[None, :], axis=1)
        with np.errstate(divide="ignore"):
            return -np.log(self.posteriors[np.arange(len(self.true_labels)), true_indices])

    @property
    def brier_score(self) -> np.ndarray:
        one_hot = self.true_labels[:, None] == self.classes[None, :]
        return np.sum((self.posteriors - one_hot) ** 2, axis=1)

    def metrics(self) -> Dict[str, Any]:
        """Descriptive metrics. Intervals and statistical replication are external."""
        present = np.unique(self.true_labels)
        return {
            "n_cases": len(self.true_labels),
            "accuracy": float(np.mean(self.correctness)),
            "balanced_accuracy": float(np.mean([
                self.correctness[self.true_labels == label].mean() for label in present
            ])),
            "usage": float(np.mean(self.usage)), "reward": float(np.mean(self.reward)),
            "log_loss": float(np.mean(self.log_loss)), "brier_score": float(np.mean(self.brier_score)),
            "elapsed_seconds": float(self.elapsed_seconds),
            "candidate_evaluations": int(self.candidate_evaluations.sum()),
        }

    def records(self) -> List[Dict[str, Any]]:
        """JSON-ready records. Timing is amortized batch time, not case latency."""
        policy_data = asdict(self.policy)
        if policy_data["order"] is not None:
            policy_data["order"] = list(map(int, policy_data["order"]))
        elapsed_per_case = self.elapsed_seconds / len(self.row_ids)
        logs, briers = self.log_loss, self.brier_score
        return [
            {
                "row_id": self.row_ids[i], "batch": self.batches[i].item(),
                "true_class": self.true_labels[i].item(), "policy": policy_data,
                "prediction": self.predictions[i].item(),
                "posterior_class_order": self.classes.tolist(),
                "posterior": self.posteriors[i].tolist(),
                "correctness": int(self.correctness[i]), "usage": int(self.usage[i]),
                "reward": float(self.reward[i]),
                "acquired_sensors": self.acquisition_order[i, :self.usage[i]].tolist(),
                "observed_categories": self.observations[i, :self.usage[i]].tolist(),
                "candidate_evaluations": int(self.candidate_evaluations[i]),
                "log_loss": float(logs[i]), "brier_score": float(briers[i]),
                "amortized_runtime_seconds": elapsed_per_case,
            }
            for i in range(len(self.row_ids))
        ]


def _replay_chunk(
    model: SensorModel,
    encoded: np.ndarray,
    policy: SensorPolicy,
    base_cost: float,
    fixed_order: np.ndarray,
) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    n = len(encoded)
    beliefs = np.tile(model.prior, (n, 1))
    available = np.ones((n, model.n_sensors), dtype=bool)
    usage = np.zeros(n, dtype=np.int16)
    order = np.full((n, model.n_sensors), -1, dtype=np.int16)
    observations = np.full_like(order, -1)
    evaluations = np.zeros(n, dtype=np.int64)
    active = np.arange(n)
    limit = 0 if policy.kind == "zero" else model.n_sensors
    if policy.kind in {"fixed_cmi", "fixed_order"}:
        limit = int(policy.count)
    for step in range(limit):
        if active.size == 0:
            break
        if policy.kind in {"fixed_order", "all"}:
            sensor = np.full(len(active), fixed_order[step], dtype=int)
        else:
            # Every active case has exactly 'step' acquisitions. Remaining
            # sensor indices are in ascending order, with no padded actions.
            candidates = np.nonzero(available[active])[1].reshape(len(active), model.n_sensors - step)
            information, accuracy = observation_values(model, beliefs[active], candidates)
            evaluations[active] += candidates.shape[1]
            if policy.kind == "fixed_cmi":
                scores = information
                sensor = _choose_sensor(scores, candidates)
            else:
                scores = accuracy - base_cost
                if policy.kind == "weight":
                    scores = scores + policy.weight * information
                else:
                    scores = scores - policy.penalty
                sensor = _choose_sensor(scores, candidates, beliefs[active].max(axis=1))
            keep = sensor >= 0
            active = active[keep]
            sensor = sensor[keep]
            if active.size == 0:
                break

        observed = encoded[active, sensor]
        posterior = beliefs[active] * model.likelihood[sensor, :, observed]
        mass = posterior.sum(axis=1)
        if np.any(mass <= 0):
            raise ValueError("actual record has zero predictive mass under the supplied model")
        beliefs[active] = posterior / mass[:, None]
        available[active, sensor] = False
        order[active, step] = sensor
        observations[active, step] = observed
        usage[active] += 1
    return beliefs, usage, order, observations, evaluations


def evaluate_policies(
    model: SensorModel,
    Z: np.ndarray,
    y: Sequence,
    policies: Sequence[SensorPolicy],
    *,
    row_ids: Optional[Sequence[str]] = None,
    batches: Optional[Sequence] = None,
    chunk_size: int = 512,
    base_cost: float = 0.02,
) -> Dict[str, ReplayResult]:
    """Replay policies on real encoded rows in aligned, memory-bounded batches.

    Labels are used only after policy replay to score terminal predictions.
    Direct policies use base_cost + penalty for selection but all returns are
    scored at base_cost. Result arrays retain the input row order for pairing.
    """
    encoded = np.asarray(Z)
    labels = np.asarray(y)
    if (encoded.ndim != 2 or encoded.shape[1] != model.n_sensors or len(encoded) == 0
            or not np.issubdtype(encoded.dtype, np.integer)
            or np.any(encoded < 0) or np.any(encoded >= model.n_categories)):
        raise ValueError("encoded data must be a nonempty matrix of valid integer categories")
    if labels.shape != (len(encoded),) or not np.all(np.isin(labels, model.classes)):
        raise ValueError("evaluation labels must align and belong to model classes")
    if not isinstance(chunk_size, (int, np.integer)) or chunk_size < 1:
        raise ValueError("chunk_size must be a positive integer")
    if not np.isfinite(base_cost) or base_cost < 0:
        raise ValueError("base_cost must be finite and nonnegative")
    ids = [str(i) for i in range(len(encoded))] if row_ids is None else [str(x) for x in row_ids]
    if len(ids) != len(encoded) or len(set(ids)) != len(ids):
        raise ValueError("row IDs must be aligned and unique")
    batch_values = np.full(len(encoded), -1) if batches is None else np.asarray(batches)
    if batch_values.shape != (len(encoded),):
        raise ValueError("batch metadata must align with encoded records")
    policies = list(policies)
    if len({p.name for p in policies}) != len(policies):
        raise ValueError("policy names must be unique")
    for policy in policies:
        policy.validate(model.n_sensors)
    default_order = prior_sensor_order(model)
    results = {}
    for policy in policies:
        started = perf_counter()
        n = len(encoded)
        beliefs = np.empty((n, len(model.classes)))
        usage = np.empty(n, dtype=np.int16)
        order = np.empty((n, model.n_sensors), dtype=np.int16)
        observations = np.empty_like(order)
        evaluations = np.empty(n, dtype=np.int64)
        fixed_order = default_order if policy.order is None else np.asarray(policy.order)
        # Full acquisition uses the same prior order. Its posterior is order
        # invariant, subject to ordinary floating-point multiplication error.
        for offset in range(0, n, chunk_size):
            stop = min(offset + chunk_size, n)
            b, u, actions, observed, counts = _replay_chunk(model, encoded[offset:stop], policy, base_cost, fixed_order)
            beliefs[offset:stop], usage[offset:stop] = b, u
            order[offset:stop], observations[offset:stop] = actions, observed
            evaluations[offset:stop] = counts
        class_priority = np.argsort(model.classes)
        predictions = model.classes[class_priority[np.argmax(beliefs[:, class_priority], axis=1)]]
        correctness = (predictions == labels).astype(np.int8)
        results[policy.name] = ReplayResult(
            policy, model.classes.copy(), ids.copy(), batch_values.copy(), labels.copy(),
            predictions, beliefs, correctness, usage, correctness - base_cost * usage,
            order, observations, evaluations, perf_counter() - started,
        )
    return results
