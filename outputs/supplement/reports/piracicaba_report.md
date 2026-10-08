# ET₀ site report — Piracicaba

Mata Atlantica · Cwa · SP · Brazil

[← Results index](../index.md)

## Site metadata

- **Latitude**: -22.7083
- **Longitude**: -47.6333
- **Altitude (m)**: 546.0
- **Biome**: Mata Atlantica
- **Climate**: Cwa
- **Region**: Southeast
- **Country**: Brazil
- **State**: SP

## Data quality

Coverage and QC flags by input variable.

| site | variable | row_count | expected_days | start_date | end_date | missing_dates | duplicate_dates | missing_values | interpolated_values | physical_limit_violations |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| piracicaba | tmed_c | 366 | 366 | 2024-01-01 | 2024-12-31 | — | — | 0 | 0 | 0 |
| piracicaba | rh_mean_pct | 366 | 366 | 2024-01-01 | 2024-12-31 | — | — | 0 | 0 | 0 |
| piracicaba | wind_mean_ms | 366 | 366 | 2024-01-01 | 2024-12-31 | — | — | 0 | 0 | 0 |
| piracicaba | tmax_c | 366 | 366 | 2024-01-01 | 2024-12-31 | — | — | 0 | 0 | 0 |
| piracicaba | rh_max_pct | 366 | 366 | 2024-01-01 | 2024-12-31 | — | — | 0 | 0 | 0 |
| piracicaba | wind_max_ms | 366 | 366 | 2024-01-01 | 2024-12-31 | — | — | 0 | 0 | 0 |
| piracicaba | tmin_c | 366 | 366 | 2024-01-01 | 2024-12-31 | — | — | 0 | 0 | 0 |
| piracicaba | rh_min_pct | 366 | 366 | 2024-01-01 | 2024-12-31 | — | — | 0 | 0 | 0 |
| piracicaba | rain_mm | 366 | 366 | 2024-01-01 | 2024-12-31 | — | — | 0 | 0 | 0 |
| piracicaba | rad_global_mj_m2_d | 366 | 366 | 2024-01-01 | 2024-12-31 | — | — | 0 | 0 | 0 |
| piracicaba | rad_net_mj_m2_d | 366 | 366 | 2024-01-01 | 2024-12-31 | — | — | 0 | 0 | 0 |
| piracicaba | et_thornthwaite | 366 | 366 | 2024-01-01 | 2024-12-31 | — | — | 0 | 0 | 0 |
| piracicaba | et_thornthwaite_camargo | 366 | 366 | 2024-01-01 | 2024-12-31 | — | — | 0 | 0 | 0 |
| piracicaba | et_camargo | 366 | 366 | 2024-01-01 | 2024-12-31 | — | — | 0 | 0 | 0 |
| piracicaba | et_hargreaves_samani | 366 | 366 | 2024-01-01 | 2024-12-31 | — | — | 0 | 0 | 0 |
| piracicaba | et_hargreaves_samani_corr | 366 | 366 | 2024-01-01 | 2024-12-31 | — | — | 0 | 0 | 0 |
| piracicaba | et_priestley_taylor | 366 | 366 | 2024-01-01 | 2024-12-31 | — | — | 0 | 0 | 0 |
| piracicaba | et_penman_monteith | 366 | 366 | 2024-01-01 | 2024-12-31 | — | — | 0 | 0 | 0 |
| piracicaba | et_garcia_lopez | 366 | 366 | 2024-01-01 | 2024-12-31 | — | — | 0 | 0 | 39 |
| piracicaba | ra_extraterrestre_mj_m2_d | 366 | 366 | 2024-01-01 | 2024-12-31 | — | — | 0 | 0 | 0 |

## Method feasibility

Which methods can be computed from available inputs.

[Open HTML version](piracicaba_method_feasibility.html)

