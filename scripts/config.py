from __future__ import annotations

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[1]

DATA_RAW = BASE_DIR / "data" / "raw"
DATA_CLEANED = BASE_DIR / "data" / "cleaned"
OUTPUTS_RESULTS = BASE_DIR / "outputs" / "results"
OUTPUTS_FIGURES = BASE_DIR / "outputs" / "figures"
OUTPUTS_TABLES = BASE_DIR / "outputs" / "tables"
OUTPUTS_REPORTS = BASE_DIR / "outputs" / "reports"

DEFAULT_YEAR = 2024

SITES = {
    "manaus": {
        "sheet": "Manaus",
        "lat": -3.1019,
        "lon": -60.0164,
        "alt_m": 61.25,
    },
    "piracicaba": {
        "sheet": "Piracicaba",
        "lat": -22.7083,
        "lon": -47.6333,
        "alt_m": 546.0,
    },
}

METHOD_COLUMNS = {
    "Thornthwaite": "et_thornthwaite",
    "Thornthwaite-Camargo": "et_thornthwaite_camargo",
    "Camargo": "et_camargo",
    "Hargreaves & Samani": "et_hargreaves_samani",
    "Hargreaves & Samani (corrigido)": "et_hargreaves_samani_corr",
    "Priestley-Taylor": "et_priestley_taylor",
    "Penman-Monteith": "et_penman_monteith",
    "Garcia Lopez": "et_garcia_lopez",
}

METHOD_SHORT = {
    "et_thornthwaite": "thorn",
    "et_thornthwaite_camargo": "thorn_camargo",
    "et_camargo": "camargo",
    "et_hargreaves_samani": "hs",
    "et_hargreaves_samani_corr": "hs_corr",
    "et_priestley_taylor": "pt",
    "et_penman_monteith": "pm",
    "et_garcia_lopez": "gl",
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
