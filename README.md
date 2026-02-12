# Reference Evapotranspiration (ETo) Methods Comparison

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.18615164.svg)](https://doi.org/10.5281/zenodo.18615164)

**A reproducible analysis comparing empirical and semi-empirical ETo estimation methods against Penman-Monteith (FAO-56) for Brazilian climates.**

## Key Findings

This study evaluates 7 ETo methods across two contrasting Brazilian climates:
- **Piracicaba, SP** (Cwa — humid subtropical with dry winter)
- **Manaus, AM** (Af — tropical rainforest)

**Main results:**
- Temperature-based methods (Thornthwaite, Camargo) systematically underestimate ETo in both climates, with errors exceeding 30% RMSE
- Priestley-Taylor shows excellent performance in humid Manaus (RMSE < 15%), but moderate performance in Piracicaba
- Hargreaves-Samani (calibrated) achieves best balance across both sites when radiation data is unavailable
- All simplified methods degrade more in Manaus than Piracicaba, highlighting the challenge of tropical humid climates

**→ See `outputs/tables/*_daily_metrics.csv` and `outputs/tables/*_monthly_metrics.csv` for complete numerical results.**

---

## What This Repository Provides

### Ready-to-Use Results (for Piracicaba and Manaus)
Clone and run the pipeline in under 5 minutes to generate:

**📊 Metrics Tables** (`outputs/tables/`)
- `{site}_daily_metrics.csv` — RMSE, MAE, R², bias for daily estimates
- `{site}_monthly_metrics.csv` — Same metrics aggregated monthly
- **→ These tables are your primary evidence for method performance**

**📈 Figures** (`outputs/figures/{site}/`)
- Taylor diagrams (daily and monthly) — Visual summary of method agreement
- Scatter plots — Method vs Penman-Monteith comparisons
- Time series — Temporal patterns over the year
- Monthly totals — Seasonal ETo accumulation by method

**📁 Intermediate Data** (`data/cleaned/`, `outputs/results/`)
- Cleaned daily time series for both sites
- 7-day rolling means
- Monthly aggregations

### Extensible Framework
The pipeline works for **any location** where you have meteorological data:
- Add your data to `data/raw/` (see Data Sources below)
- Run the same pipeline
- Get the same outputs for your site

---

## Quick Start

### Prerequisites
- **Python 3.8 or higher** (tested on 3.9, 3.10, 3.11)
  - Check your version: `python3 --version`
- **pip** for package management
- **Git** for cloning the repository

### Step-by-Step Installation

**1. Clone the repository**
```bash
git clone https://github.com/yourusername/eto-methods-comparison.git
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

**6. Run the complete pipeline**
```bash
python -m scripts.cli all --year 2024
```

**Expected output:**
```
Processing Piracicaba...
Processing Manaus...
Generating metrics...
Creating figures...
Done!
```

**7. Check your results**
```bash
ls outputs/tables/
# Should show: piracicaba_daily_metrics.csv, piracicaba_monthly_metrics.csv
#              manaus_daily_metrics.csv, manaus_monthly_metrics.csv

ls outputs/figures/piracicaba/
# Should show: multiple .png files (Taylor diagrams, scatter plots, time series)
```

### Running Individual Steps

If you only need specific outputs:

```bash
python -m scripts.cli clean      # Clean raw data → data/cleaned/
python -m scripts.cli aggregate  # Create aggregations → outputs/results/
python -m scripts.cli metrics    # Compute RMSE, R², etc. → outputs/tables/
python -m scripts.cli plots      # Generate all figures → outputs/figures/
```

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

To compute all 7 methods, you need daily data for:

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

**2. Edit configuration** (`scripts/config.py`)

Add your site to the `SITES` dictionary:
```python
SITES = {
    "piracicaba": {"sheet": "Piracicaba", "lat": -22.7, "elev": 546},
    "manaus": {"sheet": "Manaus", "lat": -3.1, "elev": 92},
    "cuiaba": {"sheet": "Cuiaba", "lat": -15.6, "elev": 165},  # Your new site
}
```

**3. Run the pipeline**
```bash
python -m scripts.cli all --year 2024
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
│   ├── results/        # Intermediate aggregations (7-day rolling, monthly totals)
│   ├── figures/        # All generated plots (Taylor diagrams, scatter plots, time series)
│   └── tables/         # **Metrics tables (RMSE, R², MAE, bias) ← Start here**
├── scripts/            # Analysis pipeline (CLI, cleaning, metrics, plotting)
├── notebooks/          # Educational Jupyter notebooks with step-by-step explanations
├── docs/               # Detailed methodology, equations, and interpretation guides
└── requirements.txt    # Python dependencies
```

---

## How to Cite

If you use this repository or its outputs in academic work, please cite:

> Vieira, B. M. M. (2026). *Fisica Ambiental — Evapotranspiracao de Referencia (ETo)*. Dataset and analysis code. Universidade Federal do Mato Grosso. https://doi.org/10.5281/zenodo.18615049

**Concept DOI (all versions):** https://doi.org/10.5281/zenodo.18615050

**BibTeX:**
```bibtex
@misc{vieira2026eto,
  author = {Vieira, Bruno Martins M.},
  title = {Fisica Ambiental --- Evapotranspiracao de Referencia (ETo)},
  year = {2026},
  howpublished = {Dataset and analysis code},
  institution = {Universidade Federal do Mato Grosso},
  doi = {10.5281/zenodo.18615049},
  doi_concept = {10.5281/zenodo.18615050},
  url = {https://doi.org/10.5281/zenodo.18615049}
}
```

---

## Methods Overview

This study evaluates **7 ETo estimation methods:**

**Reference standard:**
- **Penman-Monteith (FAO-56)** — Energy balance + aerodynamic approach, requires full met data

**Temperature-based (empirical):**
- **Thornthwaite** — Monthly temperature + photoperiod
- **Camargo** — Brazilian adaptation of Thornthwaite for tropical climates
- **Thornthwaite-Camargo** — Hybrid approach

**Temperature-range based (semi-empirical):**
- **Hargreaves-Samani (original)** — Uses daily temperature range as radiation proxy
- **Hargreaves-Samani (calibrated)** — Locally adjusted coefficients

**Energy-balance based (semi-empirical):**
- **Priestley-Taylor** — Simplified energy balance with empirical coefficient

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

[Add your license here if applicable]

## Contact

For questions, suggestions, or collaboration:
- **Author:** Bruno Martins M. Vieira
- **Institution:** Universidade Federal do Mato Grosso
- **GitHub Issues:** [Report issues or ask questions](https://github.com/yourusername/eto-methods-comparison/issues)
