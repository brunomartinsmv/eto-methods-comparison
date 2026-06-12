import pandas as pd

from scripts.eto_layers import build_data_layers


def test_build_data_layers_separates_weather_derived_and_precomputed_eto_columns() -> None:
    df = pd.DataFrame(
        {
            "date": ["2024-01-01"],
            "tmed_c": [25.0],
            "rad_net_mj_m2_d": [12.0],
            "ra_extraterrestre_mj_m2_d": [35.0],
            "et_penman_monteith": [4.2],
            "et_camargo": [3.1],
            "notes": ["kept outside layers"],
        }
    )

    layers = build_data_layers(df)

    assert layers.raw_weather_columns == ("date", "tmed_c", "rad_net_mj_m2_d")
    assert layers.derived_weather_columns == ("ra_extraterrestre_mj_m2_d",)
    assert layers.precomputed_eto_columns == ("et_camargo", "et_penman_monteith")
    assert layers.calculated_eto_columns == ()
