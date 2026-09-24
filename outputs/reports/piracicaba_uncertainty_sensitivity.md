# Uncertainty and sensitivity analysis: piracicaba

Bootstrap intervals use paired daily resampling against Penman-Monteith and are descriptive, not a substitute for measurement-error propagation.
Wet/dry grouping is data-driven from the median monthly rainfall within the analyzed year.

## Bootstrap intervals

| method | metric | estimate | ci_lower | ci_upper | n | n_boot | confidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| et_thornthwaite | rmse | 1.2325 | 1.1306 | 1.3235 | 366 | 1000 | 0.9500 |
| et_thornthwaite | mae | 0.9596 | 0.8784 | 1.0368 | 366 | 1000 | 0.9500 |
| et_thornthwaite | mbe | 0.0793 | -0.0493 | 0.1978 | 366 | 1000 | 0.9500 |
| et_thornthwaite_camargo | rmse | 3.4196 | 3.3032 | 3.5390 | 366 | 1000 | 0.9500 |
| et_thornthwaite_camargo | mae | 3.1605 | 3.0320 | 3.2909 | 366 | 1000 | 0.9500 |
| et_thornthwaite_camargo | mbe | -3.1604 | -3.2909 | -3.0319 | 366 | 1000 | 0.9500 |
| et_camargo | rmse | 2.1678 | 2.0707 | 2.2572 | 366 | 1000 | 0.9500 |
| et_camargo | mae | 1.9410 | 1.8436 | 2.0385 | 366 | 1000 | 0.9500 |
| et_camargo | mbe | -1.8616 | -1.9798 | -1.7446 | 366 | 1000 | 0.9500 |
| et_hargreaves_samani | rmse | 1.5587 | 1.4746 | 1.6409 | 366 | 1000 | 0.9500 |
| et_hargreaves_samani | mae | 1.3440 | 1.2666 | 1.4292 | 366 | 1000 | 0.9500 |
| et_hargreaves_samani | mbe | -1.2459 | -1.3396 | -1.1528 | 366 | 1000 | 0.9500 |
| et_hargreaves_samani_corr | rmse | 1.8777 | 1.8025 | 1.9476 | 366 | 1000 | 0.9500 |
| et_hargreaves_samani_corr | mae | 1.7409 | 1.6668 | 1.8121 | 366 | 1000 | 0.9500 |
| et_hargreaves_samani_corr | mbe | 1.7322 | 1.6573 | 1.8015 | 366 | 1000 | 0.9500 |
| et_priestley_taylor | rmse | 0.4982 | 0.4580 | 0.5393 | 366 | 1000 | 0.9500 |
| et_priestley_taylor | mae | 0.3934 | 0.3644 | 0.4232 | 366 | 1000 | 0.9500 |
| et_priestley_taylor | mbe | 0.1144 | 0.0625 | 0.1640 | 366 | 1000 | 0.9500 |
| et_garcia_lopez | rmse | 1.4046 | 1.3211 | 1.4851 | 366 | 1000 | 0.9500 |
| et_garcia_lopez | mae | 1.1946 | 1.1195 | 1.2698 | 366 | 1000 | 0.9500 |

Showing first 20 of 54 rows. See CSV outputs for complete tables.

## Monthly and rainfall-season errors

| period_type | period | method | n | rain_mm | rmse | mae | mbe |
| --- | --- | --- | --- | --- | --- | --- | --- |
| month | 2024-01 | et_thornthwaite | 31 | 136.6800 | 1.2413 | 0.9501 | 0.0092 |
| month | 2024-01 | et_thornthwaite_camargo | 31 | 136.6800 | 4.2067 | 4.0194 | -4.0194 |
| month | 2024-01 | et_camargo | 31 | 136.6800 | 2.5771 | 2.4146 | -2.3187 |
| month | 2024-01 | et_hargreaves_samani | 31 | 136.6800 | 1.9097 | 1.7500 | -1.6526 |
| month | 2024-01 | et_hargreaves_samani_corr | 31 | 136.6800 | 2.1397 | 2.0288 | 2.0288 |
| month | 2024-01 | et_priestley_taylor | 31 | 136.6800 | 0.5111 | 0.4491 | 0.4121 |
| month | 2024-01 | et_garcia_lopez | 31 | 136.6800 | 1.5879 | 1.4496 | -1.4436 |
| month | 2024-01 | et_makkink | 31 | 136.6800 | 0.3044 | 0.2452 | 0.0659 |
| month | 2024-01 | et_mccloud | 31 | 136.6800 | 80.6202 | 79.5934 | 79.5934 |
| month | 2024-01 | et_turc | 31 | 136.6800 | 0.8052 | 0.7635 | 0.7635 |
| month | 2024-01 | et_global_radiation | 31 | 136.6800 | 0.8916 | 0.8429 | 0.8429 |
| month | 2024-01 | et_ivanov | 31 | 136.6800 | 0.7842 | 0.6597 | -0.1862 |
| month | 2024-01 | et_jensen_heise | 31 | 136.6800 | 1.1672 | 1.0993 | 1.0993 |
| month | 2024-01 | et_net_radiation | 31 | 136.6800 | 0.7417 | 0.6918 | 0.6504 |
| month | 2024-01 | et_radiation_temperature | 31 | 136.6800 | 0.4707 | 0.4042 | -0.3206 |
| month | 2024-01 | et_lungeon | 31 | 136.6800 | 3.6612 | 3.5038 | -3.5006 |
| month | 2024-01 | et_stephens_stewart | 31 | 136.6800 | 0.2782 | 0.2141 | 0.0860 |
| month | 2024-01 | et_hicks_hess | 31 | 136.6800 | 1.1060 | 0.9187 | 0.8885 |
| month | 2024-02 | et_thornthwaite | 29 | 140.9840 | 1.4538 | 1.1804 | 0.4179 |
| month | 2024-02 | et_thornthwaite_camargo | 29 | 140.9840 | 3.9444 | 3.6904 | -3.6904 |

