from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import yaml

BASE_DIR = Path(__file__).resolve().parents[1]

DATA_RAW = BASE_DIR / "data" / "raw"
DATA_CLEANED = BASE_DIR / "data" / "cleaned"
CONFIGS = BASE_DIR / "configs"
OUTPUTS_RESULTS = BASE_DIR / "outputs" / "results"
OUTPUTS_FIGURES = BASE_DIR / "outputs" / "figures"
OUTPUTS_TABLES = BASE_DIR / "outputs" / "tables"
OUTPUTS_REPORTS = BASE_DIR / "outputs" / "reports"

DEFAULT_YEAR = 2024

SITES_CONFIG = CONFIGS / "sites.yml"
METHODS_CONFIG = CONFIGS / "methods.yml"


@dataclass(frozen=True)
class MethodsConfig:
    columns: dict[str, str]
    short_names: dict[str, str]
    reference_column: str = "et_penman_monteith"


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
    reference_column = "et_penman_monteith"
    for method_name, meta in methods.items():
        if not isinstance(meta, dict) or "column" not in meta:
            raise ValueError(f"Method '{method_name}' in {path} must define a column")
        column = str(meta["column"])
        columns[str(method_name)] = column
        if "short" in meta:
            short_names[column] = str(meta["short"])
        if bool(meta.get("reference")):
            reference_column = column

    return MethodsConfig(columns=columns, short_names=short_names, reference_column=reference_column)


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


SITES = load_sites_config()
METHODS = load_methods_config()
METHOD_COLUMNS = METHODS.columns
METHOD_SHORT = METHODS.short_names
REFERENCE_COLUMN = METHODS.reference_column

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
