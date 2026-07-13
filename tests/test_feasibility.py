from __future__ import annotations

import pandas as pd

from scripts import feasibility


def _sample_weather() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "date": pd.date_range("2024-01-01", periods=3, freq="D"),
            "tmin_c": [20.0, 21.0, 22.0],
            "tmax_c": [30.0, 31.0, 32.0],
            "tmed_c": [25.0, 26.0, 27.0],
            "rh_mean_pct": [80.0, 81.0, 82.0],
            "wind_mean_ms": [2.0, 2.1, 2.2],
            "rad_global_mj_m2_d": [18.0, 19.0, 20.0],
            "rad_net_mj_m2_d": [10.0, 11.0, 12.0],
            "ra_extraterrestre_mj_m2_d": [34.0, 34.5, 35.0],
        }
    )


def test_build_method_feasibility_marks_computable_methods() -> None:
    df = _sample_weather()
    report = feasibility.build_method_feasibility(df)
    hs = report.loc[report["column"] == "et_hargreaves_samani", "status"].iloc[0]
    assert hs == "computable"


def test_build_input_summary_counts_valid_days() -> None:
    df = _sample_weather()
    summary = feasibility.build_input_summary(df)
    tmed = summary.loc[summary["variable"] == "tmed_c", "valid_days"].iloc[0]
    assert tmed == 3


def test_resolve_method_column_accepts_short_name() -> None:
    assert feasibility.resolve_method_column("hs") == "et_hargreaves_samani"
    assert feasibility.resolve_method_column("hargreaves_samani") == "et_hargreaves_samani"


def test_write_feasibility_reports_creates_files(tmp_path) -> None:
    df = _sample_weather()
    feasibility_df = feasibility.build_feasibility_from_compute(df, {"alt_m": 60.0})
    input_summary = feasibility.build_input_summary(df)
    csv_path, md_path, input_csv, input_md = feasibility.write_feasibility_reports(
        feasibility_df,
        input_summary,
        tmp_path,
        "manaus",
    )
    assert csv_path.exists()
    assert md_path.exists()
    assert input_csv.exists()
    assert input_md.exists()
    assert "Method feasibility" in md_path.read_text(encoding="utf-8")
    assert "## Summary" in md_path.read_text(encoding="utf-8")
    assert "Computable" in md_path.read_text(encoding="utf-8")
    assert (tmp_path / "manaus_method_feasibility.html").exists()
    assert "Newsreader" in (tmp_path / "manaus_method_feasibility.html").read_text(encoding="utf-8")
