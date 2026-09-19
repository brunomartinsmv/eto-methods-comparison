"""Smoke tests for figure generation."""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd
from matplotlib.axes import Axes

from scripts import cli
from scripts.cli import cmd_plots
from scripts.config import REFERENCE_COLUMN
from scripts.naming import figure_filename
from scripts.plots import _taylor_stats, plot_taylor


def _minimal_eto_frame(n_days: int = 40) -> pd.DataFrame:
    """Enough days to span two months so monthly Taylor diagram is generated."""
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
    results_dir = tmp_path / "results"
    cleaned_dir.mkdir()
    results_dir.mkdir()
    _minimal_eto_frame().to_csv(cleaned_dir / "manaus_daily.csv", index=False)

    monkeypatch.setattr(cli, "OUTPUTS_FIGURES", figures_dir)
    monkeypatch.setattr("scripts.eto_io.OUTPUTS_RESULTS", results_dir)

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


def test_plot_taylor_uses_paired_finite_values(tmp_path: Path) -> None:
    frame = pd.DataFrame(
        {
            REFERENCE_COLUMN: [1.0, np.nan, 3.0],
            "method": [1.2, 2.0, 3.1],
        }
    )
    output_path = tmp_path / "taylor.png"

    plot_taylor(frame, REFERENCE_COLUMN, [REFERENCE_COLUMN, "method"], output_path, "Taylor")

    assert output_path.is_file()
    assert output_path.stat().st_size > 0


def test_plot_taylor_skips_method_with_fewer_than_two_finite_pairs(
    tmp_path: Path, monkeypatch
) -> None:
    plotted_labels = []
    original_plot = Axes.plot

    def record_plot(self, *args, **kwargs):
        plotted_labels.append(kwargs.get("label"))
        return original_plot(self, *args, **kwargs)

    monkeypatch.setattr(Axes, "plot", record_plot)
    frame = pd.DataFrame(
        {
            REFERENCE_COLUMN: [1.0, 2.0, 3.0],
            "method": [1.2, np.nan, np.nan],
            "valid_method": [1.1, 2.1, 3.1],
        }
    )
    output_path = tmp_path / "taylor.png"

    plot_taylor(
        frame,
        REFERENCE_COLUMN,
        [REFERENCE_COLUMN, "method", "valid_method"],
        output_path,
        "Taylor",
    )

    assert np.isnan(
        _taylor_stats(frame[REFERENCE_COLUMN].to_numpy(), frame["method"].to_numpy())[2]
    )
    assert plotted_labels == ["Reference", "valid_method"]
    assert output_path.is_file()


def test_plot_taylor_returns_without_plotting_when_reference_is_insufficient(tmp_path: Path) -> None:
    frame = pd.DataFrame(
        {
            REFERENCE_COLUMN: [1.0, np.nan],
            "method": [1.2, 2.0],
        }
    )
    output_path = tmp_path / "taylor.png"

    plot_taylor(frame, REFERENCE_COLUMN, [REFERENCE_COLUMN, "method"], output_path, "Taylor")

    assert not output_path.exists()
