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
    """FAO-56 Penman-Monteith reference ET0 (eq. 6).

    ET0 = [0.408 Delta (Rn - G) + gamma * 900/(T + 273) * u2 * (es - ea)]
    / [Delta + gamma (1 + 0.34 u2)].

    Parameters
    ----------
    t_mean_c: daily mean air temperature, degrees C.
    rn_mj_m2_day: net radiation, MJ m-2 day-1.
    g_mj_m2_day: soil heat flux, MJ m-2 day-1 (often 0 at daily scale).
    wind_2m_m_s: wind speed at 2 m, m s-1.
    saturation_vapor_pressure_kpa: saturation vapor pressure es, kPa.
    actual_vapor_pressure_kpa: actual vapor pressure ea, kPa.
    delta_kpa_c: slope of the saturation vapor-pressure curve, kPa C-1.
    gamma_kpa_c: psychrometric constant, kPa C-1.

    Units
    -----
    ET0 in mm day-1.

    Returns
    -------
    float, numpy.ndarray, or pandas.Series.
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
