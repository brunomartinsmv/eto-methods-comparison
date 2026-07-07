from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

from . import eto_methods, metrics
from .config import REFERENCE_COLUMN
from .naming import calibration_coefficients_filename, calibration_metrics_filename

OBJECTIVE = "minimize_train_rmse"


@dataclass(frozen=True)
class CalibratableMethod:
    method: str
    original_column: str
    calibrated_column: str
    coefficient_name: str
    predictor: Callable[[pd.DataFrame, float], pd.Series]


@dataclass(frozen=True)
class CalibrationResult:
    coefficients: pd.DataFrame
    metrics: pd.DataFrame
    predictions: pd.DataFrame


def _hargreaves_samani(df: pd.DataFrame, coefficient: float) -> pd.Series:
    return pd.Series(
        eto_methods.hargreaves_samani(
            t_min_c=df["tmin_c"],
            t_max_c=df["tmax_c"],
            t_mean_c=df["tmed_c"],
            ra_mj_m2_day=df["ra_extraterrestre_mj_m2_d"],
            coefficient=coefficient,
        ),
        index=df.index,
    )


def _turc(df: pd.DataFrame, coefficient: float) -> pd.Series:
    rh = df["rh_mean_pct"] if "rh_mean_pct" in df.columns else None
    return pd.Series(
        eto_methods.turc(
            t_mean_c=df["tmed_c"],
            rs_mj_m2_day=df["rad_global_mj_m2_d"],
            rh_mean_pct=rh,
            coefficient=coefficient,
        ),
        index=df.index,
    )


def _radiation_temperature(df: pd.DataFrame, coefficient: float) -> pd.Series:
    return pd.Series(
        eto_methods.radiation_temperature(
            t_mean_c=df["tmed_c"],
            rs_mj_m2_day=df["rad_global_mj_m2_d"],
            coefficient=coefficient,
        ),
        index=df.index,
    )


CALIBRATABLE_METHODS: dict[str, CalibratableMethod] = {
    "hargreaves_samani": CalibratableMethod(
        method="hargreaves_samani",
        original_column="et_hargreaves_samani",
        calibrated_column="et_hargreaves_samani_calibrated",
        coefficient_name="coefficient",
        predictor=_hargreaves_samani,
    ),
    "turc": CalibratableMethod(
        method="turc",
        original_column="et_turc",
        calibrated_column="et_turc_calibrated",
        coefficient_name="coefficient",
        predictor=_turc,
    ),
    "radiation_temperature": CalibratableMethod(
        method="radiation_temperature",
        original_column="et_radiation_temperature",
        calibrated_column="et_radiation_temperature_calibrated",
        coefficient_name="coefficient",
        predictor=_radiation_temperature,
    ),
}


def _require_columns(df: pd.DataFrame, columns: list[str], method: str) -> None:
    missing = [column for column in columns if column not in df.columns]
    if missing:
        raise ValueError(f"Method '{method}' requires missing columns: {', '.join(missing)}")


def _method_requirements(method: str) -> list[str]:
    if method == "hargreaves_samani":
        return ["tmin_c", "tmax_c", "tmed_c", "ra_extraterrestre_mj_m2_d"]
    if method in {"turc", "radiation_temperature"}:
        return ["tmed_c", "rad_global_mj_m2_d"]
    raise ValueError(f"Unsupported calibration method '{method}'")


def _date_mask(df: pd.DataFrame, start: str, end: str) -> pd.Series:
    dates = pd.to_datetime(df["date"])
    return (dates >= pd.Timestamp(start)) & (dates <= pd.Timestamp(end))


def _default_temporal_split(df: pd.DataFrame) -> tuple[str, str, str, str]:
    dates = pd.Series(pd.to_datetime(df["date"]).dropna().sort_values().unique())
    if len(dates) < 2:
        raise ValueError("Need at least two dates for separate train/test calibration")
    split_idx = max(1, int(np.floor(len(dates) * 0.7)))
    if split_idx >= len(dates):
        split_idx = len(dates) - 1
    return (
        str(dates.iloc[0].date()),
        str(dates.iloc[split_idx - 1].date()),
        str(dates.iloc[split_idx].date()),
        str(dates.iloc[-1].date()),
    )


def _resolve_split(
    df: pd.DataFrame,
    train_start: str | None,
    train_end: str | None,
    test_start: str | None,
    test_end: str | None,
) -> tuple[str, str, str, str]:
    if not any([train_start, train_end, test_start, test_end]):
        return _default_temporal_split(df)
    if not all([train_start, train_end, test_start, test_end]):
        raise ValueError("Provide all split dates: train-start, train-end, test-start, test-end")
    assert train_start is not None
    assert train_end is not None
    assert test_start is not None
    assert test_end is not None
    if pd.Timestamp(train_end) >= pd.Timestamp(test_start):
        raise ValueError("Training period must end before the test period starts")
    return train_start, train_end, test_start, test_end


