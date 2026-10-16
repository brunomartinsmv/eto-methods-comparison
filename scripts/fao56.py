from __future__ import annotations

import numpy as np
import pandas as pd

from .conversions import ArrayLike, as_array, restore_from_inputs
from .derived_meteo import (
    psychrometric_constant_kpa_c,
    saturation_vapor_pressure_kpa,
    vapor_pressure_slope_kpa_c,
)

# FAO-56 Eq. 39. MJ K-4 m-2 day-1.
_STEFAN_BOLTZMANN = 4.903e-9


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


def _solar_to_clear_sky_ratio(rs: np.ndarray, rso: np.ndarray) -> np.ndarray:
    """Rs/Rso limited to 1, as required by FAO-56 Eq. 39."""
    ratio = np.ones_like(rs, dtype=float)
    np.divide(rs, rso, out=ratio, where=rso > 0)
    return np.minimum(ratio, 1.0)


def fao56_pmt(
    *,
    t_min_c: ArrayLike,
    t_max_c: ArrayLike,
    ra_mj_m2_day: ArrayLike,
    altitude_m: float,
    k_rs: float = 0.16,
    wind_2m_m_s: float = 2.0,
    albedo: float = 0.23,
) -> float | np.ndarray | pd.Series:
    """FAO-56 Penman-Monteith temperature method (PMT) for missing humidity, radiation, and wind.

    Estimates the missing inputs with the FAO-56 procedures and then applies Eq. 6.
    Actual vapor pressure uses dewpoint equal to minimum temperature (Eq. 48).
    Solar radiation is ``k_rs * sqrt(Tmax - Tmin) * Ra`` (Eq. 50). Wind at 2 m
    defaults to 2 m s-1. Net radiation is rebuilt from that solar estimate
    (Eqs. 37-39); measured net radiation is not used.

    Parameters
    ----------
    t_min_c, t_max_c: daily minimum and maximum air temperature, degrees C.
    ra_mj_m2_day: extraterrestrial radiation, MJ m-2 day-1.
    altitude_m: station elevation, m, used for the psychrometric constant and clear-sky radiation.
    k_rs: Hargreaves radiation coefficient, degrees C-0.5. FAO-56 uses 0.16 for interior sites.
    wind_2m_m_s: wind speed substituted at 2 m, m s-1.
    albedo: reference-crop albedo, dimensionless.

    Units
    -----
    ET0 in mm day-1. Radiation arguments are MJ m-2 day-1.

    Returns
    -------
    float, numpy.ndarray, or pandas.Series.
    """
    t_min = as_array(t_min_c)
    t_max = as_array(t_max_c)
    ra = as_array(ra_mj_m2_day)
    t_mean = (t_max + t_min) / 2.0
    es_tmax = as_array(saturation_vapor_pressure_kpa(t_max))
    es_tmin = as_array(saturation_vapor_pressure_kpa(t_min))
    es = (es_tmax + es_tmin) / 2.0
    ea = es_tmin
    delta = as_array(vapor_pressure_slope_kpa_c(t_mean))
    gamma = psychrometric_constant_kpa_c(altitude_m)

    temp_range = np.maximum(t_max - t_min, 0.0)
    rs = k_rs * np.sqrt(temp_range) * ra
    rso = (0.75 + 2.0e-5 * altitude_m) * ra
    ratio = _solar_to_clear_sky_ratio(rs, rso)
    rns = (1.0 - albedo) * rs
    t_max_k = t_max + 273.16
    t_min_k = t_min + 273.16
    stefan = _STEFAN_BOLTZMANN * ((t_max_k**4 + t_min_k**4) / 2.0)
    emissivity = 0.34 - 0.14 * np.sqrt(np.maximum(ea, 0.0))
    cloudiness = 1.35 * ratio - 0.35
    rnl = stefan * emissivity * cloudiness
    rn = rns - rnl

    result = penman_monteith_fao56(
        t_mean_c=t_mean,
        rn_mj_m2_day=rn,
        g_mj_m2_day=0.0,
        wind_2m_m_s=wind_2m_m_s,
        saturation_vapor_pressure_kpa=es,
        actual_vapor_pressure_kpa=ea,
        delta_kpa_c=delta,
        gamma_kpa_c=gamma,
    )
    return restore_from_inputs(np.asarray(result, dtype=float), t_min_c, t_max_c, ra_mj_m2_day)
