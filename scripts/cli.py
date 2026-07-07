from __future__ import annotations

import argparse
import shutil
import warnings
from pathlib import Path

import pandas as pd

from . import (
    aggregate,
    calibration,
    cleaning,
    compute_eto,
    io,
    metrics,
    pca_analysis,
    plots,
    quality,
    sensitivity,
    summary,
    uncertainty,
)
from .config import (
    DATA_CLEANED,
    DATA_RAW,
    DEFAULT_YEAR,
    METHOD_COLUMNS,
    METHOD_SHORT,
    OUTPUTS_FIGURES,
    OUTPUTS_REPORTS,
    OUTPUTS_RESULTS,
    OUTPUTS_SUPPLEMENT,
    OUTPUTS_TABLES,
    REFERENCE_COLUMN,
    SITES,
    select_sites,
)
from .eto_io import read_eto_frame
from .logging_config import get_logger, setup_logging
from .naming import (
    bias_bins_filename,
    bootstrap_filename,
    cleaned_daily_filename,
    daily_eto_filename,
    figure_filename,
    metrics_filename,
    monthly_totals_filename,
    rolling_7d_filename,
    seasonal_filename,
    sensitivity_filename,
)

logger = get_logger("cli")


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


def _compute_eto_requested(args: argparse.Namespace) -> bool:
    return getattr(args, "eto_source", "precomputed") == "compute"


def _maybe_compute_eto_after_clean(args: argparse.Namespace) -> None:
    if not _compute_eto_requested(args):
        return
    compute_args = argparse.Namespace(
        input=str(Path(args.output)),
        output=str(OUTPUTS_RESULTS),
        year=getattr(args, "year", DEFAULT_YEAR),
        site=getattr(args, "site", None),
        all_sites=getattr(args, "all_sites", True),
        include_precomputed=getattr(args, "include_precomputed", False),
    )
    cmd_compute_eto(compute_args)


def _selected_sites(args: argparse.Namespace) -> dict[str, dict]:
    return select_sites(SITES, site=getattr(args, "site", None), all_sites=getattr(args, "all_sites", True))


def _pipeline_site_kwargs(args: argparse.Namespace) -> dict[str, int | str | bool | None]:
    return {
        "year": args.year,
        "site": args.site,
        "all_sites": args.all_sites,
    }


def _run_downstream_analysis(args: argparse.Namespace, *, cleaned_input: str | None = None) -> None:
    cleaned = cleaned_input or str(DATA_CLEANED)
    site_kwargs = _pipeline_site_kwargs(args)

    cmd_aggregate(
        argparse.Namespace(
            input=cleaned,
            output=str(OUTPUTS_RESULTS),
            **site_kwargs,
        )
    )
    cmd_metrics(
        argparse.Namespace(
            input=cleaned,
            output=str(OUTPUTS_TABLES),
            **site_kwargs,
        )
    )
    cmd_plots(
        argparse.Namespace(
            input=cleaned,
            output=str(OUTPUTS_FIGURES),
            **site_kwargs,
        )
    )
    cmd_analyze_uncertainty(
        argparse.Namespace(
            input=cleaned,
            tables_output=str(OUTPUTS_TABLES),
            reports_output=str(OUTPUTS_REPORTS),
            figures_output=str(OUTPUTS_FIGURES),
            bootstrap_samples=1000,
            confidence=0.95,
            random_state=args.year,
            rainfall_column="rain_mm",
            eto_bins=4,
            **site_kwargs,
        )
    )


def _run_compute_eto(
    args: argparse.Namespace,
    *,
    include_precomputed: bool = False,
    input_dir: str | None = None,
    output_dir: str | None = None,
) -> None:
    compute_args = argparse.Namespace(
        input=input_dir or str(DATA_CLEANED),
        output=output_dir or str(OUTPUTS_RESULTS),
        include_precomputed=include_precomputed,
        **_pipeline_site_kwargs(args),
    )
    cmd_compute_eto(compute_args)


