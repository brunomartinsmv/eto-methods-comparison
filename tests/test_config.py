from pathlib import Path

import pytest
import yaml

from scripts.config import METHODS_CONFIG, load_methods_config, load_sites_config, select_sites


def test_load_sites_config_reads_site_metadata_from_yaml(tmp_path: Path) -> None:
    config_path = tmp_path / "sites.yml"
    config_path.write_text(
        """
sites:
  test_site:
    sheet: Test Sheet
    lat: -10.5
    lon: -55.2
    alt_m: 120.0
    biome: Cerrado
    climate_class: Aw
    region: Centro-Oeste
    country: Brazil
    state: MT
""".strip()
    )

    sites = load_sites_config(config_path)

    assert sites == {
        "test_site": {
            "sheet": "Test Sheet",
            "lat": -10.5,
            "lon": -55.2,
            "alt_m": 120.0,
            "biome": "Cerrado",
            "climate_class": "Aw",
            "region": "Centro-Oeste",
            "country": "Brazil",
            "state": "MT",
        }
    }


def test_load_sites_config_keeps_optional_metadata_optional(tmp_path: Path) -> None:
    config_path = tmp_path / "sites.yml"
    config_path.write_text(
        """
sites:
  test_site:
    sheet: Test Sheet
    lat: -10.5
    lon: -55.2
    alt_m: 120.0
""".strip()
    )

    sites = load_sites_config(config_path)

    assert "biome" not in sites["test_site"]
    assert sites["test_site"]["sheet"] == "Test Sheet"


def test_select_sites_returns_requested_site_and_rejects_unknown_site() -> None:
    sites = {
        "manaus": {"sheet": "Manaus"},
        "piracicaba": {"sheet": "Piracicaba"},
    }

    assert select_sites(sites, site="manaus", all_sites=False) == {
        "manaus": {"sheet": "Manaus"}
    }

    with pytest.raises(ValueError, match="Unknown site"):
        select_sites(sites, site="cuiaba", all_sites=False)


def test_load_methods_config_reads_column_map_and_short_names(tmp_path: Path) -> None:
    config_path = tmp_path / "methods.yml"
    config_path.write_text(
        """
methods:
  Penman-Monteith:
    column: et_penman_monteith
    short: pm
    reference: true
  Camargo:
    column: et_camargo
    short: camargo
""".strip()
    )

    methods = load_methods_config(config_path)

    assert methods.columns == {
        "Penman-Monteith": "et_penman_monteith",
        "Camargo": "et_camargo",
    }
    assert methods.short_names == {
        "et_penman_monteith": "pm",
        "et_camargo": "camargo",
    }
    assert methods.reference_column == "et_penman_monteith"


def test_repository_methods_config_lists_15_et0_methods_and_reference() -> None:
    methods = load_methods_config()

    expected_alternatives = {
        "Camargo",
        "Hargreaves-Samani",
        "Makkink",
        "McCloud",
        "Priestley-Taylor",
        "Turc",
        "Global Radiation",
        "Ivanov",
        "Jensen-Heise",
        "Garcia-Lopez",
        "Net Radiation",
        "Radiation-Temperature",
        "Lungeon",
        "Stephens-Stewart",
        "Hicks-Hess",
    }

    configured_methods = set(methods.columns)
    assert expected_alternatives <= configured_methods
    assert "Penman-Monteith FAO-56" in configured_methods
    assert methods.reference_column == "et_penman_monteith"
    assert len(expected_alternatives) == 15
    assert len(set(methods.columns.values())) == len(methods.columns)
    assert len(set(methods.short_names.values())) == len(methods.short_names)


def test_repository_methods_config_declares_full_name_and_computation_status() -> None:
    data = yaml.safe_load(METHODS_CONFIG.read_text(encoding="utf-8"))

    for metadata in data["methods"].values():
        assert metadata["full_name"]
        assert metadata["column"].startswith("et_")
        assert metadata["short"]
        assert metadata["status"] in {"computed", "configured_not_computed", "reference"}

    configured_not_computed = {
        method_name
        for method_name, metadata in data["methods"].items()
        if metadata["status"] == "configured_not_computed"
    }
    assert {
        "Makkink",
        "McCloud",
        "Turc",
        "Global Radiation",
        "Ivanov",
        "Jensen-Heise",
        "Net Radiation",
        "Radiation-Temperature",
        "Lungeon",
        "Stephens-Stewart",
        "Hicks-Hess",
    } <= configured_not_computed
