from __future__ import annotations

import numpy as np
import pandas as pd

from .conversions import ArrayLike, as_array, mj_m2_day_to_mm_day, restore_from_inputs


def _doc_note(method: str) -> str:
    return (
        f"{method} is implemented as a pure numerical transform. Coefficients "
        "are explicit keyword defaults so local calibration can be documented by callers."
    )


def camargo(
    *,
    t_mean_c: ArrayLike,
    ra_mj_m2_day: ArrayLike,
    coefficient: float = 0.01,
) -> float | np.ndarray | pd.Series:
    """Estimate ET0 with a Camargo-style temperature and extraterrestrial-radiation form.

    Equation summary:
        ET0 = c * Ra_mm * Tmean.

    Parameters
    ----------
    t_mean_c:
        Daily mean air temperature.
    ra_mj_m2_day:
        Extraterrestrial radiation.
    coefficient:
        Empirical Camargo coefficient.

    Units
    -----
    Temperature is degrees C; Ra is MJ m-2 day-1 and is converted to mm day-1.

    Returns
    -------
    float, numpy.ndarray, or pandas.Series
        ET0 in mm day-1. A pandas.Series input index/name is preserved.
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
) -> float | np.ndarray | pd.Series:
    """Estimate ET0 with the Hargreaves-Samani temperature-range method.

    Equation summary:
        ET0 = c * Ra_mm * sqrt(Tmax - Tmin) * (Tmean + 17.8).

    Parameters
    ----------
    t_min_c, t_max_c, t_mean_c:
        Daily minimum, maximum, and mean air temperature.
    ra_mj_m2_day:
        Extraterrestrial radiation.
    coefficient:
        Hargreaves-Samani empirical coefficient.

    Units
    -----
    Temperatures are degrees C; Ra is MJ m-2 day-1 and is converted to mm day-1.

    Returns
    -------
    float, numpy.ndarray, or pandas.Series
        ET0 in mm day-1. A pandas.Series input index/name is preserved.
    """
    temp_range = np.maximum(as_array(t_max_c) - as_array(t_min_c), 0)
    ra_mm = as_array(mj_m2_day_to_mm_day(ra_mj_m2_day))
    result = coefficient * ra_mm * np.sqrt(temp_range) * (as_array(t_mean_c) + 17.8)
    return restore_from_inputs(result, t_min_c, t_max_c, t_mean_c, ra_mj_m2_day)


def makkink(
    *,
    delta_kpa_c: ArrayLike,
    gamma_kpa_c: ArrayLike,
    rs_mj_m2_day: ArrayLike,
    coefficient: float = 0.61,
    intercept_mm_day: float = -0.12,
) -> float | np.ndarray | pd.Series:
    """Estimate ET0 with the Makkink radiation-temperature method.

    Equation summary:
        ET0 = c * [Delta / (Delta + gamma)] * Rs_mm + intercept.

    Parameters
    ----------
    delta_kpa_c:
        Slope of saturation vapor pressure curve.
    gamma_kpa_c:
        Psychrometric constant.
    rs_mj_m2_day:
        Incoming solar/global radiation.
    coefficient, intercept_mm_day:
        Empirical Makkink coefficients.

    Units
    -----
    Delta and gamma are kPa C-1; Rs is MJ m-2 day-1 and is converted to mm day-1.

    Returns
    -------
    float, numpy.ndarray, or pandas.Series
        ET0 in mm day-1. A pandas.Series input index/name is preserved.
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
) -> float | np.ndarray | pd.Series:
    """Estimate ET0 with a McCloud temperature-power form.

    Equation summary:
        ET0 = c * max(Tmean, 0)^p.

    Parameters
    ----------
    t_mean_c:
        Daily mean air temperature.
    exponent:
        Empirical temperature exponent.
    coefficient:
        Empirical scaling coefficient.

    Units
    -----
    Temperature is degrees C; output is mm day-1 under the chosen coefficients.

    Returns
    -------
    float, numpy.ndarray, or pandas.Series
        ET0 in mm day-1. A pandas.Series input index/name is preserved.
    """
    result = coefficient * np.maximum(as_array(t_mean_c), 0) ** exponent
    return restore_from_inputs(result, t_mean_c)


