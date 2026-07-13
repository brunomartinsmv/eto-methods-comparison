# Contributing

Thank you for considering a contribution. This repository is curated as a reproducible scientific companion for a future preprint, so contributions should preserve auditability, data provenance, and scientific interpretation.

## Scope

Useful contributions include:

- fixes to reproducibility, installation, or documentation;
- tests for the scientific pipeline;
- clearer method descriptions, assumptions, or citations;
- improvements to reports, figures, and tables;
- support for additional sites through documented configuration and data provenance.

Please do not replace or edit raw data files without opening an issue first. Raw-data changes need a clear provenance note, source citation, and explanation of how outputs are affected.

## Development setup

Use Python 3.10 or newer from the repository root:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

The historical runtime-only install path also remains supported:

```bash
python -m pip install -r requirements.txt
```

## Reproducing the analysis

```bash
MPLCONFIGDIR=/tmp/matplotlib-cache python -m scripts.cli quickstart --year 2024
```

Generated outputs should go to the existing `outputs/` subdirectories. Do not place current preprint-facing results under `outputs/**/legacy/`.

## Quality checks

Before opening a pull request, run:

```bash
python -m ruff check .
python -m pytest
MPLCONFIGDIR=/tmp/matplotlib-cache python -m scripts.cli quickstart --year 2024
```

If raw data are unavailable in your checkout, note that limitation in the pull request and still run lint and tests.

## Scientific-change expectations

Changes that alter metrics, rankings, figures, or cleaned data should include:

- a short explanation of the scientific reason for the change;
- the affected files under `outputs/`;
- any relevant method or assumption updates in `docs/`;
- tests when the change affects code behavior.

Avoid changing generated outputs only because of formatting, Matplotlib version differences, or floating-point noise unless the change is intentional and documented.

## Pull request checklist

- The purpose and scope are clear.
- Installation and reproduction instructions still work.
- Tests and lint pass, or limitations are explained.
- Scientific outputs are either unchanged or their changes are justified.
- Documentation and citation metadata remain consistent.
- No private credentials, local paths, or unpublished raw data are introduced.

## Reporting problems

Use GitHub Issues for bugs, reproducibility failures, unclear methods, missing citations, or questions about extending the pipeline to another site. Include the command you ran, your Python version, and relevant error output.
