from __future__ import annotations

import pandas as pd

from scripts import report_builder


def test_build_site_report_markdown_includes_rankings(tmp_path, monkeypatch) -> None:
    reports = tmp_path / "reports"
    tables = tmp_path / "tables"
    figures = tmp_path / "figures"
    reports.mkdir()
    tables.mkdir()
    figures.mkdir(parents=True)

    pd.DataFrame({"site": ["manaus"], "method": ["et_hs"], "rmse": [1.0]}).to_csv(
        tables / "summary_rankings.csv", index=False
    )
    pd.DataFrame({"variable": ["tmed_c"], "missing_days": [0]}).to_csv(
        reports / "manaus_data_quality.csv", index=False
    )
    pd.DataFrame(
        {
            "method_name": ["Hargreaves-Samani"],
            "column": ["et_hargreaves_samani"],
            "status": ["computable"],
            "required_columns": ["tmed_c"],
            "missing_columns": [""],
            "valid_day_fraction": [1.0],
            "reason": ["ok"],
        }
    ).to_csv(reports / "manaus_method_feasibility.csv", index=False)

    monkeypatch.setattr(report_builder, "OUTPUTS_REPORTS", reports)
    monkeypatch.setattr(report_builder, "OUTPUTS_TABLES", tables)
    monkeypatch.setattr(report_builder, "OUTPUTS_FIGURES", figures)
    monkeypatch.setattr(report_builder, "SITES", {"manaus": {"lat": -3.1, "country": "Brazil"}})

    text = report_builder.build_site_report_markdown("manaus")
    assert "ET₀ site report" in text
    assert "Method rankings" in text
    assert "Latitude" in text


def test_write_index_creates_markdown_and_html(tmp_path, monkeypatch) -> None:
    reports = tmp_path / "reports"
    tables = tmp_path / "tables"
    figures = tmp_path / "figures" / "manaus"
    reports.mkdir()
    tables.mkdir()
    figures.mkdir(parents=True)
    (figures / "manaus_daily_taylor.png").write_bytes(b"png")
    pd.DataFrame(
        {
            "site": ["manaus", "manaus"],
            "scale": ["daily", "monthly"],
            "rank": [1, 1],
            "method": ["et_lungeon", "et_lungeon"],
            "rmse": [0.5, 10.0],
            "mae": [0.4, 9.0],
            "mbe": [-0.3, -8.0],
            "r": [0.9, 0.95],
            "r2": [0.8, 0.9],
            "willmott_d": [0.7, 0.7],
            "c": [0.6, 0.65],
            "classification": ["Good", "Good"],
        }
    ).to_csv(tables / "summary_rankings.csv", index=False)

    monkeypatch.setattr(report_builder, "OUTPUTS_REPORTS", reports)
    monkeypatch.setattr(report_builder, "OUTPUTS_TABLES", tables)
    monkeypatch.setattr(report_builder, "OUTPUTS_FIGURES", tmp_path / "figures")

    md_path, html_path = report_builder.write_index(["manaus", "piracicaba"], tmp_path)
    assert md_path.exists()
    assert html_path.exists()
    md_text = md_path.read_text(encoding="utf-8")
    html_text = html_path.read_text(encoding="utf-8")
    assert "manaus" in md_text
    assert "tables/manaus_daily_metrics.csv" in md_text
    assert "../tables/" not in md_text
    assert "<html" in html_text.lower()
    assert "tables/manaus_daily_metrics.csv" in html_text
    assert "../tables/" not in html_text
    assert "figures/manaus/index.html" in html_text
    assert "method_feasibility.html" in html_text
    assert "Method rankings" in html_text
    assert "lungeon" in html_text.lower()
    monthly_pos = html_text.find("Manaus — monthly")
    daily_pos = html_text.find("Manaus — daily")
    assert monthly_pos != -1 and daily_pos != -1
    assert monthly_pos < daily_pos
    assert (tmp_path / "figures" / "manaus" / "index.html").exists()


def test_build_figures_gallery_lists_pngs(tmp_path) -> None:
    site_dir = tmp_path / "manaus"
    site_dir.mkdir()
    (site_dir / "manaus_daily_taylor.png").write_bytes(b"png")
    html_text = report_builder.build_figures_gallery_html("manaus", figures_dir=tmp_path)
    assert "manaus_daily_taylor.png" in html_text
    assert "daily_taylor" in html_text