| method_name | status | required_columns | missing_columns | valid_day_fraction | reason |
| --- | --- | --- | --- | --- | --- |
| Thornthwaite | precomputed_only | spreadsheet column | — | 1.0000 | attached from input |
| Thornthwaite-Camargo | precomputed_only | spreadsheet column | — | 1.0000 | attached from input |
| Camargo | computable | tmed_c, ra_extraterrestre_mj_m2_d | — | 1.0000 | computed successfully in dry-run |
| Hargreaves-Samani | computable | tmin_c, tmax_c, tmed_c, ra_extraterrestre_mj_m2_d | — | 1.0000 | computed successfully in dry-run |
| Hargreaves-Samani corrected | precomputed_only | spreadsheet column | — | 1.0000 | attached from input |
| Priestley-Taylor | computable | tmed_c, rad_net_mj_m2_d | — | 1.0000 | computed successfully in dry-run |
| Penman-Monteith FAO-56 | computable | tmed_c, rad_net_mj_m2_d, wind_mean_ms | — | 1.0000 | computed successfully in dry-run |
| Garcia-Lopez | computable | tmed_c, rad_global_mj_m2_d, rh_mean_pct, wind_mean_ms | — | 1.0000 | computed successfully in dry-run |
| Makkink | computable | tmed_c, rad_global_mj_m2_d | — | 1.0000 | computed successfully in dry-run |
| McCloud | computable | tmed_c | — | 1.0000 | computed successfully in dry-run |
| Turc | computable | tmed_c, rad_global_mj_m2_d | — | 1.0000 | computed successfully in dry-run |
| Global Radiation | computable | rad_global_mj_m2_d | — | 1.0000 | computed successfully in dry-run |
| Ivanov | computable | tmed_c, rh_mean_pct | — | 1.0000 | computed successfully in dry-run |
| Jensen-Heise | computable | tmed_c, rad_global_mj_m2_d | — | 1.0000 | computed successfully in dry-run |
| Net Radiation | computable | rad_net_mj_m2_d | — | 1.0000 | computed successfully in dry-run |
| Radiation-Temperature | computable | tmed_c, rad_global_mj_m2_d | — | 1.0000 | computed successfully in dry-run |
| Lungeon | computable | tmed_c, rh_mean_pct | — | 1.0000 | computed successfully in dry-run |
| Stephens-Stewart | computable | tmed_c, rad_global_mj_m2_d | — | 1.0000 | computed successfully in dry-run |
| Hicks-Hess | computable | tmed_c, rad_global_mj_m2_d, wind_mean_ms | — | 1.0000 | computed successfully in dry-run |

## Method rankings

Composite rank within this site. Monthly scale is listed before daily.

### Piracicaba — monthly

Best overall: **Stephens Stewart** (composite rank).

| rank | method | rmse | mae | mbe | r | r2 | willmott_d | c | classification |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Stephens Stewart | 5.5159 | 4.3223 | -1.5531 | 0.9683 | 0.9377 | 0.9816 | 0.9505 | Excellent |
| 2 | Makkink | 5.1717 | 4.4327 | 0.3243 | 0.9657 | 0.9326 | 0.9818 | 0.9481 | Excellent |
| 3 | Radiation Temperature | 10.9880 | 9.7282 | -9.7282 | 0.9686 | 0.9381 | 0.9206 | 0.8916 | Excellent |
| 4 | Priestley Taylor | 11.6571 | 10.2603 | 3.4885 | 0.9142 | 0.8357 | 0.9327 | 0.8526 | Excellent |
| 5 | Hicks Hess | 16.7243 | 12.3605 | 10.1405 | 0.9369 | 0.8779 | 0.8884 | 0.8323 | Very Good |
| 6 | Net Radiation | 15.5411 | 13.0154 | 11.0675 | 0.9123 | 0.8323 | 0.8841 | 0.8066 | Very Good |
| 7 | Thornthwaite | 15.1841 | 11.6509 | 2.4172 | 0.8832 | 0.7800 | 0.8993 | 0.7942 | Very Good |
| 8 | Jensen Heise | 22.1735 | 19.4235 | 19.4235 | 0.9659 | 0.9330 | 0.8169 | 0.7890 | Very Good |
| 9 | Turc | 20.8024 | 20.4003 | 20.4003 | 0.9809 | 0.9621 | 0.7908 | 0.7757 | Very Good |
| 10 | Global Radiation | 23.1461 | 22.3804 | 22.3804 | 0.9550 | 0.9120 | 0.7382 | 0.7050 | Good |
| 11 | Hargreaves Samani | 39.2669 | 37.9986 | -37.9986 | 0.9641 | 0.9294 | 0.5272 | 0.5082 | Poor |
| 12 | Mccloud | 45.4405 | 42.2892 | 42.2892 | 0.8891 | 0.7905 | 0.5375 | 0.4779 | Bad |
| 13 | Hargreaves Samani Corr | 53.7460 | 52.8334 | 52.8334 | 0.9641 | 0.9294 | 0.4674 | 0.4506 | Bad |
| 14 | Camargo | 57.8432 | 56.7780 | -56.7780 | 0.9280 | 0.8612 | 0.4070 | 0.3777 | Very Poor |
| 15 | Garcia Lopez | 38.0570 | 33.6941 | -32.5982 | 0.6241 | 0.3895 | 0.5666 | 0.3536 | Very Poor |
| 16 | Lungeon | 82.3540 | 80.0178 | -80.0178 | 0.1937 | 0.0375 | 0.2785 | 0.0540 | Very Poor |
| 17 | Ivanov | 3705.7601 | 3564.7179 | 3564.7179 | 0.1616 | 0.0261 | 0.0087 | 0.0014 | Very Poor |
| 18 | Thornthwaite Camargo | 98.4131 | 96.3929 | -96.3929 | — | — | 0.2427 | — | — |

