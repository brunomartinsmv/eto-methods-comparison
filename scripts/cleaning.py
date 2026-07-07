from __future__ import annotations

from dataclasses import dataclass, field

import pandas as pd


@dataclass(frozen=True)
class CleaningAudit:
    interpolated_by_variable: dict[str, int]
    long_gaps_by_variable: dict[str, list[tuple[pd.Timestamp, pd.Timestamp, int]]] = field(default_factory=dict)


def _missing_runs(series: pd.Series) -> list[tuple[int, int]]:
    runs: list[tuple[int, int]] = []
    start: int | None = None
    for idx, value in enumerate(series):
        if pd.isna(value):
            if start is None:
                start = idx
        elif start is not None:
            runs.append((start, idx - start))
            start = None
    if start is not None:
        runs.append((start, len(series) - start))
    return runs


def clean_daily_with_audit(df: pd.DataFrame, *, max_gap: int | None = None) -> tuple[pd.DataFrame, CleaningAudit]:
    df = df.copy()

    if "date" in df.columns:
        df = df.sort_values("date")

    numeric_cols = df.select_dtypes(include=["number"]).columns
    original_numeric = df[numeric_cols].copy()
    missing_before = original_numeric.isna().sum()
    interpolate_kwargs: dict[str, object] = {"method": "linear", "limit_direction": "both"}
    if max_gap is not None:
        interpolate_kwargs["limit"] = max_gap
    df[numeric_cols] = original_numeric.interpolate(**interpolate_kwargs)
    missing_after = df[numeric_cols].isna().sum()
    interpolated = (missing_before - missing_after).clip(lower=0).astype(int)

    long_gaps: dict[str, list[tuple[pd.Timestamp, pd.Timestamp, int]]] = {}
    if max_gap is not None and "date" in df.columns:
        dates = pd.to_datetime(df["date"], errors="coerce")
        for column in numeric_cols:
            segments: list[tuple[pd.Timestamp, pd.Timestamp, int]] = []
            for start_idx, length in _missing_runs(original_numeric[column]):
                if length <= max_gap:
                    continue
                start_date = dates.iloc[start_idx]
                end_date = dates.iloc[min(start_idx + length - 1, len(dates) - 1)]
                if pd.isna(start_date) or pd.isna(end_date):
                    continue
                segments.append((pd.Timestamp(start_date), pd.Timestamp(end_date), length))
            if segments:
                long_gaps[column] = segments

    if "date" in df.columns:
        df = df.drop_duplicates(subset=["date"], keep="first")

    audit = CleaningAudit(
        interpolated_by_variable={
            column: int(count) for column, count in interpolated.items() if int(count) > 0
        },
        long_gaps_by_variable=long_gaps,
    )
    return df, audit


def clean_daily(df: pd.DataFrame, *, max_gap: int | None = None) -> pd.DataFrame:
    cleaned, _audit = clean_daily_with_audit(df, max_gap=max_gap)
    return cleaned
