from scripts.naming import (
    bias_bins_filename,
    bootstrap_filename,
    calibration_coefficients_filename,
    calibration_metrics_filename,
    cleaned_daily_filename,
    daily_eto_filename,
    figure_filename,
    metrics_filename,
    monthly_totals_filename,
    rolling_7d_filename,
    seasonal_filename,
    sensitivity_filename,
)


def test_cleaned_daily_filename() -> None:
    assert cleaned_daily_filename("manaus") == "manaus_daily.csv"


def test_rolling_7d_filename() -> None:
    assert rolling_7d_filename("piracicaba") == "piracicaba_rolling_7d.csv"


def test_monthly_totals_filename() -> None:
    assert monthly_totals_filename("manaus") == "manaus_monthly_totals.csv"


def test_daily_eto_filename() -> None:
    assert daily_eto_filename("manaus") == "manaus_daily_eto.csv"


def test_metrics_filename() -> None:
    assert metrics_filename("manaus", "daily") == "manaus_daily_metrics.csv"
    assert metrics_filename("manaus", "monthly") == "manaus_monthly_metrics.csv"


def test_bootstrap_filename() -> None:
    assert bootstrap_filename("manaus") == "manaus_bootstrap_metric_intervals.csv"


def test_seasonal_filename() -> None:
    assert seasonal_filename("manaus") == "manaus_seasonal_error_metrics.csv"


def test_bias_bins_filename() -> None:
    assert bias_bins_filename("manaus") == "manaus_bias_by_eto_bin.csv"


def test_sensitivity_filename() -> None:
    assert sensitivity_filename("manaus", "penman_monteith") == "manaus_sensitivity_penman_monteith.csv"


def test_calibration_filenames() -> None:
    assert (
        calibration_coefficients_filename("manaus", "hargreaves_samani")
        == "manaus_hargreaves_samani_calibration_coefficients.csv"
    )
    assert (
        calibration_metrics_filename("manaus", "hargreaves_samani")
        == "manaus_hargreaves_samani_calibration_metrics.csv"
    )


def test_figure_filename() -> None:
    assert figure_filename("manaus", "daily_taylor") == "manaus_daily_taylor.png"
