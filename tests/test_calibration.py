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
    assert result.coefficients.loc[0, "exponent"] == pytest.approx(0.5)
    assert result.coefficients.loc[0, "exponent_status"] == "fixed"

    before = result.metrics.query("period == 'test' and variant == 'original'").iloc[0]
    after = result.metrics.query("period == 'test' and variant == 'calibrated'").iloc[0]
    assert after["method"] == "et_hargreaves_samani_calibrated"
    assert after["rmse"] < before["rmse"]
    assert after["rmse"] < 1e-12


def test_calibration_original_variant_recomputes_same_form_baseline() -> None:
    df = _synthetic_hargreaves_frame()
    df["et_hargreaves_samani"] = 99.0

    result = calibration.calibrate_method(
        df,
        method="hargreaves_samani",
        train_start="2024-01-01",
        train_end="2024-01-04",
        test_start="2024-01-05",
        test_end="2024-01-08",
    )

    expected_baseline = hargreaves_samani(
        t_min_c=df["tmin_c"],
        t_max_c=df["tmax_c"],
        t_mean_c=df["tmed_c"],
        ra_mj_m2_day=df["ra_extraterrestre_mj_m2_d"],
        coefficient=calibration.default_coefficient("hargreaves_samani"),
    )
    assert result.predictions["et_hargreaves_samani"].to_numpy() == pytest.approx(
        expected_baseline.to_numpy()
    )
    before = result.metrics.query("period == 'test' and variant == 'original'").iloc[0]
    after = result.metrics.query("period == 'test' and variant == 'calibrated'").iloc[0]
    assert before["rmse"] < 10.0
    assert after["rmse"] < before["rmse"]


def test_calibration_requires_finite_test_pairs() -> None:
    df = _synthetic_hargreaves_frame()
    df.loc[df["date"] >= "2024-01-05", "et_penman_monteith"] = np.nan

    with pytest.raises(ValueError, match="No finite test observations"):
        calibration.calibrate_method(
            df,
            method="hargreaves_samani",
            train_start="2024-01-01",
            train_end="2024-01-04",
            test_start="2024-01-05",
            test_end="2024-01-08",
        )


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


def _varying_hargreaves_frame(
    *,
    coefficient: float,
    exponent: float,
    n_days: int = 40,
    start: str = "2024-01-01",
) -> pd.DataFrame:
    dates = pd.date_range(start, periods=n_days, freq="D")
    tmin = np.linspace(16.0, 22.0, n_days)
    tmax = tmin + np.linspace(4.0, 15.0, n_days)
    df = pd.DataFrame(
        {
            "date": dates,
            "tmin_c": tmin,
            "tmax_c": tmax,
            "tmed_c": (tmin + tmax) / 2.0,
            "ra_extraterrestre_mj_m2_d": np.linspace(28.0, 40.0, n_days),
        }
    )
    df["et_penman_monteith"] = hargreaves_samani(
        t_min_c=df["tmin_c"],
        t_max_c=df["tmax_c"],
        t_mean_c=df["tmed_c"],
        ra_mj_m2_day=df["ra_extraterrestre_mj_m2_d"],
        coefficient=coefficient,
        exponent=exponent,
    )
    return df


def test_free_exponent_recovers_generating_parameters_and_keeps_train_test() -> None:
    df = _varying_hargreaves_frame(coefficient=0.0019, exponent=0.35)
    result = calibration.calibrate_method(
        df,
        method="hargreaves_samani",
        train_start="2024-01-01",
        train_end="2024-01-28",
        test_start="2024-01-29",
        test_end="2024-02-09",
        fit_exponent=True,
    )

    assert result.coefficients.loc[0, "exponent_status"] == "fitted"
    assert result.coefficients.loc[0, "exponent"] == pytest.approx(0.35, abs=2e-4)
    assert result.coefficients.loc[0, "coefficient"] == pytest.approx(0.0019, rel=1e-3, abs=1e-5)
    assert set(result.metrics["period"]) == {"train", "test"}
    assert set(result.metrics["variant"]) == {"original", "calibrated"}
    test_calibrated = result.metrics.query("period == 'test' and variant == 'calibrated'").iloc[0]
    assert test_calibrated["rmse"] < 1e-6

    published = hargreaves_samani(
        t_min_c=df["tmin_c"],
        t_max_c=df["tmax_c"],
        t_mean_c=df["tmed_c"],
        ra_mj_m2_day=df["ra_extraterrestre_mj_m2_d"],
        coefficient=calibration.default_coefficient("hargreaves_samani"),
        exponent=calibration.HARGREAVES_EXPONENT_DEFAULT,
    )
    assert result.predictions["et_hargreaves_samani"].to_numpy() == pytest.approx(
        np.asarray(published, dtype=float)
    )


