from __future__ import annotations

import warnings

import pandas as pd

from scripts.io import _parse_date_series, select_cleaned_columns


def test_parse_date_series_warns_on_day_of_month_fallback() -> None:
    series = pd.Series(["not-a-date", "still-not-a-date", "nope"])

    with warnings.catch_warnings(record=True) as caught:
        warnings.simplefilter("always")
        parsed = _parse_date_series(series, year=2024)

    assert len(parsed) == 3
    assert any("day-of-month heuristics" in str(item.message) for item in caught)


def test_select_cleaned_columns_drops_legacy_spreadsheet_fields() -> None:
    df = pd.DataFrame(
        {
            "date": pd.to_datetime(["2024-01-01"]),
            "tmed_c": [25.0],
            "et_penman_monteith": [4.0],
            "T_med": [25.0],
            "es": [2.0],
        }
    )

    result = select_cleaned_columns(df)

    assert list(result.columns) == ["date", "tmed_c", "et_penman_monteith"]
