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
| piracicaba | T_med | 366 | 366 | 2024-01-01 | 2024-12-31 | — | — | 354 | 354 | 0 |
| piracicaba | I | 366 | 366 | 2024-01-01 | 2024-12-31 | — | — | 354 | 354 | 0 |
| piracicaba | I_Anual | 366 | 366 | 2024-01-01 | 2024-12-31 | — | — | 365 | 365 | 0 |
| piracicaba | a | 366 | 366 | 2024-01-01 | 2024-12-31 | — | — | 365 | 365 | 0 |
| piracicaba | et | 366 | 366 | 2024-01-01 | 2024-12-31 | — | — | 353 | 353 | 0 |
| piracicaba | T | 366 | 366 | 2024-01-01 | 2024-12-31 | — | — | 0 | 0 | 0 |
| piracicaba | UR | 366 | 366 | 2024-01-01 | 2024-12-31 | — | — | 0 | 0 | 0 |
| piracicaba | es_max | 366 | 366 | 2024-01-01 | 2024-12-31 | — | — | 0 | 0 | 0 |
| piracicaba | es_min | 366 | 366 | 2024-01-01 | 2024-12-31 | — | — | 0 | 0 | 0 |
| piracicaba | es | 366 | 366 | 2024-01-01 | 2024-12-31 | — | — | 0 | 0 | 0 |
| piracicaba | s | 366 | 366 | 2024-01-01 | 2024-12-31 | — | — | 0 | 0 | 0 |

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

Best overall: **Makkink** (composite rank).

| rank | method | rmse | mae | mbe | r | r2 | willmott_d | c | classification |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Makkink | 8.5015 | 5.8852 | -4.7418 | 0.9374 | 0.8788 | 0.9518 | 0.8923 | Excellent |
| 2 | Stephens Stewart | 9.8682 | 6.9649 | -6.6192 | 0.9381 | 0.8800 | 0.9427 | 0.8843 | Excellent |
| 3 | Turc | 16.3449 | 15.3342 | 15.3342 | 0.9622 | 0.9258 | 0.8591 | 0.8266 | Very Good |
| 4 | Jensen Heise | 18.7174 | 15.5843 | 14.3574 | 0.9346 | 0.8736 | 0.8611 | 0.8048 | Very Good |
| 5 | Radiation Temperature | 16.3891 | 14.7943 | -14.7943 | 0.9391 | 0.8820 | 0.8458 | 0.7943 | Very Good |
| 6 | Priestley Taylor | 13.4000 | 11.8551 | -1.5776 | 0.8603 | 0.7401 | 0.9116 | 0.7842 | Very Good |
| 7 | Net Radiation | 14.4216 | 12.4665 | 6.0014 | 0.8583 | 0.7367 | 0.8953 | 0.7685 | Very Good |
| 8 | Global Radiation | 18.8716 | 17.5325 | 17.3142 | 0.9293 | 0.8636 | 0.8062 | 0.7492 | Good |
| 9 | Hicks Hess | 30.5628 | 23.7490 | 23.7490 | 0.9343 | 0.8729 | 0.7493 | 0.7001 | Good |
| 10 | Hargreaves Samani | 44.2709 | 43.0648 | -43.0648 | 0.9660 | 0.9331 | 0.4908 | 0.4741 | Bad |
| 11 | Garcia Lopez | 33.7056 | 29.5440 | -26.3328 | 0.7100 | 0.5040 | 0.6535 | 0.4639 | Bad |
| 12 | Camargo | 63.0266 | 61.8441 | -61.8441 | 0.8877 | 0.7881 | 0.3822 | 0.3393 | Very Poor |
| 13 | Lungeon | 87.2594 | 85.0839 | -85.0839 | 0.3046 | 0.0928 | 0.2681 | 0.0817 | Very Poor |
| 14 | Mccloud | 2160.4530 | 2134.1598 | 2134.1598 | 0.8671 | 0.7519 | 0.0162 | 0.0141 | Very Poor |
| 15 | Ivanov | 3700.2472 | 3559.6517 | 3559.6517 | 0.2737 | 0.0749 | 0.0093 | 0.0025 | Very Poor |

