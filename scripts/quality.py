from __future__ import annotations

from pathlib import Path

import pandas as pd

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


def build_quality_report(
    site: str,
    raw_df: pd.DataFrame,
    cleaned_df: pd.DataFrame,
    year: int,
    interpolated_by_variable: dict[str, int] | None = None,
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
    present_dates = pd.DatetimeIndex(cleaned_dates.dropna().dt.normalize().unique())
    missing_dates = expected_dates.difference(present_dates)
    duplicate_dates = raw_dates[raw_dates.duplicated(keep=False)]

    variables = [
        column
        for column in raw_df.columns
        if column != "date" and (column in cleaned_df.columns or column in interpolated_by_variable)
    ]

    rows = []
    for variable in variables:
        rows.append(
            {
                "site": site,
                "variable": variable,
                "row_count": int(len(cleaned_df)),
                "expected_days": int(len(expected_dates)),
                "start_date": cleaned_dates.min().strftime("%Y-%m-%d")
                if cleaned_dates.notna().any()
                else "",
                "end_date": cleaned_dates.max().strftime("%Y-%m-%d")
                if cleaned_dates.notna().any()
                else "",
                "missing_dates": _format_dates(missing_dates),
                "duplicate_dates": _format_dates(duplicate_dates),
                "missing_values": int(raw_df[variable].isna().sum()),
                "interpolated_values": int(interpolated_by_variable.get(variable, 0)),
                "physical_limit_violations": _physical_limit_violations(raw_df[variable], variable),
            }
        )

    return pd.DataFrame(rows)


def write_quality_report(report: pd.DataFrame, output_dir: Path, site: str) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / f"{site}_data_quality.csv"
    report.to_csv(output_path, index=False)
    return output_path
