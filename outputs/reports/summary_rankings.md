# Method rankings

Methods are ranked within each site and temporal scale.
Overall `rank` follows lowest RMSE; per-metric ranks use the same criterion
(MBE ranks by absolute bias; R² and Willmott d favor higher values).

## Manaus — daily

Best overall: **et_lungeon** (RMSE = 0.7705).

| site | scale | rank | method | rmse | mae | mbe | r2 | willmott_d | rank_rmse | rank_mae | rank_mbe | rank_r2 | rank_willmott_d |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| manaus | daily | 1 | et_lungeon | 0.7705 | 0.6325 | -0.6312 | 0.8401 | 0.6334 | 1 | 1 | 1 | 2 | 1 |
| manaus | daily | 2 | et_camargo | 0.9182 | 0.8270 | 0.6976 | 0.7701 | 0.5303 | 2 | 3 | 2 | 5 | 3 |
| manaus | daily | 3 | et_hargreaves_samani | 0.9739 | 0.8925 | 0.7984 | 0.4246 | 0.5506 | 3 | 4 | 4 | 15 | 2 |
| manaus | daily | 4 | et_turc | 0.9887 | 0.7530 | -0.7274 | 0.5960 | 0.4637 | 4 | 2 | 3 | 7 | 4 |
| manaus | daily | 5 | et_hicks_hess | 1.2977 | 1.1230 | -1.1230 | 0.6982 | 0.4349 | 5 | 6 | 6 | 6 | 5 |
| manaus | daily | 6 | et_jensen_heise | 1.3015 | 1.1197 | -1.1197 | 0.5695 | 0.4308 | 6 | 5 | 5 | 8 | 6 |
| manaus | daily | 7 | et_global_radiation | 1.3344 | 1.1487 | -1.1487 | 0.4513 | 0.4213 | 7 | 7 | 7 | 13 | 9 |
| manaus | daily | 8 | et_stephens_stewart | 1.3370 | 1.1541 | -1.1541 | 0.5454 | 0.4221 | 8 | 8 | 8 | 9 | 8 |
| manaus | daily | 9 | et_garcia_lopez | 1.3500 | 1.1859 | -1.1859 | 0.9052 | 0.4268 | 9 | 12 | 12 | 1 | 7 |
| manaus | daily | 10 | et_net_radiation | 1.3500 | 1.1647 | -1.1647 | 0.4513 | 0.4179 | 10 | 9 | 9 | 14 | 12 |
| manaus | daily | 11 | et_priestley_taylor | 1.3511 | 1.1667 | -1.1667 | 0.4890 | 0.4181 | 11 | 10 | 10 | 11 | 11 |
| manaus | daily | 12 | et_radiation_temperature | 1.3519 | 1.1685 | -1.1685 | 0.5261 | 0.4184 | 12 | 11 | 11 | 10 | 10 |
| manaus | daily | 13 | et_makkink | 1.4506 | 1.2813 | -1.2813 | 0.4890 | 0.4061 | 13 | 13 | 13 | 12 | 13 |
| manaus | daily | 14 | et_mccloud | 107.7087 | 107.0175 | 107.0175 | 0.7770 | 0.0116 | 14 | 14 | 14 | 4 | 14 |
| manaus | daily | 15 | et_ivanov | 152.6745 | 137.8740 | 137.8740 | 0.8397 | 0.0109 | 15 | 15 | 15 | 3 | 15 |

## Manaus — monthly

Best overall: **et_lungeon** (RMSE = 20.5217).