### Piracicaba — daily

Best overall: **Stephens Stewart** (composite rank).

| rank | method | rmse | mae | mbe | r | r2 | willmott_d | c | classification |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Stephens Stewart | 0.3825 | 0.2466 | -0.0509 | 0.9571 | 0.9160 | 0.9769 | 0.9350 | Excellent |
| 2 | Priestley Taylor | 0.4982 | 0.3934 | 0.1144 | 0.9509 | 0.9042 | 0.9682 | 0.9206 | Excellent |
| 3 | Makkink | 0.4200 | 0.2913 | 0.0106 | 0.9482 | 0.8991 | 0.9708 | 0.9206 | Excellent |
| 4 | Radiation Temperature | 0.5295 | 0.4024 | -0.3190 | 0.9557 | 0.9134 | 0.9511 | 0.9090 | Excellent |
| 5 | Net Radiation | 0.6440 | 0.5298 | 0.3629 | 0.9442 | 0.8915 | 0.9487 | 0.8958 | Excellent |
| 6 | Jensen Heise | 0.8315 | 0.6996 | 0.6368 | 0.9539 | 0.9100 | 0.9213 | 0.8789 | Excellent |
| 7 | Turc | 0.7670 | 0.7030 | 0.6689 | 0.9579 | 0.9176 | 0.9163 | 0.8777 | Excellent |
| 8 | Global Radiation | 0.8860 | 0.7917 | 0.7338 | 0.9276 | 0.8604 | 0.8923 | 0.8276 | Very Good |
| 9 | Hicks Hess | 0.7885 | 0.5311 | 0.3325 | 0.8936 | 0.7985 | 0.9229 | 0.8247 | Very Good |
| 10 | Garcia Lopez | 1.4046 | 1.1946 | -1.0688 | 0.7846 | 0.6156 | 0.7739 | 0.6072 | Average |
| 11 | Hargreaves Samani Corr | 1.8777 | 1.7409 | 1.7322 | 0.8392 | 0.7043 | 0.6547 | 0.5494 | Poor |
| 12 | Hargreaves Samani | 1.5587 | 1.3440 | -1.2459 | 0.8392 | 0.7043 | 0.6087 | 0.5108 | Poor |
| 13 | Mccloud | 1.8848 | 1.5002 | 1.3865 | 0.6776 | 0.4592 | 0.6632 | 0.4494 | Bad |
| 14 | Camargo | 2.1678 | 1.9410 | -1.8616 | 0.6382 | 0.4073 | 0.4905 | 0.3130 | Very Poor |
| 15 | Thornthwaite | 1.2325 | 0.9596 | 0.0793 | 0.4486 | 0.2013 | 0.6655 | 0.2986 | Very Poor |
| 16 | Lungeon | 2.8668 | 2.6243 | -2.6235 | 0.6175 | 0.3813 | 0.4277 | 0.2641 | Very Poor |
| 17 | Ivanov | 131.4282 | 116.8765 | 116.8760 | 0.6087 | 0.3705 | 0.0189 | 0.0115 | Very Poor |
| 18 | Thornthwaite Camargo | 3.4196 | 3.1605 | -3.1604 | — | — | 0.3670 | — | — |


