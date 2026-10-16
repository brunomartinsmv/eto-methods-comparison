from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd
import pytest

from scripts.cli import cmd_sensitivity
from scripts.compute_eto import compute_daily_eto
from scripts.sensitivity import (
    SensitivityVariable,
    default_perturbations,
    default_relative_perturbation_pct,
    run_oat_sensitivity,
    run_penman_monteith_relative_sensitivity,
)


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


def test_oat_perturbation_range_stays_at_plus_minus_50() -> None:
    perturbations = default_perturbations()
    assert perturbations[0] == -50
    assert perturbations[-1] == 50
    assert 10 in perturbations
    assert default_relative_perturbation_pct() == pytest.approx(1)


def test_relative_sensitivity_baseline_matches_pipeline_penman_monteith() -> None:
    df = _sample_weather()
    meta = {"alt_m": 80, "wind_height_m": 10.0}
    result = run_penman_monteith_relative_sensitivity(df, site_meta=meta)
    expected = float(
        pd.to_numeric(
            compute_daily_eto(df, site_meta=meta).frame["et_penman_monteith"],
            errors="coerce",
        ).mean()
    )
    annual = result[result["period_type"] == "annual"]
    assert set(annual["variable"]) == {
        "temperature",
        "vapor_pressure_deficit",
        "wind",
        "radiation",
    }
    assert annual["baseline_mean_eto_mm_d"].tolist() == pytest.approx([expected] * 4)
    assert annual["perturbation_pct"].tolist() == pytest.approx([1] * 4)
    assert "site" not in result.columns


def test_relative_sensitivity_radiation_and_vpd_limits() -> None:
    calm = _sample_weather()
    calm["wind_mean_ms"] = 0.0
    calm_result = run_penman_monteith_relative_sensitivity(
        calm, site_meta={"alt_m": 80, "wind_height_m": 2.0}
    )
    calm_annual = calm_result[calm_result["period_type"] == "annual"].set_index("variable")
    assert calm_annual.loc["radiation", "sensitivity_coefficient"] == pytest.approx(1.0, abs=1e-6)
    assert calm_annual.loc["vapor_pressure_deficit", "sensitivity_coefficient"] == pytest.approx(
        0.0, abs=1e-6
    )
    assert calm_annual.loc["wind", "sensitivity_coefficient"] == pytest.approx(0.0, abs=1e-6)

    dark = _sample_weather()
    dark["rad_net_mj_m2_d"] = 0.0
    dark_result = run_penman_monteith_relative_sensitivity(
        dark, site_meta={"alt_m": 80, "wind_height_m": 2.0}
    )
    dark_annual = dark_result[dark_result["period_type"] == "annual"].set_index("variable")
    assert dark_annual.loc["vapor_pressure_deficit", "sensitivity_coefficient"] == pytest.approx(
        1.0, abs=1e-6
    )
    assert dark_annual.loc["radiation", "sensitivity_coefficient"] == pytest.approx(0.0, abs=1e-6)


def test_relative_sensitivity_is_unweighted_mean_of_daily_coefficients() -> None:
    meta = {"alt_m": 80, "wind_height_m": 10.0}
    weather = _sample_weather()
    day_a = weather.iloc[[0]].copy()
    day_b = weather.iloc[[1]].copy()
    both = pd.concat([day_a, day_b], ignore_index=True)
    coefficient_a = _annual_coefficient(day_a, meta, "temperature")
    coefficient_b = _annual_coefficient(day_b, meta, "temperature")
    assert coefficient_a != pytest.approx(coefficient_b)

    combined = _annual_coefficient(both, meta, "temperature")
    assert combined == pytest.approx((coefficient_a + coefficient_b) / 2)


def test_temperature_coefficient_holds_vapor_pressure_deficit_constant() -> None:
    df = _sample_weather()
    meta = {"alt_m": 80, "wind_height_m": 10.0}
    partial = _annual_coefficient(df, meta, "temperature")

    def _mean_eto(frame: pd.DataFrame) -> float:
        series = compute_daily_eto(frame, site_meta=meta).frame["et_penman_monteith"]
        return float(pd.to_numeric(series, errors="coerce").mean())

    baseline = _mean_eto(df)
    warmer = df.copy()
    warmer["tmed_c"] = warmer["tmed_c"] * 1.01
    cooler = df.copy()
    cooler["tmed_c"] = cooler["tmed_c"] * 0.99
    confounded = (_mean_eto(warmer) - _mean_eto(cooler)) / (0.02 * baseline)
    assert partial != pytest.approx(confounded, rel=1e-3)