def cmd_clean(args: argparse.Namespace) -> None:
    input_path = Path(args.input)
    output_dir = Path(args.output)
    _ensure_dir(output_dir)

    for site, meta in _selected_sites(args).items():
        df = io.read_evapo_sheet(input_path, meta["sheet"], year=args.year)
        df = cleaning.clean_daily(df)
        output_path = output_dir / cleaned_daily_filename(site)
        io.write_cleaned(df, output_path)
        logger.info("wrote cleaned daily data for %s to %s", site, output_path)

    _maybe_compute_eto_after_clean(args)


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
        summary_path = output_dir / "data_quality_summary.csv"
        combined.to_csv(summary_path, index=False)
        logger.info("wrote data quality summary to %s (%d site report(s))", summary_path, len(reports))


def cmd_aggregate(args: argparse.Namespace) -> None:
    input_dir = Path(args.input)
    output_dir = Path(args.output)
    _ensure_dir(output_dir)

    for site in _selected_sites(args).keys():
        df = read_eto_frame(site, cleaned_dir=input_dir)
        method_cols = _method_cols_present(df)

        rolling = aggregate.rolling_mean(df, window=7)
        rolling.to_csv(output_dir / rolling_7d_filename(site), index=False)

        monthly = aggregate.monthly_sum(df, method_cols)
        monthly.to_csv(output_dir / monthly_totals_filename(site), index=False)
        logger.info("wrote rolling and monthly aggregates for %s", site)


def cmd_metrics(args: argparse.Namespace) -> None:
    input_dir = Path(args.input)
    output_dir = Path(args.output)
    _ensure_dir(output_dir)

    for site in _selected_sites(args).keys():
        df = read_eto_frame(site, cleaned_dir=input_dir)
        method_cols = _method_cols_present(df)
        ref_col = REFERENCE_COLUMN

        if ref_col not in df.columns:
            raise ValueError(f"Reference column '{ref_col}' not found for {site}")

        daily_metrics = metrics.compute_metrics(df, ref_col, [c for c in method_cols if c != ref_col])
        daily_metrics.to_csv(output_dir / metrics_filename(site, "daily"), index=False)

        monthly_df = aggregate.monthly_sum(df, method_cols)
        monthly_metrics = metrics.compute_metrics(monthly_df, ref_col, [c for c in method_cols if c != ref_col])
        monthly_metrics.to_csv(output_dir / metrics_filename(site, "monthly"), index=False)
        logger.info("wrote daily and monthly metrics for %s (%d methods)", site, len(method_cols) - 1)


def _calibration_results_dir(input_dir: Path, results_input: str | None) -> Path | None:
    if results_input is not None:
        return Path(results_input)
    if input_dir.resolve() == DATA_CLEANED.resolve():
        return OUTPUTS_RESULTS
    return None


def _read_calibration_input(
    input_dir: Path,
    site: str,
    *,
    results_input: str | None = None,
) -> pd.DataFrame:
    cleaned = pd.read_csv(input_dir / cleaned_daily_filename(site), parse_dates=["date"])
    results_dir = _calibration_results_dir(input_dir, results_input)
    if results_dir is None:
        return cleaned

    computed_path = results_dir / daily_eto_filename(site)
    if not computed_path.exists():
        if results_input is not None:
            raise ValueError(f"Computed results file '{computed_path}' not found for {site}")
        return cleaned

    computed = pd.read_csv(computed_path, parse_dates=["date"])
    if REFERENCE_COLUMN not in computed.columns:
        raise ValueError(f"Reference column '{REFERENCE_COLUMN}' not found for {site}")

    reference = computed[["date", REFERENCE_COLUMN]].rename(
        columns={REFERENCE_COLUMN: f"computed_{REFERENCE_COLUMN}"}
    )
    reference["computed_reference_row_present"] = True
    merged = cleaned.drop(columns=[REFERENCE_COLUMN], errors="ignore").merge(
        reference,
        on="date",
        how="left",
        validate="one_to_one",
    )
    if merged["computed_reference_row_present"].isna().any():
        raise ValueError(f"Computed reference series does not cover all cleaned dates for {site}")
    merged = merged.drop(columns=["computed_reference_row_present"])
    merged[REFERENCE_COLUMN] = merged.pop(f"computed_{REFERENCE_COLUMN}")
    return merged


