"""Tests for supplement export (file copy and MANIFEST.md)."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from scripts import cli
from scripts.cli import cmd_export_supplement


def test_export_supplement_copies_csv_files_and_writes_manifest(
    tmp_path: Path, monkeypatch
) -> None:
    tables_dir = tmp_path / "tables"
    results_dir = tmp_path / "results"
    reports_dir = tmp_path / "reports"
    supplement_dir = tmp_path / "supplement"

    for directory in (tables_dir, results_dir, reports_dir):
        directory.mkdir()

    pd.DataFrame({"method": ["et_hs"], "rmse": [1.0]}).to_csv(
        tables_dir / "manaus_daily_metrics.csv", index=False
    )
    pd.DataFrame({"date": ["2024-01-01"], "et_penman_monteith": [2.0]}).to_csv(
        results_dir / "manaus_daily_eto.csv", index=False
    )
    pd.DataFrame({"site": ["manaus"], "missing_days": [0]}).to_csv(
        reports_dir / "data_quality_summary.csv", index=False
    )

    monkeypatch.setattr(cli, "OUTPUTS_TABLES", tables_dir)
    monkeypatch.setattr(cli, "OUTPUTS_RESULTS", results_dir)
    monkeypatch.setattr(cli, "OUTPUTS_REPORTS", reports_dir)

    args = argparse.Namespace(output=str(supplement_dir))
    cmd_export_supplement(args)

    copied_tables = supplement_dir / "tables" / "manaus_daily_metrics.csv"
    copied_results = supplement_dir / "results" / "manaus_daily_eto.csv"
    copied_reports = supplement_dir / "reports" / "data_quality_summary.csv"
    manifest = supplement_dir / "MANIFEST.md"

    assert copied_tables.exists()
    assert copied_results.exists()
    assert copied_reports.exists()
    assert manifest.exists()

    manifest_text = manifest.read_text(encoding="utf-8")
    assert "# Supplement export" in manifest_text
    assert "tables/manaus_daily_metrics.csv" in manifest_text
    assert "SHA256" in manifest_text

    assert pd.read_csv(copied_tables).equals(pd.read_csv(tables_dir / "manaus_daily_metrics.csv"))
