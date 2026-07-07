import argparse
from pathlib import Path

import pandas as pd

from scripts.cli import cmd_aggregate, cmd_metrics
from scripts.eto_io import eto_input_path, read_eto_frame
from scripts.naming import daily_eto_filename


def test_eto_input_path_prefers_computed_daily_eto(tmp_path: Path) -> None:
    cleaned_dir = tmp_path / "cleaned"
    results_dir = tmp_path / "results"
    cleaned_dir.mkdir()
    results_dir.mkdir()

    cleaned_path = cleaned_dir / "manaus_daily.csv"
    computed_path = results_dir / daily_eto_filename("manaus")
    cleaned_path.write_text("date,et_penman_monteith\n2024-01-01,1.0\n", encoding="utf-8")
    computed_path.write_text("date,et_penman_monteith\n2024-01-01,2.0\n", encoding="utf-8")

    assert eto_input_path("manaus", cleaned_dir=cleaned_dir, results_dir=results_dir) == computed_path


def test_eto_input_path_falls_back_to_cleaned_daily_csv(tmp_path: Path) -> None:
    cleaned_dir = tmp_path / "cleaned"
    results_dir = tmp_path / "results"
    cleaned_dir.mkdir()
    results_dir.mkdir()

    cleaned_path = cleaned_dir / "manaus_daily.csv"
    cleaned_path.write_text("date,et_penman_monteith\n2024-01-01,1.0\n", encoding="utf-8")

    assert eto_input_path("manaus", cleaned_dir=cleaned_dir, results_dir=results_dir) == cleaned_path


def test_read_eto_frame_loads_preferred_source(tmp_path: Path) -> None:
    cleaned_dir = tmp_path / "cleaned"
    results_dir = tmp_path / "results"
    cleaned_dir.mkdir()
    results_dir.mkdir()

    pd.DataFrame(
        {
            "date": ["2024-01-01"],
            "et_penman_monteith": [1.0],
            "et_camargo": [10.0],
        }
    ).to_csv(cleaned_dir / "manaus_daily.csv", index=False)
    pd.DataFrame(
        {
            "date": ["2024-01-01"],
            "et_penman_monteith": [1.0],
            "et_camargo": [2.0],
        }
    ).to_csv(results_dir / daily_eto_filename("manaus"), index=False)

    frame = read_eto_frame("manaus", cleaned_dir=cleaned_dir, results_dir=results_dir)

    assert frame.loc[0, "et_camargo"] == 2.0


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

    monkeypatch.setattr("scripts.eto_io.OUTPUTS_RESULTS", results_dir)

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


def test_aggregate_prefers_computed_daily_eto_when_available(tmp_path: Path, monkeypatch) -> None:
    cleaned_dir = tmp_path / "cleaned"
    results_dir = tmp_path / "results"
    output_dir = tmp_path / "out"
    cleaned_dir.mkdir()
    results_dir.mkdir()

    pd.DataFrame(
        {
            "date": ["2024-01-01", "2024-01-02"],
            "et_penman_monteith": [1.0, 3.0],
            "et_camargo": [10.0, 30.0],
        }
    ).to_csv(cleaned_dir / "manaus_daily.csv", index=False)
    pd.DataFrame(
        {
            "date": ["2024-01-01", "2024-01-02"],
            "et_penman_monteith": [2.0, 4.0],
            "et_camargo": [20.0, 40.0],
        }
    ).to_csv(results_dir / daily_eto_filename("manaus"), index=False)

    monkeypatch.setattr("scripts.eto_io.OUTPUTS_RESULTS", results_dir)

    args = argparse.Namespace(
        input=str(cleaned_dir),
        output=str(output_dir),
        year=2024,
        site="manaus",
        all_sites=False,
    )
    cmd_aggregate(args)

    monthly = pd.read_csv(output_dir / "manaus_monthly_totals.csv")
    assert monthly.loc[0, "et_camargo"] == 60.0
