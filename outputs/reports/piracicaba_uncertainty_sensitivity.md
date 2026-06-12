# Uncertainty and sensitivity analysis: piracicaba

Bootstrap intervals use paired daily resampling against Penman-Monteith and are descriptive, not a substitute for measurement-error propagation.
Wet/dry grouping is data-driven from the median monthly rainfall within the analyzed year.

## Bootstrap intervals

| method | metric | estimate | ci_lower | ci_upper | n | n_boot | confidence |
| --- | --- | --- | --- | --- | --- | --- | --- |
| et_thornthwaite | rmse | 2.2480 | 2.1304 | 2.3623 | 366 | 1000 | 0.9500 |
| et_thornthwaite | mae | 1.9378 | 1.8210 | 2.0545 | 366 | 1000 | 0.9500 |
| et_thornthwaite | mbe | -1.6530 | -1.8103 | -1.4972 | 366 | 1000 | 0.9500 |
| et_thornthwaite_camargo | rmse | 5.1084 | 4.9732 | 5.2425 | 366 | 1000 | 0.9500 |
| et_thornthwaite_camargo | mae | 4.8927 | 4.7475 | 5.0401 | 366 | 1000 | 0.9500 |
| et_thornthwaite_camargo | mbe | -4.8927 | -5.0401 | -4.7475 | 366 | 1000 | 0.9500 |
| et_camargo | rmse | 2.2619 | 2.1542 | 2.3762 | 366 | 1000 | 0.9500 |
| et_camargo | mae | 1.9877 | 1.8819 | 2.0983 | 366 | 1000 | 0.9500 |
| et_camargo | mbe | -1.7105 | -1.8613 | -1.5631 | 366 | 1000 | 0.9500 |
| et_hargreaves_samani | rmse | 0.7821 | 0.7339 | 0.8362 | 366 | 1000 | 0.9500 |
| et_hargreaves_samani | mae | 0.6525 | 0.6090 | 0.7013 | 366 | 1000 | 0.9500 |
| et_hargreaves_samani | mbe | -0.2020 | -0.2786 | -0.1221 | 366 | 1000 | 0.9500 |
| et_hargreaves_samani_corr | rmse | 0.7523 | 0.7051 | 0.8017 | 366 | 1000 | 0.9500 |
| et_hargreaves_samani_corr | mae | 0.6181 | 0.5764 | 0.6612 | 366 | 1000 | 0.9500 |
| et_hargreaves_samani_corr | mbe | -0.0000 | -0.0760 | 0.0779 | 366 | 1000 | 0.9500 |
| et_priestley_taylor | rmse | 1.9575 | 1.8266 | 2.0887 | 366 | 1000 | 0.9500 |
| et_priestley_taylor | mae | 1.5362 | 1.4212 | 1.6620 | 366 | 1000 | 0.9500 |
| et_priestley_taylor | mbe | 1.4373 | 1.3066 | 1.5698 | 366 | 1000 | 0.9500 |
| et_garcia_lopez | rmse | 17.4512 | 16.6491 | 18.2835 | 366 | 1000 | 0.9500 |
| et_garcia_lopez | mae | 16.0792 | 15.3899 | 16.7950 | 366 | 1000 | 0.9500 |

Showing first 20 of 21 rows. See CSV outputs for complete tables.

## Monthly and rainfall-season errors

| period_type | period | method | n | rain_mm | rmse | mae | mbe |
| --- | --- | --- | --- | --- | --- | --- | --- |
| month | 2024-01 | et_thornthwaite | 31 | 136.6800 | 2.0484 | 1.7661 | -1.5320 |
| month | 2024-01 | et_thornthwaite_camargo | 31 | 136.6800 | 5.7245 | 5.5607 | -5.5607 |
| month | 2024-01 | et_camargo | 31 | 136.6800 | 1.9474 | 1.6637 | -1.3941 |
| month | 2024-01 | et_hargreaves_samani | 31 | 136.6800 | 0.5725 | 0.4581 | 0.2379 |
| month | 2024-01 | et_hargreaves_samani_corr | 31 | 136.6800 | 0.6900 | 0.5866 | 0.4876 |
| month | 2024-01 | et_priestley_taylor | 31 | 136.6800 | 2.7031 | 2.5236 | 2.5236 |
| month | 2024-01 | et_garcia_lopez | 31 | 136.6800 | 20.5186 | 19.7961 | 19.7961 |
| month | 2024-02 | et_thornthwaite | 29 | 140.9840 | 1.5463 | 1.3187 | -0.8639 |
| month | 2024-02 | et_thornthwaite_camargo | 29 | 140.9840 | 5.1350 | 4.9723 | -4.9723 |
| month | 2024-02 | et_camargo | 29 | 140.9840 | 1.5927 | 1.3640 | -0.9445 |
| month | 2024-02 | et_hargreaves_samani | 29 | 140.9840 | 0.6663 | 0.5187 | 0.3612 |
| month | 2024-02 | et_hargreaves_samani_corr | 29 | 140.9840 | 0.7944 | 0.6193 | 0.5908 |
| month | 2024-02 | et_priestley_taylor | 29 | 140.9840 | 2.6548 | 2.4475 | 2.4475 |
| month | 2024-02 | et_garcia_lopez | 29 | 140.9840 | 21.3371 | 20.8299 | 20.8299 |
| month | 2024-03 | et_thornthwaite | 31 | 163.8300 | 1.7147 | 1.5231 | -0.6348 |
| month | 2024-03 | et_thornthwaite_camargo | 31 | 163.8300 | 4.8891 | 4.6224 | -4.6224 |
| month | 2024-03 | et_camargo | 31 | 163.8300 | 1.8921 | 1.7255 | -1.0212 |
| month | 2024-03 | et_hargreaves_samani | 31 | 163.8300 | 0.7059 | 0.5923 | 0.0132 |
| month | 2024-03 | et_hargreaves_samani_corr | 31 | 163.8300 | 0.7032 | 0.5554 | 0.2128 |
| month | 2024-03 | et_priestley_taylor | 31 | 163.8300 | 2.3781 | 2.1149 | 2.1149 |

