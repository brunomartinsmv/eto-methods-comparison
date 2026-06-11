# Roadmap: migracao de variaveis meteorologicas brutas para ETo calculada

Este documento registra a issue tecnica da transicao para reduzir a dependencia
de colunas de ETo ja calculadas em `Evapo.xlsx`.

## Objetivo

Permitir que o usuario forneca variaveis meteorologicas brutas ou minimamente
padronizadas, e que o repositorio calcule as series de ETo dos metodos antes de
gerar metricas, tabelas e figuras.

## Estado atual

- O comportamento padrao permanece `--use-precomputed-eto`.
- `scripts.io.read_evapo_sheet` padroniza tanto variaveis meteorologicas quanto
  colunas de ETo ja calculadas.
- `scripts.eto_layers.build_data_layers` separa colunas padronizadas em dados
  meteorologicos brutos, variaveis derivadas, ETo pre-calculada e ETo calculada.
- `--compute-eto` existe como flag preparatoria em `clean`, `validate-data`,
  `all` e `reproduce-paper`, mas interrompe a execucao ate que as formulas sejam
  implementadas e validadas.

## Arquivos ainda dependentes de ETo pre-calculada

- `configs/methods.yml`
- `scripts/config.py`
- `scripts/io.py`
- `scripts/cli.py`
- `scripts/aggregate.py`
- `scripts/metrics.py`
- `scripts/uncertainty.py`
- `scripts/plots.py`
- `scripts/quality.py`
- `scripts/summary.py`
- `tests/*` que constroem DataFrames diretamente com colunas `et_*`

`configs/methods.yml` tambem contem metodos configurados mas ainda nao
calculados no pipeline atual, como Makkink, McCloud, Turc, Ivanov e outros. A
migracao deve distinguir metodos prontos para calculo, metodos apenas
configurados e colunas historicas presentes em planilhas legadas.

## Plano de migracao

1. Definir contrato de entrada meteorologica por metodo.
   - Campos obrigatorios e opcionais por metodo.
   - Unidades canonicas.
   - Tratamento de altitude, latitude, hemisferio, calendario e ano bissexto.

2. Implementar modulo de variaveis derivadas.
   - Radiacao extraterrestre por dia e latitude.
   - Pressao atmosferica e constante psicrometrica por altitude.
   - Pressao de vapor de saturacao e real.
   - Slope da curva de pressao de vapor.
   - Conversao de vento para 2 m quando a altura for conhecida.

3. Implementar formulas de ETo em modulo dedicado.
   - Penman-Monteith FAO-56.
   - Priestley-Taylor.
   - Hargreaves-Samani.
   - Thornthwaite.
   - Camargo e Thornthwaite-Camargo.
   - Garcia Lopez, com fonte bibliografica e coeficientes documentados.
   - Hargreaves-Samani corrigido somente com coeficientes versionados.

4. Criar validadores cientificos.
   - Checagem de unidades e faixas fisicas antes do calculo.
   - Erros claros para insumos insuficientes.
   - Relatorio de quais metodos puderam ser calculados por localidade.

5. Integrar `--compute-eto`.
   - `clean --compute-eto` deve produzir CSV limpo com variaveis meteorologicas,
     derivadas e colunas `et_*` calculadas.
   - `--use-precomputed-eto` deve continuar disponivel para reproduzir o
     baseline historico.
   - Enquanto os dois modos coexistirem, outputs devem registrar o modo usado.

6. Validar contra o baseline legado.
   - Comparar series calculadas contra colunas de `Evapo.xlsx`.
   - Explicar diferencas por formula, unidade, coeficiente ou arredondamento.
   - So alterar resultados versionados depois de registrar justificativa.

7. Atualizar documentacao e testes.
   - Expandir `docs/data_provenance.md` com fontes e formulas.
   - Atualizar `docs/methodological_assumptions.md`.
   - Adicionar testes unitarios por formula com exemplos publicados.
   - Adicionar teste de integracao para `--compute-eto`.

## Criterios de conclusao da migracao

- O pipeline principal calcula ETo a partir de variaveis meteorologicas para as
  localidades analisadas.
- As colunas pre-calculadas deixam de ser exigidas no input principal.
- A reproducao historica continua possivel via modo legado documentado.
- Cada diferenca numerica em relacao aos outputs atuais tem justificativa
  metodologica registrada.
