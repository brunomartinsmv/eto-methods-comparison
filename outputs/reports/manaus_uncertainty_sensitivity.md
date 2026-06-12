# Uncertainty and sensitivity analysis: manaus

Bootstrap intervals use paired daily resampling against Penman-Monteith and are descriptive, not a substitute for measurement-error propagation.
Wet/dry grouping is data-driven from the median monthly rainfall within the analyzed year.

## Bootstrap intervals

| method | metric | estimate | ci_lower | ci_upper | n | n_boot | confidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| et_thornthwaite | rmse | 2.6762 | 2.6300 | 2.7229 | 366 | 1000 | 0.9500 |
| et_thornthwaite | mae | 2.6345 | 2.5879 | 2.6819 | 366 | 1000 | 0.9500 |
| et_thornthwaite | mbe | 2.6345 | 2.5879 | 2.6819 | 366 | 1000 | 0.9500 |
| et_thornthwaite_camargo | rmse | 2.5779 | 2.5125 | 2.6430 | 366 | 1000 | 0.9500 |
| et_thornthwaite_camargo | mae | 2.4958 | 2.4309 | 2.5579 | 366 | 1000 | 0.9500 |
| et_thornthwaite_camargo | mbe | 2.4958 | 2.4309 | 2.5579 | 366 | 1000 | 0.9500 |
| et_camargo | rmse | 2.5997 | 2.5333 | 2.6664 | 366 | 1000 | 0.9500 |
| et_camargo | mae | 2.5135 | 2.4463 | 2.5850 | 366 | 1000 | 0.9500 |
| et_camargo | mbe | -2.4027 | -2.5066 | -2.2971 | 366 | 1000 | 0.9500 |
| et_hargreaves_samani | rmse | 2.5547 | 2.5199 | 2.5908 | 366 | 1000 | 0.9500 |
| et_hargreaves_samani | mae | 2.5304 | 2.4957 | 2.5682 | 366 | 1000 | 0.9500 |
| et_hargreaves_samani | mbe | 2.5304 | 2.4957 | 2.5682 | 366 | 1000 | 0.9500 |
| et_hargreaves_samani_corr | rmse | 0.3588 | 0.3309 | 0.3865 | 366 | 1000 | 0.9500 |
| et_hargreaves_samani_corr | mae | 0.2885 | 0.2677 | 0.3093 | 366 | 1000 | 0.9500 |
| et_hargreaves_samani_corr | mbe | 0.0000 | -0.0376 | 0.0371 | 366 | 1000 | 0.9500 |
| et_priestley_taylor | rmse | 2.3966 | 2.3388 | 2.4601 | 366 | 1000 | 0.9500 |
| et_priestley_taylor | mae | 2.3241 | 2.2651 | 2.3873 | 366 | 1000 | 0.9500 |
| et_priestley_taylor | mbe | -2.3241 | -2.3873 | -2.2651 | 366 | 1000 | 0.9500 |
| et_garcia_lopez | rmse | 35.0926 | 35.0215 | 35.1580 | 366 | 1000 | 0.9500 |
| et_garcia_lopez | mae | 35.0868 | 35.0150 | 35.1519 | 366 | 1000 | 0.9500 |

Showing first 20 of 21 rows. See CSV outputs for complete tables.

## Monthly and rainfall-season errors

| period_type | period | method | n | rain_mm | rmse | mae | mbe |
| --- | --- | --- | --- | --- | --- | --- | --- |
| month | 2024-01 | et_thornthwaite | 31 | 137.0000 | 2.5969 | 2.5451 | 2.5451 |
| month | 2024-01 | et_thornthwaite_camargo | 31 | 137.0000 | 2.5969 | 2.5451 | 2.5451 |
| month | 2024-01 | et_camargo | 31 | 137.0000 | 2.3286 | 2.2272 | -0.9183 |
| month | 2024-01 | et_hargreaves_samani | 31 | 137.0000 | 2.3579 | 2.3389 | 2.3389 |
| month | 2024-01 | et_hargreaves_samani_corr | 31 | 137.0000 | 0.2979 | 0.2633 | -0.0712 |
| month | 2024-01 | et_priestley_taylor | 31 | 137.0000 | 2.3008 | 2.2547 | -2.2547 |
| month | 2024-01 | et_garcia_lopez | 31 | 137.0000 | 35.1368 | 35.1331 | 35.1331 |
| month | 2024-02 | et_thornthwaite | 29 | 324.4000 | 2.5390 | 2.4544 | 2.4544 |
| month | 2024-02 | et_thornthwaite_camargo | 29 | 324.4000 | 2.4640 | 2.3767 | 2.3767 |
| month | 2024-02 | et_camargo | 29 | 324.4000 | 2.7329 | 2.6545 | -2.6545 |
| month | 2024-02 | et_hargreaves_samani | 29 | 324.4000 | 2.3376 | 2.3190 | 2.3190 |
| month | 2024-02 | et_hargreaves_samani_corr | 29 | 324.4000 | 0.3948 | 0.3447 | -0.1653 |
| month | 2024-02 | et_priestley_taylor | 29 | 324.4000 | 2.4685 | 2.4024 | -2.4024 |
| month | 2024-02 | et_garcia_lopez | 29 | 324.4000 | 34.9715 | 34.9656 | 34.9656 |
| month | 2024-03 | et_thornthwaite | 31 | 419.8000 | 2.7685 | 2.7043 | 2.7043 |
| month | 2024-03 | et_thornthwaite_camargo | 31 | 419.8000 | 2.8768 | 2.8150 | 2.8150 |
| month | 2024-03 | et_camargo | 31 | 419.8000 | 2.2942 | 2.2162 | -2.2162 |
| month | 2024-03 | et_hargreaves_samani | 31 | 419.8000 | 2.4049 | 2.3905 | 2.3905 |
| month | 2024-03 | et_hargreaves_samani_corr | 31 | 419.8000 | 0.2856 | 0.2412 | 0.0894 |
| month | 2024-03 | et_priestley_taylor | 31 | 419.8000 | 2.0759 | 2.0111 | -2.0111 |

