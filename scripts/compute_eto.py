from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import pandas as pd

from . import eto_methods
from .config import METHODS
from .derived_meteo import (
    actual_vapor_pressure_kpa,
    psychrometric_constant_kpa_c,
    saturation_vapor_pressure_kpa,
    vapor_pressure_slope_kpa_c,
    wind_speed_at_2m,
)
from .fao56 import penman_monteith_fao56
from .logging_config import get_logger

DEFAULT_ALTITUDE_M = 0.0
DEFAULT_WIND_HEIGHT_M = 10.0
logger = get_logger("compute_eto")

# Re-export derived meteorological helpers for backward compatibility.
__all__ = [
    "ComputeDailyEtoResult",
    "ComputeEtoReport",
    "MethodSkip",
    "PrecomputedComparison",
    "actual_vapor_pressure_kpa",
    "compute_daily_eto",
    "compute_selected_methods",
    "psychrometric_constant_kpa_c",
    "saturation_vapor_pressure_kpa",
    "vapor_pressure_slope_kpa_c",
]


@dataclass(frozen=True)
class MethodSkip:
    column: str
    reason: str


@dataclass(frozen=True)
class PrecomputedComparison:
    column: str
    n_pairs: int
    rmse: float
    mae: float
    max_abs_diff: float


@dataclass
class ComputeEtoReport:
    computed: list[str] = field(default_factory=list)
    skipped: list[MethodSkip] = field(default_factory=list)
    attached_precomputed_only: list[str] = field(default_factory=list)
    comparisons: list[PrecomputedComparison] = field(default_factory=list)

    def log_summary(self, *, site: str | None = None) -> None:
        prefix = f"{site}: " if site else ""
        if self.computed:
            logger.info("%scomputed %d method(s): %s", prefix, len(self.computed), ", ".join(self.computed))
        if self.attached_precomputed_only:
            logger.info(
                "%sattached %d precomputed-only column(s): %s",
                prefix,
                len(self.attached_precomputed_only),
                ", ".join(self.attached_precomputed_only),
            )
        for skip in self.skipped:
            logger.info("%sskipped %s (%s)", prefix, skip.column, skip.reason)
        for comparison in self.comparisons:
            logger.info(
                "%svalidation %s vs precomputed: n=%d rmse=%.4f mae=%.4f max_abs_diff=%.4f",
                prefix,
                comparison.column,
                comparison.n_pairs,
                comparison.rmse,
                comparison.mae,
                comparison.max_abs_diff,
            )


@dataclass(frozen=True)
class ComputeDailyEtoResult:
    frame: pd.DataFrame
    report: ComputeEtoReport


def _missing_columns(df: pd.DataFrame, columns: list[str]) -> list[str]:
    return [column for column in columns if column not in df.columns]


def _record_skip(report: ComputeEtoReport, column: str, missing: list[str]) -> None:
    report.skipped.append(MethodSkip(column, f"missing columns: {', '.join(missing)}"))


def _record_computed(report: ComputeEtoReport, column: str) -> None:
    report.computed.append(column)


def _wind_for_pm(df: pd.DataFrame, site_meta: dict) -> pd.Series:
    wind_height_m = float(site_meta.get("wind_height_m", DEFAULT_WIND_HEIGHT_M))
    return wind_speed_at_2m(df["wind_mean_ms"], measurement_height_m=wind_height_m)


def _compare_with_precomputed(
    result: pd.DataFrame,
    df: pd.DataFrame,
    report: ComputeEtoReport,
) -> pd.DataFrame:
    for column in list(result.columns):
        if not column.startswith("et_") or column not in df.columns:
            continue
        precomputed_col = f"precomputed_{column}"
        result[precomputed_col] = df[column]
        computed = pd.to_numeric(result[column], errors="coerce")
        precomputed = pd.to_numeric(result[precomputed_col], errors="coerce")
        mask = computed.notna() & precomputed.notna()
        n_pairs = int(mask.sum())
        if n_pairs == 0:
            logger.info("validation %s vs precomputed: no overlapping finite pairs", column)
            continue
        diff = computed[mask] - precomputed[mask]
        report.comparisons.append(
            PrecomputedComparison(
                column=column,
                n_pairs=n_pairs,
                rmse=float(np.sqrt(np.mean(diff**2))),
                mae=float(np.mean(np.abs(diff))),
                max_abs_diff=float(np.max(np.abs(diff))),
            )
        )
    return result


def _attach_precomputed_only_columns(
    result: pd.DataFrame,
    df: pd.DataFrame,
    report: ComputeEtoReport,
) -> pd.DataFrame:
    for column in sorted(METHODS.precomputed_only_columns):
        if column in result.columns:
            continue
        if column not in df.columns:
            _record_skip(report, column, ["precomputed column absent from input"])
            continue
        result[column] = df[column]
        report.attached_precomputed_only.append(column)
    return result


