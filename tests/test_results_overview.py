import argparse
import pytest

from scripts import cli, results_overview
from scripts.cli import build_parser


def test_overview_command_parser_defaults() -> None:
    parser = build_parser()
    args = parser.parse_args(["overview"])
    assert args.site is None
    assert args.all_sites is True
    assert args.func == cli.cmd_overview


def test_overview_command_parser_with_site() -> None:
    parser = build_parser()
    args = parser.parse_args(["overview", "--site", "piracicaba"])
    assert args.site == "piracicaba"
    assert args.all_sites is False
    assert args.func == cli.cmd_overview


def test_results_overview_alias_parser() -> None:
    parser = build_parser()
    args = parser.parse_args(["results-overview"])
    assert args.func == cli.cmd_overview


def test_cmd_overview_calls_show_results_overview(monkeypatch) -> None:
    called_with = []
    monkeypatch.setattr(results_overview, "show_results_overview", lambda sites=None: called_with.append(sites))

    parser = build_parser()
    args = parser.parse_args(["overview", "--site", "piracicaba"])
    args.func(args)

    assert called_with == [["piracicaba"]]


def test_results_overview_main_entrypoint(monkeypatch) -> None:
    called_with = []
    monkeypatch.setattr(results_overview, "show_results_overview", lambda sites=None: called_with.append(sites))

    results_overview.main(["--site", "manaus"])
    assert called_with == [["manaus"]]
