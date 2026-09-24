import argparse
from pathlib import Path

import pandas as pd

from scripts import cli
from scripts.cleaning import clean_daily_with_audit
from scripts.config import METHODS
from scripts.quality import PHYSICAL_LIMITS, build_quality_report, write_quality_report


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
    input_report = report[report["stage"] == "input"].set_index("variable")
    assert set(input_report["row_count"]) == {3}
    assert set(input_report["expected_days"]) == {4}
    assert set(input_report["start_date"]) == {"2024-01-01"}
    assert set(input_report["end_date"]) == {"2024-01-04"}
    assert set(input_report["missing_dates"]) == {"2024-01-03"}
    assert set(input_report["duplicate_dates"]) == {"2024-01-02"}

    assert input_report.loc["tmax_c", "missing_values"] == 1
    assert input_report.loc["tmax_c", "interpolated_values"] == 1
    assert input_report.loc["tmax_c", "physical_limit_violations"] == 1
    assert input_report.loc["rh_mean_pct", "physical_limit_violations"] == 1
    assert input_report.loc["tmax_c", "valid_days"] == 3
    assert input_report.loc["tmax_c", "valid_fraction"] == 0.75


def test_quality_report_audits_precomputed_and_calculated_methods() -> None:
    assert set(METHODS.columns.values()) <= PHYSICAL_LIMITS.keys()
    raw = pd.DataFrame(
        {
            "date": pd.date_range("2024-01-01", periods=3),
            "tmed_c": [20.0, 21.0, 22.0],
            "et_thornthwaite": [1.0, float("inf"), None],
        }
    )
    cleaned = raw[["date", "tmed_c", "et_thornthwaite"]]
    calculated = pd.DataFrame(
        {
            "date": pd.to_datetime(["2024-01-01", "2024-01-03"]),
            "et_penman_monteith": [2.0, None],
        }
    )

    report = build_quality_report(
        site="manaus",
        raw_df=raw,
        cleaned_df=cleaned,
        year=2024,
        calculated_df=calculated,
    )

    precomputed = report[
        (report["stage"] == "precomputed_et0") & (report["variable"] == "et_thornthwaite")
    ].iloc[0]
    assert precomputed["finite_values"] == 1
    assert precomputed["non_finite_values"] == 2
    assert precomputed["physical_limit_violations"] == 1
    assert precomputed["valid_fraction"] == 1 / 3

    calculated_method = report[
        (report["stage"] == "computed_et0")
        & (report["variable"] == "et_penman_monteith")
    ].iloc[0]
    assert calculated_method["status"] == "available"
    assert calculated_method["valid_days"] == 1
    assert calculated_method["valid_fraction"] == 1 / 3

    skipped_method = report[
        (report["stage"] == "computed_et0") & (report["variable"] == "et_mccloud")
    ].iloc[0]
    assert skipped_method["status"] == "not_available"
    assert skipped_method["valid_fraction"] == 0


def test_calculated_coverage_ignores_dates_outside_cleaned_calendar() -> None:
    raw = pd.DataFrame({"date": pd.to_datetime(["2024-01-01", "2024-01-02"]), "tmed_c": [20, 21]})
    calculated = pd.DataFrame(
        {
            "date": pd.to_datetime(["2024-01-01", "2024-01-02", "2024-01-03", "2024-01-03"]),
            "et_penman_monteith": [2.0, 2.5, 9.0, 10.0],
        }
    )

    report = build_quality_report(
        site="manaus", raw_df=raw, cleaned_df=raw, year=2024, calculated_df=calculated
    )
    row = report.loc[
        (report["stage"] == "computed_et0")
        & (report["variable"] == "et_penman_monteith")
    ].iloc[0]

    assert row["expected_days"] == 2
    assert row["valid_days"] == 2
    assert row["valid_fraction"] == 1
    assert row["start_date"] == "2024-01-01"
    assert row["end_date"] == "2024-01-02"
    assert row["missing_dates"] == ""
    assert row["duplicate_dates"] == ""


def test_validate_data_reads_computed_results_and_marks_source_stages(
    tmp_path: Path, monkeypatch
) -> None:
    results_dir = tmp_path / "results"
    results_dir.mkdir()
    pd.DataFrame(
        {
            "date": pd.date_range("2024-01-01", periods=2),
            "et_penman_monteith": [2.0, 2.5],
        }
    ).to_csv(results_dir / "manaus_daily_eto.csv", index=False)
    raw = pd.DataFrame(
        {
            "date": pd.date_range("2024-01-01", periods=2),
            "tmed_c": [20.0, 21.0],
            "et_thornthwaite": [1.0, 1.5],
        }
    )
    monkeypatch.setattr(cli, "OUTPUTS_RESULTS", results_dir)
    monkeypatch.setattr(cli, "_selected_sites", lambda _: {"manaus": {}})
    monkeypatch.setattr(cli.io, "read_site_data", lambda *args, **kwargs: raw)

    cli.cmd_validate_data(
        argparse.Namespace(
            input="unused.xlsx",
            output=str(tmp_path / "reports"),
            year=2024,
            site="manaus",
            all_sites=False,
            use_calculated_results=True,
        )
    )

    report = pd.read_csv(tmp_path / "reports" / "manaus_data_quality.csv")
    assert {"input", "precomputed_et0", "computed_et0"} <= set(report["stage"])
    assert report.loc[
        (report["stage"] == "computed_et0")
        & (report["variable"] == "et_penman_monteith"),
        "valid_fraction",
    ].iloc[0] == 1


def test_validate_data_does_not_mix_custom_input_with_default_calculated_results(
    tmp_path: Path, monkeypatch
) -> None:
    results_dir = tmp_path / "results"
    results_dir.mkdir()
    pd.DataFrame(
        {"date": pd.date_range("2024-01-01", periods=1), "et_penman_monteith": [2.0]}
    ).to_csv(results_dir / "manaus_daily_eto.csv", index=False)
    raw = pd.DataFrame({"date": pd.date_range("2024-01-01", periods=1), "tmed_c": [20.0]})
    monkeypatch.setattr(cli, "OUTPUTS_RESULTS", results_dir)
    monkeypatch.setattr(cli, "_selected_sites", lambda _: {"manaus": {}})
    monkeypatch.setattr(cli.io, "read_site_data", lambda *args, **kwargs: raw)

    cli.cmd_validate_data(
        argparse.Namespace(
            input="custom.xlsx",
            output=str(tmp_path / "reports"),
            year=2024,
            site="manaus",
            all_sites=False,
        )
    )

    report = pd.read_csv(tmp_path / "reports" / "manaus_data_quality.csv")
    reference = report.loc[
        (report["stage"] == "computed_et0")
        & (report["variable"] == "et_penman_monteith")
    ].iloc[0]
    assert reference["status"] == "not_run"


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
