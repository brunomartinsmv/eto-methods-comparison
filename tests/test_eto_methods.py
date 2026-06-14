from __future__ import annotations

import inspect

import numpy as np
import pandas as pd
import pytest

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

SYNTHETIC_WEATHER = {
    "t_mean_c": np.array([20.0, 25.0, 30.0]),
    "t_min_c": np.array([15.0, 20.0, 25.0]),
    "t_max_c": np.array([25.0, 30.0, 35.0]),
    "ra_mj_m2_day": np.array([30.0, 35.0, 40.0]),
    "rs_mj_m2_day": np.array([16.0, 18.0, 20.0]),
    "rn_mj_m2_day": np.array([8.0, 10.0, 12.0]),
    "delta_kpa_c": np.array([0.1447, 0.1887, 0.2434]),
    "gamma_kpa_c": np.array([0.0665, 0.0665, 0.0665]),
    "rh_mean_pct": np.array([80.0, 70.0, 60.0]),
    "wind_2m_m_s": np.array([1.5, 2.0, 2.5]),
}

METHOD_CASES = {
    "camargo": (
        eto_methods.camargo,
        {
            "t_mean_c": SYNTHETIC_WEATHER["t_mean_c"],
            "ra_mj_m2_day": SYNTHETIC_WEATHER["ra_mj_m2_day"],
        },
        np.array([2.4489795918, 3.5714285714, 4.8979591837]),
    ),
    "hargreaves_samani": (
        eto_methods.hargreaves_samani,
        {
            "t_min_c": SYNTHETIC_WEATHER["t_min_c"],
            "t_max_c": SYNTHETIC_WEATHER["t_max_c"],
            "t_mean_c": SYNTHETIC_WEATHER["t_mean_c"],
            "ra_mj_m2_day": SYNTHETIC_WEATHER["ra_mj_m2_day"],
        },
        np.array([3.3664704462, 4.4470658981, 5.6760947912]),
    ),
    "makkink": (
        eto_methods.makkink,
        {
            "delta_kpa_c": SYNTHETIC_WEATHER["delta_kpa_c"],
            "gamma_kpa_c": SYNTHETIC_WEATHER["gamma_kpa_c"],
            "rs_mj_m2_day": SYNTHETIC_WEATHER["rs_mj_m2_day"],
        },
        np.array([2.6093444651, 3.1938090973, 3.7910443790]),
    ),
    "mccloud": (
        eto_methods.mccloud,
        {"t_mean_c": SYNTHETIC_WEATHER["t_mean_c"]},
        np.array([55.8068756000, 83.3922577898, 115.7849133880]),
    ),
    "priestley_taylor": (
        eto_methods.priestley_taylor,
        {
            "delta_kpa_c": SYNTHETIC_WEATHER["delta_kpa_c"],
            "gamma_kpa_c": SYNTHETIC_WEATHER["gamma_kpa_c"],
            "rn_mj_m2_day": SYNTHETIC_WEATHER["rn_mj_m2_day"],
        },
        np.array([2.8188311688, 3.8027317510, 4.8471304107]),
    ),
    "turc": (
        eto_methods.turc,
        {
            "t_mean_c": SYNTHETIC_WEATHER["t_mean_c"],
            "rs_mj_m2_day": SYNTHETIC_WEATHER["rs_mj_m2_day"],
            "rh_mean_pct": SYNTHETIC_WEATHER["rh_mean_pct"],
        },
        np.array([3.2121856000, 3.9017127500, 4.5761040000]),
    ),
    "global_radiation": (
        eto_methods.global_radiation,
        {"rs_mj_m2_day": SYNTHETIC_WEATHER["rs_mj_m2_day"]},
        np.array([3.4612244898, 3.8938775510, 4.3265306122]),
    ),
    "ivanov": (
        eto_methods.ivanov,
        {
            "t_mean_c": SYNTHETIC_WEATHER["t_mean_c"],
            "rh_mean_pct": SYNTHETIC_WEATHER["rh_mean_pct"],
        },
        np.array([72.9000000000, 135.0000000000, 217.8000000000]),
    ),
    "jensen_heise": (
        eto_methods.jensen_heise,
        {
            "t_mean_c": SYNTHETIC_WEATHER["t_mean_c"],
            "rs_mj_m2_day": SYNTHETIC_WEATHER["rs_mj_m2_day"],
        },
        np.array([2.7755102041, 4.0408163265, 5.5102040816]),
    ),
    "garcia_lopez": (
        eto_methods.garcia_lopez,
        {
            "t_mean_c": SYNTHETIC_WEATHER["t_mean_c"],
            "rh_mean_pct": SYNTHETIC_WEATHER["rh_mean_pct"],
            "wind_2m_m_s": SYNTHETIC_WEATHER["wind_2m_m_s"],
            "rs_mj_m2_day": SYNTHETIC_WEATHER["rs_mj_m2_day"],
        },
        np.array([1.3387755102, 3.0416326531, 5.8285714286]),
    ),
    "net_radiation": (
        eto_methods.net_radiation,
        {"rn_mj_m2_day": SYNTHETIC_WEATHER["rn_mj_m2_day"]},
        np.array([3.2640000000, 4.0800000000, 4.8960000000]),
    ),
    "radiation_temperature": (
        eto_methods.radiation_temperature,
        {
            "t_mean_c": SYNTHETIC_WEATHER["t_mean_c"],
            "rs_mj_m2_day": SYNTHETIC_WEATHER["rs_mj_m2_day"],
        },
        np.array([2.2857142857, 2.9387755102, 3.6734693878]),
    ),
    "lungeon": (
        eto_methods.lungeon,
        {
            "t_mean_c": SYNTHETIC_WEATHER["t_mean_c"],
            "rh_mean_pct": SYNTHETIC_WEATHER["rh_mean_pct"],
        },
        np.array([0.3200000000, 0.6075000000, 1.0000000000]),
    ),
    "stephens_stewart": (
        eto_methods.stephens_stewart,
        {
            "t_mean_c": SYNTHETIC_WEATHER["t_mean_c"],
            "rs_mj_m2_day": SYNTHETIC_WEATHER["rs_mj_m2_day"],
        },
        np.array([2.4097959184, 3.2532244898, 4.2171428571]),
    ),
    "hicks_hess": (
        eto_methods.hicks_hess,
        {
            "t_mean_c": SYNTHETIC_WEATHER["t_mean_c"],
            "rs_mj_m2_day": SYNTHETIC_WEATHER["rs_mj_m2_day"],
            "wind_2m_m_s": SYNTHETIC_WEATHER["wind_2m_m_s"],
        },
        np.array([3.3942857143, 5.1884081633, 7.5114285714]),
    ),
}


