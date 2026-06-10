from pathlib import Path

import pandas as pd

from scripts.summary import build_summary, write_summary


def test_build_summary_selects_best_method_by_rmse_for_each_site_and_scale(tmp_path: Path) -> None:
    tables_dir = tmp_path / "tables"
    tables_dir.mkdir()
    pd.DataFrame(
        {
            "method": ["et_camargo", "et_priestley_taylor"],
            "rmse": [1.2, 0.7],
            "mae": [1.0, 0.5],
            "mbe": [-0.2, 0.1],
            "r2": [0.8, 0.9],
            "willmott_d": [0.7, 0.95],
        }
    ).to_csv(tables_dir / "manaus_daily_metrics.csv", index=False)
    pd.DataFrame(
        {
            "method": ["et_camargo", "et_priestley_taylor"],
            "rmse": [3.0, 4.0],
            "mae": [2.5, 3.5],
            "mbe": [-1.0, 1.5],
            "r2": [0.6, 0.5],
            "willmott_d": [0.75, 0.65],
        }
    ).to_csv(tables_dir / "manaus_monthly_metrics.csv", index=False)

    summary = build_summary(tables_dir, sites=["manaus"])

    assert summary[["site", "scale", "best_method", "rmse"]].to_dict("records") == [
        {
            "site": "manaus",
            "scale": "daily",
            "best_method": "et_priestley_taylor",
            "rmse": 0.7,
        },
        {
            "site": "manaus",
            "scale": "monthly",
            "best_method": "et_camargo",
            "rmse": 3.0,
        },
    ]


def test_write_summary_creates_csv_and_markdown(tmp_path: Path) -> None:
    summary = pd.DataFrame(
        {
            "site": ["manaus"],
            "scale": ["daily"],
            "best_method": ["et_priestley_taylor"],
            "rmse": [0.7],
        }
    )

    csv_path, markdown_path = write_summary(summary, tmp_path)

    assert csv_path == tmp_path / "summary.csv"
    assert markdown_path == tmp_path / "summary.md"
    assert "et_priestley_taylor" in markdown_path.read_text()
