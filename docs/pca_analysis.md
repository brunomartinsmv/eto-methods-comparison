# PCA analysis

**PT**
Este comando adiciona uma analise PCA opcional para explorar quais variaveis meteorologicas explicam a variabilidade dos dados usados na estimativa de ET0.

Variaveis candidatas:
- temperatura media
- temperatura maxima
- temperatura minima
- umidade relativa media
- velocidade media do vento
- radiacao global
- radiacao liquida, quando disponivel

Uso:
```bash
python -m scripts.cli pca --site manaus
python -m scripts.cli pca --all-sites
```

Saidas por localidade:
- `outputs/tables/{site}_pca_loadings.csv`
- `outputs/tables/{site}_pca_explained_variance.csv`
- `outputs/figures/{site}/{site}_pca_biplot.png`

Com dados insuficientes, o comando falha para uma cidade individual ou emite aviso e pula a localidade quando executado em `--all-sites`.
Se houver metadados de `group` ou `biome`/`bioma` em `configs/sites.yml`, a mesma rotina tambem tenta gerar uma PCA agregada para o grupo.

**EN**
This optional PCA command explores which meteorological variables explain variability in the ET0 input data.
