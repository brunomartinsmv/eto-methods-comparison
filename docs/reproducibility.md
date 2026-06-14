# Reprodutibilidade / Reproducibility

**PT**
Este documento descreve o ambiente, dependencias e passos minimos para reproduzir o estudo.

**EN**
This document describes the environment, dependencies, and minimum steps to reproduce the study.

## Escopo / Scope

**PT**
O comando principal preservado para compatibilidade e:

```bash
python -m scripts.cli all --year 2024
```

Ele regenera dados limpos, agregacoes, metricas e figuras principais para Manaus e Piracicaba. Para a colecao mais completa usada em revisao academica, incluindo relatorios de qualidade e sumarios, use `reproduce-paper`.

**EN**
The compatibility command is:

```bash
python -m scripts.cli all --year 2024
```

It regenerates cleaned data, aggregations, metrics, and main figures for Manaus and Piracicaba. For the fuller review-facing collection, including data-quality reports and summaries, use `reproduce-paper`.

## Ambiente / Environment
Recomendado para novas instalacoes:
```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

Fluxo compativel com a instalacao historica do repositorio:
```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

Para reproduzir com as versoes travadas usadas na curadoria do repositorio:
```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -r requirements-lock.txt
python -m pip install -e . --no-deps
```

Se o Matplotlib nao conseguir escrever cache, defina:
```bash
export MPLCONFIGDIR=/tmp/mpl-cache
```

## Pipeline
```bash
python -m scripts.cli all --year 2024
```

Para reproduzir a colecao completa esperada para revisao do preprint:
```bash
python -m scripts.cli reproduce-paper --year 2024
```

Para reproduzir apenas uma localidade configurada:
```bash
python -m scripts.cli all --year 2024 --site manaus
python -m scripts.cli all --year 2024 --site piracicaba
python -m scripts.cli all --year 2024 --all-sites
```

As localidades ficam em `configs/sites.yml`; os metodos e nomes de colunas ficam em `configs/methods.yml`.

## Comandos cientificos
```bash
python -m scripts.cli compute-eto --year 2024
python -m scripts.cli validate-data --year 2024
python -m scripts.cli pca --site manaus
python -m scripts.cli summarize --ranking composite
python -m scripts.cli summarize --ranking rmse
python -m scripts.cli export-supplement
```

- `compute-eto` le `data/cleaned/{site}_daily.csv` e escreve `outputs/results/{site}_daily_eto.csv` com ET0 calculada a partir de variaveis meteorologicas padronizadas.
- `validate-data` escreve relatorios CSV em `outputs/reports/`.
- `pca` escreve `outputs/tables/{site}_pca_loadings.csv`, `outputs/tables/{site}_pca_explained_variance.csv` e `outputs/figures/{site}/{site}_pca_biplot.png` quando ha variaveis e linhas suficientes.
- `summarize` escreve `outputs/reports/summary.csv`, `outputs/reports/summary.md` e `outputs/tables/summary_rankings.csv` com `rank` e `selection_rule`. A regra padrao `composite` ordena por maior `c`, menor `rmse`, menor `mae`, maior `willmott_d` e menor modulo de `mbe`; tambem e possivel escolher `rmse`, `mae`, `c` ou `willmott_d`.
- `export-supplement` cria `outputs/supplement/` com CSVs atuais de `outputs/tables/`, `outputs/results/` e `outputs/reports/`, deixando outputs legados fora do pacote suplementar.
- `all` continua disponivel para compatibilidade historica.
- `metrics` prefere `outputs/results/{site}_daily_eto.csv` quando esse arquivo existe; se nao existir, usa as colunas `et_*` pre-calculadas em `data/cleaned/{site}_daily.csv`.

## Como verificar os resultados / How to check results

**PT**
Depois de executar o pipeline, comece por:

- `outputs/tables/summary_rankings.csv`, para ranking por localidade e escala;
- `outputs/reports/summary_rankings.md`, para uma versao legivel em Markdown;
- `outputs/tables/{site}_daily_metrics.csv`, para metricas diarias;
- `outputs/figures/{site}/{site}_daily_taylor.png`, para comparacao visual;
- `outputs/reports/{site}_data_quality.csv`, para auditoria de dados.

**EN**
After running the pipeline, start with:

- `outputs/tables/summary_rankings.csv`, for rankings by site and scale;
- `outputs/reports/summary_rankings.md`, for a readable Markdown version;
- `outputs/tables/{site}_daily_metrics.csv`, for daily metrics;
- `outputs/figures/{site}/{site}_daily_taylor.png`, for visual comparison;
- `outputs/reports/{site}_data_quality.csv`, for data-quality auditing.

## Checagens de desenvolvimento / Development checks
```bash
python -m pytest
python -m ruff check .
```

O CI executa lint, testes e o pipeline principal quando `data/raw/Evapo.xlsx` esta disponivel no checkout.

## Saidas esperadas
- `data/cleaned/*_daily.csv`
- `outputs/results/*_rolling_7d.csv`
- `outputs/results/*_monthly_totals.csv`
- `outputs/results/*_daily_eto.csv`
- `outputs/tables/*_daily_metrics.csv`
- `outputs/tables/*_monthly_metrics.csv`
- `outputs/tables/*_pca_loadings.csv`
- `outputs/tables/*_pca_explained_variance.csv`
- `outputs/figures/<site>/*.png`
- `outputs/figures/<site>/*_pca_biplot.png`
- `outputs/reports/*_data_quality.csv`
- `outputs/reports/summary.csv`
- `outputs/reports/summary.md`
- `outputs/supplement/MANIFEST.md`

## Citacao / Citation

**PT**
Use `CITATION.cff` ou a secao "How to Cite" do `README.md` para citar o repositorio. O DOI de versao arquivado no Zenodo e `10.5281/zenodo.18615164`; o DOI conceitual para todas as versoes e `10.5281/zenodo.18615049`.

**EN**
Use `CITATION.cff` or the "How to Cite" section in `README.md` to cite the repository. The archived Zenodo version DOI is `10.5281/zenodo.18615164`; the concept DOI for all versions is `10.5281/zenodo.18615049`.

## Padrao de nomes / Naming standard
- Resultados diarios: `data/cleaned/{site}_daily.csv`
- Resultados de 7 dias: `outputs/results/{site}_rolling_7d.csv`
- Resultados mensais: `outputs/results/{site}_monthly_totals.csv`
- ET0 diaria calculada: `outputs/results/{site}_daily_eto.csv`
- Metricas: `outputs/tables/{site}_daily_metrics.csv` e `{site}_monthly_metrics.csv`
- Figuras: `outputs/figures/{site}/{site}_daily_scatter_{method}_vs_pm.png`, `{site}_daily_series_{method}_vs_pm.png`, `{site}_monthly_totals.png`, `{site}_daily_taylor.png`, `{site}_monthly_taylor.png`
- Relatorios: `outputs/reports/{site}_data_quality.csv`, `outputs/reports/data_quality_summary.csv`, `outputs/reports/summary.csv`, `outputs/reports/summary.md`

`rolling7d` e uma convencao antiga. Os resultados atuais gerados pela CLI usam
`rolling_7d`.

Arquivos sob `outputs/**/legacy/` sao mantidos apenas para auditoria historica e nao devem ser tratados como resultados principais do preprint. Veja `docs/legacy.md`.