### Piracicaba — daily

Best overall: **Stephens Stewart** (composite rank).

| rank | method | rmse | mae | mbe | r | r2 | willmott_d | c | classification |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Stephens Stewart | 0.4975 | 0.3442 | -0.2170 | 0.9451 | 0.8933 | 0.9628 | 0.9100 | Excellent |
| 2 | Makkink | 0.5147 | 0.3556 | -0.1555 | 0.9354 | 0.8749 | 0.9581 | 0.8962 | Excellent |
| 3 | Turc | 0.6576 | 0.5699 | 0.5028 | 0.9503 | 0.9030 | 0.9388 | 0.8921 | Excellent |
| 4 | Jensen Heise | 0.7319 | 0.5982 | 0.4707 | 0.9425 | 0.8884 | 0.9395 | 0.8855 | Excellent |
| 5 | Priestley Taylor | 0.5813 | 0.4405 | -0.0517 | 0.9238 | 0.8535 | 0.9579 | 0.8849 | Excellent |
| 6 | Radiation Temperature | 0.6948 | 0.5499 | -0.4851 | 0.9434 | 0.8901 | 0.9216 | 0.8695 | Excellent |
| 7 | Net Radiation | 0.6526 | 0.5123 | 0.1968 | 0.9162 | 0.8394 | 0.9482 | 0.8687 | Excellent |
| 8 | Global Radiation | 0.7929 | 0.6827 | 0.5677 | 0.9144 | 0.8361 | 0.9132 | 0.8350 | Very Good |
| 9 | Hicks Hess | 1.2431 | 0.8752 | 0.7787 | 0.8797 | 0.7739 | 0.8577 | 0.7545 | Very Good |
| 10 | Garcia Lopez | 1.3238 | 1.1169 | -0.8634 | 0.8167 | 0.6670 | 0.8264 | 0.6749 | Good |
| 11 | Hargreaves Samani | 1.7225 | 1.4991 | -1.4120 | 0.8415 | 0.7082 | 0.5918 | 0.4980 | Bad |
| 12 | Camargo | 2.3417 | 2.0996 | -2.0277 | 0.6176 | 0.3814 | 0.4802 | 0.2966 | Very Poor |
| 13 | Lungeon | 3.0336 | 2.7899 | -2.7896 | 0.6696 | 0.4483 | 0.4243 | 0.2841 | Very Poor |
| 14 | Mccloud | 71.9653 | 69.9725 | 69.9725 | 0.7020 | 0.4927 | 0.0354 | 0.0248 | Very Poor |
| 15 | Ivanov | 131.2327 | 116.7104 | 116.7099 | 0.6614 | 0.4374 | 0.0205 | 0.0135 | Very Poor |


## Monthly metrics

Error and agreement metrics versus Penman–Monteith.

