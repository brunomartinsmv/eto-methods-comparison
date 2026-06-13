from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from scripts import calibration
from scripts.eto_methods import hargreaves_samani


def _synthetic_hargreaves_frame() -> pd.DataFrame:
    dates = pd.date_range("2024-01-01", periods=8, freq="D")
    df = pd.DataFrame(
        {
            "date": dates,
            "tmin_c": np.linspace(20.0, 21.4, len(dates)),
            "tmax_c": np.linspace(30.0, 31.4, len(dates)),
            "tmed_c": np.linspace(25.0, 26.4, len(dates)),
            "ra_extraterrestre_mj_m2_d": np.linspace(34.0, 37.5, len(dates)),
        }
    )
    df["et_penman_monteith"] = hargreaves_samani(
        t_min_c=df["tmin_c"],
        t_max_c=df["tmax_c"],
        t_mean_c=df["tmed_c"],
        ra_mj_m2_day=df["ra_extraterrestre_mj_m2_d"],
        coefficient=0.0031,
    )
    df["et_hargreaves_samani"] = hargreaves_samani(
        t_min_c=df["tmin_c"],
        t_max_c=df["tmax_c"],
        t_mean_c=df["tmed_c"],
        ra_mj_m2_day=df["ra_extraterrestre_mj_m2_d"],
    )
    return df


def test_calibrate_method_uses_train_split_and_reports_test_improvement() -> None:
    result = calibration.calibrate_method(
        _synthetic_hargreaves_frame(),
        method="hargreaves_samani",
        train_start="2024-01-01",
        train_end="2024-01-04",
        test_start="2024-01-05",
        test_end="2024-01-08",
    )

    assert result.coefficients.loc[0, "method"] == "hargreaves_samani_calibrated"
    assert result.coefficients.loc[0, "coefficient"] == pytest.approx(0.0031)
    assert result.coefficients.loc[0, "train_start"] == "2024-01-01"
    assert result.coefficients.loc[0, "test_end"] == "2024-01-08"
    assert result.coefficients.loc[0, "objective"] == "minimize_train_rmse"

    before = result.metrics.query("period == 'test' and variant == 'original'").iloc[0]
    after = result.metrics.query("period == 'test' and variant == 'calibrated'").iloc[0]
    assert after["method"] == "et_hargreaves_samani_calibrated"
    assert after["rmse"] < before["rmse"]
    assert after["rmse"] < 1e-12


def test_write_calibration_outputs_uses_separate_coefficient_and_metric_files(tmp_path: Path) -> None:
    result = calibration.calibrate_method(
        _synthetic_hargreaves_frame(),
        method="hargreaves_samani",
        train_start="2024-01-01",
        train_end="2024-01-04",
        test_start="2024-01-05",
        test_end="2024-01-08",
    )

    coefficient_path, metrics_path = calibration.write_calibration_outputs(
        result,
        output_dir=tmp_path,
        site="manaus",
        method="hargreaves_samani",
    )

    assert coefficient_path == tmp_path / "manaus_hargreaves_samani_calibration_coefficients.csv"
    assert metrics_path == tmp_path / "manaus_hargreaves_samani_calibration_metrics.csv"
    assert "hargreaves_samani_calibrated" in coefficient_path.read_text()
    metrics_df = pd.read_csv(metrics_path)
    assert set(metrics_df["variant"]) == {"original", "calibrated"}
