from __future__ import annotations

from pathlib import Path

import pandas as pd

METRIC_COLUMNS = ["rmse", "mae", "mbe", "r2", "willmott_d"]


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
