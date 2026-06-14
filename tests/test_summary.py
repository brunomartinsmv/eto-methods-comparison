from pathlib import Path

import pandas as pd

from scripts.summary import build_rankings, build_summary, write_rankings, write_summary


def test_build_summary_selects_best_method_by_requested_rmse_rule(tmp_path: Path) -> None:
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
            "c": [0.56, 0.86],
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
            "c": [0.45, 0.33],
        }
    ).to_csv(tables_dir / "manaus_monthly_metrics.csv", index=False)

    summary = build_summary(tables_dir, sites=["manaus"], ranking="rmse")

    assert summary[["site", "scale", "rank", "selection_rule", "best_method", "rmse"]].to_dict("records") == [
        {
            "site": "manaus",
            "scale": "daily",
            "rank": 1,
            "selection_rule": "rmse",
            "best_method": "et_priestley_taylor",
            "rmse": 0.7,
        },
        {
            "site": "manaus",
            "scale": "monthly",
            "rank": 1,
            "selection_rule": "rmse",
            "best_method": "et_camargo",
            "rmse": 3.0,
        },
    ]


def test_build_summary_selects_best_method_by_composite_rule(tmp_path: Path) -> None:
    tables_dir = tmp_path / "tables"
    tables_dir.mkdir()
    pd.DataFrame(
        {
            "method": ["et_low_rmse", "et_high_c", "et_high_c_lower_error"],
            "rmse": [0.4, 0.8, 0.6],
            "mae": [0.35, 0.7, 0.5],
            "mbe": [0.0, 0.2, -0.1],
            "r2": [0.95, 0.9, 0.92],
            "willmott_d": [0.94, 0.97, 0.98],
            "c": [0.85, 0.9, 0.9],
        }
    ).to_csv(tables_dir / "manaus_daily_metrics.csv", index=False)

    summary = build_summary(tables_dir, sites=["manaus"], ranking="composite")

    assert summary[["scale", "rank", "selection_rule", "best_method", "c", "rmse"]].to_dict("records") == [
        {
            "scale": "daily",
            "rank": 1,
            "selection_rule": "composite",
            "best_method": "et_high_c_lower_error",
            "c": 0.9,
            "rmse": 0.6,
        }
    ]


def test_build_summary_adds_optional_site_metadata_when_available(tmp_path: Path) -> None:
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
            "c": [0.56, 0.86],
        }
    ).to_csv(tables_dir / "manaus_daily_metrics.csv", index=False)

    summary = build_summary(
        tables_dir,
        sites=["manaus"],
        site_metadata={
            "manaus": {
                "biome": "Amazonia",
                "climate_class": "Af",
                "region": "North",
                "country": "Brazil",
                "state": "AM",
            }
        },
    )

    assert summary[
        ["site", "biome", "climate_class", "region", "country", "state", "best_method"]
    ].to_dict("records") == [
        {
            "site": "manaus",
            "biome": "Amazonia",
            "climate_class": "Af",
            "region": "North",
            "country": "Brazil",
            "state": "AM",
            "best_method": "et_priestley_taylor",
        }
    ]


