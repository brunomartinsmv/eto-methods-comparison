from __future__ import annotations

from pathlib import Path

import pandas as pd

METRIC_COLUMNS = ["rmse", "mae", "mbe", "r", "r2", "willmott_d", "c", "classification"]
SITE_METADATA_COLUMNS = ["biome", "climate_class", "region", "country", "state"]
RANKING_RULES = ("rmse", "mae", "c", "willmott_d", "composite")
DEFAULT_RANKING = "composite"
SELECTION_RULE_DESCRIPTIONS = {
    "rmse": "lowest RMSE",
    "mae": "lowest MAE",
    "c": "highest confidence coefficient c",
    "willmott_d": "highest Willmott d",
    "composite": "highest c, then lowest RMSE, lowest MAE, highest Willmott d, and lowest absolute MBE",
}
RANK_COLUMNS = [
    "rank_rmse",
    "rank_mae",
    "rank_mbe",
    "rank_r",
    "rank_r2",
    "rank_willmott_d",
    "rank_c",
]
RANKING_COLUMNS = [
    "site",
    *SITE_METADATA_COLUMNS,
    "scale",
    "rank",
    "selection_rule",
    "method",
    *METRIC_COLUMNS,
    *RANK_COLUMNS,
]


def _rank_series(series: pd.Series, *, ascending: bool) -> pd.Series:
    return series.rank(method="min", ascending=ascending, na_option="bottom").astype("Int64")


def _rank_metrics(table: pd.DataFrame) -> pd.DataFrame:
    ranked = table.copy()
    ranked["rank_rmse"] = _rank_series(ranked["rmse"], ascending=True)
    ranked["rank_mae"] = _rank_series(ranked["mae"], ascending=True)
    ranked["rank_mbe"] = _rank_series(ranked["mbe"].abs(), ascending=True)
    if "r" in ranked.columns:
        ranked["rank_r"] = _rank_series(ranked["r"], ascending=False)
    if "r2" in ranked.columns:
        ranked["rank_r2"] = _rank_series(ranked["r2"], ascending=False)
    if "willmott_d" in ranked.columns:
        ranked["rank_willmott_d"] = _rank_series(ranked["willmott_d"], ascending=False)
    if "c" in ranked.columns:
        ranked["rank_c"] = _rank_series(ranked["c"], ascending=False)
    return ranked


def _validate_ranking(ranking: str) -> None:
    if ranking not in RANKING_RULES:
        valid = ", ".join(RANKING_RULES)
        raise ValueError(f"Unknown ranking rule '{ranking}'. Valid rules: {valid}.")


def _required_columns_for_ranking(ranking: str) -> list[str]:
    if ranking == "composite":
        return ["c", "rmse", "mae", "willmott_d", "mbe"]
    if ranking in {"rmse", "mae", "c", "willmott_d"}:
        return [ranking]
    _validate_ranking(ranking)
    return []


def _sort_ranked_table(ranked: pd.DataFrame, *, ranking: str) -> pd.DataFrame:
    _validate_ranking(ranking)
    missing = [column for column in _required_columns_for_ranking(ranking) if column not in ranked.columns]
    if missing:
        missing_text = ", ".join(missing)
        raise ValueError(f"Ranking rule '{ranking}' requires missing metric columns: {missing_text}.")

    ranked = ranked.copy()
    if ranking == "composite":
        ranked["_abs_mbe"] = ranked["mbe"].abs()
        sorted_table = ranked.sort_values(
            ["c", "rmse", "mae", "willmott_d", "_abs_mbe", "method"],
            ascending=[False, True, True, False, True, True],
            na_position="last",
        ).drop(columns=["_abs_mbe"])
    elif ranking in {"rmse", "mae"}:
        sorted_table = ranked.sort_values([ranking, "method"], ascending=[True, True], na_position="last")
    else:
        sorted_table = ranked.sort_values([ranking, "method"], ascending=[False, True], na_position="last")

    sorted_table = sorted_table.reset_index(drop=True)
    sorted_table["rank"] = pd.Series(range(1, len(sorted_table) + 1), dtype="Int64")
    sorted_table["selection_rule"] = ranking
    return sorted_table


