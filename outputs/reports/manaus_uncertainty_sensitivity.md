# Uncertainty and sensitivity analysis: manaus

Bootstrap intervals use paired daily resampling against Penman-Monteith and are descriptive, not a substitute for measurement-error propagation.
Wet/dry grouping is data-driven from the median monthly rainfall within the analyzed year.

## Bootstrap intervals

| method | metric | estimate | ci_lower | ci_upper | n | n_boot | confidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| et_thornthwaite | rmse | 4.1902 | 4.1570 | 4.2246 | 366 | 1000 | 0.9500 |
| et_thornthwaite | mae | 4.1763 | 4.1422 | 4.2124 | 366 | 1000 | 0.9500 |
| et_thornthwaite | mbe | 4.1763 | 4.1422 | 4.2124 | 366 | 1000 | 0.9500 |
| et_thornthwaite_camargo | rmse | 4.0750 | 4.0214 | 4.1256 | 366 | 1000 | 0.9500 |
| et_thornthwaite_camargo | mae | 4.0376 | 3.9794 | 4.0917 | 366 | 1000 | 0.9500 |
| et_thornthwaite_camargo | mbe | 4.0376 | 3.9794 | 4.0917 | 366 | 1000 | 0.9500 |
| et_camargo | rmse | 1.0691 | 1.0350 | 1.1010 | 366 | 1000 | 0.9500 |
| et_camargo | mae | 0.9969 | 0.9555 | 1.0366 | 366 | 1000 | 0.9500 |
| et_camargo | mbe | 0.9732 | 0.9250 | 1.0187 | 366 | 1000 | 0.9500 |
| et_hargreaves_samani | rmse | 1.1537 | 1.1202 | 1.1853 | 366 | 1000 | 0.9500 |
| et_hargreaves_samani | mae | 1.0857 | 1.0443 | 1.1261 | 366 | 1000 | 0.9500 |
| et_hargreaves_samani | mbe | 1.0741 | 1.0294 | 1.1162 | 366 | 1000 | 0.9500 |
| et_hargreaves_samani_corr | rmse | 1.5976 | 1.5622 | 1.6362 | 366 | 1000 | 0.9500 |
| et_hargreaves_samani_corr | mae | 1.5418 | 1.5005 | 1.5855 | 366 | 1000 | 0.9500 |
| et_hargreaves_samani_corr | mbe | 1.5418 | 1.5005 | 1.5855 | 366 | 1000 | 0.9500 |
| et_priestley_taylor | rmse | 1.0344 | 0.9709 | 1.1002 | 366 | 1000 | 0.9500 |
| et_priestley_taylor | mae | 0.8910 | 0.8356 | 0.9460 | 366 | 1000 | 0.9500 |
| et_priestley_taylor | mbe | -0.8910 | -0.9460 | -0.8356 | 366 | 1000 | 0.9500 |
| et_garcia_lopez | rmse | 1.0496 | 0.9871 | 1.1157 | 366 | 1000 | 0.9500 |
| et_garcia_lopez | mae | 0.9230 | 0.8686 | 0.9780 | 366 | 1000 | 0.9500 |

Showing first 20 of 54 rows. See CSV outputs for complete tables.

## Monthly and rainfall-season errors

| period_type | period | method | n | rain_mm | rmse | mae | mbe |
| --- | --- | --- | --- | --- | --- | --- | --- |
| month | 2024-01 | et_thornthwaite | 31 | 137.0000 | 4.1577 | 4.1470 | 4.1470 |
| month | 2024-01 | et_thornthwaite_camargo | 31 | 137.0000 | 4.1577 | 4.1470 | 4.1470 |
| month | 2024-01 | et_camargo | 31 | 137.0000 | 1.0617 | 1.0343 | 1.0343 |
| month | 2024-01 | et_hargreaves_samani | 31 | 137.0000 | 1.1211 | 1.0852 | 1.0852 |
| month | 2024-01 | et_hargreaves_samani_corr | 31 | 137.0000 | 1.5613 | 1.5307 | 1.5307 |
| month | 2024-01 | et_priestley_taylor | 31 | 137.0000 | 0.8184 | 0.7717 | -0.7717 |
| month | 2024-01 | et_garcia_lopez | 31 | 137.0000 | 0.8623 | 0.8201 | -0.8201 |
| month | 2024-01 | et_makkink | 31 | 137.0000 | 0.9263 | 0.8858 | -0.8858 |
| month | 2024-01 | et_mccloud | 31 | 137.0000 | 102.7385 | 102.4732 | 102.4732 |
| month | 2024-01 | et_turc | 31 | 137.0000 | 0.4269 | 0.3450 | -0.3348 |
| month | 2024-01 | et_global_radiation | 31 | 137.0000 | 0.7974 | 0.7506 | -0.7506 |
| month | 2024-01 | et_ivanov | 31 | 137.0000 | 2.9809 | 2.8969 | 2.8969 |
| month | 2024-01 | et_jensen_heise | 31 | 137.0000 | 0.7690 | 0.7241 | -0.7241 |
| month | 2024-01 | et_net_radiation | 31 | 137.0000 | 0.8153 | 0.7683 | -0.7683 |
| month | 2024-01 | et_radiation_temperature | 31 | 137.0000 | 0.8212 | 0.7748 | -0.7748 |
| month | 2024-01 | et_lungeon | 31 | 137.0000 | 0.4157 | 0.3665 | -0.3665 |
| month | 2024-01 | et_stephens_stewart | 31 | 137.0000 | 0.8058 | 0.7599 | -0.7599 |
| month | 2024-01 | et_hicks_hess | 31 | 137.0000 | 0.7848 | 0.7435 | -0.7435 |
| month | 2024-02 | et_thornthwaite | 29 | 324.4000 | 4.1194 | 4.0859 | 4.0859 |
| month | 2024-02 | et_thornthwaite_camargo | 29 | 324.4000 | 4.0424 | 4.0083 | 4.0083 |

