import numpy as np
import pandas as pd

from scripts.aggregate import monthly_sum, rolling_mean
from scripts.metrics import compute_metrics


def test_monthly_sum_groups_daily_values_by_calendar_month() -> None:
    df = pd.DataFrame(
        {
            "date": pd.to_datetime(["2024-01-01", "2024-01-31", "2024-02-01"]),
            "pm_fao56": [1.0, 2.0, 4.0],
            "hargreaves_samani": [0.5, 1.5, 3.0],
        }
    )

    result = monthly_sum(df, ["pm_fao56", "hargreaves_samani"])

    expected = pd.DataFrame(
        {
            "month": pd.to_datetime(["2024-01-01", "2024-02-01"]),
            "pm_fao56": [3.0, 4.0],
            "hargreaves_samani": [2.0, 3.0],
            "pm_fao56_valid_days": [2, 1],
            "pm_fao56_valid_fraction": [2 / 31, 1 / 29],
            "hargreaves_samani_valid_days": [2, 1],
            "hargreaves_samani_valid_fraction": [2 / 31, 1 / 29],
        }
    )
    pd.testing.assert_frame_equal(result, expected)


def test_monthly_sum_preserves_empty_months_and_reports_partial_coverage() -> None:
    df = pd.DataFrame(
        {
            "date": pd.to_datetime(["2024-01-01", "2024-01-02", "2024-02-01"]),
            "ref": [1.0, 2.0, np.nan],
            "method": [np.nan, np.nan, np.nan],
        }
    )

    monthly = monthly_sum(df, ["ref", "method"])

    assert monthly.loc[0, "method"] != monthly.loc[0, "method"]
    assert monthly.loc[0, "method_valid_days"] == 0
    assert monthly.loc[0, "method_valid_fraction"] == 0
    assert monthly.loc[1, "ref_valid_days"] == 0
    assert monthly.loc[1, "ref_valid_fraction"] == 0
    assert compute_metrics(monthly, "ref", ["method"])["rmse"].isna().all()


def test_rolling_mean_computes_seven_day_trailing_mean_after_sorting_dates() -> None:
    df = pd.DataFrame(
        {
            "date": pd.to_datetime(
                [
                    "2024-01-08",
                    "2024-01-01",
                    "2024-01-02",
                    "2024-01-03",
                    "2024-01-04",
                    "2024-01-05",
                    "2024-01-06",
                    "2024-01-07",
                ]
            ),
            "pm_fao56": [8.0, 1.0, 2.0, 3.0, 4.0, 5.0, 6.0, 7.0],
        }
    )

    result = rolling_mean(df, window=7)

    assert result["date"].tolist() == sorted(df["date"].tolist())
    assert result["pm_fao56"].tolist() == [1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0, 5.0]
