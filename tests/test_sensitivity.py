from __future__ import annotations

import pandas as pd
import pytest

from scripts.sensitivity import SensitivityVariable, run_oat_sensitivity


def _sample_weather() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "date": pd.to_datetime(["2024-01-01", "2024-01-02", "2024-01-03"]),
            "tmed_c": [27.0, 28.0, 29.0],
            "tmax_c": [31.0, 32.0, 33.0],
            "tmin_c": [23.0, 24.0, 25.0],
            "rh_mean_pct": [80.0, 78.0, 76.0],
            "rh_max_pct": [94.0, 92.0, 90.0],
            "rh_min_pct": [66.0, 64.0, 62.0],
            "wind_mean_ms": [1.6, 1.8, 2.0],
            "rad_global_mj_m2_d": [18.0, 19.0, 20.0],
            "rad_net_mj_m2_d": [10.0, 11.0, 12.0],
        }
    )


def test_oat_sensitivity_summarizes_perturbation_response() -> None:
    result = run_oat_sensitivity(
        _sample_weather(),
        site_meta={"alt_m": 80},
        method="penman_monteith",
        perturbations=(-10, 0, 10),
        variables=[SensitivityVariable("tmed_c", "temperatura_media")],
    )

    assert result["perturbation_pct"].tolist() == [-10, 0, 10]
    assert set(result.columns) == {
        "method",
        "eto_column",
        "variable",
        "column",
        "perturbation_pct",
        "baseline_mean_eto_mm_d",
        "perturbed_mean_eto_mm_d",
        "delta_mean_eto_mm_d",
        "relative_delta_pct",
        "n",
        "status",
    }
    assert (result["status"] == "ok").all()
    assert result.loc[result["perturbation_pct"] == 0, "delta_mean_eto_mm_d"].iloc[0] == pytest.approx(0)


def test_penman_humidity_sensitivity_uses_min_max_rh_when_available() -> None:
    result = run_oat_sensitivity(
        _sample_weather(),
        site_meta={"alt_m": 80},
        method="penman_monteith",
        perturbations=(-10, 0, 10),
        variables=[SensitivityVariable("rh_mean_pct", "umidade_relativa")],
    )

    assert result["column"].unique().tolist() == ["rh_min_pct,rh_max_pct"]
    assert result.loc[result["perturbation_pct"] == 0, "delta_mean_eto_mm_d"].iloc[0] == pytest.approx(0)
    assert result.loc[result["perturbation_pct"] == -10, "delta_mean_eto_mm_d"].iloc[0] != pytest.approx(0)
    assert result.loc[result["perturbation_pct"] == 10, "delta_mean_eto_mm_d"].iloc[0] != pytest.approx(0)


def test_oat_sensitivity_reports_missing_candidate_variable() -> None:
    with pytest.warns(UserWarning, match="column not found"):
        result = run_oat_sensitivity(
            _sample_weather(),
            site_meta={"alt_m": 80},
            method="turc",
            perturbations=(0,),
            variables=[
                SensitivityVariable("tmed_c", "temperatura_media"),
                SensitivityVariable("not_available", "ausente"),
            ],
        )

    missing = result[result["status"] == "missing_column"].iloc[0]
    assert missing["column"] == "not_available"
    assert pd.isna(missing["perturbation_pct"])


def test_oat_sensitivity_requires_method_inputs() -> None:
    df = _sample_weather().drop(columns=["rad_net_mj_m2_d"])

    with pytest.raises(ValueError, match="missing required column"):
        run_oat_sensitivity(df, site_meta={"alt_m": 80}, method="penman_monteith")
