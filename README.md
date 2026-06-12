# Reference Evapotranspiration (ETo) Methods Comparison

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.18615164.svg)](https://doi.org/10.5281/zenodo.18615164)
[![CI](https://github.com/brunomartinsmv/eto-methods-comparison/actions/workflows/reproduce.yml/badge.svg)](https://github.com/brunomartinsmv/eto-methods-comparison/actions/workflows/reproduce.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Cite this repository](https://img.shields.io/badge/citation-CITATION.cff-blue.svg)](CITATION.cff)
[![Python](https://img.shields.io/badge/python-3.10%2B-blue.svg)](pyproject.toml)
[![Results](https://img.shields.io/badge/results-summary_rankings.csv-informational.svg)](outputs/tables/summary_rankings.csv)
[![Contact](https://img.shields.io/badge/contact-GitHub%20Issues-lightgrey.svg)](https://github.com/brunomartinsmv/eto-methods-comparison/issues)

**A reproducible analysis framework for comparing up to 15 empirical and semi-empirical ET0 estimation methods against Penman-Monteith (FAO-56).**

This repository is organized as an open, citable research compendium: it includes source data notes, executable scripts, generated outputs, tests, citation metadata, licensing, contribution guidance, and documentation for reproducing the analysis.

## Key Findings

This repository now configures **15 alternative ET0 methods plus Penman-Monteith FAO-56 as reference**. The current computed demonstration results use the method columns already available for two contrasting Brazilian climates:
- **Piracicaba, SP** (Cwa — humid subtropical with dry winter)
- **Manaus, AM** (Af — tropical rainforest)

Manaus and Piracicaba are demonstration sites, not a fixed multicity study design. Additional sites can be added through `configs/sites.yml` without changing the code structure.

**Main results:**
- Temperature-based methods (Thornthwaite, Camargo) systematically underestimate ETo in both climates, with errors exceeding 30% RMSE
- Priestley-Taylor shows excellent performance in humid Manaus (RMSE < 15%), but moderate performance in Piracicaba
- Hargreaves-Samani (calibrated) achieves best balance across both sites when radiation data is unavailable
- All simplified methods degrade more in Manaus than Piracicaba, highlighting the challenge of tropical humid climates

**→ See [`outputs/tables/summary_rankings.csv`](outputs/tables/summary_rankings.csv) for a ranked comparison across sites and scales (also available as [`outputs/reports/summary_rankings.md`](outputs/reports/summary_rankings.md)).**

Per-method metrics remain in `outputs/tables/{site}_{daily|monthly}_metrics.csv`. After running `compute-eto`, metrics use the pipeline-calculated ET0 series in `outputs/results/{site}_daily_eto.csv`; if those files are absent, the legacy precomputed columns in `data/cleaned/` remain the fallback.

---

## What This Repository Provides

### Ready-to-Use Results (for Demonstration Sites)
Clone and run the pipeline in under 5 minutes to generate:

**📊 Metrics Tables** (`outputs/tables/`)
- `summary_rankings.csv` — All methods ranked by site (Manaus, Piracicaba) and scale (daily, monthly)
- `{site}_daily_metrics.csv` — RMSE, MAE, MBE, Pearson r, R², Willmott d, confidence c, and performance classification for daily estimates
- `{site}_monthly_metrics.csv` — Same metrics aggregated monthly
- **→ Start with `summary_rankings.csv` to see which methods perform best in each climate**

**📈 Figures** (`outputs/figures/{site}/`)
- Taylor diagrams (daily and monthly) — Visual summary of method agreement
- Scatter plots — Method vs Penman-Monteith comparisons
- Time series — Temporal patterns over the year
- Monthly totals — Seasonal ETo accumulation by method

**📁 Intermediate Data** (`data/cleaned/`, `outputs/results/`)
- Cleaned daily time series: `data/cleaned/{site}_daily.csv`
- 7-day rolling means: `outputs/results/{site}_rolling_7d.csv`
- Monthly aggregations: `outputs/results/{site}_monthly_totals.csv`

### Extensible Framework
The pipeline works for **any location** where you have meteorological data:
- Add site metadata to `configs/sites.yml`
- Add compatible data to `data/raw/` or adapt the reader for your source format
- Keep method metadata in `configs/methods.yml`
- Run the same pipeline and get the same output structure for any number of configured sites

---

## Quick Start

### Prerequisites
- **Python 3.10 or higher** (CI uses Python 3.12)
  - Check your version: `python3 --version`
- **pip** for package management
- **Git** for cloning the repository

### Step-by-Step Installation

**1. Clone the repository**
```bash
git clone https://github.com/brunomartinsmv/eto-methods-comparison.git
cd eto-methods-comparison
```

**2. Verify data is present**
```bash
ls data/raw/
# You should see: Evapo.xlsx
```
This file contains the raw meteorological data for Piracicaba and Manaus (2024).

**3. Create a virtual environment** (recommended to avoid dependency conflicts)
```bash
python3 -m venv .venv
```

**4. Activate the virtual environment**
```bash
# On macOS/Linux:
source .venv/bin/activate

# On Windows (Command Prompt):
.venv\Scripts\activate.bat

# On Windows (PowerShell):
.venv\Scripts\Activate.ps1
```
Your prompt should now show `(.venv)` prefix.

**5. Install dependencies**
```bash
pip install --upgrade pip
pip install -r requirements.txt
```
This installs: pandas, numpy, matplotlib, openpyxl, and scientific libraries.

For development and test workflows, install the package with development dependencies:

```bash
pip install -e ".[dev]"
```

**6. Run the complete pipeline**
```bash
python -m scripts.cli all --year 2024
```

The command runs without interactive prompts and updates the generated files in
`data/cleaned/`, `outputs/results/`, `outputs/tables/`, and `outputs/figures/`.

**7. Check your results**
```bash
ls outputs/tables/
# Should show: piracicaba_daily_metrics.csv, piracicaba_monthly_metrics.csv
#              manaus_daily_metrics.csv, manaus_monthly_metrics.csv

ls outputs/figures/piracicaba/
# Should show: multiple .png files (Taylor diagrams, scatter plots, time series)
```

### Output Naming Standard

The current CLI uses snake-case suffixes for generated files:

- Daily cleaned data: `data/cleaned/{site}_daily.csv`
- 7-day rolling results: `outputs/results/{site}_rolling_7d.csv`
- Monthly totals: `outputs/results/{site}_monthly_totals.csv`
- Computed daily ET0 methods: `outputs/results/{site}_daily_eto.csv`
- Daily metrics: `outputs/tables/{site}_daily_metrics.csv`
- Monthly metrics: `outputs/tables/{site}_monthly_metrics.csv`
- Daily scatter figures: `outputs/figures/{site}/{site}_daily_scatter_{method}_vs_pm.png`
- Daily time-series figures: `outputs/figures/{site}/{site}_daily_series_{method}_vs_pm.png`
- Monthly totals figure: `outputs/figures/{site}/{site}_monthly_totals.png`
- Taylor figures: `outputs/figures/{site}/{site}_daily_taylor.png` and `{site}_monthly_taylor.png`
- Data-quality reports: `outputs/reports/{site}_data_quality.csv`
- Method rankings: `outputs/tables/summary_rankings.csv` and `outputs/reports/summary_rankings.md`
- Summary reports: `outputs/reports/summary.csv` and `outputs/reports/summary.md`

Older `rolling7d` files are legacy names. Use `rolling_7d` for current pipeline
outputs.

### Running Individual Steps

If you only need specific outputs:

```bash
python -m scripts.cli clean      # Clean raw data → data/cleaned/
python -m scripts.cli compute-eto --year 2024  # Compute ET0 from cleaned weather variables → outputs/results/
python -m scripts.cli aggregate  # Create aggregations → outputs/results/
python -m scripts.cli metrics    # Compute RMSE, r, R², Willmott d, c, etc. → outputs/tables/ (prefers computed ET0 if available)
python -m scripts.cli plots      # Generate all figures → outputs/figures/
python -m scripts.cli pca        # Optional PCA on meteorological drivers
python -m scripts.cli validate-data  # Audit dates, missing values, interpolation traces
python -m scripts.cli summarize      # Rank methods and summarize best performers by site and scale
python -m scripts.cli reproduce-paper --year 2024  # Regenerate paper-facing outputs
python -m scripts.cli export-supplement             # Collect supplemental CSV outputs
```

`metrics` remains backward compatible: if `outputs/results/{site}_daily_eto.csv`
does not exist, it falls back to `data/cleaned/{site}_daily.csv` and uses the
precomputed `et_*` columns from the cleaned data.

**Expected runtime:** ~30 seconds for full pipeline on both sites (2024 data).

---

### Troubleshooting

**Problem: `ModuleNotFoundError: No module named 'scripts'`**

**Solution:** Make sure you're running from the repository root directory and using `-m` flag:
```bash
cd /path/to/eto-methods-comparison
python -m scripts.cli all --year 2024
```

---

**Problem: `FileNotFoundError: data/raw/Evapo.xlsx not found`**

**Solution:**
- Verify the file exists: `ls data/raw/Evapo.xlsx`
- If missing, the data file may not have been committed to git. Contact the repository maintainer or see "Using Your Own Data" section below.

---

**Problem: `ImportError: openpyxl` or similar import errors**

**Solution:** Reinstall dependencies:
```bash
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall
```

---

**Problem: Virtual environment won't activate on Windows PowerShell**

**Solution:** Enable script execution:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
.venv\Scripts\Activate.ps1
```

---

**Problem: Plots look wrong or metrics are NaN**

**Solution:**
- Check for missing data: `python -c "import pandas as pd; df = pd.read_csv('data/cleaned/piracicaba_daily.csv'); print(df.isnull().sum())"`
- Ensure you're using `--year 2024` (the year with complete data)
- If using your own data, verify all required meteorological variables are present

---

**Problem: `Permission denied` when creating directories**

**Solution:** Check write permissions:
```bash
chmod -R u+w outputs/ data/cleaned/
```

---

**Still having issues?**
- Check Python version: `python3 --version` (must be ≥3.8)
- Try running in a fresh virtual environment
- Open an issue on GitHub with the full error message

---

## Using Your Own Data

The pipeline is designed for **any location** with meteorological data. Here's how to add a new city:

### Required Meteorological Variables

To compute the full configured set of 15 ET0 methods, you generally need daily data for:

**Minimum requirements (for basic methods):**
- Date
- Temperature (mean, min, max)
- Latitude of the site

**For complete analysis (including Penman-Monteith):**
- Net radiation (Rn) or solar radiation
- Wind speed at 2m height (u2)
- Relative humidity or vapor pressure
- Soil heat flux (G) — often assumed as 0 for daily calculations

### Data Sources

**Option 1: INMET (Brazilian stations)**
- Portal: https://portal.inmet.gov.br/
- Navigate to: Dados → Estações → Dados Históricos
- Download automatic station data (CSV format)
- Best for Brazilian locations with high-quality automated measurements

**Option 2: ERA5 Reanalysis (global coverage)**
- Portal: https://cds.climate.copernicus.eu/
- Product: ERA5 hourly/daily data on single levels
- Variables needed: 2m temperature, surface solar radiation, 10m wind, dewpoint
- **Automated download tool:** Use this repository to download and process ERA5 data automatically:
  ```bash
  git clone https://github.com/brunomartinsmv/ear5-daily-statistics-data-download.git
  ```
  Follow the instructions there to get daily statistics for any location globally.
- Best for locations without ground stations or historical gap-filling

### Adding a New Site to the Pipeline

**1. Prepare your data file**
- Format as Excel (.xlsx) with one sheet per site
- Columns must include: date, temperature variables, radiation, wind, humidity
- See `data/raw/Evapo.xlsx` as reference

**2. Edit configuration** (`configs/sites.yml`)

Add your site to the `sites` mapping:
```yaml
sites:
  cuiaba:
    sheet: Cuiaba
    lat: -15.6
    lon: -56.1
    alt_m: 165.0
    biome: Cerrado
    climate_class: Aw
    region: Centro-Oeste
    country: Brazil
    state: MT
```

`biome`, `climate_class`, `region`, `country`, and `state` are optional interpretive metadata. They are useful for summaries and optional grouping, but the project does not require them and does not become a fixed regional or multicity study when they are present.

Method column mappings and short labels live in `configs/methods.yml`.

**3. Run the pipeline**
```bash
python -m scripts.cli all --year 2024
```

To run one configured site:

```bash
python -m scripts.cli all --year 2024 --site manaus
python -m scripts.cli all --year 2024 --site piracicaba
```

The pipeline will automatically:
- Process your new site
- Generate metrics comparing all methods
- Create figures in `outputs/figures/cuiaba/`
- Compute performance tables in `outputs/tables/cuiaba_*.csv`

### Data Format Example

Your Excel sheet should look like:
```
date       | temp_mean | temp_min | temp_max | radiation | wind_2m | rh_mean
2024-01-01 | 25.3      | 19.2     | 32.1     | 22.5      | 1.8     | 68.2
2024-01-02 | 26.1      | 20.0     | 33.5     | 23.1      | 2.1     | 65.5
...
```

**Note:** Column names should match those expected by `scripts/io.py`. Check the existing data structure or modify the reading functions if your format differs.

---

## Repository Structure

```
.
├── data/
│   ├── raw/            # Original meteorological data (Evapo.xlsx)
│   └── cleaned/        # Processed daily time series
├── outputs/
│   ├── results/        # Intermediate aggregations (rolling_7d, monthly totals)
│   ├── figures/        # All generated plots (Taylor diagrams, scatter plots, time series)
│   ├── reports/        # Data quality reports
│   └── tables/         # **Metrics tables (RMSE, r, R², Willmott d, c) ← Start here**
├── scripts/            # Analysis pipeline (CLI, cleaning, metrics, plotting)
├── notebooks/          # Educational Jupyter notebooks with step-by-step explanations
├── docs/               # Detailed methodology, equations, and interpretation guides
└── requirements.txt    # Python dependencies
```

Files under `outputs/**/legacy/` are historical notebook-era outputs, not the
official preprint result set. See [`docs/legacy.md`](docs/legacy.md).

For a documentation map, start with [`docs/README.md`](docs/README.md). For exact reproduction commands, see [`docs/reproducibility.md`](docs/reproducibility.md). For contribution expectations, see [`CONTRIBUTING.md`](CONTRIBUTING.md). Participants are also covered by the project [`CODE_OF_CONDUCT.md`](CODE_OF_CONDUCT.md).

---

## How to Cite

If you use this repository or its outputs in academic work, please cite:

> Vieira, B. M. M. (2026). *Reference Evapotranspiration (ETo) Methods Comparison* (Version 1.0.2) [Software]. Universidade Federal do Mato Grosso. https://doi.org/10.5281/zenodo.18615164

**Version DOI:** https://doi.org/10.5281/zenodo.18615164

**Concept DOI (all versions):** https://doi.org/10.5281/zenodo.18615049

The repository also includes [`CITATION.cff`](CITATION.cff), which GitHub can use to generate citation formats automatically. Add the arXiv DOI to `CITATION.cff` and this section after the preprint is available.

**BibTeX:**
```bibtex
@misc{vieira2026eto,
  author = {Vieira, Bruno Martins M.},
  title = {Reference Evapotranspiration (ETo) Methods Comparison},
  year = {2026},
  version = {1.0.2},
  howpublished = {Software and analysis outputs},
  institution = {Universidade Federal do Mato Grosso},
  doi = {10.5281/zenodo.18615164},
  doi_concept = {10.5281/zenodo.18615049},
  url = {https://github.com/brunomartinsmv/eto-methods-comparison}
}
```

---

## Methods Overview

The repository configuration targets **15 alternative ET0 estimation methods** plus **Penman-Monteith FAO-56** as the reference. The `compute-eto` command calculates those methods from standardized meteorological variables and writes daily calculated series to `outputs/results/{site}_daily_eto.csv`.

**Reference standard:**
- **Penman-Monteith (FAO-56)** — Energy balance + aerodynamic approach, requires full met data

**Computed 15-method comparison scope:** Camargo, Hargreaves-Samani, Makkink, McCloud, Priestley-Taylor, Turc, Global Radiation, Ivanov, Jensen-Heise, Garcia-Lopez, Net Radiation, Radiation-Temperature, Lungeon, Stephens-Stewart, and Hicks-Hess.

The configuration also preserves existing computed legacy/auxiliary method columns: Thornthwaite, Thornthwaite-Camargo, and locally corrected Hargreaves-Samani.

**For detailed equations, assumptions, limitations, and climate suitability of each method, see [`docs/methodology.md`](docs/methodology.md).**

---

## For Students & Learners

**New to ETo estimation?** Start here:

1. **Read the methodology first:** [`docs/methodology.md`](docs/methodology.md) explains each method's physics, equations, and when to use them.

2. **Explore the notebooks:** `notebooks/` contains step-by-step Jupyter notebooks that explain:
   - Why we estimate ETo and what it represents
   - How each method works conceptually
   - How to interpret Taylor diagrams and performance metrics
   - Common pitfalls and climate-specific considerations

3. **Run the pipeline:** Follow the Quick Start above to generate results for Piracicaba and Manaus.

4. **Interpret the results:**
   - Start with `outputs/tables/*_daily_metrics.csv` — these show which methods perform best
   - Check Taylor diagrams in `outputs/figures/{site}/{site}_daily_taylor.png` for visual summary
   - Compare daily vs monthly performance to understand temporal aggregation effects

5. **Experiment:** Try adding a new city using your own data or ERA5 downloads.

---

## References

- Allen, R. G., Pereira, L. S., Raes, D., & Smith, M. (1998). *Crop Evapotranspiration — Guidelines for computing crop water requirements* (FAO Irrigation and Drainage Paper No. 56). FAO.
- Thornthwaite, C. W. (1948). An approach toward a rational classification of climate. *Geographical Review*.
- Hargreaves, G. H., & Samani, Z. A. (1985). Reference crop evapotranspiration from temperature. *Applied Engineering in Agriculture*.
- Priestley, C. H. B., & Taylor, R. J. (1972). On the assessment of surface heat flux and evaporation using large-scale parameters. *Monthly Weather Review*.

For complete references and method-specific citations, see [`docs/methodology.md`](docs/methodology.md).

---

## License

This project is distributed under the MIT License. See [`LICENSE`](LICENSE).

## Contact

For questions, suggestions, or collaboration:
- **Author:** Bruno Martins M. Vieira
- **Institution:** Universidade Federal do Mato Grosso
- **GitHub Issues:** [Report issues or ask questions](https://github.com/brunomartinsmv/eto-methods-comparison/issues)

## Contributing

Contributions that improve reproducibility, documentation, tests, method auditability, or support for additional well-documented sites are welcome. Please read [`CONTRIBUTING.md`](CONTRIBUTING.md) before opening a pull request.
