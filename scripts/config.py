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


def _read_yaml(path: Path) -> dict:
    with path.open(encoding="utf-8") as stream:
        loaded = yaml.safe_load(stream) or {}
    if not isinstance(loaded, dict):
        raise ValueError(f"Expected mapping in {path}")
    return loaded


def load_sites_config(path: Path = SITES_CONFIG) -> dict[str, dict]:
    data = _read_yaml(path)
    sites = data.get("sites")
    if not isinstance(sites, dict) or not sites:
        raise ValueError(f"Expected non-empty 'sites' mapping in {path}")
    return {str(site): dict(meta) for site, meta in sites.items()}


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


def clear_config_cache() -> None:
    """Clear lazily loaded configuration caches (useful in tests)."""
    _cached_sites.cache_clear()
    _cached_methods.cache_clear()


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
