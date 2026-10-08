# ET₀ site report — Manaus

Amazonia · Af · AM · Brazil

[← Results index](../index.md)

## Site metadata

- **Latitude**: -3.1019
- **Longitude**: -60.0164
- **Altitude (m)**: 61.25
- **Biome**: Amazonia
- **Climate**: Af
- **Region**: North
- **Country**: Brazil
- **State**: AM

## Data quality

Coverage and QC flags by input variable.

| site | variable | row_count | expected_days | start_date | end_date | missing_dates | duplicate_dates | missing_values | interpolated_values | physical_limit_violations |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| manaus | tmed_c | 366 | 366 | 2024-01-01 | 2024-12-31 | — | — | 0 | 0 | 0 |
| manaus | rh_mean_pct | 366 | 366 | 2024-01-01 | 2024-12-31 | — | — | 0 | 0 | 0 |
| manaus | wind_mean_ms | 366 | 366 | 2024-01-01 | 2024-12-31 | — | — | 0 | 0 | 0 |
| manaus | tmax_c | 366 | 366 | 2024-01-01 | 2024-12-31 | — | — | 0 | 0 | 0 |
| manaus | rh_max_pct | 366 | 366 | 2024-01-01 | 2024-12-31 | — | — | 0 | 0 | 0 |
| manaus | wind_max_ms | 366 | 366 | 2024-01-01 | 2024-12-31 | — | — | 0 | 0 | 0 |
| manaus | tmin_c | 366 | 366 | 2024-01-01 | 2024-12-31 | — | — | 0 | 0 | 0 |
| manaus | rh_min_pct | 366 | 366 | 2024-01-01 | 2024-12-31 | — | — | 0 | 0 | 0 |
| manaus | rain_mm | 366 | 366 | 2024-01-01 | 2024-12-31 | — | — | 1 | 1 | 0 |
| manaus | rad_global_mj_m2_d | 366 | 366 | 2024-01-01 | 2024-12-31 | — | — | 0 | 0 | 0 |
| manaus | rad_net_mj_m2_d | 366 | 366 | 2024-01-01 | 2024-12-31 | — | — | 0 | 0 | 0 |
| manaus | et_thornthwaite | 366 | 366 | 2024-01-01 | 2024-12-31 | — | — | 0 | 0 | 0 |
| manaus | et_thornthwaite_camargo | 366 | 366 | 2024-01-01 | 2024-12-31 | — | — | 0 | 0 | 0 |
| manaus | et_camargo | 366 | 366 | 2024-01-01 | 2024-12-31 | — | — | 0 | 0 | 0 |
| manaus | et_hargreaves_samani | 366 | 366 | 2024-01-01 | 2024-12-31 | — | — | 0 | 0 | 0 |
| manaus | et_hargreaves_samani_corr | 366 | 366 | 2024-01-01 | 2024-12-31 | — | — | 0 | 0 | 0 |
| manaus | et_priestley_taylor | 366 | 366 | 2024-01-01 | 2024-12-31 | — | — | 0 | 0 | 0 |
| manaus | et_penman_monteith | 366 | 366 | 2024-01-01 | 2024-12-31 | — | — | 0 | 0 | 0 |
| manaus | et_garcia_lopez | 366 | 366 | 2024-01-01 | 2024-12-31 | — | — | 0 | 0 | 366 |
| manaus | ra_extraterrestre_mj_m2_d | 366 | 366 | 2024-01-01 | 2024-12-31 | — | — | 0 | 0 | 0 |

## Method feasibility

Which methods can be computed from available inputs.

[Open HTML version](manaus_method_feasibility.html)

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

### Manaus — monthly

Best overall: **Lungeon** (composite rank).

