# Future scope and deferred analyses

This document records planned improvements, known limitations, and analyses intentionally
deferred from the current reproducible pipeline.

## Implemented in the UX layer (CLI)

- `inspect`: pre-flight feasibility report for which ET0 methods can be computed from available data.
- `run-site`: single-site wrapper over the core pipeline steps.
- `run-method`: compute one ET0 method plus the Penman-Monteith reference.
- `quickstart`: full pipeline (`analysis` + reports + supplement + `outputs/index.html`).
- `report-site` and `build-index`: consolidated Markdown/HTML reports.
- `clean-outputs`: remove regenerable artifacts under `outputs/`.
- Flexible site readers via optional `reader` blocks in `configs/sites.yml`.

## Still deferred or partial

### Precomputed-only legacy methods

Thornthwaite, Thornthwaite-Camargo, and locally corrected Hargreaves-Samani remain
`precomputed_only`. They depend on spreadsheet columns in `Evapo.xlsx` and are not
recalculated by `compute-eto`. Daily disaggregation for Thornthwaite-family methods is
not documented in code.

### Garcia-Lopez scale divergence

Pipeline-computed Garcia-Lopez values differ greatly from the legacy spreadsheet column.
See `docs/roadmap_raw_to_eto.md` and `tests/test_precomputed_regression.py`.

### Thornthwaite implementation in Python

A documented Python implementation of Thornthwaite and Thornthwaite-Camargo with
photoperiod correction is deferred until the legacy disaggregation rule is audited.

### Interactive GUI / web application

The repository remains a CLI research compendium. A packaged desktop or web UI is out of
scope unless a separate distribution layer is added.

### Autocorrelated uncertainty

Bootstrap confidence intervals resample paired days but do not model temporal
autocorrelation explicitly.

### Multi-year and cross-site synthesis

The default workflow targets one analysis year per run. Cross-year pooling and formal
multicity meta-analysis are not automated.

### ERA5 ingestion inside this repository

ERA5 download remains in the companion `era5-daily-statistics-data-download` repository.
This project accepts ERA5-derived CSVs through the generic reader configuration.

## Recommended next steps

1. Implement Thornthwaite-family methods with cited equations and regression fixtures.
2. Resolve or document the Garcia-Lopez unit/scale mismatch with the legacy spreadsheet.
3. Add optional cross-validation for calibration beyond temporal train/test splits.
4. Publish a Zenodo release when preprint-linked outputs stabilize.
