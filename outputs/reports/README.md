# Data quality reports

This directory stores CSV reports generated with:

```bash
python -m scripts.cli validate-data --year 2024
```

Each site report (`*_data_quality.csv`) contains one row per variable and records:

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

They report the best-performing method by lowest RMSE for each site and temporal
scale, using the current metrics tables in `outputs/tables/`. Ranking outputs
also include per-metric ranks for MAE, MBE, Pearson r, R², Willmott d, and the
confidence coefficient c.

`summary_rankings.md` is generated alongside `outputs/tables/summary_rankings.csv`
and lists every method ranked within each site and temporal scale.

Current report naming patterns:

- Site data-quality reports: `<site>_data_quality.csv`
- Combined data-quality report: `data_quality_summary.csv`
- Method rankings: `summary_rankings.md` (CSV in `outputs/tables/`)
- Summary reports: `summary.csv` and `summary.md`