| site | scale | rank | method | rmse | mae | mbe | r2 | willmott_d | rank_rmse | rank_mae | rank_mbe | rank_r2 | rank_willmott_d |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| manaus | monthly | 1 | et_lungeon | 20.5217 | 19.2526 | -19.2526 | 0.9563 | 0.5795 | 1 | 1 | 1 | 1 | 1 |
| manaus | monthly | 2 | et_camargo | 24.1782 | 21.8935 | 21.2765 | 0.7737 | 0.4976 | 2 | 2 | 2 | 6 | 3 |
| manaus | monthly | 3 | et_turc | 25.8510 | 22.1849 | -22.1849 | 0.5705 | 0.4385 | 3 | 3 | 3 | 7 | 4 |
| manaus | monthly | 4 | et_hargreaves_samani | 26.0025 | 24.3521 | 24.3521 | 0.8155 | 0.5198 | 4 | 4 | 4 | 5 | 2 |
| manaus | monthly | 5 | et_jensen_heise | 36.6042 | 34.1506 | -34.1506 | 0.5512 | 0.3737 | 5 | 5 | 5 | 9 | 6 |
| manaus | monthly | 6 | et_hicks_hess | 36.6677 | 34.2514 | -34.2514 | 0.5671 | 0.3742 | 6 | 6 | 6 | 8 | 5 |
| manaus | monthly | 7 | et_global_radiation | 37.5385 | 35.0352 | -35.0352 | 0.3870 | 0.3659 | 7 | 7 | 7 | 15 | 9 |
| manaus | monthly | 8 | et_stephens_stewart | 37.6545 | 35.2000 | -35.2000 | 0.5182 | 0.3660 | 8 | 8 | 8 | 10 | 8 |
| manaus | monthly | 9 | et_net_radiation | 38.0119 | 35.5222 | -35.5222 | 0.3870 | 0.3628 | 9 | 9 | 9 | 14 | 12 |
| manaus | monthly | 10 | et_priestley_taylor | 38.0575 | 35.5843 | -35.5843 | 0.4402 | 0.3628 | 10 | 10 | 10 | 12 | 11 |
| manaus | monthly | 11 | et_radiation_temperature | 38.0957 | 35.6390 | -35.6390 | 0.4917 | 0.3629 | 11 | 11 | 11 | 11 | 10 |
| manaus | monthly | 12 | et_garcia_lopez | 38.3370 | 36.1689 | -36.1689 | 0.9095 | 0.3669 | 12 | 12 | 12 | 3 | 7 |
| manaus | monthly | 13 | et_makkink | 41.3374 | 39.0802 | -39.0802 | 0.4282 | 0.3464 | 13 | 13 | 13 | 13 | 13 |
| manaus | monthly | 14 | et_mccloud | 3273.8507 | 3264.0347 | 3264.0347 | 0.8872 | 0.0078 | 14 | 14 | 14 | 4 | 14 |
| manaus | monthly | 15 | et_ivanov | 4468.4163 | 4205.1577 | 4205.1577 | 0.9558 | 0.0074 | 15 | 15 | 15 | 2 | 15 |

## Piracicaba — daily

Best overall: **et_stephens_stewart** (RMSE = 0.4975).

| site | scale | rank | method | rmse | mae | mbe | r2 | willmott_d | rank_rmse | rank_mae | rank_mbe | rank_r2 | rank_willmott_d |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| piracicaba | daily | 1 | et_stephens_stewart | 0.4975 | 0.3442 | -0.2170 | 0.8933 | 0.9628 | 1 | 1 | 4 | 2 | 1 |
| piracicaba | daily | 2 | et_makkink | 0.5147 | 0.3556 | -0.1555 | 0.8749 | 0.9581 | 2 | 2 | 2 | 5 | 2 |
| piracicaba | daily | 3 | et_priestley_taylor | 0.5813 | 0.4405 | -0.0517 | 0.8535 | 0.9579 | 3 | 3 | 1 | 6 | 3 |
| piracicaba | daily | 4 | et_net_radiation | 0.6526 | 0.5123 | 0.1968 | 0.8394 | 0.9482 | 4 | 4 | 3 | 7 | 4 |
| piracicaba | daily | 5 | et_turc | 0.6576 | 0.5699 | 0.5028 | 0.9030 | 0.9388 | 5 | 6 | 7 | 1 | 6 |
| piracicaba | daily | 6 | et_radiation_temperature | 0.6948 | 0.5499 | -0.4851 | 0.8901 | 0.9216 | 6 | 5 | 6 | 3 | 7 |
| piracicaba | daily | 7 | et_jensen_heise | 0.7319 | 0.5982 | 0.4707 | 0.8884 | 0.9395 | 7 | 7 | 5 | 4 | 5 |
| piracicaba | daily | 8 | et_global_radiation | 0.7929 | 0.6827 | 0.5677 | 0.8361 | 0.9132 | 8 | 8 | 8 | 8 | 8 |
| piracicaba | daily | 9 | et_hicks_hess | 1.2431 | 0.8752 | 0.7787 | 0.7739 | 0.8577 | 9 | 9 | 9 | 9 | 9 |
| piracicaba | daily | 10 | et_garcia_lopez | 1.3238 | 1.1169 | -0.8634 | 0.6670 | 0.8264 | 10 | 10 | 10 | 11 | 10 |
| piracicaba | daily | 11 | et_hargreaves_samani | 1.7225 | 1.4991 | -1.4120 | 0.7082 | 0.5918 | 11 | 11 | 11 | 10 | 11 |
| piracicaba | daily | 12 | et_camargo | 2.3417 | 2.0996 | -2.0277 | 0.3814 | 0.4802 | 12 | 12 | 12 | 15 | 12 |
| piracicaba | daily | 13 | et_lungeon | 3.0336 | 2.7899 | -2.7896 | 0.4483 | 0.4243 | 13 | 13 | 13 | 13 | 13 |
| piracicaba | daily | 14 | et_mccloud | 71.9653 | 69.9725 | 69.9725 | 0.4927 | 0.0354 | 14 | 14 | 14 | 12 | 14 |
| piracicaba | daily | 15 | et_ivanov | 131.2327 | 116.7104 | 116.7099 | 0.4374 | 0.0205 | 15 | 15 | 15 | 14 | 15 |

