from scripts.cli import build_parser
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

    summarize = parser.parse_args(["summarize"])
    assert summarize.input.endswith("outputs/tables")
    assert summarize.output.endswith("outputs/reports")

    reproduce = parser.parse_args(["reproduce-paper"])
    assert reproduce.year == DEFAULT_YEAR
    assert reproduce.all_sites is True

    supplement = parser.parse_args(["export-supplement"])
    assert supplement.output.endswith("outputs/supplement")