def test_build_rankings_orders_methods_by_rmse_within_each_site_and_scale(tmp_path: Path) -> None:
    tables_dir = tmp_path / "tables"
    tables_dir.mkdir()
    pd.DataFrame(
        {
            "method": ["et_camargo", "et_priestley_taylor", "et_hargreaves_samani_corr"],
            "rmse": [1.2, 0.7, 0.5],
            "mae": [1.0, 0.5, 0.4],
            "mbe": [-0.2, 0.1, 0.0],
            "r2": [0.8, 0.9, 0.95],
            "willmott_d": [0.7, 0.95, 0.98],
            "c": [0.56, 0.86, 0.93],
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
            "c": [0.45, 0.33],
        }
    ).to_csv(tables_dir / "piracicaba_monthly_metrics.csv", index=False)

    rankings = build_rankings(tables_dir, sites=["manaus", "piracicaba"], ranking="rmse")

    assert rankings[["site", "scale", "rank", "selection_rule", "method", "rmse"]].to_dict("records") == [
        {
            "site": "manaus",
            "scale": "daily",
            "rank": 1,
            "selection_rule": "rmse",
            "method": "et_hargreaves_samani_corr",
            "rmse": 0.5,
        },
        {
            "site": "manaus",
            "scale": "daily",
            "rank": 2,
            "selection_rule": "rmse",
            "method": "et_priestley_taylor",
            "rmse": 0.7,
        },
        {
            "site": "manaus",
            "scale": "daily",
            "rank": 3,
            "selection_rule": "rmse",
            "method": "et_camargo",
            "rmse": 1.2,
        },
        {
            "site": "piracicaba",
            "scale": "monthly",
            "rank": 1,
            "selection_rule": "rmse",
            "method": "et_camargo",
            "rmse": 3.0,
        },
        {
            "site": "piracicaba",
            "scale": "monthly",
            "rank": 2,
            "selection_rule": "rmse",
            "method": "et_priestley_taylor",
            "rmse": 4.0,
        },
    ]
    assert rankings.loc[rankings["method"] == "et_hargreaves_samani_corr", "rank_rmse"].iloc[0] == 1
    assert rankings.loc[rankings["method"] == "et_camargo", "rank_mbe"].iloc[0] == 3


def test_build_rankings_adds_optional_site_metadata_when_available(tmp_path: Path) -> None:
    tables_dir = tmp_path / "tables"
    tables_dir.mkdir()
    pd.DataFrame(
        {
            "method": ["et_camargo"],
            "rmse": [1.2],
            "mae": [1.0],
            "mbe": [-0.2],
            "r2": [0.8],
            "willmott_d": [0.7],
            "c": [0.56],
        }
    ).to_csv(tables_dir / "manaus_daily_metrics.csv", index=False)

    rankings = build_rankings(
        tables_dir,
        sites=["manaus"],
        site_metadata={"manaus": {"biome": "Amazonia", "climate_class": "Af"}},
    )

    assert rankings.loc[0, "biome"] == "Amazonia"
    assert rankings.loc[0, "climate_class"] == "Af"


def test_write_rankings_creates_csv_and_markdown(tmp_path: Path) -> None:
    rankings = pd.DataFrame(
        {
            "site": ["manaus"],
            "scale": ["daily"],
            "rank": [1],
            "selection_rule": ["composite"],
            "method": ["et_hargreaves_samani_corr"],
            "rmse": [0.5],
            "mae": [0.4],
            "mbe": [0.0],
            "r2": [0.95],
            "willmott_d": [0.98],
            "rank_rmse": [1],
            "rank_mae": [1],
            "rank_mbe": [1],
            "rank_r2": [1],
            "rank_willmott_d": [1],
        }
    )

    csv_path, markdown_path = write_rankings(rankings, tmp_path / "tables", tmp_path / "reports")

    assert csv_path == tmp_path / "tables" / "summary_rankings.csv"
    assert markdown_path == tmp_path / "reports" / "summary_rankings.md"
    assert "et_hargreaves_samani_corr" in markdown_path.read_text()
    assert "Manaus" in markdown_path.read_text()
    assert "composite" in markdown_path.read_text()


def test_write_summary_creates_csv_and_markdown(tmp_path: Path) -> None:
    summary = pd.DataFrame(
        {
            "site": ["manaus"],
            "scale": ["daily"],
            "rank": [1],
            "selection_rule": ["composite"],
            "best_method": ["et_priestley_taylor"],
            "rmse": [0.7],
        }
    )

    csv_path, markdown_path = write_summary(summary, tmp_path)

    assert csv_path == tmp_path / "summary.csv"
    assert markdown_path == tmp_path / "summary.md"
    assert "et_priestley_taylor" in markdown_path.read_text()
