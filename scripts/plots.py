from __future__ import annotations

from pathlib import Path

import matplotlib
import numpy as np

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd


def plot_scatter(df: pd.DataFrame, ref_col: str, method_col: str, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.figure(figsize=(6, 6))
    plt.scatter(df[ref_col], df[method_col], alpha=0.6)
    plt.xlabel(ref_col)
    plt.ylabel(method_col)
    plt.title(f"Scatter: {method_col} vs {ref_col}")
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(output_path, dpi=200)
    plt.close()


def plot_timeseries(df: pd.DataFrame, ref_col: str, method_col: str, output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.figure(figsize=(10, 4))
    plt.plot(df["date"], df[ref_col], label=ref_col)
    plt.plot(df["date"], df[method_col], label=method_col)
    plt.xlabel("Date")
    plt.ylabel("ETo (mm/d)")
    plt.title(f"Time series: {method_col} vs {ref_col}")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(output_path, dpi=200)
    plt.close()


def plot_monthly_totals(df: pd.DataFrame, method_cols: list[str], output_path: Path) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)
    plt.figure(figsize=(10, 4))
    for col in method_cols:
        plt.plot(df["month"], df[col], label=col)
    plt.xlabel("Month")
    plt.ylabel("Monthly total (mm)")
    plt.title("Monthly totals")
    plt.legend(ncol=2, fontsize=8)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(output_path, dpi=200)
    plt.close()


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


def plot_taylor(df: pd.DataFrame, ref_col: str, method_cols: list[str], output_path: Path, title: str) -> None:
    output_path.parent.mkdir(parents=True, exist_ok=True)

    ref = df[ref_col].to_numpy()
    ref = ref[np.isfinite(ref)]
    if ref.size < 2:
        return
    ref_std = np.std(ref, ddof=1)

    fig = plt.figure(figsize=(7, 6))
    ax = fig.add_subplot(111, polar=True)
    ax.set_theta_direction(-1)
    ax.set_theta_zero_location("E")

    # Correlation labels (0 to 1)
    corr_ticks = np.array([1.0, 0.9, 0.8, 0.7, 0.6, 0.5])
    ax.set_thetagrids(np.degrees(np.arccos(corr_ticks)), labels=[f"{c:.1f}" for c in corr_ticks])
    ax.set_rlabel_position(135)

    # Reference point
    ax.plot(0, ref_std, marker="o", color="black", label="Reference")

    for col in method_cols:
        if col == ref_col:
            continue
        series = df[col].to_numpy()
        _, series_std, corr = _taylor_stats(ref, series)
        if np.isnan(corr):
            continue
        theta = np.arccos(corr)
        ax.plot(theta, series_std, marker="o", label=col)

    ax.set_title(title, pad=20)
    ax.set_xlabel("Correlation", labelpad=10)
    ax.set_ylabel("Standard deviation", labelpad=30)
    ax.legend(loc="upper right", bbox_to_anchor=(1.35, 1.15), fontsize=8)
    plt.tight_layout()
    plt.savefig(output_path, dpi=200)
    plt.close()
