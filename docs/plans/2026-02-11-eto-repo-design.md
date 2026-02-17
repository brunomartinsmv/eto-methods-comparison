# Plano de organizacao e pipeline (2026-02-11)

## Objetivo
Reestruturar o repositorio para uso didatico, com separacao clara de dados brutos, dados corrigidos, resultados intermediarios e produtos finais. Criar scripts Python com CLI para reprodutibilidade e documentacao bilingüe.

## Decisoes-chave
- Estrutura padrao cientifica: `data/raw`, `data/cleaned`, `outputs/results`, `outputs/figures`, `outputs/tables`, `scripts`, `notebooks`, `docs`.
- Pipeline modular + CLI.
- Documentacao bilingue (PT/EN), com metodologia extensa em `docs/methodology.md`.
- Notebooks mantidos como guia principal.

## Entregas
- Scripts: `scripts/cli.py` e modulos de leitura, limpeza, agregacao, metricas e graficos.
- READMEs por pasta, com instrucoes curtas de reproducao.
- Metodologia detalhada com referencias.
