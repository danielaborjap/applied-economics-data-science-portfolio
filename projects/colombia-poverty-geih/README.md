# Replicating Colombia's official monetary poverty rate from GEIH microdata

> **Status: work in progress.** Repo structure, data download script, loading notebook and
> tested weighted-statistics functions are in place. Results tables below will be filled
> in as each step is completed. No number is reported here until it is computed from the microdata.

## Question

Can DANE's official 2025 monetary poverty, extreme poverty and Gini figures be reproduced
from the public microdata, and what do the same data show beyond the published tables?

## Data

DANE, *Medición de Pobreza Monetaria y Desigualdad* (built on the Gran Encuesta Integrada
de Hogares, GEIH), microdata portal: [2025](https://microdatos.dane.gov.co/index.php/catalog/908),
[2024](https://microdatos.dane.gov.co/index.php/catalog/874). Two files: `hogares`
(one row per household) and `personas` (one row per person). Key variables:

| Variable | Meaning |
|---|---|
| `ingpcug` | per-capita income of the spending unit (*unidad de gasto*) |
| `lp`, `li` | poverty line and extreme poverty line (per capita, monthly) |
| `pobre`, `indigente` | poor / extremely poor flags |
| `fex_c` | expansion factor (sampling weight) |
| `npersug` | persons in the spending unit |
| `fac_emp` | splice factor — empalme datasets only: use `ingpcug × fac_emp` |

Variable names change across releases; `src/povcol/load.py` maps known aliases and the
notebook prints the mapping so it can be checked against each year's data dictionary.
Raw files are not committed (`data/` is gitignored).

## Method

- **Weights.** The GEIH is a stratified, clustered sample, so households differ in how many
  people they represent. `fex_c` is the number of households each sampled household stands for.
  Poverty incidence is a share of *persons*, so each household is weighted by `fex_c × npersug`.
- **Why it matters.** Rural and poorer areas are sampled at different rates than cities; an
  unweighted mean over survey rows estimates the poverty rate *of the sample*, not of Colombia.
  The replication reports both to show the size of that error.
- **Own implementations.** Weighted quantiles and the Gini coefficient are written from scratch
  in `src/povcol/weighted.py` and unit-tested (equal-weight and replication-weight identities,
  pairwise mean-absolute-difference formula).

## Replication targets (DANE, 2025 bulletin)

| Indicator | DANE 2024 | DANE 2025 | This repo 2025 |
|---|---|---|---|
| Monetary poverty, national (%) | 31.8 | 28.0 | _pending_ |
| Monetary poverty, cabeceras (%) | 28.6 | 24.6 | _pending_ |
| Monetary poverty, rural (%) | 42.5 | 39.5 | _pending_ |
| Extreme poverty, national (%) | 11.7 | 9.6 | _pending_ |
| Gini, national | 0.551 | 0.531 | _pending_ |

Source: DANE, [Boletín técnico, Pobreza monetaria en Colombia, año 2025](https://www.dane.gov.co/files/operaciones/PM/bol-PM-2025.pdf) (12 June 2026).
Target: within ±0.1 percentage points.

## Plan

- [x] Repo, download script, data loading and sanity checks (`notebooks/01_load_data.ipynb`)
- [x] Weighted quantile and Gini functions with tests (`src/povcol/weighted.py`)
- [ ] Replicate national poverty, extreme poverty; weighted vs. unweighted comparison
- [ ] Breakdowns: urban/rural, department, sex of household head; weighted Gini
- [ ] Second year (2024 vs 2025) and design-based confidence intervals (`samplics`)
- [ ] Charts and limitations

## Reproduce

```bash
pip install -r requirements.txt
python data/download.py 2025 --zip ~/Downloads/<dane_file>.zip   # portal needs a free login
jupyter lab notebooks/01_load_data.ipynb
pytest tests
```

## Repository layout

```
data/download.py        fetch + unpack microdata into data/raw/<year>/ (gitignored), writes SHA-256 manifest
notebooks/              analysis notebooks (_build_nb.py regenerates 01 from source)
src/povcol/load.py      file discovery, variable-name mapping, splice factor, household-head sex
src/povcol/weighted.py  weighted mean/rate, weighted quantile, Gini
src/povcol/official.py  DANE published figures used as replication targets
tests/                  unit tests for the weighted statistics
```

## Limitations (to expand)

- Rates computed with expansion factors alone are point estimates; standard errors need the
  design variables (strata, PSUs), which may be restricted in the public files.
- DANE's income aggregate includes imputation and matching with administrative records
  (institutional transfers, PILA); the replication uses DANE's final `ingpcug` and does not
  rebuild income from the raw GEIH modules.