## Monthly metrics

Error and agreement metrics versus Penman–Monteith.

| method | rmse | mae | mbe | r | r2 | willmott_d | c | classification |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Stephens Stewart | 5.5159 | 4.3223 | -1.5531 | 0.9683 | 0.9377 | 0.9816 | 0.9505 | Excellent |
| Makkink | 5.1717 | 4.4327 | 0.3243 | 0.9657 | 0.9326 | 0.9818 | 0.9481 | Excellent |
| Radiation Temperature | 10.9880 | 9.7282 | -9.7282 | 0.9686 | 0.9381 | 0.9206 | 0.8916 | Excellent |
| Priestley Taylor | 11.6571 | 10.2603 | 3.4885 | 0.9142 | 0.8357 | 0.9327 | 0.8526 | Excellent |
| Hicks Hess | 16.7243 | 12.3605 | 10.1405 | 0.9369 | 0.8779 | 0.8884 | 0.8323 | Very Good |
| Net Radiation | 15.5411 | 13.0154 | 11.0675 | 0.9123 | 0.8323 | 0.8841 | 0.8066 | Very Good |
| Thornthwaite | 15.1841 | 11.6509 | 2.4172 | 0.8832 | 0.7800 | 0.8993 | 0.7942 | Very Good |
| Jensen Heise | 22.1735 | 19.4235 | 19.4235 | 0.9659 | 0.9330 | 0.8169 | 0.7890 | Very Good |
| Turc | 20.8024 | 20.4003 | 20.4003 | 0.9809 | 0.9621 | 0.7908 | 0.7757 | Very Good |
| Global Radiation | 23.1461 | 22.3804 | 22.3804 | 0.9550 | 0.9120 | 0.7382 | 0.7050 | Good |
| Hargreaves Samani | 39.2669 | 37.9986 | -37.9986 | 0.9641 | 0.9294 | 0.5272 | 0.5082 | Poor |
| Mccloud | 45.4405 | 42.2892 | 42.2892 | 0.8891 | 0.7905 | 0.5375 | 0.4779 | Bad |
| Hargreaves Samani Corr | 53.7460 | 52.8334 | 52.8334 | 0.9641 | 0.9294 | 0.4674 | 0.4506 | Bad |
| Camargo | 57.8432 | 56.7780 | -56.7780 | 0.9280 | 0.8612 | 0.4070 | 0.3777 | Very Poor |
| Garcia Lopez | 38.0570 | 33.6941 | -32.5982 | 0.6241 | 0.3895 | 0.5666 | 0.3536 | Very Poor |
| Lungeon | 82.3540 | 80.0178 | -80.0178 | 0.1937 | 0.0375 | 0.2785 | 0.0540 | Very Poor |
| Ivanov | 3705.7601 | 3564.7179 | 3564.7179 | 0.1616 | 0.0261 | 0.0087 | 0.0014 | Very Poor |
| Thornthwaite Camargo | 98.4131 | 96.3929 | -96.3929 | — | — | 0.2427 | — | — |

## Daily metrics

Error and agreement metrics versus Penman–Monteith.