## Piracicaba — monthly

Best overall: **et_makkink** (RMSE = 8.5015).

| site | scale | rank | method | rmse | mae | mbe | r2 | willmott_d | rank_rmse | rank_mae | rank_mbe | rank_r2 | rank_willmott_d |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| piracicaba | monthly | 1 | et_makkink | 8.5015 | 5.8852 | -4.7418 | 0.8788 | 0.9518 | 1 | 1 | 2 | 5 | 1 |
| piracicaba | monthly | 2 | et_stephens_stewart | 9.8682 | 6.9649 | -6.6192 | 0.8800 | 0.9427 | 2 | 2 | 4 | 4 | 2 |
| piracicaba | monthly | 3 | et_priestley_taylor | 13.4000 | 11.8551 | -1.5776 | 0.7401 | 0.9116 | 3 | 3 | 1 | 11 | 3 |
| piracicaba | monthly | 4 | et_net_radiation | 14.4216 | 12.4665 | 6.0014 | 0.7367 | 0.8953 | 4 | 4 | 3 | 12 | 4 |
| piracicaba | monthly | 5 | et_turc | 16.3449 | 15.3342 | 15.3342 | 0.9258 | 0.8591 | 5 | 6 | 7 | 2 | 6 |
| piracicaba | monthly | 6 | et_radiation_temperature | 16.3891 | 14.7943 | -14.7943 | 0.8820 | 0.8458 | 6 | 5 | 6 | 3 | 7 |
| piracicaba | monthly | 7 | et_jensen_heise | 18.7174 | 15.5843 | 14.3574 | 0.8736 | 0.8611 | 7 | 7 | 5 | 6 | 5 |
| piracicaba | monthly | 8 | et_global_radiation | 18.8716 | 17.5325 | 17.3142 | 0.8636 | 0.8062 | 8 | 8 | 8 | 8 | 8 |
| piracicaba | monthly | 9 | et_hicks_hess | 30.5628 | 23.7490 | 23.7490 | 0.8729 | 0.7493 | 9 | 9 | 9 | 7 | 9 |
| piracicaba | monthly | 10 | et_garcia_lopez | 33.7056 | 29.5440 | -26.3328 | 0.5040 | 0.6535 | 10 | 10 | 10 | 13 | 10 |
| piracicaba | monthly | 11 | et_hargreaves_samani | 44.2709 | 43.0648 | -43.0648 | 0.9331 | 0.4908 | 11 | 11 | 11 | 1 | 11 |
| piracicaba | monthly | 12 | et_camargo | 63.0266 | 61.8441 | -61.8441 | 0.7881 | 0.3822 | 12 | 12 | 12 | 9 | 12 |
| piracicaba | monthly | 13 | et_lungeon | 87.2594 | 85.0839 | -85.0839 | 0.0928 | 0.2681 | 13 | 13 | 13 | 14 | 13 |
| piracicaba | monthly | 14 | et_mccloud | 2160.4530 | 2134.1598 | 2134.1598 | 0.7519 | 0.0162 | 14 | 14 | 14 | 10 | 14 |
| piracicaba | monthly | 15 | et_ivanov | 3700.2472 | 3559.6517 | 3559.6517 | 0.0749 | 0.0093 | 15 | 15 | 15 | 15 | 15 |
