# Methodological assumptions and sensitive implementation choices

This document records the assumptions used to calculate and compare ET₀. It identifies the input transformations and the limits of the reported metrics.

## Reference treatment: FAO-56 Penman-Monteith

Penman-Monteith FAO-56 is treated as the reference series for method comparison, not as an error-free physical truth. Metrics, bootstrap intervals, monthly errors, rainfall-season summaries, and ETo-bin bias tables are computed as deviations of each alternative method from `et_penman_monteith`.

`quickstart` recalculates the reference from cleaned weather inputs and writes it to `outputs/results/{site}_daily_eto.csv`. Metrics prefer that file when it exists; otherwise, they use the spreadsheet reference retained in the cleaned data. Penman-Monteith is not calibrated. Measurement errors in radiation, humidity, wind, or temperature can affect the reference, but the metrics do not propagate those errors explicitly.

## Net radiation

Net radiation is read from the cleaned daily data as `rad_net_mj_m2_d` when present. The current reproducible pipeline does not recompute net radiation from shortwave and longwave components. This avoids silently changing the scientific baseline from the legacy spreadsheets, but it means the analysis inherits the radiation assumptions and quality of the upstream data preparation.

Priestley-Taylor and Penman-Monteith are especially sensitive to net radiation. Biases in `rad_net_mj_m2_d` can therefore affect both the reference and one of the compared methods in correlated ways.

## Wind

Daily wind inputs are standardized as `wind_mean_ms` and `wind_max_ms`. When calculating Penman-Monteith, the pipeline converts mean wind to 2 m using FAO-56 equation 47 and the site's `wind_height_m`. The default measurement height is 10 m when that metadata is absent; the source height must therefore be checked when adding a site.

The metrics stage compares the resulting ET₀ series without another wind conversion. Methods that omit wind can differ from the reference when aerodynamic demand changes.

## Humidity

Relative humidity inputs are standardized as daily mean, maximum, and minimum columns. The reference calculation estimates actual vapor pressure from minimum/maximum temperature and humidity when those columns exist, or from mean temperature and humidity otherwise. Saturation vapor pressure is calculated from mean temperature. These choices are implemented in `scripts/compute_eto.py` and `scripts/derived_meteo.py`.

The daily bootstrap resamples method-reference pairs without perturbing humidity. The separate optional OAT sensitivity command can perturb humidity inputs. Temperature-only methods omit this control on atmospheric demand.

## Limited-data Penman-Monteith

`python -m scripts.cli limited-data` writes `outputs/tables/{site}_limited_data_metrics.csv`. It recomputes FAO-56 Penman-Monteith after replacing wind, humidity, radiation, or all three, and scores those series against the full-data pipeline Penman-Monteith. Hargreaves-Samani and Turc are on the same table. They keep their usual inputs. They are not filled with the Penman-Monteith substitutes.

The reference is `et_penman_monteith` from `outputs/results/{site}_daily_eto.csv` when that file exists and `--input` is `data/cleaned`. A custom `--results-input` must contain the file. Without a pipeline file, the reference is the full-data equation recomputed from the cleaned weather. Every row uses the days on which the reference and all seven series are finite (`comparison_days = common_finite`).

Substitutes follow Allen et al. (1998):

- Wind, when replaced, is the site value `regional_wind_2m_ms` if it is set, otherwise 2 m s⁻¹. That substitute is already at 2 m and is not converted from the measurement height. Values below 0.5 m s⁻¹ are raised to 0.5 m s⁻¹ before they enter equation 6. Measured wind is still converted with equation 47 and is not floored.
- Humidity, when replaced, uses dewpoint equal to daily minimum temperature, so actual vapor pressure is saturation vapor pressure at Tmin (equation 48). Measured relative humidity is not used in that scenario. Saturation vapor pressure in the aerodynamic term stays es(Tmean), as in the full-data pipeline. The measured net-radiation column is kept, so this scenario changes only the aerodynamic humidity term.
- Radiation, when replaced, uses Rs = kRs √(Tmax − Tmin) Ra (equation 50). kRs is 0.16 for an interior site unless the site sets `k_rs` or `radiation_setting: coastal` (0.19). Estimated Rs is limited to clear-sky radiation Rso = (0.75 + 2×10⁻⁵ z) Ra (equation 37). Net radiation is then rebuilt as Rns − Rnl with albedo 0.23 (equations 38–40). Rs/Rso in the longwave term is limited to ≤ 1. Replacing radiation does not keep `rad_net_mj_m2_d`.
- The temperature approach (scenario `pm_pmt`) replaces all three. Estimated actual vapor pressure enters both the aerodynamic term and the longwave term.

