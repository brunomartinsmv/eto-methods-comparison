# Methodological assumptions and sensitive implementation choices

This document records assumptions that affect interpretation of the ETo comparison. It is intended to let a reviewer audit the methodological decisions without reading the source code.

## Reference treatment: FAO-56 Penman-Monteith

Penman-Monteith FAO-56 is treated as the reference series for method comparison, not as an error-free physical truth. Metrics, bootstrap intervals, monthly errors, rainfall-season summaries, and ETo-bin bias tables are computed as deviations of each alternative method from `et_penman_monteith`.

The pipeline preserves the reference column supplied in the cleaned data. It does not recalibrate Penman-Monteith during analysis. Therefore, any uncertainty or measurement error in radiation, humidity, wind, or temperature inputs propagates into the reference but is not explicitly modeled in the current metrics.

## Net radiation

Net radiation is read from the cleaned daily data as `rad_net_mj_m2_d` when present. The current reproducible pipeline does not recompute net radiation from shortwave and longwave components. This avoids silently changing the scientific baseline from the legacy spreadsheets, but it means the analysis inherits the radiation assumptions and quality of the upstream data preparation.

Priestley-Taylor and Penman-Monteith are especially sensitive to net radiation. Biases in `rad_net_mj_m2_d` can therefore affect both the reference and one of the compared methods in correlated ways.

## Wind

Wind is represented by daily wind variables from the input sheets, standardized in cleaned data as `wind_mean_ms` and `wind_max_ms` when available. The analysis does not apply an additional height conversion or roughness correction at the metrics stage.

Because FAO-56 Penman-Monteith uses wind speed at 2 m, the validity of the reference depends on the upstream source having already supplied compatible wind values or having applied the needed conversion. Alternative temperature- or radiation-based methods do not use wind directly, so site-specific wind regimes can appear as systematic method bias.

## Humidity

Relative humidity variables are standardized as daily mean, maximum, and minimum humidity columns when available. The metrics stage does not recompute vapor pressure deficit or humidity corrections. Humidity affects the Penman-Monteith reference through the source-derived ETo values and is not perturbed in the uncertainty analysis.

This is important for Manaus, where high humidity and low vapor-pressure deficit can reduce aerodynamic demand. Temperature-only methods may miss this control and can show climate-specific bias.

## Missing days and interpolation

Cleaning produces one daily table per site for the target year. The data-quality reports in `outputs/reports/*_data_quality.csv` document missingness and interpolation counts by variable. The metrics functions use pairwise finite observations for each method-reference comparison, so rows with missing values in either the reference or the method are excluded for that method.

Interpolation is treated as an upstream data-preparation decision. The bootstrap analysis resamples the resulting daily paired records and does not distinguish observed from interpolated days. Confidence intervals therefore describe sampling variability in the analyzed daily series, not the uncertainty introduced by interpolation.

## Hargreaves-Samani corrected calibration

The corrected Hargreaves-Samani column is treated as a precomputed calibrated method (`et_hargreaves_samani_corr`). The current analysis compares it to Penman-Monteith but does not refit its coefficients during the pipeline.

This choice preserves compatibility with the existing results. It also means the corrected method should be interpreted as locally calibrated for the dataset that produced the column. Its coefficients may not transfer to another site, year, or climate regime without recalibration and validation on independent data.

## Monthly and rainfall-season analysis

Monthly error tables group daily errors by calendar month. Rainfall-season summaries split months into `wet` and `dry` groups using each site's median monthly rainfall in the analyzed year. This is a data-driven descriptive classification, not a climatological season definition.

This approach is justified for comparing Manaus and Piracicaba within the same pipeline because it avoids hard-coding site-specific seasonal calendars. It should not be used to infer long-term climatological wet/dry behavior from a single year.

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