def priestley_taylor(
    *,
    delta_kpa_c: ArrayLike,
    gamma_kpa_c: ArrayLike,
    rn_mj_m2_day: ArrayLike,
    g_mj_m2_day: ArrayLike = 0.0,
    alpha: float = 1.26,
) -> float | np.ndarray | pd.Series:
    """Estimate ET0 with the Priestley-Taylor equilibrium evaporation method.

    Equation summary:
        ET0 = alpha * [Delta / (Delta + gamma)] * (Rn - G)_mm.

    Parameters
    ----------
    delta_kpa_c:
        Slope of saturation vapor pressure curve.
    gamma_kpa_c:
        Psychrometric constant.
    rn_mj_m2_day:
        Net radiation.
    g_mj_m2_day:
        Soil heat flux density.
    alpha:
        Priestley-Taylor coefficient.

    Units
    -----
    Delta and gamma are kPa C-1; Rn and G are MJ m-2 day-1 and are converted to
    mm day-1.

    Returns
    -------
    float, numpy.ndarray, or pandas.Series
        ET0 in mm day-1. A pandas.Series input index/name is preserved.
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
    """Estimate ET0 with the Turc radiation-temperature method.

    Equation summary:
        ET0 = 0.013 * Tmean/(Tmean + 15) * (Rs_cal_cm2_day + 50), with a
        humidity correction when RH < 50 percent.

    Parameters
    ----------
    t_mean_c:
        Daily mean air temperature.
    rs_mj_m2_day:
        Incoming solar/global radiation.
    rh_mean_pct:
        Mean relative humidity. If provided below 50 percent, Turc's dry-air
        correction is applied.
    coefficient:
        Turc empirical radiation-temperature coefficient.

    Units
    -----
    Temperature is degrees C; Rs is MJ m-2 day-1 and internally converted to
    cal cm-2 day-1.

    Returns
    -------
    float, numpy.ndarray, or pandas.Series
        ET0 in mm day-1. A pandas.Series input index/name is preserved.
    """
    t = as_array(t_mean_c)
    rs_cal_cm2_day = as_array(rs_mj_m2_day) * 23.9006
    result = coefficient * (t / (t + 15)) * (rs_cal_cm2_day + 50)
    if rh_mean_pct is not None:
        rh = as_array(rh_mean_pct)
        correction = np.where(rh < 50, 1 + (50 - rh) / 70, 1.0)
        result = result * correction
    inputs = (t_mean_c, rs_mj_m2_day) if rh_mean_pct is None else (t_mean_c, rs_mj_m2_day, rh_mean_pct)
    return restore_from_inputs(result, *inputs)


def global_radiation(
    *,
    rs_mj_m2_day: ArrayLike,
    coefficient: float = 0.53,
) -> float | np.ndarray | pd.Series:
    """Estimate ET0 as a calibrated fraction of global radiation.

    Equation summary:
        ET0 = c * Rs_mm.

    Parameters
    ----------
    rs_mj_m2_day:
        Incoming solar/global radiation.
    coefficient:
        Empirical radiation coefficient.

    Units
    -----
    Rs is MJ m-2 day-1 and is converted to mm day-1.

    Returns
    -------
    float, numpy.ndarray, or pandas.Series
        ET0 in mm day-1. A pandas.Series input index/name is preserved.
    """
    result = coefficient * as_array(mj_m2_day_to_mm_day(rs_mj_m2_day))
    return restore_from_inputs(result, rs_mj_m2_day)


def ivanov(
    *,
    t_mean_c: ArrayLike,
    rh_mean_pct: ArrayLike,
    coefficient: float = 0.0018,
) -> float | np.ndarray | pd.Series:
    """Estimate ET0 with the Ivanov temperature-humidity method.

    Equation summary:
        ET0 = c * (Tmean + 25)^2 * (100 - RH).

    Parameters
    ----------
    t_mean_c:
        Daily mean air temperature.
    rh_mean_pct:
        Mean relative humidity.
    coefficient:
        Empirical Ivanov coefficient.

    Units
    -----
    Temperature is degrees C; relative humidity is percent; output is mm day-1.

    Returns
    -------
    float, numpy.ndarray, or pandas.Series
        ET0 in mm day-1. A pandas.Series input index/name is preserved.
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
    """Estimate ET0 with the Jensen-Heise radiation-temperature method.

    Equation summary:
        ET0 = Rs_mm * Ct * (Tmean - Tx).

    Parameters
    ----------
    t_mean_c:
        Daily mean air temperature.
    rs_mj_m2_day:
        Incoming solar/global radiation.
    temperature_coefficient:
        Empirical temperature coefficient.
    temperature_offset_c:
        Empirical temperature offset.

    Units
    -----
    Temperature is degrees C; Rs is MJ m-2 day-1 and is converted to mm day-1.

    Returns
    -------
    float, numpy.ndarray, or pandas.Series
        ET0 in mm day-1. A pandas.Series input index/name is preserved.
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
    """Estimate ET0 with a Garcia-Lopez combined empirical form.

    Equation summary:
        ET0 = c * (Tmean + 21) * (1 - RH/100) * (1 + u2) * Rs_mm.

    Parameters
    ----------
    t_mean_c:
        Daily mean air temperature.
    rh_mean_pct:
        Mean relative humidity.
    wind_2m_m_s:
        Wind speed at 2 m height.
    rs_mj_m2_day:
        Incoming solar/global radiation.
    coefficient:
        Empirical Garcia-Lopez scaling coefficient.

    Units
    -----
    Temperature is degrees C; relative humidity is percent; wind is m s-1; Rs
    is MJ m-2 day-1 and is converted to mm day-1.

    Returns
    -------
    float, numpy.ndarray, or pandas.Series
        ET0 in mm day-1. A pandas.Series input index/name is preserved.
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
    """Estimate ET0 from net radiation alone.

    Equation summary:
        ET0 = c * Rn, where c defaults to the FAO-56 0.408 conversion.

    Parameters
    ----------
    rn_mj_m2_day:
        Net radiation.
    coefficient:
        Conversion/scaling coefficient.

    Units
    -----
    Rn is MJ m-2 day-1; output is mm day-1 when c is 0.408.

    Returns
    -------
    float, numpy.ndarray, or pandas.Series
        ET0 in mm day-1. A pandas.Series input index/name is preserved.
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
    """Estimate ET0 with a generic radiation-temperature empirical form.

    Equation summary:
        ET0 = c * Rs_mm * (Tmean + offset).

    Parameters
    ----------
    t_mean_c:
        Daily mean air temperature.
    rs_mj_m2_day:
        Incoming solar/global radiation.
    coefficient:
        Empirical scaling coefficient.
    temperature_offset_c:
        Empirical temperature offset.

    Units
    -----
    Temperature is degrees C; Rs is MJ m-2 day-1 and is converted to mm day-1.

    Returns
    -------
    float, numpy.ndarray, or pandas.Series
        ET0 in mm day-1. A pandas.Series input index/name is preserved.
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
    """Estimate ET0 with a Lungeon temperature-humidity empirical form.

    Equation summary:
        ET0 = c * (Tmean + 20)^2 * (1 - RH/100).

    Parameters
    ----------
    t_mean_c:
        Daily mean air temperature.
    rh_mean_pct:
        Mean relative humidity.
    coefficient:
        Empirical Lungeon scaling coefficient.

    Units
    -----
    Temperature is degrees C; relative humidity is percent; output is mm day-1.

    Returns
    -------
    float, numpy.ndarray, or pandas.Series
        ET0 in mm day-1. A pandas.Series input index/name is preserved.
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
    """Estimate ET0 with the Stephens-Stewart radiation-temperature method.

    Equation summary:
        ET0 = c * (Tmean + offset) * Rs_mm.

    Parameters
    ----------
    t_mean_c:
        Daily mean air temperature.
    rs_mj_m2_day:
        Incoming solar/global radiation.
    coefficient:
        Empirical Stephens-Stewart coefficient.
    temperature_offset_c:
        Empirical temperature offset.

    Units
    -----
    Temperature is degrees C; Rs is MJ m-2 day-1 and is converted to mm day-1.

    Returns
    -------
    float, numpy.ndarray, or pandas.Series
        ET0 in mm day-1. A pandas.Series input index/name is preserved.
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
    """Estimate ET0 with a Hicks-Hess radiation-temperature-wind form.

    Equation summary:
        ET0 = c * Rs_mm * (Tmean + 17.8) * (1 + u2).

    Parameters
    ----------
    t_mean_c:
        Daily mean air temperature.
    rs_mj_m2_day:
        Incoming solar/global radiation.
    wind_2m_m_s:
        Wind speed at 2 m height.
    coefficient:
        Empirical Hicks-Hess scaling coefficient.

    Units
    -----
    Temperature is degrees C; Rs is MJ m-2 day-1 and is converted to mm day-1;
    wind is m s-1.

    Returns
    -------
    float, numpy.ndarray, or pandas.Series
        ET0 in mm day-1. A pandas.Series input index/name is preserved.
    """
    result = (
        coefficient
        * as_array(mj_m2_day_to_mm_day(rs_mj_m2_day))
        * (as_array(t_mean_c) + 17.8)
        * (1 + as_array(wind_2m_m_s))
    )
    return restore_from_inputs(result, t_mean_c, rs_mj_m2_day, wind_2m_m_s)


__doc__ = _doc_note("ET0 methods")
