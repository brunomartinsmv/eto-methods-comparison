from __future__ import annotations

from pathlib import Path

import pandas as pd

from .config import DEFAULT_YEAR, METHOD_COLUMNS, WEATHER_COLUMNS


def _parse_date_series(series: pd.Series, year: int) -> pd.Series:
    # If numeric day-of-year
    numeric = pd.to_numeric(series, errors="coerce")
    if numeric.notna().any() and numeric.max() <= 366 and numeric.min() >= 1:
        return pd.to_datetime(f"{year}-01-01") + pd.to_timedelta(numeric - 1, unit="D")

    # Try datetime parsing
    parsed = pd.to_datetime(series, errors="coerce")
    if parsed.notna().sum() > len(series) * 0.5:
        return parsed

    # Fallback: treat as day-of-month (1-31) in sequential months
    numeric = numeric.fillna(1).astype(int)
    months = []
    current_month = 1
    prev_day = None
    for day in numeric:
        if prev_day is not None and day < prev_day:
            current_month += 1
            if current_month > 12:
                current_month = 12
        months.append(current_month)
        prev_day = day

    return pd.to_datetime({"year": year, "month": months, "day": numeric})


def read_evapo_sheet(path: Path, sheet: str, year: int = DEFAULT_YEAR) -> pd.DataFrame:
    df = pd.read_excel(path, sheet_name=sheet, skiprows=4)

    # Drop unnamed columns
    df = df.loc[:, [c for c in df.columns if not str(c).startswith("Unnamed")]]

    rename_map = {}
    rename_map.update(WEATHER_COLUMNS)
    rename_map.update(METHOD_COLUMNS)

    df = df.rename(columns=rename_map)

    if "date" in df.columns:
        df["date"] = _parse_date_series(df["date"], year)

    return df


def write_cleaned(df: pd.DataFrame, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(output_path, index=False)
