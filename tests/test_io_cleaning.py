from pathlib import Path

import pandas as pd

from scripts.cleaning import clean_daily
from scripts.io import read_evapo_sheet


def test_clean_daily_sorts_dates_interpolates_numeric_values_and_drops_duplicate_dates() -> None:
    df = pd.DataFrame(
        {
            "date": pd.to_datetime(["2024-01-03", "2024-01-01", "2024-01-02", "2024-01-02"]),
            "pm_fao56": [3.0, 1.0, None, 2.0],
            "station": ["c", "a", "b", "duplicate"],
        }
    )

    result = clean_daily(df)

    assert result["date"].tolist() == pd.to_datetime(
        ["2024-01-01", "2024-01-02", "2024-01-03"]
    ).tolist()
    assert result["pm_fao56"].tolist() == [1.0, 1.5, 3.0]
    assert result["station"].tolist() == ["a", "b", "c"]


def test_read_evapo_sheet_renames_columns_drops_unnamed_columns_and_parses_day_of_year(
    monkeypatch,
) -> None:
    synthetic = pd.DataFrame(
        {
            "DIA": [1, 2],
            "TMAX (oC)": [31.0, 32.0],
            "TMIN (oC)": [21.0, 22.0],
            "Unnamed: 9": ["drop", "drop"],
            "Penman-Monteith": [4.1, 4.2],
        }
    )

    def fake_read_excel(path, sheet_name, skiprows):
        assert path == Path("synthetic.xlsx")
        assert sheet_name == "Manaus"
        assert skiprows == 4
        return synthetic

    monkeypatch.setattr(pd, "read_excel", fake_read_excel)

    result = read_evapo_sheet(Path("synthetic.xlsx"), "Manaus", year=2024)

    assert "Unnamed: 9" not in result.columns
    assert result["date"].tolist() == pd.to_datetime(["2024-01-01", "2024-01-02"]).tolist()
    assert result["tmax_c"].tolist() == [31.0, 32.0]
    assert result["tmin_c"].tolist() == [21.0, 22.0]
    assert result["et_penman_monteith"].tolist() == [4.1, 4.2]
