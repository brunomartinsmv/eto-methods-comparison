import math

import pandas as pd

from scripts.metrics import compute_metrics


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
