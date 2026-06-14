from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from scripts import eto_methods
from scripts.fao56 import penman_monteith_fao56
from scripts.metrics import (
    classify_confidence,
    compute_metrics,
    confidence_c,
    mae,
    mbe,
    pearson_r,
    r2_score,
    rmse,
    willmott_d,
)

FIXTURE_DIR = Path(__file__).parent / "fixtures"
SYNTHETIC_WEATHER_FIXTURE = FIXTURE_DIR / "synthetic_weather_regression.csv"


def test_reference_fixture_drives_stable_daily_eto_regression_values() -> None:
    df = pd.read_csv(SYNTHETIC_WEATHER_FIXTURE)

    pm = penman_monteith_fao56(
        t_mean_c=df["t_mean_c"],
        rn_mj_m2_day=df["rn_mj_m2_day"],
        g_mj_m2_day=0.0,
        wind_2m_m_s=df["wind_2m_m_s"],
        saturation_vapor_pressure_kpa=df["saturation_vapor_pressure_kpa"],
        actual_vapor_pressure_kpa=df["actual_vapor_pressure_kpa"],
        delta_kpa_c=df["delta_kpa_c"],
        gamma_kpa_c=df["gamma_kpa_c"],
    )
    hs = eto_methods.hargreaves_samani(
        t_min_c=df["t_min_c"],
        t_max_c=df["t_max_c"],
        t_mean_c=df["t_mean_c"],
        ra_mj_m2_day=df["ra_mj_m2_day"],
    )
    pt = eto_methods.priestley_taylor(
        delta_kpa_c=df["delta_kpa_c"],
        gamma_kpa_c=df["gamma_kpa_c"],
        rn_mj_m2_day=df["rn_mj_m2_day"],
    )

    assert np.allclose(
        pm.to_numpy(),
        np.array([2.5118645556, 3.8329337585, 5.5391557955]),
        rtol=1e-10,
        atol=1e-10,
    )
    assert np.allclose(
        hs.to_numpy(),
        np.array([3.3664704462, 4.4470658981, 5.6760947912]),
        rtol=1e-10,
        atol=1e-10,
    )
    assert np.allclose(
        pt.to_numpy(),
        np.array([2.8188311688, 3.8027317510, 4.8471304107]),
        rtol=1e-10,
        atol=1e-10,
    )
    assert np.all(np.isfinite(pm))
    assert np.all(np.diff(pm) > 0)
    assert np.all(pm > 0)


def test_metric_regression_values_and_classification_are_stable() -> None:
    observed = np.array([1.0, 2.0, 3.0, 4.0])
    estimated = np.array([1.1, 1.9, 3.2, 3.8])

    assert np.isclose(rmse(observed, estimated), 0.158113883008, rtol=1e-10, atol=1e-12)
    assert np.isclose(mae(observed, estimated), 0.15, rtol=1e-10, atol=1e-12)
    assert np.isclose(mbe(observed, estimated), 0.0, rtol=0.0, atol=1e-12)
    assert np.isclose(pearson_r(observed, estimated), 0.990847000186, rtol=1e-10, atol=1e-12)
    assert np.isclose(r2_score(observed, estimated), 0.981777777778, rtol=1e-10, atol=1e-12)
    assert np.isclose(willmott_d(observed, estimated), 0.994708994709, rtol=1e-10, atol=1e-12)
    assert np.isclose(confidence_c(observed, estimated), 0.985604423466, rtol=1e-10, atol=1e-12)
    assert classify_confidence(confidence_c(observed, estimated)) == "Excellent"


def test_compute_metrics_table_preserves_metric_regression_contract() -> None:
    df = pd.DataFrame(
        {
            "pm": [1.0, 2.0, 3.0, 4.0],
            "method": [1.1, 1.9, 3.2, 3.8],
            "method_with_nan": [1.1, np.nan, 3.2, 3.8],
        }
    )

    result = compute_metrics(df, "pm", ["method", "method_with_nan"])

    method = result.loc[result["method"] == "method"].iloc[0]
    assert np.isclose(method["rmse"], 0.158113883008, rtol=1e-10, atol=1e-12)
    assert np.isclose(method["mae"], 0.15, rtol=1e-10, atol=1e-12)
    assert np.isclose(method["mbe"], 0.0, rtol=0.0, atol=1e-12)
    assert np.isclose(method["r2"], 0.981777777778, rtol=1e-10, atol=1e-12)
    assert np.isclose(method["r"], 0.990847000186, rtol=1e-10, atol=1e-12)
    assert np.isclose(method["willmott_d"], 0.994708994709, rtol=1e-10, atol=1e-12)
    assert np.isclose(method["c"], 0.985604423466, rtol=1e-10, atol=1e-12)
    assert method["classification"] == "Excellent"

    method_with_nan = result.loc[result["method"] == "method_with_nan"].iloc[0]
    assert method_with_nan["classification"] == "Excellent"
    assert np.isfinite(method_with_nan["rmse"])
