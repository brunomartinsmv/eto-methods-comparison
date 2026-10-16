from __future__ import annotations

import warnings
from dataclasses import dataclass
from pathlib import Path

import matplotlib
import numpy as np
import pandas as pd

from . import compute_eto
from .config import METHODS, PIPELINE
from .derived_meteo import (
    actual_vapor_pressure_kpa,
    psychrometric_constant_kpa_c,
    saturation_vapor_pressure_kpa,
    vapor_pressure_slope_kpa_c,
    wind_speed_at_2m,
)
from .fao56 import penman_monteith_fao56
from .feasibility import METHOD_REQUIRED_COLUMNS
from .figure_style import PALETTE, apply_figure_style, style_axis

matplotlib.use("Agg")
import matplotlib.pyplot as plt


def _method_key(column: str) -> str:
    return column.removeprefix("et_")


METHOD_OUTPUT_COLUMNS = {
    _method_key(column): column
    for column in sorted(METHODS.computed_columns | {METHODS.reference_column})
}

METHOD_REQUIRED_COLUMNS = {
    _method_key(column): requirements
    for column, requirements in METHOD_REQUIRED_COLUMNS.items()
    if column in METHOD_OUTPUT_COLUMNS.values()
}


@dataclass(frozen=True)
class SensitivityVariable:
    column: str
    label: str


SENSITIVITY_VARIABLES = [
    SensitivityVariable("tmed_c", "temperatura_media"),
    SensitivityVariable("tmax_c", "temperatura_maxima"),
    SensitivityVariable("tmin_c", "temperatura_minima"),
    SensitivityVariable("rh_mean_pct", "umidade_relativa"),
    SensitivityVariable("wind_mean_ms", "velocidade_vento"),
    SensitivityVariable("rad_global_mj_m2_d", "radiacao_global"),
    SensitivityVariable("rad_net_mj_m2_d", "radiacao_liquida"),
]


def default_perturbations() -> tuple[int, ...]:
    pipeline = PIPELINE
    return tuple(
        range(
            pipeline.sensitivity_perturbation_min_pct,
            pipeline.sensitivity_perturbation_max_pct + 1,
            pipeline.sensitivity_perturbation_step_pct,
        )
    )


PERTURBATIONS = default_perturbations()


def run_oat_sensitivity(
    df: pd.DataFrame,
    *,
    site_meta: dict,
    method: str,
    perturbations: tuple[int, ...] = PERTURBATIONS,
    variables: list[SensitivityVariable] | None = None,
) -> pd.DataFrame:
    """Run one-at-a-time perturbations and summarize mean ET0 response."""
    if method not in METHOD_OUTPUT_COLUMNS:
        available = ", ".join(sorted(METHOD_OUTPUT_COLUMNS))
        raise ValueError(f"Unknown sensitivity method '{method}'. Available methods: {available}")

    variables = variables or SENSITIVITY_VARIABLES
    method_col = METHOD_OUTPUT_COLUMNS[method]
    _require_method_inputs(df, method)

    baseline = compute_eto.compute_daily_eto(df, site_meta=site_meta).frame
    if method_col not in baseline.columns:
        raise ValueError(
            f"Method '{method}' could not be computed. Expected output column '{method_col}' was not produced."
        )
    baseline_series = pd.to_numeric(baseline[method_col], errors="coerce")
    baseline_mean = float(baseline_series.mean())
    baseline_n = int(np.isfinite(baseline_series).sum())

    rows: list[dict[str, object]] = []
    for variable in variables:
        perturbation_columns = _perturbation_columns(df, method, variable)
        if not perturbation_columns:
            message = f"Skipping sensitivity variable '{variable.column}': column not found in input data."
            warnings.warn(message, stacklevel=2)
            rows.append(
                {
                    "method": method,
                    "eto_column": method_col,
                    "variable": variable.label,
                    "column": variable.column,
                    "perturbation_pct": np.nan,
                    "baseline_mean_eto_mm_d": baseline_mean,
                    "perturbed_mean_eto_mm_d": np.nan,
                    "delta_mean_eto_mm_d": np.nan,
                    "relative_delta_pct": np.nan,
                    "n": baseline_n,
                    "status": "missing_column",
                }
            )
            continue

        for perturbation in perturbations:
            perturbed = df.copy()
            factor = 1 + perturbation / 100
            for column in perturbation_columns:
                perturbed[column] = pd.to_numeric(perturbed[column], errors="coerce") * factor
            result = compute_eto.compute_daily_eto(perturbed, site_meta=site_meta).frame
            series = pd.to_numeric(result[method_col], errors="coerce")
            perturbed_mean = float(series.mean())
            delta = perturbed_mean - baseline_mean
            relative_delta = np.nan if baseline_mean == 0 else 100 * delta / baseline_mean
            rows.append(
                {
                    "method": method,
                    "eto_column": method_col,
                    "variable": variable.label,
                    "column": ",".join(perturbation_columns),
                    "perturbation_pct": perturbation,
                    "baseline_mean_eto_mm_d": baseline_mean,
                    "perturbed_mean_eto_mm_d": perturbed_mean,
                    "delta_mean_eto_mm_d": delta,
                    "relative_delta_pct": relative_delta,
                    "n": int(np.isfinite(series).sum()),
                    "status": "ok",
                }
            )

    result = pd.DataFrame(rows)
    if result[result["status"] == "ok"].empty:
        raise ValueError("Sensitivity analysis produced no valid perturbation rows.")
    return result


