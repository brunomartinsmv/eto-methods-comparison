from __future__ import annotations

import html
from pathlib import Path

import pandas as pd

from .config import OUTPUTS_FIGURES, OUTPUTS_REPORTS, OUTPUTS_TABLES, SITES

_HTML_STYLE = """
body { font-family: system-ui, sans-serif; max-width: 960px; margin: 2rem auto; padding: 0 1rem; line-height: 1.5; }
h1, h2 { color: #1a365d; }
table { border-collapse: collapse; width: 100%; margin: 1rem 0; }
th, td { border: 1px solid #cbd5e0; padding: 0.4rem 0.6rem; text-align: left; }
th { background: #edf2f7; }
a { color: #2b6cb0; }
img { max-width: 100%; height: auto; margin: 0.5rem 0; }
.card { background: #f7fafc; border: 1px solid #e2e8f0; border-radius: 6px; padding: 1rem; margin: 1rem 0; }
"""


def _read_csv_if_exists(path: Path) -> pd.DataFrame | None:
    if not path.exists():
        return None
    return pd.read_csv(path)


def _md_table(df: pd.DataFrame, max_rows: int = 20) -> str:
    if df is None or df.empty:
        return "_No data available._"
    display = df.head(max_rows)
    headers = [str(column) for column in display.columns]
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    for _, row in display.iterrows():
        cells = [str(row[column]).replace("|", "\\|") for column in display.columns]
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines)


def _figure_links(site: str, figures_dir: Path) -> list[tuple[str, Path]]:
    site_dir = figures_dir / site
    if not site_dir.exists():
        return []
    preferred = [
        f"{site}_daily_taylor.png",
        f"{site}_monthly_taylor.png",
        f"{site}_monthly_totals.png",
        f"{site}_bias_by_eto_bin.png",
    ]
    links: list[tuple[str, Path]] = []
    for name in preferred:
        path = site_dir / name
        if path.exists():
            links.append((name.replace(f"{site}_", "").replace(".png", ""), path))
    for path in sorted(site_dir.glob("*.png")):
        if path.name not in {item[1].name for item in links}:
            links.append((path.stem.replace(f"{site}_", ""), path))
    return links[:12]


def build_site_report_markdown(
    site: str,
    *,
    reports_dir: Path = OUTPUTS_REPORTS,
    tables_dir: Path = OUTPUTS_TABLES,
    figures_dir: Path = OUTPUTS_FIGURES,
) -> str:
    meta = SITES.get(site, {})
    lines = [
        f"# ET0 site report — {site}",
        "",
        "## Site metadata",
        "",
    ]
    for key in ("lat", "lon", "alt_m", "biome", "climate_class", "region", "country", "state"):
        if key in meta:
            lines.append(f"- **{key}**: {meta[key]}")
    lines.extend(["", "## Data quality", ""])

    quality = _read_csv_if_exists(reports_dir / f"{site}_data_quality.csv")
    lines.append(_md_table(quality, max_rows=15))
    lines.extend(["", "## Method feasibility", ""])

    feasibility = _read_csv_if_exists(reports_dir / f"{site}_method_feasibility.csv")
    lines.append(_md_table(feasibility))
    lines.extend(["", "## Rankings", ""])

    rankings = _read_csv_if_exists(tables_dir / "summary_rankings.csv")
    if rankings is not None and "site" in rankings.columns:
        site_rankings = rankings[rankings["site"] == site]
        lines.append(_md_table(site_rankings))
    else:
        lines.append("_No rankings available._")

    for scale in ("daily", "monthly"):
        lines.extend(["", f"## {scale.title()} metrics", ""])
        metrics = _read_csv_if_exists(tables_dir / f"{site}_{scale}_metrics.csv")
        lines.append(_md_table(metrics))

    uncertainty_path = reports_dir / f"{site}_uncertainty_sensitivity.md"
    if uncertainty_path.exists():
        lines.extend(["", "## Uncertainty and sensitivity", "", uncertainty_path.read_text(encoding="utf-8")])

    figures = _figure_links(site, figures_dir)
    if figures:
        lines.extend(["", "## Figures", ""])
        for label, path in figures:
            rel = Path("..") / "figures" / site / path.name
            lines.append(f"- [{label}]({rel.as_posix()})")

    return "\n".join(lines) + "\n"


