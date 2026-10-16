# Derivações LaTeX por método de ET₀

Cada seção segue a estrutura: **base física → derivação → equação final → coeficientes padrão → implementação**.

Status dos métodos conforme `configs/methods.yml`:

| Status | Significado |
| --- | --- |
| `reference` | referência FAO-56; calculado em `scripts/fao56.py` |
| `computed` | calculado em `scripts/eto_methods.py` via `compute-eto` |
| `precomputed_only` | coluna legada de `Evapo.xlsx`; fórmula documentada mas não auditada no código Python |

---

## 1. Penman-Monteith FAO-56 (`reference`)

**Implementação:** `scripts/fao56.py` → `penman_monteith_fao56`

### Base física

O método combina o balanço de energia na superfície de referência (grama bem irrigada, altura 0,12 m) com a teoria de transferência de vapor de Penman.

### Balanço de energia

$$R_n - G = \lambda E + H$$

onde \(E\) é a evapotranspiração (kg m⁻² s⁻¹), \(H\) o fluxo sensível e \(G\) o fluxo no solo (frequentemente \(G \approx 0\) em escala diária).

### Equação de Penman combinada

Penman (1948) combina os termos radiativo e aerodinâmico:

$$\lambda E = \frac{\Delta(R_n - G) + \rho\,c_p\,\frac{VPD}{r_a}}{\Delta + \gamma\left(1 + \frac{r_s}{r_a}\right)}$$

Para superfície de referência FAO-56, a resistência de superfície \(r_s\) é incorporada nos coeficientes empíricos do termo aerodinâmico.

### Forma FAO-56 (eq. 6) usada no pipeline

Convertendo para unidades diárias (mm d⁻¹) e vento \(u_2\) em m s⁻¹:

$$\mathrm{ET_0} = \frac{0{,}408\,\Delta\,(R_n - G) + \gamma\,\dfrac{900}{T + 273}\,u_2\,(e_s - e_a)}{\Delta + \gamma\,(1 + 0{,}34\,u_2)}$$

### Derivação do termo aerodinâmico

O numerador aerodinâmico surge de:

$$\frac{\rho\,c_p}{\lambda}\,\frac{(e_s - e_a)}{r_a}$$

com \(900/(T+273)\) absorvendo densidade do ar, calor específico e conversão de unidades para obter mm d⁻¹ quando \(e_s - e_a\) está em kPa.

### Variáveis derivadas necessárias

\(e_s\), \(e_a\), \(\Delta\), \(\gamma\), \(u_2\) — ver [`derived_meteorology.md`](derived_meteorology.md).

---

## 2. Thornthwaite (`precomputed_only`)

**Coluna:** `et_thornthwaite` — série legada da planilha; **não recalculada** pelo pipeline.

### Base física

Thornthwaite (1948) relaciona evapotranspiração potencial mensal ao índice de calor \(I\), proxy da energia térmica acumulada, e ao fotoperíodo.

### Índice de calor anual

Para cada mês \(m\) com temperatura média \(T_m > 0\) °C:

$$I = \sum_{m=1}^{12}\left(\frac{T_m}{5}\right)^{1{,}514}$$

### Expoente empírico

$$a = \frac{6I}{5} + 1{,}3$$

### Evapotranspiração mensal

$$\mathrm{ET_m} = 16\left(\frac{10\,T_m}{I}\right)^a$$

### Desagregação diária (legado)

A planilha `Evapo.xlsx` aplica ajuste por fotoperíodo \(N\) (horas de luz médias do mês) e número de dias \(N_d\):

$$\mathrm{ET_0}_{dia} = \mathrm{ET_m} \cdot \frac{N}{12} \cdot \frac{N_d}{30}$$

**Nota:** a regra exata de desagregação diária não está implementada em Python; ver [`../future_scope.md`](../future_scope.md).

---

## 3. Camargo (`computed`)

**Implementação:** `scripts/eto_methods.py` → `camargo`

### Base física

Camargo (1971) propôs ajustes empíricos ao Thornthwaite para climas tropicais brasileiros, incorporando radiação extraterrestre como proxy de energia disponível.

