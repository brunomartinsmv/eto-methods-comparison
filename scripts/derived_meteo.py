from __future__ import annotations

import math

import numpy as np
import pandas as pd

DEFAULT_WIND_MEASUREMENT_HEIGHT_M = 10.0


def saturation_vapor_pressure_kpa(t_c: pd.Series) -> pd.Series:
    """Return saturation vapor pressure in kPa for air temperature in degrees C."""
    return 0.6108 * np.exp((17.27 * t_c) / (t_c + 237.3))


def vapor_pressure_slope_kpa_c(t_c: pd.Series) -> pd.Series:
    """Return slope of saturation vapor pressure curve in kPa C-1."""
    es = saturation_vapor_pressure_kpa(t_c)
    return 4098 * es / (t_c + 237.3) ** 2


def atmospheric_pressure_kpa(altitude_m: float) -> float:
    """Return atmospheric pressure in kPa from altitude in m using FAO-56."""
    return 101.3 * ((293 - 0.0065 * altitude_m) / 293) ** 5.26


def psychrometric_constant_kpa_c(altitude_m: float) -> float:
    """Return psychrometric constant in kPa C-1 from altitude in m."""
    return 0.000665 * atmospheric_pressure_kpa(altitude_m)


def actual_vapor_pressure_kpa(df: pd.DataFrame) -> pd.Series:
    """Estimate actual vapor pressure in kPa from standardized humidity columns."""
    if {"tmin_c", "tmax_c", "rh_min_pct", "rh_max_pct"} <= set(df.columns):
        es_tmin = saturation_vapor_pressure_kpa(df["tmin_c"])
        es_tmax = saturation_vapor_pressure_kpa(df["tmax_c"])
        return (es_tmin * df["rh_max_pct"] / 100 + es_tmax * df["rh_min_pct"] / 100) / 2
    if "rh_mean_pct" in df.columns:
        return saturation_vapor_pressure_kpa(df["tmed_c"]) * df["rh_mean_pct"] / 100
    raise ValueError("Need humidity columns to estimate actual vapor pressure")


def wind_speed_at_2m(
    wind_m_s: pd.Series,
    *,
    measurement_height_m: float = DEFAULT_WIND_MEASUREMENT_HEIGHT_M,
) -> pd.Series:
    """Convert wind speed measured at *measurement_height_m* to 2 m height (FAO-56 eq. 47)."""
    if measurement_height_m <= 0:
        raise ValueError("Wind measurement height must be positive")
    if abs(measurement_height_m - 2.0) < 1e-9:
        return wind_m_s
    log_term = math.log(67.8 * measurement_height_m - 5.42)
    factor = 4.87 / log_term
    return pd.to_numeric(wind_m_s, errors="coerce") * factor


def extraterrestrial_radiation_mj_m2_day(
    day_of_year: pd.Series | np.ndarray,
    latitude_deg: float,
) -> pd.Series:
    """Return extraterrestrial radiation Ra in MJ m-2 day-1 (FAO-56 eq. 21)."""
    julian = pd.to_numeric(day_of_year, errors="coerce")
    lat_rad = math.radians(latitude_deg)
    dr = 1 + 0.033 * np.cos(2 * np.pi / 365 * julian)
    solar_declination = 0.409 * np.sin(2 * np.pi / 365 * julian - 1.39)
    sunset_hour_angle = np.arccos(np.clip(-np.tan(lat_rad) * np.tan(solar_declination), -1.0, 1.0))
    ra = (
        (24 * 60 / np.pi)
        * 0.0820
        * dr
        * (
            sunset_hour_angle * np.sin(lat_rad) * np.sin(solar_declination)
            + np.cos(lat_rad) * np.cos(solar_declination) * np.sin(sunset_hour_angle)
        )
    )
    if isinstance(day_of_year, pd.Series):
        return pd.Series(ra, index=day_of_year.index, name="ra_extraterrestre_mj_m2_d")
    return pd.Series(ra)


def day_of_year_from_dates(dates: pd.Series) -> pd.Series:
    """Return day-of-year (1-366) for a date series."""
    parsed = pd.to_datetime(dates, errors="coerce")
    return parsed.dt.dayofyear.astype("Int64")


# FAO-56 eq. 39. Daily Stefan-Boltzmann constant, MJ K-4 m-2 day-1.
STEFAN_BOLTZMANN_MJ_M2_DAY_K4 = 4.903e-9
# FAO-56 grass-reference albedo (eq. 38).
REFERENCE_ALBEDO = 0.23
# FAO-56 eq. 50. Interior locations use 0.16; coastal locations use 0.19.
FAO56_INTERIOR_K_RS = 0.16
FAO56_COASTAL_K_RS = 0.19
# FAO-56 missing-wind substitute: mean of about 2 000 stations, already at 2 m.
FAO56_DEFAULT_WIND_2M_MS = 2.0
# FAO-56 lower bound applied to the wind substitute inside the ET0 equation.
FAO56_MINIMUM_WIND_2M_MS = 0.5


