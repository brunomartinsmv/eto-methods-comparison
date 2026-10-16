"""Regression tests for FAO-56 PMT and the Valiantzas temperature-radiation equation."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from scripts import eto_methods
from scripts.cli import _method_cols_present
from scripts.compute_eto import compute_daily_eto
from scripts.config import load_methods_config
from scripts.fao56 import fao56_pmt
from scripts.summary import build_rankings, build_summary


def test_fao56_pmt_matches_fao56_example_20() -> None:
    """Allen et al. (1998), FAO-56 Example 20, Lyon, July, temperature only.

    Published result with kRs = 0.16 and u2 = 2 m s-1 is 4.56 mm day-1.
    The same example reports 4.2 mm day-1 at 1 m s-1 and 4.8 mm day-1 at 3 m s-1.
    """
    published = dict(t_min_c=14.8, t_max_c=26.6, ra_mj_m2_day=40.55, altitude_m=200.0)

    default = fao56_pmt(**published)
    slower_wind = fao56_pmt(**published, wind_2m_m_s=1.0)
    faster_wind = fao56_pmt(**published, wind_2m_m_s=3.0)
    coastal = fao56_pmt(**published, k_rs=0.19)

    assert round(default, 2) == 4.56
    assert round(slower_wind, 1) == 4.2
    assert round(faster_wind, 1) == 4.8
    assert round(coastal, 2) != 4.56


def test_valiantzas_temperature_radiation_matches_published_equation() -> None:
    """Valiantzas (2013a), J. Irrig. Drain. Eng. 139(1):1-8, temperature and Rs form.

    ET0 = 0.0393 Rs sqrt(T + 9.5) - 0.19 Rs^0.6 |phi|^0.15
    + 0.0061 (T + 20) (1.12 T - Tmin - 2)^0.7,
    with Rs in MJ m-2 day-1 and phi in radians. The expected value is that
    expression at Rs = 15, T = 25, Tmin = 12, latitude = 40 degrees.
    """
    result = eto_methods.valiantzas(
        t_mean_c=25.0,
        t_min_c=12.0,
        rs_mj_m2_day=15.0,
        latitude_deg=40.0,
    )
    southern = eto_methods.valiantzas(
        t_mean_c=25.0,
        t_min_c=12.0,
        rs_mj_m2_day=15.0,
        latitude_deg=-40.0,
    )

    assert np.isclose(result, 4.289550556627, rtol=1e-12, atol=1e-12)
    assert np.isclose(southern, result, rtol=0.0, atol=0.0)


def test_compute_daily_eto_adds_pmt_and_valiantzas_outside_default_columns() -> None:
    weather = pd.DataFrame(
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
    result = compute_daily_eto(weather, site_meta={"alt_m": 546.0, "lat": -22.7083})

    assert "et_fao56_pmt" in result.report.computed
    assert "et_valiantzas" in result.report.computed
    assert np.isfinite(result.frame["et_fao56_pmt"]).all()
    assert np.isfinite(result.frame["et_valiantzas"]).all()

    present = _method_cols_present(result.frame)
    assert "et_penman_monteith" in present
    assert "et_fao56_pmt" not in present
    assert "et_valiantzas" not in present


def test_default_ranking_omits_pmt_and_valiantzas_even_if_metrics_include_them(tmp_path: Path) -> None:
    tables_dir = tmp_path / "tables"
    tables_dir.mkdir()
    pd.DataFrame(
        {
            "method": ["et_turc", "et_fao56_pmt", "et_valiantzas"],
            "rmse": [1.0, 0.01, 0.02],
            "mae": [0.8, 0.01, 0.02],
            "mbe": [0.1, 0.0, 0.0],
            "r": [0.9, 0.99, 0.99],
            "r2": [0.8, 0.99, 0.99],
            "willmott_d": [0.85, 0.99, 0.99],
            "c": [0.7, 0.99, 0.98],
            "classification": ["Good", "Excellent", "Excellent"],
        }
    ).to_csv(tables_dir / "manaus_daily_metrics.csv", index=False)

    rankings = build_rankings(tables_dir, sites=["manaus"])
    summary = build_summary(tables_dir, sites=["manaus"])

    assert rankings["method"].tolist() == ["et_turc"]
    assert summary["best_method"].tolist() == ["et_turc"]
    methods = load_methods_config()
    assert methods.status_by_name["FAO-56 PMT"] == "computed"
    assert methods.status_by_name["Valiantzas"] == "computed"
