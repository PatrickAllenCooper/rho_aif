"""Integrity and hand-oracle checks for actual-record sensor acquisition."""

import json

import numpy as np
import pytest

from rho_aif.real_sensor import (
    SensorModel,
    SensorPolicy,
    evaluate_policies,
    fit_sensor_model,
    observation_values,
    prior_sensor_order,
)


@pytest.fixture
def two_sensor_model():
    return SensorModel(
        classes=np.array([1, 2]), prior=np.array([0.5, 0.5]),
        likelihood=np.array([
            [[0.8, 0.2], [0.2, 0.8]],
            [[0.6, 0.4], [0.4, 0.6]],
        ]),
    )


def test_one_step_values_against_hand_oracle(two_sensor_model):
    information, accuracy = observation_values(two_sensor_model, np.array([[0.5, 0.5], [0.8, 0.2]]))
    binary_entropy_08 = -(0.8 * np.log2(0.8) + 0.2 * np.log2(0.2))
    binary_entropy_06 = -(0.6 * np.log2(0.6) + 0.4 * np.log2(0.4))
    np.testing.assert_allclose(information[0], [1 - binary_entropy_08, 1 - binary_entropy_06])
    np.testing.assert_allclose(accuracy[0], [0.8, 0.6])
    # Once the 80%-accurate result is observed, another 60%-accurate result
    # cannot change the Bayes decision. Its instrumental gain is exactly zero.
    assert accuracy[1, 1] == pytest.approx(0.8)
    np.testing.assert_array_equal(prior_sensor_order(two_sensor_model), [0, 1])


def test_actual_rows_stop_and_reward_hand_oracle(two_sensor_model):
    data = np.array([[0, 1], [1, 0]])
    result = evaluate_policies(
        two_sensor_model, data, [1, 1], [SensorPolicy("reward_only")],
        base_cost=0.2, row_ids=["a", "b"], batches=[1, 1],
    )["reward_only"]
    np.testing.assert_array_equal(result.usage, [1, 1])
    np.testing.assert_array_equal(result.acquisition_order[:, 0], [0, 0])
    np.testing.assert_array_equal(result.observations[:, 0], [0, 1])
    np.testing.assert_allclose(result.posteriors, [[0.8, 0.2], [0.2, 0.8]])
    np.testing.assert_allclose(result.reward, [0.8, -0.2])
    assert result.metrics()["accuracy"] == 0.5
    assert result.metrics()["usage"] == 1
    assert result.records()[1]["observed_categories"] == [1]
    assert result.records()[0]["acquired_sensors"] == [0]


def test_weight_bonus_differs_from_direct_penalty(two_sensor_model):
    results = evaluate_policies(
        two_sensor_model, np.array([[0, 1]]), [1],
        [SensorPolicy("weight", weight=2), SensorPolicy("direct", kind="direct", penalty=0.28)],
    )
    # Reward-only first acquisition is tied with stopping: .8 - (.02+.28)=.5.
    assert results["direct"].usage[0] == 0
    # Information-weighted policy values the second sensor after the first.
    assert results["weight"].usage[0] == 2
    assert results["weight"].reward[0] == pytest.approx(0.96)
    np.testing.assert_allclose(results["weight"].posteriors[0], [8 / 11, 3 / 11])


def test_relative_tolerance_stops_and_sensor_ties_choose_lowest():
    model = SensorModel([1, 2], [0.5, 0.5], np.array([[[0.8, 0.2], [0.2, 0.8]]] * 2))
    results = evaluate_policies(
        model, np.array([[0, 1]]), [1],
        [SensorPolicy("tied"), SensorPolicy("forced", kind="fixed_cmi", count=1)],
        base_cost=0.3 - 1e-13,
    )
    assert results["tied"].usage[0] == 0
    assert results["forced"].acquisition_order[0, 0] == 0
    improving = evaluate_policies(model, np.array([[0, 1]]), [1], [SensorPolicy("improve")], base_cost=0.3 - 1e-10)
    assert improving["improve"].usage[0] == 1


def test_global_tolerance_differs_from_pairwise_near_tie_chaining():
    accuracies = np.array([0.7, 0.7 + 0.5e-12, 0.7 + 1.0e-12])
    model = SensorModel([1, 2], [0.5, 0.5], np.array([
        [[a, 1 - a], [1 - a, a]] for a in accuracies
    ]))
    result = evaluate_policies(model, np.array([[0, 0, 0]]), [1], [SensorPolicy("tolerance")])["tolerance"]
    # Scale is approximately .68, so sensor 1 lies within tolerance of the
    # maximum but sensor 0 does not. Pairwise comparisons would pick sensor 2.
    assert result.acquisition_order[0, 0] == 1


def test_terminal_tie_uses_lowest_class_id_with_unsorted_model():
    model = SensorModel([2, 1], [0.5, 0.5], [[[0.5, 0.5], [0.5, 0.5]]])
    result = evaluate_policies(model, np.array([[0]]), [1], [SensorPolicy("zero", kind="zero")])["zero"]
    assert result.predictions[0] == 1


def test_zero_all_fixed_and_subsidized_counts_without_repetition(two_sensor_model):
    policies = [
        SensorPolicy("zero", kind="zero"), SensorPolicy("all", kind="all"),
        SensorPolicy("cmi", kind="fixed_cmi", count=1),
        SensorPolicy("fixed", kind="fixed_order", count=2, order=[1, 0]),
        SensorPolicy("subsidized", kind="direct", penalty=-1),
    ]
    results = evaluate_policies(two_sensor_model, np.array([[0, 1], [1, 0]]), [1, 2], policies)
    for name, count in [("zero", 0), ("all", 2), ("cmi", 1), ("fixed", 2), ("subsidized", 2)]:
        np.testing.assert_array_equal(results[name].usage, [count, count])
        for row in results[name].acquisition_order:
            assert len(set(row[:count])) == count
    np.testing.assert_allclose(results["all"].posteriors, results["fixed"].posteriors)
    np.testing.assert_allclose(results["subsidized"].reward, [0.96, 0.96])
    np.testing.assert_array_equal(results["fixed"].observations, [[1, 0], [0, 1]])


