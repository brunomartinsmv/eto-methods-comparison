"""FAO-56 / ASCE daily global-radiation consistency screen.

The clear-sky estimate is FAO-56 equation 37 (ASCE-EWRI 2005 equation 19):

    Rso = (0.75 + 2e-5 * z) * Ra

ASCE-EWRI (2005) equation 18 limits the cloudiness ratio used in the
standardized net-radiation calculation to 0.25 <= Rs/Rso <= 1.0. A day is
also outside the envelope when measured global radiation exceeds
extraterrestrial radiation (Rs > Ra). Days that fail either comparison are
counted; they are not removed from the full-year metric tables. This module
does not modify ``rad_net_mj_m2_d``.
"""

from __future__ import annotations

from pathlib import Path

import numpy as np
import pandas as pd

from .derived_meteo import (
    clear_sky_radiation_mj_m2_day,
    day_of_year_from_dates,
    extraterrestrial_radiation_mj_m2_day,
)
from .naming import radiation_screen_filename

RS_OVER_RSO_MIN = 0.25
RS_OVER_RSO_MAX = 1.0
OUTSIDE_STATUSES = (
    "above_clear_sky",
    "below_cloudiness_floor",
    "above_extraterrestrial",
)


def radiation_consistency_frame(
    df: pd.DataFrame,
    *,
    elevation_m: float,
    latitude_deg: float | None = None,
) -> pd.DataFrame:
    """Return Rs, Ra, Rso, both ratios, and whether each day is inside the envelope.

    When ``latitude_deg`` and ``date`` are available, extraterrestrial radiation
    is FAO-56 equation 21. The cleaned ``ra_extraterrestre_mj_m2_d`` column is
    used only if latitude is absent. The input frame is not modified.
    """
    rs = _numeric_column(df, "rad_global_mj_m2_d")
    ra = _extraterrestrial_radiation(df, latitude_deg=latitude_deg)
    rso = clear_sky_radiation_mj_m2_day(ra, elevation_m)
    rso.index = df.index

    rs_over_ra = rs / ra.where(ra > 0)
    rs_over_rso = rs / rso.where(rso > 0)
    finite = (
        np.isfinite(rs.to_numpy(dtype=float))
        & np.isfinite(ra.to_numpy(dtype=float))
        & np.isfinite(rso.to_numpy(dtype=float))
        & (ra.to_numpy(dtype=float) > 0)
        & (rso.to_numpy(dtype=float) > 0)
    )
    finite_mask = pd.Series(finite, index=df.index)
    above_ra = finite_mask & (rs > ra)
    above_rso = finite_mask & ~above_ra & (rs_over_rso > RS_OVER_RSO_MAX)
    below_floor = finite_mask & ~above_ra & (rs_over_rso < RS_OVER_RSO_MIN)
    inside = finite_mask & ~above_ra & ~above_rso & ~below_floor

    status = pd.Series("unevaluable", index=df.index, dtype="object")
    status.loc[above_ra] = "above_extraterrestrial"
    status.loc[above_rso] = "above_clear_sky"
    status.loc[below_floor] = "below_cloudiness_floor"
    status.loc[inside] = "inside"

    frame = pd.DataFrame(
        {
            "rad_global_mj_m2_d": rs,
            "ra_mj_m2_d": ra,
            "rso_clear_sky_mj_m2_d": rso,
            "rs_over_ra": rs_over_ra,
            "rs_over_rso": rs_over_rso,
            "inside_envelope": inside,
            "envelope_status": status,
        },
        index=df.index,
    )
    if "date" in df.columns:
        frame.insert(0, "date", df["date"].to_numpy())
    return frame


def envelope_counts(frame: pd.DataFrame) -> dict[str, int]:
    """Count days inside, outside, and unevaluable for a consistency frame."""
    status = frame["envelope_status"]
    return {
        "inside": int((status == "inside").sum()),
        "outside": int(status.isin(OUTSIDE_STATUSES).sum()),
        "unevaluable": int((status == "unevaluable").sum()),
    }


def write_radiation_screen(frame: pd.DataFrame, output_dir: Path, site: str) -> Path:
    """Write the daily radiation-consistency table for one site."""
    output_dir.mkdir(parents=True, exist_ok=True)
    output_path = output_dir / radiation_screen_filename(site)
    export = frame.copy()
    if "date" in export.columns:
        export["date"] = pd.to_datetime(export["date"], errors="coerce").dt.strftime("%Y-%m-%d")
    export.to_csv(output_path, index=False)
    return output_path


def _numeric_column(df: pd.DataFrame, column: str) -> pd.Series:
    if column not in df.columns:
        return pd.Series(np.nan, index=df.index, dtype="float64")
    return pd.to_numeric(df[column], errors="coerce")


def _extraterrestrial_radiation(
    df: pd.DataFrame,
    *,
    latitude_deg: float | None,
) -> pd.Series:
    if latitude_deg is not None and "date" in df.columns:
        day_of_year = day_of_year_from_dates(df["date"])
        ra = extraterrestrial_radiation_mj_m2_day(day_of_year, float(latitude_deg))
        return pd.Series(pd.to_numeric(ra, errors="coerce").to_numpy(), index=df.index, dtype="float64")
    if "ra_extraterrestre_mj_m2_d" in df.columns:
        return pd.to_numeric(df["ra_extraterrestre_mj_m2_d"], errors="coerce")
    return pd.Series(np.nan, index=df.index, dtype="float64")
