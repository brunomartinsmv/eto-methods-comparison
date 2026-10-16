"""FAO-56 missing-input Penman-Monteith scenarios."""

from __future__ import annotations

import math
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from scripts import compute_eto, derived_meteo, limited_data
from scripts.cli import build_parser, cmd_limited_data
from scripts.config import SITES
from scripts.derived_meteo import (
    actual_vapor_pressure_kpa,
    net_radiation_from_solar_mj_m2_day,
    solar_radiation_from_temperature_mj_m2_day,
)
from scripts.fao56 import penman_monteith_fao56
from scripts.limited_data import SCENARIO_ORDER, resolve_limited_data_settings
from scripts.naming import limited_data_metrics_filename


def _weather() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "date": pd.to_datetime(["2024-01-01", "2024-01-02", "2024-01-03"]),
            "tmed_c": [25.0, 26.0, 24.0],
            "tmin_c": [18.0, 19.0, 17.0],
            "tmax_c": [32.0, 33.0, 31.0],
            "rh_mean_pct": [70.0, 60.0, 80.0],
            "wind_mean_ms": [3.0, 4.0, 2.2],
            "rad_global_mj_m2_d": [18.0, 20.0, 16.0],
            "rad_net_mj_m2_d": [10.0, 11.0, 9.0],
            "ra_extraterrestre_mj_m2_d": [32.0, 32.5, 31.5],
        }
    )


def _meta() -> dict:
    return {"alt_m": 100.0, "wind_height_m": 10.0}


def test_fao56_example_15_solar_radiation_from_temperature() -> None:
    """Lyon, July: Rs = 0.16 * sqrt(Tmax - Tmin) * Ra = 22.3 MJ m-2 day-1."""
    rs = derived_meteo.solar_radiation_from_temperature_mj_m2_day(
        14.8,
        26.6,
        40.6,
        k_rs=0.16,
        altitude_m=200.0,
    )
    exact = 0.16 * math.sqrt(26.6 - 14.8) * 40.6
    assert float(rs) == pytest.approx(exact)
    assert float(rs) == pytest.approx(22.3, abs=0.05)


def test_fao56_example_11_and_12_net_radiation_near_sea_level() -> None:
    """Rio de Janeiro, May: published Rnl = 3.5 and Rn = 7.6 MJ m-2 day-1."""
    rso = derived_meteo.clear_sky_radiation_mj_m2_day(25.1, 0.0)
    assert float(rso) == pytest.approx(0.75 * 25.1)
    rnl = derived_meteo.net_longwave_radiation_mj_m2_day(19.1, 25.1, 2.1, 14.5, rso)
    rn = derived_meteo.net_radiation_from_solar_mj_m2_day(
        19.1,
        25.1,
        2.1,
        14.5,
        25.1,
        altitude_m=0.0,
    )
    assert float(rnl) == pytest.approx(3.5, abs=0.05)
    assert float(rn) == pytest.approx(7.6, abs=0.1)


def test_fao56_example_16_coastal_temperature_net_radiation() -> None:
    """Bangkok, April: coastal kRs = 0.19 and published Rn = 13.9 MJ m-2 day-1."""
    rs = derived_meteo.solar_radiation_from_temperature_mj_m2_day(
        25.6,
        34.8,
        38.1,
        k_rs=0.19,
        altitude_m=2.0,
    )
    rn = derived_meteo.net_radiation_from_solar_mj_m2_day(
        25.6,
        34.8,
        2.85,
        rs,
        38.1,
        altitude_m=2.0,
    )
    assert float(rs) == pytest.approx(21.9, abs=0.1)
    assert float(rn) == pytest.approx(13.9, abs=0.15)


def test_estimated_solar_radiation_does_not_exceed_clear_sky() -> None:
    ra = 30.0
    rs = derived_meteo.solar_radiation_from_temperature_mj_m2_day(
        0.0,
        40.0,
        ra,
        k_rs=0.19,
        altitude_m=0.0,
    )
    rso = derived_meteo.clear_sky_radiation_mj_m2_day(ra, 0.0)
    assert float(rs) == pytest.approx(float(rso))
    assert float(rs) < 0.19 * math.sqrt(40.0) * ra


