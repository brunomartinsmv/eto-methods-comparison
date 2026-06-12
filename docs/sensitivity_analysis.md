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

Limitacoes:
- A analise OAT e local e descritiva; ela nao estima incerteza conjunta entre variaveis.
- Perturbacoes percentuais em temperatura sao uma aproximacao numerica para comparar resposta do metodo, nao um cenario meteorologico fisicamente completo.
- Variaveis que nao entram na formula do metodo selecionado podem apresentar resposta nula.

**EN**
This optional command runs local one-at-a-time sensitivity analysis for selected ET0 methods. It perturbs one meteorological variable at a time from -50% to +50% in 10% steps, writes a CSV summary, and saves a headless Matplotlib figure.
