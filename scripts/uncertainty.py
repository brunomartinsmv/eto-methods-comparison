from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from . import metrics

METRICS_FOR_INTERVALS = {
    "rmse": metrics.rmse,
    "mae": metrics.mae,
    "mbe": metrics.mbe,
}


def _paired_arrays(df: pd.DataFrame, ref_col: str, method_col: str) -> tuple[np.ndarray, np.ndarray]:
    ref = df[ref_col].to_numpy(dtype=float)
    series = df[method_col].to_numpy(dtype=float)
    mask = np.isfinite(ref) & np.isfinite(series)
    return ref[mask], series[mask]


def bootstrap_metric_intervals(
    df: pd.DataFrame,
    ref_col: str,
    method_cols: list[str],
    *,
    n_boot: int = 1000,
    confidence: float = 0.95,
    random_state: int = 2024,
) -> pd.DataFrame:
    """Estimate percentile bootstrap confidence intervals for daily metrics."""
    if n_boot < 1:
        raise ValueError("n_boot must be at least 1")
    if not 0 < confidence < 1:
        raise ValueError("confidence must be between 0 and 1")

    rng = np.random.default_rng(random_state)
    alpha = 1 - confidence
    rows = []
    for method_col in method_cols:
        ref, series = _paired_arrays(df, ref_col, method_col)
        n = len(ref)
        if n == 0:
            continue
        sample_indices = rng.integers(0, n, size=(n_boot, n))
        for metric_name, metric_func in METRICS_FOR_INTERVALS.items():
            estimates = np.array(
                [metric_func(ref[indices], series[indices]) for indices in sample_indices],
                dtype=float,
            )
            rows.append(
                {
                    "method": method_col,
                    "metric": metric_name,
                    "estimate": metric_func(ref, series),
                    "ci_lower": float(np.nanquantile(estimates, alpha / 2)),
                    "ci_upper": float(np.nanquantile(estimates, 1 - alpha / 2)),
                    "n": n,
                    "n_boot": n_boot,
                    "confidence": confidence,
                }
            )
    return pd.DataFrame(
        rows,
        columns=[
            "method",
            "metric",
            "estimate",
            "ci_lower",
            "ci_upper",
            "n",
            "n_boot",
            "confidence",
        ],
    )


def seasonal_error_metrics(
    df: pd.DataFrame,
    ref_col: str,
    method_cols: list[str],
    *,
    rainfall_col: str = "rain_mm",
) -> pd.DataFrame:
    """Summarize method errors by calendar month and local wet/dry months."""
    work = df.copy()
    work["date"] = pd.to_datetime(work["date"])
    work["month"] = work["date"].dt.to_period("M").astype(str)

    rows = []
    for month, group in work.groupby("month", sort=True):
        rows.extend(_error_rows(group, ref_col, method_cols, "month", month, rainfall_col))

    if rainfall_col in work.columns:
        monthly_rain = work.groupby("month", sort=True)[rainfall_col].sum()
        threshold = monthly_rain.median()
        season_by_month = {
            month: "wet" if rain >= threshold else "dry" for month, rain in monthly_rain.items()
        }
        work["rainfall_season"] = work["month"].map(season_by_month)
        for season, group in work.groupby("rainfall_season", sort=True):
            rows.extend(_error_rows(group, ref_col, method_cols, "rainfall_season", season, rainfall_col))

    return pd.DataFrame(
        rows,
        columns=["period_type", "period", "method", "n", "rain_mm", "rmse", "mae", "mbe"],
    )


def _error_rows(
    df: pd.DataFrame,
    ref_col: str,
    method_cols: list[str],
    period_type: str,
    period: str,
    rainfall_col: str,
) -> list[dict[str, object]]:
    rows = []
    rain_mm = float(df[rainfall_col].sum()) if rainfall_col in df.columns else float("nan")
    for method_col in method_cols:
        ref, series = _paired_arrays(df, ref_col, method_col)
        if len(ref) == 0:
            continue
        rows.append(
            {
                "period_type": period_type,
                "period": period,
                "method": method_col,
                "n": len(ref),
                "rain_mm": rain_mm,
                "rmse": metrics.rmse(ref, series),
                "mae": metrics.mae(ref, series),
                "mbe": metrics.mbe(ref, series),
            }
        )
    return rows