def _wrap_html(title: str, body: str) -> str:
    return (
        "<!DOCTYPE html>\n<html lang=\"en\">\n<head>\n"
        f"<meta charset=\"utf-8\"><title>{html.escape(title)}</title>\n"
        f"<style>{_HTML_STYLE}</style>\n</head>\n<body>\n{body}\n</body>\n</html>\n"
    )


def _df_to_html_table(df: pd.DataFrame, max_rows: int = 20) -> str:
    if df is None or df.empty:
        return "<p><em>No data available.</em></p>"
    return df.head(max_rows).to_html(index=False, border=0, classes="data-table")


def build_site_report_html(
    site: str,
    *,
    reports_dir: Path = OUTPUTS_REPORTS,
    tables_dir: Path = OUTPUTS_TABLES,
    figures_dir: Path = OUTPUTS_FIGURES,
) -> str:
    meta = SITES.get(site, {})
    parts = [f"<h1>ET0 site report — {html.escape(site)}</h1>", "<div class=\"card\"><h2>Site metadata</h2><ul>"]
    for key in ("lat", "lon", "alt_m", "biome", "climate_class", "region", "country", "state"):
        if key in meta:
            parts.append(f"<li><strong>{html.escape(key)}</strong>: {html.escape(str(meta[key]))}</li>")
    parts.append("</ul></div>")

    quality = _read_csv_if_exists(reports_dir / f"{site}_data_quality.csv")
    parts.extend(["<h2>Data quality</h2>", _df_to_html_table(quality)])

    feasibility = _read_csv_if_exists(reports_dir / f"{site}_method_feasibility.csv")
    parts.extend(["<h2>Method feasibility</h2>", _df_to_html_table(feasibility)])

    rankings = _read_csv_if_exists(tables_dir / "summary_rankings.csv")
    if rankings is not None and "site" in rankings.columns:
        parts.extend(["<h2>Rankings</h2>", _df_to_html_table(rankings[rankings["site"] == site])])

    for scale in ("daily", "monthly"):
        metrics = _read_csv_if_exists(tables_dir / f"{site}_{scale}_metrics.csv")
        parts.extend([f"<h2>{scale.title()} metrics</h2>", _df_to_html_table(metrics)])

    uncertainty_path = reports_dir / f"{site}_uncertainty_sensitivity.md"
    if uncertainty_path.exists():
        parts.extend(
            [
                "<h2>Uncertainty and sensitivity</h2>",
                f"<pre>{html.escape(uncertainty_path.read_text(encoding='utf-8'))}</pre>",
            ]
        )

    figures = _figure_links(site, figures_dir)
    if figures:
        parts.append("<h2>Figures</h2>")
        for label, path in figures:
            rel = Path("..") / "figures" / site / path.name
            parts.append(
                f"<figure><figcaption>{html.escape(label)}</figcaption>"
                f"<img src=\"{rel.as_posix()}\" alt=\"{html.escape(label)}\"></figure>"
            )

    return _wrap_html(f"ET0 report — {site}", "\n".join(parts))


