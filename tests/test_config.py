from pathlib import Path

import pytest

from scripts.config import load_methods_config, load_sites_config, select_sites


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
""".strip()
    )

    sites = load_sites_config(config_path)

    assert sites == {
        "test_site": {
            "sheet": "Test Sheet",
            "lat": -10.5,
            "lon": -55.2,
            "alt_m": 120.0,
        }
    }


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