def compute_daily_eto(
    df: pd.DataFrame,
    *,
    site_meta: dict,
    include_precomputed: bool = False,
) -> ComputeDailyEtoResult:
    """Compute daily ET0 methods from standardized meteorological columns.

    The function expects cleaned, standardized weather columns such as
    `tmed_c`, `tmin_c`, `tmax_c`, `rh_mean_pct`, `wind_mean_ms`,
    `rad_global_mj_m2_d`, `rad_net_mj_m2_d`, and
    `ra_extraterrestre_mj_m2_d`. It does not read or write files.

    Returns a frame plus a report summarizing which methods were computed,
    skipped, attached from precomputed-only configuration, and compared
    against spreadsheet columns when ``include_precomputed`` is true.
    """
    report = ComputeEtoReport()
    result = pd.DataFrame(index=df.index)
    if "date" in df.columns:
        result["date"] = df["date"]

    altitude_m = float(site_meta.get("alt_m", DEFAULT_ALTITUDE_M))
    gamma = psychrometric_constant_kpa_c(altitude_m)
    wind_2m = _wind_for_pm(df, site_meta) if "wind_mean_ms" in df.columns else None

    missing = _missing_columns(df, ["tmed_c", "rad_net_mj_m2_d", "wind_mean_ms"])
    if not missing:
        delta = vapor_pressure_slope_kpa_c(df["tmed_c"])
        es = saturation_vapor_pressure_kpa(df["tmed_c"])
        ea = actual_vapor_pressure_kpa(df)
        result["et_penman_monteith"] = penman_monteith_fao56(
            t_mean_c=df["tmed_c"],
            rn_mj_m2_day=df["rad_net_mj_m2_d"],
            g_mj_m2_day=0.0,
            wind_2m_m_s=wind_2m,
            saturation_vapor_pressure_kpa=es,
            actual_vapor_pressure_kpa=ea,
            delta_kpa_c=delta,
            gamma_kpa_c=gamma,
        )
        _record_computed(report, "et_penman_monteith")
    else:
        _record_skip(report, "et_penman_monteith", missing)

    missing = _missing_columns(df, ["tmed_c", "ra_extraterrestre_mj_m2_d"])
    if not missing:
        result["et_camargo"] = eto_methods.camargo(
            t_mean_c=df["tmed_c"],
            ra_mj_m2_day=df["ra_extraterrestre_mj_m2_d"],
        )
        _record_computed(report, "et_camargo")
    else:
        _record_skip(report, "et_camargo", missing)

    missing = _missing_columns(df, ["tmin_c", "tmax_c", "tmed_c", "ra_extraterrestre_mj_m2_d"])
    if not missing:
        result["et_hargreaves_samani"] = eto_methods.hargreaves_samani(
            t_min_c=df["tmin_c"],
            t_max_c=df["tmax_c"],
            t_mean_c=df["tmed_c"],
            ra_mj_m2_day=df["ra_extraterrestre_mj_m2_d"],
        )
        _record_computed(report, "et_hargreaves_samani")
    else:
        _record_skip(report, "et_hargreaves_samani", missing)

    missing = _missing_columns(df, ["tmed_c", "rad_global_mj_m2_d"])
    if not missing:
        delta = vapor_pressure_slope_kpa_c(df["tmed_c"])
        result["et_makkink"] = eto_methods.makkink(
            delta_kpa_c=delta,
            gamma_kpa_c=gamma,
            rs_mj_m2_day=df["rad_global_mj_m2_d"],
        )
        _record_computed(report, "et_makkink")
        result["et_turc"] = eto_methods.turc(
            t_mean_c=df["tmed_c"],
            rs_mj_m2_day=df["rad_global_mj_m2_d"],
            rh_mean_pct=df["rh_mean_pct"] if "rh_mean_pct" in df.columns else None,
        )
        _record_computed(report, "et_turc")
        result["et_global_radiation"] = eto_methods.global_radiation(
            rs_mj_m2_day=df["rad_global_mj_m2_d"],
        )
        _record_computed(report, "et_global_radiation")
        result["et_jensen_heise"] = eto_methods.jensen_heise(
            t_mean_c=df["tmed_c"],
            rs_mj_m2_day=df["rad_global_mj_m2_d"],
        )
        _record_computed(report, "et_jensen_heise")
        result["et_radiation_temperature"] = eto_methods.radiation_temperature(
            t_mean_c=df["tmed_c"],
            rs_mj_m2_day=df["rad_global_mj_m2_d"],
        )
        _record_computed(report, "et_radiation_temperature")
        result["et_stephens_stewart"] = eto_methods.stephens_stewart(
            t_mean_c=df["tmed_c"],
            rs_mj_m2_day=df["rad_global_mj_m2_d"],
        )
        _record_computed(report, "et_stephens_stewart")
        if wind_2m is not None:
            result["et_hicks_hess"] = eto_methods.hicks_hess(
                t_mean_c=df["tmed_c"],
                rs_mj_m2_day=df["rad_global_mj_m2_d"],
                wind_2m_m_s=wind_2m,
            )
            _record_computed(report, "et_hicks_hess")
        else:
            _record_skip(report, "et_hicks_hess", ["wind_mean_ms"])
        if {"rh_mean_pct", "wind_mean_ms"} <= set(df.columns) and wind_2m is not None:
            result["et_garcia_lopez"] = eto_methods.garcia_lopez(
                t_mean_c=df["tmed_c"],
                rh_mean_pct=df["rh_mean_pct"],
                wind_2m_m_s=wind_2m,
                rs_mj_m2_day=df["rad_global_mj_m2_d"],
            )
            _record_computed(report, "et_garcia_lopez")
        else:
            missing_optional = _missing_columns(df, ["rh_mean_pct", "wind_mean_ms"])
            _record_skip(report, "et_garcia_lopez", missing_optional)
    else:
        for column in (
            "et_makkink",
            "et_turc",
            "et_global_radiation",
            "et_jensen_heise",
            "et_radiation_temperature",
            "et_stephens_stewart",
            "et_hicks_hess",
            "et_garcia_lopez",
        ):
            _record_skip(report, column, missing)

    missing = _missing_columns(df, ["tmed_c"])
    if not missing:
        result["et_mccloud"] = eto_methods.mccloud(t_mean_c=df["tmed_c"])
        _record_computed(report, "et_mccloud")
    else:
        _record_skip(report, "et_mccloud", missing)

    missing = _missing_columns(df, ["tmed_c", "rh_mean_pct"])
    if not missing:
        result["et_ivanov"] = eto_methods.ivanov(
            t_mean_c=df["tmed_c"],
            rh_mean_pct=df["rh_mean_pct"],
        )
        _record_computed(report, "et_ivanov")
        result["et_lungeon"] = eto_methods.lungeon(
            t_mean_c=df["tmed_c"],
            rh_mean_pct=df["rh_mean_pct"],
        )
        _record_computed(report, "et_lungeon")
    else:
        _record_skip(report, "et_ivanov", missing)
        _record_skip(report, "et_lungeon", missing)

    missing = _missing_columns(df, ["rad_net_mj_m2_d"])
    if not missing:
        result["et_net_radiation"] = eto_methods.net_radiation(
            rn_mj_m2_day=df["rad_net_mj_m2_d"],
        )
        _record_computed(report, "et_net_radiation")
        if "tmed_c" in df.columns:
            delta = vapor_pressure_slope_kpa_c(df["tmed_c"])
            result["et_priestley_taylor"] = eto_methods.priestley_taylor(
                delta_kpa_c=delta,
                gamma_kpa_c=gamma,
                rn_mj_m2_day=df["rad_net_mj_m2_d"],
            )
            _record_computed(report, "et_priestley_taylor")
        else:
            _record_skip(report, "et_priestley_taylor", ["tmed_c"])
    else:
        _record_skip(report, "et_net_radiation", missing)
        _record_skip(report, "et_priestley_taylor", missing + (["tmed_c"] if "tmed_c" not in df.columns else []))

    result = _attach_precomputed_only_columns(result, df, report)
    if include_precomputed:
        result = _compare_with_precomputed(result, df, report)

    return ComputeDailyEtoResult(frame=result, report=report)


def compute_selected_methods(
    df: pd.DataFrame,
    *,
    method_columns: list[str],
    site_meta: dict,
    include_reference: bool = True,
) -> ComputeDailyEtoResult:
    """Compute a subset of ET0 methods plus the reference when requested."""
    full = compute_daily_eto(df, site_meta=site_meta, include_precomputed=False)
    selected = list(method_columns)
    if include_reference and "et_penman_monteith" not in selected:
        selected.append("et_penman_monteith")

    frame = pd.DataFrame(index=df.index)
    if "date" in df.columns:
        frame["date"] = df["date"]

    report = ComputeEtoReport()
    for column in selected:
        if column in full.frame.columns:
            frame[column] = full.frame[column]
            if column in full.report.computed:
                report.computed.append(column)
            elif column in full.report.attached_precomputed_only:
                report.attached_precomputed_only.append(column)
        else:
            skip = next((item for item in full.report.skipped if item.column == column), None)
            if skip:
                report.skipped.append(skip)
            else:
                report.skipped.append(MethodSkip(column, "method not produced"))

    return ComputeDailyEtoResult(frame=frame, report=report)
