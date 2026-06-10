from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from . import aggregate, cleaning, io, metrics, plots, quality
from .config import (
    DATA_CLEANED,
    DATA_RAW,
    DEFAULT_YEAR,
    METHOD_COLUMNS,
    METHOD_SHORT,
    OUTPUTS_FIGURES,
    OUTPUTS_REPORTS,
    OUTPUTS_RESULTS,
    OUTPUTS_TABLES,
    REFERENCE_COLUMN,
    SITES,
    select_sites,
)


class SiteAction(argparse.Action):
    def __call__(
        self,
        parser: argparse.ArgumentParser,
        namespace: argparse.Namespace,
        values: str,
        option_string: str | None = None,
    ) -> None:
        setattr(namespace, self.dest, values)
        namespace.all_sites = False


def _ensure_dir(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)


def _method_cols_present(df: pd.DataFrame) -> list[str]:
    return [col for col in METHOD_COLUMNS.values() if col in df.columns]


def _selected_sites(args: argparse.Namespace) -> dict[str, dict]:
    return select_sites(SITES, site=getattr(args, "site", None), all_sites=getattr(args, "all_sites", True))


def cmd_clean(args: argparse.Namespace) -> None:
    input_path = Path(args.input)
    output_dir = Path(args.output)
    _ensure_dir(output_dir)

    for site, meta in _selected_sites(args).items():
        df = io.read_evapo_sheet(input_path, meta["sheet"], year=args.year)
        df = cleaning.clean_daily(df)
        io.write_cleaned(df, output_dir / f"{site}_daily.csv")


def cmd_validate_data(args: argparse.Namespace) -> None:
    input_path = Path(args.input)
    output_dir = Path(args.output)
    _ensure_dir(output_dir)

    reports = []
    for site, meta in _selected_sites(args).items():
        raw_df = io.read_evapo_sheet(input_path, meta["sheet"], year=args.year)
        cleaned_df, audit = cleaning.clean_daily_with_audit(raw_df)
        report = quality.build_quality_report(
            site=site,
            raw_df=raw_df,
            cleaned_df=cleaned_df,
            year=args.year,
            interpolated_by_variable=audit.interpolated_by_variable,
        )
        quality.write_quality_report(report, output_dir, site)
        reports.append(report)

    if reports:
        combined = pd.concat(reports, ignore_index=True)
        combined.to_csv(output_dir / "data_quality_summary.csv", index=False)


def cmd_aggregate(args: argparse.Namespace) -> None:
    input_dir = Path(args.input)
    output_dir = Path(args.output)
    _ensure_dir(output_dir)

    for site in _selected_sites(args).keys():
        df = pd.read_csv(input_dir / f"{site}_daily.csv", parse_dates=["date"])
        method_cols = _method_cols_present(df)

        rolling = aggregate.rolling_mean(df, window=7)
        rolling.to_csv(output_dir / f"{site}_rolling7d.csv", index=False)

        monthly = aggregate.monthly_sum(df, method_cols)
        monthly.to_csv(output_dir / f"{site}_monthly_totals.csv", index=False)


def cmd_metrics(args: argparse.Namespace) -> None:
    input_dir = Path(args.input)
    output_dir = Path(args.output)
    _ensure_dir(output_dir)

    for site in _selected_sites(args).keys():
        df = pd.read_csv(input_dir / f"{site}_daily.csv", parse_dates=["date"])
        method_cols = _method_cols_present(df)
        ref_col = REFERENCE_COLUMN

        if ref_col not in df.columns:
            raise ValueError(f"Reference column '{ref_col}' not found for {site}")

        daily_metrics = metrics.compute_metrics(df, ref_col, [c for c in method_cols if c != ref_col])
        daily_metrics.to_csv(output_dir / f"{site}_daily_metrics.csv", index=False)

        monthly_df = aggregate.monthly_sum(df, method_cols)
        monthly_metrics = metrics.compute_metrics(monthly_df, ref_col, [c for c in method_cols if c != ref_col])
        monthly_metrics.to_csv(output_dir / f"{site}_monthly_metrics.csv", index=False)


def cmd_plots(args: argparse.Namespace) -> None:
    input_dir = Path(args.input)
    figures_dir = Path(args.output)
    _ensure_dir(figures_dir)

    for site in _selected_sites(args).keys():
        df = pd.read_csv(input_dir / f"{site}_daily.csv", parse_dates=["date"])
        method_cols = _method_cols_present(df)
        ref_col = REFERENCE_COLUMN

        site_dir = figures_dir / site
        _ensure_dir(site_dir)

        for col in method_cols:
            if col == ref_col:
                continue
            method_id = METHOD_SHORT.get(col, col)
            ref_id = METHOD_SHORT.get(ref_col, "pm")
            plots.plot_scatter(df, ref_col, col, site_dir / f"{site}_daily_scatter_{method_id}_vs_{ref_id}.png")
            plots.plot_timeseries(df, ref_col, col, site_dir / f"{site}_daily_series_{method_id}_vs_{ref_id}.png")

        monthly_df = aggregate.monthly_sum(df, method_cols)
        plots.plot_monthly_totals(monthly_df, method_cols, site_dir / f"{site}_monthly_totals.png")
        plots.plot_taylor(
            df,
            ref_col,
            method_cols,
            site_dir / f"{site}_daily_taylor.png",
            title=f"Taylor diagram (daily) - {site}",
        )
        plots.plot_taylor(
            monthly_df,
            ref_col,
            method_cols,
            site_dir / f"{site}_monthly_taylor.png",
            title=f"Taylor diagram (monthly) - {site}",
        )