def _perturbation_columns(
    df: pd.DataFrame, method: str, variable: SensitivityVariable
) -> list[str]:
    if method == "penman_monteith" and variable.column == "rh_mean_pct":
        if {"tmin_c", "tmax_c", "rh_min_pct", "rh_max_pct"} <= set(df.columns):
            return ["rh_min_pct", "rh_max_pct"]
        if "rh_mean_pct" in df.columns:
            return ["rh_mean_pct"]
        return []
    if variable.column in df.columns:
        return [variable.column]
    return []


def write_sensitivity_outputs(
    sensitivity: pd.DataFrame,
    *,
    table_path: Path,
    figure_path: Path,
    title: str,
) -> None:
    table_path.parent.mkdir(parents=True, exist_ok=True)
    figure_path.parent.mkdir(parents=True, exist_ok=True)
    sensitivity.to_csv(table_path, index=False)
    plot_sensitivity(sensitivity, figure_path, title=title)


def plot_sensitivity(sensitivity: pd.DataFrame, output_path: Path, *, title: str) -> None:
    ok = sensitivity[sensitivity["status"] == "ok"].copy()
    if ok.empty:
        raise ValueError("Cannot plot sensitivity without valid perturbation rows.")

    apply_figure_style()
    groups = list(ok.groupby("variable", sort=False))
    panels = [groups[index : index + 4] for index in range(0, len(groups), 4)]
    fig, axes = plt.subplots(
        1, len(panels), figsize=(8 * len(panels), 6), sharex=True, sharey=True, squeeze=False
    )
    colors = [PALETTE[key] for key in ("blue", "red", "teal", "violet")]
    for ax, panel in zip(axes[0], panels, strict=True):
        for index, (variable, group) in enumerate(panel):
            group = group.sort_values("perturbation_pct")
            ax.plot(
                group["perturbation_pct"],
                group["delta_mean_eto_mm_d"],
                marker=["o", "s", "^", "D"][index],
                linestyle=["-", "--", ":", "-."][index],
                markersize=4,
                linewidth=2,
                color=colors[index],
                label=variable.replace("_", " ").title(),
            )
        ax.axhline(0, color=PALETTE["ink"], linewidth=1)
        ax.set(xlabel="Input perturbation (%)", ylabel="Change in mean ET₀ (mm d⁻¹)")
        ax.legend(ncol=2, loc="upper center", bbox_to_anchor=(0.5, -0.2), fontsize=11)
        style_axis(ax)
        ax.grid(axis="x", visible=False)
    fig.suptitle(title, fontsize=18)
    fig.tight_layout(pad=2)
    fig.savefig(output_path, dpi=300, bbox_inches="tight")
    plt.close(fig)


@dataclass(frozen=True)
class RelativeSensitivityDriver:
    variable: str
    column: str


RELATIVE_SENSITIVITY_DRIVERS = (
    RelativeSensitivityDriver("temperature", "tmed_c"),
    RelativeSensitivityDriver("vapor_pressure_deficit", "vpd_kpa"),
    RelativeSensitivityDriver("wind", "wind_2m_ms"),
    RelativeSensitivityDriver("radiation", "rad_net_mj_m2_d"),
)


def default_relative_perturbation_pct() -> float:
    return float(PIPELINE.sensitivity_relative_perturbation_pct)


