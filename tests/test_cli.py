import argparse

import pandas as pd
import pytest

from scripts.cli import build_parser, cmd_aggregate, require_precomputed_eto_mode
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
            "tmin_c": [21.0, None, 22.0],
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
    assert prepared.shape == (1, 7)


def test_slugify_label_normalizes_pca_output_names() -> None:
    assert slugify_label("Mata Atlântica") == "mata_atlantica"