def cmd_compute_eto(args: argparse.Namespace) -> None:
    input_dir = Path(args.input)
    output_dir = Path(args.output)
    _ensure_dir(output_dir)

    for site, meta in _selected_sites(args).items():
        df = pd.read_csv(input_dir / cleaned_daily_filename(site), parse_dates=["date"])
        result = compute_eto.compute_daily_eto(
            df,
            site_meta=meta,
            include_precomputed=args.include_precomputed,
        )
        output_path = output_dir / daily_eto_filename(site)
        result.frame.to_csv(output_path, index=False)
        result.report.log_summary(site=site)
        logger.info("wrote computed daily ETo for %s to %s", site, output_path)


def cmd_calibrate(args: argparse.Namespace) -> None:
    input_dir = Path(args.input)
    output_dir = Path(args.output)
    _ensure_dir(output_dir)

    for site in _selected_sites(args).keys():
        df = _read_calibration_input(
            input_dir,
            site,
            results_input=getattr(args, "results_input", None),
        )
        result = calibration.calibrate_method(
            df,
            method=args.method,
            train_start=args.train_start,
            train_end=args.train_end,
            test_start=args.test_start,
            test_end=args.test_end,
        )
        calibration.write_calibration_outputs(
            result,
            output_dir=output_dir,
            site=site,
            method=args.method,
        )
        logger.info("wrote calibration outputs for %s (%s)", site, args.method)


def cmd_plots(args: argparse.Namespace) -> None:
    input_dir = Path(args.input)
    figures_dir = Path(args.output)
    _ensure_dir(figures_dir)

    for site in _selected_sites(args).keys():
        df = read_eto_frame(site, cleaned_dir=input_dir)
        method_cols = _method_cols_present(df)
        ref_col = REFERENCE_COLUMN

        site_dir = figures_dir / site
        _ensure_dir(site_dir)

        for col in method_cols:
            if col == ref_col:
                continue
            method_id = METHOD_SHORT.get(col, col)
            ref_id = METHOD_SHORT.get(ref_col, "pm")
            plots.plot_scatter(
                df,
                ref_col,
                col,
                site_dir / figure_filename(site, f"daily_scatter_{method_id}_vs_{ref_id}"),
            )
            plots.plot_timeseries(
                df,
                ref_col,
                col,
                site_dir / figure_filename(site, f"daily_series_{method_id}_vs_{ref_id}"),
            )

        monthly_df = aggregate.monthly_sum(df, method_cols)
        plots.plot_monthly_totals(monthly_df, method_cols, site_dir / figure_filename(site, "monthly_totals"))
        plots.plot_taylor(
            df,
            ref_col,
            method_cols,
            site_dir / figure_filename(site, "daily_taylor"),
            title=f"Taylor diagram (daily) - {site}",
        )
        plots.plot_taylor(
            monthly_df,
            ref_col,
            method_cols,
            site_dir / figure_filename(site, "monthly_taylor"),
            title=f"Taylor diagram (monthly) - {site}",
        )
        logger.info("wrote figures for %s (%d alternative methods)", site, len(method_cols) - 1)


def _site_group_label(meta: dict) -> str | None:
    for key in ("group", "biome", "bioma"):
        value = meta.get(key)
        if value:
            return str(value)
    return None


def _run_pca_for_frame(
    df: pd.DataFrame,
    label: str,
    tables_dir: Path,
    figures_dir: Path,
) -> None:
    result = pca_analysis.run_pca(df, label)
    pca_analysis.write_pca_outputs(result, tables_dir, figures_dir)


