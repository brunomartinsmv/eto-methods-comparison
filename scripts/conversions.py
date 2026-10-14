from __future__ import annotations

from typing import TypeAlias

import numpy as np
import pandas as pd

ArrayLike: TypeAlias = float | int | np.ndarray | pd.Series

LATENT_HEAT_VAPORIZATION_MJ_KG = 2.45


def as_array(values: ArrayLike) -> np.ndarray:
    return np.asarray(values, dtype=float)


def restore_type(values: np.ndarray | np.floating | float, template: ArrayLike) -> float | np.ndarray | pd.Series:
    if isinstance(template, pd.Series):
        return pd.Series(np.asarray(values, dtype=float), index=template.index, name=template.name)
    if np.isscalar(template):
        return float(np.asarray(values, dtype=float))
    return np.asarray(values, dtype=float)


def first_series(*values: ArrayLike) -> pd.Series | None:
    for value in values:
        if isinstance(value, pd.Series):
            return value
    return None


def restore_from_inputs(values: np.ndarray | np.floating | float, *inputs: ArrayLike) -> float | np.ndarray | pd.Series:
    template = first_series(*inputs)
    if template is not None:
        return restore_type(values, template)
    if all(np.isscalar(value) for value in inputs):
        return float(np.asarray(values, dtype=float))
    return np.asarray(values, dtype=float)


def mj_m2_day_to_mm_day(
    radiation_mj_m2_day: ArrayLike,
    *,
    latent_heat_mj_kg: float = LATENT_HEAT_VAPORIZATION_MJ_KG,
) -> float | np.ndarray | pd.Series:
    """Convert MJ m-2 day-1 to equivalent water depth in mm day-1.

    Depth = radiation / lambda. FAO-56 uses lambda = 2.45 MJ kg-1;
    1 mm of water is 1 kg m-2.

    Parameters
    ----------
    radiation_mj_m2_day: energy flux, MJ m-2 day-1.
    latent_heat_mj_kg: latent heat of vaporization, MJ kg-1.

    Units
    -----
    Output is mm day-1.

    Returns
    -------
    float, numpy.ndarray, or pandas.Series.
    """
    result = as_array(radiation_mj_m2_day) / latent_heat_mj_kg
    return restore_type(result, radiation_mj_m2_day)