def test_radiation_conversion_accepts_arrays_and_preserves_series_index() -> None:
    converted = mj_m2_day_to_mm_day(np.array([2.45, 4.90]))
    assert np.allclose(converted, np.array([1.0, 2.0]))

    series = pd.Series([2.45, 4.90], index=["a", "b"], name="rn")
    converted_series = mj_m2_day_to_mm_day(series)

    assert isinstance(converted_series, pd.Series)
    assert converted_series.index.tolist() == ["a", "b"]
    assert converted_series.name == "rn"
    assert converted_series.tolist() == [1.0, 2.0]


@pytest.mark.parametrize("method_name", PUBLIC_METHODS)
def test_public_methods_have_synthetic_regression_values(method_name: str) -> None:
    function, kwargs, expected = METHOD_CASES[method_name]

    result = np.asarray(function(**kwargs), dtype=float)

    assert result.shape == expected.shape
    assert np.all(np.isfinite(result))
    assert np.all(result > 0)
    assert np.all(np.diff(result) > 0)
    assert np.allclose(result, expected, rtol=1e-10, atol=1e-10)


def test_hargreaves_samani_is_zero_when_temperature_range_is_zero() -> None:
    result = eto_methods.hargreaves_samani(
        t_min_c=np.array([25.0]),
        t_max_c=np.array([25.0]),
        t_mean_c=np.array([25.0]),
        ra_mj_m2_day=np.array([35.0]),
    )

    assert np.allclose(result, np.array([0.0]), rtol=0.0, atol=1e-12)


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

    assert np.isclose(result, 4.124144185, rtol=1e-10, atol=1e-10)


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
