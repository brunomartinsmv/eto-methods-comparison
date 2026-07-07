# docs

**PT**
Documentacao academica do projeto. Use `methodology.md` como referencia principal para metodos, `reproducibility.md` para o passo a passo e `teaching_checklist.md` como guia rapido de estudo.

**EN**
Academic documentation. Use `methodology.md` for methods, `reproducibility.md` for reproducibility steps, and `teaching_checklist.md` as a quick study guide.

## Mapa rapido / Quick map

- [`methodology.md`](methodology.md): equacoes, requisitos de dados, recomendacao climatica e limitacoes dos metodos de ETo.
- [`reproducibility.md`](reproducibility.md): ambiente, instalacao, comandos de reproducao, checagens e saidas esperadas.
- [`data_provenance.md`](data_provenance.md): origem e rastreabilidade dos dados usados no estudo.
- [`roadmap_raw_to_eto.md`](roadmap_raw_to_eto.md): plano tecnico para migrar de colunas ETo pre-calculadas para calculo a partir de variaveis meteorologicas.
- [`future_scope.md`](future_scope.md): escopo futuro, limitacoes conhecidas e analises adiadas.
- [`sensitivity_analysis.md`](sensitivity_analysis.md): analise opcional OAT para resposta da ET0 a perturbacoes meteorologicas.
- [`legacy.md`](legacy.md): diferenca entre outputs historicos e resultados atuais do pipeline.
- [`teaching_checklist.md`](teaching_checklist.md): roteiro curto para estudantes e leitores que estao aprendendo ETo.

## Leitura recomendada para revisores / Recommended reviewer path

1. Leia o resumo e a secao "How to Cite" no [`../README.md`](../README.md).
2. Rode `python -m scripts.cli all --year 2024` seguindo [`reproducibility.md`](reproducibility.md).
3. Confira `outputs/tables/summary_rankings.csv` e `outputs/reports/summary_rankings.md`.
4. Use [`methodology.md`](methodology.md) para auditar os metodos e suas limitacoes.
5. Use [`data_provenance.md`](data_provenance.md) e `outputs/reports/*_data_quality.csv` para auditar dados.