| rank | method | rmse | mae | mbe | r | r2 | willmott_d | c | classification |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Lungeon | 11.6004 | 10.8453 | -10.8453 | 0.9768 | 0.9542 | 0.7046 | 0.6883 | Good |
| 2 | Turc | 17.1076 | 13.7775 | -13.7775 | 0.7590 | 0.5761 | 0.4654 | 0.3532 | Very Poor |
| 3 | Hargreaves Samani | 33.3339 | 32.7595 | 32.7595 | 0.9025 | 0.8145 | 0.3913 | 0.3531 | Very Poor |
| 4 | Garcia Lopez | 29.7984 | 28.1513 | -28.1513 | 0.9554 | 0.9127 | 0.3664 | 0.3501 | Very Poor |
| 5 | Camargo | 30.8472 | 29.6838 | 29.6838 | 0.8777 | 0.7704 | 0.3851 | 0.3380 | Very Poor |
| 6 | Jensen Heise | 27.6341 | 25.7432 | -25.7432 | 0.7477 | 0.5591 | 0.3806 | 0.2846 | Very Poor |
| 7 | Hicks Hess | 28.3723 | 26.5155 | -26.5155 | 0.7555 | 0.5708 | 0.3744 | 0.2829 | Very Poor |
| 8 | Hargreaves Samani Corr | 47.3360 | 47.0262 | 47.0262 | 0.9025 | 0.8145 | 0.3079 | 0.2779 | Very Poor |
| 9 | Stephens Stewart | 28.6835 | 26.7926 | -26.7926 | 0.7254 | 0.5262 | 0.3704 | 0.2687 | Very Poor |
| 10 | Radiation Temperature | 29.1246 | 27.2316 | -27.2316 | 0.7069 | 0.4997 | 0.3662 | 0.2589 | Very Poor |
| 11 | Priestley Taylor | 29.0864 | 27.1769 | -27.1769 | 0.6696 | 0.4483 | 0.3661 | 0.2452 | Very Poor |
| 12 | Global Radiation | 28.5679 | 26.6278 | -26.6278 | 0.6285 | 0.3950 | 0.3702 | 0.2327 | Very Poor |
| 13 | Net Radiation | 29.0409 | 27.1149 | -27.1149 | 0.6285 | 0.3950 | 0.3661 | 0.2301 | Very Poor |
| 14 | Makkink | 32.3695 | 30.6728 | -30.6728 | 0.6607 | 0.4365 | 0.3447 | 0.2278 | Very Poor |
| 15 | Ivanov | 118.2675 | 111.1566 | 111.1566 | 0.9765 | 0.9536 | 0.1919 | 0.1874 | Very Poor |
| 16 | Thornthwaite | 127.4527 | 127.3784 | 127.3784 | 0.9174 | 0.8416 | 0.1325 | 0.1215 | Very Poor |
| 17 | Mccloud | 3282.4615 | 3272.4421 | 3272.4421 | 0.9406 | 0.8847 | 0.0060 | 0.0056 | Very Poor |
| 18 | Thornthwaite Camargo | 123.6738 | 123.1483 | 123.1483 | -0.0517 | 0.0027 | 0.1249 | -0.0065 | Very Poor |

### Manaus — daily

Best overall: **Lungeon** (composite rank).

| rank | method | rmse | mae | mbe | r | r2 | willmott_d | c | classification |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Lungeon | 0.4632 | 0.3603 | -0.3556 | 0.9138 | 0.8350 | 0.7583 | 0.6929 | Good |
| 2 | Garcia Lopez | 1.0496 | 0.9230 | -0.9230 | 0.9508 | 0.9041 | 0.4284 | 0.4073 | Bad |
| 3 | Camargo | 1.0691 | 0.9969 | 0.9732 | 0.8756 | 0.7667 | 0.4606 | 0.4033 | Bad |
| 4 | Turc | 0.6840 | 0.5013 | -0.4517 | 0.7759 | 0.6021 | 0.4752 | 0.3687 | Very Poor |
| 5 | Hicks Hess | 1.0051 | 0.8694 | -0.8694 | 0.8337 | 0.6951 | 0.4372 | 0.3645 | Very Poor |
| 6 | Jensen Heise | 0.9849 | 0.8440 | -0.8440 | 0.7589 | 0.5760 | 0.4407 | 0.3344 | Very Poor |
| 7 | Stephens Stewart | 1.0203 | 0.8784 | -0.8784 | 0.7431 | 0.5521 | 0.4290 | 0.3188 | Very Poor |
| 8 | Radiation Temperature | 1.0352 | 0.8928 | -0.8928 | 0.7301 | 0.5331 | 0.4242 | 0.3097 | Very Poor |
| 9 | Hargreaves Samani | 1.1537 | 1.0857 | 1.0741 | 0.6514 | 0.4244 | 0.4601 | 0.2997 | Very Poor |
| 10 | Priestley Taylor | 1.0344 | 0.8910 | -0.8910 | 0.7043 | 0.4961 | 0.4239 | 0.2985 | Very Poor |
| 11 | Global Radiation | 1.0178 | 0.8730 | -0.8730 | 0.6772 | 0.4586 | 0.4280 | 0.2898 | Very Poor |
| 12 | Makkink | 1.1340 | 1.0057 | -1.0057 | 0.7043 | 0.4961 | 0.4080 | 0.2874 | Very Poor |
| 13 | Net Radiation | 1.0333 | 0.8890 | -0.8890 | 0.6772 | 0.4586 | 0.4236 | 0.2868 | Very Poor |
| 14 | Hargreaves Samani Corr | 1.5976 | 1.5418 | 1.5418 | 0.6514 | 0.4244 | 0.3827 | 0.2493 | Very Poor |
| 15 | Ivanov | 4.0295 | 3.6445 | 3.6445 | 0.9136 | 0.8346 | 0.2649 | 0.2420 | Very Poor |
| 16 | Thornthwaite | 4.1902 | 4.1763 | 4.1763 | 0.7883 | 0.6214 | 0.1849 | 0.1458 | Very Poor |
| 17 | Mccloud | 107.9981 | 107.2932 | 107.2932 | 0.8794 | 0.7734 | 0.0090 | 0.0079 | Very Poor |
| 18 | Thornthwaite Camargo | 4.0750 | 4.0376 | 4.0376 | 0.0000 | 0.0000 | 0.1717 | 0.0000 | Very Poor |


