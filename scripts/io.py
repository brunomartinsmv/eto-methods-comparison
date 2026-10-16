from __future__ import annotations

import re
import unicodedata
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


@dataclass(frozen=True)
class SiteTable:
    frame: pd.DataFrame
    station_status: str | None = None


_CANONICAL_WEATHER = (
    "tmed_c",
    "tmax_c",
    "tmin_c",
    "rh_mean_pct",
    "rh_max_pct",
    "rh_min_pct",
    "wind_mean_ms",
    "wind_max_ms",
    "rain_mm",
    "pressure_hpa",
    "rad_global_mj_m2_d",
    "rad_net_mj_m2_d",
)


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
    elif merged_format in {"generic", "csv"}:
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
    weather = [col for col in _CANONICAL_WEATHER if col in df.columns]
    listed = set(_CANONICAL_WEATHER)
    for column in WEATHER_COLUMNS.values():
        if column in df.columns and column != "date" and column not in listed and column not in weather:
            weather.append(column)
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


def _ascii_key(value: object) -> str:
    text = unicodedata.normalize("NFKD", str(value)).encode("ascii", "ignore").decode("ascii")
    text = re.sub(r"[^a-z0-9]+", " ", text.lower())
    return " ".join(text.split())


def _canonical_inmet_column(key: str) -> str | None:
    """Map one INMET automatic-station header onto a canonical weather name.

    Radiation columns are copied only when the sheet already has them. This
    function does not create a radiation series.
    """
    if not key or key.startswith("unnamed"):
        return None
    if key == "data medicao":
        return "date"
    if key.startswith("precipitacao"):
        return "rain_mm"
    if key.startswith("pressao atmosferica"):
        return "pressure_hpa"
    if key.startswith("temperatura maxima"):
        return "tmax_c"
    if key.startswith("temperatura media"):
        return "tmed_c"
    if key.startswith("temperatura minima"):
        return "tmin_c"
    if key.startswith("umidade relativa"):
        if "minima" in key:
            return "rh_min_pct"
        if "maxima" in key:
            return "rh_max_pct"
        if "media" in key:
            return "rh_mean_pct"
        return None
    if key.startswith("vento"):
        if "media" in key:
            return "wind_mean_ms"
        if "max" in key or "rajada" in key:
            return "wind_max_ms"
        return None
    if "radiacao" in key or key.startswith("rad "):
        if "liq" in key:
            return "rad_net_mj_m2_d"
        if "extrater" in key or key in {"q 0", "q0"}:
            return "ra_extraterrestre_mj_m2_d"
        return "rad_global_mj_m2_d"
    return None


def _inmet_metadata_value(raw_value: str) -> str:
    return " ".join(raw_value.strip().split())


def read_inmet_limited_table(path: Path, sheet: str) -> SiteTable:
    """Read an INMET automatic-station sheet as a limited weather table.

    The sheet header block carries station metadata, including ``Situacao``.
    Daily columns are renamed when they match temperature, humidity, wind,
    pressure, or rain. Missing radiation stays missing.
    """
    raw = pd.read_excel(path, sheet_name=sheet, header=None)
    header_idx: int | None = None
    metadata: dict[str, str] = {}
    for idx in range(len(raw)):
        row = raw.iloc[idx]
        keys = ["" if pd.isna(cell) else _ascii_key(cell) for cell in row.tolist()]
        if "data medicao" in keys:
            header_idx = idx
            break
        first = row.iloc[0]
        if pd.isna(first):
            continue
        text = str(first).strip()
        if ":" not in text:
            continue
        key, raw_value = text.split(":", 1)
        metadata[_ascii_key(key)] = _inmet_metadata_value(raw_value)

    if header_idx is None:
        raise ValueError(f"INMET limited reader did not find a 'Data Medicao' header in sheet {sheet}")

    header_keys = [
        "" if pd.isna(cell) else _ascii_key(cell) for cell in raw.iloc[header_idx].tolist()
    ]
    canonical = [_canonical_inmet_column(key) for key in header_keys]
    renamed = [name for name in canonical if name]
    duplicates = {name for name in renamed if renamed.count(name) > 1}
    if duplicates:
        raise ValueError(
            f"INMET limited reader found duplicate columns in sheet {sheet}: {', '.join(sorted(duplicates))}"
        )

    body = raw.iloc[header_idx + 1 :].copy()
    body.columns = [name if name else f"__drop_{pos}" for pos, name in enumerate(canonical)]
    keep = [column for column in body.columns if not str(column).startswith("__drop_")]
    body = body.loc[:, keep].dropna(how="all")
    if "date" not in body.columns:
        raise ValueError(f"INMET limited reader did not map a date column in sheet {sheet}")

    status = metadata.get("situacao") or None
    return SiteTable(frame=body.reset_index(drop=True), station_status=status)


