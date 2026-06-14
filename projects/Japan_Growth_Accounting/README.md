# Growth Facts and Growth Accounting for Japan

Decomposing Japan's postwar growth (1950–2023) into the contributions of
capital, labor, and total factor productivity (TFP), using the Solow growth
accounting framework. The analysis asks a simple question: when Japan's growth
slowed from nearly 9% a year to almost zero, **which input slowed with it?**

The answer is mostly **TFP**. Capital's contribution faded slowly and
predictably as the economy matured, but the swing in productivity, from
**+2.73%** a year in the postwar miracle to **−0.66%** during the 1990s "Lost
Decade", accounts for most of the collapse in growth.

## Methods

The core analysis applies the Solow decomposition as an accounting identity:

```
ΔY/Y = s̄ᴷ · ΔK/K  +  s̄ᴸ · ΔL/L  +  ΔA/A
       (capital)      (labor)       (TFP, the residual)
```

where factor inputs are weighted by their income shares and TFP is recovered as
the residual. The work includes:

- **Growth facts:** real GDP and GDP-per-worker growth, and the labor income share over time.
- **Year-by-year decomposition** of output growth into capital, labor, and TFP.
- **Sub-period averages** across Japan's growth regimes (miracle, oil shocks, bubble, Lost Decade, stagnation, Abenomics, pandemic).
- **Extension 1 — Basic vs Extended TFP:** comparing a crude residual (capital stock + headcount) with a quality-adjusted one, illustrating the Jorgenson–Griliches point that part of measured TFP is really unmeasured input quality.
- **Extension 2 — Capital composition (EU KLEMS):** splitting capital into ICT, non-ICT, and intangible types, and confirming the negative-TFP signature of the Lost Decade in an independent dataset.

## Data

| Source | Coverage | Used for |
|--------|----------|----------|
| [Penn World Table 11.0](https://www.rug.nl/ggdc/productivity/pwt/) | Japan, 1950–2023, aggregate | Main decomposition and Extension 1 |
| [EU KLEMS (2023 release)](https://euklems-intanprod-llee.luiss.it/) | Japan, 1995–2021, industry-level | Extension 2 (capital composition) |

## Files

| File | Description |
|------|-------------|
| `Japan_Growth_Accounting_Report.Rmd` | Full R Markdown source (code + analysis) |
| `Japan_Growth_Accounting_Report.pdf` | Knitted report |

## Reproducing

The report is written in R Markdown and knits to PDF. To reproduce:

1. Place `pwt110.xlsx` and the EU KLEMS Japan growth-accounts file in the project folder.
2. Open the `.Rmd` in RStudio and knit, or run:

```r
rmarkdown::render("Japan_Growth_Accounting_Report.Rmd")
```

**Dependencies:** `readxl`, `dplyr`, `tidyr`, `ggplot2`, `knitr`, and a LaTeX
engine for PDF output (e.g. `tinytex::install_tinytex()`).

## Key result

Japan's growth history is a story of switching engines. Capital accumulation and
strong TFP drove the postwar miracle; the bursting of the 1991 asset bubble
opened a long stagnation in which TFP turned negative and capital was the only
thing holding growth above zero. Two independent datasets tell the same story.

## Author

**Daniela Borja** — Applied Economics & Data Science

## References

- Feenstra, R. C., Inklaar, R., & Timmer, M. P. (2015). The Next Generation of the Penn World Table. *American Economic Review*, 105(10), 3150–3182.
- Jorgenson, D. W., & Griliches, Z. (1967). The Explanation of Productivity Change. *Review of Economic Studies*, 34(3), 249–283.
- Solow, R. M. (1957). Technical Change and the Aggregate Production Function. *Review of Economics and Statistics*, 39(3), 312–320.
- Hulten, C. R. (1978). Growth Accounting with Intermediate Inputs. *Review of Economic Studies*, 45(3), 511–518.
- EU KLEMS & INTANProd (2023 release), Luiss Lab of European Economics.