def _site_metadata_row(site: str, site_metadata: dict[str, dict] | None) -> dict[str, object]:
    if not site_metadata:
        return {}
    metadata = site_metadata.get(site, {})
    return {
        column: metadata.get(column, "")
        for column in SITE_METADATA_COLUMNS
        if any(column in values for values in site_metadata.values())
    }


def _ordered_columns(df: pd.DataFrame, preferred: list[str]) -> list[str]:
    return [column for column in preferred if column in df.columns]


def build_rankings(
    tables_dir: Path,
    sites: list[str],
    site_metadata: dict[str, dict] | None = None,
    ranking: str = DEFAULT_RANKING,
) -> pd.DataFrame:
    _validate_ranking(ranking)
    rows = []
    for site in sites:
        for scale in ["daily", "monthly"]:
            metrics_path = tables_dir / f"{site}_{scale}_metrics.csv"
            if not metrics_path.exists():
                continue
            table = pd.read_csv(metrics_path)
            if table.empty:
                continue
            ranked = _sort_ranked_table(_rank_metrics(table), ranking=ranking)
            for _, row in ranked.iterrows():
                rows.append(
                    {
                        "site": site,
                        **_site_metadata_row(site, site_metadata),
                        "scale": scale,
                        "rank": row["rank"],
                        "selection_rule": row["selection_rule"],
                        "method": row["method"],
                        **{column: row[column] for column in METRIC_COLUMNS if column in row},
                        **{column: row[column] for column in RANK_COLUMNS if column in row},
                    }
                )
    df = pd.DataFrame(rows)
    return df[_ordered_columns(df, RANKING_COLUMNS)] if not df.empty else pd.DataFrame(columns=["site", "scale"])


def build_summary(
    tables_dir: Path,
    sites: list[str],
    site_metadata: dict[str, dict] | None = None,
    ranking: str = DEFAULT_RANKING,
) -> pd.DataFrame:
    _validate_ranking(ranking)
    rows = []
    for site in sites:
        for scale in ["daily", "monthly"]:
            metrics_path = tables_dir / f"{site}_{scale}_metrics.csv"
            if not metrics_path.exists():
                continue
            table = pd.read_csv(metrics_path)
            if table.empty:
                continue
            best = _sort_ranked_table(_rank_metrics(table), ranking=ranking).iloc[0]
            row = {
                "site": site,
                **_site_metadata_row(site, site_metadata),
                "scale": scale,
                "rank": best["rank"],
                "selection_rule": best["selection_rule"],
                "best_method": best["method"],
            }
            for column in METRIC_COLUMNS:
                if column in table.columns:
                    row[column] = best[column]
            rows.append(row)
    df = pd.DataFrame(rows)
    preferred = ["site", *SITE_METADATA_COLUMNS, "scale", "rank", "selection_rule", "best_method", *METRIC_COLUMNS]
    return df[_ordered_columns(df, preferred)] if not df.empty else pd.DataFrame()


def write_summary(summary: pd.DataFrame, output_dir: Path) -> tuple[Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    csv_path = output_dir / "summary.csv"
    markdown_path = output_dir / "summary.md"
    summary.to_csv(csv_path, index=False)

    rule = summary["selection_rule"].iloc[0] if "selection_rule" in summary.columns and not summary.empty else DEFAULT_RANKING
    rule_description = SELECTION_RULE_DESCRIPTIONS.get(str(rule), str(rule))
    lines = [
        "# Results summary",
        "",
        f"Best methods are selected by `{rule}` ({rule_description}) for each site and temporal scale.",
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

    rule = rankings["selection_rule"].iloc[0] if "selection_rule" in rankings.columns and not rankings.empty else DEFAULT_RANKING
    rule_description = SELECTION_RULE_DESCRIPTIONS.get(str(rule), str(rule))
    lines = [
        "# Method rankings",
        "",
        "Methods are ranked within each site and temporal scale.",
        f"Overall `rank` follows `{rule}` ({rule_description}); per-metric ranks use their own metric criterion",
        "(MBE ranks by absolute bias; r, R², Willmott d, and confidence c favor higher values).",
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
                    f"Best overall: **{group.iloc[0]['method']}** by `{rule}`.",
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
