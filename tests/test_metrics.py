import math

import numpy as np
import pandas as pd

from scripts.metrics import compute_metrics, mae, mbe, r2_score, rmse, willmott_d


def test_metric_functions_return_manually_verifiable_values() -> None:
    observed = np.array([1.0, 2.0, 3.0])
    estimated = np.array([1.0, 3.0, 2.0])

    assert math.isclose(rmse(observed, estimated), math.sqrt(2 / 3))
    assert math.isclose(mae(observed, estimated), 2 / 3)
    assert math.isclose(mbe(observed, estimated), 0.0)
    assert math.isclose(r2_score(observed, estimated), 0.25)
    assert math.isclose(willmott_d(observed, estimated), 2 / 3)


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
    assert math.isclose(row["r2"], 0.25)
    assert math.isclose(row["willmott_d"], 2 / 3)