def test_longwave_ratio_is_capped_at_one() -> None:
    capped = derived_meteo.net_longwave_radiation_mj_m2_day(20.0, 30.0, 1.5, 40.0, 20.0)
    at_clear_sky = derived_meteo.net_longwave_radiation_mj_m2_day(20.0, 30.0, 1.5, 20.0, 20.0)
    assert float(capped) == pytest.approx(float(at_clear_sky))


def test_dewpoint_substitute_is_saturation_vapor_pressure_at_tmin() -> None:
    tmin = pd.Series([18.0, 19.0])
    ea = derived_meteo.actual_vapor_pressure_from_tmin_kpa(tmin)
    assert ea.tolist() == pytest.approx(derived_meteo.saturation_vapor_pressure_kpa(tmin).tolist())


def test_full_penman_monteith_matches_compute_eto() -> None:
    df = _weather()
    meta = _meta()
    settings = resolve_limited_data_settings(meta)
    series = limited_data.limited_data_series(df, site_meta=meta, settings=settings)
    computed = compute_eto.compute_daily_eto(df, site_meta=meta).frame["et_penman_monteith"]
    assert np.allclose(series["pm_full"], computed)


def test_each_replaced_input_is_isolated() -> None:
    df = _weather()
    meta = _meta()
    settings = resolve_limited_data_settings(meta)
    base = limited_data.limited_data_series(df, site_meta=meta, settings=settings)

    wind_changed = df.copy()
    wind_changed["wind_mean_ms"] = [8.0, 9.0, 7.5]
    after_wind = limited_data.limited_data_series(wind_changed, site_meta=meta, settings=settings)
    assert np.allclose(base["pm_wind_replaced"], after_wind["pm_wind_replaced"])
    assert np.allclose(base["pm_pmt"], after_wind["pm_pmt"])
    assert not np.allclose(base["pm_full"], after_wind["pm_full"])
    assert not np.allclose(base["pm_radiation_replaced"], after_wind["pm_radiation_replaced"])
    assert not np.allclose(base["pm_humidity_replaced"], after_wind["pm_humidity_replaced"])

    humidity_changed = df.copy()
    humidity_changed["rh_mean_pct"] = [30.0, 35.0, 40.0]
    after_humidity = limited_data.limited_data_series(
        humidity_changed, site_meta=meta, settings=settings
    )
    assert np.allclose(base["pm_humidity_replaced"], after_humidity["pm_humidity_replaced"])
    assert np.allclose(base["pm_pmt"], after_humidity["pm_pmt"])
    assert not np.allclose(base["pm_full"], after_humidity["pm_full"])
    assert not np.allclose(base["pm_radiation_replaced"], after_humidity["pm_radiation_replaced"])

    radiation_changed = df.copy()
    radiation_changed["rad_net_mj_m2_d"] = [1.0, 1.5, 2.0]
    after_radiation = limited_data.limited_data_series(
        radiation_changed, site_meta=meta, settings=settings
    )
    assert not np.allclose(base["pm_full"], after_radiation["pm_full"])
    assert np.allclose(base["pm_radiation_replaced"], after_radiation["pm_radiation_replaced"])
    assert np.allclose(base["pm_pmt"], after_radiation["pm_pmt"])
    assert not np.allclose(base["pm_humidity_replaced"], after_radiation["pm_humidity_replaced"])


