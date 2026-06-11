from __future__ import annotations

import numpy as np
import pandas as pd

from .conversions import ArrayLike, as_array, restore_from_inputs


def penman_monteith_fao56(
    *,
    t_mean_c: ArrayLike,
    rn_mj_m2_day: ArrayLike,
    g_mj_m2_day: ArrayLike = 0.0,
    wind_2m_m_s: ArrayLike,
    saturation_vapor_pressure_kpa: ArrayLike,
    actual_vapor_pressure_kpa: ArrayLike,
    delta_kpa_c: ArrayLike,
    gamma_kpa_c: ArrayLike,
) -> float | np.ndarray | pd.Series:
    """Estimate reference ET0 using the FAO-56 Penman-Monteith equation.

    Equation summary:
        ET0 = [0.408 Delta (Rn - G) + gamma 900/(T + 273) u2 (es - ea)]
        / [Delta + gamma (1 + 0.34 u2)].

    Parameters
    ----------
    t_mean_c:
        Daily mean air temperature.
    rn_mj_m2_day:
        Net radiation at crop surface.
    g_mj_m2_day:
        Soil heat flux density, often 0 for daily calculations.
    wind_2m_m_s:
        Wind speed at 2 m height.
    saturation_vapor_pressure_kpa:
        Saturation vapor pressure, es.
    actual_vapor_pressure_kpa:
        Actual vapor pressure, ea.
    delta_kpa_c:
        Slope of saturation vapor pressure curve.
    gamma_kpa_c:
        Psychrometric constant.

    Units
    -----
    Temperature is degrees C; radiation and soil heat flux are MJ m-2 day-1;
    wind is m s-1; vapor pressures are kPa; Delta and gamma are kPa C-1.

    Returns
    -------
    float, numpy.ndarray, or pandas.Series
        ET0 in mm day-1. A pandas.Series input index/name is preserved.
    """
    t = as_array(t_mean_c)
    rn = as_array(rn_mj_m2_day)
    g = as_array(g_mj_m2_day)
    u2 = as_array(wind_2m_m_s)
    es = as_array(saturation_vapor_pressure_kpa)
    ea = as_array(actual_vapor_pressure_kpa)
    delta = as_array(delta_kpa_c)
    gamma = as_array(gamma_kpa_c)

    numerator = 0.408 * delta * (rn - g) + gamma * (900 / (t + 273)) * u2 * (es - ea)
    denominator = delta + gamma * (1 + 0.34 * u2)
    result = numerator / denominator
    return restore_from_inputs(
        result,
        t_mean_c,
        rn_mj_m2_day,
        g_mj_m2_day,
        wind_2m_m_s,
        saturation_vapor_pressure_kpa,
        actual_vapor_pressure_kpa,
        delta_kpa_c,
        gamma_kpa_c,
    )
