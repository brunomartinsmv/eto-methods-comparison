import argparse

import pandas as pd

from scripts.cli import build_parser, cmd_aggregate
from scripts.config import DEFAULT_YEAR


def test_all_command_keeps_2024_default_year_and_default_input() -> None:
    args = build_parser().parse_args(["all"])

    assert args.year == DEFAULT_YEAR
    assert args.input.endswith("data/raw/Evapo.xlsx")
    assert args.output.endswith("data/cleaned")
    assert args.site is None
    assert args.all_sites is True


def test_all_command_accepts_single_site_selection() -> None:
    args = build_parser().parse_args(["all", "--site", "manaus"])

    assert args.site == "manaus"
    assert args.all_sites is False


def test_validate_data_command_defaults_to_raw_input_and_reports_output() -> None:
    args = build_parser().parse_args(["validate-data"])

    assert args.year == DEFAULT_YEAR
    assert args.input.endswith("data/raw/Evapo.xlsx")
    assert args.output.endswith("outputs/reports")


def test_scientific_cli_commands_are_available() -> None:
    parser = build_parser()

    analyze = parser.parse_args(["analyze-uncertainty"])
    analyze_with_year = parser.parse_args(["analyze-uncertainty", "--year", "2024"])
    assert analyze.input.endswith("data/cleaned")
    assert analyze.tables_output.endswith("outputs/tables")
    assert analyze.reports_output.endswith("outputs/reports")
    assert analyze.figures_output.endswith("outputs/figures")
    assert analyze_with_year.year == 2024

    summarize = parser.parse_args(["summarize"])
    assert summarize.input.endswith("outputs/tables")
    assert summarize.output.endswith("outputs/reports")

    reproduce = parser.parse_args(["reproduce-paper"])
    assert reproduce.year == DEFAULT_YEAR
    assert reproduce.all_sites is True

    supplement = parser.parse_args(["export-supplement"])
    assert supplement.output.endswith("outputs/supplement")


def test_aggregate_command_writes_standardized_result_filenames(tmp_path) -> None:
    input_dir = tmp_path / "cleaned"
    output_dir = tmp_path / "results"
    input_dir.mkdir()

    pd.DataFrame(
        {
            "date": ["2024-01-01", "2024-01-02"],
            "et_penman_monteith": [1.0, 2.0],
            "et_priestley_taylor": [1.1, 2.1],
        }
    ).to_csv(input_dir / "manaus_daily.csv", index=False)

    args = argparse.Namespace(input=str(input_dir), output=str(output_dir), site="manaus", all_sites=False)
    cmd_aggregate(args)

    assert (output_dir / "manaus_rolling_7d.csv").exists()
    assert (output_dir / "manaus_monthly_totals.csv").exists()
    assert not (output_dir / "manaus_rolling7d.csv").exists()