def test_relative_sensitivity_reports_month_and_year_separately() -> None:
    january = _sample_weather()
    february = _sample_weather().iloc[[0, 1]].copy()
    february["date"] = pd.to_datetime(["2024-02-01", "2024-02-02"])
    df = pd.concat([january, february], ignore_index=True)
    result = run_penman_monteith_relative_sensitivity(
        df, site_meta={"alt_m": 61.25, "wind_height_m": 10.0}
    )

    assert result.loc[result["period_type"] == "month", "period"].unique().tolist() == [
        "2024-01",
        "2024-02",
    ]
    assert result.loc[result["period_type"] == "annual", "period"].unique().tolist() == ["2024"]
    january_n = result.loc[result["period"] == "2024-01", "n"]
    february_n = result.loc[result["period"] == "2024-02", "n"]
    annual_n = result.loc[result["period"] == "2024", "n"]
    assert january_n.tolist() == [3, 3, 3, 3]
    assert february_n.tolist() == [2, 2, 2, 2]
    assert annual_n.tolist() == [5, 5, 5, 5]


def test_relative_sensitivity_labels_mixed_years_as_annual() -> None:
    df = _sample_weather()
    df.loc[2, "date"] = "2025-01-03"
    result = run_penman_monteith_relative_sensitivity(df, site_meta={"alt_m": 80})
    assert result.loc[result["period_type"] == "annual", "period"].unique().tolist() == ["annual"]
    assert set(result.loc[result["period_type"] == "month", "period"]) == {"2024-01", "2025-01"}


def test_relative_sensitivity_requires_penman_monteith_inputs() -> None:
    df = _sample_weather().drop(columns=["wind_mean_ms"])
    with pytest.raises(ValueError, match="missing required column"):
        run_penman_monteith_relative_sensitivity(df, site_meta={"alt_m": 80})


def test_relative_perturbation_rejects_zero() -> None:
    with pytest.raises(ValueError, match="strictly between 0 and 100"):
        run_penman_monteith_relative_sensitivity(
            _sample_weather(),
            site_meta={"alt_m": 80},
            perturbation_pct=0,
        )


def test_cmd_sensitivity_keeps_oat_table_and_adds_penman_relative_table(tmp_path: Path) -> None:
    input_dir = tmp_path / "cleaned"
    tables_dir = tmp_path / "tables"
    figures_dir = tmp_path / "figures"
    input_dir.mkdir()
    _sample_weather().to_csv(input_dir / "manaus_daily.csv", index=False)

    cmd_sensitivity(
        argparse.Namespace(
            input=str(input_dir),
            tables_output=str(tables_dir),
            figures_output=str(figures_dir),
            perturbations="-10,0,10",
            method="penman_monteith",
            site="manaus",
            all_sites=False,
            year=2024,
        )
    )

    oat = pd.read_csv(tables_dir / "manaus_sensitivity_penman_monteith.csv")
    assert oat["perturbation_pct"].min() == -10
    assert oat["perturbation_pct"].max() == 10
    relative = pd.read_csv(tables_dir / "manaus_sensitivity_penman_monteith_relative.csv")
    assert set(relative["period_type"]) == {"month", "annual"}
    assert relative["perturbation_pct"].unique().tolist() == pytest.approx([1])

    piracicaba = _sample_weather()
    piracicaba.to_csv(input_dir / "piracicaba_daily.csv", index=False)
    cmd_sensitivity(
        argparse.Namespace(
            input=str(input_dir),
            tables_output=str(tables_dir),
            figures_output=str(figures_dir),
            perturbations="0",
            method="turc",
            site="piracicaba",
            all_sites=False,
            year=2024,
        )
    )
    assert (tables_dir / "piracicaba_sensitivity_turc.csv").exists()
    assert not (tables_dir / "piracicaba_sensitivity_turc_relative.csv").exists()
    assert not (tables_dir / "piracicaba_sensitivity_penman_monteith_relative.csv").exists()


def _annual_coefficient(df: pd.DataFrame, site_meta: dict, variable: str) -> float:
    result = run_penman_monteith_relative_sensitivity(df, site_meta=site_meta)
    row = result[(result["period_type"] == "annual") & (result["variable"] == variable)].iloc[0]
    return float(row["sensitivity_coefficient"])
