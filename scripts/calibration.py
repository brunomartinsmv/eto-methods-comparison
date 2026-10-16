from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

from . import eto_methods, metrics
from .config import REFERENCE_COLUMN
from .conversions import mj_m2_day_to_mm_day
from .naming import (
    calibration_coefficients_filename,
    calibration_metrics_filename,
    calibration_transfer_filename,
)

OBJECTIVE = "minimize_train_rmse"
HARGREAVES_EXPONENT_DEFAULT = 0.5
HARGREAVES_EXPONENT_MIN = 0.05
HARGREAVES_EXPONENT_MAX = 1.5
HARGREAVES_EXPONENT_STEP = 1e-4
HARGREAVES_EXPONENT_RMSE_TOLERANCE = 1e-8
SIDE_BY_SIDE_METRICS = ("rmse", "mae", "mbe", "r", "r2", "willmott_d", "c", "classification")


@dataclass(frozen=True)
class CalibratableMethod:
    method: str
    original_column: str
    calibrated_column: str
    coefficient_name: str
    predictor: Callable[..., pd.Series]


@dataclass(frozen=True)
class CalibrationResult:
    coefficients: pd.DataFrame
    metrics: pd.DataFrame
    predictions: pd.DataFrame


def _hargreaves_samani(
    df: pd.DataFrame,
    coefficient: float,
    exponent: float = HARGREAVES_EXPONENT_DEFAULT,
) -> pd.Series:
    return pd.Series(
        eto_methods.hargreaves_samani(
            t_min_c=df["tmin_c"],
            t_max_c=df["tmax_c"],
            t_mean_c=df["tmed_c"],
            ra_mj_m2_day=df["ra_extraterrestre_mj_m2_d"],
            coefficient=coefficient,
            exponent=exponent,
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


def _default_temporal_split(df: pd.DataFrame, *, train_fraction: float = 0.7) -> tuple[str, str, str, str]:
    dates = pd.Series(pd.to_datetime(df["date"]).dropna().sort_values().unique())
    if len(dates) < 2:
        raise ValueError("Need at least two dates for separate train/test calibration")
    split_idx = max(1, int(np.floor(len(dates) * train_fraction)))
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
    *,
    train_fraction: float = 0.7,
) -> tuple[str, str, str, str]:
    if not any([train_start, train_end, test_start, test_end]):
        return _default_temporal_split(df, train_fraction=train_fraction)
    if not all([train_start, train_end, test_start, test_end]):
        raise ValueError("Provide all split dates: train-start, train-end, test-start, test-end")
    assert train_start is not None
    assert train_end is not None
    assert test_start is not None
    assert test_end is not None
    if pd.Timestamp(train_end) >= pd.Timestamp(test_start):
        raise ValueError("Training period must end before the test period starts")
    return train_start, train_end, test_start, test_end


def _apply_predictor(
    spec: CalibratableMethod,
    df: pd.DataFrame,
    coefficient: float,
    exponent: float | None,
) -> pd.Series:
    if spec.method == "hargreaves_samani":
        if exponent is None:
            raise ValueError("Hargreaves-Samani calibration requires an exponent")
        return spec.predictor(df, coefficient, exponent)
    return spec.predictor(df, coefficient)


def _exponent_grid() -> np.ndarray:
    step = HARGREAVES_EXPONENT_STEP
    start = int(round(HARGREAVES_EXPONENT_MIN / step))
    stop = int(round(HARGREAVES_EXPONENT_MAX / step))
    grid = np.arange(start, stop + 1, dtype=float) * step
    grid = np.unique(np.concatenate([grid, np.array([HARGREAVES_EXPONENT_DEFAULT])]))
    return grid[(grid >= HARGREAVES_EXPONENT_MIN) & (grid <= HARGREAVES_EXPONENT_MAX)]


def _select_exponent(exponents: np.ndarray, rmses: np.ndarray) -> float:
    finite = np.isfinite(rmses)
    if not finite.any():
        raise ValueError("No finite train observations available for calibration")
    best = float(np.min(rmses[finite]))
    close = finite & (rmses <= best + HARGREAVES_EXPONENT_RMSE_TOLERANCE)
    candidates = exponents[close]
    distances = np.abs(candidates - HARGREAVES_EXPONENT_DEFAULT)
    return float(candidates[int(np.argmin(distances))])


def _fit_hargreaves_exponent(df: pd.DataFrame, reference: pd.Series) -> float:
    """Profile the temperature-range exponent by training RMSE.

    For each candidate exponent the leading coefficient is the ordinary
    least-squares solution. Ties within a negligible RMSE tolerance keep the
    published exponent 0.5. The search bounds are numerical limits, not a
    regional estimate.
    """
    temp_range = np.maximum(
        df["tmax_c"].to_numpy(dtype=float) - df["tmin_c"].to_numpy(dtype=float),
        0.0,
    )
    ra_mm = np.asarray(
        mj_m2_day_to_mm_day(df["ra_extraterrestre_mj_m2_d"].to_numpy(dtype=float)),
        dtype=float,
    )
    scale = ra_mm * (df["tmed_c"].to_numpy(dtype=float) + 17.8)
    observed = reference.to_numpy(dtype=float)
    finite = np.isfinite(temp_range) & np.isfinite(scale) & np.isfinite(observed)
    if not finite.any():
        raise ValueError("No finite train observations available for calibration")
    temp_range = temp_range[finite]
    scale = scale[finite]
    observed = observed[finite]
    if not np.any((temp_range > 0.0) & (scale != 0.0)):
        raise ValueError("Cannot calibrate coefficient from a zero predictor")

    exponents = _exponent_grid()
    rmses = np.empty(len(exponents), dtype=float)
    positive = temp_range > 0.0
    log_range = np.zeros(temp_range.shape, dtype=float)
    log_range[positive] = np.log(temp_range[positive])
    chunk = 2000
    for start in range(0, len(exponents), chunk):
        batch = exponents[start : start + chunk]
        powered = np.exp(batch[:, None] * log_range[None, :])
        powered[:, ~positive] = 0.0
        predictor = powered * scale[None, :]
        xy = predictor @ observed
        xx = np.einsum("ij,ij->i", predictor, predictor)
        coefficient = np.divide(xy, xx, out=np.full(len(batch), np.nan), where=xx > 0.0)
        residual = observed[None, :] - coefficient[:, None] * predictor
        rmses[start : start + chunk] = np.sqrt(np.mean(residual * residual, axis=1))
    return _select_exponent(exponents, rmses)


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
    train_fraction: float = 0.7,
    fit_exponent: bool = False,
) -> CalibrationResult:
    if method not in CALIBRATABLE_METHODS:
        available = ", ".join(sorted(CALIBRATABLE_METHODS))
        raise ValueError(f"Unsupported calibration method '{method}'. Available: {available}")
    if fit_exponent and method != "hargreaves_samani":
        raise ValueError(
            "A free temperature-range exponent is available only for hargreaves_samani"
        )
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
        train_fraction=train_fraction,
    )
    train_mask = _date_mask(df, train_start, train_end)
    test_mask = _date_mask(df, test_start, test_end)
    if (train_mask & test_mask).any():
        raise ValueError("Training and test periods must not overlap")
    if not train_mask.any() or not test_mask.any():
        raise ValueError("Training and test periods must both contain observations")

    published_exponent = default_exponent(method)
    if method == "hargreaves_samani" and fit_exponent:
        exponent: float | None = _fit_hargreaves_exponent(
            df.loc[train_mask],
            df.loc[train_mask, reference_col],
        )
        exponent_status = "fitted"
    elif method == "hargreaves_samani":
        exponent = published_exponent
        exponent_status = "fixed"
    else:
        exponent = None
        exponent_status = "not_applicable"

    predictions = df.copy()
    predictions[spec.original_column] = _apply_predictor(
        spec,
        predictions,
        default_coefficient(method),
        published_exponent,
    )

    train_base = _apply_predictor(spec, predictions.loc[train_mask], 1.0, exponent)
    coefficient = _fit_scalar_coefficient(train_base, predictions.loc[train_mask, reference_col])
    predictions[spec.calibrated_column] = _apply_predictor(spec, predictions, coefficient, exponent)
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
                "exponent": exponent if exponent is not None else np.nan,
                "exponent_status": exponent_status,
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


