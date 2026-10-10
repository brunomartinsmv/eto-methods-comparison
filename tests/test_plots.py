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
    assert plotted_labels == ["Penman–Monteith", "Valid Method"]
    assert output_path.is_file()


def test_plot_taylor_returns_without_plotting_when_reference_is_insufficient(
    tmp_path: Path,
) -> None:
    frame = pd.DataFrame(
        {
            REFERENCE_COLUMN: [1.0, np.nan],
            "method": [1.2, 2.0],
        }
    )
    output_path = tmp_path / "taylor.png"

    plot_taylor(frame, REFERENCE_COLUMN, [REFERENCE_COLUMN, "method"], output_path, "Taylor")

    assert not output_path.exists()


def test_scatter_excludes_nonfinite_pairs(tmp_path: Path, monkeypatch) -> None:
    from matplotlib.figure import Figure

    from scripts.plots import plot_scatter

    captured = []
    monkeypatch.setattr(Figure, "savefig", lambda self, *args, **kwargs: captured.append(self))
    frame = pd.DataFrame({"reference": [1.0, np.inf, 3.0], "method": [2.0, 2.0, np.nan]})
    plot_scatter(frame, "reference", "method", tmp_path / "scatter.png")

    ax = captured[0].axes[0]
    np.testing.assert_array_equal(ax.collections[0].get_offsets(), [[1.0, 2.0]])
    assert ax.get_xlim() == ax.get_ylim()
    assert ax.get_xlabel() == "Reference ET₀ (mm d⁻¹)"


def test_scatter_skips_when_no_finite_pairs(tmp_path: Path) -> None:
    from scripts.plots import plot_scatter

    frame = pd.DataFrame({"reference": [np.inf, np.nan], "method": [1.0, 2.0]})
    output = tmp_path / "scatter.png"
    plot_scatter(frame, "reference", "method", output)
    assert not output.exists()


def test_monthly_totals_without_reference(tmp_path: Path) -> None:
    from scripts.plots import plot_monthly_totals

    frame = pd.DataFrame(
        {
            "month": pd.date_range("2024-01-01", periods=2, freq="MS"),
            "method": [1.0, 2.0],
            "other": [2.0, 3.0],
        }
    )
    output = tmp_path / "monthly.png"
    plot_monthly_totals(frame, ["method", "other"], output)
    assert output.is_file()


def test_overview_ignores_nonfinite_errors_and_handles_zero_rmse(
    tmp_path: Path, monkeypatch
) -> None:
    from matplotlib.figure import Figure

    from scripts.plots import plot_readme_overview

    captured = []
    monkeypatch.setattr(Figure, "savefig", lambda self, *args, **kwargs: captured.append(self))
    valid = pd.DataFrame({"method": ["exact", "infinite"], "rmse": [0.0, np.inf]})
    missing = pd.DataFrame({"method": ["missing"], "rmse": [np.nan]})
    plot_readme_overview({"custom": valid, "missing": missing}, tmp_path / "overview.png")
    ax = captured[0].axes[0]
    assert ax.get_title(loc="left") == "Custom"
    assert [label.get_text() for label in ax.get_yticklabels()] == ["Exact"]
    assert ax.get_xlim()[1] > 0


def test_plots_overview_uses_selected_site_and_current_frame(tmp_path: Path, monkeypatch) -> None:
    cleaned = tmp_path / "cleaned"
    figures = tmp_path / "figures"
    results = tmp_path / "results"
    cleaned.mkdir()
    results.mkdir()
    frame = _minimal_eto_frame()
    frame.to_csv(cleaned / "manaus_daily.csv", index=False)
    monkeypatch.setattr("scripts.eto_io.OUTPUTS_RESULTS", results)
    for name in ("plot_scatter", "plot_timeseries", "plot_monthly_totals", "plot_taylor"):
        monkeypatch.setattr(cli.plots, name, lambda *args, **kwargs: None)
    captured = []
    monkeypatch.setattr(cli.plots, "plot_readme_overview", lambda data, path: captured.append(data))
    cmd_plots(
        argparse.Namespace(
            input=str(cleaned), output=str(figures), year=2024, site="manaus", all_sites=False
        )
    )
    assert list(captured[0]) == ["manaus"]
    np.testing.assert_allclose(captured[0]["manaus"]["rmse"], [0.2, 0.2])


def test_taylor_shows_negative_correlation_and_monthly_units(tmp_path: Path, monkeypatch) -> None:
    from matplotlib.figure import Figure

    captured = []
    monkeypatch.setattr(Figure, "savefig", lambda self, *args, **kwargs: captured.append(self))
    frame = pd.DataFrame({REFERENCE_COLUMN: [1.0, 2.0, 3.0], "opposite": [3.0, 2.0, 1.0]})
    plot_taylor(
        frame,
        REFERENCE_COLUMN,
        [REFERENCE_COLUMN, "opposite"],
        tmp_path / "taylor.png",
        "Monthly",
        unit="mm",
    )
    ax = captured[0].axes[0]
    assert ax.get_ylabel() == "Standard deviation (mm)"
    assert ax.get_thetamax() == 180
    np.testing.assert_allclose(ax.lines[1].get_xdata(), [np.pi])


def test_overview_svg_is_reproducible(tmp_path: Path) -> None:
    from scripts.plots import plot_readme_overview

    metrics = {"manaus": pd.DataFrame({"method": ["et_turc"], "rmse": [0.5]})}
    first = tmp_path / "first.png"
    second = tmp_path / "second.png"
    plot_readme_overview(metrics, first)
    plot_readme_overview(metrics, second)
    assert first.with_suffix(".svg").read_bytes() == second.with_suffix(".svg").read_bytes()
