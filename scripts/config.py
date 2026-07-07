from __future__ import annotations

from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

BASE_DIR = Path(__file__).resolve().parents[1]

DATA_RAW = BASE_DIR / "data" / "raw"
DATA_CLEANED = BASE_DIR / "data" / "cleaned"
CONFIGS = BASE_DIR / "configs"
OUTPUTS_RESULTS = BASE_DIR / "outputs" / "results"
OUTPUTS_FIGURES = BASE_DIR / "outputs" / "figures"
OUTPUTS_TABLES = BASE_DIR / "outputs" / "tables"
OUTPUTS_REPORTS = BASE_DIR / "outputs" / "reports"
OUTPUTS_SUPPLEMENT = BASE_DIR / "outputs" / "supplement"

DEFAULT_YEAR = 2024

SITES_CONFIG = CONFIGS / "sites.yml"
METHODS_CONFIG = CONFIGS / "methods.yml"
PIPELINE_CONFIG = CONFIGS / "pipeline.yml"


VALID_METHOD_STATUSES = frozenset({"computed", "precomputed_only", "reference"})


@dataclass(frozen=True)
class MethodsConfig:
    columns: dict[str, str]
    short_names: dict[str, str]
    status_by_name: dict[str, str]
    reference_column: str = "et_penman_monteith"

    @property
    def precomputed_only_columns(self) -> frozenset[str]:
        return frozenset(
            column
            for name, column in self.columns.items()
            if self.status_by_name.get(name) == "precomputed_only"
        )

    @property
    def computed_columns(self) -> frozenset[str]:
        return frozenset(
            column
            for name, column in self.columns.items()
            if self.status_by_name.get(name) == "computed"
        )


@dataclass(frozen=True)
class SitesDefaults:
    reader: dict[str, object]
    wind_height_m: float = 10.0


@dataclass(frozen=True)
class PipelineConfig:
    calibration_train_fraction: float = 0.7
    sensitivity_perturbation_min_pct: int = -50
    sensitivity_perturbation_max_pct: int = 50
    sensitivity_perturbation_step_pct: int = 10
    uncertainty_bootstrap_samples: int = 1000
    uncertainty_confidence: float = 0.95
    uncertainty_eto_bins: int = 4
    uncertainty_rainfall_column: str = "rain_mm"
    cleaning_max_gap_days: int | None = 7


def _read_yaml(path: Path) -> dict:
    with path.open(encoding="utf-8") as stream:
        loaded = yaml.safe_load(stream) or {}
    if not isinstance(loaded, dict):
        raise ValueError(f"Expected mapping in {path}")
    return loaded


def load_sites_defaults(path: Path = SITES_CONFIG) -> SitesDefaults:
    data = _read_yaml(path)
    defaults = data.get("defaults", {})
    if not isinstance(defaults, dict):
        defaults = {}
    reader = defaults.get("reader", {})
    if not isinstance(reader, dict):
        reader = {}
    return SitesDefaults(
        reader=reader,
        wind_height_m=float(defaults.get("wind_height_m", 10.0)),
    )


def load_sites_config(path: Path = SITES_CONFIG) -> dict[str, dict]:
    data = _read_yaml(path)
    defaults = load_sites_defaults(path)
    sites = data.get("sites")
    if not isinstance(sites, dict) or not sites:
        raise ValueError(f"Expected non-empty 'sites' mapping in {path}")

    merged: dict[str, dict] = {}
    for site, meta in sites.items():
        site_meta = dict(meta)
        if "wind_height_m" not in site_meta:
            site_meta["wind_height_m"] = defaults.wind_height_m
        merged[str(site)] = site_meta
    return merged


def load_pipeline_config(path: Path = PIPELINE_CONFIG) -> PipelineConfig:
    data = _read_yaml(path)
    calibration = data.get("calibration", {})
    sensitivity = data.get("sensitivity", {})
    uncertainty = data.get("uncertainty", {})
    cleaning = data.get("cleaning", {})
    if not all(isinstance(section, dict) for section in (calibration, sensitivity, uncertainty, cleaning)):
        raise ValueError(f"Expected section mappings in {path}")
    max_gap = cleaning.get("max_gap_days")
    return PipelineConfig(
        calibration_train_fraction=float(calibration.get("train_fraction", 0.7)),
        sensitivity_perturbation_min_pct=int(sensitivity.get("perturbation_min_pct", -50)),
        sensitivity_perturbation_max_pct=int(sensitivity.get("perturbation_max_pct", 50)),
        sensitivity_perturbation_step_pct=int(sensitivity.get("perturbation_step_pct", 10)),
        uncertainty_bootstrap_samples=int(uncertainty.get("bootstrap_samples", 1000)),
        uncertainty_confidence=float(uncertainty.get("confidence", 0.95)),
        uncertainty_eto_bins=int(uncertainty.get("eto_bins", 4)),
        uncertainty_rainfall_column=str(uncertainty.get("rainfall_column", "rain_mm")),
        cleaning_max_gap_days=None if max_gap is None else int(max_gap),
    )