def run_penman_monteith_relative_sensitivity(
    df: pd.DataFrame,
    *,
    site_meta: dict,
    perturbation_pct: float | None = None,
    drivers: tuple[RelativeSensitivityDriver, ...] = RELATIVE_SENSITIVITY_DRIVERS,
) -> pd.DataFrame:
    """Monthly and annual relative sensitivity of Penman-Monteith ET0.

    The daily coefficient is the central difference

    S_x = (ET0(x + dx) - ET0(x - dx)) / (2 dx) * (x / ET0)

    with dx/x = perturbation_pct/100. Monthly and annual values are the
    unweighted mean of finite daily coefficients. Temperature is perturbed
    at constant vapor-pressure deficit. One site frame per call.
    """
    if perturbation_pct is None:
        perturbation_pct = default_relative_perturbation_pct()
    step = float(perturbation_pct) / 100.0
    if not np.isfinite(step) or step <= 0 or step >= 1:
        raise ValueError(
            "Relative perturbation must be a percentage strictly between 0 and 100."
        )

    _require_relative_inputs(df)
    baseline_state = _penman_monteith_state(df, site_meta)
    baseline = _evaluate_penman_monteith(baseline_state)
    parsed_dates = pd.to_datetime(df["date"], errors="coerce")
    if parsed_dates.isna().all():
        raise ValueError("Cannot compute monthly relative sensitivity without parseable dates.")

    daily: dict[str, pd.Series] = {}
    for driver in drivers:
        plus = _perturb_penman_monteith(baseline_state, driver.variable, 1 + step)
        minus = _perturb_penman_monteith(baseline_state, driver.variable, 1 - step)
        daily[driver.variable] = _daily_relative_coefficient(baseline, plus, minus, step)

    rows: list[dict[str, object]] = []
    dated = parsed_dates.notna()
    month_labels = parsed_dates.dt.strftime("%Y-%m")
    periods = [("month", label) for label in sorted(month_labels.dropna().unique())]
    years = parsed_dates.dt.year.dropna().unique()
    annual_label = str(int(years[0])) if len(years) == 1 else "annual"
    periods.append(("annual", annual_label))

    for period_type, period in periods:
        if period_type == "month":
            mask = dated & (month_labels == period)
        else:
            mask = dated
        for driver in drivers:
            coefficient, mean_eto, n = _summarize_coefficient(
                daily[driver.variable], baseline, mask
            )
            rows.append(
                {
                    "method": "penman_monteith",
                    "period_type": period_type,
                    "period": period,
                    "variable": driver.variable,
                    "column": driver.column,
                    "perturbation_pct": float(perturbation_pct),
                    "baseline_mean_eto_mm_d": mean_eto,
                    "sensitivity_coefficient": coefficient,
                    "n": n,
                }
            )

    result = pd.DataFrame(rows)
    if result.empty or int(result["n"].sum()) == 0:
        raise ValueError("Relative sensitivity produced no finite Penman-Monteith days.")
    return result


def write_relative_sensitivity_table(table: pd.DataFrame, table_path: Path) -> None:
    table_path.parent.mkdir(parents=True, exist_ok=True)
    table.to_csv(table_path, index=False)


def _require_relative_inputs(df: pd.DataFrame) -> None:
    missing = [
        column
        for column in ("date", "tmed_c", "rad_net_mj_m2_d", "wind_mean_ms")
        if column not in df.columns
    ]
    has_humidity = "rh_mean_pct" in df.columns or {
        "tmin_c",
        "tmax_c",
        "rh_min_pct",
        "rh_max_pct",
    } <= set(df.columns)
    if not has_humidity:
        missing.append("rh_mean_pct or tmin_c/tmax_c/rh_min_pct/rh_max_pct")
    if missing:
        joined = ", ".join(missing)
        raise ValueError(
            "Cannot run Penman-Monteith relative sensitivity: "
            f"missing required column(s): {joined}"
        )


@dataclass(frozen=True)
class _PenmanMonteithState:
    t: pd.Series
    rn: pd.Series
    u2: pd.Series
    es: pd.Series
    ea: pd.Series
    delta: pd.Series
    gamma: float


def _penman_monteith_state(df: pd.DataFrame, site_meta: dict) -> _PenmanMonteithState:
    altitude_m = float(site_meta.get("alt_m", compute_eto.DEFAULT_ALTITUDE_M))
    wind_height_m = float(site_meta.get("wind_height_m", compute_eto.DEFAULT_WIND_HEIGHT_M))
    t = pd.to_numeric(df["tmed_c"], errors="coerce")
    return _PenmanMonteithState(
        t=t,
        rn=pd.to_numeric(df["rad_net_mj_m2_d"], errors="coerce"),
        u2=wind_speed_at_2m(
            pd.to_numeric(df["wind_mean_ms"], errors="coerce"),
            measurement_height_m=wind_height_m,
        ),
        es=saturation_vapor_pressure_kpa(t),
        ea=actual_vapor_pressure_kpa(df),
        delta=vapor_pressure_slope_kpa_c(t),
        gamma=psychrometric_constant_kpa_c(altitude_m),
    )


