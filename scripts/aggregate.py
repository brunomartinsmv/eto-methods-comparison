from __future__ import annotations

import numpy as np
import pandas as pd


def add_month(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    if "date" in df.columns:
        df["month"] = df["date"].dt.to_period("M").dt.to_timestamp()
    return df


def rolling_mean(df: pd.DataFrame, window: int = 7) -> pd.DataFrame:
    df = df.copy()
    if "date" in df.columns:
        df = df.sort_values("date")
    numeric_cols = df.select_dtypes(include=["number"]).columns
    df[numeric_cols] = df[numeric_cols].rolling(window=window, min_periods=1).mean()
    return df


def monthly_sum(df: pd.DataFrame, value_cols: list[str]) -> pd.DataFrame:
    df = add_month(df)
    if "month" not in df.columns:
        raise ValueError("No 'month' column available for aggregation")

    labels = df["month"]
    if isinstance(labels.dtype, pd.PeriodDtype):
        months = labels.dt.to_timestamp()
    elif pd.api.types.is_integer_dtype(labels):
        months = pd.to_datetime(labels.astype("string"), format="%Y%m", errors="coerce")
    else:
        months = pd.to_datetime(labels, errors="coerce")
    if months.isna().any():
        raise ValueError("'month' values must be date-like or YYYYMM integers")
    months = months.dt.to_period("M").dt.to_timestamp()

    values = df[value_cols].apply(pd.to_numeric, errors="coerce")
    values = values.where(np.isfinite(values))
    grouped = values.groupby(months)
    monthly = grouped.sum(min_count=1)
    valid_days = grouped.count()
    expected_months = pd.date_range(monthly.index.min(), monthly.index.max(), freq="MS")
    monthly = monthly.reindex(expected_months)
    valid_days = valid_days.reindex(expected_months, fill_value=0)
    monthly.index.name = "month"
    valid_days.index.name = "month"
    days_in_month = monthly.index.days_in_month

    for column in value_cols:
        monthly[f"{column}_valid_days"] = valid_days[column]
        monthly[f"{column}_valid_fraction"] = valid_days[column] / days_in_month

    return monthly.reset_index()
