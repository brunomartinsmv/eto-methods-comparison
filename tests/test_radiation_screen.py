import argparse
from pathlib import Path

import pandas as pd
import pytest

from scripts import cli
from scripts.metrics import compute_metrics
from scripts.quality import build_quality_report
from scripts.radiation_screen import envelope_counts, radiation_consistency_frame


def _sample_frame() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "date": pd.to_datetime(["2024-01-01", "2024-01-02", "2024-01-03", "2024-01-04"]),
            "rad_global_mj_m2_d": [0.510083333333333, 12.0, 13.5, 20.0],
            "ra_extraterrestre_mj_m2_d": [16.7, 16.7, 16.7, 16.7],
            "rad_net_mj_m2_d": [0.2346383333333332, 6.0, 7.0, 8.0],
            "tmed_c": [28.3, 28.0, 27.0, 26.0],
        }
    )


def test_manaus_low_radiation_day_is_outside_clear_sky_envelope() -> None:
    original = _sample_frame()
    net = original["rad_net_mj_m2_d"].copy()
    screen = radiation_consistency_frame(original, elevation_m=61.25)
    rso = (0.75 + 2e-5 * 61.25) * 16.7

    assert "rad_net_mj_m2_d" not in screen.columns
    assert original["rad_net_mj_m2_d"].tolist() == net.tolist()
    assert screen.loc[0, "rs_over_ra"] == pytest.approx(0.510083333333333 / 16.7)
    assert screen.loc[0, "rs_over_rso"] == pytest.approx(0.510083333333333 / rso)
    assert screen["envelope_status"].tolist() == [
        "below_cloudiness_floor",
        "inside",
        "above_clear_sky",
        "above_extraterrestrial",
    ]
    assert screen["inside_envelope"].tolist() == [False, True, False, False]
    assert envelope_counts(screen) == {"inside": 1, "outside": 3, "unevaluable": 0}


def test_missing_radiation_is_unevaluable_not_outside() -> None:
    frame = pd.DataFrame(
        {
            "date": pd.to_datetime(["2024-01-01", "2024-01-02"]),
            "rad_global_mj_m2_d": [12.0, None],
            "ra_extraterrestre_mj_m2_d": [16.7, 16.7],
        }
    )
    screen = radiation_consistency_frame(frame, elevation_m=546.0)
    assert screen["envelope_status"].tolist() == ["inside", "unevaluable"]
    assert envelope_counts(screen) == {"inside": 1, "outside": 0, "unevaluable": 1}


def test_clear_sky_ratio_can_use_computed_extraterrestrial_radiation() -> None:
    frame = pd.DataFrame(
        {
            "date": pd.to_datetime(["2024-07-01"]),
            "rad_global_mj_m2_d": [18.0],
        }
    )
    screen = radiation_consistency_frame(frame, elevation_m=61.25, latitude_deg=-3.1019)
    assert screen.loc[0, "ra_mj_m2_d"] > 20
    assert screen.loc[0, "envelope_status"] == "inside"


def test_latitude_overrides_constant_spreadsheet_extraterrestrial_radiation() -> None:
    frame = pd.DataFrame(
        {
            "date": pd.to_datetime(["2024-01-01"]),
            "rad_global_mj_m2_d": [0.510083333333333],
            "ra_extraterrestre_mj_m2_d": [16.7],
        }
    )
    screen = radiation_consistency_frame(frame, elevation_m=61.25, latitude_deg=-3.1019)
    assert screen.loc[0, "ra_mj_m2_d"] > 30
    assert screen.loc[0, "rs_over_ra"] < 0.51 / 16.7
    assert screen.loc[0, "envelope_status"] == "below_cloudiness_floor"
    assert frame.loc[0, "ra_extraterrestre_mj_m2_d"] == 16.7


def test_quality_report_counts_days_outside_the_envelope() -> None:
    frame = _sample_frame()
    report = build_quality_report(
        site="manaus",
        raw_df=frame,
        cleaned_df=frame,
        year=2024,
        elevation_m=61.25,
    )
    envelope = report.loc[report["stage"] == "radiation_envelope"].iloc[0]
    assert envelope["variable"] == "rad_global_mj_m2_d"
    assert int(envelope["envelope_days_inside"]) == 1
    assert int(envelope["envelope_days_outside"]) == 3
    assert int(envelope["envelope_days_unevaluable"]) == 0
    assert int(envelope["physical_limit_violations"]) == 0

    without_elevation = build_quality_report(
        site="manaus",
        raw_df=frame,
        cleaned_df=frame,
        year=2024,
    )
    assert "radiation_envelope" not in set(without_elevation["stage"])


def test_screened_metrics_drop_days_outside_the_envelope() -> None:
    frame = pd.DataFrame(
        {
            "date": pd.to_datetime(["2024-01-01", "2024-01-02"]),
            "rad_global_mj_m2_d": [0.51, 12.0],
            "ra_extraterrestre_mj_m2_d": [16.7, 16.7],
            "et_penman_monteith": [0.6, 4.0],
            "et_turc": [0.5, 3.5],
        }
    )
    screen = radiation_consistency_frame(frame, elevation_m=61.25)
    full = compute_metrics(frame, "et_penman_monteith", ["et_turc"])
    screened = compute_metrics(frame.loc[screen["inside_envelope"]], "et_penman_monteith", ["et_turc"])
    assert full.loc[0, "rmse"] != pytest.approx(screened.loc[0, "rmse"])
    assert screened.loc[0, "rmse"] == pytest.approx(0.5)


def test_cmd_metrics_writes_screened_table_without_changing_net_radiation(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> None:
    cleaned = tmp_path / "cleaned"
    results = tmp_path / "results"
    tables = tmp_path / "tables"
    cleaned.mkdir()
    results.mkdir()
    dates = pd.to_datetime(["2024-01-01", "2024-01-02"])
    weather = pd.DataFrame(
        {
            "date": dates,
            "rad_global_mj_m2_d": [0.51, 12.0],
            "ra_extraterrestre_mj_m2_d": [16.7, 16.7],
            "rad_net_mj_m2_d": [0.23, 6.0],
            "et_penman_monteith": [0.6, 4.0],
            "et_turc": [0.5, 3.5],
        }
    )
    weather.to_csv(cleaned / "manaus_daily.csv", index=False)
    weather[["date", "et_penman_monteith", "et_turc"]].to_csv(
        results / "manaus_daily_eto.csv", index=False
    )
    monkeypatch.setattr("scripts.eto_io.OUTPUTS_RESULTS", results)
    monkeypatch.setattr(
        cli,
        "_selected_sites",
        lambda _: {"manaus": {"alt_m": 61.25, "lat": -3.1019}},
    )

    cli.cmd_metrics(
        argparse.Namespace(
            input=str(cleaned),
            output=str(tables),
            year=2024,
            site="manaus",
            all_sites=False,
        )
    )

    full = pd.read_csv(tables / "manaus_daily_metrics.csv")
    screened = pd.read_csv(tables / "manaus_daily_metrics_radiation_screen.csv")
    assert full["method"].tolist() == ["et_turc"]
    assert screened["method"].tolist() == ["et_turc"]
    assert full.loc[0, "rmse"] != pytest.approx(screened.loc[0, "rmse"])
    assert screened.loc[0, "rmse"] == pytest.approx(0.5)
    assert (tables / "manaus_monthly_metrics.csv").exists()
    reread = pd.read_csv(cleaned / "manaus_daily.csv")
    assert reread["rad_net_mj_m2_d"].tolist() == pytest.approx([0.23, 6.0])
