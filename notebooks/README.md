# notebooks

**PT**
O notebook principal e `eto_results_overview.ipynb`. Ele explica e inspeciona os resultados gerados pelo pipeline sem duplicar logica central de metricas, limpeza ou graficos.

**EN**
The primary notebook is `eto_results_overview.ipynb`. It explains and inspects pipeline-generated results without duplicating core metric, cleaning, or plotting logic.

## Como usar / How to use
Execute primeiro, a partir da raiz do repositorio:

```bash
python -m scripts.cli all --year 2024
python -m scripts.cli validate-data --year 2024
```

Depois abra e execute:

```text
notebooks/eto_results_overview.ipynb
```

Os notebooks antigos foram movidos para `notebooks/legacy/`. Eles ficam apenas como material suplementar historico e podem conter caminhos antigos ou logica duplicada que foi substituida pelos modulos em `scripts/`.
