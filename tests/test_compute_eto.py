from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

from scripts import cli, compute_eto
from scripts.cli import cmd_compute_eto, cmd_metrics
from scripts.config import REFERENCE_COLUMN
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

    assert "date" in result.columns
    assert REFERENCE_COLUMN in result.columns
    assert "et_hargreaves_samani" in result.columns
    assert "et_makkink" in result.columns
    assert "et_turc" in result.columns
    assert "et_hicks_hess" in result.columns
    assert np.isfinite(result[REFERENCE_COLUMN]).all()
    assert np.isfinite(result["et_hargreaves_samani"]).all()


def test_compute_daily_eto_can_keep_precomputed_columns_for_validation() -> None:
    df = _weather_frame()
    df["et_penman_monteith"] = [4.0, 4.2]

    result = compute_eto.compute_daily_eto(
        df,
        site_meta={"alt_m": 120.0},
        include_precomputed=True,
    )

    assert "precomputed_et_penman_monteith" in result.columns
    assert result["precomputed_et_penman_monteith"].tolist() == [4.0, 4.2]
    assert result[REFERENCE_COLUMN].tolist() != [4.0, 4.2]


def test_compute_eto_cli_writes_daily_eto_file(tmp_path: Path) -> None:
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
    )
    cmd_compute_eto(args)

    output_path = output_dir / daily_eto_filename("manaus")
    assert output_path.exists()
    output = pd.read_csv(output_path)
    assert REFERENCE_COLUMN in output.columns
    assert "et_makkink" in output.columns


def test_metrics_prefers_computed_daily_eto_when_available(tmp_path: Path, monkeypatch) -> None:
    cleaned_dir = tmp_path / "cleaned"
    results_dir = tmp_path / "results"
    tables_dir = tmp_path / "tables"
    cleaned_dir.mkdir()
    results_dir.mkdir()

    pd.DataFrame(
        {
            "date": ["2024-01-01", "2024-01-02"],
            "et_penman_monteith": [1.0, 1.0],
            "et_camargo": [10.0, 10.0],
        }
    ).to_csv(cleaned_dir / "manaus_daily.csv", index=False)
    pd.DataFrame(
        {
            "date": ["2024-01-01", "2024-01-02"],
            "et_penman_monteith": [1.0, 1.0],
            "et_camargo": [2.0, 2.0],
        }
    ).to_csv(results_dir / daily_eto_filename("manaus"), index=False)

    monkeypatch.setattr(cli, "OUTPUTS_RESULTS", results_dir)

    args = argparse.Namespace(
        input=str(cleaned_dir),
        output=str(tables_dir),
        year=2024,
        site="manaus",
        all_sites=False,
    )
    cmd_metrics(args)

    metrics = pd.read_csv(tables_dir / "manaus_daily_metrics.csv")
    camargo = metrics.loc[metrics["method"] == "et_camargo"].iloc[0]
    assert camargo["rmse"] == 1.0