| method | rmse | mae | mbe | r | r2 | willmott_d | c | classification |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Stephens Stewart | 0.3825 | 0.2466 | -0.0509 | 0.9571 | 0.9160 | 0.9769 | 0.9350 | Excellent |
| Priestley Taylor | 0.4982 | 0.3934 | 0.1144 | 0.9509 | 0.9042 | 0.9682 | 0.9206 | Excellent |
| Makkink | 0.4200 | 0.2913 | 0.0106 | 0.9482 | 0.8991 | 0.9708 | 0.9206 | Excellent |
| Radiation Temperature | 0.5295 | 0.4024 | -0.3190 | 0.9557 | 0.9134 | 0.9511 | 0.9090 | Excellent |
| Net Radiation | 0.6440 | 0.5298 | 0.3629 | 0.9442 | 0.8915 | 0.9487 | 0.8958 | Excellent |
| Jensen Heise | 0.8315 | 0.6996 | 0.6368 | 0.9539 | 0.9100 | 0.9213 | 0.8789 | Excellent |
| Turc | 0.7670 | 0.7030 | 0.6689 | 0.9579 | 0.9176 | 0.9163 | 0.8777 | Excellent |
| Global Radiation | 0.8860 | 0.7917 | 0.7338 | 0.9276 | 0.8604 | 0.8923 | 0.8276 | Very Good |
| Hicks Hess | 0.7885 | 0.5311 | 0.3325 | 0.8936 | 0.7985 | 0.9229 | 0.8247 | Very Good |
| Garcia Lopez | 1.4046 | 1.1946 | -1.0688 | 0.7846 | 0.6156 | 0.7739 | 0.6072 | Average |
| Hargreaves Samani Corr | 1.8777 | 1.7409 | 1.7322 | 0.8392 | 0.7043 | 0.6547 | 0.5494 | Poor |
| Hargreaves Samani | 1.5587 | 1.3440 | -1.2459 | 0.8392 | 0.7043 | 0.6087 | 0.5108 | Poor |
| Mccloud | 1.8848 | 1.5002 | 1.3865 | 0.6776 | 0.4592 | 0.6632 | 0.4494 | Bad |
| Camargo | 2.1678 | 1.9410 | -1.8616 | 0.6382 | 0.4073 | 0.4905 | 0.3130 | Very Poor |
| Thornthwaite | 1.2325 | 0.9596 | 0.0793 | 0.4486 | 0.2013 | 0.6655 | 0.2986 | Very Poor |
| Lungeon | 2.8668 | 2.6243 | -2.6235 | 0.6175 | 0.3813 | 0.4277 | 0.2641 | Very Poor |
| Ivanov | 131.4282 | 116.8765 | 116.8760 | 0.6087 | 0.3705 | 0.0189 | 0.0115 | Very Poor |
| Thornthwaite Camargo | 3.4196 | 3.1605 | -3.1604 | — | — | 0.3670 | — | — |

## Uncertainty and sensitivity

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
| month | 2024-01 | et_mccloud | 31 | 136.6800 | 1.8071 | 1.5104 | 1.4906 |
| month | 2024-01 | et_turc | 31 | 136.6800 | 0.8052 | 0.7635 | 0.7635 |
| month | 2024-01 | et_global_radiation | 31 | 136.6800 | 0.8916 | 0.8429 | 0.8429 |
| month | 2024-01 | et_ivanov | 31 | 136.6800 | 119.0876 | 110.9760 | 110.9760 |
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


## Figures

- [Full figures gallery (HTML)](../figures/piracicaba/index.html)
- [daily_taylor](../figures/piracicaba/piracicaba_daily_taylor.png)
- [monthly_taylor](../figures/piracicaba/piracicaba_monthly_taylor.png)
- [monthly_totals](../figures/piracicaba/piracicaba_monthly_totals.png)
- [bias_by_eto_bin](../figures/piracicaba/piracicaba_bias_by_eto_bin.png)
- [daily_scatter_camargo_vs_pm](../figures/piracicaba/piracicaba_daily_scatter_camargo_vs_pm.png)
- [daily_scatter_gl_vs_pm](../figures/piracicaba/piracicaba_daily_scatter_gl_vs_pm.png)
- [daily_scatter_global_rad_vs_pm](../figures/piracicaba/piracicaba_daily_scatter_global_rad_vs_pm.png)
- [daily_scatter_hh_vs_pm](../figures/piracicaba/piracicaba_daily_scatter_hh_vs_pm.png)
- [daily_scatter_hs_corr_vs_pm](../figures/piracicaba/piracicaba_daily_scatter_hs_corr_vs_pm.png)
- [daily_scatter_hs_vs_pm](../figures/piracicaba/piracicaba_daily_scatter_hs_vs_pm.png)
- [daily_scatter_ivanov_vs_pm](../figures/piracicaba/piracicaba_daily_scatter_ivanov_vs_pm.png)
- [daily_scatter_jh_vs_pm](../figures/piracicaba/piracicaba_daily_scatter_jh_vs_pm.png)

---

Generated by the ET₀ methods comparison pipeline.
