# outputs/figures

**PT**
Graficos finais usados na analise. Subpastas organizadas por localidade. Inclui diagramas de Taylor (diario e mensal).
As figuras oficiais do preprint ficam em `outputs/figures/manaus/` e `outputs/figures/piracicaba/`.

**EN**
Final figures used in the analysis. Subfolders are organized by site. Includes Taylor diagrams (daily and monthly).
Official preprint figures live in `outputs/figures/manaus/` and `outputs/figures/piracicaba/`.

**Nota**: Figuras geradas nos notebooks ficam em `outputs/figures/legacy/` e sao material historico/suplementar. Veja `docs/legacy.md`.

## Captions / Legendas
- `<site>_daily_scatter_<method>_vs_pm.png`: dispersao diaria do metodo vs Penman-Monteith.
- `<site>_daily_series_<method>_vs_pm.png`: series temporais diarias (metodo vs referencia).
- `<site>_monthly_totals.png`: totais mensais por metodo.
- `<site>_daily_taylor.png`: diagrama de Taylor diario.
- `<site>_monthly_taylor.png`: diagrama de Taylor mensal.

Para este estudo, `<site>` e `manaus` ou `piracicaba`.

## Como reproduzir / How to reproduce
```bash
python -m scripts.cli plots --input data/cleaned --output outputs/figures
```
