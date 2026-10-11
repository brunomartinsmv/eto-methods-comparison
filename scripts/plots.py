from __future__ import annotations

from io import StringIO
from pathlib import Path

import matplotlib
import matplotlib.dates as mdates
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

from .figure_style import PALETTE, apply_figure_style, method_label, style_axis


def plot_scatter(df: pd.DataFrame, ref_col: str, method_col: str, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    valid = df[[ref_col, method_col]].apply(pd.to_numeric, errors="coerce")
    valid = valid.loc[np.isfinite(valid).all(axis=1)]
    if valid.empty:
        output_path.unlink(missing_ok=True)
        return
    apply_figure_style()
    fig, ax = plt.subplots(figsize=(7.0, 6.5))
    ax.scatter(
        valid[ref_col], valid[method_col], s=18, alpha=0.42, color=PALETTE["blue"], linewidths=0
    )
    lower = min(0.0, float(valid.min().min()))
    upper = float(valid.max().max())
    margin = max((upper - lower) * 0.04, 0.1)
    limits = (lower - margin, upper + margin)
    ax.plot(limits, limits, color=PALETTE["red"], linewidth=1.3, linestyle=(0, (4, 3)), label="1:1")
    ax.set(
        xlim=limits,
        ylim=limits,
        xlabel=f"{method_label(ref_col)} ET₀ (mm d⁻¹)",
        ylabel=f"{method_label(method_col)} ET₀ (mm d⁻¹)",
    )
    ax.set_aspect("equal", adjustable="box")
    ax.legend(loc="upper left")
    ax.grid(color=PALETTE["gray_light"], linewidth=0.5, alpha=0.55)
    fig.tight_layout(pad=1.2)
    fig.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close(fig)


def plot_timeseries(df: pd.DataFrame, ref_col: str, method_col: str, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    apply_figure_style()
    fig, ax = plt.subplots(figsize=(12, 4.5))
    ax.plot(
        df["date"],
        df[ref_col],
        color=PALETTE["ink"],
        linewidth=2.0,
        alpha=0.9,
        label=method_label(ref_col),
    )
    ax.plot(
        df["date"],
        df[method_col],
        color=PALETTE["blue"],
        linewidth=1.8,
        alpha=0.9,
        label=method_label(method_col),
    )
    ax.set(xlabel="Date", ylabel="ET₀ (mm d⁻¹)")
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, 1.16), ncol=2)
    style_axis(ax)
    ax.grid(axis="x", visible=False)
    fig.autofmt_xdate(rotation=0)
    fig.tight_layout(pad=1.1)
    fig.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close(fig)


