# Changelog

All notable changes to this project are documented in this file.

## [Unreleased]

### Added

- Added configuration metadata for 15 ET0 estimation methods plus Penman-Monteith FAO-56 as the reference.
- Marked not-yet-implemented method outputs as `configured_not_computed` in `configs/methods.yml`.
- Added `CONTRIBUTING.md` with reproducibility, scientific-change, and pull request expectations.
- Added `CODE_OF_CONDUCT.md` for respectful academic and open-source participation.
- Added README badges for DOI, CI, license, citation metadata, Python version, results, and contact.
- Added reviewer-oriented navigation to `docs/README.md`.

### Changed

- Clarified that the repository is organized as an open, citable research compendium.
- Clarified that Manaus and Piracicaba are demonstration sites and that additional sites are configurable.
- Updated README installation guidance to match the Python 3.10+ requirement in `pyproject.toml`.
- Expanded `docs/reproducibility.md` with scope, result-checking guidance, CI behavior, and citation instructions.

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
