# Metodologia e Metodos de ETo (PT/EN)

Para uma auditoria das decisoes implementacionais sensiveis, veja tambem [`methodological_assumptions.md`](methodological_assumptions.md). Esse documento explicita como a referencia Penman-Monteith, radiacao liquida, vento, umidade, dias faltantes, interpolacao, calibracao do Hargreaves-Samani corrigido e limitacoes por metodo/localidade sao tratados no pipeline reprodutivel.

Este capitulo apresenta, de forma detalhada, os metodos usados para estimar a evapotranspiracao de referencia (ETo/ET0), incluindo equacoes, hipoteses, requisitos de dados, limitacoes e recomendacao de clima/regiao. As referencias bibliograficas aparecem ao final.

## Escopo configurado dos metodos

O repositorio agora configura 15 metodos alternativos de ET0 e usa Penman-Monteith FAO-56 como referencia. Manaus e Piracicaba sao localidades demonstrativas configuradas em `configs/sites.yml`; o projeto nao esta limitado a essas cidades. Novas localidades podem ser adicionadas por configuracao e por dados de entrada compatíveis.

O comando `compute-eto` calcula os metodos com `status: computed` a partir de variaveis meteorologicas padronizadas em `data/cleaned/` e escreve `outputs/results/{site}_daily_eto.csv`. Metodos com `status: precomputed_only` sao preservados da planilha quando presentes no input limpo. As metricas preferem essas series calculadas quando o arquivo existe; caso contrario, usam as colunas `et_*` pre-calculadas dos dados limpos como fallback historico.

| Metodo | Coluna esperada | Status atual |
| --- | --- | --- |
| Thornthwaite | `et_thornthwaite` | precomputed_only |
| Thornthwaite-Camargo | `et_thornthwaite_camargo` | precomputed_only |
| Hargreaves-Samani corrected | `et_hargreaves_samani_corr` | precomputed_only |
| Camargo | `et_camargo` | computed |
| Hargreaves-Samani | `et_hargreaves_samani` | computed |
| Makkink | `et_makkink` | computed |
| McCloud | `et_mccloud` | computed |
| Priestley-Taylor | `et_priestley_taylor` | computed |
| Turc | `et_turc` | computed |
| Global Radiation | `et_global_radiation` | computed |
| Ivanov | `et_ivanov` | computed |
| Jensen-Heise | `et_jensen_heise` | computed |
| Garcia-Lopez | `et_garcia_lopez` | computed |
| Net Radiation | `et_net_radiation` | computed |
| Radiation-Temperature | `et_radiation_temperature` | computed |
| Lungeon | `et_lungeon` | computed |
| Stephens-Stewart | `et_stephens_stewart` | computed |
| Hicks-Hess | `et_hicks_hess` | computed |
| Penman-Monteith FAO-56 | `et_penman_monteith` | reference |

Metodos `precomputed_only` dependem de colunas historicas da planilha `Evapo.xlsx` e nao sao recalculados pelo pipeline. Thornthwaite e Thornthwaite-Camargo usam desagregacao diaria legada nao documentada no codigo; Hargreaves-Samani corrigido usa coeficientes locais calibrados fora do pipeline (ver `methodological_assumptions.md`). O comando `compute-eto --include-precomputed` registra comparacoes automaticas entre series calculadas e colunas pre-calculadas quando ambas estao disponiveis.

## Metricas de avaliacao

As tabelas em `outputs/tables/{site}_{daily|monthly}_metrics.csv` comparam cada metodo alternativo contra `et_penman_monteith` usando apenas pares finitos metodo-referencia. As metricas reportadas sao:

- `rmse`: raiz do erro quadratico medio, em mm por periodo;
- `mae`: erro absoluto medio, em mm por periodo;
- `mbe`: vies medio, calculado como metodo menos referencia;
- `r`: coeficiente de correlacao de Pearson;
- `r2`: quadrado de `r`;
- `willmott_d`: indice de concordancia de Willmott;
- `c`: coeficiente de confianca, calculado como `r * willmott_d`;
- `classification`: classe de desempenho derivada de `c`.

