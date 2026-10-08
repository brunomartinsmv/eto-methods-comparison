# Data quality reports

This directory stores CSV reports generated with:

```bash
python -m scripts.cli validate-data --year 2024
```

Each site report (`*_data_quality.csv`) contains input and precomputed ET0 rows plus one row per calculated method.
Methods configured as `precomputed_only` appear only in the precomputed stage.
The report records:

- `stage`: `input`, `precomputed_et0`, or `computed_et0`.
- `status`: `available`, `not_available`, or `not_run`.
- `source_present`: whether the source contains the series.
- `valid_days` and `valid_fraction`: finite daily coverage within the expected calendar.
- `finite_values` and `non_finite_values`: numeric value counts.

- `row_count`: rows retained after cleaning.
- `expected_days`: daily dates expected within the observed period.
- `start_date` and `end_date`: cleaned data period.
- `missing_dates`: semicolon-separated dates absent from the cleaned daily series.
- `duplicate_dates`: semicolon-separated duplicate dates found before cleaning.
- `missing_values`: missing values in the raw standardized input.
- `interpolated_values`: values filled by numeric interpolation during cleaning.
- `physical_limit_violations`: values outside conservative physical plausibility limits.

`data_quality_summary.csv` concatenates the site-level reports for quick review.

`summary.csv` and `summary.md` are generated with:

```bash
python -m scripts.cli summarize
```

They report the best-performing method for each site and temporal scale using
the selected ranking rule and the current metrics tables in `outputs/tables/`.
The default is `--ranking composite`: highest confidence coefficient c, then
lowest RMSE, lowest MAE, highest Willmott d, and lowest absolute MBE. You can
also choose `--ranking rmse`, `--ranking mae`, `--ranking c`, or
`--ranking willmott_d`. Ranking outputs include `rank`, `selection_rule`, and
per-metric ranks for MAE, MBE, Pearson r, R², Willmott d, and the confidence
coefficient c.

`summary_rankings.md` is generated alongside `outputs/tables/summary_rankings.csv`
and lists every method ranked within each site and temporal scale.

Current report naming patterns:

- Site data-quality reports: `<site>_data_quality.csv`
- Combined data-quality report: `data_quality_summary.csv`
- Method rankings: `summary_rankings.md` (CSV in `outputs/tables/`)
- Summary reports: `summary.csv` and `summary.md`
