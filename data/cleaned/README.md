# data/cleaned

**PT**
Dados corrigidos/interpolados. Aqui ficam arquivos resultantes do tratamento de falhas, padronizacao de colunas e conversoes. Estes dados sao a base para agregacoes e metricas.

**EN**
Corrected/interpolated data. Files here result from cleaning missing values, standardizing columns, and conversions. These are the inputs for aggregation and metrics.

## Colunas canonicas / Canonical columns

Os CSVs diarios (`{site}_daily.csv`) mantem apenas:

- `date` e variaveis meteorologicas padronizadas (`tmed_c`, `rh_mean_pct`, `wind_mean_ms`, …)
- variaveis derivadas usadas no pipeline (`ra_extraterrestre_mj_m2_d`)
- colunas de ETo (`et_*`) vindas da planilha ou pre-calculadas

Colunas legadas da planilha original (por exemplo `T_med`, `I`, `es`, `ea`, `delta_e`) sao descartadas na escrita de `clean`. Arquivos historicos fora desse padrao foram movidos para `legacy/`.

## Como reproduzir / How to reproduce

```bash
python -m scripts.cli clean --input data/raw/Evapo.xlsx --output data/cleaned
```

## Arquivos legados / Legacy files

Planilhas e exports antigos que nao seguem o contrato `{site}_daily.csv` estao em `data/cleaned/legacy/`.