def cmd_pca(args: argparse.Namespace) -> None:
    input_dir = Path(args.input)
    tables_dir = Path(args.tables)
    figures_dir = Path(args.figures)
    _ensure_dir(tables_dir)
    _ensure_dir(figures_dir)

    selected_sites = _selected_sites(args)
    successful_labels: list[str] = []
    skipped: list[str] = []
    grouped_frames: dict[str, list[pd.DataFrame]] = {}

    for site, meta in selected_sites.items():
        site_path = input_dir / cleaned_daily_filename(site)
        df = pd.read_csv(site_path, parse_dates=["date"])
        group_label = _site_group_label(meta)
        if group_label:
            group_df = df.copy()
            group_df["site"] = site
            grouped_frames.setdefault(group_label, []).append(group_df)
        try:
            _run_pca_for_frame(df, site, tables_dir, figures_dir)
            successful_labels.append(site)
        except ValueError as exc:
            message = f"Skipping PCA for {site}: {exc}"
            if getattr(args, "all_sites", True):
                warnings.warn(message, stacklevel=2)
                skipped.append(site)
                continue
            raise ValueError(message) from exc

    for group_label, frames in grouped_frames.items():
        if len(frames) < 2:
            continue
        combined = pd.concat(frames, ignore_index=True)
        try:
            _run_pca_for_frame(combined, group_label, tables_dir, figures_dir)
            successful_labels.append(group_label)
        except ValueError as exc:
            warnings.warn(f"Skipping PCA for {group_label}: {exc}", stacklevel=2)
            skipped.append(group_label)

    if not successful_labels:
        if skipped:
            raise ValueError(
                "PCA could not be completed for any selected site. "
                "Check that at least two candidate meteorological variables are available."
            )
        raise ValueError("PCA could not be completed for the selected input.")
    logger.info("completed PCA for %s", ", ".join(successful_labels))


def cmd_analyze_uncertainty(args: argparse.Namespace) -> None:
    input_dir = Path(args.input)
    tables_dir = Path(args.tables_output)
    reports_dir = Path(args.reports_output)
    figures_dir = Path(args.figures_output)
    _ensure_dir(tables_dir)
    _ensure_dir(reports_dir)
    _ensure_dir(figures_dir)

    for site in _selected_sites(args).keys():
        df = read_eto_frame(site, cleaned_dir=input_dir, merge_cleaned_auxiliary=True)
        method_cols = [col for col in _method_cols_present(df) if col != REFERENCE_COLUMN]
        if REFERENCE_COLUMN not in df.columns:
            raise ValueError(f"Reference column '{REFERENCE_COLUMN}' not found for {site}")

        bootstrap = uncertainty.bootstrap_metric_intervals(
            df,
            REFERENCE_COLUMN,
            method_cols,
            n_boot=args.bootstrap_samples,
            confidence=args.confidence,
            random_state=args.random_state,
        )
        seasonal = uncertainty.seasonal_error_metrics(
            df,
            REFERENCE_COLUMN,
            method_cols,
            rainfall_col=args.rainfall_column,
        )
        bias_bins = uncertainty.bias_by_eto_bin(
            df,
            REFERENCE_COLUMN,
            method_cols,
            n_bins=args.eto_bins,
        )

        bootstrap.to_csv(tables_dir / bootstrap_filename(site), index=False)
        seasonal.to_csv(tables_dir / seasonal_filename(site), index=False)
        bias_bins.to_csv(tables_dir / bias_bins_filename(site), index=False)
        uncertainty.write_uncertainty_report(site, bootstrap, seasonal, bias_bins, reports_dir)

        site_dir = figures_dir / site
        plots.plot_bias_by_eto_bin(
            bias_bins,
            site_dir / figure_filename(site, "bias_by_eto_bin"),
            title=f"Bias by Penman-Monteith ETo range - {site}",
        )
        logger.info("wrote uncertainty analysis outputs for %s", site)


def cmd_sensitivity(args: argparse.Namespace) -> None:
    input_dir = Path(args.input)
    tables_dir = Path(args.tables_output)
    figures_dir = Path(args.figures_output)
    _ensure_dir(tables_dir)
    _ensure_dir(figures_dir)

    for site, meta in _selected_sites(args).items():
        df = pd.read_csv(input_dir / cleaned_daily_filename(site), parse_dates=["date"])
        result = sensitivity.run_oat_sensitivity(df, site_meta=meta, method=args.method)
        sensitivity.write_sensitivity_outputs(
            result,
            table_path=tables_dir / sensitivity_filename(site, args.method),
            figure_path=figures_dir / site / figure_filename(site, f"sensitivity_{args.method}"),
            title=f"OAT sensitivity - {site} - {args.method}",
        )
        logger.info("wrote sensitivity outputs for %s (%s)", site, args.method)


