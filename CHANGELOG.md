# Changelog

All notable changes to this project are documented in this file.

## [Unreleased]

### Added

- Added Pearson correlation (`r`), confidence coefficient (`c = r * d`), and literature performance classes to generated metrics tables.
- Added ranking columns for Pearson `r` and confidence `c` in summary rankings.
- Added configuration metadata for 15 ET0 estimation methods plus Penman-Monteith FAO-56 as the reference.
- Added optional configured-site metadata for biome, climate class, region, country, and state.
- Marked not-yet-implemented method outputs as `configured_not_computed` in `configs/methods.yml`.
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

### Changed

- Updated metrics documentation and generated summaries to report RMSE, MAE, MBE, Pearson `r`, R², Willmott `d`, confidence `c`, and performance classification.
- Clarified that the repository is organized as an open, citable research compendium.
- Clarified that Manaus and Piracicaba are demonstration sites and that additional sites are configurable.
- Updated README installation guidance to match the Python 3.10+ requirement in `pyproject.toml`.
- Expanded `docs/reproducibility.md` with scope, result-checking guidance, CI behavior, and citation instructions.
- Documented methodological assumptions for Penman-Monteith, radiation, wind, humidity, interpolation, calibration, and climate-related limitations.
- Improved calibration consistency by aligning calibration references with the pipeline-computed Penman-- Monteith reference when matching computed ET0 results are available.
- Improved calibration input handling for custom cleaned-data directories and explicit computed-results inputs.

### Fixed

- Fixed calibration reporting so original and calibrated variants are evaluated against the same method form before comparing performance.
- Fixed explicit --results-input handling to fail when the selected site's computed ET0 file is missing instead of silently falling back to cleaned inputs.
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
