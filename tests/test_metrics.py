import math

import numpy as np
import pandas as pd

from scripts.metrics import (
    classify_confidence,
    compute_metrics,
    confidence_c,
    mae,
    mbe,
    pearson_r,
    r2_score,
    rmse,
    willmott_d,
)


def test_metric_functions_return_manually_verifiable_values() -> None:
    observed = np.array([1.0, 2.0, 3.0])
    estimated = np.array([1.0, 3.0, 2.0])

    assert math.isclose(rmse(observed, estimated), math.sqrt(2 / 3))
    assert math.isclose(mae(observed, estimated), 2 / 3)
    assert math.isclose(mbe(observed, estimated), 0.0)
    assert math.isclose(pearson_r(observed, estimated), 0.5)
    assert math.isclose(r2_score(observed, estimated), 0.25)
    assert math.isclose(willmott_d(observed, estimated), 2 / 3)
    assert math.isclose(confidence_c(observed, estimated), 1 / 3)


def test_compute_metrics_ignores_nan_pairs_and_reports_standard_scores() -> None:
    df = pd.DataFrame(
        {
            "reference": [1.0, 2.0, 3.0, float("nan")],
            "method": [1.0, 3.0, 2.0, 4.0],
        }
    )

    result = compute_metrics(df, "reference", ["method"])

    row = result.iloc[0]
    assert row["method"] == "method"
    assert math.isclose(row["rmse"], math.sqrt(2 / 3))
    assert math.isclose(row["mae"], 2 / 3)
    assert math.isclose(row["mbe"], 0.0)
    assert math.isclose(row["r"], 0.5)
    assert math.isclose(row["r2"], 0.25)
    assert math.isclose(row["willmott_d"], 2 / 3)
    assert math.isclose(row["c"], 1 / 3)
    assert row["classification"] == "Very Poor"


def test_classify_confidence_covers_literature_thresholds() -> None:
    assert classify_confidence(0.86) == "Excellent"
    assert classify_confidence(0.85) == "Very Good"
    assert classify_confidence(0.76) == "Very Good"
    assert classify_confidence(0.75) == "Good"
    assert classify_confidence(0.66) == "Good"
    assert classify_confidence(0.65) == "Average"
    assert classify_confidence(0.61) == "Average"
    assert classify_confidence(0.60) == "Poor"
    assert classify_confidence(0.51) == "Poor"
    assert classify_confidence(0.50) == "Bad"
    assert classify_confidence(0.41) == "Bad"
    assert classify_confidence(0.40) == "Very Poor"
    assert classify_confidence(float("nan")) == ""


def test_correlation_metrics_return_nan_safely_for_constant_or_too_short_series() -> None:
    assert math.isnan(pearson_r(np.array([1.0]), np.array([1.0])))
    assert math.isnan(confidence_c(np.array([1.0, 1.0]), np.array([2.0, 2.0])))
