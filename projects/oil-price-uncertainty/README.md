# Oil Price Uncertainty: Europe vs Asia Under the Shadow of the Iran Crisis

**Author:** Daniela Borja Polanco  
**context:** Forecasting Methods   
**Last updated:** 2026

---

## Overview

This report investigates how geopolitical uncertainty — specifically escalating
tensions involving Iran and the Strait of Hormuz — affects oil prices asymmetrically
across regions. It compares the **Brent crude benchmark** (Europe) against the
**Dubai crude benchmark** (Asia/Japan) using real data pulled directly from the
FRED database, and applies the forecasting methods studied in the course.

**Key question:** Does every region of the world suffer equally when oil prices
spike? The short answer is no — and this report shows why.

---

## What's in this repo

```
oil-price-uncertainty/
│
├── oil_price_uncertainty_report.Rmd   ← Main report (knit this to PDF)
├── oil_price_uncertainty_report.pdf   ← Rendered output
└── README.md                          ← This file
```

---

## Data

All data is retrieved **directly inside R** — no CSV downloads needed.

| Series code | Description | Source | Frequency |
|-------------|-------------|--------|-----------|
| `DCOILBRENTEU` | Crude Oil Prices: Brent — Europe | U.S. EIA via FRED | Daily |
| `POILDUBUSDM`  | Global price of Dubai Crude | IMF via FRED | Monthly |

Data is pulled using the `tidyquant` package:

```r
library(tidyquant)
brent <- tq_get("DCOILBRENTEU", get = "economic.data", from = "2010-01-01")
dubai <- tq_get("POILDUBUSDM",  get = "economic.data", from = "2010-01-01")
```

This works exactly like the `WDI` package for World Bank data — just pass the
FRED series code, no API key required.

---

## How to reproduce

1. Clone this repository:
   ```bash
   git clone https://github.com/YOUR_USERNAME/oil-price-uncertainty.git
   cd oil-price-uncertainty
   ```

2. Open `oil_price_uncertainty_report.Rmd` in RStudio

3. Install required packages (first time only):
   ```r
   install.packages(c("tidyquant", "tidyverse", "forecast", "fpp2",
                       "knitr", "kableExtra", "ggthemes", "gridExtra"))
   ```

4. Knit to PDF:
   - Click **Knit → Knit to PDF** in RStudio, or run:
   ```r
   rmarkdown::render("oil_price_uncertainty_report.Rmd")
   ```
   > Note: PDF output requires a LaTeX installation.
   > If you don't have one, run `tinytex::install_tinytex()` once.

---

## Methods used

| Method | Applied to | Purpose |
|--------|-----------|---------|
| Time series visualisation | Both benchmarks | Identify trend, seasonality, shocks |
| Spread analysis | Brent − Dubai | Measure regional price divergence |
| Simple Exponential Smoothing (SES) | Both benchmarks | Baseline forecast |
| Holt's damped trend | Both benchmarks | Forecast with trend |
| RMSE comparison | SES vs Holt | Model selection |

---

## Key findings

- Over the full sample, Brent traded on average $2.10/barrel above Dubai — but this 
relationship collapsed dramatically in late 2025/early 2026 when the spread fell 
to −$23/barrel, meaning Asia was paying $23 more per barrel than Europe.
- Japan and South Korea face the highest structural exposure to the Iran crisis: 
90% and 70% of their oil imports respectively transit the Strait of Hormuz with 
virtually no alternative supply routes at scale.
- China and India occupy an intermediate position — high Middle East dependence 
but with meaningful alternatives through Russian supply used actively since 2022.
- European economies (Germany, France) source primarily from Norway, North Sea, 
and Algeria — the Strait of Hormuz is relevant but not existential for their 
energy security.
- Both benchmarks returned α = 0.9999 in SES — confirming that oil prices behave 
as a near-random walk. The best forecast of tomorrow's price is today's price, 
and historical averages carry almost no predictive weight.
- The Dubai forecast's extreme upper confidence bound (~$300/barrel) is not a 
price prediction — it is a quantification of how severely the Asian crude market 
has been destabilised by the current geopolitical shock.
---

## About this project

This is a personal project applying forecasting methods to a real-world question 
I found genuinely interesting: do oil price shocks hit every region of the world 
equally? Using publicly available data from the FRED API, I applied time series 
techniques — Simple Exponential Smoothing and Holt's damped trend method, to 
compare the European (Brent) and Asian (Dubai) crude oil benchmarks, and explore 
what the current Iran crisis means for energy costs across different regions.

---

## License

This project is for educational and portfolio purposes.  
Data sourced from FRED (Federal Reserve Bank of St. Louis) — free for academic use
with citation.

---

*Built with R, RMarkdown, tidyquant, and forecast.*