A classificacao segue estes limiares: `Excellent` para `c > 0.85`; `Very Good` para `0.75 < c <= 0.85`; `Good` para `0.65 < c <= 0.75`; `Average` para `0.60 < c <= 0.65`; `Poor` para `0.50 < c <= 0.60`; `Bad` para `0.40 < c <= 0.50`; e `Very Poor` para `c <= 0.40`. Quando `r`, `d` ou `c` nao podem ser estimados, a classe fica vazia.

## Calibracao local opcional

O comando `calibrate` ajusta coeficientes locais sem substituir silenciosamente os metodos originais. As series originais mantem seus nomes (`et_hargreaves_samani`, `et_turc`, `et_radiation_temperature`); as series calibradas usam nomes separados como `et_hargreaves_samani_calibrated`.

Metodos calibraveis nesta etapa:

- `hargreaves_samani`: coeficiente escalar da equacao Hargreaves-Samani;
- `turc`: coeficiente escalar da equacao Turc, mantendo a correcao de umidade quando disponivel;
- `radiation_temperature`: coeficiente escalar da forma radiacao-temperatura.

A funcao objetivo e `minimize_train_rmse`: o coeficiente e estimado no periodo de treino por minimos quadrados ordinarios para minimizar RMSE contra `et_penman_monteith`. A calibracao usa as variaveis meteorologicas do cleaned input selecionado; quando o input padrao `data/cleaned/{site}_daily.csv` e usado, a referencia `et_penman_monteith` de `outputs/results/{site}_daily_eto.csv` substitui a referencia pre-computada dos dados limpos quando esse arquivo calculado existe, mantendo consistencia com o comando `metrics`. Para cleaned inputs customizados, informe o diretorio de resultados calculados correspondente com `--results-input`; nesse modo, `{site}_daily_eto.csv` deve existir no diretorio informado. Sem `--results-input`, a referencia vem do proprio cleaned input customizado. A avaliacao e reportada separadamente para treino e teste, com metricas antes/depois (`variant = original` e `variant = calibrated`). Nao se deve interpretar a metrica de treino como desempenho independente.

Uso recomendado:

```bash
python -m scripts.cli calibrate --site manaus --method hargreaves_samani \
  --results-input outputs/results \
  --train-start 2024-01-01 --train-end 2024-06-30 \
  --test-start 2024-07-01 --test-end 2024-12-31
```

Se as quatro datas nao forem informadas, o comando usa um split temporal deterministico 70/30 com os primeiros 70% dos dias para treino e os dias restantes para teste. Se qualquer data for informada, todas as quatro devem ser fornecidas, e `train-end` deve ser anterior a `test-start`.

Artefatos:

- `outputs/tables/{site}_{method}_calibration_coefficients.csv`: metodo calibrado, metodo base, nome e valor do coeficiente, periodo de treino, periodo de teste, referencia, objetivo e contagens de observacoes;
- `outputs/tables/{site}_{method}_calibration_metrics.csv`: impacto nas metricas em treino e teste, antes e depois da calibracao.

Esses coeficientes sao locais e nao devem ser transferidos para outras localidades ou periodos sem nova validacao independente.

## 1. Penman-Monteith (FAO-56)

**PT — Descricao**
O metodo Penman-Monteith, padronizado pela FAO-56, combina balanço de energia e transporte de massa, sendo o metodo de referencia para ETo. Ele integra radiação, temperatura, umidade e vento para estimar a demanda atmosferica por evapotranspiracao. A equacao pode ser lida como a soma de dois mecanismos: (i) o termo radiativo, que expressa a energia disponivel na superficie (Rn - G), e (ii) o termo aerodinamico, que expressa a eficiencia com que a atmosfera remove vapor (função de vento e deficit de pressao de vapor). A ponderacao por \u0394 e \u03b3 representa o acoplamento entre processos energeticos e aerodinamicos.

**Equacao (FAO-56)**

