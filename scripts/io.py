from __future__ import annotations

import warnings
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from .config import (
    BASE_DIR,
    DEFAULT_YEAR,
    LEGACY_METHOD_COLUMN_ALIASES,
    METHOD_COLUMNS,
    WEATHER_COLUMNS,
    load_sites_defaults,
)


@dataclass(frozen=True)
class ReaderConfig:
    format: str = "evapo_legacy"
    path: str | None = None
    sheet: str | None = None
    skiprows: int = 4
    column_map: dict[str, str] | None = None


def resolve_reader_config(site_meta: dict, default_input: Path) -> ReaderConfig:
    defaults = load_sites_defaults()
    default_reader = defaults.reader if isinstance(defaults.reader, dict) else {}
    reader = site_meta.get("reader")
    if not isinstance(reader, dict):
        reader = {}
    merged_reader = {**default_reader, **reader}

    column_map = merged_reader.get("column_map")
    default_format = str(default_reader.get("format", "evapo_legacy"))
    merged_format = str(merged_reader.get("format", default_format))
    if "skiprows" in reader:
        skiprows = int(reader["skiprows"])
    elif merged_format == "generic":
        skiprows = 0
    else:
        skiprows = int(merged_reader.get("skiprows", int(default_reader.get("skiprows", 4))))

    return ReaderConfig(
        format=merged_format,
        path=merged_reader.get("path"),
        sheet=merged_reader.get("sheet", site_meta.get("sheet")),
        skiprows=skiprows,
        column_map={str(k): str(v) for k, v in column_map.items()} if isinstance(column_map, dict) else None,
    )


def _parse_date_series(series: pd.Series, year: int) -> pd.Series:
    numeric = pd.to_numeric(series, errors="coerce")
    if numeric.notna().any() and numeric.max() <= 366 and numeric.min() >= 1:
        return pd.to_datetime(f"{year}-01-01") + pd.to_timedelta(numeric - 1, unit="D")

    parsed = pd.to_datetime(series, errors="coerce")
    if parsed.notna().sum() > len(series) * 0.5:
        return parsed

    warnings.warn(
        "Date parsing fell back to day-of-month heuristics with implicit month rollover; "
        "verify parsed dates against the source spreadsheet.",
        UserWarning,
        stacklevel=3,
    )
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


def _apply_column_map(df: pd.DataFrame, column_map: dict[str, str] | None) -> pd.DataFrame:
    rename_map: dict[str, str] = {}
    rename_map.update(WEATHER_COLUMNS)
    rename_map.update(LEGACY_METHOD_COLUMN_ALIASES)
    rename_map.update(METHOD_COLUMNS)
    if column_map:
        rename_map.update(column_map)
    return df.rename(columns=rename_map)


def canonical_cleaned_columns(df: pd.DataFrame) -> list[str]:
    """Return column order for cleaned daily CSV output."""
    weather = [col for col in WEATHER_COLUMNS.values() if col in df.columns and col != "date"]
    derived = [col for col in ("ra_extraterrestre_mj_m2_d",) if col in df.columns]
    methods = sorted(col for col in METHOD_COLUMNS.values() if col in df.columns)
    ordered = ["date"] if "date" in df.columns else []
    for group in (weather, derived, methods):
        for column in group:
            if column not in ordered:
                ordered.append(column)
    return ordered


def select_cleaned_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Keep canonical weather, derived, and ET0 columns; drop legacy spreadsheet extras."""
    columns = canonical_cleaned_columns(df)
    if not columns:
        return df
    return df.loc[:, columns]


def read_evapo_sheet(
    path: Path,
    sheet: str,
    year: int = DEFAULT_YEAR,
    *,
    skiprows: int | None = None,
) -> pd.DataFrame:
    if skiprows is None:
        skiprows = int(load_sites_defaults().reader.get("skiprows", 4))
    df = pd.read_excel(path, sheet_name=sheet, skiprows=skiprows)
    df = df.loc[:, [c for c in df.columns if not str(c).startswith("Unnamed")]]
    df = _apply_column_map(df, None)
    if "date" in df.columns:
        df["date"] = _parse_date_series(df["date"], year)
    return df


def read_generic_table(path: Path, *, skiprows: int = 0, column_map: dict[str, str] | None = None) -> pd.DataFrame:
    if path.suffix.lower() in {".xlsx", ".xls"}:
        df = pd.read_excel(path, skiprows=skiprows)
    else:
        df = pd.read_csv(path, skiprows=skiprows)
    df = df.loc[:, [c for c in df.columns if not str(c).startswith("Unnamed")]]
    return _apply_column_map(df, column_map)


def read_site_data(
    default_input: Path,
    site_meta: dict,
    *,
    year: int = DEFAULT_YEAR,
) -> pd.DataFrame:
    reader = resolve_reader_config(site_meta, default_input)
    if reader.format == "generic":
        if not reader.path:
            raise ValueError("Generic reader requires reader.path in site configuration")
        path = Path(reader.path)
        if not path.is_absolute():
            path = BASE_DIR / path
        if not path.exists():
            raise FileNotFoundError(f"Configured data path not found: {reader.path}")
        df = read_generic_table(path, skiprows=reader.skiprows, column_map=reader.column_map)
    else:
        sheet = reader.sheet or site_meta.get("sheet")
        if not sheet:
            raise ValueError("Site configuration must define 'sheet' or reader.sheet")
        path = Path(reader.path) if reader.path else default_input
        df = pd.read_excel(path, sheet_name=sheet, skiprows=reader.skiprows)
        df = df.loc[:, [c for c in df.columns if not str(c).startswith("Unnamed")]]
        df = _apply_column_map(df, reader.column_map)

    if "date" not in df.columns:
        raise ValueError("Input data must contain a date column after column mapping")
    df["date"] = _parse_date_series(df["date"], year)
    return df


def write_cleaned(df: pd.DataFrame, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    select_cleaned_columns(df).to_csv(output_path, index=False)