### Forma implementada no pipeline

O código atual usa uma forma simplificada com radiação extraterrestre \(R_a\) e temperatura média:

$$\mathrm{ET_0} = c \cdot \frac{R_a}{\lambda} \cdot T_{mean}$$

com \(c = 0{,}01\) (padrão) e \(\lambda = 2{,}45\) MJ kg⁻¹.

### Derivação a partir da conversão energética

Substituindo \(R_{a,\mathrm{mm}} = R_a / \lambda\):

$$\mathrm{ET_0} = c \cdot R_{a,\mathrm{mm}} \cdot T_{mean}$$

### Variante legada

Uma forma exploratória antiga, fora do pipeline, usa:

$$\mathrm{ET_{CAM,legado}} = K \cdot R_s \cdot (T_{mean} + 20), \qquad K = 0{,}01$$

Essa variante usa radiação global \(R_s\) e deslocamento térmico +20 °C. **O pipeline oficial não implementa essa forma**; use a equação acima para reproduzir `compute-eto`.

---

## 4. Thornthwaite-Camargo (`precomputed_only`)

**Coluna:** `et_thornthwaite_camargo` — série legada; **não recalculada** pelo pipeline.

### Base física

Combina a evapotranspiração mensal Thornthwaite com correção de fotoperíodo de Camargo.

### Equação mensal (legado)

$$\mathrm{ET_{m,THC}} = \mathrm{ET_{m,Thorn}} \cdot \frac{N}{12}$$

onde \(N\) é o fotoperíodo médio mensal (horas de luz).

### Desagregação diária (legado)

Como no Thornthwaite puro, aplica-se também o fator de dias:

$$\mathrm{ET_0}_{dia} = \mathrm{ET_{m,THC}} \cdot \frac{N_d}{30}$$

**Nota:** implementação Python pendente; ver [`../future_scope.md`](../future_scope.md).

---

## 5. Hargreaves-Samani (`computed`)

**Implementação:** `scripts/eto_methods.py` → `hargreaves_samani`

### Base física

Hargreaves & Samani (1985) aproximam a radiação de onda curta a partir da amplitude térmica diária e da temperatura média, combinando com \(R_a\) para estimar ET₀ em regiões sem medição de radiação.

### Derivação

1. A radiação de onda curta é proporcional à amplitude térmica: \(R_s \propto (T_{max} - T_{min})^{0{,}5}\).
2. A demanda evaporativa cresce com a temperatura média: fator \((T_{mean} + 17{,}8)\).
3. A radiação extraterrestre \(R_a\) normaliza a latitude e a época do ano.

### Equação final

$$\mathrm{ET_0} = c \cdot \frac{R_a}{\lambda} \cdot (T_{max} - T_{min})^{0{,}5} \cdot (T_{mean} + 17{,}8)$$

com \(c = 0{,}0023\) e expoente \(0{,}5\) (padrão publicado). O código aplica \(\max(T_{max} - T_{min},\, 0)\) antes da potência. Com `calibrate --free-exponent`, o expoente pode ser estimado no período de treino junto com \(c\); o padrão publicado permanece quando a opção é omitida. O ajuste não embute um expoente regional nem coeficientes de outra região. Um RMSE de teste menor contra o Penman-Monteith calculado não é validação em lisímetro.

---

## 6. Hargreaves-Samani corrigido (`precomputed_only`)

**Coluna:** `et_hargreaves_samani_corr` — coeficientes calibrados localmente fora do pipeline.

### Equação base

Mesma forma do Hargreaves-Samani original, com coeficiente \(c_{local}\) ajustado para reduzir viés em relação à referência local:

$$\mathrm{ET_0} = c_{local} \cdot \frac{R_a}{\lambda} \cdot (T_{max} - T_{min})^{0{,}5} \cdot (T_{mean} + 17{,}8)$$

### Calibração

O valor de \(c_{local}\) provém da planilha legada e não é refitado pelo comando `calibrate` (que opera sobre `et_hargreaves_samani`, não sobre a coluna corrigida). Ver [`../methodological_assumptions.md`](../methodological_assumptions.md).