def cmd_all(args: argparse.Namespace) -> None:
    clean_args = argparse.Namespace(
        input=args.input,
        output=args.output,
        year=args.year,
        site=args.site,
        all_sites=args.all_sites,
        eto_source=getattr(args, "eto_source", "precomputed"),
    )
    cmd_clean(clean_args)

    _run_downstream_analysis(args)
    logger.info("completed pipeline for year %s", args.year)


def cmd_summarize(args: argparse.Namespace) -> None:
    sites = list(_selected_sites(args).keys())
    tables_dir = Path(args.input)
    reports_dir = Path(args.output)
    selected_sites = _selected_sites(args)
    ranking = getattr(args, "ranking", summary.DEFAULT_RANKING)
    summary_df = summary.build_summary(tables_dir, sites=sites, site_metadata=selected_sites, ranking=ranking)
    summary.write_summary(summary_df, reports_dir)
    rankings_df = summary.build_rankings(tables_dir, sites=sites, site_metadata=selected_sites, ranking=ranking)
    summary.write_rankings(rankings_df, tables_dir, reports_dir)
    logger.info("wrote summary and rankings to %s", reports_dir)


def cmd_reproduce_paper(args: argparse.Namespace) -> None:
    cmd_all(args)
    _run_compute_eto(args, include_precomputed=True)
    _run_downstream_analysis(args)
    validate_args = argparse.Namespace(
        input=args.input,
        output=str(OUTPUTS_REPORTS),
        year=args.year,
        site=args.site,
        all_sites=args.all_sites,
    )
    cmd_validate_data(validate_args)
    summarize_args = argparse.Namespace(
        input=str(OUTPUTS_TABLES),
        output=str(OUTPUTS_REPORTS),
        site=args.site,
        all_sites=args.all_sites,
        ranking=summary.DEFAULT_RANKING,
    )
    cmd_summarize(summarize_args)
    logger.info("completed paper reproduction for year %s", args.year)


def cmd_export_supplement(args: argparse.Namespace) -> None:
    output_dir = Path(args.output)
    _ensure_dir(output_dir)

    sources = [
        OUTPUTS_TABLES,
        OUTPUTS_RESULTS,
        OUTPUTS_REPORTS,
    ]
    copied: list[str] = []
    for source_dir in sources:
        if not source_dir.exists():
            continue
        destination_dir = output_dir / source_dir.name
        _ensure_dir(destination_dir)
        for source_path in sorted(source_dir.glob("*.csv")):
            destination_path = destination_dir / source_path.name
            shutil.copy2(source_path, destination_path)
            copied.append(str(destination_path.relative_to(output_dir)))

    manifest = output_dir / "MANIFEST.md"
    lines = [
        "# Supplement export",
        "",
        "This directory contains CSV tables, intermediate results, and data-quality reports",
        "generated by the current CLI pipeline. Legacy outputs are intentionally excluded.",
        "",
        "## Files",
        "",
    ]
    lines.extend(f"- `{path}`" for path in copied)
    manifest.write_text("\n".join(lines) + "\n", encoding="utf-8")
    logger.info("exported %d supplement file(s) to %s", len(copied), output_dir)


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


