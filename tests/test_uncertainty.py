from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from scripts import metrics
from scripts.uncertainty import (
    _resample_indices,
    bias_by_eto_bin,
    bootstrap_metric_intervals,
    seasonal_error_metrics,
    write_uncertainty_report,
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
        "resampling",
        "block_length",
    }
    assert (intervals["resampling"] == "iid").all()
    assert (intervals["block_length"] == 1).all()
    assert (intervals["ci_lower"] <= intervals["estimate"]).all()
    assert (intervals["estimate"] <= intervals["ci_upper"]).all()

    ref = _sample_daily()["et_penman_monteith"].to_numpy(dtype=float)
    series = _sample_daily()["et_test"].to_numpy(dtype=float)
    draw = np.random.default_rng(123).integers(0, len(ref), size=(80, len(ref)))
    rmse_draws = np.array([metrics.rmse(ref[idx], series[idx]) for idx in draw], dtype=float)
    rmse_row = intervals.loc[intervals["metric"] == "rmse"].iloc[0]
    assert rmse_row["ci_lower"] == float(np.nanquantile(rmse_draws, 0.025))
    assert rmse_row["ci_upper"] == float(np.nanquantile(rmse_draws, 0.975))


def test_moving_block_records_length_and_matches_iid_at_length_one() -> None:
    iid = bootstrap_metric_intervals(
        _sample_daily(),
        ref_col="et_penman_monteith",
        method_cols=["et_test"],
        n_boot=40,
        random_state=7,
    )
    length_one = bootstrap_metric_intervals(
        _sample_daily(),
        ref_col="et_penman_monteith",
        method_cols=["et_test"],
        n_boot=40,
        random_state=7,
        scheme="moving-block",
        block_length=1,
    )
    blocks = bootstrap_metric_intervals(
        _sample_daily(),
        ref_col="et_penman_monteith",
        method_cols=["et_test"],
        n_boot=40,
        random_state=7,
        scheme="moving_block",
        block_length=4,
    )

    shared = ["method", "metric", "estimate", "ci_lower", "ci_upper", "n", "n_boot", "confidence"]
    assert length_one[shared].to_dict("records") == iid[shared].to_dict("records")
    assert (length_one["resampling"] == "moving_block").all()
    assert (length_one["block_length"] == 1).all()
    assert (blocks["resampling"] == "moving_block").all()
    assert (blocks["block_length"] == 4).all()
    assert blocks["estimate"].tolist() == iid["estimate"].tolist()
    assert blocks["ci_lower"].tolist() != iid["ci_lower"].tolist()


def test_moving_block_indices_are_contiguous_nonwrapping_segments() -> None:
    indices = _resample_indices(10, 4, 25, np.random.default_rng(0))

    assert indices.shape == (25, 10)
    for sample in indices:
        position = 0
        while position < 10:
            take = min(4, 10 - position)
            segment = sample[position : position + take]
            assert np.all(np.diff(segment) == 1)
            assert segment[0] >= 0
            assert segment[-1] < 10
            position += take


def test_moving_block_of_full_length_repeats_the_paired_series() -> None:
    n = len(_sample_daily())
    intervals = bootstrap_metric_intervals(
        _sample_daily(),
        ref_col="et_penman_monteith",
        method_cols=["et_test"],
        n_boot=15,
        random_state=1,
        scheme="moving_block",
        block_length=n,
    )

    assert (intervals["ci_lower"] == intervals["estimate"]).all()
    assert (intervals["ci_upper"] == intervals["estimate"]).all()
    assert (intervals["block_length"] == n).all()


def test_bootstrap_rejects_invalid_scheme_and_block_length() -> None:
    with pytest.raises(ValueError, match="bootstrap scheme"):
        bootstrap_metric_intervals(
            _sample_daily(),
            ref_col="et_penman_monteith",
            method_cols=["et_test"],
            scheme="circular",
        )
    with pytest.raises(ValueError, match="block_length 1"):
        bootstrap_metric_intervals(
            _sample_daily(),
            ref_col="et_penman_monteith",
            method_cols=["et_test"],
            scheme="iid",
            block_length=3,
        )
    with pytest.raises(ValueError, match="exceeds"):
        bootstrap_metric_intervals(
            _sample_daily(),
            ref_col="et_penman_monteith",
            method_cols=["et_test"],
            scheme="moving_block",
            block_length=len(_sample_daily()) + 1,
        )


def test_uncertainty_report_names_the_moving_block_length(tmp_path) -> None:
    intervals = bootstrap_metric_intervals(
        _sample_daily(),
        ref_col="et_penman_monteith",
        method_cols=["et_test"],
        n_boot=5,
        scheme="moving_block",
        block_length=3,
    )
    path = write_uncertainty_report(
        "manaus",
        intervals,
        seasonal_error_metrics(
            _sample_daily(),
            ref_col="et_penman_monteith",
            method_cols=["et_test"],
        ),
        bias_by_eto_bin(
            _sample_daily(),
            ref_col="et_penman_monteith",
            method_cols=["et_test"],
        ),
        tmp_path,
    )
    text = path.read_text(encoding="utf-8")
    assert "moving-block" in text
    assert "block length 3" in text
    assert "block_length" in text


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
