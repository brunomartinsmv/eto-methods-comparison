# Equações e derivações LaTeX dos métodos de ET₀

**PT** — Este diretório contém as derivações completas, em notação LaTeX, de todos os métodos configurados em `configs/methods.yml`, além das variáveis meteorológicas derivadas usadas pelo pipeline.

**EN** — This directory holds full LaTeX derivations for every method in `configs/methods.yml`, plus the derived meteorological quantities used by the pipeline.

## Leitura recomendada

1. [`derived_meteorology.md`](derived_meteorology.md) — pressão de vapor, constante psicrométrica, radiação extraterrestre, conversão energia→profundidade e vento a 2 m.
2. [`et0_methods.md`](et0_methods.md) — derivação e equação final de cada um dos 19 métodos, com coeficientes padrão do código e status (`computed`, `reference`, `precomputed_only`).

## Relação com outros documentos

| Documento | Papel |
| --- | --- |
| [`../methodology.md`](../methodology.md) | Visão geral, requisitos de dados, clima e limitações |
| [`../methodological_assumptions.md`](../methodological_assumptions.md) | Decisões implementacionais sensíveis |
| [`../future_scope.md`](../future_scope.md) | Itens adiados (Thornthwaite em Python, escala Garcia-Lopez) |
| `scripts/eto_methods.py`, `scripts/fao56.py` | Implementação numérica canônica |

## Convenções de notação

| Símbolo | Unidade | Significado |
| --- | --- | --- |
| \(T\), \(T_{mean}\) | °C | temperatura média do ar |
| \(T_{min}\), \(T_{max}\) | °C | temperatura mínima e máxima diárias |
| \(R_n\) | MJ m⁻² d⁻¹ | radiação líquida na superfície |
| \(R_s\) | MJ m⁻² d⁻¹ | radiação solar/global de entrada |
| \(R_a\) | MJ m⁻² d⁻¹ | radiação extraterrestre |
| \(G\) | MJ m⁻² d⁻¹ | fluxo de calor no solo |
| \(u_2\) | m s⁻¹ | velocidade do vento a 2 m |
| \(e_s\), \(e_a\) | kPa | pressão de vapor de saturação e atual |
| \(\Delta\) | kPa °C⁻¹ | inclinação da curva de pressão de vapor |
| \(\gamma\) | kPa °C⁻¹ | constante psicrométrica |
| \(\mathrm{ET_0}\) | mm d⁻¹ | evapotranspiração de referência |
| \(\lambda\) | MJ kg⁻¹ | calor latente de vaporização (2,45 MJ kg⁻¹ no pipeline) |

Conversão energia→profundidade usada em quase todos os métodos baseados em radiação:

$$\mathrm{ET_{depth}} = \frac{R_{\mathrm{energy}}}{\lambda}, \qquad \lambda = 2{,}45\ \mathrm{MJ\ kg^{-1}}$$

Implementação: `scripts/conversions.py` (`mj_m2_day_to_mm_day`).