def cmd_all(args: argparse.Namespace) -> None:
    clean_args = argparse.Namespace(
        input=args.input,
        output=args.output,
        year=args.year,
        site=args.site,
        all_sites=args.all_sites,
    )
    cmd_clean(clean_args)

    aggregate_args = argparse.Namespace(
        input=str(DATA_CLEANED),
        output=str(OUTPUTS_RESULTS),
        year=args.year,
        site=args.site,
        all_sites=args.all_sites,
    )
    cmd_aggregate(aggregate_args)

    metrics_args = argparse.Namespace(
        input=str(DATA_CLEANED),
        output=str(OUTPUTS_TABLES),
        year=args.year,
        site=args.site,
        all_sites=args.all_sites,
    )
    cmd_metrics(metrics_args)

    plots_args = argparse.Namespace(
        input=str(DATA_CLEANED),
        output=str(OUTPUTS_FIGURES),
        year=args.year,
        site=args.site,
        all_sites=args.all_sites,
    )
    cmd_plots(plots_args)


def _add_site_selection(parser: argparse.ArgumentParser) -> None:
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--site",
        choices=sorted(SITES),
        action=SiteAction,
        help="Run only one configured site",
    )
    group.add_argument(
        "--all-sites",
        action="store_true",
        default=True,
        help="Run all configured sites (default)",
    )
    parser.set_defaults(all_sites=True)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="ETo pipeline CLI")
    parser.add_argument("--year", type=int, default=DEFAULT_YEAR)

    subparsers = parser.add_subparsers(dest="command", required=True)

    clean_parser = subparsers.add_parser("clean", help="Clean and standardize daily data")
    clean_parser.add_argument("--year", type=int, default=DEFAULT_YEAR)
    clean_parser.add_argument("--input", default=str(DATA_RAW / "Evapo.xlsx"))
    clean_parser.add_argument("--output", default=str(DATA_CLEANED))
    _add_site_selection(clean_parser)
    clean_parser.set_defaults(func=cmd_clean)

    aggregate_parser = subparsers.add_parser("aggregate", help="Create rolling and monthly aggregates")
    aggregate_parser.add_argument("--year", type=int, default=DEFAULT_YEAR)
    aggregate_parser.add_argument("--input", default=str(DATA_CLEANED))
    aggregate_parser.add_argument("--output", default=str(OUTPUTS_RESULTS))
    _add_site_selection(aggregate_parser)
    aggregate_parser.set_defaults(func=cmd_aggregate)

    validate_parser = subparsers.add_parser(
        "validate-data",
        help="Generate auditable data quality reports",
    )
    validate_parser.add_argument("--year", type=int, default=DEFAULT_YEAR)
    validate_parser.add_argument("--input", default=str(DATA_RAW / "Evapo.xlsx"))
    validate_parser.add_argument("--output", default=str(OUTPUTS_REPORTS))
    _add_site_selection(validate_parser)
    validate_parser.set_defaults(func=cmd_validate_data)

    metrics_parser = subparsers.add_parser("metrics", help="Compute metrics vs Penman-Monteith")
    metrics_parser.add_argument("--year", type=int, default=DEFAULT_YEAR)
    metrics_parser.add_argument("--input", default=str(DATA_CLEANED))
    metrics_parser.add_argument("--output", default=str(OUTPUTS_TABLES))
    _add_site_selection(metrics_parser)
    metrics_parser.set_defaults(func=cmd_metrics)

    plots_parser = subparsers.add_parser("plots", help="Generate figures")
    plots_parser.add_argument("--year", type=int, default=DEFAULT_YEAR)
    plots_parser.add_argument("--input", default=str(DATA_CLEANED))
    plots_parser.add_argument("--output", default=str(OUTPUTS_FIGURES))
    _add_site_selection(plots_parser)
    plots_parser.set_defaults(func=cmd_plots)

    all_parser = subparsers.add_parser("all", help="Run full pipeline")
    all_parser.add_argument("--year", type=int, default=DEFAULT_YEAR)
    all_parser.add_argument("--input", default=str(DATA_RAW / "Evapo.xlsx"))
    all_parser.add_argument("--output", default=str(DATA_CLEANED))
    _add_site_selection(all_parser)
    all_parser.set_defaults(func=cmd_all)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    args.func(args)


if __name__ == "__main__":
    main()