def _evaluate_penman_monteith(state: _PenmanMonteithState) -> pd.Series:
    result = penman_monteith_fao56(
        t_mean_c=state.t,
        rn_mj_m2_day=state.rn,
        g_mj_m2_day=0.0,
        wind_2m_m_s=state.u2,
        saturation_vapor_pressure_kpa=state.es,
        actual_vapor_pressure_kpa=state.ea,
        delta_kpa_c=state.delta,
        gamma_kpa_c=state.gamma,
    )
    if isinstance(result, pd.Series):
        return result
    return pd.Series(np.asarray(result, dtype=float), index=state.t.index)


def _perturb_penman_monteith(
    state: _PenmanMonteithState, variable: str, factor: float
) -> pd.Series:
    if variable == "temperature":
        t_new = state.t * factor
        es_new = saturation_vapor_pressure_kpa(t_new)
        vpd = state.es - state.ea
        return _evaluate_penman_monteith(
            _PenmanMonteithState(
                t=t_new,
                rn=state.rn,
                u2=state.u2,
                es=es_new,
                ea=es_new - vpd,
                delta=vapor_pressure_slope_kpa_c(t_new),
                gamma=state.gamma,
            )
        )
    if variable == "vapor_pressure_deficit":
        vpd_new = (state.es - state.ea) * factor
        return _evaluate_penman_monteith(
            _PenmanMonteithState(
                t=state.t,
                rn=state.rn,
                u2=state.u2,
                es=state.es,
                ea=state.es - vpd_new,
                delta=state.delta,
                gamma=state.gamma,
            )
        )
    if variable == "wind":
        return _evaluate_penman_monteith(
            _PenmanMonteithState(
                t=state.t,
                rn=state.rn,
                u2=state.u2 * factor,
                es=state.es,
                ea=state.ea,
                delta=state.delta,
                gamma=state.gamma,
            )
        )
    if variable == "radiation":
        return _evaluate_penman_monteith(
            _PenmanMonteithState(
                t=state.t,
                rn=state.rn * factor,
                u2=state.u2,
                es=state.es,
                ea=state.ea,
                delta=state.delta,
                gamma=state.gamma,
            )
        )
    known = ", ".join(driver.variable for driver in RELATIVE_SENSITIVITY_DRIVERS)
    raise ValueError(f"Unknown relative sensitivity variable '{variable}'. Expected: {known}")


def _daily_relative_coefficient(
    baseline: pd.Series,
    plus: pd.Series,
    minus: pd.Series,
    step: float,
) -> pd.Series:
    base = baseline.to_numpy(dtype=float)
    high = plus.to_numpy(dtype=float)
    low = minus.to_numpy(dtype=float)
    with np.errstate(divide="ignore", invalid="ignore"):
        coefficient = (high - low) / (2.0 * step * base)
    invalid = ~np.isfinite(base) | ~np.isfinite(high) | ~np.isfinite(low) | (base == 0)
    return pd.Series(coefficient, index=baseline.index).mask(invalid)


def _summarize_coefficient(
    coefficient: pd.Series,
    baseline: pd.Series,
    mask: pd.Series,
) -> tuple[float, float, int]:
    valid = mask.to_numpy(dtype=bool) & np.isfinite(coefficient.to_numpy(dtype=float))
    n = int(valid.sum())
    if n == 0:
        return np.nan, np.nan, 0
    return (
        float(coefficient.to_numpy(dtype=float)[valid].mean()),
        float(baseline.to_numpy(dtype=float)[valid].mean()),
        n,
    )


def _require_method_inputs(df: pd.DataFrame, method: str) -> None:
    required = METHOD_REQUIRED_COLUMNS.get(method, [])
    missing = [column for column in required if column not in df.columns]
    if method == "penman_monteith":
        has_humidity = "rh_mean_pct" in df.columns or {
            "tmin_c",
            "tmax_c",
            "rh_min_pct",
            "rh_max_pct",
        } <= set(df.columns)
        if not has_humidity:
            missing.append("rh_mean_pct or tmin_c/tmax_c/rh_min_pct/rh_max_pct")
    if missing:
        joined = ", ".join(missing)
        raise ValueError(
            f"Cannot run sensitivity for method '{method}': missing required column(s): {joined}"
        )