Row order is the scenario list: full Penman-Monteith, wind replaced, humidity replaced, radiation replaced, all three replaced, Hargreaves-Samani, Turc. The table does not sort by error. Manaus and Piracicaba are humid demonstration climates. Agreement with calculated Penman-Monteith in this table is not a ranking taken from another climate.

## Missing days and interpolation

Cleaning produces one daily table per site for the target year. The data-quality reports in `outputs/reports/*_data_quality.csv` document missingness and interpolation counts by variable. The metrics functions use pairwise finite observations for each method-reference comparison, so rows with missing values in either the reference or the method are excluded for that method.

Interpolation is treated as an upstream data-preparation decision. The bootstrap analysis resamples the resulting daily paired records and does not distinguish observed from interpolated days. Confidence intervals therefore describe sampling variability in the analyzed daily series, not the uncertainty introduced by interpolation.

## Hargreaves-Samani corrected calibration

The corrected Hargreaves-Samani column is treated as a precomputed calibrated method (`et_hargreaves_samani_corr`). The current analysis compares it to Penman-Monteith but does not refit its coefficients during the pipeline.

The corrected series retains the calibration used to produce the spreadsheet column. Its coefficients may not transfer to another site, year, or climate regime without recalibration and validation on independent data.

## Monthly and rainfall-season analysis

Monthly totals sum finite daily estimates and preserve missing months as missing values. Each method has accompanying `_valid_days` and `_valid_fraction` columns. Partial totals are not rescaled to a full month; monthly comparisons can therefore involve unequal coverage, which must be checked before interpreting the ranking.

Monthly error tables in the uncertainty analysis group daily errors by calendar month. Rainfall-season summaries split months into `wet` and `dry` groups using each site's median monthly rainfall in the analyzed year. This is a data-driven descriptive classification, not a climatological season definition.

This rule applies the same descriptive classification to both sites without prescribing seasonal calendars. It should not be used to infer long-term climatological wet/dry behavior from a single year.

## Bootstrap uncertainty

Bootstrap confidence intervals use paired resampling of daily Penman-Monteith and method values. The implemented intervals cover RMSE, MAE, and MBE. The resampling is reproducible through a fixed random seed.

The method does not explicitly model temporal autocorrelation, instrument error, uncertainty in physical constants, or uncertainty from calibration. Intervals should be read as descriptive uncertainty for the available paired daily records.

## Bias by ETo range

Bias-by-bin tables split the Penman-Monteith daily ETo distribution into quantile bins and summarize method minus reference bias within each bin. Quantile bins keep sample sizes balanced, but the ETo width of each bin can differ.

These tables are intended to reveal whether a method behaves differently under low, moderate, and high atmospheric demand. They are not a replacement for process-level error attribution.

## Method-specific limitations

Penman-Monteith depends on physically consistent radiation, humidity, wind, and temperature inputs.

Thornthwaite and Camargo are primarily temperature-based and can miss radiative, humidity, and aerodynamic controls.

Thornthwaite-Camargo remains limited by its reliance on temperature and empirical adjustments.

Hargreaves-Samani uses daily temperature range as a radiation proxy and can degrade in humid climates where temperature range is a weak proxy for available energy.

Corrected Hargreaves-Samani can reduce local bias but may overfit local conditions if calibration and evaluation are not separated.

Priestley-Taylor assumes an energy-limited, well-watered surface and can underperform when aerodynamic controls or water limitation are important.

## Climate and locality limitations

Manaus represents a humid tropical setting where humidity, cloudiness, and limited daily temperature range can challenge temperature-only methods.

Piracicaba represents a subtropical/agricultural setting with stronger seasonality and periods where water availability and atmospheric demand may diverge. Locally calibrated methods may perform well there but should not be assumed transferable.

The study uses 2024 data. Single-year results should be interpreted as a reproducible case study rather than a definitive climatological ranking.
