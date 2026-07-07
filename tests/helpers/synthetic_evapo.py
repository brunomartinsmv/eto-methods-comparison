"""Helpers to build minimal synthetic Evapo.xlsx fixtures for integration tests."""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd


def write_synthetic_evapo_xlsx(
    path: Path,
    *,
    sheet: str = "Manaus",
    n_days: int = 14,
    year: int = 2024,
) -> None:
    """Write a minimal workbook compatible with ``read_evapo_sheet`` (skiprows=4)."""
    days = np.arange(1, n_days + 1)
    tmed = 25.0 + 0.3 * days
    tmax = tmed + 5.0
    tmin = tmed - 5.0
    rh = 75.0 - 0.5 * days
    wind = 1.5 + 0.05 * days
    rs = 15.0 + 0.4 * days
    rn = 8.0 + 0.2 * days
    ra = 34.0 + 0.1 * days

    # Spreadsheet-style precomputed ET0 (legacy magnitudes for Garcia-Lopez).
    et_pm = 2.0 + 0.05 * days
    et_gl = 37.5 + 0.01 * days
    et_hs = 4.0 + 0.03 * days

    data = pd.DataFrame(
        {
            "DIA": days,
            "TMED (oC)": tmed,
            "TMAX (oC)": tmax,
            "TMIN (oC)": tmin,
            "UR MED (%)": rh,
            "Vento (m/s)": wind,
            "Chuva (mm)": 0.0,
            "Rad.Glob. (MJ/m2.d)": rs,
            "Rad Liq (MJ/m2.d)": rn,
            "Q_0": ra,
            "Penman-Monteith": et_pm,
            "Garcia Lopez": et_gl,
            "Hargreaves & Samani": et_hs,
            "Thornthwaite": 5.0,
            "Thornthwaite Camargo": 5.0,
            "Hargreaves & Samani (corrigido)": 2.5,
        }
    )

    path.parent.mkdir(parents=True, exist_ok=True)
    padding = pd.DataFrame([["Synthetic fixture header row"]] * 4)
    with pd.ExcelWriter(path, engine="openpyxl") as writer:
        padding.to_excel(writer, sheet_name=sheet, index=False, header=False)
        data.to_excel(writer, sheet_name=sheet, index=False, startrow=4)
