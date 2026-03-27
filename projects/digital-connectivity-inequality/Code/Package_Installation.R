# ============================================================
# Package Installation Script
# Purpose: Install all packages required for the project
# Run: ONCE per machine / R version (Console only)
# ============================================================


# ------------------------------------------------------------
# 1. Core data manipulation & visualization
# ------------------------------------------------------------
# - tidyverse: data manipulation (dplyr), tidying (tidyr),
#   plotting (ggplot2), functional programming (purrr)
# - plotly: interactive visualizations
install.packages(c(
  "tidyverse",
  "plotly"
))


# ------------------------------------------------------------
# 2. Data import & web scraping / APIs
# ------------------------------------------------------------
# - readxl: Excel files
# - httr2: modern HTTP requests (APIs)
# - jsonlite: JSON parsing
# - rvest: web scraping
install.packages(c(
  "readxl",
  "httr2",
  "jsonlite",
  "rvest"
))


# ------------------------------------------------------------
# 3. Panel data econometrics & fixed effects
# ------------------------------------------------------------
# - fixest: fast OLS, fixed effects, clustered SEs (feols)
# - plm: panel data models (FE / RE)
# - lmtest: hypothesis tests
# - sandwich: robust & clustered standard errors
# - AER: applied econometrics tools (IV, diagnostics)
# - estimatr: robust OLS estimators
install.packages(c(
  "fixest",
  "plm",
  "lmtest",
  "sandwich",
  "AER",
  "estimatr"
))


# ------------------------------------------------------------
# 4. Causal inference tools (optional)
# ------------------------------------------------------------
# - did: Difference-in-Differences estimators
# - MatchIt: matching methods
install.packages(c(
  "did",
  "MatchIt"
))


# ------------------------------------------------------------
# 5. Reporting, tables & reproducible documents
# ------------------------------------------------------------
# - modelsummary: regression tables
# - broom: tidy model outputs
# - kableExtra: formatted tables
# - rmarkdown: dynamic reports
install.packages(c(
  "modelsummary",
  "broom",
  "kableExtra",
  "rmarkdown"
))


# ------------------------------------------------------------
# 6. Data cleaning, diagnostics & exploration
# ------------------------------------------------------------
# - janitor: clean variable names, tabulations
# - skimr: quick descriptive summaries
# - corrr: correlation matrices
install.packages(c(
  "janitor",
  "skimr",
  "corrr"
))


# ------------------------------------------------------------
# 7. World Bank & macroeconomic data
# ------------------------------------------------------------
# - wbstats: World Bank API access
# - WDI: World Development Indicators
install.packages(c(
  "wbstats",
  "WDI"
))
