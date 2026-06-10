# Reprodutibilidade / Reproducibility

**PT**
Este documento descreve o ambiente, dependencias e passos minimos para reproduzir o estudo.

**EN**
This document describes the environment, dependencies, and minimum steps to reproduce the study.

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

Para reproduzir apenas uma localidade configurada:
```bash
python -m scripts.cli all --year 2024 --site manaus
python -m scripts.cli all --year 2024 --site piracicaba
python -m scripts.cli all --year 2024 --all-sites
```

As localidades ficam em `configs/sites.yml`; os metodos e nomes de colunas ficam em `configs/methods.yml`.

## Checagens de desenvolvimento / Development checks
```bash
python -m pytest
python -m ruff check .
```

Se ainda nao houver testes versionados no checkout, `pytest` pode encerrar sem coletar testes. O CI deve tratar esse caso explicitamente ate a suite minima ser adicionada.

## Saidas esperadas
- `data/cleaned/*_daily.csv`
- `outputs/results/*_rolling_7d.csv`
- `outputs/results/*_monthly_totals.csv`
- `outputs/tables/*_metrics_*.csv`
- `outputs/figures/<site>/*.png`
- `outputs/reports/*_data_quality.csv`

Arquivos sob `outputs/**/legacy/` sao mantidos apenas para auditoria historica e nao devem ser tratados como resultados principais do preprint. Veja `docs/legacy.md`.