$$\mathrm{ETo} = \frac{0.408\,\Delta\,(R_n - G) + \gamma\,\frac{900}{T + 273}\,u_2\,(e_s - e_a)}{\Delta + \gamma\,(1 + 0.34\,u_2)}$$

**Requisitos de dados**
Radiação liquida, temperatura media, umidade (ou pressão de vapor) e velocidade do vento. Necessita dados mais completos, mas oferece maior robustez fisica.

**Clima/regiao recomendada**
Aplicavel em praticamente todos os climas quando os dados estao disponiveis. Em climas tropicais umidos (ex.: Amazonia) e subtropicais com estacao seca (ex.: interior de SP), tende a capturar bem a variabilidade diaria da ETo. E o metodo recomendado em estudos comparativos e para calibracao de metodos simplificados.

**Limitacoes**
Sensivel a erros de medicao em radiacao e vento. Exige mais variaveis de entrada do que metodos empiricos.

---

## 2. Thornthwaite

**PT — Descricao**
Metodo empirico baseado apenas na temperatura media mensal e no fotoperiodo. Foi desenvolvido para climas temperados, com boa performance quando a disponibilidade de energia esta relacionada principalmente a temperatura.

**Equacao**

$$\mathrm{ETo} = 16\left(\frac{10T}{I}\right)^a \cdot \frac{N}{12} \cdot \frac{N_d}{30}$$

**Requisitos de dados**
Temperatura media mensal e latitude (para fotoperiodo).

**Clima/regiao recomendada**
Climas temperados ou subtropicais com sazonalidade clara (ex.: Sul/Sudeste do Brasil). Pode subestimar em climas tropicais muito umidos (ex.: Amazonia), onde radiacao e umidade exercem papel dominante.

**Limitacoes**
Nao considera vento, umidade e radiacao, podendo gerar vies significativo em regioes de clima umido ou semi-arido.

---

## 3. Camargo

**PT — Descricao**
Metodo brasileiro derivado de Thornthwaite, com ajustes empiricos para climas tropicais. Busca reduzir a subestimativa comum do Thornthwaite em regioes equatoriais.

**Requisitos de dados**
Temperatura media e latitude (similar ao Thornthwaite), com coeficientes empiricos ajustados.

**Referencia**
Metodo originalmente proposto por Camargo (1971) na literatura brasileira. A referencia original nao esta amplamente disponivel em formato digital; quando necessario, cite fontes secundarias que descrevem o metodo e explicite a limitacao.

**Clima/regiao recomendada**
Regioes tropicais e equatoriais do Brasil, com alta umidade e pequena amplitude termica (ex.: Amazonia). Em regioes semi-aridas, tende a apresentar vies por subrepresentar o controle radiativo e aerodinamico.

**Limitacoes**
Continua fortemente dependente da temperatura, podendo falhar em locais com variabilidade radiativa significativa.

---

## 4. Thornthwaite-Camargo

**PT — Descricao**
Metodo hibrido que combina o racional de Thornthwaite com os ajustes do Camargo, tentando equilibrar desempenho em diferentes climas brasileiros.

**Requisitos de dados**
Temperatura media e latitude.

**Clima/regiao recomendada**
Regioes de transicao (subtropical-tropical), como partes do Sudeste e Centro-Oeste. Em geral, apresenta desempenho intermediario entre Thornthwaite e Camargo.

**Limitacoes**
Ainda limitado pela dependencia exclusiva da temperatura.

---

## 5. Hargreaves & Samani (original)

**PT — Descricao**
Metodo semi-empirico que usa temperatura minima e maxima como proxy de radiacao. Popular por exigir poucos dados e apresentar desempenho razoavel em climas secos.

**Equacao**

$$\mathrm{ETo} = 0.0023\,R_a\,(T_{max} - T_{min})^{0.5}\,(T_{mean} + 17.8)$$

**Requisitos de dados**
Temperatura maxima, minima e media; radiacao extraterrestre (calculada via latitude e dia do ano).

