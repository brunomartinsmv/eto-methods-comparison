"""Petrolina is a temperature-humidity-wind sheet, not a Penman-Monteith site."""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd
import pytest

from scripts import cli
from scripts.cli import build_parser
from scripts.config import (
    DATA_RAW,
    clear_config_cache,
    load_sites_config,
    site_is_full_penman_monteith,
)
from scripts.io import read_inmet_limited_table, read_site_table
from scripts.quality import build_quality_report

RADIATION_COLUMNS = (
    "rad_global_mj_m2_d",
    "rad_net_mj_m2_d",
    "ra_extraterrestre_mj_m2_d",
)
LIMITED_COLUMNS = (
    "tmed_c",
    "tmax_c",
    "tmin_c",
    "rh_mean_pct",
    "rh_min_pct",
    "wind_mean_ms",
    "rain_mm",
    "pressure_hpa",
)


def test_petrolina_is_configured_outside_the_penman_monteith_sites() -> None:
    clear_config_cache()
    sites = load_sites_config()

    assert sites["petrolina"]["data_case"] == "temperature_humidity_wind"
    assert sites["petrolina"]["reader"]["format"] == "inmet_limited"
    assert sites["petrolina"]["station_code"] == "A307"
    assert site_is_full_penman_monteith(sites["manaus"])
    assert site_is_full_penman_monteith(sites["piracicaba"])
    assert not site_is_full_penman_monteith(sites["petrolina"])

    selected = cli._selected_sites(argparse.Namespace(site=None, all_sites=True))
    assert set(selected) == {"manaus", "piracicaba"}


def test_inmet_limited_reader_keeps_sheet_columns_and_skips_absent_radiation(tmp_path: Path) -> None:
    path = tmp_path / "station.xlsx"
    pd.DataFrame(
        [
            ["Nome: TESTE", None, None, None],
            ["Situacao: Pane", None, None, None],
            [None, None, None, None],
            [
                "Data Medicao",
                "TEMPERATURA MEDIA, DIARIA (AUT)(°C)",
                "UMIDADE RELATIVA DO AR, MEDIA DIARIA (AUT)(%)",
                "VENTO, VELOCIDADE MEDIA DIARIA (AUT)(m/s)",
            ],
            ["2024-01-01", 28.0, 40.0, 2.5],
        ]
    ).to_excel(path, sheet_name="Station", index=False, header=False)

    table = read_inmet_limited_table(path, "Station")

    assert table.station_status == "Pane"
    assert list(table.frame.columns) == ["date", "tmed_c", "rh_mean_pct", "wind_mean_ms"]
    assert set(RADIATION_COLUMNS).isdisjoint(table.frame.columns)


def test_inmet_limited_reader_requires_a_measurement_date_header(tmp_path: Path) -> None:
    path = tmp_path / "station.xlsx"
    pd.DataFrame([["Situacao: Pane"], ["sem cabecalho"]]).to_excel(
        path, sheet_name="Station", index=False, header=False
    )

    with pytest.raises(ValueError, match="Data Medicao"):
        read_inmet_limited_table(path, "Station")


def test_petrolina_sheet_is_temperature_humidity_wind_with_status_pane() -> None:
    workbook = DATA_RAW / "Evapo.xlsx"
    if not workbook.exists():
        pytest.skip("data/raw/Evapo.xlsx is not in this checkout")

    sites = load_sites_config()
    table = read_site_table(workbook, sites["petrolina"], year=2024)
    frame = table.frame
    first = frame.loc[frame["date"] == pd.Timestamp("2024-01-01")].iloc[0]

    assert table.station_status == "Pane"
    assert len(frame) == 366
    for column in LIMITED_COLUMNS:
        assert column in frame.columns
    assert set(RADIATION_COLUMNS).isdisjoint(frame.columns)
    assert first["tmed_c"] == pytest.approx(27.9)
    assert first["rh_mean_pct"] == pytest.approx(68.4)
    assert first["wind_mean_ms"] == pytest.approx(1.7)
    assert first["rain_mm"] == pytest.approx(11.4)
    assert first["pressure_hpa"] == pytest.approx(969.3)
    assert first["tmax_c"] == pytest.approx(33.6)
    assert first["tmin_c"] == pytest.approx(23.0)


def test_quality_report_labels_petrolina_station_status_and_omits_radiation(tmp_path: Path) -> None:
    workbook = DATA_RAW / "Evapo.xlsx"
    if not workbook.exists():
        pytest.skip("data/raw/Evapo.xlsx is not in this checkout")

    cli.cmd_validate_data(
        argparse.Namespace(
            input=str(workbook),
            output=str(tmp_path),
            year=2024,
            site="petrolina",
            all_sites=False,
            max_gap=7,
            use_calculated_results=False,
        )
    )

    report = pd.read_csv(tmp_path / "petrolina_data_quality.csv")
    station = report.loc[report["variable"] == "station_status"].iloc[0]
    assert station["stage"] == "station"
    assert station["status"] == "Pane"
    assert station["source_present"]
    assert set(report["station_status"]) == {"Pane"}
    assert set(RADIATION_COLUMNS).isdisjoint(report["variable"])
    assert {"tmed_c", "rh_mean_pct", "wind_mean_ms", "pressure_hpa", "rain_mm"} <= set(report["variable"])
    assert "computed_et0" not in set(report["stage"])
    assert "et_penman_monteith" not in set(report["variable"])


def test_quality_report_without_station_status_keeps_the_existing_columns() -> None:
    raw = pd.DataFrame(
        {"date": pd.to_datetime(["2024-01-01"]), "tmed_c": [20.0]}
    )
    report = build_quality_report(site="manaus", raw_df=raw, cleaned_df=raw, year=2024)
    assert "station_status" not in report.columns
    assert "station" not in set(report["stage"])


def test_clean_petrolina_does_not_invent_radiation(tmp_path: Path) -> None:
    workbook = DATA_RAW / "Evapo.xlsx"
    if not workbook.exists():
        pytest.skip("data/raw/Evapo.xlsx is not in this checkout")

    cli.cmd_clean(
        argparse.Namespace(
            input=str(workbook),
            output=str(tmp_path),
            year=2024,
            site="petrolina",
            all_sites=False,
            eto_source="precomputed",
            max_gap=7,
        )
    )

    cleaned = pd.read_csv(tmp_path / "petrolina_daily.csv")
    for column in ("tmed_c", "rh_mean_pct", "wind_mean_ms", "pressure_hpa", "rain_mm"):
        assert column in cleaned.columns
    assert set(RADIATION_COLUMNS).isdisjoint(cleaned.columns)
    assert not any(str(column).startswith("et_") for column in cleaned.columns)


def test_penman_monteith_commands_reject_petrolina(tmp_path: Path) -> None:
    metrics_args = build_parser().parse_args(
        ["metrics", "--site", "petrolina", "--input", str(tmp_path), "--output", str(tmp_path)]
    )
    with pytest.raises(ValueError, match="radiation-bearing"):
        cli.cmd_metrics(metrics_args)

    all_args = build_parser().parse_args(
        ["all", "--site", "petrolina", "--output", str(tmp_path)]
    )
    with pytest.raises(ValueError, match="radiation-bearing"):
        cli.cmd_all(all_args)

    assert not (tmp_path / "petrolina_daily.csv").exists()
    assert not (DATA_RAW.parent / "cleaned" / "petrolina_daily.csv").exists()
