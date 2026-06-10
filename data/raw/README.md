# data/raw

**PT**
Arquivos originais, sem modificacao. Estes arquivos nao devem ser alterados; qualquer tratamento deve gerar novos arquivos em `data/cleaned/` ou `outputs/`.

**EN**
Original files with no modification. Do not edit these files; any treatment should produce new files in `data/cleaned/` or `outputs/`.

## Arquivos esperados / Expected files

| Arquivo / File | Uso / Use |
| --- | --- |
| `Evapo.xlsx` | Entrada bruta padrao da CLI para Manaus e Piracicaba em 2024. / Default raw CLI input for Manaus and Piracicaba in 2024. |
| `Evapo_2.xlsx` | Arquivo auxiliar/legado com variaveis meteorologicas basicas. / Auxiliary/legacy workbook with basic meteorological variables. |

Checksums SHA-256 dos arquivos versionados:

```text
e3a7841cf56234c70bed9fdcfd1ae3feb3636200968fd9cec62a094139ac4561  Evapo.xlsx
815e5f9a906cc5513c399646323e13a0cec79ae4d2aca0e0340e347fdbbe1e5e  Evapo_2.xlsx
```

## Como reproduzir / How to reproduce
- Fonte primaria: Instituto Nacional de Meteorologia (INMET).
- Portais de acesso: https://portal.inmet.gov.br/dadoshistoricos e https://bdmep.inmet.gov.br/.
- Baixar os dados de 2024 para as estacoes/localidades Manaus, AM, e Piracicaba, SP.
- Salvar aqui mantendo nome, formato e checksum.
- Nao editar arquivos nesta pasta; registre qualquer transformacao em scripts e gere derivados fora de `data/raw/`.

Detalhes completos de proveniencia, variaveis, unidades, transformacoes e lacunas conhecidas estao em [`docs/data_provenance.md`](../../docs/data_provenance.md).
