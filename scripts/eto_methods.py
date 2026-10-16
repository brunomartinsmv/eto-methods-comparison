"""ET0 methods implemented as pure numerical transforms.

Coefficients are explicit keyword defaults so callers can document local calibration.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from .conversions import ArrayLike, as_array, mj_m2_day_to_mm_day, restore_from_inputs


def camargo(
    *,
    t_mean_c: ArrayLike,
    ra_mj_m2_day: ArrayLike,
    coefficient: float = 0.01,
) -> float | np.ndarray | pd.Series:
    """Camargo ET0 = c * Ra_mm * Tmean.

    Parameters
    ----------
    t_mean_c: daily mean air temperature, degrees C.
    ra_mj_m2_day: extraterrestrial radiation, MJ m-2 day-1, converted to mm day-1.
    coefficient: empirical coefficient.

    Units
    -----
    ET0 in mm day-1.

    Returns
    -------
    float, numpy.ndarray, or pandas.Series.
    """
    ra_mm = as_array(mj_m2_day_to_mm_day(ra_mj_m2_day))
    result = coefficient * ra_mm * as_array(t_mean_c)
    return restore_from_inputs(result, t_mean_c, ra_mj_m2_day)


def hargreaves_samani(
    *,
    t_min_c: ArrayLike,
    t_max_c: ArrayLike,
    t_mean_c: ArrayLike,
    ra_mj_m2_day: ArrayLike,
    coefficient: float = 0.0023,
    exponent: float = 0.5,
) -> float | np.ndarray | pd.Series:
    """Hargreaves-Samani ET0 = c * Ra_mm * (Tmax - Tmin)**exponent * (Tmean + 17.8).

    Parameters
    ----------
    t_min_c, t_max_c, t_mean_c: daily minimum, maximum, and mean air temperature, degrees C.
    ra_mj_m2_day: extraterrestrial radiation, MJ m-2 day-1, converted to mm day-1.
    coefficient: empirical coefficient. Published default is 0.0023.
    exponent: power on daily temperature range. Published default is 0.5.

    Units
    -----
    ET0 in mm day-1.

    Returns
    -------
    float, numpy.ndarray, or pandas.Series.
    """
    if not np.isfinite(exponent) or exponent <= 0.0:
        raise ValueError("Hargreaves-Samani exponent must be finite and greater than 0")
    temp_range = np.maximum(as_array(t_max_c) - as_array(t_min_c), 0)
    ra_mm = as_array(mj_m2_day_to_mm_day(ra_mj_m2_day))
    powered = _temperature_range_power(temp_range, exponent)
    result = coefficient * ra_mm * powered * (as_array(t_mean_c) + 17.8)
    return restore_from_inputs(result, t_min_c, t_max_c, t_mean_c, ra_mj_m2_day)


def _temperature_range_power(temp_range: np.ndarray, exponent: float) -> np.ndarray:
    if exponent == 0.5:
        return np.sqrt(temp_range)
    range_values = np.asarray(temp_range, dtype=float)
    if range_values.ndim == 0:
        value = float(range_values)
        return np.asarray(value**exponent if value > 0.0 else 0.0)
    powered = np.zeros(range_values.shape, dtype=float)
    positive = range_values > 0.0
    powered[positive] = np.power(range_values[positive], exponent)
    return powered


def makkink(
    *,
    delta_kpa_c: ArrayLike,
    gamma_kpa_c: ArrayLike,
    rs_mj_m2_day: ArrayLike,
    coefficient: float = 0.61,
    intercept_mm_day: float = -0.12,
) -> float | np.ndarray | pd.Series:
    """Makkink ET0 = c * [Delta / (Delta + gamma)] * Rs_mm + intercept.

    Parameters
    ----------
    delta_kpa_c: slope of the saturation vapor-pressure curve, kPa C-1.
    gamma_kpa_c: psychrometric constant, kPa C-1.
    rs_mj_m2_day: global radiation, MJ m-2 day-1, converted to mm day-1.
    coefficient, intercept_mm_day: empirical coefficients.

    Units
    -----
    ET0 in mm day-1.

    Returns
    -------
    float, numpy.ndarray, or pandas.Series.
    """
    delta = as_array(delta_kpa_c)
    gamma = as_array(gamma_kpa_c)
    rs_mm = as_array(mj_m2_day_to_mm_day(rs_mj_m2_day))
    result = coefficient * (delta / (delta + gamma)) * rs_mm + intercept_mm_day
    return restore_from_inputs(result, delta_kpa_c, gamma_kpa_c, rs_mj_m2_day)


def mccloud(
    *,
    t_mean_c: ArrayLike,
    exponent: float = 1.8,
    coefficient: float = 0.254,
    base: float = 1.07,
) -> float | np.ndarray | pd.Series:
    """McCloud ET0 = c * base^(p * Tmean).

    Parameters
    ----------
    t_mean_c: daily mean air temperature, degrees C.
    exponent: empirical temperature exponent.
    coefficient: daily scaling coefficient.
    base: empirical temperature base.

    Units
    -----
    ET0 in mm day-1.

    Returns
    -------
    float, numpy.ndarray, or pandas.Series.
    """
    result = coefficient * base ** (exponent * as_array(t_mean_c))
    return restore_from_inputs(result, t_mean_c)


def priestley_taylor(
    *,
    delta_kpa_c: ArrayLike,
    gamma_kpa_c: ArrayLike,
    rn_mj_m2_day: ArrayLike,
    g_mj_m2_day: ArrayLike = 0.0,
    alpha: float = 1.26,
) -> float | np.ndarray | pd.Series:
    """Priestley-Taylor ET0 = alpha * [Delta / (Delta + gamma)] * (Rn - G)_mm.

    Parameters
    ----------
    delta_kpa_c: slope of the saturation vapor-pressure curve, kPa C-1.
    gamma_kpa_c: psychrometric constant, kPa C-1.
    rn_mj_m2_day: net radiation, MJ m-2 day-1.
    g_mj_m2_day: soil heat flux, MJ m-2 day-1.
    alpha: Priestley-Taylor coefficient.

    Units
    -----
    Rn and G are converted to mm day-1. ET0 is mm day-1.

    Returns
    -------
    float, numpy.ndarray, or pandas.Series.
    """
    delta = as_array(delta_kpa_c)
    gamma = as_array(gamma_kpa_c)
    available_mm = as_array(mj_m2_day_to_mm_day(as_array(rn_mj_m2_day) - as_array(g_mj_m2_day)))
    result = alpha * (delta / (delta + gamma)) * available_mm
    return restore_from_inputs(result, delta_kpa_c, gamma_kpa_c, rn_mj_m2_day, g_mj_m2_day)


def turc(
    *,
    t_mean_c: ArrayLike,
    rs_mj_m2_day: ArrayLike,
    rh_mean_pct: ArrayLike | None = None,
    coefficient: float = 0.013,
) -> float | np.ndarray | pd.Series:
    """Turc ET0 = c * Tmean / (Tmean + 15) * (Rs_cal_cm2_day + 50).

    When relative humidity is below 50 percent, multiply by 1 + (50 - RH) / 70.

    Parameters
    ----------
    t_mean_c: daily mean air temperature, degrees C.
    rs_mj_m2_day: global radiation, MJ m-2 day-1, converted to cal cm-2 day-1.
    rh_mean_pct: mean relative humidity, percent. Optional.
    coefficient: empirical coefficient.

    Units
    -----
    ET0 in mm day-1.

    Returns
    -------
    float, numpy.ndarray, or pandas.Series.
    """
    t = as_array(t_mean_c)
    rs_cal_cm2_day = as_array(rs_mj_m2_day) * 23.9006
    result = coefficient * (t / (t + 15)) * (rs_cal_cm2_day + 50)
    if rh_mean_pct is not None:
        rh = as_array(rh_mean_pct)
        correction = np.where(rh < 50, 1 + (50 - rh) / 70, 1.0)
        result = result * correction
    inputs = (
        (t_mean_c, rs_mj_m2_day) if rh_mean_pct is None else (t_mean_c, rs_mj_m2_day, rh_mean_pct)
    )
    return restore_from_inputs(result, *inputs)


def global_radiation(
    *,
    rs_mj_m2_day: ArrayLike,
    coefficient: float = 0.53,
) -> float | np.ndarray | pd.Series:
    """ET0 = c * Rs_mm.

    Parameters
    ----------
    rs_mj_m2_day: global radiation, MJ m-2 day-1, converted to mm day-1.
    coefficient: empirical coefficient.

    Units
    -----
    ET0 in mm day-1.

    Returns
    -------
    float, numpy.ndarray, or pandas.Series.
    """
    result = coefficient * as_array(mj_m2_day_to_mm_day(rs_mj_m2_day))
    return restore_from_inputs(result, rs_mj_m2_day)


def ivanov(
    *,
    t_mean_c: ArrayLike,
    rh_mean_pct: ArrayLike,
    coefficient: float = 0.00006,
) -> float | np.ndarray | pd.Series:
    """Ivanov ET0 = c_daily * (Tmean + 25)^2 * (100 - RH).

    Parameters
    ----------
    t_mean_c: daily mean air temperature, degrees C.
    rh_mean_pct: mean relative humidity, percent.
    coefficient: daily empirical coefficient.

    Units
    -----
    ET0 in mm day-1.

    Returns
    -------
    float, numpy.ndarray, or pandas.Series.
    """
    result = coefficient * (as_array(t_mean_c) + 25) ** 2 * (100 - as_array(rh_mean_pct))
    return restore_from_inputs(result, t_mean_c, rh_mean_pct)


def jensen_heise(
    *,
    t_mean_c: ArrayLike,
    rs_mj_m2_day: ArrayLike,
    temperature_coefficient: float = 0.025,
    temperature_offset_c: float = 3.0,
) -> float | np.ndarray | pd.Series:
    """Jensen-Heise ET0 = Rs_mm * Ct * (Tmean - Tx).

    Parameters
    ----------
    t_mean_c: daily mean air temperature, degrees C.
    rs_mj_m2_day: global radiation, MJ m-2 day-1, converted to mm day-1.
    temperature_coefficient: empirical temperature coefficient.
    temperature_offset_c: empirical temperature offset, degrees C.

    Units
    -----
    ET0 in mm day-1.

    Returns
    -------
    float, numpy.ndarray, or pandas.Series.
    """
    rs_mm = as_array(mj_m2_day_to_mm_day(rs_mj_m2_day))
    result = rs_mm * temperature_coefficient * (as_array(t_mean_c) - temperature_offset_c)
    return restore_from_inputs(result, t_mean_c, rs_mj_m2_day)


def garcia_lopez(
    *,
    t_mean_c: ArrayLike,
    rh_mean_pct: ArrayLike,
    wind_2m_m_s: ArrayLike,
    rs_mj_m2_day: ArrayLike,
    coefficient: float = 0.01,
) -> float | np.ndarray | pd.Series:
    """Garcia-Lopez ET0 = c * (Tmean + 21) * (1 - RH/100) * (1 + u2) * Rs_mm.

    Parameters
    ----------
    t_mean_c: daily mean air temperature, degrees C.
    rh_mean_pct: mean relative humidity, percent.
    wind_2m_m_s: wind speed at 2 m, m s-1.
    rs_mj_m2_day: global radiation, MJ m-2 day-1, converted to mm day-1.
    coefficient: empirical coefficient.

    Units
    -----
    ET0 in mm day-1.

    Returns
    -------
    float, numpy.ndarray, or pandas.Series.
    """
    rs_mm = as_array(mj_m2_day_to_mm_day(rs_mj_m2_day))
    result = (
        coefficient
        * (as_array(t_mean_c) + 21)
        * (1 - as_array(rh_mean_pct) / 100)
        * (1 + as_array(wind_2m_m_s))
        * rs_mm
    )
    return restore_from_inputs(result, t_mean_c, rh_mean_pct, wind_2m_m_s, rs_mj_m2_day)


def net_radiation(
    *,
    rn_mj_m2_day: ArrayLike,
    coefficient: float = 0.408,
) -> float | np.ndarray | pd.Series:
    """ET0 = c * Rn. The default c is the FAO-56 factor 0.408.

    Parameters
    ----------
    rn_mj_m2_day: net radiation, MJ m-2 day-1.
    coefficient: conversion coefficient.

    Units
    -----
    ET0 in mm day-1 when c is 0.408.

    Returns
    -------
    float, numpy.ndarray, or pandas.Series.
    """
    result = coefficient * as_array(rn_mj_m2_day)
    return restore_from_inputs(result, rn_mj_m2_day)


def radiation_temperature(
    *,
    t_mean_c: ArrayLike,
    rs_mj_m2_day: ArrayLike,
    coefficient: float = 0.01,
    temperature_offset_c: float = 15.0,
) -> float | np.ndarray | pd.Series:
    """ET0 = c * Rs_mm * (Tmean + offset).

    Parameters
    ----------
    t_mean_c: daily mean air temperature, degrees C.
    rs_mj_m2_day: global radiation, MJ m-2 day-1, converted to mm day-1.
    coefficient: empirical coefficient.
    temperature_offset_c: empirical temperature offset, degrees C.

    Units
    -----
    ET0 in mm day-1.

    Returns
    -------
    float, numpy.ndarray, or pandas.Series.
    """
    result = (
        coefficient
        * as_array(mj_m2_day_to_mm_day(rs_mj_m2_day))
        * (as_array(t_mean_c) + temperature_offset_c)
    )
    return restore_from_inputs(result, t_mean_c, rs_mj_m2_day)


def lungeon(
    *,
    t_mean_c: ArrayLike,
    rh_mean_pct: ArrayLike,
    coefficient: float = 0.001,
) -> float | np.ndarray | pd.Series:
    """Lungeon ET0 = c * (Tmean + 20)^2 * (1 - RH/100).

    Parameters
    ----------
    t_mean_c: daily mean air temperature, degrees C.
    rh_mean_pct: mean relative humidity, percent.
    coefficient: empirical coefficient.

    Units
    -----
    ET0 in mm day-1.

    Returns
    -------
    float, numpy.ndarray, or pandas.Series.
    """
    result = coefficient * (as_array(t_mean_c) + 20) ** 2 * (1 - as_array(rh_mean_pct) / 100)
    return restore_from_inputs(result, t_mean_c, rh_mean_pct)


def stephens_stewart(
    *,
    t_mean_c: ArrayLike,
    rs_mj_m2_day: ArrayLike,
    coefficient: float = 0.01476,
    temperature_offset_c: float = 5.0,
) -> float | np.ndarray | pd.Series:
    """Stephens-Stewart ET0 = c * (Tmean + offset) * Rs_mm.

    Parameters
    ----------
    t_mean_c: daily mean air temperature, degrees C.
    rs_mj_m2_day: global radiation, MJ m-2 day-1, converted to mm day-1.
    coefficient: empirical coefficient.
    temperature_offset_c: empirical temperature offset, degrees C.

    Units
    -----
    ET0 in mm day-1.

    Returns
    -------
    float, numpy.ndarray, or pandas.Series.
    """
    result = (
        coefficient
        * (as_array(t_mean_c) + temperature_offset_c)
        * as_array(mj_m2_day_to_mm_day(rs_mj_m2_day))
    )
    return restore_from_inputs(result, t_mean_c, rs_mj_m2_day)


def hicks_hess(
    *,
    t_mean_c: ArrayLike,
    rs_mj_m2_day: ArrayLike,
    wind_2m_m_s: ArrayLike,
    coefficient: float = 0.0055,
) -> float | np.ndarray | pd.Series:
    """Hicks-Hess ET0 = c * Rs_mm * (Tmean + 17.8) * (1 + u2).

    Parameters
    ----------
    t_mean_c: daily mean air temperature, degrees C.
    rs_mj_m2_day: global radiation, MJ m-2 day-1, converted to mm day-1.
    wind_2m_m_s: wind speed at 2 m, m s-1.
    coefficient: empirical coefficient.

    Units
    -----
    ET0 in mm day-1.

    Returns
    -------
    float, numpy.ndarray, or pandas.Series.
    """
    result = (
        coefficient
        * as_array(mj_m2_day_to_mm_day(rs_mj_m2_day))
        * (as_array(t_mean_c) + 17.8)
        * (1 + as_array(wind_2m_m_s))
    )
    return restore_from_inputs(result, t_mean_c, rs_mj_m2_day, wind_2m_m_s)
