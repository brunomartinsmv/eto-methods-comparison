from __future__ import annotations

import numpy as np
import pandas as pd

from . import eto_methods
from .fao56 import penman_monteith_fao56

DEFAULT_ALTITUDE_M = 0.0


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


def _required(df: pd.DataFrame, columns: list[str]) -> bool:
    missing = [column for column in columns if column not in df.columns]
    return not missing


def _with_precomputed(result: pd.DataFrame, df: pd.DataFrame, include_precomputed: bool) -> pd.DataFrame:
    if not include_precomputed:
        return result
    for column in df.columns:
        if column.startswith("et_") and column in result.columns:
            result[f"precomputed_{column}"] = df[column]
    return result


def compute_daily_eto(
    df: pd.DataFrame,
    *,
    site_meta: dict,
    include_precomputed: bool = False,
) -> pd.DataFrame:
    """Compute daily ET0 methods from standardized meteorological columns.

    The function expects cleaned, standardized weather columns such as
    `tmed_c`, `tmin_c`, `tmax_c`, `rh_mean_pct`, `wind_mean_ms`,
    `rad_global_mj_m2_d`, `rad_net_mj_m2_d`, and
    `ra_extraterrestre_mj_m2_d`. It does not read or write files.
    """
    result = pd.DataFrame(index=df.index)
    if "date" in df.columns:
        result["date"] = df["date"]

    altitude_m = float(site_meta.get("alt_m", DEFAULT_ALTITUDE_M))
    gamma = psychrometric_constant_kpa_c(altitude_m)

    if _required(df, ["tmed_c", "rad_net_mj_m2_d", "wind_mean_ms"]):
        delta = vapor_pressure_slope_kpa_c(df["tmed_c"])
        es = saturation_vapor_pressure_kpa(df["tmed_c"])
        ea = actual_vapor_pressure_kpa(df)
        result["et_penman_monteith"] = penman_monteith_fao56(
            t_mean_c=df["tmed_c"],
            rn_mj_m2_day=df["rad_net_mj_m2_d"],
            g_mj_m2_day=0.0,
            wind_2m_m_s=df["wind_mean_ms"],
            saturation_vapor_pressure_kpa=es,
            actual_vapor_pressure_kpa=ea,
            delta_kpa_c=delta,
            gamma_kpa_c=gamma,
        )

    if _required(df, ["tmed_c", "ra_extraterrestre_mj_m2_d"]):
        result["et_camargo"] = eto_methods.camargo(
            t_mean_c=df["tmed_c"],
            ra_mj_m2_day=df["ra_extraterrestre_mj_m2_d"],
        )

    if _required(
        df,
        ["tmin_c", "tmax_c", "tmed_c", "ra_extraterrestre_mj_m2_d"],
    ):
        result["et_hargreaves_samani"] = eto_methods.hargreaves_samani(
            t_min_c=df["tmin_c"],
            t_max_c=df["tmax_c"],
            t_mean_c=df["tmed_c"],
            ra_mj_m2_day=df["ra_extraterrestre_mj_m2_d"],
        )

    if _required(df, ["tmed_c", "rad_global_mj_m2_d"]):
        delta = vapor_pressure_slope_kpa_c(df["tmed_c"])
        result["et_makkink"] = eto_methods.makkink(
            delta_kpa_c=delta,
            gamma_kpa_c=gamma,
            rs_mj_m2_day=df["rad_global_mj_m2_d"],
        )
        result["et_turc"] = eto_methods.turc(
            t_mean_c=df["tmed_c"],
            rs_mj_m2_day=df["rad_global_mj_m2_d"],
            rh_mean_pct=df["rh_mean_pct"] if "rh_mean_pct" in df.columns else None,
        )
        result["et_global_radiation"] = eto_methods.global_radiation(
            rs_mj_m2_day=df["rad_global_mj_m2_d"],
        )
        result["et_jensen_heise"] = eto_methods.jensen_heise(
            t_mean_c=df["tmed_c"],
            rs_mj_m2_day=df["rad_global_mj_m2_d"],
        )
        result["et_radiation_temperature"] = eto_methods.radiation_temperature(
            t_mean_c=df["tmed_c"],
            rs_mj_m2_day=df["rad_global_mj_m2_d"],
        )
        result["et_stephens_stewart"] = eto_methods.stephens_stewart(
            t_mean_c=df["tmed_c"],
            rs_mj_m2_day=df["rad_global_mj_m2_d"],
        )
        if "wind_mean_ms" in df.columns:
            result["et_hicks_hess"] = eto_methods.hicks_hess(
                t_mean_c=df["tmed_c"],
                rs_mj_m2_day=df["rad_global_mj_m2_d"],
                wind_2m_m_s=df["wind_mean_ms"],
            )
        if {"rh_mean_pct", "wind_mean_ms"} <= set(df.columns):
            result["et_garcia_lopez"] = eto_methods.garcia_lopez(
                t_mean_c=df["tmed_c"],
                rh_mean_pct=df["rh_mean_pct"],
                wind_2m_m_s=df["wind_mean_ms"],
                rs_mj_m2_day=df["rad_global_mj_m2_d"],
            )

    if _required(df, ["tmed_c"]):
        result["et_mccloud"] = eto_methods.mccloud(t_mean_c=df["tmed_c"])

    if _required(df, ["tmed_c", "rh_mean_pct"]):
        result["et_ivanov"] = eto_methods.ivanov(
            t_mean_c=df["tmed_c"],
            rh_mean_pct=df["rh_mean_pct"],
        )
        result["et_lungeon"] = eto_methods.lungeon(
            t_mean_c=df["tmed_c"],
            rh_mean_pct=df["rh_mean_pct"],
        )

    if _required(df, ["rad_net_mj_m2_d"]):
        result["et_net_radiation"] = eto_methods.net_radiation(
            rn_mj_m2_day=df["rad_net_mj_m2_d"],
        )
        if "tmed_c" in df.columns:
            delta = vapor_pressure_slope_kpa_c(df["tmed_c"])
            result["et_priestley_taylor"] = eto_methods.priestley_taylor(
                delta_kpa_c=delta,
                gamma_kpa_c=gamma,
                rn_mj_m2_day=df["rad_net_mj_m2_d"],
            )

    return _with_precomputed(result, df, include_precomputed)
