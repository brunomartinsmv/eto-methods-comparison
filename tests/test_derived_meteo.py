from __future__ import annotations

import math

import pandas as pd
import pytest

from scripts.derived_meteo import (
    extraterrestrial_radiation_mj_m2_day,
    psychrometric_constant_kpa_c,
    saturation_vapor_pressure_kpa,
    wind_speed_at_2m,
)


def test_saturation_vapor_pressure_at_zero_c() -> None:
    result = saturation_vapor_pressure_kpa(pd.Series([0.0]))
    assert result.iloc[0] == pytest.approx(0.6108, rel=1e-4)


def test_wind_speed_at_2m_is_unchanged_when_measured_at_2m() -> None:
    wind = pd.Series([2.0, 3.0])
    assert wind_speed_at_2m(wind, measurement_height_m=2.0).tolist() == [2.0, 3.0]


def test_wind_speed_at_2m_reduces_10m_wind() -> None:
    wind = pd.Series([5.0])
    converted = float(wind_speed_at_2m(wind, measurement_height_m=10.0).iloc[0])
    assert converted < 5.0
    expected = 5.0 * 4.87 / math.log(67.8 * 10 - 5.42)
    assert converted == pytest.approx(expected)


def test_extraterrestrial_radiation_mid_year_tropics() -> None:
    ra = extraterrestrial_radiation_mj_m2_day(pd.Series([182]), latitude_deg=-3.1)
    assert float(ra.iloc[0]) == pytest.approx(32.18, rel=0.01)


def test_psychrometric_constant_decreases_with_altitude() -> None:
    sea_level = psychrometric_constant_kpa_c(0.0)
    high = psychrometric_constant_kpa_c(1000.0)
    assert high < sea_level
