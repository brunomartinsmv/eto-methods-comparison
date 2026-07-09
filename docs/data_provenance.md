# Proveniencia dos dados

Este documento registra a origem e o tratamento dos dados usados no estudo de
evapotranspiracao de referencia (ETo) para 2024. Ele deve ser atualizado sempre
que os arquivos em `data/raw/` forem substituidos.

## Fonte primaria

- Fonte institucional: Instituto Nacional de Meteorologia (INMET), dados
  meteorologicos de estacoes brasileiras.
- Portal de dados historicos anuais: https://portal.inmet.gov.br/dadoshistoricos
- Banco de Dados Meteorologicos (BDMEP): https://bdmep.inmet.gov.br/
- Orientacao oficial de acesso: o INMET informa que os dados meteorologicos
  publicos podem ser acessados pelo portal e pelo BDMEP, e que os dados de
  estacoes automaticas sao brutos e de uso sob responsabilidade do usuario.

## Arquivos brutos versionados

| Arquivo | Papel no repositorio | SHA-256 |
| --- | --- | --- |
| `data/raw/Evapo.xlsx` | Planilha bruta esperada pela CLI; contem abas `Piracicaba`, `Manaus` e `Petrolina`. As analises versionadas usam `Piracicaba` e `Manaus`. | `e3a7841cf56234c70bed9fdcfd1ae3feb3636200968fd9cec62a094139ac4561` |
| `data/raw/Evapo_2.xlsx` | Planilha auxiliar/legada com variaveis meteorologicas basicas nas mesmas abas. Nao e o input padrao da CLI atual. | `815e5f9a906cc5513c399646323e13a0cec79ae4d2aca0e0340e347fdbbe1e5e` |

O comando padrao do estudo espera:

```bash
python -m scripts.cli all --year 2024 --input data/raw/Evapo.xlsx --use-precomputed-eto
```

`--use-precomputed-eto` e o modo padrao atual por compatibilidade. A flag
torna explicita a dependencia transitoria de colunas de ETo ja calculadas na
planilha. A flag `--compute-eto` nos comandos `clean` e `all` calcula ET0 a
partir das variaveis meteorologicas padronizadas apos a limpeza e escreve
`outputs/results/{site}_daily_eto.csv`. O comando dedicado `compute-eto` e o
passo `compute-eto` de `run-site` / `reproduce-paper` fazem o mesmo calculo de
forma explicita. Metodos com `status: precomputed_only` continuam dependentes
das colunas historicas da planilha.

## Localidades analisadas

As coordenadas e altitudes abaixo sao as usadas pela configuracao do pipeline
em `configs/sites.yml`.

| Localidade | Aba em `Evapo.xlsx` | Latitude | Longitude | Altitude | Periodo usado |
| --- | --- | ---: | ---: | ---: | --- |
| Manaus, AM | `Manaus` | -3.1019 | -60.0164 | 61.25 m | 2024-01-01 a 2024-12-31 |
| Piracicaba, SP | `Piracicaba` | -22.7083 | -47.6333 | 546.0 m | 2024-01-01 a 2024-12-31 |

Codigo exato da estacao INMET e data original de download nao estao registrados
nos arquivos atualmente versionados. Para auditoria futura, esses campos devem
ser preenchidos no momento do download ou da substituicao do arquivo bruto.

## Variaveis usadas e unidades originais

| Coluna original | Nome padronizado | Unidade original |
| --- | --- | --- |
| `DIA` | `date` | dia do ano ou data |
| `TMED (oC)` | `tmed_c` | graus Celsius |
| `TMAX (oC)` | `tmax_c` | graus Celsius |
| `TMIN (oC)` | `tmin_c` | graus Celsius |
| `UR MED (%)` | `rh_mean_pct` | porcentagem |
| `UR MAX (%)` | `rh_max_pct` | porcentagem |
| `UR MIN (%)` | `rh_min_pct` | porcentagem |
| `Vento (m/s)` | `wind_mean_ms` | m s-1 |
| `Vel.Vento Max (m/s)` | `wind_max_ms` | m s-1 |
| `Chuva (mm)` | `rain_mm` | mm |
| `Rad.Glob. (MJ/m2.d)` / `Rad. Global (MJ/ma^2)` | `rad_global_mj_m2_d` | MJ m-2 d-1 |
| `Rad Liq (MJ/m2.d)` / `Rad. Líquida (MJ/ma^2)` | `rad_net_mj_m2_d` | MJ m-2 d-1 |
| `Q_0` | `ra_extraterrestre_mj_m2_d` | MJ m-2 d-1 |

`Evapo.xlsx` tambem contem colunas de ETo ja calculadas ou auxiliares de
calculo, incluindo `Thornthwaite`, `Thornthwaite-Camargo`, `Camargo`,
`Hargreaves & Samani`, `Hargreaves & Samani (corrigido)`,
`Priestley-Taylor`, `Penman-Monteith` e `Garcia Lopez`. A coluna
`Penman-Monteith` e padronizada como `et_penman_monteith` e usada como
referencia para as metricas comparativas.

## Camadas de dados na transicao raw-to-ETo

A transicao metodologica separa quatro camadas:

| Camada | Conteudo | Estado atual |
| --- | --- | --- |
| Dados meteorologicos brutos padronizados | Data, temperatura, umidade, vento, chuva e radiacao vindas da planilha ou de fontes INMET futuras. | Lidos por `scripts.io.read_evapo_sheet` via `WEATHER_COLUMNS`. |
| Variaveis meteorologicas derivadas | Variaveis calculadas a partir de coordenadas/data ou de outros insumos, como `ra_extraterrestre_mj_m2_d`. | Classificadas em `scripts.eto_layers`, mas ainda consumidas da planilha quando presentes. |
| ETo calculada pelos metodos | Series `et_*` produzidas por formulas versionadas de Thornthwaite, Camargo, Hargreaves-Samani, Priestley-Taylor, Penman-Monteith e metodos radiativos configurados. | Calculada por `scripts.compute_eto` e escrita em `outputs/results/{site}_daily_eto.csv`. |
| Metricas comparativas | RMSE, MAE, MBE, r, R2, Willmott d, c, classificacao por c, agregacoes mensais, bootstrap, sazonalidade e vies por faixa de ETo. | Calculadas por `scripts.metrics`, `scripts.aggregate`, `scripts.uncertainty`, `scripts.plots` e `scripts.summary`; `metrics` prefere ET0 calculada em `outputs/results/` e usa colunas `et_*` limpas como fallback. |

`scripts.eto_layers.build_data_layers` e a camada intermediaria inicial para
auditar essa separacao no DataFrame padronizado. Ela nao muda resultados; apenas
classifica colunas existentes.

## Dependencias atuais de ETo pre-calculada

Os seguintes pontos ainda dependem explicitamente de colunas `et_*` vindas de
`Evapo.xlsx` ou de CSVs limpos derivados dela:

| Arquivo | Dependencia |
| --- | --- |
| `configs/methods.yml` | Define os nomes padronizados das colunas de ETo dos metodos configurados. |
| `scripts/config.py` | Carrega `METHOD_COLUMNS` e `REFERENCE_COLUMN`; `WEATHER_COLUMNS` ainda inclui somente padronizacao de insumos, nao formulas; `LEGACY_METHOD_COLUMN_ALIASES` mantem compatibilidade com cabecalhos historicos da planilha. |
| `scripts/io.py` | Renomeia as colunas de metodos da planilha para `et_*`. |
| `scripts/cli.py` | `clean` preserva colunas `et_*`; `aggregate`, `metrics`, `plots` e `analyze-uncertainty` selecionam colunas `et_*` presentes no CSV limpo. |
| `scripts/aggregate.py` | Soma colunas de ETo para totais mensais. |
| `scripts/metrics.py` | Calcula metricas comparando metodos contra `et_penman_monteith`. |
| `scripts/uncertainty.py` | Reamostra e estratifica vies usando a serie `et_penman_monteith` como referencia. |
| `scripts/plots.py` | Gera figuras a partir de colunas de ETo ja existentes. |
| `scripts/quality.py` | Aplica limites de qualidade tambem as colunas `et_*`, assumindo que elas ja existem. |
| `scripts/summary.py` | Resume tabelas de metricas ja calculadas a partir de `et_*`. |

Essa dependencia e considerada legado/transitoria. Nenhum resultado versionado e
alterado por esta documentacao ou pela flag preparatoria.

## Transformacoes realizadas pelo pipeline

1. `scripts.io.read_evapo_sheet` le a aba da localidade com `skiprows=4`.
2. Colunas `Unnamed:*` sao descartadas.
3. Nomes de colunas meteorologicas e de metodos sao padronizados conforme
   `scripts/config.py` e `configs/methods.yml`.
4. A coluna `date` e interpretada como dia do ano quando numerica entre 1 e
   366; caso contrario, e lida como data.
5. `scripts.cleaning.clean_daily` ordena por data, interpola colunas numericas
   com interpolacao linear e `limit_direction="both"`, e remove datas
   duplicadas mantendo a primeira ocorrencia.
6. `scripts.cli aggregate`, `metrics` e `plots` geram agregacoes, metricas e
   figuras em `outputs/`.

Para auditar interpolacao, duplicatas, datas ausentes e limites fisicos, execute:

```bash
python -m scripts.cli validate-data --year 2024
```

Os relatatorios sao gravados em `outputs/reports/`.

## Como reobter os dados brutos

1. Acessar https://portal.inmet.gov.br/dadoshistoricos ou
   https://bdmep.inmet.gov.br/.
2. Selecionar dados meteorologicos de 2024 para as estacoes correspondentes a
   Manaus, AM, e Piracicaba, SP.
3. Baixar os arquivos originais do INMET sem edicao manual.
4. Preservar uma copia dos arquivos baixados em `data/raw/` ou em um deposito
   externo com DOI, mantendo os checksums.
5. Se for necessario converter os arquivos do INMET para `Evapo.xlsx`, registrar
   em commit separado o script ou procedimento usado para montar as abas
   `Manaus` e `Piracicaba`.

## Lacunas conhecidas de proveniencia

- A data original de download nao esta embutida nos arquivos versionados.
- Os codigos oficiais das estacoes INMET nao estao registrados na planilha.
- A planilha `Evapo.xlsx` inclui colunas de ETo e colunas auxiliares ja
  calculadas; o procedimento historico que produziu essas colunas deve ser
  documentado ou substituido por calculo totalmente scriptado em entrega futura.
- Metodos `precomputed_only` (Thornthwaite, Thornthwaite-Camargo e
  Hargreaves-Samani corrigido) ainda dependem de colunas historicas da
  planilha e nao sao recalculados por `compute-eto`.