def write_site_report(
    site: str,
    output_dir: Path,
    *,
    reports_dir: Path = OUTPUTS_REPORTS,
    tables_dir: Path = OUTPUTS_TABLES,
    figures_dir: Path = OUTPUTS_FIGURES,
) -> tuple[Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    md_path = output_dir / f"{site}_report.md"
    html_path = output_dir / f"{site}_report.html"
    md_path.write_text(
        build_site_report_markdown(site, reports_dir=reports_dir, tables_dir=tables_dir, figures_dir=figures_dir),
        encoding="utf-8",
    )
    html_path.write_text(
        build_site_report_html(site, reports_dir=reports_dir, tables_dir=tables_dir, figures_dir=figures_dir),
        encoding="utf-8",
    )
    return md_path, html_path


def build_index_markdown(
    sites: list[str],
    *,
    reports_dir: Path = OUTPUTS_REPORTS,
    tables_dir: Path = OUTPUTS_TABLES,
    figures_dir: Path = OUTPUTS_FIGURES,
) -> str:
    lines = [
        "# ET0 pipeline results index",
        "",
        "Consolidated navigation for generated tables, reports, and figures.",
        "",
        "## Sites",
        "",
    ]
    for site in sites:
        lines.append(f"### {site}")
        lines.append(f"- [Site report (Markdown)](reports/{site}_report.md)")
        lines.append(f"- [Site report (HTML)](reports/{site}_report.html)")
        lines.append(f"- [Method feasibility](reports/{site}_method_feasibility.md)")
        lines.append(f"- [Data quality](reports/{site}_data_quality.csv)")
        lines.append(f"- [Daily metrics](../tables/{site}_daily_metrics.csv)")
        lines.append(f"- [Monthly metrics](../tables/{site}_monthly_metrics.csv)")
        lines.append(f"- [Figures directory](../figures/{site}/)")
        lines.append("")

    lines.extend(["## Global summaries", ""])
    for name in ("summary_rankings.md", "summary.md", "data_quality_summary.csv"):
        path = reports_dir / name if name.endswith(".md") else reports_dir / name
        if path.exists():
            lines.append(f"- [{name}](reports/{name})")
    rankings_csv = tables_dir / "summary_rankings.csv"
    if rankings_csv.exists():
        lines.append("- [summary_rankings.csv](../tables/summary_rankings.csv)")

    _ = figures_dir  # reserved for future thumbnail index
    return "\n".join(lines) + "\n"


def build_index_html(sites: list[str], *, reports_dir: Path = OUTPUTS_REPORTS) -> str:
    parts = ["<h1>ET0 pipeline results index</h1>", "<p>Consolidated navigation for generated outputs.</p>"]
    for site in sites:
        parts.append(f"<div class=\"card\"><h2>{html.escape(site)}</h2><ul>")
        for label, href in (
            ("Site report (HTML)", f"reports/{site}_report.html"),
            ("Site report (Markdown)", f"reports/{site}_report.md"),
            ("Method feasibility", f"reports/{site}_method_feasibility.md"),
            ("Data quality", f"reports/{site}_data_quality.csv"),
            ("Daily metrics", f"../tables/{site}_daily_metrics.csv"),
            ("Figures", f"../figures/{site}/"),
        ):
            parts.append(f"<li><a href=\"{href}\">{html.escape(label)}</a></li>")
        parts.append("</ul></div>")

    parts.append("<h2>Global summaries</h2><ul>")
    for name in ("summary_rankings.md", "summary.md"):
        if (reports_dir / name).exists():
            parts.append(f"<li><a href=\"reports/{name}\">{html.escape(name)}</a></li>")
    parts.append("</ul>")
    return _wrap_html("ET0 results index", "\n".join(parts))


def write_index(
    sites: list[str],
    output_dir: Path,
    *,
    reports_dir: Path = OUTPUTS_REPORTS,
    tables_dir: Path = OUTPUTS_TABLES,
    figures_dir: Path = OUTPUTS_FIGURES,
) -> tuple[Path, Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    md_path = output_dir / "index.md"
    html_path = output_dir / "index.html"
    md_path.write_text(
        build_index_markdown(sites, reports_dir=reports_dir, tables_dir=tables_dir, figures_dir=figures_dir),
        encoding="utf-8",
    )
    html_path.write_text(build_index_html(sites, reports_dir=reports_dir), encoding="utf-8")
    return md_path, html_path