def load_methods_config(path: Path = METHODS_CONFIG) -> MethodsConfig:
    data = _read_yaml(path)
    methods = data.get("methods")
    if not isinstance(methods, dict) or not methods:
        raise ValueError(f"Expected non-empty 'methods' mapping in {path}")

    columns: dict[str, str] = {}
    short_names: dict[str, str] = {}
    status_by_name: dict[str, str] = {}
    reference_column = "et_penman_monteith"
    for method_name, meta in methods.items():
        if not isinstance(meta, dict) or "column" not in meta:
            raise ValueError(f"Method '{method_name}' in {path} must define a column")
        column = str(meta["column"])
        name = str(method_name)
        columns[name] = column
        status = str(meta.get("status", "computed"))
        if status not in VALID_METHOD_STATUSES:
            allowed = ", ".join(sorted(VALID_METHOD_STATUSES))
            raise ValueError(f"Method '{method_name}' in {path} has invalid status '{status}'. Expected: {allowed}")
        status_by_name[name] = status
        if "short" in meta:
            short_names[column] = str(meta["short"])
        if bool(meta.get("reference")):
            reference_column = column

    return MethodsConfig(
        columns=columns,
        short_names=short_names,
        status_by_name=status_by_name,
        reference_column=reference_column,
    )


def select_sites(
    sites: dict[str, dict],
    site: str | None = None,
    all_sites: bool = True,
) -> dict[str, dict]:
    if site:
        if site not in sites:
            available = ", ".join(sorted(sites))
            raise ValueError(f"Unknown site '{site}'. Available sites: {available}")
        return {site: sites[site]}
    if all_sites:
        return sites
    return sites


@lru_cache(maxsize=1)
def _cached_sites() -> dict[str, dict]:
    return load_sites_config()


@lru_cache(maxsize=1)
def _cached_methods() -> MethodsConfig:
    return load_methods_config()


@lru_cache(maxsize=1)
def _cached_pipeline() -> PipelineConfig:
    return load_pipeline_config()


def clear_config_cache() -> None:
    """Clear lazily loaded configuration caches (useful in tests)."""
    _cached_sites.cache_clear()
    _cached_methods.cache_clear()
    _cached_pipeline.cache_clear()


def __getattr__(name: str) -> Any:
    if name == "SITES":
        return _cached_sites()
    if name == "METHODS":
        return _cached_methods()
    if name == "METHOD_COLUMNS":
        return _cached_methods().columns
    if name == "METHOD_SHORT":
        return _cached_methods().short_names
    if name == "REFERENCE_COLUMN":
        return _cached_methods().reference_column
    if name == "PIPELINE":
        return _cached_pipeline()
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


LEGACY_METHOD_COLUMN_ALIASES = {
    "Hargreaves & Samani": "et_hargreaves_samani",
    "Hargreaves & Samani (corrigido)": "et_hargreaves_samani_corr",
    "Penman-Monteith": "et_penman_monteith",
    "Garcia Lopez": "et_garcia_lopez",
}

WEATHER_COLUMNS = {
    "DIA": "date",
    "TMED (oC)": "tmed_c",
    "TMAX (oC)": "tmax_c",
    "TMIN (oC)": "tmin_c",
    "UR MED (%)": "rh_mean_pct",
    "UR MAX (%)": "rh_max_pct",
    "UR MIN (%)": "rh_min_pct",
    "Vento (m/s)": "wind_mean_ms",
    "Vel.Vento Max (m/s)": "wind_max_ms",
    "Chuva (mm)": "rain_mm",
    "Rad.Glob. (MJ/m2.d)": "rad_global_mj_m2_d",
    "Rad. Global (MJ/ma^2)": "rad_global_mj_m2_d",
    "Rad Liq (MJ/m2.d)": "rad_net_mj_m2_d",
    "Rad. Líquida (MJ/ma^2)": "rad_net_mj_m2_d",
    "Q_0": "ra_extraterrestre_mj_m2_d",
}