Showing first 20 of 98 rows. See CSV outputs for complete tables.

## Bias by reference ETo range

| method | eto_bin | eto_min | eto_max | n | mean_ref_eto | mean_bias | median_bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| et_thornthwaite | 1 | 0.7094 | 2.1340 | 92 | 1.7085 | 3.1181 | 3.0855 |
| et_thornthwaite | 2 | 2.1415 | 2.5667 | 91 | 2.3677 | 2.6877 | 2.6797 |
| et_thornthwaite | 3 | 2.5695 | 2.9186 | 91 | 2.7330 | 2.5226 | 2.4301 |
| et_thornthwaite | 4 | 2.9224 | 4.5540 | 92 | 3.3331 | 2.2090 | 2.2134 |
| et_thornthwaite_camargo | 1 | 0.7094 | 2.1340 | 92 | 1.7085 | 3.3228 | 3.2283 |
| et_thornthwaite_camargo | 2 | 2.1415 | 2.5667 | 91 | 2.3677 | 2.6636 | 2.6528 |
| et_thornthwaite_camargo | 3 | 2.5695 | 2.9186 | 91 | 2.7330 | 2.2983 | 2.2973 |
| et_thornthwaite_camargo | 4 | 2.9224 | 4.5540 | 92 | 3.3331 | 1.6982 | 1.7817 |
| et_camargo | 1 | 0.7094 | 2.1340 | 92 | 1.7085 | -1.5361 | -1.7957 |
| et_camargo | 2 | 2.1415 | 2.5667 | 91 | 2.3677 | -2.1895 | -2.3785 |
| et_camargo | 3 | 2.5695 | 2.9186 | 91 | 2.7330 | -2.6406 | -2.7269 |
| et_camargo | 4 | 2.9224 | 4.5540 | 92 | 3.3331 | -3.2448 | -3.2496 |
| et_hargreaves_samani | 1 | 0.7094 | 2.1340 | 92 | 1.7085 | 2.4212 | 2.3883 |
| et_hargreaves_samani | 2 | 2.1415 | 2.5667 | 91 | 2.3677 | 2.6497 | 2.6451 |
| et_hargreaves_samani | 3 | 2.5695 | 2.9186 | 91 | 2.7330 | 2.5903 | 2.5555 |
| et_hargreaves_samani | 4 | 2.9224 | 4.5540 | 92 | 3.3331 | 2.4624 | 2.4530 |
| et_hargreaves_samani_corr | 1 | 0.7094 | 2.1340 | 92 | 1.7085 | 0.3584 | 0.3491 |
| et_hargreaves_samani_corr | 2 | 2.1415 | 2.5667 | 91 | 2.3677 | 0.1435 | 0.1444 |
| et_hargreaves_samani_corr | 3 | 2.5695 | 2.9186 | 91 | 2.7330 | -0.0687 | -0.1027 |
| et_hargreaves_samani_corr | 4 | 2.9224 | 4.5540 | 92 | 3.3331 | -0.4324 | -0.3868 |

Showing first 20 of 28 rows. See CSV outputs for complete tables.

## Limitations

- Confidence intervals resample available paired days and do not model autocorrelation explicitly.
- Wet/dry labels are relative to each site's 2024 monthly rainfall distribution.
- Bias bins are quantile-based, so bin widths differ when the Penman-Monteith ETo distribution is uneven.