## Monthly metrics

Error and agreement metrics versus Penman–Monteith.

| method | rmse | mae | mbe | r | r2 | willmott_d | c | classification |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Lungeon | 11.6004 | 10.8453 | -10.8453 | 0.9768 | 0.9542 | 0.7046 | 0.6883 | Good |
| Turc | 17.1076 | 13.7775 | -13.7775 | 0.7590 | 0.5761 | 0.4654 | 0.3532 | Very Poor |
| Hargreaves Samani | 33.3339 | 32.7595 | 32.7595 | 0.9025 | 0.8145 | 0.3913 | 0.3531 | Very Poor |
| Garcia Lopez | 29.7984 | 28.1513 | -28.1513 | 0.9554 | 0.9127 | 0.3664 | 0.3501 | Very Poor |
| Camargo | 30.8472 | 29.6838 | 29.6838 | 0.8777 | 0.7704 | 0.3851 | 0.3380 | Very Poor |
| Jensen Heise | 27.6341 | 25.7432 | -25.7432 | 0.7477 | 0.5591 | 0.3806 | 0.2846 | Very Poor |
| Hicks Hess | 28.3723 | 26.5155 | -26.5155 | 0.7555 | 0.5708 | 0.3744 | 0.2829 | Very Poor |
| Hargreaves Samani Corr | 47.3360 | 47.0262 | 47.0262 | 0.9025 | 0.8145 | 0.3079 | 0.2779 | Very Poor |
| Stephens Stewart | 28.6835 | 26.7926 | -26.7926 | 0.7254 | 0.5262 | 0.3704 | 0.2687 | Very Poor |
| Radiation Temperature | 29.1246 | 27.2316 | -27.2316 | 0.7069 | 0.4997 | 0.3662 | 0.2589 | Very Poor |
| Priestley Taylor | 29.0864 | 27.1769 | -27.1769 | 0.6696 | 0.4483 | 0.3661 | 0.2452 | Very Poor |
| Global Radiation | 28.5679 | 26.6278 | -26.6278 | 0.6285 | 0.3950 | 0.3702 | 0.2327 | Very Poor |
| Net Radiation | 29.0409 | 27.1149 | -27.1149 | 0.6285 | 0.3950 | 0.3661 | 0.2301 | Very Poor |
| Makkink | 32.3695 | 30.6728 | -30.6728 | 0.6607 | 0.4365 | 0.3447 | 0.2278 | Very Poor |
| Ivanov | 118.2675 | 111.1566 | 111.1566 | 0.9765 | 0.9536 | 0.1919 | 0.1874 | Very Poor |
| Thornthwaite | 127.4527 | 127.3784 | 127.3784 | 0.9174 | 0.8416 | 0.1325 | 0.1215 | Very Poor |
| Mccloud | 3282.4615 | 3272.4421 | 3272.4421 | 0.9406 | 0.8847 | 0.0060 | 0.0056 | Very Poor |
| Thornthwaite Camargo | 123.6738 | 123.1483 | 123.1483 | -0.0517 | 0.0027 | 0.1249 | -0.0065 | Very Poor |

## Daily metrics

Error and agreement metrics versus Penman–Monteith.