def plot_monthly_totals(df: pd.DataFrame, method_cols: list[str], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    apply_figure_style()
    alternatives = [col for col in method_cols if col != "et_penman_monteith"]
    panels = [alternatives[index : index + 3] for index in range(0, len(alternatives), 3)] or [[]]
    ncols = min(2, len(panels))
    fig, axes = plt.subplots(
        (len(panels) + ncols - 1) // ncols,
        ncols,
        figsize=(8 * ncols, 4.8 * ((len(panels) + ncols - 1) // ncols)),
        sharex=True,
        sharey=True,
        squeeze=False,
    )
    colors = [PALETTE["blue"], PALETTE["red"], PALETTE["teal"]]
    for ax, columns in zip(axes.flat, panels, strict=False):
        for index, col in enumerate(columns):
            ax.plot(
                df["month"],
                df[col],
                color=colors[index],
                linestyle=["-", "--", ":"][index],
                marker=["o", "s", "^"][index],
                markersize=4,
                linewidth=2,
                label=method_label(col),
            )
        if "et_penman_monteith" in method_cols:
            ax.plot(
                df["month"],
                df["et_penman_monteith"],
                color=PALETTE["ink"],
                linewidth=2.5,
                label="Penman–Monteith",
                zorder=5,
            )
        ax.set(xlabel="Month", ylabel="Monthly ET₀ (mm)")
        ax.xaxis.set_major_locator(mdates.MonthLocator(interval=2))
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%b"))
        ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.22), ncol=2, fontsize=10)
        style_axis(ax)
        ax.grid(axis="x", visible=False)
    for ax in list(axes.flat)[len(panels) :]:
        ax.set_axis_off()
    fig.tight_layout(pad=2, h_pad=4)
    fig.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close(fig)


def plot_bias_by_eto_bin(df: pd.DataFrame, output_path: Path, title: str) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if df.empty:
        output_path.unlink(missing_ok=True)
        return

    apply_figure_style()
    groups = list(df.groupby("method", sort=False))
    panels = [groups[index : index + 3] for index in range(0, len(groups), 3)]
    ncols = min(2, len(panels))
    nrows = (len(panels) + ncols - 1) // ncols
    fig, axes = plt.subplots(
        nrows, ncols, figsize=(8 * ncols, 4.5 * nrows), sharex=True, sharey=True, squeeze=False
    )
    colors = [PALETTE["blue"], PALETTE["red"], PALETTE["teal"]]
    for ax, panel in zip(axes.flat, panels, strict=False):
        for index, (method, group) in enumerate(panel):
            group = group.sort_values("eto_bin")
            ax.plot(
                group["eto_bin"],
                group["mean_bias"],
                marker=["o", "s", "^"][index],
                linestyle=["-", "--", ":"][index],
                markersize=5,
                linewidth=2,
                color=colors[index],
                label=method_label(method),
            )
        ax.axhline(0, color=PALETTE["ink"], linewidth=1)
        ax.set(xlabel="Reference ET₀ quantile bin", ylabel="Mean bias (mm d⁻¹)")
        ax.set_xticks(sorted(df["eto_bin"].unique()))
        ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.22), ncol=2, fontsize=10)
        style_axis(ax)
        ax.grid(axis="x", visible=False)
    for ax in list(axes.flat)[len(panels) :]:
        ax.set_axis_off()
    fig.suptitle(title, fontsize=18)
    fig.tight_layout(pad=2, h_pad=4)
    fig.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close(fig)


def _taylor_stats(ref: np.ndarray, series: np.ndarray) -> tuple[float, float, float]:
    mask = np.isfinite(ref) & np.isfinite(series)
    ref = ref[mask]
    series = series[mask]
    if ref.size < 2 or series.size < 2:
        return np.nan, np.nan, np.nan
    ref_std = np.std(ref, ddof=1)
    series_std = np.std(series, ddof=1)
    if ref_std == 0 or series_std == 0:
        corr = np.nan
    else:
        corr = np.corrcoef(ref, series)[0, 1]
    return ref_std, series_std, corr