---

## 7. Priestley-Taylor (`computed`)

**Implementação:** `scripts/eto_methods.py` → `priestley_taylor`

### Base física

Priestley & Taylor (1972) assumem que, em superfícies extensas e bem irrigadas, o termo aerodinâmico é uma fração constante do termo radiativo, introduzindo o coeficiente \(\alpha\).

### Derivação a partir de Penman

Partindo da equação de Penman e assumindo que o transporte aerodinâmico é proporcional ao termo radiativo com fator \(\alpha - \Delta/(\Delta + \gamma)\):

$$\mathrm{ET_0} = \alpha \cdot \frac{\Delta}{\Delta + \gamma} \cdot \frac{R_n - G}{\lambda}$$

### Equivalência de notação

Com \(\lambda = 2{,}45\) MJ kg⁻¹:

$$\frac{R_n - G}{\lambda} = (R_n - G)_{\mathrm{mm}}$$

Logo a forma em `docs/methodology.md`:

$$\mathrm{ET_0} = \alpha\,\frac{\Delta}{\Delta + \gamma}\,\frac{R_n}{\lambda}$$

é equivalente à implementação com \((R_n - G)_{\mathrm{mm}}\), com \(\alpha = 1{,}26\) (padrão) e \(G = 0\).

---

## 8. Garcia-Lopez (`computed`)

**Implementação:** `scripts/eto_methods.py` → `garcia_lopez`

### Base física

Método empírico que combina temperatura, umidade relativa, vento e radiação global em forma multiplicativa.

### Equação final

$$\mathrm{ET_0} = c \cdot (T_{mean} + 21) \cdot \left(1 - \frac{RH}{100}\right) \cdot (1 + u_2) \cdot \frac{R_s}{\lambda}$$

com \(c = 0{,}01\) (padrão).

### Derivação (forma empírica)

1. \((T_{mean} + 21)\): demanda térmica deslocada.
2. \((1 - RH/100)\): déficit de umidade como fator limitante inverso à saturação.
3. \((1 + u_2)\): reforço aerodinâmico linear com vento a 2 m.
4. \(R_{s,\mathrm{mm}} = R_s/\lambda\): energia radiativa disponível.

### Nota sobre escala legada

Valores computados diferem amplamente da coluna pré-calculada em `Evapo.xlsx`; ver `tests/test_precomputed_regression.py` e [`../future_scope.md`](../future_scope.md).

---

## 9. Makkink (`computed`)

**Implementação:** `scripts/eto_methods.py` → `makkink`

### Base física

Makkink (1957) propõe uma forma semelhante a Priestley-Taylor, mas usando radiação global \(R_s\) em vez de \(R_n\), com coeficiente e intercepto empíricos para medições de bacia.

### Derivação

Partindo da fração radiativa \(\Delta/(\Delta + \gamma)\) de Penman e substituindo \(R_n\) por \(R_s\):

$$\mathrm{ET_0} = c \cdot \frac{\Delta}{\Delta + \gamma} \cdot \frac{R_s}{\lambda} + b$$

### Equação final

$$\mathrm{ET_0} = 0{,}61 \cdot \frac{\Delta}{\Delta + \gamma} \cdot R_{s,\mathrm{mm}} - 0{,}12$$

com \(c = 0{,}61\) e intercepto \(b = -0{,}12\) mm d⁻¹ (padrões do código).

---

## 10. McCloud (`computed`)

**Implementação:** `scripts/eto_methods.py` → `mccloud`

### Base física

Relação empírica exponencial entre a temperatura média diária e ET₀.

### Equação final

$$\mathrm{ET_0} = c \cdot W^{p T_{mean}}$$