def bias_by_eto_bin(
    df: pd.DataFrame,
    ref_col: str,
    method_cols: list[str],
    *,
    n_bins: int = 4,
) -> pd.DataFrame:
    if n_bins < 2:
        raise ValueError("n_bins must be at least 2")

    rows = []
    ref = pd.to_numeric(df[ref_col], errors="coerce")
    valid_ref = ref[np.isfinite(ref)]
    if valid_ref.empty:
        return pd.DataFrame()

    ranks = valid_ref.rank(method="first")
    bin_labels = pd.qcut(ranks, q=n_bins, labels=False, duplicates="drop") + 1
    binned = df.loc[valid_ref.index].copy()
    binned["eto_bin"] = bin_labels.astype("Int64")

    for method_col in method_cols:
        work = binned[[ref_col, method_col, "eto_bin"]].copy()
        work[method_col] = pd.to_numeric(work[method_col], errors="coerce")
        work["bias"] = work[method_col] - work[ref_col]
        work = work[np.isfinite(work["bias"])]
        for eto_bin, group in work.groupby("eto_bin", sort=True):
            rows.append(
                {
                    "method": method_col,
                    "eto_bin": int(eto_bin),
                    "eto_min": float(group[ref_col].min()),
                    "eto_max": float(group[ref_col].max()),
                    "n": len(group),
                    "mean_ref_eto": float(group[ref_col].mean()),
                    "mean_bias": float(group["bias"].mean()),
                    "median_bias": float(group["bias"].median()),
                }
            )
    return pd.DataFrame(
        rows,
        columns=[
            "method",
            "eto_bin",
            "eto_min",
            "eto_max",
            "n",
            "mean_ref_eto",
            "mean_bias",
            "median_bias",
        ],
    )


def write_uncertainty_report(
    site: str,
    bootstrap: pd.DataFrame,
    seasonal: pd.DataFrame,
    bias_bins: pd.DataFrame,
    output_dir: Path,
) -> Path:
    output_dir.mkdir(parents=True, exist_ok=True)
    path = output_dir / f"{site}_uncertainty_sensitivity.md"
    lines = [
        f"# Uncertainty and sensitivity analysis: {site}",
        "",
        "Bootstrap intervals use paired daily resampling against Penman-Monteith and are descriptive, not a substitute for measurement-error propagation.",
        "Wet/dry grouping is data-driven from the median monthly rainfall within the analyzed year.",
        "",
        "## Bootstrap intervals",
        "",
        _markdown_table(bootstrap),
        "",
        "## Monthly and rainfall-season errors",
        "",
        _markdown_table(seasonal),
        "",
        "## Bias by reference ETo range",
        "",
        _markdown_table(bias_bins),
        "",
        "## Limitations",
        "",
        "- Confidence intervals resample available paired days and do not model autocorrelation explicitly.",
        "- Wet/dry labels are relative to each site's 2024 monthly rainfall distribution.",
        "- Bias bins are quantile-based, so bin widths differ when the Penman-Monteith ETo distribution is uneven.",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def _markdown_table(df: pd.DataFrame, max_rows: int = 20) -> str:
    if df.empty:
        return "No rows available."
    table = df.head(max_rows).copy()
    for column in table.select_dtypes(include=["float"]).columns:
        table[column] = table[column].map(lambda value: f"{value:.4f}")
    lines = ["| " + " | ".join(table.columns) + " |"]
    lines.append("| " + " | ".join(["---"] * len(table.columns)) + " |")
    for row in table.itertuples(index=False, name=None):
        lines.append("| " + " | ".join(str(value) for value in row) + " |")
    if len(df) > max_rows:
        lines.append(f"\nShowing first {max_rows} of {len(df)} rows. See CSV outputs for complete tables.")
    return "\n".join(lines)
