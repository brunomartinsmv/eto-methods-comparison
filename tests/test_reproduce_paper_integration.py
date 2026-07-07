"""Integration test for reproduce-paper using a synthetic Evapo.xlsx fixture."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd
import pytest

from scripts import cli
from scripts.cli import cmd_reproduce_paper
from scripts.naming import cleaned_daily_filename, daily_eto_filename, metrics_filename
from tests.helpers.synthetic_evapo import write_synthetic_evapo_xlsx


@pytest.fixture
def isolated_pipeline_dirs(tmp_path: Path, monkeypatch):
    """Redirect all pipeline output directories to a temporary tree."""
    raw_dir = tmp_path / "raw"
    cleaned_dir = tmp_path / "cleaned"
    results_dir = tmp_path / "results"
    figures_dir = tmp_path / "figures"
    tables_dir = tmp_path / "tables"
    reports_dir = tmp_path / "reports"

    for directory in (raw_dir, cleaned_dir, results_dir, figures_dir, tables_dir, reports_dir):
        directory.mkdir()

    monkeypatch.setattr(cli, "DATA_CLEANED", cleaned_dir)
    monkeypatch.setattr(cli, "OUTPUTS_RESULTS", results_dir)
    monkeypatch.setattr("scripts.eto_io.OUTPUTS_RESULTS", results_dir)
    monkeypatch.setattr(cli, "OUTPUTS_FIGURES", figures_dir)
    monkeypatch.setattr(cli, "OUTPUTS_TABLES", tables_dir)
    monkeypatch.setattr(cli, "OUTPUTS_REPORTS", reports_dir)

    return {
        "raw": raw_dir,
        "cleaned": cleaned_dir,
        "results": results_dir,
        "figures": figures_dir,
        "tables": tables_dir,
        "reports": reports_dir,
    }


def test_reproduce_paper_runs_end_to_end_with_synthetic_fixture(
    isolated_pipeline_dirs, monkeypatch
) -> None:
    dirs = isolated_pipeline_dirs
    xlsx_path = dirs["raw"] / "synthetic_evapo.xlsx"
    write_synthetic_evapo_xlsx(xlsx_path, sheet="Manaus", n_days=14)

    args = argparse.Namespace(
        input=str(xlsx_path),
        output=str(dirs["cleaned"]),
        year=2024,
        site="manaus",
        all_sites=False,
        eto_source="precomputed",
    )
    cmd_reproduce_paper(args)

    assert (dirs["cleaned"] / cleaned_daily_filename("manaus")).exists()
    assert (dirs["results"] / daily_eto_filename("manaus")).exists()
    assert (dirs["tables"] / metrics_filename("manaus", "daily")).exists()
    assert (dirs["tables"] / "summary_rankings.csv").exists()
    assert (dirs["reports"] / "data_quality_summary.csv").exists()

    figures = list((dirs["figures"] / "manaus").glob("*.png"))
    assert figures, "expected figures for manaus"

    eto = pd.read_csv(dirs["results"] / daily_eto_filename("manaus"))
    assert len(eto) == 14
    assert "et_penman_monteith" in eto.columns
    assert "precomputed_et_penman_monteith" in eto.columns
