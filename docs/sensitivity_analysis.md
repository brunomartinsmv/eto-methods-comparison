# OAT sensitivity analysis

**PT**
Este comando adiciona uma analise de sensibilidade local one-at-a-time, OAT, para avaliar como alteracoes isoladas em variaveis meteorologicas afetam a ET0 calculada.

A rotina e opcional e nao substitui as metricas comparativas contra Penman-Monteith. Para cada variavel candidata, o comando recalcula o metodo selecionado com perturbacoes de -50% a +50%, em incrementos de 10%, mantendo as demais variaveis constantes.

Metodos disponiveis:
- `penman_monteith`
- `turc`
- `radiation_temperature`

Variaveis candidatas:
- temperatura media (`tmed_c`)
- temperatura maxima (`tmax_c`)
- temperatura minima (`tmin_c`)
- umidade relativa media (`rh_mean_pct`)
- velocidade media do vento (`wind_mean_ms`)
- radiacao global (`rad_global_mj_m2_d`)
- radiacao liquida (`rad_net_mj_m2_d`)

Uso:
```bash
python -m scripts.cli sensitivity --site manaus --method penman_monteith
python -m scripts.cli sensitivity --site manaus --method turc
python -m scripts.cli sensitivity --site manaus --method radiation_temperature
```

Saidas por localidade e metodo:
- `outputs/tables/{site}_sensitivity_{method}.csv`
- `outputs/figures/{site}/{site}_sensitivity_{method}.png`

A tabela registra a media basal de ET0, a media apos perturbacao, a diferenca absoluta em mm/d e a diferenca relativa percentual. Variaveis candidatas ausentes sao registradas com `status=missing_column` e tambem geram aviso. Se o metodo selecionado nao puder ser calculado por falta de colunas obrigatorias, o comando falha com uma mensagem indicando as colunas faltantes.

Para `penman_monteith`, o mesmo comando tambem escreve coeficientes relativos de sensibilidade, mensais e anuais:

- `outputs/tables/{site}_sensitivity_penman_monteith_relative.csv`

A perturbacao dessa tabela e central, de ±1% (`relative_perturbation_pct` em `configs/pipeline.yml`). Ela nao substitui a varredura de -50% a +50%. O coeficiente diario e

S_x = (ET0(1.01 x) - ET0(0.99 x)) / (0.02 ET0)

e o valor do mes ou do ano e a media desses coeficientes diarios. Um coeficiente 0,5 significa que uma variacao de 1% no fator altera a ET0 em cerca de 0,5%.

Fatores, um de cada vez, com os demais mantidos constantes na equacao diaria:

- temperatura media (`tmed_c`), com o deficit de pressao de vapor mantido no valor basal e a declividade da curva de saturacao recalculada
- deficit de pressao de vapor (`vpd_kpa` = es(Tmed) - ea)
- vento a 2 m (`wind_2m_ms`)
- radiacao liquida (`rad_net_mj_m2_d`), que e o termo de radiacao usado por Penman-Monteith neste pipeline

Manaus e Piracicaba saem em arquivos separados. A ordem entre os fatores e local; a tabela nao ranqueia um sitio contra o outro. Turc e a equacao radiacao-temperatura continuam apenas na varredura de ±50%.

Limitacoes:
- A analise OAT e local e descritiva; ela nao estima incerteza conjunta entre variaveis.
- Perturbacoes percentuais em temperatura sao uma aproximacao numerica para comparar resposta do metodo, nao um cenario meteorologico fisicamente completo.
- Variaveis que nao entram na formula do metodo selecionado podem apresentar resposta nula.
- O coeficiente relativo e uma derivada local. A perturbacao percentual da temperatura em graus Celsius e uma sonda numerica, nao um cenario meteorologico.
- Dias com ET0 nao finita ou igual a zero ficam de fora da media.

**EN**
This optional command runs local one-at-a-time sensitivity analysis for selected ET0 methods. It perturbs one meteorological variable at a time from -50% to +50% in 10% steps, writes a CSV summary, and saves a headless Matplotlib figure.

For Penman-Monteith it also writes `outputs/tables/{site}_sensitivity_penman_monteith_relative.csv`: monthly and annual means of daily relative sensitivity coefficients at a ±1% central difference. The drivers are mean temperature (vapor-pressure deficit held constant), vapor-pressure deficit, 2 m wind, and net radiation. Manaus and Piracicaba are separate files. The ±50% sweep is unchanged.
