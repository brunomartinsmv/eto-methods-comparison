from __future__ import annotations

import pandas as pd

from scripts.uncertainty import (
    bias_by_eto_bin,
    bootstrap_metric_intervals,
    seasonal_error_metrics,
)


def _sample_daily() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "date": pd.to_datetime(
                [
                    "2024-01-01",
                    "2024-01-02",
                    "2024-02-01",
                    "2024-02-02",
                    "2024-08-01",
                    "2024-08-02",
                    "2024-09-01",
                    "2024-09-02",
                ]
            ),
            "rain_mm": [20.0, 30.0, 10.0, 20.0, 0.0, 1.0, 2.0, 0.0],
            "et_penman_monteith": [2.0, 3.0, 3.0, 4.0, 5.0, 6.0, 6.0, 7.0],
            "et_test": [2.5, 3.5, 2.5, 3.5, 4.0, 5.0, 7.0, 8.0],
        }
    )


def test_bootstrap_metric_intervals_are_reproducible_and_include_point_estimates() -> None:
    intervals = bootstrap_metric_intervals(
        _sample_daily(),
        ref_col="et_penman_monteith",
        method_cols=["et_test"],
        n_boot=80,
        random_state=123,
    )

    repeat = bootstrap_metric_intervals(
        _sample_daily(),
        ref_col="et_penman_monteith",
        method_cols=["et_test"],
        n_boot=80,
        random_state=123,
    )

    assert intervals.to_dict("records") == repeat.to_dict("records")
    assert set(intervals["metric"]) == {"rmse", "mae", "mbe"}
    assert set(intervals.columns) == {
        "method",
        "metric",
        "estimate",
        "ci_lower",
        "ci_upper",
        "n",
        "n_boot",
        "confidence",
    }
    assert (intervals["ci_lower"] <= intervals["estimate"]).all()
    assert (intervals["estimate"] <= intervals["ci_upper"]).all()


def test_seasonal_error_metrics_returns_monthly_and_rainfall_season_rows() -> None:
    seasonal = seasonal_error_metrics(
        _sample_daily(),
        ref_col="et_penman_monteith",
        method_cols=["et_test"],
        rainfall_col="rain_mm",
    )

    monthly = seasonal[seasonal["period_type"] == "month"]
    seasons = seasonal[seasonal["period_type"] == "rainfall_season"]

    assert monthly["period"].tolist() == ["2024-01", "2024-02", "2024-08", "2024-09"]
    assert set(seasons["period"]) == {"wet", "dry"}
    assert set(seasonal.columns) == {
        "period_type",
        "period",
        "method",
        "n",
        "rain_mm",
        "rmse",
        "mae",
        "mbe",
    }


def test_bias_by_eto_bin_summarizes_bias_across_reference_quantiles() -> None:
    bins = bias_by_eto_bin(
        _sample_daily(),
        ref_col="et_penman_monteith",
        method_cols=["et_test"],
        n_bins=4,
    )

    assert len(bins) == 4
    assert bins["eto_bin"].tolist() == [1, 2, 3, 4]
    assert set(bins.columns) == {
        "method",
        "eto_bin",
        "eto_min",
        "eto_max",
        "n",
        "mean_ref_eto",
        "mean_bias",
        "median_bias",
    }
    assert bins.loc[bins["eto_bin"] == 1, "mean_bias"].iloc[0] == 0.5
