from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from .config import METHOD_COLUMNS, WEATHER_COLUMNS

DERIVED_WEATHER_COLUMNS = frozenset(
    {
        "ra_extraterrestre_mj_m2_d",
    }
)


@dataclass(frozen=True)
class DataLayers:
    raw_weather_columns: tuple[str, ...]
    derived_weather_columns: tuple[str, ...]
    precomputed_eto_columns: tuple[str, ...]
    calculated_eto_columns: tuple[str, ...]


def build_data_layers(
    df: pd.DataFrame,
    *,
    calculated_eto_columns: tuple[str, ...] = (),
) -> DataLayers:
    """Classify standardized columns by their role in the ETo pipeline."""
    weather_columns = set(WEATHER_COLUMNS.values())
    method_columns = set(METHOD_COLUMNS.values())
    calculated = set(calculated_eto_columns)

    raw_weather = tuple(
        col for col in df.columns if col in weather_columns and col not in DERIVED_WEATHER_COLUMNS
    )
    derived_weather = tuple(col for col in df.columns if col in DERIVED_WEATHER_COLUMNS)
    precomputed_eto = tuple(sorted(col for col in df.columns if col in method_columns - calculated))

    return DataLayers(
        raw_weather_columns=raw_weather,
        derived_weather_columns=derived_weather,
        precomputed_eto_columns=precomputed_eto,
        calculated_eto_columns=tuple(col for col in df.columns if col in calculated),
    )
