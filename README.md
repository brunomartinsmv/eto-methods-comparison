# Fisica Ambiental — Evapotranspiracao de Referencia (ETo)

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.18615164.svg)](https://doi.org/10.5281/zenodo.18615164)

**PT (Resumo)**
Este repositorio organiza um estudo academico sobre a estimativa de ETo para Piracicaba (SP) e Manaus (AM), comparando metodos empiricos e semi-empiricos com Penman-Monteith como referencia. O foco e reprodutibilidade: dados brutos, dados corrigidos, resultados intermediarios e produtos finais estao claramente separados.

**EN (Summary)**
This repository presents an academic study on reference evapotranspiration (ETo) for Piracicaba (SP) and Manaus (AM), comparing empirical and semi-empirical methods against Penman-Monteith as the reference. The structure prioritizes reproducibility by separating raw data, cleaned data, intermediate results, and final outputs.

## Estrutura / Structure
```
.
├── data/
│   ├── raw/            # dados originais / raw data
│   └── cleaned/        # dados corrigidos / cleaned data
├── outputs/
│   ├── results/        # agregacoes intermediarias / intermediate aggregates
│   ├── figures/        # graficos finais / final figures
│   └── tables/         # tabelas finais / final tables
├── scripts/            # pipeline Python (CLI)
├── notebooks/          # guias didaticos
├── docs/               # metodologia e reproducibilidade
└── README.md
```

## Reproducao rapida / Quickstart
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

# pipeline completo
python -m scripts.cli all --year 2024
```

## Student Quickstart
1. Run the pipeline: `python -m scripts.cli all --year 2024`.
2. Check outputs in `data/cleaned/`, `outputs/results/`, `outputs/tables/`, `outputs/figures/`.
3. Read `docs/methodology.md` before interpreting results.

## How to Cite
If you use this repository or its outputs in academic work, cite as:

> Vieira, B. M. M. (2026). *Fisica Ambiental — Evapotranspiracao de Referencia (ETo)*. Dataset and analysis code. Universidade Federal do Mato Grosso. https://doi.org/10.5281/zenodo.18615049

Concept DOI (all versions): https://doi.org/10.5281/zenodo.18615050

BibTeX:
```bibtex
@misc{vieira2026eto,
  author = {Vieira, Bruno Martins M.},
  title = {Fisica Ambiental --- Evapotranspiracao de Referencia (ETo)},
  year = {2026},
  howpublished = {Dataset and analysis code},
  institution = {Universidade Federal do Mato Grosso},
  doi = {10.5281/zenodo.18615049},
  doi_concept = {10.5281/zenodo.18615050},
  url = {https://doi.org/10.5281/zenodo.18615049}
}
```

## Metodos de ETo (resumo curto)
**PT:** Este repositorio avalia Thornthwaite, Thornthwaite-Camargo, Camargo, Hargreaves-Samani (original e corrigido), Priestley-Taylor e Penman-Monteith. A descricao completa, com equacoes, hipoteses, limitacoes e climas/regioes recomendadas, esta em `docs/methodology.md`.

**EN:** This repository evaluates Thornthwaite, Thornthwaite-Camargo, Camargo, Hargreaves-Samani (original and corrected), Priestley-Taylor, and Penman-Monteith. A complete description with equations, assumptions, limitations, and recommended climates/regions is in `docs/methodology.md`.

## Notebooks
Os notebooks em `notebooks/` sao o guia principal para estudantes. Eles explicam a motivacao e a interpretacao dos resultados, enquanto os scripts garantem reprodutibilidade.

## Referencias
Ver `docs/methodology.md` para referencias bibliograficas completas.
