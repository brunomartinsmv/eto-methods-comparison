"""Smoke tests for figure generation."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from scripts import cli
from scripts.cli import cmd_plots
from scripts.config import REFERENCE_COLUMN
from scripts.naming import figure_filename


def _minimal_eto_frame(n_days: int = 7) -> pd.DataFrame:
    dates = pd.date_range("2024-01-01", periods=n_days, freq="D")
    return pd.DataFrame(
        {
            "date": dates,
            REFERENCE_COLUMN: [2.0 + 0.1 * i for i in range(n_days)],
            "et_hargreaves_samani": [2.2 + 0.1 * i for i in range(n_days)],
            "et_priestley_taylor": [1.8 + 0.1 * i for i in range(n_days)],
        }
    )


def test_plots_command_writes_expected_figures_in_temporary_directory(
    tmp_path: Path, monkeypatch
) -> None:
    cleaned_dir = tmp_path / "cleaned"
    figures_dir = tmp_path / "figures"
    cleaned_dir.mkdir()
    _minimal_eto_frame().to_csv(cleaned_dir / "manaus_daily.csv", index=False)

    monkeypatch.setattr(cli, "OUTPUTS_FIGURES", figures_dir)

    args = argparse.Namespace(
        input=str(cleaned_dir),
        output=str(figures_dir),
        year=2024,
        site="manaus",
        all_sites=False,
    )
    cmd_plots(args)

    site_dir = figures_dir / "manaus"
    assert site_dir.is_dir()
    png_files = sorted(site_dir.glob("*.png"))
    assert png_files, "expected at least one PNG figure"

    expected_stems = {
        Path(figure_filename("manaus", "daily_scatter_hs_vs_pm")).stem,
        Path(figure_filename("manaus", "daily_scatter_pt_vs_pm")).stem,
        Path(figure_filename("manaus", "daily_series_hs_vs_pm")).stem,
        Path(figure_filename("manaus", "monthly_totals")).stem,
        Path(figure_filename("manaus", "daily_taylor")).stem,
        Path(figure_filename("manaus", "monthly_taylor")).stem,
    }
    written_stems = {path.stem for path in png_files}
    assert expected_stems <= written_stems

    for path in png_files:
        assert path.stat().st_size > 0
