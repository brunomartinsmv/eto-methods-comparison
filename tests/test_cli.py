import argparse

import pandas as pd
import pytest

from scripts.cli import build_parser, cmd_aggregate, cmd_calibrate, require_precomputed_eto_mode
from scripts.config import DEFAULT_YEAR
from scripts.pca_analysis import prepare_pca_data, slugify_label


def test_all_command_keeps_2024_default_year_and_default_input() -> None:
    args = build_parser().parse_args(["all"])

    assert args.year == DEFAULT_YEAR
    assert args.input.endswith("data/raw/Evapo.xlsx")
    assert args.output.endswith("data/cleaned")
    assert args.eto_source == "precomputed"
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
    assert args.eto_source == "precomputed"


def test_compute_eto_mode_is_explicitly_not_implemented_yet() -> None:
    args = build_parser().parse_args(["clean", "--compute-eto"])

    with pytest.raises(NotImplementedError, match="compute-eto"):
        require_precomputed_eto_mode(args)


def test_scientific_cli_commands_are_available() -> None:
    parser = build_parser()

    compute = parser.parse_args(["compute-eto", "--site", "manaus", "--include-precomputed"])
    assert compute.input.endswith("data/cleaned")
    assert compute.output.endswith("outputs/results")
    assert compute.site == "manaus"
    assert compute.all_sites is False
    assert compute.include_precomputed is True

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

    pca = parser.parse_args(["pca"])
    assert pca.input.endswith("data/cleaned")
    assert pca.tables.endswith("outputs/tables")
    assert pca.figures.endswith("outputs/figures")

    sensitivity = parser.parse_args(["sensitivity", "--site", "manaus", "--method", "penman_monteith"])
    assert sensitivity.input.endswith("data/cleaned")
    assert sensitivity.tables_output.endswith("outputs/tables")
    assert sensitivity.figures_output.endswith("outputs/figures")
    assert sensitivity.site == "manaus"
    assert sensitivity.all_sites is False
    assert sensitivity.method == "penman_monteith"

    calibrate = parser.parse_args(
        [
            "calibrate",
            "--site",
            "manaus",
            "--method",
            "hargreaves_samani",
            "--train-start",
            "2024-01-01",
            "--train-end",
            "2024-06-30",
            "--test-start",
            "2024-07-01",
            "--test-end",
            "2024-12-31",
        ]
    )
    assert calibrate.input.endswith("data/cleaned")
    assert calibrate.output.endswith("outputs/tables")
    assert calibrate.site == "manaus"
    assert calibrate.all_sites is False
    assert calibrate.method == "hargreaves_samani"
    assert calibrate.train_start == "2024-01-01"


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


def test_prepare_pca_data_keeps_available_candidate_columns_and_drops_incomplete_rows() -> None:
    df = pd.DataFrame(
        {
            "tmed_c": [25.0, 26.0, None],
            "tmax_c": [31.0, 32.0, 33.0],
            "tmin_c": [21.0, 22.0, 23.0],
            "rh_mean_pct": [80.0, 81.0, 82.0],
            "wind_mean_ms": [2.1, 2.2, 2.3],
            "rad_global_mj_m2_d": [18.0, 19.0, 20.0],
            "rad_net_mj_m2_d": [10.0, 11.0, 12.0],
        }
    )

    prepared, columns = prepare_pca_data(df)

    assert columns == [
        "tmed_c",
        "tmax_c",
        "tmin_c",
        "rh_mean_pct",
        "wind_mean_ms",
        "rad_global_mj_m2_d",
        "rad_net_mj_m2_d",
    ]
    assert prepared.shape == (2, 7)


def test_prepare_pca_data_requires_two_complete_rows() -> None:
    df = pd.DataFrame(
        {
            "tmed_c": [25.0, None],
            "tmax_c": [31.0, 32.0],
            "tmin_c": [21.0, 22.0],
            "rh_mean_pct": [80.0, 81.0],
            "wind_mean_ms": [2.1, 2.2],
            "rad_global_mj_m2_d": [18.0, 19.0],
            "rad_net_mj_m2_d": [10.0, 11.0],
        }
    )

    with pytest.raises(ValueError, match="at least two complete rows"):
        prepare_pca_data(df)


def test_slugify_label_normalizes_pca_output_names() -> None:
    assert slugify_label("Mata Atlântica") == "mata_atlantica"


def test_calibrate_command_writes_coefficients_and_metrics(tmp_path) -> None:
    input_dir = tmp_path / "cleaned"
    output_dir = tmp_path / "tables"
    input_dir.mkdir()

    dates = pd.date_range("2024-01-01", periods=4, freq="D")
    pd.DataFrame(
        {
            "date": dates,
            "tmin_c": [20.0, 20.2, 20.4, 20.6],
            "tmax_c": [30.0, 30.2, 30.4, 30.6],
            "tmed_c": [25.0, 25.2, 25.4, 25.6],
            "ra_extraterrestre_mj_m2_d": [34.0, 34.2, 34.4, 34.6],
            "et_penman_monteith": [4.1, 4.2, 4.3, 4.4],
        }
    ).to_csv(input_dir / "manaus_daily.csv", index=False)

    args = argparse.Namespace(
        input=str(input_dir),
        output=str(output_dir),
        year=2024,
        site="manaus",
        all_sites=False,
        method="hargreaves_samani",
        train_start="2024-01-01",
        train_end="2024-01-02",
        test_start="2024-01-03",
        test_end="2024-01-04",
    )
    cmd_calibrate(args)

    assert (output_dir / "manaus_hargreaves_samani_calibration_coefficients.csv").exists()
    metrics = pd.read_csv(output_dir / "manaus_hargreaves_samani_calibration_metrics.csv")
    assert set(metrics["period"]) == {"train", "test"}
    assert set(metrics["variant"]) == {"original", "calibrated"}