| method | rmse | mae | mbe | r | r2 | willmott_d | c | classification |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Makkink | 8.5015 | 5.8852 | -4.7418 | 0.9374 | 0.8788 | 0.9518 | 0.8923 | Excellent |
| Stephens Stewart | 9.8682 | 6.9649 | -6.6192 | 0.9381 | 0.8800 | 0.9427 | 0.8843 | Excellent |
| Turc | 16.3449 | 15.3342 | 15.3342 | 0.9622 | 0.9258 | 0.8591 | 0.8266 | Very Good |
| Jensen Heise | 18.7174 | 15.5843 | 14.3574 | 0.9346 | 0.8736 | 0.8611 | 0.8048 | Very Good |
| Radiation Temperature | 16.3891 | 14.7943 | -14.7943 | 0.9391 | 0.8820 | 0.8458 | 0.7943 | Very Good |
| Priestley Taylor | 13.4000 | 11.8551 | -1.5776 | 0.8603 | 0.7401 | 0.9116 | 0.7842 | Very Good |
| Net Radiation | 14.4216 | 12.4665 | 6.0014 | 0.8583 | 0.7367 | 0.8953 | 0.7685 | Very Good |
| Global Radiation | 18.8716 | 17.5325 | 17.3142 | 0.9293 | 0.8636 | 0.8062 | 0.7492 | Good |
| Hicks Hess | 30.5628 | 23.7490 | 23.7490 | 0.9343 | 0.8729 | 0.7493 | 0.7001 | Good |
| Hargreaves Samani | 44.2709 | 43.0648 | -43.0648 | 0.9660 | 0.9331 | 0.4908 | 0.4741 | Bad |
| Garcia Lopez | 33.7056 | 29.5440 | -26.3328 | 0.7100 | 0.5040 | 0.6535 | 0.4639 | Bad |
| Camargo | 63.0266 | 61.8441 | -61.8441 | 0.8877 | 0.7881 | 0.3822 | 0.3393 | Very Poor |
| Lungeon | 87.2594 | 85.0839 | -85.0839 | 0.3046 | 0.0928 | 0.2681 | 0.0817 | Very Poor |
| Mccloud | 2160.4530 | 2134.1598 | 2134.1598 | 0.8671 | 0.7519 | 0.0162 | 0.0141 | Very Poor |
| Ivanov | 3700.2472 | 3559.6517 | 3559.6517 | 0.2737 | 0.0749 | 0.0093 | 0.0025 | Very Poor |

## Daily metrics

Error and agreement metrics versus Penman–Monteith.

| method | rmse | mae | mbe | r | r2 | willmott_d | c | classification |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Stephens Stewart | 0.4975 | 0.3442 | -0.2170 | 0.9451 | 0.8933 | 0.9628 | 0.9100 | Excellent |
| Makkink | 0.5147 | 0.3556 | -0.1555 | 0.9354 | 0.8749 | 0.9581 | 0.8962 | Excellent |
| Turc | 0.6576 | 0.5699 | 0.5028 | 0.9503 | 0.9030 | 0.9388 | 0.8921 | Excellent |
| Jensen Heise | 0.7319 | 0.5982 | 0.4707 | 0.9425 | 0.8884 | 0.9395 | 0.8855 | Excellent |
| Priestley Taylor | 0.5813 | 0.4405 | -0.0517 | 0.9238 | 0.8535 | 0.9579 | 0.8849 | Excellent |
| Radiation Temperature | 0.6948 | 0.5499 | -0.4851 | 0.9434 | 0.8901 | 0.9216 | 0.8695 | Excellent |
| Net Radiation | 0.6526 | 0.5123 | 0.1968 | 0.9162 | 0.8394 | 0.9482 | 0.8687 | Excellent |
| Global Radiation | 0.7929 | 0.6827 | 0.5677 | 0.9144 | 0.8361 | 0.9132 | 0.8350 | Very Good |
| Hicks Hess | 1.2431 | 0.8752 | 0.7787 | 0.8797 | 0.7739 | 0.8577 | 0.7545 | Very Good |
| Garcia Lopez | 1.3238 | 1.1169 | -0.8634 | 0.8167 | 0.6670 | 0.8264 | 0.6749 | Good |
| Hargreaves Samani | 1.7225 | 1.4991 | -1.4120 | 0.8415 | 0.7082 | 0.5918 | 0.4980 | Bad |
| Camargo | 2.3417 | 2.0996 | -2.0277 | 0.6176 | 0.3814 | 0.4802 | 0.2966 | Very Poor |
| Lungeon | 3.0336 | 2.7899 | -2.7896 | 0.6696 | 0.4483 | 0.4243 | 0.2841 | Very Poor |
| Mccloud | 71.9653 | 69.9725 | 69.9725 | 0.7020 | 0.4927 | 0.0354 | 0.0248 | Very Poor |
| Ivanov | 131.2327 | 116.7104 | 116.7099 | 0.6614 | 0.4374 | 0.0205 | 0.0135 | Very Poor |

## Uncertainty and sensitivity

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
