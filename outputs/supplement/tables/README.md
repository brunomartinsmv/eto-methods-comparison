# outputs/tables

**PT**
Tabelas finais de metricas, rankings e consolidados. Cada tabela deve indicar claramente o metodo, a localidade e o periodo.
As tabelas oficiais do preprint ficam diretamente em `outputs/tables/`, fora de `legacy/`.

**EN**
Final tables with metrics, rankings, and consolidated outputs. Each table should clearly state method, site, and period.
Official preprint tables live directly in `outputs/tables/`, outside `legacy/`.

**Nota**: Tabelas geradas nos notebooks ficam em `outputs/tables/legacy/` e sao material historico/suplementar. Veja `docs/legacy.md`.

## Resultados oficiais / Official results
- `summary_rankings.csv` — ranked comparison across sites and temporal scales
- `{site}_limited_data_metrics.csv` — Penman-Monteith with FAO-56 substitutes for missing wind, humidity, or radiation, plus Hargreaves-Samani and Turc, scored on the same days against the full-data pipeline reference
- `manaus_daily_metrics.csv`
- `manaus_monthly_metrics.csv`
- `piracicaba_daily_metrics.csv`
- `piracicaba_monthly_metrics.csv`
- `{site}_daily_metrics_radiation_screen.csv` — daily metrics on days inside the FAO-56/ASCE radiation envelope

Padrao / Pattern: `<site>_daily_metrics.csv` and `<site>_monthly_metrics.csv`.
`<site>_daily_metrics_radiation_screen.csv` uses the same metric columns on the days that pass the radiation screen. The full-year tables are unchanged.
Metric columns include RMSE, MAE, MBE, Pearson r, R², Willmott d, confidence c,
Kling–Gupta efficiency (`kge`), percent bias (`pbias`), and the c-based
performance classification.

`calibrate` writes `<site>_<method>_calibration_coefficients.csv` and
`<site>_<method>_calibration_metrics.csv`. With two or more configured sites it
also writes `<method>_calibration_transfer.csv`: fit on one site's training
window, score at the other, original and calibrated metrics side by side.
`--free-exponent` estimates the Hargreaves-Samani temperature-range exponent;
otherwise that exponent stays at the published value 0.5. A lower test RMSE
against calculated Penman-Monteith is not a lysimeter validation.

## Como reproduzir / How to reproduce
```bash
python -m scripts.cli metrics --input data/cleaned --output outputs/tables
python -m scripts.cli limited-data --input data/cleaned --output outputs/tables
python -m scripts.cli summarize --input outputs/tables --output outputs/reports
```