def clear_sky_radiation_mj_m2_day(
    ra_mj_m2_day: pd.Series | np.ndarray | float,
    altitude_m: float | None = None,
    *,
    elevation_m: float | None = None,
) -> pd.Series | np.ndarray | float:
    """Clear-sky solar radiation Rso (FAO-56 eq. 37), MJ m-2 day-1.

    Rso = (0.75 + 2e-5 * z) * Ra. At sea level this matches eq. 36 with as+bs = 0.75.
    ``elevation_m`` is the same station elevation as ``altitude_m``.
    """
    if altitude_m is None and elevation_m is None:
        raise ValueError("station elevation is required")
    if (
        altitude_m is not None
        and elevation_m is not None
        and float(altitude_m) != float(elevation_m)
    ):
        raise ValueError("altitude_m and elevation_m differ")
    station_elevation_m = elevation_m if elevation_m is not None else altitude_m
    ra = pd.to_numeric(ra_mj_m2_day, errors="coerce")
    rso = (0.75 + 2e-5 * float(station_elevation_m)) * ra
    if isinstance(ra_mj_m2_day, pd.Series):
        return pd.Series(rso, index=ra_mj_m2_day.index, name="rso_mj_m2_d")
    return rso


def solar_radiation_from_temperature_mj_m2_day(
    t_min_c: pd.Series | np.ndarray | float,
    t_max_c: pd.Series | np.ndarray | float,
    ra_mj_m2_day: pd.Series | np.ndarray | float,
    *,
    k_rs: float,
    altitude_m: float,
) -> pd.Series | np.ndarray | float:
    """Solar radiation from the temperature range (FAO-56 eq. 50), MJ m-2 day-1.

    Rs = kRs * sqrt(Tmax - Tmin) * Ra, limited to clear-sky radiation Rso.
    """
    if k_rs <= 0:
        raise ValueError("kRs must be positive")
    tmin = pd.to_numeric(t_min_c, errors="coerce")
    tmax = pd.to_numeric(t_max_c, errors="coerce")
    ra = pd.to_numeric(ra_mj_m2_day, errors="coerce")
    rs = k_rs * np.sqrt(np.maximum(tmax - tmin, 0.0)) * ra
    rso = clear_sky_radiation_mj_m2_day(ra, altitude_m)
    rs = np.minimum(rs, pd.to_numeric(rso, errors="coerce"))
    if isinstance(t_min_c, pd.Series):
        return pd.Series(np.asarray(rs, dtype=float), index=t_min_c.index, name="rs_estimated_mj_m2_d")
    return rs


def net_longwave_radiation_mj_m2_day(
    t_min_c: pd.Series | np.ndarray | float,
    t_max_c: pd.Series | np.ndarray | float,
    actual_vapor_pressure_kpa: pd.Series | np.ndarray | float,
    rs_mj_m2_day: pd.Series | np.ndarray | float,
    rso_mj_m2_day: pd.Series | np.ndarray | float,
) -> pd.Series | np.ndarray | float:
    """Net outgoing longwave radiation Rnl (FAO-56 eq. 39), MJ m-2 day-1.

    Rs/Rso is limited to at most 1. FAO-56 does not impose a lower bound.
    """
    tmin_k = pd.to_numeric(t_min_c, errors="coerce") + 273.16
    tmax_k = pd.to_numeric(t_max_c, errors="coerce") + 273.16
    ea = np.maximum(pd.to_numeric(actual_vapor_pressure_kpa, errors="coerce"), 0.0)
    rs = pd.to_numeric(rs_mj_m2_day, errors="coerce")
    rso = pd.to_numeric(rso_mj_m2_day, errors="coerce")
    with np.errstate(divide="ignore", invalid="ignore"):
        ratio = np.where(rso > 0, rs / rso, np.nan)
    ratio = np.minimum(ratio, 1.0)
    sigma_t4 = STEFAN_BOLTZMANN_MJ_M2_DAY_K4 * (np.power(tmax_k, 4) + np.power(tmin_k, 4)) / 2.0
    humidity_term = 0.34 - 0.14 * np.sqrt(ea)
    cloud_term = 1.35 * ratio - 0.35
    rnl = sigma_t4 * humidity_term * cloud_term
    if isinstance(t_min_c, pd.Series):
        return pd.Series(np.asarray(rnl, dtype=float), index=t_min_c.index, name="rnl_mj_m2_d")
    return rnl


def net_radiation_from_solar_mj_m2_day(
    t_min_c: pd.Series | np.ndarray | float,
    t_max_c: pd.Series | np.ndarray | float,
    actual_vapor_pressure_kpa: pd.Series | np.ndarray | float,
    rs_mj_m2_day: pd.Series | np.ndarray | float,
    ra_mj_m2_day: pd.Series | np.ndarray | float,
    *,
    altitude_m: float,
    albedo: float = REFERENCE_ALBEDO,
) -> pd.Series | np.ndarray | float:
    """Net radiation Rn = Rns - Rnl (FAO-56 eqs. 37-40), MJ m-2 day-1."""
    if not 0.0 <= albedo <= 1.0:
        raise ValueError("Albedo must be between 0 and 1")
    rso = clear_sky_radiation_mj_m2_day(ra_mj_m2_day, altitude_m)
    rs = pd.to_numeric(rs_mj_m2_day, errors="coerce")
    rns = (1.0 - albedo) * rs
    rnl = net_longwave_radiation_mj_m2_day(
        t_min_c,
        t_max_c,
        actual_vapor_pressure_kpa,
        rs,
        rso,
    )
    rn = rns - pd.to_numeric(rnl, errors="coerce")
    if isinstance(t_min_c, pd.Series):
        return pd.Series(np.asarray(rn, dtype=float), index=t_min_c.index, name="rn_estimated_mj_m2_d")
    return rn


def actual_vapor_pressure_from_tmin_kpa(
    t_min_c: pd.Series | np.ndarray | float,
) -> pd.Series | np.ndarray | float:
    """Actual vapor pressure when dewpoint is taken as Tmin (FAO-56 eq. 48), kPa."""
    return saturation_vapor_pressure_kpa(t_min_c)
