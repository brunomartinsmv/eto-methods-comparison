# AGENTS.md

## Cursor Cloud specific instructions

This is a self-contained Python CLI research pipeline (`eto-methods-comparison`) that
compares reference evapotranspiration (ET₀) methods against FAO-56 Penman-Monteith.
There are no long-running services, servers, or databases — everything runs as batch
CLI commands via `python -m scripts.cli <command>`.

### Environment
- Python 3.12; dependencies are installed into a virtualenv at `.venv` by the update
  script. Activate it before running anything: `source .venv/bin/activate`.
- Standard commands live in `README.md`, `CONTRIBUTING.md`, and CI
  (`.github/workflows/reproduce.yml`). Prefer those as the source of truth.

### Non-obvious gotchas
- Always set `MPLCONFIGDIR=/tmp/matplotlib-cache` before commands that generate figures
  (`plots`, `all`, `reproduce-paper`), matching CI. Without a writable matplotlib config
  dir, figure generation can warn or fail.
- The `all` / pipeline commands print nothing on success — verify by checking regenerated
  files under `outputs/` and `data/cleaned/` instead of relying on stdout.
- Generated outputs under `outputs/` and `data/cleaned/` are tracked in git. Running the
  pipeline will show them as modified; `git checkout -- outputs/ data/cleaned/` to discard
  incidental regeneration when it is not part of your change.
- The full pipeline requires `data/raw/Evapo.xlsx` (present in the repo). CI skips the
  reproduction step when that file is absent.

### Common commands (run from repo root with `.venv` active)
- Lint: `python -m ruff check .`
- Tests: `python -m pytest`
- Full pipeline: `MPLCONFIGDIR=/tmp/matplotlib-cache python -m scripts.cli all --year 2024`