def test_substitutes_match_explicit_penman_monteith_calls() -> None:
    df = _weather()
    meta = _meta()
    settings = resolve_limited_data_settings(
        {**meta, "regional_wind_2m_ms": 1.4, "radiation_setting": "coastal"}
    )
    assert settings.wind_source == "regional"
    assert settings.wind_2m_m_s == pytest.approx(1.4)
    assert settings.k_rs == pytest.approx(0.19)
    assert settings.k_rs_source == "fao56_coastal"

    series = limited_data.limited_data_series(df, site_meta=meta, settings=settings)
    measured_ea = actual_vapor_pressure_kpa(df)
    tmin_ea = derived_meteo.actual_vapor_pressure_from_tmin_kpa(df["tmin_c"])
    estimated_rs = solar_radiation_from_temperature_mj_m2_day(
        df["tmin_c"],
        df["tmax_c"],
        df["ra_extraterrestre_mj_m2_d"],
        k_rs=0.19,
        altitude_m=100.0,
    )
    rn_measured_ea = net_radiation_from_solar_mj_m2_day(
        df["tmin_c"],
        df["tmax_c"],
        measured_ea,
        estimated_rs,
        df["ra_extraterrestre_mj_m2_d"],
        altitude_m=100.0,
    )
    rn_tmin_ea = net_radiation_from_solar_mj_m2_day(
        df["tmin_c"],
        df["tmax_c"],
        tmin_ea,
        estimated_rs,
        df["ra_extraterrestre_mj_m2_d"],
        altitude_m=100.0,
    )
    gamma = derived_meteo.psychrometric_constant_kpa_c(100.0)
    delta = derived_meteo.vapor_pressure_slope_kpa_c(df["tmed_c"])
    es = derived_meteo.saturation_vapor_pressure_kpa(df["tmed_c"])
    measured_wind = derived_meteo.wind_speed_at_2m(df["wind_mean_ms"], measurement_height_m=10.0)

    def pm(wind, ea, rn):
        return penman_monteith_fao56(
            t_mean_c=df["tmed_c"],
            rn_mj_m2_day=rn,
            g_mj_m2_day=0.0,
            wind_2m_m_s=wind,
            saturation_vapor_pressure_kpa=es,
            actual_vapor_pressure_kpa=ea,
            delta_kpa_c=delta,
            gamma_kpa_c=gamma,
        )

    assert np.allclose(series["pm_wind_replaced"], pm(1.4, measured_ea, df["rad_net_mj_m2_d"]))
    assert np.allclose(
        series["pm_humidity_replaced"],
        pm(measured_wind, tmin_ea, df["rad_net_mj_m2_d"]),
    )
    assert np.allclose(
        series["pm_radiation_replaced"],
        pm(measured_wind, measured_ea, rn_measured_ea),
    )
    assert np.allclose(series["pm_pmt"], pm(1.4, tmin_ea, rn_tmin_ea))


def test_wind_substitute_is_floored_at_fao56_minimum() -> None:
    settings = resolve_limited_data_settings({}, wind_2m_m_s=0.2)
    assert settings.wind_2m_m_s == pytest.approx(0.5)
    assert settings.wind_source == "override"


def test_table_uses_pipeline_reference_not_the_spreadsheet_column(tmp_path: Path) -> None:
    df = _weather()
    df["et_penman_monteith"] = 50.0
    meta = _meta()
    settings = resolve_limited_data_settings(meta)
    full = limited_data.limited_data_series(df, site_meta=meta, settings=settings)["pm_full"]

    results = tmp_path / "results"
    results.mkdir()
    pd.DataFrame(
        {"date": df["date"], "et_penman_monteith": full.to_numpy() + 1.0}
    ).to_csv(results / "demo_daily_eto.csv", index=False)

    table = limited_data.limited_data_metrics_table(
        df,
        site="demo",
        site_meta=meta,
        settings=settings,
        results_dir=results,
    )

    assert table["scenario"].tolist() == list(SCENARIO_ORDER)
    assert set(table["equation"]) >= {"penman_monteith", "hargreaves_samani", "turc"}
    assert table["n"].nunique() == 1
    assert int(table["n"].iloc[0]) == len(df)
    assert table["comparison_days"].eq("common_finite").all()
    assert table["reference"].eq("et_penman_monteith").all()
    assert table["reference_source"].eq("pipeline_daily_eto").all()
    full_row = table.loc[table["scenario"] == "pm_full"].iloc[0]
    assert full_row["mbe"] == pytest.approx(-1.0)
    assert full_row["rmse"] == pytest.approx(1.0)


