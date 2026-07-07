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
    assert "ET0 site report" in text
    assert "Rankings" in text


def test_write_index_creates_markdown_and_html(tmp_path, monkeypatch) -> None:
    reports = tmp_path / "reports"
    reports.mkdir()
    monkeypatch.setattr(report_builder, "OUTPUTS_REPORTS", reports)
    monkeypatch.setattr(report_builder, "OUTPUTS_TABLES", tmp_path / "tables")
    monkeypatch.setattr(report_builder, "OUTPUTS_FIGURES", tmp_path / "figures")

    md_path, html_path = report_builder.write_index(["manaus", "piracicaba"], tmp_path)
    assert md_path.exists()
    assert html_path.exists()
    assert "manaus" in md_path.read_text(encoding="utf-8")
    assert "<html" in html_path.read_text(encoding="utf-8").lower()
