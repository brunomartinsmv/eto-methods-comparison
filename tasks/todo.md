# Pipeline backlog

## Completed

- [x] Scientific regression tests for ET0 methods (`tests/test_scientific_regression.py`)
- [x] Composite ranking for ET0 summaries (`summarize --ranking composite`)
- [x] Improved supplemental export package (`export-supplement` with reports, figures, checksums)
- [x] README reflects configurable ET0 workflow
- [x] Future scope documentation (`docs/future_scope.md`)
- [x] Flexible site readers via `reader` blocks in `configs/sites.yml`
- [x] Pre-calculation diagnostics (`inspect`)
- [x] Single-site wrapper (`run-site`, alias `run-one`)
- [x] Single-method mode (`run-method`)
- [x] Input synthesis (`inspect` input summary reports)
- [x] Consolidated site reports (`report-site`)
- [x] Global results index (`build-index`)
- [x] Clean older outputs (`clean-outputs`)
- [x] Friendly onboarding workflow (`quickstart`)
- [x] Derived meteorological variables module (`scripts/derived_meteo.py`)
- [x] Configurable pipeline defaults (`configs/pipeline.yml`)
- [x] Cleaning gap limits and long-gap warnings (`clean --max-gap`)

## Deferred

- Expand equation documentation with full LaTeX derivations per method
- Implement Thornthwaite-family methods in Python (currently `precomputed_only`)
- Resolve Garcia-Lopez legacy scale mismatch with spreadsheet baseline
- Packaged GUI / web application distribution