Showing first 20 of 252 rows. See CSV outputs for complete tables.

## Bias by reference ETo range

| method | eto_bin | eto_min | eto_max | n | mean_ref_eto | mean_bias | median_bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| et_thornthwaite | 1 | 0.0777 | 0.5944 | 92 | 0.4025 | 4.3967 | 4.4522 |
| et_thornthwaite | 2 | 0.5987 | 0.8982 | 91 | 0.7475 | 4.2656 | 4.2901 |
| et_thornthwaite | 3 | 0.8991 | 1.2751 | 91 | 1.0720 | 4.1745 | 4.1554 |
| et_thornthwaite | 4 | 1.2777 | 3.0744 | 92 | 1.7507 | 3.8695 | 3.8944 |
| et_thornthwaite_camargo | 1 | 0.0777 | 0.5944 | 92 | 0.4025 | 4.6288 | 4.6134 |
| et_thornthwaite_camargo | 2 | 0.5987 | 0.8982 | 91 | 0.7475 | 4.2838 | 4.2792 |
| et_thornthwaite_camargo | 3 | 0.8991 | 1.2751 | 91 | 1.0720 | 3.9592 | 3.9750 |
| et_thornthwaite_camargo | 4 | 1.2777 | 3.0744 | 92 | 1.7507 | 3.2806 | 3.4023 |
| et_camargo | 1 | 0.0777 | 0.5944 | 92 | 0.4025 | 1.4250 | 1.4144 |
| et_camargo | 2 | 0.5987 | 0.8982 | 91 | 0.7475 | 1.1711 | 1.1735 |
| et_camargo | 3 | 0.8991 | 1.2751 | 91 | 1.0720 | 0.9271 | 0.9316 |
| et_camargo | 4 | 1.2777 | 3.0744 | 92 | 1.7507 | 0.3714 | 0.5073 |
| et_hargreaves_samani | 1 | 0.0777 | 0.5944 | 92 | 0.4025 | 1.3394 | 1.3524 |
| et_hargreaves_samani | 2 | 0.5987 | 0.8982 | 91 | 0.7475 | 1.2916 | 1.3251 |
| et_hargreaves_samani | 3 | 0.8991 | 1.2751 | 91 | 1.0720 | 1.1028 | 1.1005 |
| et_hargreaves_samani | 4 | 1.2777 | 3.0744 | 92 | 1.7507 | 0.5652 | 0.6679 |
| et_hargreaves_samani_corr | 1 | 0.0777 | 0.5944 | 92 | 0.4025 | 1.7335 | 1.7747 |
| et_hargreaves_samani_corr | 2 | 0.5987 | 0.8982 | 91 | 0.7475 | 1.7529 | 1.7909 |
| et_hargreaves_samani_corr | 3 | 0.8991 | 1.2751 | 91 | 1.0720 | 1.5948 | 1.5757 |
| et_hargreaves_samani_corr | 4 | 1.2777 | 3.0744 | 92 | 1.7507 | 1.0891 | 1.1417 |

Showing first 20 of 72 rows. See CSV outputs for complete tables.

## Limitations

- Confidence intervals resample available paired days and do not model autocorrelation explicitly.
- Wet/dry labels are relative to each site's 2024 monthly rainfall distribution.
- Bias bins are quantile-based, so bin widths differ when the Penman-Monteith ETo distribution is uneven.
