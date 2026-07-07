"""Regression tests comparing spreadsheet precomputed ET0 vs pipeline-computed values.

The legacy spreadsheet stores Garcia-Lopez values on a different scale than the
pipeline implementation (see docs/roadmap_raw_to_eto.md). These tests lock that
documented divergence so future refactors do not silently change the comparison.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from scripts import compute_eto
from scripts.eto_methods import garcia_lopez


def _synthetic_weather_with_legacy_precomputed() -> pd.DataFrame:
    """Weather rows with spreadsheet-style precomputed ET0 columns."""
    n = 5
    days = np.arange(1, n + 1)
    tmed = 28.0 + 0.2 * days
    return pd.DataFrame(
        {
            "date": pd.date_range("2024-01-01", periods=n, freq="D"),
            "tmed_c": tmed,
            "tmin_c": tmed - 4.0,
            "tmax_c": tmed + 4.0,
            "rh_mean_pct": 75.0,
            "wind_mean_ms": 1.5,
            "rad_global_mj_m2_d": 18.0 + 0.3 * days,
            "rad_net_mj_m2_d": 10.0 + 0.2 * days,
            "ra_extraterrestre_mj_m2_d": 34.0,
            "et_penman_monteith": 2.0 + 0.05 * days,
            "et_garcia_lopez": 37.5 + 0.01 * days,
            "et_hargreaves_samani": 4.0 + 0.03 * days,
        }
    )


def test_garcia_lopez_computed_values_differ_greatly_from_spreadsheet_precomputed() -> None:
    df = _synthetic_weather_with_legacy_precomputed()
    result = compute_eto.compute_daily_eto(
        df,
        site_meta={"alt_m": 61.25},
        include_precomputed=True,
    )

    gl_comparison = next(
        comparison
        for comparison in result.report.comparisons
        if comparison.column == "et_garcia_lopez"
    )
    assert gl_comparison.n_pairs == len(df)
    assert gl_comparison.rmse > 30.0
    assert gl_comparison.max_abs_diff > 30.0

    computed_gl = result.frame["et_garcia_lopez"]
    precomputed_gl = result.frame["precomputed_et_garcia_lopez"]
    assert computed_gl.max() < 5.0
    assert precomputed_gl.min() > 37.0
    assert precomputed_gl.min() / computed_gl.max() > 10.0


def test_garcia_lopez_pipeline_matches_eto_methods_implementation() -> None:
    df = _synthetic_weather_with_legacy_precomputed()
    expected = garcia_lopez(
        t_mean_c=df["tmed_c"],
        rh_mean_pct=df["rh_mean_pct"],
        wind_2m_m_s=df["wind_mean_ms"],
        rs_mj_m2_day=df["rad_global_mj_m2_d"],
    )
    result = compute_eto.compute_daily_eto(df, site_meta={"alt_m": 61.25})
    np.testing.assert_allclose(result.frame["et_garcia_lopez"], expected, rtol=1e-10)


def test_penman_monteith_precomputed_comparison_is_smaller_than_garcia_lopez() -> None:
    df = _synthetic_weather_with_legacy_precomputed()
    result = compute_eto.compute_daily_eto(
        df,
        site_meta={"alt_m": 61.25},
        include_precomputed=True,
    )

    by_column = {comparison.column: comparison for comparison in result.report.comparisons}
    assert "et_penman_monteith" in by_column
    assert "et_garcia_lopez" in by_column
    assert by_column["et_penman_monteith"].rmse < by_column["et_garcia_lopez"].rmse


@pytest.mark.skipif(
    not __import__("pathlib").Path("data/raw/Evapo.xlsx").exists(),
    reason="Real spreadsheet not available in this checkout",
)
def test_manaus_garcia_lopez_divergence_on_first_day_of_2024() -> None:
    """Optional check against the committed cleaned Manaus series when raw data is present."""
    cleaned = pd.read_csv("data/cleaned/manaus_daily.csv", parse_dates=["date"])
    row = cleaned.loc[cleaned["date"] == "2024-01-01"].iloc[0]

    result = compute_eto.compute_daily_eto(
        cleaned.head(1),
        site_meta={"alt_m": 61.25},
        include_precomputed=True,
    )
    computed = result.frame["et_garcia_lopez"].iloc[0]
    precomputed = row["et_garcia_lopez"]

    assert precomputed > 30.0
    assert computed < 1.0
    assert abs(computed - precomputed) > 30.0
