from __future__ import annotations

import pandas as pd
import pytest

from scripts.cleaning import clean_daily_with_audit
from scripts.config import load_pipeline_config


def test_clean_daily_limits_interpolation_to_max_gap() -> None:
    df = pd.DataFrame(
        {
            "date": pd.date_range("2024-01-01", periods=8, freq="D"),
            "tmed_c": [20.0, None, None, None, None, None, None, 30.0],
        }
    )

    cleaned, audit = clean_daily_with_audit(df, max_gap=2)

    assert cleaned["tmed_c"].iloc[3:5].isna().all()
    assert cleaned["tmed_c"].iloc[1:3].notna().all()
    assert cleaned["tmed_c"].iloc[5:7].notna().all()
    assert "tmed_c" in audit.long_gaps_by_variable
    assert audit.long_gaps_by_variable["tmed_c"][0][2] == 6


def test_pipeline_config_loads_defaults() -> None:
    pipeline = load_pipeline_config()
    assert pipeline.calibration_train_fraction == pytest.approx(0.7)
    assert pipeline.sensitivity_perturbation_min_pct == -50
    assert pipeline.uncertainty_bootstrap_samples == 1000
    assert pipeline.uncertainty_confidence == pytest.approx(0.95)
    assert pipeline.uncertainty_eto_bins == 4
    assert pipeline.uncertainty_rainfall_column == "rain_mm"
    assert pipeline.cleaning_max_gap_days == 7
