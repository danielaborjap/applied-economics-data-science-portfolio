# SDG Indicator 10.1.1 – Shared Prosperity Analysis

**Author:** Daniela Borja Polanco
**Course:** Development Economics, Master in Applied Economics and Data Science

## Research question

SDG indicator 10.1.1 tracks the growth rate of household income or consumption per capita
among the **bottom 40%** of the population compared with the **total population**.
This project asks whether growth has been inclusive, meaning that the bottom 40% grows
faster than the average. It looks at two things:

1. **Cross-section (2021):** bottom 40% growth and the bottom-40%-minus-total gap for
   51 countries, grouped by World Bank income group.
2. **Over time (circa 2016–2021):** annualized growth for the bottom 40% and the total
   population in 22 selected countries, plus the **Global Prosperity Gap**, which is
   how far the bottom 40% is from a $25/day benchmark.

## Repository structure

```
.
├── Data_analysis_indicator10.1.1.R   # Full analysis: data prep, statistics, plots
├── data/
│   ├── sdg_indicator_10_1_1.xlsx                       # UN SDG Global Database, indicator 10.1.1
│   ├── GDSP-and-Median-Income-Historical-AM24-v2.xlsx  # World Bank Global Database of Shared Prosperity
│   └── CLASS.xlsx                                      # World Bank income classification
├── plots/                            # Figures created by the script
└── report/
    └── Indicator_10.1.1_Daniela_Borja.docx            # Written report
```

## Data sources

| File | Source | Notes |
|------|--------|-------|
| `sdg_indicator_10_1_1.xlsx` | [UN SDG Global Database](https://unstats.un.org/sdgs/dataportal), indicator 10.1.1 (series `SI_HEI_TOTL`) | Sheet 2 (`Goal10`). Quantile `B40` = bottom 40%, `_T` = total population. 2021 covers 51 countries. |
| `GDSP-and-Median-Income-Historical-AM24-v2.xlsx` | [World Bank Global Database of Shared Prosperity](https://www.worldbank.org/en/topic/poverty/brief/global-database-of-shared-prosperity) | All releases from 2014 to 2024. The script uses only the **AM2024** release, whose growth periods are circa 2016–2021. The exact years differ by country (see the `period` column). |
| `CLASS.xlsx` | [World Bank country and lending groups](https://datahelpdesk.worldbank.org/knowledgebase/articles/906519) | FY2025 classification, based on 2023 GNI per capita (Atlas method). |

## How to reproduce

1. Install [R](https://cran.r-project.org/) (version 4.1 or later). RStudio is recommended.
2. Clone this repository and open the folder in RStudio, or `setwd()` to the folder.
   The script uses paths relative to the repository root.
3. Run the script:
   ```r
   source("Data_analysis_indicator10.1.1.R")
   ```
   The script installs `pacman` if needed, then loads `readxl`, `dplyr`, `tidyr`,
   `ggplot2` and `countrycode`.
4. The five figures are written to `plots/`:
   - `Bottom40_Growth_Rate_2021.png`
   - `Shared_Prosperity_Gap_2021.png`
   - `B40_Growth_2016_2021.png`
   - `Total_Growth_2016_2021.png`
   - `Global_Prosperity_Gap_B40.png`

The script ends with `sessionInfo()`, which prints the R and package versions that were used.

**Tested with:** R 4.6.0 (macOS, Apple silicon), readxl 1.5.0, dplyr 1.2.1, tidyr 1.3.2,
ggplot2 4.0.3, countrycode 1.9.0.

When the GDSP file is read, readxl prints a harmless `New names: ...22, ...23` message
because the sheet has two empty columns at the end.

## Key results (2021 cross-section)

| | Bottom 40% | Total population |
|---|---|---|
| Mean growth (%) | 3.20 | 2.33 |
| Median growth (%) | 2.93 | 1.86 |

In 40 of the 51 countries, the bottom 40% grew faster than the population average in 2021.

## Methodological notes

- **Gap** = growth of the bottom 40% − growth of the total population, in percentage points.
  A positive value means growth favored the bottom 40%.
- **Global Prosperity Gap shortfall** = max(0, 25 − mean daily income or consumption of the
  bottom 40%), in 2017 PPP dollars, using the end-of-period mean (`meanb402`).
- Growth rates come from household surveys, so the period covered differs from country to
  country. The "2021" value in the SDG database is the end year of each country's growth period.

## License

The data belong to the United Nations and the World Bank, which release them under
CC BY 4.0. The code is free to reuse with attribution.