| method | rmse | mae | mbe | r | r2 | willmott_d | c | classification |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Lungeon | 0.4632 | 0.3603 | -0.3556 | 0.9138 | 0.8350 | 0.7583 | 0.6929 | Good |
| Garcia Lopez | 1.0496 | 0.9230 | -0.9230 | 0.9508 | 0.9041 | 0.4284 | 0.4073 | Bad |
| Camargo | 1.0691 | 0.9969 | 0.9732 | 0.8756 | 0.7667 | 0.4606 | 0.4033 | Bad |
| Turc | 0.6840 | 0.5013 | -0.4517 | 0.7759 | 0.6021 | 0.4752 | 0.3687 | Very Poor |
| Hicks Hess | 1.0051 | 0.8694 | -0.8694 | 0.8337 | 0.6951 | 0.4372 | 0.3645 | Very Poor |
| Jensen Heise | 0.9849 | 0.8440 | -0.8440 | 0.7589 | 0.5760 | 0.4407 | 0.3344 | Very Poor |
| Stephens Stewart | 1.0203 | 0.8784 | -0.8784 | 0.7431 | 0.5521 | 0.4290 | 0.3188 | Very Poor |
| Radiation Temperature | 1.0352 | 0.8928 | -0.8928 | 0.7301 | 0.5331 | 0.4242 | 0.3097 | Very Poor |
| Hargreaves Samani | 1.1537 | 1.0857 | 1.0741 | 0.6514 | 0.4244 | 0.4601 | 0.2997 | Very Poor |
| Priestley Taylor | 1.0344 | 0.8910 | -0.8910 | 0.7043 | 0.4961 | 0.4239 | 0.2985 | Very Poor |
| Global Radiation | 1.0178 | 0.8730 | -0.8730 | 0.6772 | 0.4586 | 0.4280 | 0.2898 | Very Poor |
| Makkink | 1.1340 | 1.0057 | -1.0057 | 0.7043 | 0.4961 | 0.4080 | 0.2874 | Very Poor |
| Net Radiation | 1.0333 | 0.8890 | -0.8890 | 0.6772 | 0.4586 | 0.4236 | 0.2868 | Very Poor |
| Hargreaves Samani Corr | 1.5976 | 1.5418 | 1.5418 | 0.6514 | 0.4244 | 0.3827 | 0.2493 | Very Poor |
| Ivanov | 4.0295 | 3.6445 | 3.6445 | 0.9136 | 0.8346 | 0.2649 | 0.2420 | Very Poor |
| Thornthwaite | 4.1902 | 4.1763 | 4.1763 | 0.7883 | 0.6214 | 0.1849 | 0.1458 | Very Poor |
| Mccloud | 107.9981 | 107.2932 | 107.2932 | 0.8794 | 0.7734 | 0.0090 | 0.0079 | Very Poor |
| Thornthwaite Camargo | 4.0750 | 4.0376 | 4.0376 | 0.0000 | 0.0000 | 0.1717 | 0.0000 | Very Poor |

## Uncertainty and sensitivity

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


## Figures

- [Full figures gallery (HTML)](../figures/manaus/index.html)
- [daily_taylor](../figures/manaus/manaus_daily_taylor.png)
- [monthly_taylor](../figures/manaus/manaus_monthly_taylor.png)
- [monthly_totals](../figures/manaus/manaus_monthly_totals.png)
- [bias_by_eto_bin](../figures/manaus/manaus_bias_by_eto_bin.png)
- [daily_scatter_camargo_vs_pm](../figures/manaus/manaus_daily_scatter_camargo_vs_pm.png)
- [daily_scatter_gl_vs_pm](../figures/manaus/manaus_daily_scatter_gl_vs_pm.png)
- [daily_scatter_global_rad_vs_pm](../figures/manaus/manaus_daily_scatter_global_rad_vs_pm.png)
- [daily_scatter_hh_vs_pm](../figures/manaus/manaus_daily_scatter_hh_vs_pm.png)
- [daily_scatter_hs_corr_vs_pm](../figures/manaus/manaus_daily_scatter_hs_corr_vs_pm.png)
- [daily_scatter_hs_vs_pm](../figures/manaus/manaus_daily_scatter_hs_vs_pm.png)
- [daily_scatter_ivanov_vs_pm](../figures/manaus/manaus_daily_scatter_ivanov_vs_pm.png)
- [daily_scatter_jh_vs_pm](../figures/manaus/manaus_daily_scatter_jh_vs_pm.png)

---

Generated by the ET₀ methods comparison pipeline.