def _fit_scalar_coefficient(predictor_at_one: pd.Series, reference: pd.Series) -> float:
    mask = np.isfinite(predictor_at_one.to_numpy()) & np.isfinite(reference.to_numpy())
    x = predictor_at_one.to_numpy(dtype=float)[mask]
    y = reference.to_numpy(dtype=float)[mask]
    if len(x) == 0:
        raise ValueError("No finite train observations available for calibration")
    denom = float(np.dot(x, x))
    if denom == 0:
        raise ValueError("Cannot calibrate coefficient from a zero predictor")
    return float(np.dot(x, y) / denom)


def _metrics_for_period(
    df: pd.DataFrame,
    *,
    period: str,
    ref_col: str,
    original_col: str,
    calibrated_col: str,
) -> pd.DataFrame:
    period_metrics = metrics.compute_metrics(df, ref_col, [original_col, calibrated_col])
    period_metrics.insert(0, "period", period)
    period_metrics.insert(1, "variant", ["original", "calibrated"])
    return period_metrics


def _require_finite_metric_pairs(
    df: pd.DataFrame,
    *,
    period: str,
    ref_col: str,
    method_cols: list[str],
) -> None:
    ref = df[ref_col].to_numpy()
    for method_col in method_cols:
        series = df[method_col].to_numpy()
        finite_pairs = np.isfinite(ref) & np.isfinite(series)
        if not finite_pairs.any():
            raise ValueError(
                f"No finite {period} observations available for {method_col} "
                f"against {ref_col}"
            )


def calibrate_method(
    df: pd.DataFrame,
    *,
    method: str,
    train_start: str | None = None,
    train_end: str | None = None,
    test_start: str | None = None,
    test_end: str | None = None,
    reference_col: str = REFERENCE_COLUMN,
) -> CalibrationResult:
    if method not in CALIBRATABLE_METHODS:
        available = ", ".join(sorted(CALIBRATABLE_METHODS))
        raise ValueError(f"Unsupported calibration method '{method}'. Available: {available}")
    if "date" not in df.columns:
        raise ValueError("Calibration input must include a date column")
    if reference_col not in df.columns:
        raise ValueError(f"Reference column '{reference_col}' not found")

    spec = CALIBRATABLE_METHODS[method]
    _require_columns(df, _method_requirements(method), method)

    train_start, train_end, test_start, test_end = _resolve_split(
        df,
        train_start,
        train_end,
        test_start,
        test_end,
    )
    train_mask = _date_mask(df, train_start, train_end)
    test_mask = _date_mask(df, test_start, test_end)
    if (train_mask & test_mask).any():
        raise ValueError("Training and test periods must not overlap")
    if not train_mask.any() or not test_mask.any():
        raise ValueError("Training and test periods must both contain observations")

    predictions = df.copy()
    predictions[spec.original_column] = spec.predictor(predictions, default_coefficient(method))

    train_base = spec.predictor(predictions.loc[train_mask], 1.0)
    coefficient = _fit_scalar_coefficient(train_base, predictions.loc[train_mask, reference_col])
    predictions[spec.calibrated_column] = spec.predictor(predictions, coefficient)
    method_cols = [spec.original_column, spec.calibrated_column]

    _require_finite_metric_pairs(
        predictions.loc[train_mask],
        period="train",
        ref_col=reference_col,
        method_cols=method_cols,
    )
    _require_finite_metric_pairs(
        predictions.loc[test_mask],
        period="test",
        ref_col=reference_col,
        method_cols=method_cols,
    )

    train_metrics = _metrics_for_period(
        predictions.loc[train_mask],
        period="train",
        ref_col=reference_col,
        original_col=method_cols[0],
        calibrated_col=method_cols[1],
    )
    test_metrics = _metrics_for_period(
        predictions.loc[test_mask],
        period="test",
        ref_col=reference_col,
        original_col=method_cols[0],
        calibrated_col=method_cols[1],
    )

    coefficients = pd.DataFrame(
        [
            {
                "method": f"{method}_calibrated",
                "base_method": method,
                "coefficient_name": spec.coefficient_name,
                spec.coefficient_name: coefficient,
                "objective": OBJECTIVE,
                "reference": reference_col,
                "train_start": train_start,
                "train_end": train_end,
                "test_start": test_start,
                "test_end": test_end,
                "n_train": int(train_mask.sum()),
                "n_test": int(test_mask.sum()),
            }
        ]
    )
    return CalibrationResult(
        coefficients=coefficients,
        metrics=pd.concat([train_metrics, test_metrics], ignore_index=True),
        predictions=predictions,
    )


def default_coefficient(method: str) -> float:
    if method == "hargreaves_samani":
        return 0.0023
    if method == "turc":
        return 0.013
    if method == "radiation_temperature":
        return 0.01
    raise ValueError(f"Unsupported calibration method '{method}'")


def write_calibration_outputs(
    result: CalibrationResult,
    *,
    output_dir: Path,
    site: str,
    method: str,
) -> tuple[Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    coefficients_path = output_dir / calibration_coefficients_filename(site, method)
    metrics_path = output_dir / calibration_metrics_filename(site, method)
    result.coefficients.to_csv(coefficients_path, index=False)
    result.metrics.to_csv(metrics_path, index=False)
    return coefficients_path, metrics_path
