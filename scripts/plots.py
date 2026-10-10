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
        return
    apply_figure_style()
    fig, ax = plt.subplots(figsize=(5.4, 5.0))
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
    fig, ax = plt.subplots(figsize=(10, 3.6))
    ax.plot(
        df["date"],
        df[ref_col],
        color=PALETTE["ink"],
        linewidth=1.25,
        alpha=0.82,
        label=method_label(ref_col),
    )
    ax.plot(
        df["date"],
        df[method_col],
        color=PALETTE["blue"],
        linewidth=1.0,
        alpha=0.8,
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
    apply_figure_style(font_size=9.5)
    fig, ax = plt.subplots(figsize=(10, 4.6))
    alternatives = [col for col in method_cols if col != "et_penman_monteith"]
    colors = plt.cm.tab20(np.linspace(0, 1, max(len(alternatives), 1)))
    for index, col in enumerate(alternatives):
        ax.plot(
            df["month"],
            df[col],
            color=colors[index],
            linewidth=1.15,
            alpha=0.78,
            label=method_label(col),
        )
    if "et_penman_monteith" in method_cols:
        ax.plot(
            df["month"],
            df["et_penman_monteith"],
            color=PALETTE["ink"],
            linewidth=2.4,
            label="Penman–Monteith",
            zorder=5,
        )
    ax.set(xlabel="Month", ylabel="Monthly ET₀ (mm)")
    ax.xaxis.set_major_locator(mdates.MonthLocator())
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b"))
    ax.legend(ncol=4, loc="upper center", bbox_to_anchor=(0.5, -0.2), fontsize=8)
    style_axis(ax)
    ax.grid(axis="x", visible=False)
    fig.tight_layout(pad=1.1)
    fig.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close(fig)


def plot_bias_by_eto_bin(df: pd.DataFrame, output_path: Path, title: str) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    if df.empty:
        return

    apply_figure_style(font_size=9.5)
    fig, ax = plt.subplots(figsize=(10, 5.2))
    groups = list(df.groupby("method", sort=False))
    colors = plt.cm.tab20(np.linspace(0, 1, max(len(groups), 1)))
    for index, (method, group) in enumerate(groups):
        group = group.sort_values("eto_bin")
        ax.plot(
            group["eto_bin"],
            group["mean_bias"],
            marker="o",
            markersize=3.5,
            linewidth=1.25,
            color=colors[index],
            label=method_label(method),
        )
    ax.axhline(0, color=PALETTE["ink"], linewidth=0.9, alpha=0.7)
    ax.set(xlabel="Penman–Monteith ET₀ quantile", ylabel="Mean bias (mm d⁻¹)", title=title)
    ax.legend(ncol=4, loc="upper center", bbox_to_anchor=(0.5, -0.2), fontsize=8)
    style_axis(ax)
    ax.grid(axis="x", visible=False)
    fig.tight_layout(pad=1.1)
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
    output_path.parent.mkdir(parents=True, exist_ok=True)

    ref = df[ref_col].to_numpy()
    finite_ref = ref[np.isfinite(ref)]
    if finite_ref.size < 2:
        return
    ref_std = np.std(finite_ref, ddof=1)

    apply_figure_style(font_size=9.5)
    fig = plt.figure(figsize=(7.5, 6.2))
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
    colors = plt.cm.tab20(np.linspace(0, 1, max(len(alternatives), 1)))
    for index, col in enumerate(alternatives):
        series = df[col].to_numpy()
        _, series_std, corr = _taylor_stats(ref, series)
        if np.isnan(corr):
            continue
        theta = np.arccos(np.clip(corr, -1.0, 1.0))
        ax.plot(
            theta,
            series_std,
            marker="o",
            markersize=4.5,
            linestyle="none",
            color=colors[index],
            label=method_label(col),
        )

    ax.set_title(title, pad=18)
    ax.set_xlabel("Correlation", labelpad=10)
    ax.set_ylabel(f"Standard deviation ({unit})", labelpad=24)
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.13), ncol=4, fontsize=8)
    fig.tight_layout(pad=1.1)
    fig.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close(fig)


def plot_readme_overview(
    metrics_by_site: dict[str, pd.DataFrame], output_path: Path, top_n: int = 8
) -> None:
    best_by_site = {}
    for site, metrics in metrics_by_site.items():
        best = metrics.assign(rmse=pd.to_numeric(metrics["rmse"], errors="coerce"))
        best = best.loc[np.isfinite(best["rmse"])]
        if not best.empty:
            best_by_site[site] = best.nsmallest(top_n, "rmse")
    if not best_by_site:
        return

    output_path.parent.mkdir(parents=True, exist_ok=True)
    apply_figure_style(font_size=11)
    fig, axes = plt.subplots(
        1, len(best_by_site), figsize=(6 * len(best_by_site), 6.1), sharex=True, squeeze=False
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
                fontsize=9,
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
        fontsize=16,
        fontweight="bold",
    )
    fig.text(
        0.08,
        0.92,
        f"Up to {top_n} methods with the lowest RMSE at each selected site",
        color=PALETTE["gray"],
        fontsize=10.5,
    )
    fig.tight_layout(rect=(0.02, 0.03, 0.98, 0.89), w_pad=2.6)
    fig.savefig(output_path, dpi=300, bbox_inches="tight")
    svg = StringIO()
    fig.savefig(svg, format="svg", bbox_inches="tight", metadata={"Date": None})
    output_path.with_suffix(".svg").write_text(
        "\n".join(line.rstrip() for line in svg.getvalue().splitlines()) + "\n", encoding="utf-8"
    )
    plt.close(fig)
