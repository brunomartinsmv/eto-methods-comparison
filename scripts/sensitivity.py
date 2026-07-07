from __future__ import annotations

import warnings
from dataclasses import dataclass
from pathlib import Path

import matplotlib
import numpy as np
import pandas as pd

from . import compute_eto

matplotlib.use("Agg")
import matplotlib.pyplot as plt

METHOD_OUTPUT_COLUMNS = {
    "penman_monteith": "et_penman_monteith",
    "turc": "et_turc",
    "radiation_temperature": "et_radiation_temperature",
}

METHOD_REQUIRED_COLUMNS = {
    "penman_monteith": ["tmed_c", "rad_net_mj_m2_d", "wind_mean_ms"],
    "turc": ["tmed_c", "rad_global_mj_m2_d"],
    "radiation_temperature": ["tmed_c", "rad_global_mj_m2_d"],
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

PERTURBATIONS = tuple(range(-50, 51, 10))


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


def _perturbation_columns(df: pd.DataFrame, method: str, variable: SensitivityVariable) -> list[str]:
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

    plt.figure(figsize=(10, 6))
    for variable, group in ok.groupby("variable", sort=False):
        group = group.sort_values("perturbation_pct")
        plt.plot(group["perturbation_pct"], group["delta_mean_eto_mm_d"], marker="o", label=variable)
    plt.axhline(0, color="black", linewidth=1, alpha=0.7)
    plt.xlabel("Perturbation (%)")
    plt.ylabel("Mean ET0 change (mm/d)")
    plt.title(title)
    plt.legend(ncol=2, fontsize=8)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig(output_path, dpi=120)
    plt.close()


def _require_method_inputs(df: pd.DataFrame, method: str) -> None:
    missing = [column for column in METHOD_REQUIRED_COLUMNS[method] if column not in df.columns]
    if method == "penman_monteith":
        has_humidity = "rh_mean_pct" in df.columns or {"tmin_c", "tmax_c", "rh_min_pct", "rh_max_pct"} <= set(
            df.columns
        )
        if not has_humidity:
            missing.append("rh_mean_pct or tmin_c/tmax_c/rh_min_pct/rh_max_pct")
    if missing:
        joined = ", ".join(missing)
        raise ValueError(f"Cannot run sensitivity for method '{method}': missing required column(s): {joined}")
