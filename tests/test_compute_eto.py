from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

from scripts import compute_eto
from scripts.cli import cmd_compute_eto
from scripts.config import METHODS, REFERENCE_COLUMN
from scripts.naming import daily_eto_filename


def _weather_frame() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "date": pd.to_datetime(["2024-01-01", "2024-01-02"]),
            "tmed_c": [25.0, 26.0],
            "tmin_c": [20.0, 21.0],
            "tmax_c": [30.0, 31.0],
            "rh_mean_pct": [70.0, 65.0],
            "wind_mean_ms": [2.0, 2.5],
            "rad_global_mj_m2_d": [18.0, 19.0],
            "rad_net_mj_m2_d": [10.0, 11.0],
            "ra_extraterrestre_mj_m2_d": [35.0, 36.0],
        }
    )


def test_compute_daily_eto_calculates_configured_methods_from_weather_columns() -> None:
    result = compute_eto.compute_daily_eto(
        _weather_frame(),
        site_meta={"alt_m": 120.0},
    )

    frame = result.frame
    assert "date" in frame.columns
    assert REFERENCE_COLUMN in frame.columns
    assert "et_hargreaves_samani" in frame.columns
    assert "et_makkink" in frame.columns
    assert "et_turc" in frame.columns
    assert "et_hicks_hess" in frame.columns
    assert np.isfinite(frame[REFERENCE_COLUMN]).all()
    assert np.isfinite(frame["et_hargreaves_samani"]).all()
    assert "et_penman_monteith" in result.report.computed


def test_compute_daily_eto_reports_skipped_methods_when_required_columns_missing() -> None:
    df = _weather_frame().drop(columns=["wind_mean_ms", "rad_net_mj_m2_d"])

    result = compute_eto.compute_daily_eto(df, site_meta={"alt_m": 120.0})

    assert REFERENCE_COLUMN not in result.frame.columns
    skipped_columns = {skip.column for skip in result.report.skipped}
    assert "et_penman_monteith" in skipped_columns
    assert "et_net_radiation" in skipped_columns


def test_compute_daily_eto_attaches_precomputed_only_columns_from_input() -> None:
    df = _weather_frame()
    df["et_thornthwaite"] = [5.0, 5.1]
    df["et_hargreaves_samani_corr"] = [2.5, 2.6]

    result = compute_eto.compute_daily_eto(df, site_meta={"alt_m": 120.0})

    assert result.frame["et_thornthwaite"].tolist() == [5.0, 5.1]
    assert result.frame["et_hargreaves_samani_corr"].tolist() == [2.5, 2.6]
    assert "et_thornthwaite" in result.report.attached_precomputed_only
    assert "et_hargreaves_samani_corr" in result.report.attached_precomputed_only
    assert "et_thornthwaite" not in result.report.computed


def test_compute_daily_eto_can_keep_precomputed_columns_for_validation() -> None:
    df = _weather_frame()
    df["et_penman_monteith"] = [4.0, 4.2]

    result = compute_eto.compute_daily_eto(
        df,
        site_meta={"alt_m": 120.0},
        include_precomputed=True,
    )

    frame = result.frame
    assert "precomputed_et_penman_monteith" in frame.columns
    assert frame["precomputed_et_penman_monteith"].tolist() == [4.0, 4.2]
    assert frame[REFERENCE_COLUMN].tolist() != [4.0, 4.2]
    assert len(result.report.comparisons) == 1
    comparison = result.report.comparisons[0]
    assert comparison.column == "et_penman_monteith"
    assert comparison.n_pairs == 2
    assert comparison.rmse > 0


def test_compute_eto_cli_writes_daily_eto_file(tmp_path: Path, caplog) -> None:
    import logging

    from scripts.logging_config import setup_logging

    setup_logging()

    input_dir = tmp_path / "cleaned"
    output_dir = tmp_path / "results"
    input_dir.mkdir()
    _weather_frame().to_csv(input_dir / "manaus_daily.csv", index=False)

    args = argparse.Namespace(
        input=str(input_dir),
        output=str(output_dir),
        year=2024,
        site="manaus",
        all_sites=False,
        include_precomputed=True,
        verbose=False,
    )

    with caplog.at_level(logging.INFO, logger="eto.compute_eto"):
        cmd_compute_eto(args)

    output_path = output_dir / daily_eto_filename("manaus")
    assert output_path.exists()
    output = pd.read_csv(output_path)
    assert REFERENCE_COLUMN in output.columns
    assert "et_makkink" in output.columns
    assert any("computed" in record.message for record in caplog.records)


def test_methods_config_lists_precomputed_only_columns() -> None:
    assert METHODS.precomputed_only_columns == {
        "et_thornthwaite",
        "et_thornthwaite_camargo",
        "et_hargreaves_samani_corr",
    }