def default_exponent(method: str) -> float | None:
    if method == "hargreaves_samani":
        return HARGREAVES_EXPONENT_DEFAULT
    if method in CALIBRATABLE_METHODS:
        return None
    raise ValueError(f"Unsupported calibration method '{method}'")


def _resolved_exponent(result: CalibrationResult, method: str) -> tuple[float | None, str]:
    row = result.coefficients.iloc[0]
    status = str(row["exponent_status"])
    if status == "not_applicable" or not np.isfinite(row["exponent"]):
        return default_exponent(method), status
    return float(row["exponent"]), status


def _side_by_side_metrics(scored: pd.DataFrame, spec: CalibratableMethod) -> dict[str, object]:
    by_method = scored.set_index("method")
    original = by_method.loc[spec.original_column]
    calibrated = by_method.loc[spec.calibrated_column]
    paired: dict[str, object] = {}
    for metric_name in SIDE_BY_SIDE_METRICS:
        paired[f"original_{metric_name}"] = original[metric_name]
        paired[f"calibrated_{metric_name}"] = calibrated[metric_name]
    return paired


def cross_site_transfer(
    frames: dict[str, pd.DataFrame],
    *,
    method: str,
    train_start: str | None = None,
    train_end: str | None = None,
    test_start: str | None = None,
    test_end: str | None = None,
    reference_col: str = REFERENCE_COLUMN,
    train_fraction: float = 0.7,
    fit_exponent: bool = False,
) -> pd.DataFrame:
    """Fit on one site's training window and score original and calibrated series at the others.

    Parameters come from the fit site's training period only. Both series are
    scored on every finite day at the score site. The original series keeps the
    published coefficient and, for Hargreaves-Samani, the published exponent.
    """
    if method not in CALIBRATABLE_METHODS:
        available = ", ".join(sorted(CALIBRATABLE_METHODS))
        raise ValueError(f"Unsupported calibration method '{method}'. Available: {available}")
    if len(frames) < 2:
        raise ValueError("Cross-site transfer requires at least two configured sites")

    spec = CALIBRATABLE_METHODS[method]
    rows: list[dict[str, object]] = []
    for fit_site, fit_frame in frames.items():
        fitted = calibrate_method(
            fit_frame,
            method=method,
            train_start=train_start,
            train_end=train_end,
            test_start=test_start,
            test_end=test_end,
            reference_col=reference_col,
            train_fraction=train_fraction,
            fit_exponent=fit_exponent,
        )
        coefficient = float(fitted.coefficients.loc[0, "coefficient"])
        exponent, exponent_status = _resolved_exponent(fitted, method)
        fit_row = fitted.coefficients.iloc[0]
        for score_site, score_frame in frames.items():
            if score_site == fit_site:
                continue
            predictions = score_frame.copy()
            predictions[spec.original_column] = _apply_predictor(
                spec,
                predictions,
                default_coefficient(method),
                default_exponent(method),
            )
            predictions[spec.calibrated_column] = _apply_predictor(
                spec,
                predictions,
                coefficient,
                exponent,
            )
            method_cols = [spec.original_column, spec.calibrated_column]
            _require_finite_metric_pairs(
                predictions,
                period="score",
                ref_col=reference_col,
                method_cols=method_cols,
            )
            ref = predictions[reference_col].to_numpy(dtype=float)
            paired = np.isfinite(ref)
            for column in method_cols:
                paired = paired & np.isfinite(predictions[column].to_numpy(dtype=float))
            scored = metrics.compute_metrics(
                predictions.loc[paired],
                reference_col,
                method_cols,
            )
            scored_dates = pd.to_datetime(predictions.loc[paired, "date"])
            rows.append(
                {
                    "fit_site": fit_site,
                    "score_site": score_site,
                    "method": f"{method}_calibrated",
                    "base_method": method,
                    "coefficient": coefficient,
                    "exponent": exponent if exponent is not None else np.nan,
                    "exponent_status": exponent_status,
                    "objective": OBJECTIVE,
                    "reference": reference_col,
                    "fit_train_start": fit_row["train_start"],
                    "fit_train_end": fit_row["train_end"],
                    "fit_test_start": fit_row["test_start"],
                    "fit_test_end": fit_row["test_end"],
                    "n_fit_train": int(fit_row["n_train"]),
                    "n_score": int(paired.sum()),
                    "score_start": str(scored_dates.min().date()),
                    "score_end": str(scored_dates.max().date()),
                    "score_days": "all_finite_days",
                    **_side_by_side_metrics(scored, spec),
                }
            )
    return pd.DataFrame(rows)


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


def write_transfer_table(
    table: pd.DataFrame,
    *,
    output_dir: Path,
    method: str,
) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / calibration_transfer_filename(method)
    table.to_csv(path, index=False)
    return path
