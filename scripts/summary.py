from __future__ import annotations

from pathlib import Path

import pandas as pd

METRIC_COLUMNS = ["rmse", "mae", "mbe", "r2", "willmott_d"]
RANK_COLUMNS = [
    "rank_rmse",
    "rank_mae",
    "rank_mbe",
    "rank_r2",
    "rank_willmott_d",
]
RANKING_COLUMNS = ["site", "scale", "rank", "method", *METRIC_COLUMNS, *RANK_COLUMNS]


def _rank_series(series: pd.Series, *, ascending: bool) -> pd.Series:
    return series.rank(method="min", ascending=ascending, na_option="bottom").astype("Int64")


def _rank_metrics(table: pd.DataFrame) -> pd.DataFrame:
    ranked = table.copy()
    ranked["rank_rmse"] = _rank_series(ranked["rmse"], ascending=True)
    ranked["rank_mae"] = _rank_series(ranked["mae"], ascending=True)
    ranked["rank_mbe"] = _rank_series(ranked["mbe"].abs(), ascending=True)
    ranked["rank_r2"] = _rank_series(ranked["r2"], ascending=False)
    ranked["rank_willmott_d"] = _rank_series(ranked["willmott_d"], ascending=False)
    ranked = ranked.sort_values("rmse", ascending=True).reset_index(drop=True)
    ranked["rank"] = pd.Series(range(1, len(ranked) + 1), dtype="Int64")
    return ranked


def build_rankings(tables_dir: Path, sites: list[str]) -> pd.DataFrame:
    rows = []
    for site in sites:
        for scale in ["daily", "monthly"]:
            metrics_path = tables_dir / f"{site}_{scale}_metrics.csv"
            if not metrics_path.exists():
                continue
            table = pd.read_csv(metrics_path)
            if table.empty or "rmse" not in table.columns:
                continue
            ranked = _rank_metrics(table)
            for _, row in ranked.iterrows():
                rows.append(
                    {
                        "site": site,
                        "scale": scale,
                        "rank": row["rank"],
                        "method": row["method"],
                        **{column: row[column] for column in METRIC_COLUMNS if column in row},
                        **{column: row[column] for column in RANK_COLUMNS},
                    }
                )
    return pd.DataFrame(rows, columns=RANKING_COLUMNS)


def build_summary(tables_dir: Path, sites: list[str]) -> pd.DataFrame:
    rows = []
    for site in sites:
        for scale in ["daily", "monthly"]:
            metrics_path = tables_dir / f"{site}_{scale}_metrics.csv"
            if not metrics_path.exists():
                continue
            table = pd.read_csv(metrics_path)
            if table.empty or "rmse" not in table.columns:
                continue
            best = table.sort_values("rmse", ascending=True).iloc[0]
            row = {
                "site": site,
                "scale": scale,
                "best_method": best["method"],
            }
            for column in METRIC_COLUMNS:
                if column in table.columns:
                    row[column] = best[column]
            rows.append(row)
    return pd.DataFrame(rows)


def write_summary(summary: pd.DataFrame, output_dir: Path) -> tuple[Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    csv_path = output_dir / "summary.csv"
    markdown_path = output_dir / "summary.md"
    summary.to_csv(csv_path, index=False)

    lines = [
        "# Results summary",
        "",
        "Best methods are selected by lowest RMSE for each site and temporal scale.",
        "",
    ]
    if summary.empty:
        lines.append("No metrics tables were available.")
    else:
        columns = list(summary.columns)
        lines.append("| " + " | ".join(columns) + " |")
        lines.append("| " + " | ".join(["---"] * len(columns)) + " |")
        for row in summary.itertuples(index=False, name=None):
            lines.append("| " + " | ".join(str(value) for value in row) + " |")
    markdown_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return csv_path, markdown_path


def _format_metric(value: object, digits: int = 4) -> str:
    if pd.isna(value):
        return ""
    if isinstance(value, float):
        return f"{value:.{digits}f}"
    return str(value)


def write_rankings(
    rankings: pd.DataFrame,
    tables_dir: Path,
    reports_dir: Path,
) -> tuple[Path, Path]:
    tables_dir.mkdir(parents=True, exist_ok=True)
    reports_dir.mkdir(parents=True, exist_ok=True)

    csv_path = tables_dir / "summary_rankings.csv"
    markdown_path = reports_dir / "summary_rankings.md"
    rankings.to_csv(csv_path, index=False)

    lines = [
        "# Method rankings",
        "",
        "Methods are ranked within each site and temporal scale.",
        "Overall `rank` follows lowest RMSE; per-metric ranks use the same criterion",
        "(MBE ranks by absolute bias; R² and Willmott d favor higher values).",
        "",
    ]
    if rankings.empty:
        lines.append("No metrics tables were available.")
    else:
        for (site, scale), group in rankings.groupby(["site", "scale"], sort=False):
            lines.extend(
                [
                    f"## {site.title()} — {scale}",
                    "",
                    f"Best overall: **{group.iloc[0]['method']}** (RMSE = {_format_metric(group.iloc[0]['rmse'])}).",
                    "",
                ]
            )
            columns = [column for column in RANKING_COLUMNS if column in group.columns]
            lines.append("| " + " | ".join(columns) + " |")
            lines.append("| " + " | ".join(["---"] * len(columns)) + " |")
            for row in group[columns].itertuples(index=False, name=None):
                formatted = [
                    _format_metric(value) if isinstance(value, float) else str(value)
                    for value in row
                ]
                lines.append("| " + " | ".join(formatted) + " |")
            lines.append("")

    markdown_path.write_text("\n".join(lines).rstrip() + "\n", encoding="utf-8")
    return csv_path, markdown_path
