# outputs/results

**PT**
Resultados intermediarios (ex.: media movel de 7 dias, totais mensais). Sao derivados diretamente dos dados limpos.
Padrao de nomes: `<site>_rolling_7d.csv` e `<site>_monthly_totals.csv`.
Os resultados oficiais ficam diretamente em `outputs/results/`. Resultados gerados nos notebooks ficam em `outputs/results/legacy/` e sao historicos/suplementares.
Arquivos antigos com `rolling7d` no nome seguem a convencao legada; use `rolling_7d` nos resultados atuais.

**EN**
Intermediate results (e.g., 7-day rolling means, monthly totals). Derived directly from cleaned data.
Naming pattern: `<site>_rolling_7d.csv` and `<site>_monthly_totals.csv`.
Official intermediate outputs live directly in `outputs/results/`. Notebook-generated results are stored in `outputs/results/legacy/` and are historical/supplemental.
Older files named with `rolling7d` follow the legacy convention; use `rolling_7d` for current outputs.

See `docs/legacy.md` before using any file under `legacy/`.

## Como reproduzir / How to reproduce
```bash
python -m scripts.cli aggregate --input data/cleaned --output outputs/results
```
