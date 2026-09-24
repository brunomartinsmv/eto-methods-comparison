from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from .config import METHODS

METHOD_COLUMNS = set(METHODS.columns.values())

PHYSICAL_LIMITS: dict[str, tuple[float | None, float | None]] = {
    "tmed_c": (-50.0, 60.0),
    "tmax_c": (-50.0, 60.0),
    "tmin_c": (-50.0, 60.0),
    "rh_mean_pct": (0.0, 100.0),
    "rh_max_pct": (0.0, 100.0),
    "rh_min_pct": (0.0, 100.0),
    "wind_mean_ms": (0.0, 75.0),
    "wind_max_ms": (0.0, 100.0),
    "rain_mm": (0.0, None),
    "rad_global_mj_m2_d": (0.0, 50.0),
    "rad_net_mj_m2_d": (-10.0, 40.0),
    "ra_extraterrestre_mj_m2_d": (0.0, 50.0),
    "et_thornthwaite": (0.0, 30.0),
    "et_thornthwaite_camargo": (0.0, 30.0),
    "et_camargo": (0.0, 30.0),
    "et_hargreaves_samani": (0.0, 30.0),
    "et_hargreaves_samani_corr": (0.0, 30.0),
    "et_priestley_taylor": (0.0, 30.0),
    "et_penman_monteith": (0.0, 30.0),
    "et_garcia_lopez": (0.0, 30.0),
}
PHYSICAL_LIMITS.update({column: (0.0, 30.0) for column in METHOD_COLUMNS})


def _format_dates(dates: pd.Series | pd.DatetimeIndex) -> str:
    values = pd.to_datetime(dates).dropna().sort_values().unique()
    return ";".join(pd.Timestamp(value).strftime("%Y-%m-%d") for value in values)


def _physical_limit_violations(series: pd.Series, variable: str) -> int:
    bounds = PHYSICAL_LIMITS.get(variable)
    if bounds is None:
        return 0

    lower, upper = bounds
    numeric = pd.to_numeric(series, errors="coerce")
    mask = pd.Series(False, index=numeric.index)
    if lower is not None:
        mask = mask | (numeric < lower)
    if upper is not None:
        mask = mask | (numeric > upper)
    return int(mask.sum())


def _quality_row(
    *,
    site: str,
    stage: str,
    variable: str,
    values: pd.Series | None,
    dates: pd.Series,
    expected_dates: pd.DatetimeIndex,
    row_count: int,
    interpolated_values: int = 0,
    status: str = "available",
) -> dict[str, object]:
    parsed_dates = pd.to_datetime(dates, errors="coerce")
    normalized_dates = parsed_dates.dt.normalize()
    in_expected_range = normalized_dates.isin(expected_dates)
    present_dates = pd.DatetimeIndex(normalized_dates.loc[in_expected_range].dropna().unique())
    finite_days = 0
    finite_values = 0
    non_finite_values: int | None = None
    missing_values: int | None = None
    physical_violations = 0

    if values is not None:
        numeric = pd.to_numeric(values, errors="coerce")
        finite = pd.Series(
            np.isfinite(numeric.to_numpy(dtype=float, na_value=np.nan)), index=numeric.index
        )
        finite_values = int(finite.sum())
        non_finite_values = int((~finite).sum())
        missing_values = int(values.isna().sum())
        valid_dates = normalized_dates.loc[finite.to_numpy() & in_expected_range].dropna().unique()
        finite_days = len(valid_dates)
        physical_violations = _physical_limit_violations(values, variable)

    expected_days = len(expected_dates)
    valid_fraction = finite_days / expected_days if expected_days else float("nan")
    return {
        "site": site,
        "stage": stage,
        "variable": variable,
        "status": status,
        "source_present": values is not None,
        "row_count": row_count,
        "expected_days": expected_days,
        "valid_days": finite_days,
        "valid_fraction": valid_fraction,
        "finite_values": finite_values,
        "non_finite_values": non_finite_values,
        "start_date": normalized_dates.loc[in_expected_range].min().strftime("%Y-%m-%d") if in_expected_range.any() else "",
        "end_date": normalized_dates.loc[in_expected_range].max().strftime("%Y-%m-%d") if in_expected_range.any() else "",
        "missing_dates": _format_dates(expected_dates.difference(present_dates)),
        "duplicate_dates": _format_dates(parsed_dates.loc[in_expected_range & parsed_dates.duplicated(keep=False)]),
        "missing_values": missing_values,
        "interpolated_values": interpolated_values,
        "physical_limit_violations": physical_violations,
    }


def build_quality_report(
    site: str,
    raw_df: pd.DataFrame,
    cleaned_df: pd.DataFrame,
    year: int,
    interpolated_by_variable: dict[str, int] | None = None,
    calculated_df: pd.DataFrame | None = None,
) -> pd.DataFrame:
    interpolated_by_variable = interpolated_by_variable or {}

    if "date" not in raw_df.columns or "date" not in cleaned_df.columns:
        raise ValueError("Quality report requires a 'date' column in raw and cleaned data")

    raw_dates = pd.to_datetime(raw_df["date"], errors="coerce")
    cleaned_dates = pd.to_datetime(cleaned_df["date"], errors="coerce")
    if cleaned_dates.notna().any():
        expected_start = cleaned_dates.min().normalize()
        expected_end = cleaned_dates.max().normalize()
    else:
        expected_start = pd.Timestamp(f"{year}-01-01")
        expected_end = pd.Timestamp(f"{year}-12-31")
    expected_dates = pd.date_range(expected_start, expected_end, freq="D")
    variables = [
        column
        for column in raw_df.columns
        if column != "date" and (column in cleaned_df.columns or column in interpolated_by_variable)
    ]

    rows: list[dict[str, object]] = []
    for variable in variables:
        stage = "precomputed_et0" if variable in METHOD_COLUMNS else "input"
        rows.append(
            _quality_row(
                site=site,
                stage=stage,
                variable=variable,
                values=raw_df[variable],
                dates=raw_dates,
                expected_dates=expected_dates,
                row_count=len(cleaned_df),
                interpolated_values=int(interpolated_by_variable.get(variable, 0)),
            )
        )

    for variable in sorted(METHOD_COLUMNS):
        source_present = calculated_df is not None and variable in calculated_df.columns
        if calculated_df is None:
            status = "not_run"
            calculated_dates = pd.Series(dtype="datetime64[ns]")
            values = None
            row_count = 0
        else:
            calculated_dates = pd.to_datetime(calculated_df["date"], errors="coerce")
            values = calculated_df[variable] if source_present else None
            status = "available" if source_present else "not_available"
            row_count = len(calculated_df)
        rows.append(
            _quality_row(
                site=site,
                stage="computed_et0",
                variable=variable,
                values=values,
                dates=calculated_dates,
                expected_dates=expected_dates,
                row_count=row_count,
                status=status,
            )
        )

    return pd.DataFrame(rows)


def write_quality_report(report: pd.DataFrame, output_dir: Path, site: str) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"{site}_data_quality.csv"
    report.to_csv(output_path, index=False)
    return output_path
