from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


@dataclass(frozen=True)
class CleaningAudit:
    interpolated_by_variable: dict[str, int]


def clean_daily_with_audit(df: pd.DataFrame) -> tuple[pd.DataFrame, CleaningAudit]:
    df = df.copy()

    if "date" in df.columns:
        df = df.sort_values("date")

    # Interpolate numeric columns
    numeric_cols = df.select_dtypes(include=["number"]).columns
    missing_before = df[numeric_cols].isna().sum()
    df[numeric_cols] = df[numeric_cols].interpolate(method="linear", limit_direction="both")
    missing_after = df[numeric_cols].isna().sum()
    interpolated = (missing_before - missing_after).clip(lower=0).astype(int)

    # Drop duplicated dates if any
    if "date" in df.columns:
        df = df.drop_duplicates(subset=["date"], keep="first")

    audit = CleaningAudit(
        interpolated_by_variable={
            column: int(count) for column, count in interpolated.items() if int(count) > 0
        }
    )
    return df, audit


def clean_daily(df: pd.DataFrame) -> pd.DataFrame:
    cleaned, _audit = clean_daily_with_audit(df)
    return cleaned
