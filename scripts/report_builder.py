from __future__ import annotations

import html
from pathlib import Path

import pandas as pd

from .config import OUTPUTS_FIGURES, OUTPUTS_REPORTS, OUTPUTS_TABLES, SITES

_RANKING_COLUMNS = [
    "rank",
    "method",
    "rmse",
    "mae",
    "mbe",
    "r",
    "r2",
    "willmott_d",
    "c",
    "classification",
]

# Prefer coarser temporal scales first in rankings and metrics sections.
SCALE_DISPLAY_ORDER = ("monthly", "daily")

_META_LABELS = {
    "lat": "Latitude",
    "lon": "Longitude",
    "alt_m": "Altitude (m)",
    "biome": "Biome",
    "climate_class": "Climate",
    "region": "Region",
    "country": "Country",
    "state": "State",
}

_METRIC_COLUMNS = ["method", "rmse", "mae", "mbe", "r", "r2", "willmott_d", "c", "classification"]
_NUMERIC_COLUMNS = {"rmse", "mae", "mbe", "r", "r2", "willmott_d", "c", "valid_day_fraction"}

_HTML_STYLE = """
@import url("https://fonts.googleapis.com/css2?family=Newsreader:opsz,wght@6..72,500;6..72,600&family=DM+Sans:ital,opsz,wght@0,9..40,400;0,9..40,500;0,9..40,600;1,9..40,400&display=swap");

:root {
  --bg: #f7f4ef;
  --bg-accent: #efe8dc;
  --surface: #fffcf7;
  --ink: #1a1915;
  --muted: #6b6560;
  --line: #e4ddd2;
  --accent: #c96442;
  --accent-soft: #f3e4dc;
  --link: #9a3412;
  --excellent: #1f6b4a;
  --excellent-bg: #e4f2eb;
  --very-good: #2f6f5e;
  --very-good-bg: #e7f1ed;
  --good: #3d6b8c;
  --good-bg: #e6eef4;
  --average: #8a6d3b;
  --average-bg: #f5eedf;
  --poor: #9a5230;
  --poor-bg: #f6e8e0;
  --bad: #8b3a3a;
  --bad-bg: #f5e4e4;
  --very-poor: #6b2e2e;
  --very-poor-bg: #f0dfdf;
  --shadow: 0 1px 2px rgba(26, 25, 21, 0.04), 0 8px 24px rgba(26, 25, 21, 0.04);
}

* { box-sizing: border-box; }
html { scroll-behavior: smooth; }
body {
  margin: 0;
  color: var(--ink);
  background:
    radial-gradient(1200px 500px at 10% -10%, #f3e4dc 0%, transparent 55%),
    radial-gradient(900px 420px at 100% 0%, #efe8dc 0%, transparent 50%),
    var(--bg);
  font-family: "DM Sans", system-ui, sans-serif;
  font-optical-sizing: auto;
  line-height: 1.55;
  font-size: 15px;
}
a { color: var(--link); text-decoration-thickness: 1px; text-underline-offset: 0.18em; }
a:hover { color: var(--accent); }
.wrap { max-width: 1100px; margin: 0 auto; padding: 2.5rem 1.25rem 4rem; }
.hero {
  padding: 0.5rem 0 1.75rem;
  border-bottom: 1px solid var(--line);
  margin-bottom: 2rem;
}
.eyebrow {
  display: inline-block;
  font-size: 0.75rem;
  letter-spacing: 0.08em;
  text-transform: uppercase;
  color: var(--accent);
  font-weight: 600;
  margin-bottom: 0.6rem;
}
h1, h2, h3 {
  font-family: "Newsreader", Georgia, serif;
  font-weight: 600;
  letter-spacing: -0.02em;
  line-height: 1.2;
  color: var(--ink);
}
h1 { font-size: clamp(2rem, 4vw, 2.75rem); margin: 0 0 0.6rem; }
h2 { font-size: 1.45rem; margin: 0 0 0.75rem; }
h3 { font-size: 1.15rem; margin: 0 0 0.5rem; }
.lede { color: var(--muted); max-width: 42rem; margin: 0; font-size: 1.02rem; }
.site-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
  gap: 1rem;
  margin-bottom: 2.5rem;
}
.card {
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: 14px;
  padding: 1.25rem 1.35rem;
  box-shadow: var(--shadow);
}
.card h2 { margin-bottom: 0.25rem; }
.meta { color: var(--muted); font-size: 0.88rem; margin: 0 0 1rem; }
.links { list-style: none; padding: 0; margin: 0; display: grid; gap: 0.45rem; }
.links a {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
  padding: 0.55rem 0.7rem;
  border-radius: 8px;
  background: var(--bg);
  border: 1px solid transparent;
  text-decoration: none;
  color: var(--ink);
  font-weight: 500;
  transition: border-color 0.15s ease, background 0.15s ease;
}
.links a:hover {
  border-color: var(--line);
  background: var(--accent-soft);
  color: var(--ink);
}
.links a span.hint { color: var(--muted); font-size: 0.78rem; font-weight: 400; }
.section { margin: 2.5rem 0; }
.section-head {
  display: flex;
  flex-wrap: wrap;
  align-items: baseline;
  justify-content: space-between;
  gap: 0.5rem 1rem;
  margin-bottom: 1rem;
}
.section-head p { margin: 0; color: var(--muted); font-size: 0.92rem; }
.rank-block {
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: 14px;
  padding: 1.1rem 1.1rem 0.4rem;
  box-shadow: var(--shadow);
  margin-bottom: 1rem;
  overflow: hidden;
}
.rank-block-head {
  display: flex;
  flex-wrap: wrap;
  align-items: baseline;
  justify-content: space-between;
  gap: 0.35rem 1rem;
  margin-bottom: 0.85rem;
  padding: 0 0.15rem;
}
.best {
  color: var(--muted);
  font-size: 0.9rem;
}
.best strong { color: var(--ink); font-weight: 600; }
.table-scroll { overflow-x: auto; margin: 0 -0.15rem 0.75rem; }
table, .data-table {
  border-collapse: collapse;
  width: 100%;
  font-size: 0.86rem;
  min-width: 720px;
}
th, td {
  padding: 0.55rem 0.65rem;
  text-align: left;
  border-bottom: 1px solid var(--line);
  white-space: nowrap;
}
th {
  color: var(--muted);
  font-weight: 600;
  font-size: 0.72rem;
  letter-spacing: 0.04em;
  text-transform: uppercase;
  background: var(--bg-accent);
  position: sticky;
  top: 0;
}
tbody tr:hover td { background: rgba(201, 100, 66, 0.04); }
td.num { font-variant-numeric: tabular-nums; text-align: right; }
td.rank {
  font-weight: 600;
  font-variant-numeric: tabular-nums;
  color: var(--muted);
}
td.method { font-weight: 500; }
.badge {
  display: inline-block;
  padding: 0.15rem 0.5rem;
  border-radius: 999px;
  font-size: 0.72rem;
  font-weight: 600;
  letter-spacing: 0.02em;
}
.badge-excellent { color: var(--excellent); background: var(--excellent-bg); }
.badge-very-good { color: var(--very-good); background: var(--very-good-bg); }
.badge-good { color: var(--good); background: var(--good-bg); }
.badge-average { color: var(--average); background: var(--average-bg); }
.badge-poor { color: var(--poor); background: var(--poor-bg); }
.badge-bad { color: var(--bad); background: var(--bad-bg); }
.badge-very-poor { color: var(--very-poor); background: var(--very-poor-bg); }
.badge-computable { color: var(--excellent); background: var(--excellent-bg); }
.badge-precomputed-only { color: var(--good); background: var(--good-bg); }
.badge-not-computable { color: var(--bad); background: var(--bad-bg); }
.meta-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(140px, 1fr));
  gap: 0.75rem;
  margin: 0;
  padding: 0;
  list-style: none;
}
.meta-grid li {
  background: var(--bg);
  border: 1px solid var(--line);
  border-radius: 10px;
  padding: 0.7rem 0.85rem;
}
.meta-grid .label {
  display: block;
  color: var(--muted);
  font-size: 0.7rem;
  letter-spacing: 0.05em;
  text-transform: uppercase;
  font-weight: 600;
  margin-bottom: 0.2rem;
}
.meta-grid .value { font-weight: 500; font-variant-numeric: tabular-nums; }
.toc {
  display: flex;
  flex-wrap: wrap;
  gap: 0.45rem;
  margin: 1.25rem 0 0;
}
.toc a {
  text-decoration: none;
  color: var(--ink);
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: 999px;
  padding: 0.35rem 0.75rem;
  font-size: 0.82rem;
  font-weight: 500;
}
.toc a:hover { background: var(--accent-soft); border-color: transparent; color: var(--ink); }
.panel {
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: 14px;
  padding: 1.1rem;
  box-shadow: var(--shadow);
}
.panel + .panel { margin-top: 1rem; }
.figure-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 1rem;
}
figure {
  margin: 0;
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: 12px;
  overflow: hidden;
  box-shadow: var(--shadow);
}
figcaption {
  padding: 0.65rem 0.8rem;
  font-size: 0.82rem;
  color: var(--muted);
  border-bottom: 1px solid var(--line);
}
img { display: block; max-width: 100%; height: auto; }
.back { margin-bottom: 1.25rem; font-size: 0.9rem; }
.footer-note {
  margin-top: 2.5rem;
  padding-top: 1rem;
  border-top: 1px solid var(--line);
  color: var(--muted);
  font-size: 0.85rem;
}
pre {
  background: var(--surface);
  border: 1px solid var(--line);
  border-radius: 10px;
  padding: 1rem;
  overflow: auto;
}
ul { padding-left: 1.2rem; }
"""


