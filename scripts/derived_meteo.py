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