def _add_eto_source_selection(parser: argparse.ArgumentParser) -> None:
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--use-precomputed-eto",
        dest="eto_source",
        action="store_const",
        const="precomputed",
        default="precomputed",
        help="Use ETo columns already present in the input spreadsheet (default, legacy-compatible)",
    )
    group.add_argument(
        "--compute-eto",
        dest="eto_source",
        action="store_const",
        const="compute",
        help=(
            "After cleaning, compute ET0 from standardized meteorological variables "
            "and write outputs/results/{site}_daily_eto.csv"
        ),
    )


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="ETo pipeline CLI")
    parser.add_argument("--year", type=int, default=DEFAULT_YEAR)
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Enable debug logging",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    clean_parser = subparsers.add_parser("clean", help="Clean and standardize daily data")
    clean_parser.add_argument("--year", type=int, default=DEFAULT_YEAR)
    clean_parser.add_argument("--input", default=str(DATA_RAW / "Evapo.xlsx"))
    clean_parser.add_argument("--output", default=str(DATA_CLEANED))
    _add_eto_source_selection(clean_parser)
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
    _add_eto_source_selection(validate_parser)
    _add_site_selection(validate_parser)
    validate_parser.set_defaults(func=cmd_validate_data)

    metrics_parser = subparsers.add_parser("metrics", help="Compute metrics vs Penman-Monteith")
    metrics_parser.add_argument("--year", type=int, default=DEFAULT_YEAR)
    metrics_parser.add_argument("--input", default=str(DATA_CLEANED))
    metrics_parser.add_argument("--output", default=str(OUTPUTS_TABLES))
    _add_site_selection(metrics_parser)
    metrics_parser.set_defaults(func=cmd_metrics)

    compute_parser = subparsers.add_parser(
        "compute-eto",
        help="Compute ET0 methods from standardized cleaned meteorological variables",
    )
    compute_parser.add_argument("--year", type=int, default=DEFAULT_YEAR)
    compute_parser.add_argument("--input", default=str(DATA_CLEANED))
    compute_parser.add_argument("--output", default=str(OUTPUTS_RESULTS))
    compute_parser.add_argument(
        "--include-precomputed",
        action="store_true",
        help="Keep precomputed et_* columns as precomputed_<column> for validation",
    )
    _add_site_selection(compute_parser)
    compute_parser.set_defaults(func=cmd_compute_eto)

    calibrate_parser = subparsers.add_parser(
        "calibrate",
        help="Calibrate selected ET0 method coefficients with a temporal train/test split",
    )
    calibrate_parser.add_argument("--year", type=int, default=DEFAULT_YEAR)
    calibrate_parser.add_argument("--input", default=str(DATA_CLEANED))
    calibrate_parser.add_argument(
        "--results-input",
        default=None,
        help=(
            "Directory containing computed daily ET0 results to use for the reference "
            "series. Defaults to outputs/results only when --input is the default "
            "data/cleaned directory."
        ),
    )
    calibrate_parser.add_argument("--output", default=str(OUTPUTS_TABLES))
    calibrate_parser.add_argument(
        "--method",
        choices=sorted(calibration.CALIBRATABLE_METHODS),
        required=True,
        help="ET0 method to calibrate",
    )
    calibrate_parser.add_argument("--train-start", default=None)
    calibrate_parser.add_argument("--train-end", default=None)
    calibrate_parser.add_argument("--test-start", default=None)
    calibrate_parser.add_argument("--test-end", default=None)
    _add_site_selection(calibrate_parser)
    calibrate_parser.set_defaults(func=cmd_calibrate)

    plots_parser = subparsers.add_parser("plots", help="Generate figures")
    plots_parser.add_argument("--year", type=int, default=DEFAULT_YEAR)
    plots_parser.add_argument("--input", default=str(DATA_CLEANED))
    plots_parser.add_argument("--output", default=str(OUTPUTS_FIGURES))
    _add_site_selection(plots_parser)
    plots_parser.set_defaults(func=cmd_plots)

    pca_parser = subparsers.add_parser(
        "pca",
        help="Run an optional PCA on meteorological drivers",
    )
    pca_parser.add_argument("--input", default=str(DATA_CLEANED))
    pca_parser.add_argument("--tables", default=str(OUTPUTS_TABLES))
    pca_parser.add_argument("--figures", default=str(OUTPUTS_FIGURES))
    _add_site_selection(pca_parser)
    pca_parser.set_defaults(func=cmd_pca)

    uncertainty_parser = subparsers.add_parser(
        "analyze-uncertainty",
        help="Generate bootstrap intervals, seasonal errors, and ETo-range bias analyses",
    )
    uncertainty_parser.add_argument("--year", type=int, default=DEFAULT_YEAR)
    uncertainty_parser.add_argument("--input", default=str(DATA_CLEANED))
    uncertainty_parser.add_argument("--tables-output", default=str(OUTPUTS_TABLES))
    uncertainty_parser.add_argument("--reports-output", default=str(OUTPUTS_REPORTS))
    uncertainty_parser.add_argument("--figures-output", default=str(OUTPUTS_FIGURES))
    uncertainty_parser.add_argument("--bootstrap-samples", type=int, default=1000)
    uncertainty_parser.add_argument("--confidence", type=float, default=0.95)
    uncertainty_parser.add_argument("--random-state", type=int, default=DEFAULT_YEAR)
    uncertainty_parser.add_argument("--rainfall-column", default="rain_mm")
    uncertainty_parser.add_argument("--eto-bins", type=int, default=4)
    _add_site_selection(uncertainty_parser)
    uncertainty_parser.set_defaults(func=cmd_analyze_uncertainty)

    sensitivity_parser = subparsers.add_parser(
        "sensitivity",
        help="Run optional one-at-a-time meteorological sensitivity analysis",
    )
    sensitivity_parser.add_argument("--year", type=int, default=DEFAULT_YEAR)
    sensitivity_parser.add_argument("--input", default=str(DATA_CLEANED))
    sensitivity_parser.add_argument("--tables-output", default=str(OUTPUTS_TABLES))
    sensitivity_parser.add_argument("--figures-output", default=str(OUTPUTS_FIGURES))
    sensitivity_parser.add_argument(
        "--method",
        choices=sorted(sensitivity.METHOD_OUTPUT_COLUMNS),
        default="penman_monteith",
        help="ET0 method to recompute under each perturbation",
    )
    _add_site_selection(sensitivity_parser)
    sensitivity_parser.set_defaults(func=cmd_sensitivity)

    summarize_parser = subparsers.add_parser(
        "summarize",
        help="Summarize best-performing methods and rankings from generated metrics tables",
    )
    summarize_parser.add_argument("--input", default=str(OUTPUTS_TABLES))
    summarize_parser.add_argument("--output", default=str(OUTPUTS_REPORTS))
    summarize_parser.add_argument(
        "--ranking",
        choices=summary.RANKING_RULES,
        default=summary.DEFAULT_RANKING,
        help=(
            "Ranking rule for selecting best methods: rmse, mae, c, willmott_d, "
            "or composite (default: composite)"
        ),
    )
    _add_site_selection(summarize_parser)
    summarize_parser.set_defaults(func=cmd_summarize)

    all_parser = subparsers.add_parser(
        "all",
        help="Run full pipeline (clean, aggregate, metrics, plots, uncertainty; use --compute-eto to calculate ET0)",
    )
    all_parser.add_argument("--year", type=int, default=DEFAULT_YEAR)
    all_parser.add_argument("--input", default=str(DATA_RAW / "Evapo.xlsx"))
    all_parser.add_argument("--output", default=str(DATA_CLEANED))
    _add_eto_source_selection(all_parser)
    _add_site_selection(all_parser)
    all_parser.set_defaults(func=cmd_all)

    reproduce_parser = subparsers.add_parser(
        "reproduce-paper",
        help="Regenerate paper tables, figures, data-quality reports, and summary",
    )
    reproduce_parser.add_argument("--year", type=int, default=DEFAULT_YEAR)
    reproduce_parser.add_argument("--input", default=str(DATA_RAW / "Evapo.xlsx"))
    reproduce_parser.add_argument("--output", default=str(DATA_CLEANED))
    _add_eto_source_selection(reproduce_parser)
    _add_site_selection(reproduce_parser)
    reproduce_parser.set_defaults(func=cmd_reproduce_paper)

    supplement_parser = subparsers.add_parser(
        "export-supplement",
        help="Copy current CSV outputs into a supplemental export directory",
    )
    supplement_parser.add_argument("--output", default=str(OUTPUTS_SUPPLEMENT))
    supplement_parser.set_defaults(func=cmd_export_supplement)

    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()
    setup_logging(verbose=getattr(args, "verbose", False))

    args.func(args)


if __name__ == "__main__":
    main()
