from pathlib import Path

import pandas as pd

from scripts.cleaning import clean_daily_with_audit
from scripts.quality import build_quality_report, write_quality_report


def test_clean_daily_with_audit_counts_interpolated_numeric_values() -> None:
    df = pd.DataFrame(
        {
            "date": pd.to_datetime(["2024-01-01", "2024-01-02", "2024-01-03"]),
            "tmax_c": [30.0, None, 34.0],
            "rain_mm": [0.0, None, None],
            "station": ["a", "b", "c"],
        }
    )

    cleaned, audit = clean_daily_with_audit(df)

    assert cleaned["tmax_c"].tolist() == [30.0, 32.0, 34.0]
    assert cleaned["rain_mm"].tolist() == [0.0, 0.0, 0.0]
    assert audit.interpolated_by_variable == {"tmax_c": 1, "rain_mm": 2}


def test_build_quality_report_records_dates_missing_values_interpolation_and_limits() -> None:
    raw = pd.DataFrame(
        {
            "date": pd.to_datetime(
                ["2024-01-01", "2024-01-02", "2024-01-02", "2024-01-04"]
            ),
            "tmax_c": [30.0, None, 32.0, 80.0],
            "rh_mean_pct": [50.0, 101.0, 60.0, 55.0],
        }
    )
    cleaned = pd.DataFrame(
        {
            "date": pd.to_datetime(["2024-01-01", "2024-01-02", "2024-01-04"]),
            "tmax_c": [30.0, 31.0, 80.0],
            "rh_mean_pct": [50.0, 101.0, 55.0],
        }
    )

    report = build_quality_report(
        site="manaus",
        raw_df=raw,
        cleaned_df=cleaned,
        year=2024,
        interpolated_by_variable={"tmax_c": 1},
    )

    assert set(report["site"]) == {"manaus"}
    assert set(report["row_count"]) == {3}
    assert set(report["expected_days"]) == {4}
    assert set(report["start_date"]) == {"2024-01-01"}
    assert set(report["end_date"]) == {"2024-01-04"}
    assert set(report["missing_dates"]) == {"2024-01-03"}
    assert set(report["duplicate_dates"]) == {"2024-01-02"}

    by_variable = report.set_index("variable")
    assert by_variable.loc["tmax_c", "missing_values"] == 1
    assert by_variable.loc["tmax_c", "interpolated_values"] == 1
    assert by_variable.loc["tmax_c", "physical_limit_violations"] == 1
    assert by_variable.loc["rh_mean_pct", "physical_limit_violations"] == 1


def test_write_quality_report_creates_csv(tmp_path: Path) -> None:
    report = pd.DataFrame(
        {
            "site": ["manaus"],
            "variable": ["tmax_c"],
            "row_count": [1],
        }
    )

    output = write_quality_report(report, tmp_path, "manaus")

    assert output == tmp_path / "manaus_data_quality.csv"
    assert output.read_text().splitlines() == ["site,variable,row_count", "manaus,tmax_c,1"]
