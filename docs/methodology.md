# Metodologia e Metodos de ETo (PT/EN)

Para uma auditoria das decisoes implementacionais sensiveis, veja tambem [`methodological_assumptions.md`](methodological_assumptions.md). Esse documento explicita como a referencia Penman-Monteith, radiacao liquida, vento, umidade, dias faltantes, interpolacao, calibracao do Hargreaves-Samani corrigido e limitacoes por metodo/localidade sao tratados no pipeline reprodutivel.

Este capitulo apresenta, de forma detalhada, os metodos usados para estimar a evapotranspiracao de referencia (ETo/ET0), incluindo equacoes, hipoteses, requisitos de dados, limitacoes e recomendacao de clima/regiao. As referencias bibliograficas aparecem ao final.

## Escopo configurado dos metodos

O repositorio agora configura 15 metodos alternativos de ET0 e usa Penman-Monteith FAO-56 como referencia. Manaus e Piracicaba sao localidades demonstrativas configuradas em `configs/sites.yml`; o projeto nao esta limitado a essas cidades. Novas localidades podem ser adicionadas por configuracao e por dados de entrada compatíveis.

Nem todo metodo configurado ja e calculado pelo pipeline atual. Para evitar alterar resultados cientificos silenciosamente, os metodos sem coluna calculada nos dados limpos ficam marcados como `configured_not_computed` em `configs/methods.yml`.

| Metodo | Coluna esperada | Status atual |
| --- | --- | --- |
| Camargo | `et_camargo` | computed |
| Hargreaves-Samani | `et_hargreaves_samani` | computed |
| Makkink | `et_makkink` | configured_not_computed |
| McCloud | `et_mccloud` | configured_not_computed |
| Priestley-Taylor | `et_priestley_taylor` | computed |
| Turc | `et_turc` | configured_not_computed |
| Global Radiation | `et_global_radiation` | configured_not_computed |
| Ivanov | `et_ivanov` | configured_not_computed |
| Jensen-Heise | `et_jensen_heise` | configured_not_computed |
| Garcia-Lopez | `et_garcia_lopez` | computed |
| Net Radiation | `et_net_radiation` | configured_not_computed |
| Radiation-Temperature | `et_radiation_temperature` | configured_not_computed |
| Lungeon | `et_lungeon` | configured_not_computed |
| Stephens-Stewart | `et_stephens_stewart` | configured_not_computed |
| Hicks-Hess | `et_hicks_hess` | configured_not_computed |
| Penman-Monteith FAO-56 | `et_penman_monteith` | reference |

Metodos ja presentes antes desta expansao continuam preservados na configuracao quando existem colunas calculadas, incluindo Thornthwaite, Thornthwaite-Camargo e Hargreaves-Samani corrigido.

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
