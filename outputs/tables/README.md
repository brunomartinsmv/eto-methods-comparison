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
- `manaus_daily_metrics.csv`
- `manaus_monthly_metrics.csv`
- `piracicaba_daily_metrics.csv`
- `piracicaba_monthly_metrics.csv`

Padrao / Pattern: `<site>_daily_metrics.csv` and `<site>_monthly_metrics.csv`.

## Como reproduzir / How to reproduce
```bash
python -m scripts.cli metrics --input data/cleaned --output outputs/tables
python -m scripts.cli summarize --input outputs/tables --output outputs/reports
```
