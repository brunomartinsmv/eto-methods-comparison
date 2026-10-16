"""FAO-56 Penman-Monteith scenarios with missing wind, humidity, or radiation.

Each scenario is scored against the full-data pipeline Penman-Monteith on the
days where that reference and every series in the table are finite. Row order
is the scenario list. It is not a performance ranking.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import numpy as np
import pandas as pd

from . import eto_methods, metrics
from .config import REFERENCE_COLUMN
from .derived_meteo import (
    FAO56_COASTAL_K_RS,
    FAO56_DEFAULT_WIND_2M_MS,
    FAO56_INTERIOR_K_RS,
    FAO56_MINIMUM_WIND_2M_MS,
    actual_vapor_pressure_from_tmin_kpa,
    actual_vapor_pressure_kpa,
    net_radiation_from_solar_mj_m2_day,
    psychrometric_constant_kpa_c,
    saturation_vapor_pressure_kpa,
    solar_radiation_from_temperature_mj_m2_day,
    vapor_pressure_slope_kpa_c,
    wind_speed_at_2m,
)
from .fao56 import penman_monteith_fao56
from .naming import daily_eto_filename

DEFAULT_WIND_HEIGHT_M = 10.0
DEFAULT_ALTITUDE_M = 0.0

REFERENCE_SOURCE_PIPELINE = "pipeline_daily_eto"
REFERENCE_SOURCE_RECOMPUTED = "recomputed_penman_monteith"
COMPARISON_DAYS = "common_finite"

SCENARIO_ORDER = (
    "pm_full",
    "pm_wind_replaced",
    "pm_humidity_replaced",
    "pm_radiation_replaced",
    "pm_pmt",
    "hargreaves_samani",
    "turc",
)

_REQUIRED_COLUMNS = (
    "date",
    "tmed_c",
    "tmin_c",
    "tmax_c",
    "wind_mean_ms",
    "rad_global_mj_m2_d",
    "rad_net_mj_m2_d",
    "ra_extraterrestre_mj_m2_d",
)

_TABLE_COLUMNS = (
    "scenario",
    "equation",
    "inputs_replaced",
    "wind_source",
    "humidity_source",
    "radiation_source",
    "k_rs",
    "k_rs_source",
    "substitute_wind_2m_m_s",
    "n",
    "rmse",
    "mae",
    "mbe",
    "r",
    "r2",
    "willmott_d",
    "c",
    "classification",
    "reference",
    "reference_source",
    "comparison_days",
)


@dataclass(frozen=True)
class LimitedDataSettings:
    """FAO-56 substitutes used when an input is treated as missing."""

    wind_2m_m_s: float
    wind_source: str
    k_rs: float
    k_rs_source: str


@dataclass(frozen=True)
class _Scenario:
    scenario: str
    equation: str
    inputs_replaced: str
    replace_wind: bool
    replace_humidity: bool
    replace_radiation: bool


_PM_SCENARIOS = (
    _Scenario("pm_full", "penman_monteith", "none", False, False, False),
    _Scenario("pm_wind_replaced", "penman_monteith", "wind", True, False, False),
    _Scenario("pm_humidity_replaced", "penman_monteith", "humidity", False, True, False),
    _Scenario("pm_radiation_replaced", "penman_monteith", "radiation", False, False, True),
    _Scenario(
        "pm_pmt",
        "penman_monteith",
        "wind+humidity+radiation",
        True,
        True,
        True,
    ),
)


def resolve_limited_data_settings(
    site_meta: dict,
    *,
    k_rs: float | None = None,
    wind_2m_m_s: float | None = None,
) -> LimitedDataSettings:
    """Resolve wind and kRs substitutes from overrides, then site metadata, then FAO-56 defaults."""
    if wind_2m_m_s is not None:
        wind = float(wind_2m_m_s)
        wind_source = "override"
    elif site_meta.get("regional_wind_2m_ms") is not None:
        wind = float(site_meta["regional_wind_2m_ms"])
        wind_source = "regional"
    else:
        wind = FAO56_DEFAULT_WIND_2M_MS
        wind_source = "fao56_default"
    if wind < FAO56_MINIMUM_WIND_2M_MS:
        wind = FAO56_MINIMUM_WIND_2M_MS

    if k_rs is not None:
        coefficient = float(k_rs)
        k_rs_source = "override"
    elif site_meta.get("k_rs") is not None:
        coefficient = float(site_meta["k_rs"])
        k_rs_source = "site"
    else:
        setting = str(site_meta.get("radiation_setting", "interior")).strip().lower()
        if setting == "coastal":
            coefficient = FAO56_COASTAL_K_RS
            k_rs_source = "fao56_coastal"
        elif setting == "interior":
            coefficient = FAO56_INTERIOR_K_RS
            k_rs_source = "fao56_interior"
        else:
            raise ValueError(
                "radiation_setting must be 'interior' or 'coastal' "
                f"(got {setting!r})"
            )
    if coefficient <= 0:
        raise ValueError("kRs must be positive")
    return LimitedDataSettings(
        wind_2m_m_s=wind,
        wind_source=wind_source,
        k_rs=coefficient,
        k_rs_source=k_rs_source,
    )


def _require_weather_columns(df: pd.DataFrame) -> None:
    missing = [column for column in _REQUIRED_COLUMNS if column not in df.columns]
    if missing:
        raise ValueError(f"Limited-data scenarios need columns: {', '.join(missing)}")


def _penman_monteith(
    df: pd.DataFrame,
    site_meta: dict,
    *,
    wind_2m: pd.Series,
    actual_vapor_pressure: pd.Series,
    rn_mj_m2_day: pd.Series,
) -> pd.Series:
    altitude_m = float(site_meta.get("alt_m", DEFAULT_ALTITUDE_M))
    return penman_monteith_fao56(
        t_mean_c=df["tmed_c"],
        rn_mj_m2_day=rn_mj_m2_day,
        g_mj_m2_day=0.0,
        wind_2m_m_s=wind_2m,
        saturation_vapor_pressure_kpa=saturation_vapor_pressure_kpa(df["tmed_c"]),
        actual_vapor_pressure_kpa=actual_vapor_pressure,
        delta_kpa_c=vapor_pressure_slope_kpa_c(df["tmed_c"]),
        gamma_kpa_c=psychrometric_constant_kpa_c(altitude_m),
    )


def _measured_wind(df: pd.DataFrame, site_meta: dict) -> pd.Series:
    height_m = float(site_meta.get("wind_height_m", DEFAULT_WIND_HEIGHT_M))
    return wind_speed_at_2m(df["wind_mean_ms"], measurement_height_m=height_m)


def _constant_wind(df: pd.DataFrame, wind_2m_m_s: float) -> pd.Series:
    return pd.Series(float(wind_2m_m_s), index=df.index, dtype=float)


def limited_data_series(
    df: pd.DataFrame,
    *,
    site_meta: dict,
    settings: LimitedDataSettings,
) -> dict[str, pd.Series]:
    """Return daily ET0 for each limited-data scenario, indexed like ``df``."""
    _require_weather_columns(df)
    altitude_m = float(site_meta.get("alt_m", DEFAULT_ALTITUDE_M))
    measured_wind = _measured_wind(df, site_meta)
    measured_ea = actual_vapor_pressure_kpa(df)
    tmin_ea = actual_vapor_pressure_from_tmin_kpa(df["tmin_c"])
    estimated_rs = solar_radiation_from_temperature_mj_m2_day(
        df["tmin_c"],
        df["tmax_c"],
        df["ra_extraterrestre_mj_m2_d"],
        k_rs=settings.k_rs,
        altitude_m=altitude_m,
    )
    rn_from_measured_ea = net_radiation_from_solar_mj_m2_day(
        df["tmin_c"],
        df["tmax_c"],
        measured_ea,
        estimated_rs,
        df["ra_extraterrestre_mj_m2_d"],
        altitude_m=altitude_m,
    )
    rn_from_tmin_ea = net_radiation_from_solar_mj_m2_day(
        df["tmin_c"],
        df["tmax_c"],
        tmin_ea,
        estimated_rs,
        df["ra_extraterrestre_mj_m2_d"],
        altitude_m=altitude_m,
    )
    substitute_wind = _constant_wind(df, settings.wind_2m_m_s)

    series: dict[str, pd.Series] = {}
    for scenario in _PM_SCENARIOS:
        wind = substitute_wind if scenario.replace_wind else measured_wind
        ea = tmin_ea if scenario.replace_humidity else measured_ea
        if scenario.replace_radiation:
            rn = rn_from_tmin_ea if scenario.replace_humidity else rn_from_measured_ea
        else:
            rn = df["rad_net_mj_m2_d"]
        series[scenario.scenario] = _penman_monteith(
            df,
            site_meta,
            wind_2m=wind,
            actual_vapor_pressure=ea,
            rn_mj_m2_day=rn,
        )

    series["hargreaves_samani"] = eto_methods.hargreaves_samani(
        t_min_c=df["tmin_c"],
        t_max_c=df["tmax_c"],
        t_mean_c=df["tmed_c"],
        ra_mj_m2_day=df["ra_extraterrestre_mj_m2_d"],
    )
    series["turc"] = eto_methods.turc(
        t_mean_c=df["tmed_c"],
        rs_mj_m2_day=df["rad_global_mj_m2_d"],
        rh_mean_pct=df["rh_mean_pct"] if "rh_mean_pct" in df.columns else None,
    )
    return series


def pipeline_reference(
    weather: pd.DataFrame,
    *,
    site: str,
    site_meta: dict,
    settings: LimitedDataSettings,
    results_dir: Path | None,
    require_results_file: bool,
) -> tuple[pd.Series, str]:
    """Return the full-data Penman-Monteith reference aligned to ``weather``.

    Uses ``outputs/results/{site}_daily_eto.csv`` when that file is present.
    Otherwise recomputes the full-data equation from the cleaned weather.
    """
    if results_dir is not None:
        path = results_dir / daily_eto_filename(site)
        if path.exists():
            computed = pd.read_csv(path, parse_dates=["date"])
            if REFERENCE_COLUMN not in computed.columns:
                raise ValueError(f"Reference column '{REFERENCE_COLUMN}' not found in {path}")
            merged = weather[["date"]].merge(
                computed[["date", REFERENCE_COLUMN]],
                on="date",
                how="left",
                validate="one_to_one",
            )
            if merged[REFERENCE_COLUMN].isna().any():
                raise ValueError(
                    f"Pipeline Penman-Monteith does not cover all cleaned dates for {site}"
                )
            reference = pd.Series(
                pd.to_numeric(merged[REFERENCE_COLUMN], errors="coerce").to_numpy(),
                index=weather.index,
                dtype=float,
            )
            return reference, REFERENCE_SOURCE_PIPELINE
        if require_results_file:
            raise ValueError(f"Computed results file '{path}' not found for {site}")

    full = limited_data_series(weather, site_meta=site_meta, settings=settings)["pm_full"]
    return full.astype(float), REFERENCE_SOURCE_RECOMPUTED


def _scenario_metadata(
    settings: LimitedDataSettings,
    *,
    turc_uses_humidity: bool,
) -> dict[str, dict[str, object]]:
    wind_label = {
        "fao56_default": "fao56_default",
        "regional": "regional",
        "override": "override",
    }[settings.wind_source]
    rows: dict[str, dict[str, object]] = {}
    for scenario in _PM_SCENARIOS:
        uses_estimated_radiation = scenario.replace_radiation
        rows[scenario.scenario] = {
            "equation": scenario.equation,
            "inputs_replaced": scenario.inputs_replaced,
            "wind_source": wind_label if scenario.replace_wind else "measured_2m",
            "humidity_source": "fao56_tdew_tmin" if scenario.replace_humidity else "measured",
            "radiation_source": (
                "fao56_temperature_rn" if uses_estimated_radiation else "measured_rn"
            ),
            "k_rs": settings.k_rs if uses_estimated_radiation else np.nan,
            "k_rs_source": settings.k_rs_source if uses_estimated_radiation else "",
            "substitute_wind_2m_m_s": (
                settings.wind_2m_m_s if scenario.replace_wind else np.nan
            ),
        }
    rows["hargreaves_samani"] = {
        "equation": "hargreaves_samani",
        "inputs_replaced": "not_applicable",
        "wind_source": "not_used",
        "humidity_source": "not_used",
        "radiation_source": "extraterrestrial_ra",
        "k_rs": np.nan,
        "k_rs_source": "",
        "substitute_wind_2m_m_s": np.nan,
    }
    rows["turc"] = {
        "equation": "turc",
        "inputs_replaced": "not_applicable",
        "wind_source": "not_used",
        "humidity_source": "measured" if turc_uses_humidity else "not_used",
        "radiation_source": "measured_rs",
        "k_rs": np.nan,
        "k_rs_source": "",
        "substitute_wind_2m_m_s": np.nan,
    }
    return rows


def score_limited_data(
    weather: pd.DataFrame,
    reference: pd.Series,
    *,
    site_meta: dict,
    settings: LimitedDataSettings,
    reference_source: str,
) -> pd.DataFrame:
    """Score every scenario against ``reference`` on the common finite days."""
    series = limited_data_series(weather, site_meta=site_meta, settings=settings)
    missing = [name for name in SCENARIO_ORDER if name not in series]
    if missing:
        raise ValueError(f"Missing limited-data series: {', '.join(missing)}")

    mask = np.isfinite(pd.to_numeric(reference, errors="coerce").to_numpy())
    for name in SCENARIO_ORDER:
        mask &= np.isfinite(pd.to_numeric(series[name], errors="coerce").to_numpy())
    n_days = int(mask.sum())
    if n_days == 0:
        raise ValueError("No common finite days for the limited-data comparison")

    frame = pd.DataFrame({"reference": pd.to_numeric(reference, errors="coerce")})
    for name in SCENARIO_ORDER:
        frame[name] = pd.to_numeric(series[name], errors="coerce")
    scored = metrics.compute_metrics(frame.loc[mask], "reference", list(SCENARIO_ORDER))
    metadata = _scenario_metadata(
        settings,
        turc_uses_humidity="rh_mean_pct" in weather.columns,
    )
    rows = []
    for _, metric_row in scored.iterrows():
        scenario = str(metric_row["method"])
        info = metadata[scenario]
        rows.append(
            {
                "scenario": scenario,
                "equation": info["equation"],
                "inputs_replaced": info["inputs_replaced"],
                "wind_source": info["wind_source"],
                "humidity_source": info["humidity_source"],
                "radiation_source": info["radiation_source"],
                "k_rs": info["k_rs"],
                "k_rs_source": info["k_rs_source"],
                "substitute_wind_2m_m_s": info["substitute_wind_2m_m_s"],
                "n": n_days,
                "rmse": metric_row["rmse"],
                "mae": metric_row["mae"],
                "mbe": metric_row["mbe"],
                "r": metric_row["r"],
                "r2": metric_row["r2"],
                "willmott_d": metric_row["willmott_d"],
                "c": metric_row["c"],
                "classification": metric_row["classification"],
                "reference": REFERENCE_COLUMN,
                "reference_source": reference_source,
                "comparison_days": COMPARISON_DAYS,
            }
        )
    table = pd.DataFrame(rows)
    return table.loc[:, list(_TABLE_COLUMNS)]


def limited_data_metrics_table(
    weather: pd.DataFrame,
    *,
    site: str,
    site_meta: dict,
    settings: LimitedDataSettings | None = None,
    results_dir: Path | None = None,
    require_results_file: bool = False,
) -> pd.DataFrame:
    """Build the limited-data metrics table for one site."""
    resolved = settings or resolve_limited_data_settings(site_meta)
    reference, reference_source = pipeline_reference(
        weather,
        site=site,
        site_meta=site_meta,
        settings=resolved,
        results_dir=results_dir,
        require_results_file=require_results_file,
    )
    return score_limited_data(
        weather,
        reference,
        site_meta=site_meta,
        settings=resolved,
        reference_source=reference_source,
    )
