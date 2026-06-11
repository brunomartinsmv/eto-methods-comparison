from __future__ import annotations

import inspect

import numpy as np
import pandas as pd

from scripts import eto_methods
from scripts.conversions import mj_m2_day_to_mm_day
from scripts.fao56 import penman_monteith_fao56

PUBLIC_METHODS = [
    "camargo",
    "hargreaves_samani",
    "makkink",
    "mccloud",
    "priestley_taylor",
    "turc",
    "global_radiation",
    "ivanov",
    "jensen_heise",
    "garcia_lopez",
    "net_radiation",
    "radiation_temperature",
    "lungeon",
    "stephens_stewart",
    "hicks_hess",
]


def test_radiation_conversion_accepts_arrays_and_preserves_series_index() -> None:
    converted = mj_m2_day_to_mm_day(np.array([2.45, 4.90]))
    assert np.allclose(converted, np.array([1.0, 2.0]))

    series = pd.Series([2.45, 4.90], index=["a", "b"], name="rn")
    converted_series = mj_m2_day_to_mm_day(series)

    assert isinstance(converted_series, pd.Series)
    assert converted_series.index.tolist() == ["a", "b"]
    assert converted_series.name == "rn"
    assert converted_series.tolist() == [1.0, 2.0]


def test_core_methods_return_expected_vector_values() -> None:
    assert np.allclose(
        eto_methods.hargreaves_samani(
            t_min_c=np.array([20.0]),
            t_max_c=np.array([30.0]),
            t_mean_c=np.array([25.0]),
            ra_mj_m2_day=np.array([35.0]),
        ),
        np.array([4.4470659]),
    )
    assert np.allclose(
        eto_methods.priestley_taylor(
            delta_kpa_c=np.array([0.1887]),
            gamma_kpa_c=np.array([0.0665]),
            rn_mj_m2_day=np.array([10.0]),
        ),
        np.array([3.802731749]),
    )
    assert np.allclose(
        eto_methods.turc(
            t_mean_c=np.array([25.0]),
            rs_mj_m2_day=np.array([18.0]),
            rh_mean_pct=np.array([70.0]),
        ),
        np.array([3.90171275]),
    )


def test_penman_monteith_fao56_matches_reference_scalar_calculation() -> None:
    result = penman_monteith_fao56(
        t_mean_c=25.0,
        rn_mj_m2_day=10.0,
        g_mj_m2_day=0.0,
        wind_2m_m_s=2.0,
        saturation_vapor_pressure_kpa=3.1678,
        actual_vapor_pressure_kpa=2.0,
        delta_kpa_c=0.1887,
        gamma_kpa_c=0.0665,
    )

    assert np.isclose(result, 4.124144185)


def test_all_public_method_functions_have_unit_docstrings_and_type_hints() -> None:
    for function_name in PUBLIC_METHODS:
        function = getattr(eto_methods, function_name)
        doc = inspect.getdoc(function)

        assert doc is not None
        assert "Parameters" in doc
        assert "Units" in doc
        assert "Returns" in doc
        assert inspect.signature(function).return_annotation != inspect.Signature.empty

    assert inspect.getdoc(penman_monteith_fao56)
    assert "FAO-56" in inspect.getdoc(penman_monteith_fao56)
