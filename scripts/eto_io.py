"""Shared helpers for reading ET₀ series across pipeline stages."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from .config import METHODS, OUTPUTS_RESULTS
from .naming import cleaned_daily_filename, daily_eto_filename


def eto_input_path(
    site: str,
    *,
    cleaned_dir: Path,
    results_dir: Path | None = None,
) -> Path:
    """Return the preferred daily ET₀ CSV path for a site.

    Prefers ``outputs/results/{site}_daily_eto.csv`` when present, otherwise
    falls back to ``data/cleaned/{site}_daily.csv``.
    """
    resolved_results = results_dir if results_dir is not None else OUTPUTS_RESULTS
    computed_path = resolved_results / daily_eto_filename(site)
    if computed_path.exists():
        return computed_path
    return cleaned_dir / cleaned_daily_filename(site)


def read_eto_frame(
    site: str,
    *,
    cleaned_dir: Path,
    results_dir: Path | None = None,
    merge_cleaned_auxiliary: bool = False,
) -> pd.DataFrame:
    """Load the preferred daily ET₀ DataFrame for a site.

    When the computed daily file is used and ``merge_cleaned_auxiliary`` is true,
    non-ET₀ columns from the cleaned CSV (e.g. ``rain_mm``) are merged in by date.
    """
    resolved_results = results_dir if results_dir is not None else OUTPUTS_RESULTS
    computed_path = resolved_results / daily_eto_filename(site)
    cleaned_path = cleaned_dir / cleaned_daily_filename(site)

    if computed_path.exists():
        df = pd.read_csv(computed_path, parse_dates=["date"])
        if cleaned_path.exists():
            cleaned = pd.read_csv(cleaned_path, parse_dates=["date"])
            merge_cols: list[str] = []
            if merge_cleaned_auxiliary:
                merge_cols.extend(
                    column for column in cleaned.columns if column != "date" and column not in df.columns
                )
            for column in METHODS.precomputed_only_columns:
                if column in cleaned.columns and column not in df.columns and column not in merge_cols:
                    merge_cols.append(column)
            if merge_cols:
                df = df.merge(
                    cleaned[["date", *merge_cols]],
                    on="date",
                    how="left",
                    validate="one_to_one",
                )
        return df

    return pd.read_csv(cleaned_path, parse_dates=["date"])
