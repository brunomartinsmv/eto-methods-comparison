"""Canonical output filenames for pipeline artifacts."""

from __future__ import annotations


def cleaned_daily_filename(site: str) -> str:
    return f"{site}_daily.csv"


def rolling_7d_filename(site: str) -> str:
    return f"{site}_rolling_7d.csv"


def monthly_totals_filename(site: str) -> str:
    return f"{site}_monthly_totals.csv"


def daily_eto_filename(site: str) -> str:
    return f"{site}_daily_eto.csv"


def metrics_filename(site: str, scale: str) -> str:
    return f"{site}_{scale}_metrics.csv"


def bootstrap_filename(site: str) -> str:
    return f"{site}_bootstrap_metric_intervals.csv"


def seasonal_filename(site: str) -> str:
    return f"{site}_seasonal_error_metrics.csv"


def bias_bins_filename(site: str) -> str:
    return f"{site}_bias_by_eto_bin.csv"


def sensitivity_filename(site: str, method: str) -> str:
    return f"{site}_sensitivity_{method}.csv"


def calibration_coefficients_filename(site: str, method: str) -> str:
    return f"{site}_{method}_calibration_coefficients.csv"


def calibration_metrics_filename(site: str, method: str) -> str:
    return f"{site}_{method}_calibration_metrics.csv"


def figure_filename(site: str, product: str) -> str:
    return f"{site}_{product}.png"


def method_only_filename(site: str, method_id: str) -> str:
    return f"{site}_{method_id}_only.csv"


def method_feasibility_filename(site: str) -> str:
    return f"{site}_method_feasibility.csv"


def input_summary_filename(site: str) -> str:
    return f"{site}_input_summary.csv"


def site_report_md_filename(site: str) -> str:
    return f"{site}_report.md"


def site_report_html_filename(site: str) -> str:
    return f"{site}_report.html"