Showing first 20 of 252 rows. See CSV outputs for complete tables.

## Bias by reference ETo range

| method | eto_bin | eto_min | eto_max | n | mean_ref_eto | mean_bias | median_bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| et_thornthwaite | 1 | -0.0142 | 2.1969 | 92 | 1.4613 | 1.1404 | 1.1912 |
| et_thornthwaite | 2 | 2.1991 | 3.2563 | 91 | 2.7296 | 0.2394 | 0.5986 |
| et_thornthwaite | 3 | 3.2744 | 4.0793 | 91 | 3.6466 | -0.1145 | 0.1322 |
| et_thornthwaite | 4 | 4.0840 | 5.8921 | 92 | 4.8048 | -0.9487 | -0.8924 |
| et_thornthwaite_camargo | 1 | -0.0142 | 2.1969 | 92 | 1.4613 | -1.4613 | -1.6523 |
| et_thornthwaite_camargo | 2 | 2.1991 | 3.2563 | 91 | 2.7296 | -2.7296 | -2.7267 |
| et_thornthwaite_camargo | 3 | 3.2744 | 4.0793 | 91 | 3.6466 | -3.6466 | -3.6399 |
| et_thornthwaite_camargo | 4 | 4.0840 | 5.8921 | 92 | 4.8048 | -4.8048 | -4.7522 |
| et_camargo | 1 | -0.0142 | 2.1969 | 92 | 1.4613 | -0.4476 | -0.6503 |
| et_camargo | 2 | 2.1991 | 3.2563 | 91 | 2.7296 | -1.5822 | -1.5754 |
| et_camargo | 3 | 3.2744 | 4.0793 | 91 | 3.6466 | -2.2570 | -2.2806 |
| et_camargo | 4 | 4.0840 | 5.8921 | 92 | 4.8048 | -3.1608 | -3.1049 |
| et_hargreaves_samani | 1 | -0.0142 | 2.1969 | 92 | 1.4613 | -0.0883 | -0.1868 |
| et_hargreaves_samani | 2 | 2.1991 | 3.2563 | 91 | 2.7296 | -0.9668 | -0.9614 |
| et_hargreaves_samani | 3 | 3.2744 | 4.0793 | 91 | 3.6466 | -1.5567 | -1.5568 |
| et_hargreaves_samani | 4 | 4.0840 | 5.8921 | 92 | 4.8048 | -2.3719 | -2.3514 |
| et_hargreaves_samani_corr | 1 | -0.0142 | 2.1969 | 92 | 1.4613 | 2.0473 | 1.8773 |
| et_hargreaves_samani_corr | 2 | 2.1991 | 3.2563 | 91 | 2.7296 | 1.7752 | 1.5787 |
| et_hargreaves_samani_corr | 3 | 3.2744 | 4.0793 | 91 | 3.6466 | 1.6941 | 1.6426 |
| et_hargreaves_samani_corr | 4 | 4.0840 | 5.8921 | 92 | 4.8048 | 1.4124 | 1.3994 |

Showing first 20 of 72 rows. See CSV outputs for complete tables.

## Limitations

- Confidence intervals resample available paired days and do not model autocorrelation explicitly.
- Wet/dry labels are relative to each site's 2024 monthly rainfall distribution.
- Bias bins are quantile-based, so bin widths differ when the Penman-Monteith ETo distribution is uneven.
