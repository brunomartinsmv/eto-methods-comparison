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

## Manaus — daily

Best overall: **Lungeon** by `composite`.

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

## Piracicaba — monthly

Best overall: **Stephens Stewart** by `composite`.

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
| 12 | Hargreaves Samani Corr | 53.7460 | 52.8334 | 52.8334 | 0.9641 | 0.9294 | 0.4674 | 0.4506 | Bad |
| 13 | Camargo | 57.8432 | 56.7780 | -56.7780 | 0.9280 | 0.8612 | 0.4070 | 0.3777 | Very Poor |
| 14 | Garcia Lopez | 38.0570 | 33.6941 | -32.5982 | 0.6241 | 0.3895 | 0.5666 | 0.3536 | Very Poor |
| 15 | Ivanov | 44.5007 | 34.2222 | 25.6442 | 0.1616 | 0.0261 | 0.3418 | 0.0552 | Very Poor |
| 16 | Lungeon | 82.3540 | 80.0178 | -80.0178 | 0.1937 | 0.0375 | 0.2785 | 0.0540 | Very Poor |
| 17 | Mccloud | 2165.4252 | 2139.2259 | 2139.2259 | 0.8944 | 0.7999 | 0.0162 | 0.0145 | Very Poor |
| 18 | Thornthwaite Camargo | 98.4131 | 96.3929 | -96.3929 | — | — | 0.2427 | — | — |

## Piracicaba — daily

Best overall: **Stephens Stewart** by `composite`.

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
| 13 | Ivanov | 1.8181 | 1.3161 | 0.8408 | 0.6087 | 0.3705 | 0.6853 | 0.4171 | Bad |
| 14 | Camargo | 2.1678 | 1.9410 | -1.8616 | 0.6382 | 0.4073 | 0.4905 | 0.3130 | Very Poor |
| 15 | Thornthwaite | 1.2325 | 0.9596 | 0.0793 | 0.4486 | 0.2013 | 0.6655 | 0.2986 | Very Poor |
| 16 | Lungeon | 2.8668 | 2.6243 | -2.6235 | 0.6175 | 0.3813 | 0.4277 | 0.2641 | Very Poor |
| 17 | Mccloud | 72.1348 | 70.1386 | 70.1386 | 0.7029 | 0.4941 | 0.0338 | 0.0238 | Very Poor |
| 18 | Thornthwaite Camargo | 3.4196 | 3.1605 | -3.1604 | — | — | 0.3670 | — | — |