def test_policy_does_not_observe_labels_and_chunking_is_invariant(two_sensor_model):
    data = np.array([[0, 1], [1, 0], [0, 0], [1, 1]])
    policy = [SensorPolicy("test", weight=0.25)]
    a = evaluate_policies(two_sensor_model, data, [1, 1, 1, 1], policy, chunk_size=1)["test"]
    b = evaluate_policies(two_sensor_model, data, [2, 2, 2, 2], policy, chunk_size=3)["test"]
    for name in ["usage", "acquisition_order", "observations", "posteriors", "predictions", "candidate_evaluations"]:
        np.testing.assert_array_equal(getattr(a, name), getattr(b, name))


def test_fixed_policy_observes_only_requested_sensor(two_sensor_model):
    # Modifying a never-requested sensor cannot affect the posterior or actions.
    result = evaluate_policies(
        two_sensor_model, np.array([[0, 0], [0, 1]]), [1, 1],
        [SensorPolicy("one", kind="fixed_order", count=1, order=[0, 1])],
    )["one"]
    np.testing.assert_array_equal(result.posteriors[0], result.posteriors[1])


def test_fit_training_only_blocks_smoothing_and_serialization():
    # Contiguous blocks have radically different means. The last descriptor is
    # constant, exercising StandardScaler's scale-one convention.
    training = np.array([[0, 2, 100, 7], [1, 2, 102, 7], [8, 2, 110, 7], [9, 2, 112, 7]], dtype=float)
    model = fit_sensor_model(
        training, [1, 1, 2, 2], classes=[1, 2, 3], n_sensors=2,
        features_per_sensor=2, n_categories=2, seed=31, row_ids=["a", "b", "c", "d"],
    )
    np.testing.assert_allclose(model.scaler_mean, [[4.5, 2], [106, 7]])
    np.testing.assert_allclose(model.scaler_scale[:, 1], 1)
    np.testing.assert_allclose(model.prior, [3 / 7, 3 / 7, 1 / 7])
    np.testing.assert_allclose(model.likelihood[:, 2], 0.5)
    np.testing.assert_allclose(model.likelihood.sum(axis=2), 1)
    before = json.dumps(model.to_dict(), sort_keys=True)
    model.encode(np.full((2, 4), 100000.0))
    assert json.dumps(model.to_dict(), sort_keys=True) == before
    clone = SensorModel.from_dict(json.loads(before))
    np.testing.assert_array_equal(clone.encode(training), model.encode(training))
    assert clone.provenance["training_row_ids"] == ["a", "b", "c", "d"]
    assert clone.provenance["sklearn_version"]
    # Counts use the encoder's precise assignment, rather than centroid index
    # identities or labels supplied by an external evaluation partition.
    encoded = model.encode(training)
    for sensor in range(2):
        expected = (np.bincount(encoded[:2, sensor], minlength=2) + 1) / 4
        np.testing.assert_allclose(model.likelihood[sensor, 0], expected)


def test_zero_probability_outcomes_and_impossible_actual_record():
    model = SensorModel([1, 2], [0.5, 0.5], [[[1, 0], [1, 0]]])
    information, accuracy = observation_values(model, [[0.5, 0.5]])
    np.testing.assert_allclose(information, 0)
    np.testing.assert_allclose(accuracy, 0.5)
    with pytest.raises(ValueError, match="zero predictive mass"):
        evaluate_policies(model, np.array([[1]]), [1], [SensorPolicy("all", kind="all")])


def test_metric_scores_use_class_order(two_sensor_model):
    result = evaluate_policies(two_sensor_model, np.array([[0, 0], [1, 1]]), [1, 2], [SensorPolicy("zero", kind="zero")])["zero"]
    np.testing.assert_allclose(result.log_loss, np.log(2))
    np.testing.assert_allclose(result.brier_score, 0.5)
    assert result.metrics()["balanced_accuracy"] == 0.5
    json.dumps(result.records())


@pytest.mark.parametrize("policy", [
    SensorPolicy("bad", kind="fixed_cmi", count=3),
    SensorPolicy("bad", kind="fixed_order", count=1, order=[0, 0]),
    SensorPolicy("bad", kind="direct", weight=1),
    SensorPolicy("bad", kind="weight", penalty=1),
    SensorPolicy("bad", weight=float("nan")),
])
def test_invalid_policy_rejected(two_sensor_model, policy):
    with pytest.raises(ValueError):
        evaluate_policies(two_sensor_model, np.array([[0, 1]]), [1], [policy])


def test_invalid_data_and_identity_rejected(two_sensor_model):
    for data in [np.array([[0.1, 1]]), np.array([[0, 2]]), np.array([[0]])]:
        with pytest.raises(ValueError):
            evaluate_policies(two_sensor_model, data, [1], [SensorPolicy("p")])
    with pytest.raises(ValueError, match="row IDs"):
        evaluate_policies(two_sensor_model, np.array([[0, 1], [1, 0]]), [1, 2], [SensorPolicy("p")], row_ids=["a", "a"])
    with pytest.raises(ValueError, match="unique"):
        evaluate_policies(two_sensor_model, np.array([[0, 1]]), [1], [SensorPolicy("p"), SensorPolicy("p")])
