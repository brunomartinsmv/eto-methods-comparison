from __future__ import annotations

from pathlib import Path

import pandas as pd
import pytest

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


def test_resolve_csv_reader_uses_no_header_skip() -> None:
    config = resolve_reader_config(
        {"reader": {"format": "csv", "path": "data/raw/cuiaba.csv"}},
        Path("data/raw/Evapo.xlsx"),
    )
    assert config.format == "csv"
    assert config.skiprows == 0
    assert config.path == "data/raw/cuiaba.csv"


def test_csv_reader_reads_canonical_columns_from_configured_path(tmp_path: Path, monkeypatch) -> None:
    raw_dir = tmp_path / "data" / "raw"
    raw_dir.mkdir(parents=True)
    csv_path = raw_dir / "cuiaba.csv"
    pd.DataFrame(
        {
            "date": ["2024-01-01", "2024-01-02"],
            "tmed_c": [25.3, 26.1],
            "tmax_c": [32.1, 33.5],
            "tmin_c": [19.2, 20.0],
            "rh_mean_pct": [68.2, 65.5],
            "wind_mean_ms": [1.8, 2.1],
            "rad_global_mj_m2_d": [22.5, 23.1],
            "rad_net_mj_m2_d": [12.0, 12.4],
        }
    ).to_csv(csv_path, index=False)

    from scripts import io as io_module

    monkeypatch.setattr(io_module, "BASE_DIR", tmp_path)
    df = read_site_data(
        raw_dir / "Evapo.xlsx",
        {"reader": {"format": "csv", "path": "data/raw/cuiaba.csv"}},
        year=2024,
    )
    assert df["date"].tolist() == pd.to_datetime(["2024-01-01", "2024-01-02"]).tolist()
    assert df["tmed_c"].tolist() == [25.3, 26.1]
    assert df["rad_net_mj_m2_d"].tolist() == [12.0, 12.4]


def test_csv_reader_uses_cli_input_and_spreadsheet_headers(tmp_path: Path) -> None:
    csv_path = tmp_path / "cuiaba.csv"
    pd.DataFrame(
        {
            "DIA": [1, 2],
            "TMED (oC)": [25.0, 26.0],
            "TMAX (oC)": [30.0, 31.0],
            "TMIN (oC)": [20.0, 21.0],
        }
    ).to_csv(csv_path, index=False)

    df = read_site_data(csv_path, {"reader": {"format": "csv"}}, year=2024)
    assert df["date"].tolist() == pd.to_datetime(["2024-01-01", "2024-01-02"]).tolist()
    assert df["tmax_c"].tolist() == [30.0, 31.0]


def test_csv_reader_rejects_xlsx_path(tmp_path: Path) -> None:
    workbook = tmp_path / "Evapo.xlsx"
    workbook.write_bytes(b"not a workbook")
    with pytest.raises(ValueError, match="evapo_legacy"):
        read_site_data(workbook, {"reader": {"format": "csv"}}, year=2024)


def test_evapo_legacy_rejects_csv_input(tmp_path: Path) -> None:
    csv_path = tmp_path / "cuiaba.csv"
    csv_path.write_text("date,tmed_c\n2024-01-01,25\n", encoding="utf-8")
    with pytest.raises(ValueError, match="reader.format: csv"):
        read_site_data(csv_path, {"sheet": "Cuiaba"}, year=2024)
