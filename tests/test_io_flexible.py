from __future__ import annotations

from pathlib import Path

import pandas as pd

from scripts.io import read_generic_table, read_site_data, resolve_reader_config


def test_resolve_reader_config_defaults_to_evapo_legacy() -> None:
    config = resolve_reader_config({"sheet": "Manaus"}, Path("data/raw/Evapo.xlsx"))
    assert config.format == "evapo_legacy"
    assert config.sheet == "Manaus"


def test_read_generic_table_applies_column_map(tmp_path: Path) -> None:
    csv_path = tmp_path / "site.csv"
    pd.DataFrame(
        {
            "Date": ["2024-01-01", "2024-01-02"],
            "Temp": [25.0, 26.0],
        }
    ).to_csv(csv_path, index=False)

    df = read_generic_table(csv_path, column_map={"Date": "date", "Temp": "tmed_c"})
    assert "date" in df.columns
    assert "tmed_c" in df.columns


def test_read_site_data_generic_reader(tmp_path: Path, monkeypatch) -> None:
    raw_dir = tmp_path / "data" / "raw"
    raw_dir.mkdir(parents=True)
    csv_path = raw_dir / "custom.csv"
    pd.DataFrame(
        {
            "DIA": [1, 2],
            "TMED (oC)": [25.0, 26.0],
            "TMAX (oC)": [30.0, 31.0],
            "TMIN (oC)": [20.0, 21.0],
            "UR MED (%)": [80.0, 81.0],
            "Vento (m/s)": [2.0, 2.1],
            "Rad.Glob. (MJ/m2.d)": [18.0, 19.0],
            "Rad Liq (MJ/m2.d)": [10.0, 11.0],
            "Q_0": [34.0, 34.5],
        }
    ).to_csv(csv_path, index=False)

    site_meta = {
        "reader": {
            "format": "generic",
            "path": "data/raw/custom.csv",
        }
    }

    from scripts import io as io_module

    monkeypatch.setattr(io_module, "BASE_DIR", tmp_path)
    df = read_site_data(raw_dir / "Evapo.xlsx", site_meta, year=2024)
    assert len(df) == 2
    assert "tmed_c" in df.columns