def test_row_order_stays_the_scenario_list_when_a_later_row_has_lower_error() -> None:
    df = _weather()
    df["wind_mean_ms"] = [8.0, 9.0, 7.0]
    meta = _meta()
    settings = resolve_limited_data_settings(meta)
    estimated_rn = net_radiation_from_solar_mj_m2_day(
        df["tmin_c"],
        df["tmax_c"],
        actual_vapor_pressure_kpa(df),
        solar_radiation_from_temperature_mj_m2_day(
            df["tmin_c"],
            df["tmax_c"],
            df["ra_extraterrestre_mj_m2_d"],
            k_rs=settings.k_rs,
            altitude_m=100.0,
        ),
        df["ra_extraterrestre_mj_m2_d"],
        altitude_m=100.0,
    )
    df["rad_net_mj_m2_d"] = estimated_rn
    table = limited_data.limited_data_metrics_table(
        df,
        site="demo",
        site_meta=meta,
        settings=settings,
        results_dir=None,
    )

    assert table["scenario"].tolist() == list(SCENARIO_ORDER)
    wind_rmse = float(table.loc[table["scenario"] == "pm_wind_replaced", "rmse"].iloc[0])
    radiation_rmse = float(table.loc[table["scenario"] == "pm_radiation_replaced", "rmse"].iloc[0])
    assert radiation_rmse == pytest.approx(0.0, abs=1e-8)
    assert wind_rmse > radiation_rmse
    assert table["scenario"].tolist().index("pm_wind_replaced") < table["scenario"].tolist().index(
        "pm_radiation_replaced"
    )
    radiation_row = table.loc[table["scenario"] == "pm_radiation_replaced"].iloc[0]
    assert radiation_row["k_rs"] == pytest.approx(0.16)
    assert radiation_row["k_rs_source"] == "fao56_interior"
    wind_row = table.loc[table["scenario"] == "pm_wind_replaced"].iloc[0]
    assert wind_row["wind_source"] == "fao56_default"
    assert wind_row["substitute_wind_2m_m_s"] == pytest.approx(2.0)


def test_recomputed_reference_matches_full_scenario_when_pipeline_file_is_absent() -> None:
    df = _weather()
    df["et_penman_monteith"] = 50.0
    table = limited_data.limited_data_metrics_table(
        df,
        site="demo",
        site_meta=_meta(),
        results_dir=None,
    )
    full_row = table.loc[table["scenario"] == "pm_full"].iloc[0]
    assert full_row["reference_source"] == "recomputed_penman_monteith"
    assert full_row["rmse"] == pytest.approx(0.0, abs=1e-12)
    assert full_row["mbe"] == pytest.approx(0.0, abs=1e-12)


def test_common_day_mask_drops_a_day_missing_from_any_series() -> None:
    df = _weather()
    df.loc[0, "wind_mean_ms"] = np.nan
    table = limited_data.limited_data_metrics_table(
        df,
        site="demo",
        site_meta=_meta(),
        results_dir=None,
    )
    assert table["n"].nunique() == 1
    assert int(table["n"].iloc[0]) == len(df) - 1


def test_missing_results_file_is_required_only_when_requested(tmp_path: Path) -> None:
    with pytest.raises(ValueError, match="not found"):
        limited_data.pipeline_reference(
            _weather(),
            site="demo",
            site_meta=_meta(),
            settings=resolve_limited_data_settings(_meta()),
            results_dir=tmp_path,
            require_results_file=True,
        )


def test_limited_data_command_writes_site_table(tmp_path: Path) -> None:
    cleaned = tmp_path / "cleaned"
    results = tmp_path / "results"
    tables = tmp_path / "tables"
    cleaned.mkdir()
    results.mkdir()
    df = _weather()
    meta = SITES["manaus"]
    settings = resolve_limited_data_settings(meta)
    full = limited_data.limited_data_series(df, site_meta=meta, settings=settings)["pm_full"]
    df.to_csv(cleaned / "manaus_daily.csv", index=False)
    pd.DataFrame({"date": df["date"], "et_penman_monteith": full}).to_csv(
        results / "manaus_daily_eto.csv",
        index=False,
    )

    args = build_parser().parse_args(
        [
            "limited-data",
            "--site",
            "manaus",
            "--input",
            str(cleaned),
            "--results-input",
            str(results),
            "--output",
            str(tables),
        ]
    )
    assert args.k_rs is None
    assert args.wind_2m is None
    cmd_limited_data(args)

    written = pd.read_csv(tables / limited_data_metrics_filename("manaus"))
    assert written["scenario"].tolist() == list(SCENARIO_ORDER)
    assert written["n"].nunique() == 1
    full_row = written.loc[written["scenario"] == "pm_full"].iloc[0]
    assert full_row["rmse"] == pytest.approx(0.0, abs=1e-12)
    assert full_row["reference_source"] == "pipeline_daily_eto"
    assert "hargreaves_samani" in written["scenario"].tolist()
    assert "turc" in written["scenario"].tolist()
