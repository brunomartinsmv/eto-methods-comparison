"""Print the result tables and generated figures for each configured site."""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence

import pandas as pd

from .config import OUTPUTS_FIGURES, OUTPUTS_REPORTS, OUTPUTS_TABLES, SITES

__all__ = ["main", "show_results_overview"]


def show_results_overview(sites: Sequence[str] | None = None) -> None:
    """Print daily/monthly metric rankings, data quality flags, and figure paths."""
    target_sites = list(sites) if sites else list(SITES)
    required_paths = [
        path
        for site in target_sites
        for path in (
            OUTPUTS_TABLES / f"{site}_daily_metrics.csv",
            OUTPUTS_TABLES / f"{site}_monthly_metrics.csv",
            OUTPUTS_REPORTS / f"{site}_data_quality.csv",
            OUTPUTS_FIGURES / site / f"{site}_monthly_totals.png",
            OUTPUTS_FIGURES / site / f"{site}_daily_taylor.png",
        )
    ]
    missing = [path for path in required_paths if not path.is_file()]
    if missing:
        raise FileNotFoundError(
            "Missing generated outputs. Run `MPLCONFIGDIR=/tmp/matplotlib-cache python -m scripts.cli all --year 2024` "
            "and `python -m scripts.cli validate-data --year 2024` first. Missing: "
            + ", ".join(str(path) for path in missing)
        )

    for site in target_sites:
        print(f"\n{site.upper()} daily metrics")
        daily = pd.read_csv(OUTPUTS_TABLES / f"{site}_daily_metrics.csv")
        print(daily.sort_values("rmse").to_string(index=False))

        print(f"\n{site.upper()} monthly metrics")
        monthly = pd.read_csv(OUTPUTS_TABLES / f"{site}_monthly_metrics.csv")
        print(monthly.sort_values("rmse").to_string(index=False))

        print(f"\n{site.upper()} variables with audit flags")
        report = pd.read_csv(OUTPUTS_REPORTS / f"{site}_data_quality.csv")
        flagged = report.loc[
            (report["missing_values"] > 0)
            | (report["interpolated_values"] > 0)
            | (report["physical_limit_violations"] > 0)
            | report["missing_dates"].fillna("").ne("")
            | report["duplicate_dates"].fillna("").ne("")
        ]
        print(flagged.to_string(index=False) if not flagged.empty else "No audit flags")

        for figure in (f"{site}_monthly_totals.png", f"{site}_daily_taylor.png"):
            print(f"{site.upper()} figure: {OUTPUTS_FIGURES / site / figure}")


def main(argv: Sequence[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        prog="python -m scripts.results_overview",
        description="Print result tables and generated figures for configured sites.",
    )
    parser.add_argument(
        "--site",
        choices=sorted(SITES),
        default=None,
        help="Show overview for a single configured site (default: all sites)",
    )
    args = parser.parse_args(sys.argv[1:] if argv is None else argv)
    sites = [args.site] if args.site else None
    show_results_overview(sites=sites)


if __name__ == "__main__":
    main()