**Clima/regiao recomendada**
Climas aridos e semi-aridos (ex.: interior do Nordeste), onde a amplitude termica diaria e um bom proxy da radiacao. Em climas umidos, tende a superestimar ou gerar vies.

**Limitacoes**
Nao considera umidade e vento, podendo degradar em regioes umidas.

---

## 6. Hargreaves & Samani (corrigido)

**PT — Descricao**
Versao ajustada do metodo original, com coeficientes calibrados para reduzir vies local. Essa correcao pode aumentar a acuracia em climas especificos.

**Clima/regiao recomendada**
Regioes onde ha calibracao local (ex.: Piracicaba). Em geral, a calibracao torna o metodo mais robusto para a localidade estudada, mas perde transferibilidade para outras regioes.

**Limitacoes**
A validade e local: coeficientes calibrados podem nao ser transferiveis.

---

## 7. Priestley-Taylor

**PT — Descricao**
Metodo semi-empirico baseado no balanço de energia, assumindo que a superficie e bem irrigada. Simplifica a equacao de Penman-Monteith usando um coeficiente alfa.

**Equacao**

$$\mathrm{ETo} = \alpha\,\frac{\Delta}{\Delta + \gamma}\,\frac{R_n}{\lambda}$$

**Requisitos de dados**
Radiação liquida e temperatura (para \(\Delta\)); geralmente menos variaveis que Penman-Monteith.

**Clima/regiao recomendada**
Climas umidos e superficies bem irrigadas (ex.: Amazonia e areas irrigadas do Sudeste). Em climas tropicais umidos, frequentemente apresenta bom desempenho.

**Limitacoes**
Pode subestimar em climas secos ou quando a superficie nao esta em condicoes de energia limitada.

---

# EN Summary (Short)
For English readers, the methods above are the same. The key idea is that **Penman-Monteith (FAO-56)** is the reference standard, **Thornthwaite/Camargo** rely mostly on temperature, **Hargreaves-Samani** uses temperature range as a proxy for radiation, and **Priestley-Taylor** is energy-balance based with a simplifying coefficient. Each method’s suitability depends on climate and data availability.

---

# Como interpretar Diagramas de Taylor (PT/EN)

**PT**
Use os diagramas em `outputs/figures/<site>/<site>_daily_taylor.png` e `<site>_monthly_taylor.png`. Leituras essenciais:
- O ponto de referencia (Penman-Monteith) fica no eixo horizontal, com desvio padrao igual ao do metodo de referencia.
- O angulo representa a correlacao: quanto mais proximo de 1, mais alinhado ao referencia.
- O raio representa o desvio padrao: quanto mais proximo do raio do referencia, mais similar a variabilidade.
- Pontos mais proximos do ponto de referencia indicam melhor desempenho global.
- Compare diario vs mensal para ver se o metodo melhora quando agregamos a escala temporal.

**EN**
Use the diagrams in `outputs/figures/<site>/<site>_daily_taylor.png` and `<site>_monthly_taylor.png`. Key readings:
- The reference point (Penman-Monteith) sits on the x-axis with its standard deviation as radius.
- The angle encodes correlation: closer to 1 is better.
- The radius encodes standard deviation: closer to the reference radius means similar variability.
- Points closer to the reference indicate better overall agreement.
- Compare daily vs monthly to see if performance improves with temporal aggregation.

---

# Referencias / References
- Allen, R. G., Pereira, L. S., Raes, D., & Smith, M. (1998). *Crop Evapotranspiration — Guidelines for computing crop water requirements* (FAO Irrigation and Drainage Paper No. 56). FAO.
- Thornthwaite, C. W. (1948). An approach toward a rational classification of climate. *Geographical Review*.
- Hargreaves, G. H., & Samani, Z. A. (1985). Reference crop evapotranspiration from temperature. *Applied Engineering in Agriculture*.
- Priestley, C. H. B., & Taylor, R. J. (1972). On the assessment of surface heat flux and evaporation using large-scale parameters. *Monthly Weather Review*.