Showing first 20 of 98 rows. See CSV outputs for complete tables.

## Bias by reference ETo range

| method | eto_bin | eto_min | eto_max | n | mean_ref_eto | mean_bias | median_bias |
| --- | --- | --- | --- | --- | --- | --- | --- |
| et_thornthwaite | 1 | 0.5308 | 4.0391 | 92 | 2.9905 | 0.0073 | -0.0732 |
| et_thornthwaite | 2 | 4.0513 | 4.9273 | 91 | 4.5289 | -1.6421 | -1.3809 |
| et_thornthwaite | 3 | 4.9295 | 5.9376 | 91 | 5.3543 | -2.0000 | -1.6935 |
| et_thornthwaite | 4 | 5.9393 | 9.5146 | 92 | 6.6980 | -2.9807 | -2.7559 |
| et_thornthwaite_camargo | 1 | 0.5308 | 4.0391 | 92 | 2.9905 | -2.9905 | -3.1611 |
| et_thornthwaite_camargo | 2 | 4.0513 | 4.9273 | 91 | 4.5289 | -4.5289 | -4.5662 |
| et_thornthwaite_camargo | 3 | 4.9295 | 5.9376 | 91 | 5.3543 | -5.3543 | -5.3167 |
| et_thornthwaite_camargo | 4 | 5.9393 | 9.5146 | 92 | 6.6980 | -6.6980 | -6.5355 |
| et_camargo | 1 | 0.5308 | 4.0391 | 92 | 2.9905 | 0.0351 | 0.1130 |
| et_camargo | 2 | 4.0513 | 4.9273 | 91 | 4.5289 | -1.7278 | -1.9462 |
| et_camargo | 3 | 4.9295 | 5.9376 | 91 | 5.3543 | -2.0879 | -1.9009 |
| et_camargo | 4 | 5.9393 | 9.5146 | 92 | 6.6980 | -3.0657 | -2.9093 |
| et_hargreaves_samani | 1 | 0.5308 | 4.0391 | 92 | 2.9905 | 0.4863 | 0.5699 |
| et_hargreaves_samani | 2 | 4.0513 | 4.9273 | 91 | 4.5289 | -0.3386 | -0.5381 |
| et_hargreaves_samani | 3 | 4.9295 | 5.9376 | 91 | 5.3543 | -0.3565 | -0.4018 |
| et_hargreaves_samani | 4 | 5.9393 | 9.5146 | 92 | 6.6980 | -0.6022 | -0.4965 |
| et_hargreaves_samani_corr | 1 | 0.5308 | 4.0391 | 92 | 2.9905 | 0.6360 | 0.6662 |
| et_hargreaves_samani_corr | 2 | 4.0513 | 4.9273 | 91 | 4.5289 | -0.1582 | -0.3637 |
| et_hargreaves_samani_corr | 3 | 4.9295 | 5.9376 | 91 | 5.3543 | -0.1413 | -0.1878 |
| et_hargreaves_samani_corr | 4 | 5.9393 | 9.5146 | 92 | 6.6980 | -0.3398 | -0.2338 |

Showing first 20 of 28 rows. See CSV outputs for complete tables.

## Limitations

- Confidence intervals resample available paired days and do not model autocorrelation explicitly.
- Wet/dry labels are relative to each site's 2024 monthly rainfall distribution.
- Bias bins are quantile-based, so bin widths differ when the Penman-Monteith ETo distribution is uneven.