com \(c = 0{,}254\), \(W = 1{,}07\) e \(p = 1{,}8\) (padrões); \(T_{mean}\) é a temperatura média diária em °C e a saída é mm d⁻¹. Esta forma diária corresponde à equação publicada em [Evaluation of Five Equations for Short-Term Reference Evapotranspiration Forecasting](https://www.mdpi.com/2073-4441/14/18/2888).

### Derivação

Forma empírica sem base física completa. A base e o expoente parametrizam a resposta diária à temperatura; a fórmula não eleva a própria temperatura à potência.

---

## 11. Turc (`computed`)

**Implementação:** `scripts/eto_methods.py` → `turc`

### Base física

Turc (1961) relaciona ET₀ à radiação global e temperatura média, com correção para ar seco.

### Equação principal

$$\mathrm{ET_0} = c \cdot \frac{T_{mean}}{T_{mean} + 15} \cdot \left(R_{s,\mathrm{cal}} + 50\right)$$

com \(c = 0{,}013\) e \(R_{s,\mathrm{cal}} = R_s \times 23{,}9006\) (cal cm⁻² d⁻¹).

### Derivação

1. O fator \(T/(T+15)\) limita a resposta em temperaturas baixas.
2. O termo \((R_{s,\mathrm{cal}} + 50)\) assegura um piso radiativo empírico.
3. A conversão MJ → cal segue o fator documentado em [`derived_meteorology.md`](derived_meteorology.md).

### Correção de umidade (ar seco)

Quando \(RH_{mean} < 50\%\):

$$\mathrm{ET_0} \leftarrow \mathrm{ET_0} \cdot \left(1 + \frac{50 - RH_{mean}}{70}\right)$$

---

## 12. Global Radiation (`computed`)

**Implementação:** `scripts/eto_methods.py` → `global_radiation`

### Base física

Aproximação linear entre ET₀ e radiação global — assume fração constante da energia radiativa convertida em evapotranspiração.

### Equação final

$$\mathrm{ET_0} = c \cdot \frac{R_s}{\lambda}, \qquad c = 0{,}53$$

### Derivação

A partir do balanço energético simplificado \(\mathrm{ET} \approx f \cdot R_s\), com \(f\) adimensional calibrado empiricamente.

---

## 13. Ivanov (`computed`)

**Implementação:** `scripts/eto_methods.py` → `ivanov`

### Base física

Método empírico russo que combina temperatura e déficit de umidade.

### Equação final

$$\mathrm{ET_0} = c \cdot (T_{mean} + 25)^2 \cdot (100 - RH_{mean})$$

com \(c = 0{,}00006\) (padrão diário); \(RH\) em %; saída em mm d⁻¹. O coeficiente mensal \(0{,}0018\) corresponde a cerca de 30 dias e não pode ser aplicado a cada dia; esta implementação usa a forma diária apresentada em [Ivanov-based daily ET0 formulation](https://doi.org/10.1038/s41598-024-60952-4).

### Derivação

1. \((T_{mean}+25)^2\): demanda térmica quadrática.
2. \((100 - RH)\): proxy do déficit de saturação (não normalizado a %).

---

## 14. Jensen-Heise (`computed`)

**Implementação:** `scripts/eto_methods.py` → `jensen_heise`

### Base física

Relaciona ET₀ linearmente à radiação global e ao desvio da temperatura em relação a um limiar.

### Equação final

$$\mathrm{ET_0} = R_{s,\mathrm{mm}} \cdot C_T \cdot (T_{mean} - T_x)$$

com \(C_T = 0{,}025\) e \(T_x = 3\) °C (padrões).

### Derivação

Forma linear em \(T\) condicionada a \(R_s\), com limiar \(T_x\) de atividade evaporativa.

**Nota de implementação:** a função `jensen_heise` em `scripts/eto_methods.py` avalia \((T_{mean} - T_x)\) sem clamp; valores negativos de ET₀ são possíveis quando \(T_{mean} < T_x\). A formula acima descreve a forma empírica, não um truncamento no código.

### Origem de \(C_T = 0{,}025\) e de \(3\) °C

A chave configurada permanece Jensen-Heise (`jensen_heise`, coluna `et_jensen_heise`). O produto calculado permanece

$$\mathrm{ET_0} = 0{,}025\,(T_{mean} - 3)\,\frac{R_s}{\lambda} = (0{,}025\,T_{mean} - 0{,}075)\,\frac{R_s}{\lambda},$$

com \(\lambda = 2{,}45\) MJ kg⁻¹ (`mj_m2_day_to_mm_day`).

Na literatura de Jensen–Haise, \(0{,}025\) é o coeficiente \(C_t\) e \(3\) °C é o módulo de \(T_x = -3\) °C. Xu e Singh (2000) escrevem a relação de Jensen e Haise (1963) como \(\lambda\,\mathrm{ET} = C_t\,(T - T_x)\,R_s\), com \(C_t = 0{,}025\) e \(T_x = -3\) °C. Usta (2022) explicita os mesmos valores no texto: \(C_T = 0{,}025\) e \(T_x = -3\) °C, de modo que \(T - T_x = T + 3\), e coloca ao lado a forma \((0{,}025\,T + 0{,}08)\,R_s/\lambda\). Kim et al. (2024, eq. 5) publicam

$$\mathrm{ET_0} = 0{,}025\,(T + 3)\,\frac{R_s}{\lambda}.$$

Raja et al. (2024, Tabela 2) publicam

$$\mathrm{ET_0} = \frac{R_s}{\lambda}\,(0{,}025\,T_{mean} + 0{,}08).$$

\(0{,}025 \times 3{,}2 = 0{,}08\), logo \(0{,}08\) aproxima \(0{,}025\,(T + 3{,}2)\). Nessas formas a radiação entra como \(R_s/\lambda\), no mesmo lugar que no código. O fator de temperatura do código é \(T_{mean} - (+3)\). Os fatores citados são \(T + 3\) e \(0{,}025\,T + 0{,}08\). As duas famílias de produto diferem, e a chave configurada continua Jensen-Heise. A série numérica continua a do produto configurado.

---

## 15. Net Radiation (`computed`)

**Implementação:** `scripts/eto_methods.py` → `net_radiation`

### Base física

Conversão direta da radiação líquida em evapotranspiração pelo fator 0,408 da FAO-56.

### Equação final

$$\mathrm{ET_0} = c \cdot R_n, \qquad c = 0{,}408$$

### Derivação

Do balanço energético estacionário com termo aerodinâmico desprezível:

$$\mathrm{ET_0} \approx \frac{R_n - G}{\lambda} \approx 0{,}408\,(R_n - G)$$

Com \(G = 0\) e \(R_n\) em MJ m⁻² d⁻¹, o fator 0,408 converte diretamente para mm d⁻¹ (equivalente a \(1/\lambda\)).

---

## 16. Radiation-Temperature (`computed`)

**Implementação:** `scripts/eto_methods.py` → `radiation_temperature`

### Base física

Forma empírica multiplicativa entre radiação global e temperatura deslocada.

### Equação final

$$\mathrm{ET_0} = c \cdot R_{s,\mathrm{mm}} \cdot (T_{mean} + T_0)$$

com \(c = 0{,}01\) e \(T_0 = 15\) °C (padrões).

### Derivação

Produto de dois proxies de energia disponível (radiativa e térmica), calibrado por \(c\).

---

## 17. Lungeon (`computed`)

**Implementação:** `scripts/eto_methods.py` → `lungeon`

### Base física

Semelhante a Ivanov, mas com déficit de umidade normalizado.

### Equação final

$$\mathrm{ET_0} = c \cdot (T_{mean} + 20)^2 \cdot \left(1 - \frac{RH_{mean}}{100}\right)$$

com \(c = 0{,}001\) (padrão).

### Derivação

1. \((T_{mean}+20)^2\): resposta quadrática à temperatura.
2. \((1 - RH/100)\): fração do déficit de saturação relativo.

---

## 18. Stephens-Stewart (`computed`)

**Implementação:** `scripts/eto_methods.py` → `stephens_stewart`

### Base física

Método empírico de radiação-temperatura para regiões temperadas.

### Equação final

$$\mathrm{ET_0} = c \cdot (T_{mean} + T_0) \cdot R_{s,\mathrm{mm}}$$

com \(c = 0{,}01476\) e \(T_0 = 5\) °C (padrões).

### Derivação

Forma bilinear em temperatura e radiação; coeficientes calibrados por Stephens & Stewart para condições de referência específicas.

---

## 19. Hicks-Hess (`computed`)

**Implementação:** `scripts/eto_methods.py` → `hicks_hess`

### Base física

Extensão empírica de formas radiação-temperatura com reforço aerodinâmico por vento.

### Equação final

$$\mathrm{ET_0} = c \cdot R_{s,\mathrm{mm}} \cdot (T_{mean} + 17{,}8) \cdot (1 + u_2)$$

com \(c = 0{,}0055\) (padrão).

### Derivação

1. \((T_{mean} + 17{,}8)\): mesmo deslocamento térmico de Hargreaves-Samani.
2. \((1 + u_2)\): fator aerodinâmico linear (análogo a Garcia-Lopez).
3. \(R_{s,\mathrm{mm}}\): escala radiativa.

---

## 20. FAO-56 PMT (`computed`, fora do ranking padrão)

**Implementação:** `scripts/fao56.py` → `fao56_pmt`

Penman–Monteith FAO-56 (equação 6) com umidade, radiação solar e vento ausentes preenchidos como em Allen et al. (1998), Capítulo 3 e Exemplo 20:

- \(T_{dew} = T_{min}\), logo \(e_a = e^\circ(T_{min})\) e \(e_s = [e^\circ(T_{max}) + e^\circ(T_{min})]/2\);
- \(R_s = 0{,}16 \sqrt{T_{max} - T_{min}}\, R_a\) (interior);
- \(u_2 = 2\) m s⁻¹;
- \(R_n\) é recalculada dessa \(R_s\) (equações 37–39), com \(R_s/R_{so} \le 1\).

O Exemplo 20 (Lyon, julho, \(T_{max} = 26{,}6\) °C, \(T_{min} = 14{,}8\) °C, altitude 200 m, \(R_a = 40{,}55\) MJ m⁻² d⁻¹) publica 4,56 mm d⁻¹. Vento de 1 m s⁻¹ e 3 m s⁻¹ publica 4,2 e 4,8 mm d⁻¹.

A coluna `et_fao56_pmt` é calculada por `compute-eto` e omitida do ranking padrão (`default_ranking: false`).

---

## 21. Valiantzas, temperatura e radiação (`computed`, fora do ranking padrão)

**Implementação:** `scripts/eto_methods.py` → `valiantzas`

Valiantzas (2013a) reduz a equação de Penman a temperatura e radiação solar medida:

$$\mathrm{ET_0} = 0{,}0393\, R_s \sqrt{T + 9{,}5} - 0{,}19\, R_s^{0{,}6}\, |\varphi|^{0{,}15} + 0{,}0061\, (T + 20)\, (1{,}12\, T - T_{min} - 2)^{0{,}7}$$

\(R_s\) fica em MJ m⁻² d⁻¹, \(T\) e \(T_{min}\) em °C, \(\varphi\) é a latitude em radianos e \(\mathrm{ET_0}\) sai em mm d⁻¹. O código usa \(|\varphi|\) para que a potência 0,15 permaneça real no hemisfério sul. Para \(R_s = 15\) MJ m⁻² d⁻¹, \(T = 25\) °C, \(T_{min} = 12\) °C e latitude 40°, a expressão vale 4,289550556627 mm d⁻¹.

A coluna `et_valiantzas` também fica fora do ranking padrão.

---

## Tabela resumo de coeficientes padrão

| Método | Coeficientes padrão no código |
| --- | --- |
| Penman-Monteith | — (fórmula fechada FAO-56) |
| Camargo | \(c = 0{,}01\) |
| Hargreaves-Samani | \(c = 0{,}0023\) |
| Priestley-Taylor | \(\alpha = 1{,}26\), \(G = 0\) |
| Garcia-Lopez | \(c = 0{,}01\) |
| Makkink | \(c = 0{,}61\), \(b = -0{,}12\) |
| McCloud | \(c = 0{,}254\), \(W = 1{,}07\), \(p = 1{,}8\) |
| Turc | \(c = 0{,}013\) |
| Global Radiation | \(c = 0{,}53\) |
| Ivanov | \(c = 0{,}00006\) por dia |
| Jensen-Heise | \(C_T = 0{,}025\), \(T_x = 3\) °C |
| Net Radiation | \(c = 0{,}408\) |
| Radiation-Temperature | \(c = 0{,}01\), \(T_0 = 15\) °C |
| Lungeon | \(c = 0{,}001\) |
| Stephens-Stewart | \(c = 0{,}01476\), \(T_0 = 5\) °C |
| Hicks-Hess | \(c = 0{,}0055\) |
| FAO-56 PMT | \(k_{Rs} = 0{,}16\), \(u_2 = 2\) m s⁻¹, albedo \(0{,}23\) |
| Valiantzas | \(0{,}0393\), \(0{,}19\), \(0{,}0061\); \(R_s\) em MJ m⁻² d⁻¹ |

---

## Referências bibliográficas

- Allen, R. G., Pereira, L. S., Raes, D., & Smith, M. (1998). *Crop Evapotranspiration* (FAO-56).
- Valiantzas, J. D. (2013a). Simple ET0 forms of Penman's equation without wind and/or humidity data. I: Theoretical development. *Journal of Irrigation and Drainage Engineering*, 139(1), 1–8. https://doi.org/10.1061/(ASCE)IR.1943-4774.0000520
- Thornthwaite, C. W. (1948). An approach toward a rational classification of climate. *Geographical Review*.
- Camargo, A. P. (1971). Necessidade de calor para evapotranspiração. Publicações técnicas brasileiras.
- Hargreaves, G. H., & Samani, Z. A. (1985). Reference crop evapotranspiration from temperature. *Applied Engineering in Agriculture*.
- Priestley, C. H. B., & Taylor, R. J. (1972). On the assessment of surface heat flux and evaporation. *Monthly Weather Review*.
- Makkink, G. F. (1957). Testing the Penman formula by means of lysimeters. *Journal of the Institution of Water Engineers*.
- Turc, L. (1961). Evaluation des besoins en eau d'irrigation, évapotranspiration potentielle. *Ann. Agron.*
- Garcia-Lopez, J. (1976). Medición y estimación de la evapotranspiración. *Revista de Agroquímica y Tecnología de Alimentos*.
- Jensen, M. E., & Haise, H. R. (1963). Estimating evapotranspiration from solar radiation. *Journal of the Irrigation and Drainage Division*, 89(IR4), 15–41. https://doi.org/10.1061/JRCEA4.0000287
- Xu, C.-Y., & Singh, V. P. (2000). Evaluation and generalization of radiation-based methods for calculating evaporation. *Hydrological Processes*, 14(2), 339–349. https://doi.org/10.1002/(SICI)1099-1085(20000215)14:2<339::AID-HYP928>3.0.CO;2-O
- Usta, S. (2022). Karadeniz Bölgesi iklim koşullarına uygun Jensen Haise yöntemi referans evapotranspirasyon tahmin eşitliklerinin geliştirilmesi. *Avrupa Bilim ve Teknoloji Dergisi*, (38), 415–427. https://doi.org/10.31590/ejosat.1130701
- Kim, C.-G., Lee, J., Lee, J.-E., & Chung, I.-M. (2024). Calibration and evaluation of alternative methods for reliable estimation of reference evapotranspiration in South Korea. *Water*, 16(17), 2471. https://doi.org/10.3390/w16172471
- Raja, P., Sona, F., Surendran, U., Srinivas, C. V., Kannan, K., Madhu, M., Mahesh, P., Annepu, S. K., Ahmed, M., Chandrasekar, K., Suguna, A. R., Kumar, V., & Jagadesh, M. (2024). Performance evaluation of different empirical models for reference evapotranspiration estimation over Udhagamandalm, The Nilgiris, India. *Scientific Reports*. https://doi.org/10.1038/s41598-024-60952-4