def plot_taylor(
    df: pd.DataFrame,
    ref_col: str,
    method_cols: list[str],
    output_path: Path,
    title: str,
    *,
    unit: str = "mm d⁻¹",
) -> None:
    """Plot correlation against standard deviation.

    The reference marker uses the standard deviation of every finite reference
    value. Each method uses only the days on which both that method and the
    reference are finite, so its position can describe a different subset.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)

    ref = df[ref_col].to_numpy()
    finite_ref = ref[np.isfinite(ref)]
    if finite_ref.size < 2:
        output_path.unlink(missing_ok=True)
        return
    ref_std = np.std(finite_ref, ddof=1)

    apply_figure_style()
    fig = plt.figure(figsize=(11, 8))
    ax = fig.add_subplot(111, polar=True)
    ax.set_theta_direction(1)
    ax.set_thetamin(0)
    ax.set_thetamax(180)
    ax.set_theta_zero_location("E")

    corr_ticks = np.array([1.0, 0.9, 0.7, 0.5, 0.0, -0.5, -0.7, -0.9, -1.0])
    ax.set_thetagrids(np.degrees(np.arccos(corr_ticks)), labels=[f"{c:.1f}" for c in corr_ticks])
    ax.set_rlabel_position(135)

    ax.plot(
        0,
        ref_std,
        marker="*",
        markersize=10,
        color=PALETTE["red"],
        label=method_label(ref_col),
        zorder=5,
    )

    alternatives = [col for col in method_cols if col != ref_col]
    colors = [PALETTE[key] for key in ("blue", "red", "teal", "violet", "gray", "green")]
    for index, col in enumerate(alternatives):
        series = df[col].to_numpy()
        _, series_std, corr = _taylor_stats(ref, series)
        if np.isnan(corr):
            continue
        theta = np.arccos(np.clip(corr, -1.0, 1.0))
        ax.plot(
            theta,
            series_std,
            marker=["o", "s", "^", "D", "v", "P"][index // len(colors)],
            markersize=6,
            linestyle="none",
            color=colors[index % len(colors)],
            label=method_label(col),
        )

    ax.set_title(title, pad=18)
    ax.set_xlabel("Correlation", labelpad=10)
    ax.set_ylabel(f"Standard deviation ({unit})", labelpad=24)
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.13), ncol=3, fontsize=11)
    fig.tight_layout(pad=1.1)
    fig.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close(fig)


def plot_readme_overview(
    metrics_by_site: dict[str, pd.DataFrame], output_path: Path, top_n: int = 8
) -> None:
    best_by_site = {}
    for site, metrics in metrics_by_site.items():
        if metrics.empty:
            continue
        best = metrics.assign(rmse=pd.to_numeric(metrics["rmse"], errors="coerce"))
        best = best.loc[np.isfinite(best["rmse"])]
        if not best.empty:
            best_by_site[site] = best.nsmallest(top_n, "rmse")
    if not best_by_site:
        output_path.unlink(missing_ok=True)
        output_path.with_suffix(".svg").unlink(missing_ok=True)
        return

    output_path.parent.mkdir(parents=True, exist_ok=True)
    apply_figure_style(font_size=15)
    fig, axes = plt.subplots(
        1, len(best_by_site), figsize=(8 * len(best_by_site), 7.5), sharex=True, squeeze=False
    )
    xmax = max(max(best["rmse"].max() for best in best_by_site.values()) * 1.2, 0.1)

    for ax, (site, best) in zip(axes[0], best_by_site.items(), strict=True):
        for position, row in enumerate(best.itertuples(index=False)):
            is_best = position == 0
            color = PALETTE["blue"] if is_best else PALETTE["blue_light"]
            ax.hlines(position, 0, row.rmse, color=PALETTE["gray_light"], linewidth=1.8, zorder=1)
            ax.scatter(
                row.rmse,
                position,
                s=64 if is_best else 46,
                color=color,
                edgecolor="white",
                linewidth=0.8,
                zorder=3,
            )
            ax.text(
                row.rmse + xmax * 0.018,
                position,
                f"{row.rmse:.2f}",
                va="center",
                fontsize=12,
                color=PALETTE["ink"],
            )
        ax.set_yticks(range(len(best)), [method_label(method) for method in best["method"]])
        ax.invert_yaxis()
        ax.set_xlim(0, xmax)
        ax.set_title(site.title(), loc="left", fontweight="bold", pad=12)
        ax.set_xlabel("Daily RMSE (mm d⁻¹)")
        ax.grid(axis="x", color=PALETTE["gray_light"], linewidth=0.6, alpha=0.55)
        ax.grid(axis="y", visible=False)
        ax.spines["left"].set_visible(False)
        ax.tick_params(axis="y", length=0, pad=8)

    fig.suptitle(
        "Daily agreement with FAO-56 Penman–Monteith",
        x=0.08,
        y=0.98,
        ha="left",
        fontsize=20,
        fontweight="bold",
    )
    fig.text(
        0.08,
        0.92,
        f"Up to {top_n} methods with the lowest RMSE at each selected site",
        color=PALETTE["gray"],
        fontsize=13,
    )
    fig.tight_layout(rect=(0.02, 0.03, 0.98, 0.89), w_pad=2.6)
    fig.savefig(output_path, dpi=300, bbox_inches="tight")
    svg = StringIO()
    fig.savefig(svg, format="svg", bbox_inches="tight", metadata={"Date": None})
    output_path.with_suffix(".svg").write_text(
        "\n".join(line.rstrip() for line in svg.getvalue().splitlines()) + "\n", encoding="utf-8"
    )
    plt.close(fig)
