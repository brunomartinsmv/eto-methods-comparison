# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Fixed

- Corrected the Zenodo version DOI to `10.5281/zenodo.21327869` (was pointing at an older fisicambiental record).
- Updated the Zenodo publish workflow and script defaults to use deposition ID `21327869`.

### Changed

- Removed the Zenodo concept DOI from citation metadata; cite `10.5281/zenodo.21327869` only.
- Generalized `scripts/publish_zenodo_release.py` to load metadata from `.zenodo.json`, derive publication date and changelog anchors from `CHANGELOG.md`, support `--dry-run` and HTTP timeouts, and fail clearly on download errors.
- Zenodo publish workflow now checks out the release tag and fails early when `ZENODO_ACCESS_TOKEN` is missing.

## [2.0.0] - 2026-07-12

### Added

- Added Pearson correlation (`r`), confidence coefficient (`c = r * d`), and literature performance classes to generated metrics tables.
- Added ranking columns for Pearson `r` and confidence `c` in summary rankings.
- Added configuration metadata for 15 ET0 estimation methods plus Penman-Monteith FAO-56 as the reference.
- Added optional configured-site metadata for biome, climate class, region, country, and state.
- Added `CONTRIBUTING.md` with reproducibility, scientific-change, and pull request expectations.
- Added `CODE_OF_CONDUCT.md` for respectful academic and open-source participation.
- Added README badges for DOI, CI, license, citation metadata, Python version, results, and contact.
- Added reviewer-oriented navigation to `docs/README.md`.
- Added optional PCA analysis for meteorological drivers, including site-level loading tables, explained-variance tables, and PCA biplot figures.
- Added optional one-at-a-time sensitivity analysis for ET0 calculations, with perturbation-based response tables and figures for supported methods.
- Added paired bootstrap confidence intervals for RMSE, MAE, and MBE.
- Added monthly, rainfall-season, and ET0-bin error summaries and figures.
- Added local calibration workflow for selected ET0 methods, including a calibrate CLI command, temporal train/test split support, calibrated output columns, coefficient exports, and calibration metrics exports.
- Added example Manaus calibration outputs for the Hargreaves-Samani method.
- Added `inspect` CLI command with method feasibility and input summary reports.
- Added `run-site`, `run-method`, `quickstart`, `report-site`, `build-index`, and `clean-outputs` CLI commands.
- Added flexible site readers via optional `reader` configuration in `configs/sites.yml`.
- Added consolidated Markdown/HTML site reports and a global results index.
- Added `docs/future_scope.md` documenting deferred analyses and known limitations.
- Added `docs/equations/` with full LaTeX derivations per method and derived meteorological variables.
- Added `scripts/derived_meteo.py` for saturation vapor pressure, psychrometric constant, extraterrestrial radiation, and wind height conversion.
- Added `configs/pipeline.yml` for configurable pipeline defaults (uncertainty, calibration, sensitivity, cleaning).
- Added cleaning gap limits and long-gap warnings (`clean --max-gap`).
- Added safety-net tests, golden table hashes, and reinforced CI reproduction workflow.
- Added scientific regression tests for ET0 methods (`tests/test_scientific_regression.py`).
- Added composite ranking for ET0 summaries (`summarize --ranking composite`).
- Added `AGENTS.md` with Cursor Cloud development instructions.
- Improved `export-supplement` to include reports, figures, checksums, and index files.

### Changed

- Updated metrics documentation and generated summaries to report RMSE, MAE, MBE, Pearson `r`, R², Willmott `d`, confidence `c`, and performance classification.
- Clarified that the repository is organized as an open, citable research compendium.
- Clarified that Manaus and Piracicaba are demonstration sites and that additional sites are configurable.
- Updated README installation guidance to match the Python 3.10+ requirement in `pyproject.toml`.
- Expanded `docs/reproducibility.md` with scope, result-checking guidance, CI behavior, and citation instructions.
- Documented methodological assumptions for Penman-Monteith, radiation, wind, humidity, interpolation, calibration, and climate-related limitations.
- Improved calibration consistency by aligning calibration references with the pipeline-computed Penman-Monteith reference when matching computed ET0 results are available.
- Improved calibration input handling for custom cleaned-data directories and explicit computed-results inputs.
- Marked spreadsheet-dependent method outputs as `precomputed_only` in `configs/methods.yml`.
- Unified ET₀ source across the pipeline; metrics prefer computed ET0 from `outputs/results/{site}_daily_eto.csv`.
- Refactored packaging, CLI conventions, and lazy config loading.

### Fixed

- Fixed `analyze-uncertainty` so unset CLI flags fall back to `configs/pipeline.yml` (matching `clean --max-gap`, `calibrate --train-fraction`, and `sensitivity --perturbations`).
- Corrected stale provenance docs that claimed `--compute-eto` did not calculate ET0.
- Fixed calibration reporting so original and calibrated variants are evaluated against the same method form before comparing performance.
- Fixed explicit `--results-input` handling to fail when the selected site's computed ET0 file is missing instead of silently falling back to cleaned inputs.
- Fixed calibration validation to require finite train/test reference-method pairs before writing metrics.
- Fixed computed-reference merging so non-finite Penman-Monteith values are handled by finite-pair validation rather than being treated as missing date coverage.

## [1.0.2] - 2026-02-11

### Changed

- Pointed the DOI badge to the archived Zenodo version DOI.

## [1.0.1] - 2026-02-11

### Added

- Added the Zenodo concept DOI to the citation block.

## [1.0.0] - 2026-02-11

### Added

- Added a modular Python pipeline with CLI commands under `scripts/`.
- Added daily and monthly Taylor diagram generation.
- Added bilingual methodology documentation and a teaching checklist.

### Changed

- Reorganized the repository structure for academic clarity and reproducibility.
- Standardized output naming conventions.
- Moved historical notebook-era outputs under legacy directories.

[Unreleased]: https://github.com/brunomartinsmv/eto-methods-comparison/compare/v2.0.0...HEAD
[2.0.0]: https://github.com/brunomartinsmv/eto-methods-comparison/compare/v1.0.2...v2.0.0
[1.0.2]: https://github.com/brunomartinsmv/eto-methods-comparison/compare/v1.0.1...v1.0.2
[1.0.1]: https://github.com/brunomartinsmv/eto-methods-comparison/compare/v1.0.0...v1.0.1
[1.0.0]: https://github.com/brunomartinsmv/eto-methods-comparison/releases/tag/v1.0.0
