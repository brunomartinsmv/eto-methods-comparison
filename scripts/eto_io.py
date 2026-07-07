"""Shared helpers for reading ET₀ series across pipeline stages."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

from .config import OUTPUTS_RESULTS
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
) -> pd.DataFrame:
    """Load the preferred daily ET₀ DataFrame for a site."""
    return pd.read_csv(
        eto_input_path(site, cleaned_dir=cleaned_dir, results_dir=results_dir),
        parse_dates=["date"],
    )