def _read_csv_if_exists(path: Path) -> pd.DataFrame | None:
    if not path.exists():
        return None
    return pd.read_csv(path)


def _md_table(df: pd.DataFrame, max_rows: int = 40, *, columns: list[str] | None = None) -> str:
    if df is None or df.empty:
        return "_No data available._"
    display = df.copy()
    if columns:
        keep = [column for column in columns if column in display.columns]
        display = display[keep] if keep else display
    display = display.head(max_rows)
    if "method" in display.columns:
        display = display.assign(method=display["method"].map(_pretty_method))
    headers = [str(column) for column in display.columns]
    lines = [
        "| " + " | ".join(headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    for _, row in display.iterrows():
        cells: list[str] = []
        for column in display.columns:
            value = row[column]
            if value is None or (isinstance(value, float) and pd.isna(value)) or str(value) == "nan":
                cells.append("—")
            elif column in _NUMERIC_COLUMNS:
                cells.append(_fmt_metric(value))
            elif pd.api.types.is_numeric_dtype(display[column]) and not isinstance(value, str):
                number = float(value)
                cells.append(str(int(number)) if number.is_integer() else _fmt_metric(value))
            else:
                cells.append(str(value).replace("|", "\\|"))
        lines.append("| " + " | ".join(cells) + " |")
    return "\n".join(lines)


def _figure_links(site: str, figures_dir: Path, *, limit: int | None = 12) -> list[tuple[str, Path]]:
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
    if limit is None:
        return links
    return links[:limit]


def _pretty_method(name: object) -> str:
    text = str(name)
    if text.startswith("et_"):
        text = text[3:]
    return text.replace("_", " ").title()


def _fmt_metric(value: object, digits: int = 4) -> str:
    if value is None or (isinstance(value, float) and pd.isna(value)) or value == "":
        return "—"
    try:
        number = float(value)
    except (TypeError, ValueError):
        return html.escape(str(value))
    return f"{number:.{digits}f}"


def _badge(classification: object) -> str:
    label = "" if classification is None or (isinstance(classification, float) and pd.isna(classification)) else str(classification)
    if not label:
        return "<span class=\"badge badge-very-poor\">—</span>"
    slug = label.strip().lower().replace(" ", "-")
    return f'<span class="badge badge-{html.escape(slug)}">{html.escape(label)}</span>'


def _site_meta_line(site: str) -> str:
    meta = SITES.get(site, {})
    bits = [str(meta[key]) for key in ("biome", "climate_class", "state", "country") if key in meta]
    return " · ".join(bits)


def _rankings_sections_markdown(rankings: pd.DataFrame | None, sites: list[str]) -> list[str]:
    if rankings is None or rankings.empty or "site" not in rankings.columns:
        return ["_No rankings available._"]

    lines: list[str] = []
    scales = [
        scale
        for scale in SCALE_DISPLAY_ORDER
        if "scale" not in rankings.columns or scale in set(rankings["scale"].astype(str))
    ]
    if "scale" not in rankings.columns:
        scales = ["all"]

    for site in sites:
        site_df = rankings[rankings["site"] == site]
        if site_df.empty:
            continue
        for scale in scales:
            block = site_df if scale == "all" else site_df[site_df["scale"].astype(str) == scale]
            if block.empty:
                continue
            ordered = block.sort_values("rank") if "rank" in block.columns else block
            best = ordered.iloc[0]
            best_method = _pretty_method(best["method"]) if "method" in ordered.columns else "—"
            lines.extend(
                [
                    f"### {site.title()} — {scale}",
                    "",
                    f"Best overall: **{best_method}** (composite rank).",
                    "",
                    _md_table(ordered, columns=list(_RANKING_COLUMNS)),
                    "",
                ]
            )
    return lines if lines else ["_No rankings available for selected sites._"]


def build_site_report_markdown(
    site: str,
    *,
    reports_dir: Path = OUTPUTS_REPORTS,
    tables_dir: Path = OUTPUTS_TABLES,
    figures_dir: Path = OUTPUTS_FIGURES,
) -> str:
    meta = SITES.get(site, {})
    lede = _site_meta_line(site) or "Reference ET₀ method comparison against FAO-56 Penman–Monteith."
    lines = [
        f"# ET₀ site report — {site.title()}",
        "",
        lede,
        "",
        "[← Results index](../index.md)",
        "",
        "## Site metadata",
        "",
    ]
    for key in ("lat", "lon", "alt_m", "biome", "climate_class", "region", "country", "state"):
        if key in meta:
            lines.append(f"- **{_META_LABELS.get(key, key)}**: {meta[key]}")

    lines.extend(
        [
            "",
            "## Data quality",
            "",
            "Coverage and QC flags by input variable.",
            "",
        ]
    )
    quality = _read_csv_if_exists(reports_dir / f"{site}_data_quality.csv")
    lines.append(_md_table(quality, max_rows=30))

    lines.extend(
        [
            "",
            "## Method feasibility",
            "",
            "Which methods can be computed from available inputs.",
            "",
            f"[Open HTML version]({site}_method_feasibility.html)",
            "",
        ]
    )
    feasibility = _read_csv_if_exists(reports_dir / f"{site}_method_feasibility.csv")
    lines.append(
        _md_table(
            feasibility,
            columns=[
                "method_name",
                "status",
                "required_columns",
                "missing_columns",
                "valid_day_fraction",
                "reason",
            ],
        )
    )

    lines.extend(
        [
            "",
            "## Method rankings",
            "",
            "Composite rank within this site. Monthly scale is listed before daily.",
            "",
        ]
    )
    rankings = _read_csv_if_exists(tables_dir / "summary_rankings.csv")
    lines.extend(_rankings_sections_markdown(rankings, [site]))

    for scale in SCALE_DISPLAY_ORDER:
        lines.extend(
            [
                "",
                f"## {scale.title()} metrics",
                "",
                "Error and agreement metrics versus Penman–Monteith.",
                "",
            ]
        )
        metrics = _read_csv_if_exists(tables_dir / f"{site}_{scale}_metrics.csv")
        if metrics is not None and "c" in metrics.columns:
            metrics = metrics.sort_values("c", ascending=False, na_position="last")
        lines.append(_md_table(metrics, columns=list(_METRIC_COLUMNS)))

    uncertainty_path = reports_dir / f"{site}_uncertainty_sensitivity.md"
    if uncertainty_path.exists():
        lines.extend(
            [
                "",
                "## Uncertainty and sensitivity",
                "",
                uncertainty_path.read_text(encoding="utf-8").strip(),
                "",
            ]
        )

    figures = _figure_links(site, figures_dir)
    if figures or (figures_dir / site).exists():
        lines.extend(["", "## Figures", ""])
        if (figures_dir / site / "index.html").exists():
            lines.append(f"- [Full figures gallery (HTML)](../figures/{site}/index.html)")
        for label, path in figures:
            rel = Path("..") / "figures" / site / path.name
            lines.append(f"- [{label}]({rel.as_posix()})")

    lines.extend(["", "---", "", "Generated by the ET₀ methods comparison pipeline.", ""])
    return "\n".join(lines)


def _wrap_html(title: str, body: str) -> str:
    return (
        "<!DOCTYPE html>\n<html lang=\"en\">\n<head>\n"
        f"<meta charset=\"utf-8\">\n"
        f"<meta name=\"viewport\" content=\"width=device-width, initial-scale=1\">\n"
        f"<title>{html.escape(title)}</title>\n"
        f"<style>{_HTML_STYLE}</style>\n</head>\n<body>\n"
        f"<div class=\"wrap\">\n{body}\n</div>\n"
        "</body>\n</html>\n"
    )


def _df_to_html_table(df: pd.DataFrame, max_rows: int = 40) -> str:
    if df is None or df.empty:
        return "<p><em>No data available.</em></p>"
    display = df.head(max_rows).copy()
    for column in display.columns:
        if column == "method":
            display[column] = display[column].map(_pretty_method)
    header = "".join(f"<th>{html.escape(str(column))}</th>" for column in display.columns)
    rows: list[str] = []
    for _, row in display.iterrows():
        cells: list[str] = []
        for column in display.columns:
            value = row[column]
            if column in {"classification", "status"}:
                cells.append(f"<td>{_badge(value)}</td>")
            elif column == "method":
                cells.append(f"<td class=\"method\">{html.escape(str(value))}</td>")
            elif column in _NUMERIC_COLUMNS:
                cells.append(f"<td class=\"num\">{_fmt_metric(value)}</td>")
            elif pd.api.types.is_numeric_dtype(display[column]):
                if pd.isna(value):
                    cells.append("<td class=\"num\">—</td>")
                elif float(value).is_integer():
                    cells.append(f"<td class=\"num\">{int(value)}</td>")
                else:
                    cells.append(f"<td class=\"num\">{_fmt_metric(value)}</td>")
            else:
                text = "" if value is None or (isinstance(value, float) and pd.isna(value)) else str(value)
                cells.append(f"<td>{html.escape(text) if text else '—'}</td>")
        rows.append("<tr>" + "".join(cells) + "</tr>")
    return (
        "<div class=\"table-scroll\"><table class=\"data-table\">"
        f"<thead><tr>{header}</tr></thead>"
        f"<tbody>{''.join(rows)}</tbody>"
        "</table></div>"
    )


def _metrics_table_html(df: pd.DataFrame | None) -> str:
    if df is None or df.empty:
        return "<p><em>No data available.</em></p>"
    columns = [column for column in _METRIC_COLUMNS if column in df.columns]
    if not columns:
        return _df_to_html_table(df)
    ordered = df.copy()
    if "c" in ordered.columns:
        ordered = ordered.sort_values("c", ascending=False, na_position="last")
    return _df_to_html_table(ordered[columns])


def build_site_report_html(
    site: str,
    *,
    reports_dir: Path = OUTPUTS_REPORTS,
    tables_dir: Path = OUTPUTS_TABLES,
    figures_dir: Path = OUTPUTS_FIGURES,
) -> str:
    meta = SITES.get(site, {})
    rankings = _read_csv_if_exists(tables_dir / "summary_rankings.csv")
    quality = _read_csv_if_exists(reports_dir / f"{site}_data_quality.csv")
    feasibility = _read_csv_if_exists(reports_dir / f"{site}_method_feasibility.csv")
    figures = _figure_links(site, figures_dir)
    uncertainty_path = reports_dir / f"{site}_uncertainty_sensitivity.md"

    parts = [
        "<p class=\"back\"><a href=\"../index.html\">← Back to results index</a></p>",
        "<div class=\"hero\">",
        "<p class=\"eyebrow\">Site report</p>",
        f"<h1>ET₀ — {html.escape(site.title())}</h1>",
        f"<p class=\"lede\">{html.escape(_site_meta_line(site) or 'Reference ET₀ method comparison against FAO-56 Penman–Monteith.')}</p>",
        "<nav class=\"toc\">",
        "<a href=\"#metadata\">Metadata</a>",
        "<a href=\"#quality\">Data quality</a>",
        "<a href=\"#feasibility\">Feasibility</a>",
        "<a href=\"#rankings\">Rankings</a>",
        "<a href=\"#monthly-metrics\">Monthly metrics</a>",
        "<a href=\"#daily-metrics\">Daily metrics</a>",
    ]
    if uncertainty_path.exists():
        parts.append("<a href=\"#uncertainty\">Uncertainty</a>")
    if figures or (figures_dir / site).exists():
        parts.append("<a href=\"#figures\">Figures</a>")
    parts.append("</nav></div>")

    parts.append("<div class=\"section\" id=\"metadata\"><div class=\"card\">")
    parts.append("<h2>Site metadata</h2>")
    parts.append("<ul class=\"meta-grid\">")
    for key in ("lat", "lon", "alt_m", "biome", "climate_class", "region", "country", "state"):
        if key not in meta:
            continue
        label = _META_LABELS.get(key, key)
        parts.append(
            f"<li><span class=\"label\">{html.escape(label)}</span>"
            f"<span class=\"value\">{html.escape(str(meta[key]))}</span></li>"
        )
    parts.append("</ul></div></div>")

    parts.append("<div class=\"section\" id=\"quality\">")
    parts.append("<div class=\"section-head\"><h2>Data quality</h2><p>Coverage and QC flags by input variable.</p></div>")
    parts.append("<div class=\"panel\">")
    parts.append(_df_to_html_table(quality, max_rows=30))
    parts.append("</div></div>")

    parts.append("<div class=\"section\" id=\"feasibility\">")
    parts.append(
        "<div class=\"section-head\"><h2>Method feasibility</h2>"
        f"<p><a href=\"{html.escape(site)}_method_feasibility.html\">Open dedicated feasibility page →</a></p></div>"
    )
    parts.append("<div class=\"panel\">")
    parts.append(_df_to_html_table(feasibility, max_rows=40))
    parts.append("</div></div>")

    parts.append("<div class=\"section\" id=\"rankings\">")
    parts.append(
        "<div class=\"section-head\"><h2>Method rankings</h2>"
        "<p>Composite rank within this site (monthly, then daily).</p></div>"
    )
    parts.append(_rankings_sections_html(rankings, [site]))
    parts.append("</div>")

    for scale in SCALE_DISPLAY_ORDER:
        metrics = _read_csv_if_exists(tables_dir / f"{site}_{scale}_metrics.csv")
        parts.append(f"<div class=\"section\" id=\"{scale}-metrics\">")
        parts.append(
            f"<div class=\"section-head\"><h2>{scale.title()} metrics</h2>"
            f"<p>Error and agreement metrics versus Penman–Monteith.</p></div>"
        )
        parts.append("<div class=\"panel\">")
        parts.append(_metrics_table_html(metrics))
        parts.append("</div></div>")

    if uncertainty_path.exists():
        parts.append("<div class=\"section\" id=\"uncertainty\">")
        parts.append(
            "<div class=\"section-head\"><h2>Uncertainty and sensitivity</h2>"
            "<p>Bootstrap intervals and sensitivity notes.</p></div>"
        )
        parts.append(f"<div class=\"panel\"><pre>{html.escape(uncertainty_path.read_text(encoding='utf-8'))}</pre></div>")
        parts.append("</div>")

    if figures or (figures_dir / site).exists():
        parts.append("<div class=\"section\" id=\"figures\">")
        parts.append("<div class=\"section-head\">")
        parts.append("<h2>Figures</h2>")
        gallery_href = f"../figures/{site}/index.html"
        parts.append(f"<p><a href=\"{gallery_href}\">Open full gallery →</a></p>")
        parts.append("</div>")
        if figures:
            parts.append("<div class=\"figure-grid\">")
            for label, path in figures:
                rel = Path("..") / "figures" / site / path.name
                parts.append(
                    f"<figure><figcaption>{html.escape(label)}</figcaption>"
                    f"<img src=\"{rel.as_posix()}\" alt=\"{html.escape(label)}\" loading=\"lazy\"></figure>"
                )
            parts.append("</div>")
        parts.append("</div>")

    parts.append(
        "<p class=\"footer-note\">Generated by the ET₀ methods comparison pipeline · "
        "<a href=\"../index.html\">Results index</a></p>"
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
    write_feasibility_html(site, reports_dir=output_dir)
    return md_path, html_path


def build_feasibility_html(
    site: str,
    *,
    reports_dir: Path = OUTPUTS_REPORTS,
    feasibility: pd.DataFrame | None = None,
    input_summary: pd.DataFrame | None = None,
) -> str:
    feasibility = feasibility if feasibility is not None else _read_csv_if_exists(reports_dir / f"{site}_method_feasibility.csv")
    input_summary = (
        input_summary
        if input_summary is not None
        else _read_csv_if_exists(reports_dir / f"{site}_input_summary.csv")
    )

    counts: dict[str, int] = {}
    if feasibility is not None and not feasibility.empty and "status" in feasibility.columns:
        counts = {str(status): int(count) for status, count in feasibility["status"].value_counts().items()}

    parts = [
        "<p class=\"back\"><a href=\"../index.html\">← Back to results index</a></p>",
        "<div class=\"hero\">",
        "<p class=\"eyebrow\">Method feasibility</p>",
        f"<h1>{html.escape(site.title())}</h1>",
        "<p class=\"lede\">Which ET₀ methods can be computed from the available meteorological inputs "
        f"for {html.escape(site.title())}.</p>",
        "<nav class=\"toc\">",
        "<a href=\"#summary\">Summary</a>",
        "<a href=\"#methods\">Methods</a>",
        "<a href=\"#coverage\">Input coverage</a>",
        f"<a href=\"{html.escape(site)}_report.html\">Site report</a>",
        "</nav></div>",
        "<div class=\"section\" id=\"summary\">",
        "<div class=\"section-head\"><h2>Summary</h2><p>Counts by feasibility status.</p></div>",
        "<ul class=\"meta-grid\">",
    ]
    if counts:
        for status, count in sorted(counts.items()):
            label = status.replace("_", " ").title()
            parts.append(
                f"<li><span class=\"label\">{html.escape(label)}</span>"
                f"<span class=\"value\">{count}</span></li>"
            )
    else:
        parts.append("<li><span class=\"label\">Methods</span><span class=\"value\">0</span></li>")
    parts.append("</ul></div>")

    parts.append("<div class=\"section\" id=\"methods\">")
    parts.append(
        "<div class=\"section-head\"><h2>Methods</h2>"
        "<p>Required inputs, coverage, and compute status.</p></div>"
    )
    parts.append("<div class=\"panel\">")
    if feasibility is not None:
        cols = [
            column
            for column in (
                "method_name",
                "status",
                "required_columns",
                "missing_columns",
                "valid_day_fraction",
                "reason",
            )
            if column in feasibility.columns
        ]
        parts.append(_df_to_html_table(feasibility[cols] if cols else feasibility, max_rows=50))
    else:
        parts.append("<p><em>No feasibility table available.</em></p>")
    parts.append("</div></div>")

    parts.append("<div class=\"section\" id=\"coverage\">")
    parts.append(
        "<div class=\"section-head\"><h2>Input variable coverage</h2>"
        "<p>Presence and completeness of weather variables.</p></div>"
    )
    parts.append("<div class=\"panel\">")
    parts.append(_df_to_html_table(input_summary, max_rows=40) if input_summary is not None else "<p><em>No input summary available.</em></p>")
    parts.append("</div></div>")

    parts.append(
        "<p class=\"footer-note\">Also available as "
        f"<a href=\"{html.escape(site)}_method_feasibility.md\">Markdown</a> · "
        f"<a href=\"{html.escape(site)}_method_feasibility.csv\">CSV</a></p>"
    )
    return _wrap_html(f"Method feasibility — {site}", "\n".join(parts))


def write_feasibility_html(
    site: str,
    *,
    reports_dir: Path | None = None,
    feasibility: pd.DataFrame | None = None,
    input_summary: pd.DataFrame | None = None,
) -> Path:
    reports_dir = reports_dir or OUTPUTS_REPORTS
    reports_dir.mkdir(parents=True, exist_ok=True)
    path = reports_dir / f"{site}_method_feasibility.html"
    path.write_text(
        build_feasibility_html(
            site,
            reports_dir=reports_dir,
            feasibility=feasibility,
            input_summary=input_summary,
        ),
        encoding="utf-8",
    )
    return path


def build_rankings_html(
    *,
    reports_dir: Path = OUTPUTS_REPORTS,
    tables_dir: Path = OUTPUTS_TABLES,
    sites: list[str] | None = None,
) -> str:
    rankings = _read_csv_if_exists(tables_dir / "summary_rankings.csv")
    if sites is None:
        if rankings is not None and "site" in rankings.columns:
            sites = list(dict.fromkeys(rankings["site"].astype(str).tolist()))
        else:
            sites = list(SITES.keys())

    parts = [
        "<p class=\"back\"><a href=\"../index.html\">← Back to results index</a></p>",
        "<div class=\"hero\">",
        "<p class=\"eyebrow\">Global summary</p>",
        "<h1>Method rankings</h1>",
        "<p class=\"lede\">Composite ranks within each site and temporal scale. "
        "Monthly scale is listed before daily.</p>",
        "</div>",
        "<div class=\"section\">",
        _rankings_sections_html(rankings, sites),
        "</div>",
        "<p class=\"footer-note\">Source: "
        "<a href=\"../tables/summary_rankings.csv\">summary_rankings.csv</a> · "
        "<a href=\"summary_rankings.md\">summary_rankings.md</a></p>",
    ]
    return _wrap_html("Method rankings", "\n".join(parts))


def write_rankings_html(
    *,
    reports_dir: Path | None = None,
    tables_dir: Path | None = None,
    sites: list[str] | None = None,
) -> Path:
    reports_dir = reports_dir or OUTPUTS_REPORTS
    tables_dir = tables_dir or OUTPUTS_TABLES
    reports_dir.mkdir(parents=True, exist_ok=True)
    path = reports_dir / "summary_rankings.html"
    path.write_text(
        build_rankings_html(reports_dir=reports_dir, tables_dir=tables_dir, sites=sites),
        encoding="utf-8",
    )
    return path


def build_figures_gallery_html(site: str, *, figures_dir: Path = OUTPUTS_FIGURES) -> str:
    figures = _figure_links(site, figures_dir, limit=None)
    parts = [
        "<p class=\"back\"><a href=\"../../index.html\">← Back to results index</a></p>",
        "<p class=\"eyebrow\">Figures</p>",
        f"<h1>{html.escape(site.title())}</h1>",
        f"<p class=\"lede\">Generated comparison plots for {html.escape(site)} "
        f"({len(figures)} figure{'s' if len(figures) != 1 else ''}).</p>",
    ]
    if not figures:
        parts.append("<p><em>No figures available for this site.</em></p>")
    else:
        parts.append("<div class=\"figure-grid\" style=\"margin-top:1.75rem\">")
        for label, path in figures:
            parts.append(
                f"<figure><figcaption>{html.escape(label)}</figcaption>"
                f"<img src=\"{html.escape(path.name)}\" alt=\"{html.escape(label)}\" loading=\"lazy\"></figure>"
            )
        parts.append("</div>")
    return _wrap_html(f"Figures — {site}", "\n".join(parts))


def write_figures_gallery(site: str, *, figures_dir: Path | None = None) -> Path | None:
    figures_dir = figures_dir or OUTPUTS_FIGURES
    site_dir = figures_dir / site
    if not site_dir.exists():
        return None
    path = site_dir / "index.html"
    path.write_text(build_figures_gallery_html(site, figures_dir=figures_dir), encoding="utf-8")
    return path


def _rankings_table_html(df: pd.DataFrame) -> str:
    columns = [column for column in _RANKING_COLUMNS if column in df.columns]
    if not columns:
        return "<p><em>No ranking columns available.</em></p>"

    header = "".join(f"<th>{html.escape(column)}</th>" for column in columns)
    rows: list[str] = []
    numeric = {"rmse", "mae", "mbe", "r", "r2", "willmott_d", "c"}
    for _, row in df.iterrows():
        cells: list[str] = []
        for column in columns:
            value = row[column]
            if column == "rank":
                cells.append(f"<td class=\"rank\">{html.escape(str(int(value) if pd.notna(value) else '—'))}</td>")
            elif column == "method":
                cells.append(f"<td class=\"method\">{html.escape(_pretty_method(value))}</td>")
            elif column == "classification":
                cells.append(f"<td>{_badge(value)}</td>")
            elif column in numeric:
                cells.append(f"<td class=\"num\">{_fmt_metric(value)}</td>")
            else:
                cells.append(f"<td>{html.escape(str(value))}</td>")
        rows.append("<tr>" + "".join(cells) + "</tr>")

    return (
        "<div class=\"table-scroll\"><table>"
        f"<thead><tr>{header}</tr></thead>"
        f"<tbody>{''.join(rows)}</tbody>"
        "</table></div>"
    )


def _rankings_sections_html(rankings: pd.DataFrame | None, sites: list[str]) -> str:
    if rankings is None or rankings.empty or "site" not in rankings.columns:
        return "<p><em>No rankings available. Run the summary step to generate summary_rankings.csv.</em></p>"

    parts: list[str] = []
    scales = [
        scale
        for scale in SCALE_DISPLAY_ORDER
        if "scale" not in rankings.columns or scale in set(rankings["scale"].astype(str))
    ]
    if "scale" not in rankings.columns:
        scales = ["all"]

    for site in sites:
        site_df = rankings[rankings["site"] == site]
        if site_df.empty:
            continue
        for scale in scales:
            block = site_df if scale == "all" else site_df[site_df["scale"].astype(str) == scale]
            if block.empty:
                continue
            ordered = block.sort_values("rank") if "rank" in block.columns else block
            best = ordered.iloc[0]
            best_method = _pretty_method(best["method"]) if "method" in ordered.columns else "—"
            title = f"{site.title()} — {scale}"
            parts.append("<div class=\"rank-block\">")
            parts.append("<div class=\"rank-block-head\">")
            parts.append(f"<h3>{html.escape(title)}</h3>")
            parts.append(
                f"<p class=\"best\">Best overall: <strong>{html.escape(best_method)}</strong> "
                f"(composite rank)</p>"
            )
            parts.append("</div>")
            parts.append(_rankings_table_html(ordered))
            parts.append("</div>")
    return "\n".join(parts) if parts else "<p><em>No rankings available for selected sites.</em></p>"


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
        lines.append(f"- [Site report](reports/{site}_report.html)")
        if (reports_dir / f"{site}_method_feasibility.html").exists() or (
            reports_dir / f"{site}_method_feasibility.csv"
        ).exists():
            lines.append(f"- [Method feasibility](reports/{site}_method_feasibility.html)")
        lines.append(f"- [Data quality](reports/{site}_data_quality.csv)")
        lines.append(f"- [Daily metrics](tables/{site}_daily_metrics.csv)")
        lines.append(f"- [Monthly metrics](tables/{site}_monthly_metrics.csv)")
        if (figures_dir / site).exists():
            lines.append(f"- [Figures gallery](figures/{site}/index.html)")
        lines.append("")

    lines.extend(["## Global summaries", ""])
    for name in ("summary_rankings.html", "summary_rankings.md", "summary.md", "data_quality_summary.csv"):
        path = reports_dir / name
        if path.exists():
            lines.append(f"- [{name}](reports/{name})")
    rankings_csv = tables_dir / "summary_rankings.csv"
    if rankings_csv.exists():
        lines.append("- [summary_rankings.csv](tables/summary_rankings.csv)")

    return "\n".join(lines) + "\n"


def build_index_html(
    sites: list[str],
    *,
    reports_dir: Path = OUTPUTS_REPORTS,
    tables_dir: Path = OUTPUTS_TABLES,
    figures_dir: Path = OUTPUTS_FIGURES,
) -> str:
    rankings = _read_csv_if_exists(tables_dir / "summary_rankings.csv")

    parts = [
        "<p class=\"eyebrow\">ET₀ methods comparison</p>",
        "<h1>Pipeline results</h1>",
        "<p class=\"lede\">Browse site reports, metrics tables, figure galleries, and composite method rankings "
        "against FAO-56 Penman–Monteith.</p>",
        "<div class=\"site-grid\" style=\"margin-top:2rem\">",
    ]

    for site in sites:
        meta = _site_meta_line(site)
        parts.append("<div class=\"card\">")
        parts.append(f"<h2>{html.escape(site.title())}</h2>")
        if meta:
            parts.append(f"<p class=\"meta\">{html.escape(meta)}</p>")
        parts.append("<ul class=\"links\">")
        link_items: list[tuple[str, str, str]] = [
            ("Site report", f"reports/{site}_report.html", "HTML"),
            ("Method feasibility", f"reports/{site}_method_feasibility.html", "HTML"),
            ("Data quality", f"reports/{site}_data_quality.csv", "CSV"),
            ("Monthly metrics", f"tables/{site}_monthly_metrics.csv", "CSV"),
            ("Daily metrics", f"tables/{site}_daily_metrics.csv", "CSV"),
        ]
        if (figures_dir / site).exists():
            link_items.append(("Figures gallery", f"figures/{site}/index.html", "HTML"))
        for label, href, hint in link_items:
            parts.append(
                f"<li><a href=\"{html.escape(href)}\">{html.escape(label)}"
                f"<span class=\"hint\">{html.escape(hint)}</span></a></li>"
            )
        parts.append("</ul></div>")

    parts.append("</div>")

    parts.append("<div class=\"section\" id=\"rankings\">")
    parts.append("<div class=\"section-head\">")
    parts.append("<h2>Method rankings</h2>")
    parts.append(
        "<p>Composite rank: highest c, then lowest RMSE / MAE, highest Willmott d, lowest |MBE|. "
        "Monthly scale is listed before daily.</p>"
    )
    parts.append("</div>")
    parts.append(_rankings_sections_html(rankings, sites))
    if rankings is not None:
        parts.append(
            "<p class=\"footer-note\">Source: "
            "<a href=\"tables/summary_rankings.csv\">tables/summary_rankings.csv</a> · "
            "<a href=\"reports/summary_rankings.html\">HTML</a> · "
            "<a href=\"reports/summary_rankings.md\">Markdown</a></p>"
        )
    parts.append("</div>")

    summary_links: list[str] = []
    for label, name in (
        ("Method rankings", "summary_rankings.html"),
        ("Results summary", "summary.md"),
        ("Data quality summary", "data_quality_summary.csv"),
    ):
        if (reports_dir / name).exists():
            summary_links.append(
                f"<li><a href=\"reports/{name}\">{html.escape(label)}"
                f"<span class=\"hint\">{html.escape(name.split('.')[-1].upper())}</span></a></li>"
            )
    if summary_links:
        parts.append("<div class=\"section\"><h2>Other summaries</h2><ul class=\"links\">")
        parts.extend(summary_links)
        parts.append("</ul></div>")

    return _wrap_html("ET0 results index", "\n".join(parts))


def write_index(
    sites: list[str],
    output_dir: Path,
    *,
    reports_dir: Path | None = None,
    tables_dir: Path | None = None,
    figures_dir: Path | None = None,
) -> tuple[Path, Path]:
    reports_dir = reports_dir or OUTPUTS_REPORTS
    tables_dir = tables_dir or OUTPUTS_TABLES
    figures_dir = figures_dir or OUTPUTS_FIGURES
    output_dir.mkdir(parents=True, exist_ok=True)
    for site in sites:
        write_figures_gallery(site, figures_dir=figures_dir)
        write_feasibility_html(site, reports_dir=reports_dir)
    write_rankings_html(reports_dir=reports_dir, tables_dir=tables_dir, sites=sites)

    md_path = output_dir / "index.md"
    html_path = output_dir / "index.html"
    md_path.write_text(
        build_index_markdown(sites, reports_dir=reports_dir, tables_dir=tables_dir, figures_dir=figures_dir),
        encoding="utf-8",
    )
    html_path.write_text(
        build_index_html(
            sites,
            reports_dir=reports_dir,
            tables_dir=tables_dir,
            figures_dir=figures_dir,
        ),
        encoding="utf-8",
    )
    return md_path, html_path
