# Method rankings

Methods are ranked within each site and temporal scale.
Overall `rank` follows `composite` (highest c, then lowest RMSE, lowest MAE, highest Willmott d, and lowest absolute MBE); per-metric ranks use their own metric criterion
(MBE ranks by absolute bias; r, R², Willmott d, and confidence c favor higher values).

Monthly scale is listed before daily.

[← Results index](../index.md) · [HTML version](summary_rankings.html)

## Manaus — monthly

Best overall: **Lungeon** by `composite`.

| rank | method | rmse | mae | mbe | r | r2 | willmott_d | c | classification |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Lungeon | 20.5217 | 19.2526 | -19.2526 | 0.9779 | 0.9563 | 0.5795 | 0.5667 | Poor |
| 2 | Hargreaves Samani | 26.0025 | 24.3521 | 24.3521 | 0.9031 | 0.8155 | 0.5198 | 0.4694 | Bad |
| 3 | Camargo | 24.1782 | 21.8935 | 21.2765 | 0.8796 | 0.7737 | 0.4976 | 0.4376 | Bad |
| 4 | Garcia Lopez | 38.3370 | 36.1689 | -36.1689 | 0.9537 | 0.9095 | 0.3669 | 0.3500 | Very Poor |
| 5 | Turc | 25.8510 | 22.1849 | -22.1849 | 0.7553 | 0.5705 | 0.4385 | 0.3312 | Very Poor |
| 6 | Hicks Hess | 36.6677 | 34.2514 | -34.2514 | 0.7531 | 0.5671 | 0.3742 | 0.2818 | Very Poor |
| 7 | Jensen Heise | 36.6042 | 34.1506 | -34.1506 | 0.7424 | 0.5512 | 0.3737 | 0.2775 | Very Poor |
| 8 | Stephens Stewart | 37.6545 | 35.2000 | -35.2000 | 0.7199 | 0.5182 | 0.3660 | 0.2635 | Very Poor |
| 9 | Radiation Temperature | 38.0957 | 35.6390 | -35.6390 | 0.7012 | 0.4917 | 0.3629 | 0.2545 | Very Poor |
| 10 | Priestley Taylor | 38.0575 | 35.5843 | -35.5843 | 0.6635 | 0.4402 | 0.3628 | 0.2407 | Very Poor |
| 11 | Global Radiation | 37.5385 | 35.0352 | -35.0352 | 0.6221 | 0.3870 | 0.3659 | 0.2276 | Very Poor |
| 12 | Makkink | 41.3374 | 39.0802 | -39.0802 | 0.6544 | 0.4282 | 0.3464 | 0.2267 | Very Poor |
| 13 | Net Radiation | 38.0119 | 35.5222 | -35.5222 | 0.6221 | 0.3870 | 0.3628 | 0.2257 | Very Poor |
| 14 | Mccloud | 3273.8507 | 3264.0347 | 3264.0347 | 0.9419 | 0.8872 | 0.0078 | 0.0073 | Very Poor |
| 15 | Ivanov | 4468.4163 | 4205.1577 | 4205.1577 | 0.9776 | 0.9558 | 0.0074 | 0.0072 | Very Poor |

## Manaus — daily

Best overall: **Lungeon** by `composite`.

| rank | method | rmse | mae | mbe | r | r2 | willmott_d | c | classification |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | Lungeon | 0.7705 | 0.6325 | -0.6312 | 0.9165 | 0.8401 | 0.6334 | 0.5805 | Poor |
| 2 | Camargo | 0.9182 | 0.8270 | 0.6976 | 0.8776 | 0.7701 | 0.5303 | 0.4653 | Bad |
| 3 | Garcia Lopez | 1.3500 | 1.1859 | -1.1859 | 0.9514 | 0.9052 | 0.4268 | 0.4061 | Bad |
| 4 | Hicks Hess | 1.2977 | 1.1230 | -1.1230 | 0.8356 | 0.6982 | 0.4349 | 0.3634 | Very Poor |
| 5 | Hargreaves Samani | 0.9739 | 0.8925 | 0.7984 | 0.6516 | 0.4246 | 0.5506 | 0.3588 | Very Poor |
| 6 | Turc | 0.9887 | 0.7530 | -0.7274 | 0.7720 | 0.5960 | 0.4637 | 0.3580 | Very Poor |
| 7 | Jensen Heise | 1.3015 | 1.1197 | -1.1197 | 0.7546 | 0.5695 | 0.4308 | 0.3251 | Very Poor |
| 8 | Stephens Stewart | 1.3370 | 1.1541 | -1.1541 | 0.7385 | 0.5454 | 0.4221 | 0.3117 | Very Poor |
| 9 | Radiation Temperature | 1.3519 | 1.1685 | -1.1685 | 0.7254 | 0.5261 | 0.4184 | 0.3035 | Very Poor |
| 10 | Priestley Taylor | 1.3511 | 1.1667 | -1.1667 | 0.6993 | 0.4890 | 0.4181 | 0.2924 | Very Poor |
| 11 | Makkink | 1.4506 | 1.2813 | -1.2813 | 0.6993 | 0.4890 | 0.4061 | 0.2840 | Very Poor |
| 12 | Global Radiation | 1.3344 | 1.1487 | -1.1487 | 0.6718 | 0.4513 | 0.4213 | 0.2830 | Very Poor |
| 13 | Net Radiation | 1.3500 | 1.1647 | -1.1647 | 0.6718 | 0.4513 | 0.4179 | 0.2807 | Very Poor |
| 14 | Mccloud | 107.7087 | 107.0175 | 107.0175 | 0.8815 | 0.7770 | 0.0116 | 0.0102 | Very Poor |
| 15 | Ivanov | 152.6745 | 137.8740 | 137.8740 | 0.9164 | 0.8397 | 0.0109 | 0.0100 | Very Poor |

## Piracicaba — monthly

Best overall: **Makkink** by `composite`.

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

## Piracicaba — daily

Best overall: **Stephens Stewart** by `composite`.

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