def _resolve_reader_path(path_value: str | None, default_input: Path) -> Path:
    if not path_value:
        return default_input
    path = Path(path_value)
    if not path.is_absolute():
        path = BASE_DIR / path
    return path


def read_site_table(
    default_input: Path,
    site_meta: dict,
    *,
    year: int = DEFAULT_YEAR,
) -> SiteTable:
    reader = resolve_reader_config(site_meta, default_input)
    station_status: str | None = None
    if reader.format == "csv":
        path = _resolve_reader_path(reader.path, default_input)
        if path.suffix.lower() != ".csv":
            raise ValueError(
                "CSV reader expects a .csv weather file. "
                "Keep Evapo.xlsx on reader.format evapo_legacy."
            )
        if not path.exists():
            shown = reader.path or str(default_input)
            raise FileNotFoundError(f"Configured data path not found: {shown}")
        df = read_generic_table(path, skiprows=reader.skiprows, column_map=reader.column_map)
    elif reader.format == "generic":
        if not reader.path:
            raise ValueError("Generic reader requires reader.path in site configuration")
        path = _resolve_reader_path(reader.path, default_input)
        if not path.exists():
            raise FileNotFoundError(f"Configured data path not found: {reader.path}")
        df = read_generic_table(path, skiprows=reader.skiprows, column_map=reader.column_map)
    elif reader.format == "inmet_limited":
        sheet = reader.sheet or site_meta.get("sheet")
        if not sheet:
            raise ValueError("INMET limited reader requires 'sheet' or reader.sheet")
        path = _resolve_reader_path(reader.path, default_input)
        table = read_inmet_limited_table(path, sheet)
        df = table.frame
        station_status = table.station_status
    else:
        sheet = reader.sheet or site_meta.get("sheet")
        if not sheet:
            raise ValueError("Site configuration must define 'sheet' or reader.sheet")
        path = _resolve_reader_path(reader.path, default_input)
        if path.suffix.lower() == ".csv":
            raise ValueError(
                "A .csv weather file needs reader.format: csv. "
                "evapo_legacy reads the Evapo.xlsx workbook."
            )
        df = pd.read_excel(path, sheet_name=sheet, skiprows=reader.skiprows)
        df = df.loc[:, [c for c in df.columns if not str(c).startswith("Unnamed")]]
        df = _apply_column_map(df, reader.column_map)

    if "date" not in df.columns:
        raise ValueError("Input data must contain a date column after column mapping")
    df = df.copy()
    df["date"] = _parse_date_series(df["date"], year)
    return SiteTable(frame=df, station_status=station_status)


def read_site_data(
    default_input: Path,
    site_meta: dict,
    *,
    year: int = DEFAULT_YEAR,
) -> pd.DataFrame:
    return read_site_table(default_input, site_meta, year=year).frame


def write_cleaned(df: pd.DataFrame, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    select_cleaned_columns(df).to_csv(output_path, index=False)