def test_free_exponent_keeps_published_exponent_when_range_does_not_identify_it() -> None:
    result = calibration.calibrate_method(
        _synthetic_hargreaves_frame(),
        method="hargreaves_samani",
        train_start="2024-01-01",
        train_end="2024-01-04",
        test_start="2024-01-05",
        test_end="2024-01-08",
        fit_exponent=True,
    )

    assert result.coefficients.loc[0, "exponent"] == pytest.approx(0.5)
    assert result.coefficients.loc[0, "coefficient"] == pytest.approx(0.0031)
    assert result.coefficients.loc[0, "exponent_status"] == "fitted"
    assert set(result.metrics["period"]) == {"train", "test"}


def test_free_exponent_is_rejected_for_other_methods() -> None:
    with pytest.raises(ValueError, match="hargreaves_samani"):
        calibration.calibrate_method(
            _synthetic_hargreaves_frame(),
            method="turc",
            fit_exponent=True,
        )


def test_hargreaves_exponent_search_is_not_a_single_regional_value() -> None:
    assert calibration.HARGREAVES_EXPONENT_DEFAULT == 0.5
    assert calibration.HARGREAVES_EXPONENT_MIN < 0.5 < calibration.HARGREAVES_EXPONENT_MAX
    width = calibration.HARGREAVES_EXPONENT_MAX - calibration.HARGREAVES_EXPONENT_MIN
    assert width > 1.0
    source = Path(__file__).resolve().parents[1].joinpath("scripts", "calibration.py").read_text()
    assert "0.424" not in source
    assert "0.0021" not in source
    assert "0.0027" not in source


def test_cross_site_transfer_uses_fit_site_and_places_variants_side_by_side() -> None:
    alpha = _varying_hargreaves_frame(coefficient=0.004, exponent=0.5, n_days=20)
    beta = _varying_hargreaves_frame(coefficient=0.0018, exponent=0.5, n_days=20)
    same = alpha.copy()
    split = dict(
        train_start="2024-01-01",
        train_end="2024-01-14",
        test_start="2024-01-15",
        test_end="2024-01-20",
    )
    alpha_fit = calibration.calibrate_method(alpha, method="hargreaves_samani", **split)
    beta_fit = calibration.calibrate_method(beta, method="hargreaves_samani", **split)

    table = calibration.cross_site_transfer(
        {"alpha": alpha, "beta": beta, "same": same},
        method="hargreaves_samani",
        **split,
    )

    columns = list(table.columns)
    assert columns.index("calibrated_rmse") == columns.index("original_rmse") + 1
    alpha_to_beta = table.query("fit_site == 'alpha' and score_site == 'beta'").iloc[0]
    assert alpha_to_beta["coefficient"] == pytest.approx(alpha_fit.coefficients.loc[0, "coefficient"])
    assert alpha_to_beta["coefficient"] != pytest.approx(beta_fit.coefficients.loc[0, "coefficient"])
    assert alpha_to_beta["exponent"] == pytest.approx(0.5)
    assert alpha_to_beta["exponent_status"] == "fixed"
    assert alpha_to_beta["score_days"] == "all_finite_days"
    assert alpha_to_beta["n_score"] == 20
    assert alpha_to_beta["fit_train_start"] == "2024-01-01"
    assert alpha_to_beta["fit_test_end"] == "2024-01-20"
    alpha_to_same = table.query("fit_site == 'alpha' and score_site == 'same'").iloc[0]
    assert alpha_to_same["calibrated_rmse"] < 1e-8
    assert alpha_to_same["calibrated_rmse"] < alpha_to_same["original_rmse"]


def test_cross_site_transfer_carries_the_fit_site_exponent() -> None:
    alpha = _varying_hargreaves_frame(coefficient=0.0026, exponent=0.4, n_days=30)
    beta = _varying_hargreaves_frame(coefficient=0.002, exponent=0.7, n_days=30, start="2024-03-01")
    alpha_fit = calibration.calibrate_method(alpha, method="hargreaves_samani", fit_exponent=True)
    table = calibration.cross_site_transfer(
        {"alpha": alpha, "beta": beta},
        method="hargreaves_samani",
        fit_exponent=True,
    )
    alpha_to_beta = table.query("fit_site == 'alpha' and score_site == 'beta'").iloc[0]
    assert alpha_to_beta["exponent"] == pytest.approx(alpha_fit.coefficients.loc[0, "exponent"])
    assert alpha_to_beta["exponent"] == pytest.approx(0.4, abs=2e-4)
    assert alpha_to_beta["exponent_status"] == "fitted"
    assert alpha_to_beta["coefficient"] == pytest.approx(alpha_fit.coefficients.loc[0, "coefficient"])
    assert set(alpha_fit.metrics["period"]) == {"train", "test"}
    assert pd.Timestamp(alpha_to_beta["score_start"]) == pd.Timestamp("2024-03-01")


def test_cross_site_transfer_requires_two_sites() -> None:
    with pytest.raises(ValueError, match="at least two"):
        calibration.cross_site_transfer(
            {"only": _synthetic_hargreaves_frame()},
            method="hargreaves_samani",
            train_start="2024-01-01",
            train_end="2024-01-04",
            test_start="2024-01-05",
            test_end="2024-01-08",
        )
