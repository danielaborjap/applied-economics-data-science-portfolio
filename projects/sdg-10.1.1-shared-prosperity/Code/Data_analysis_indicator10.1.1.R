# Daniela Borja Polanco
# Development Economics course
# Indicator SDG 10.1.1:
# Growth rates of household expenditure or income per capita among the bottom 40%
# of the population and the total population.
#
# Run from the repository root (open the folder as an RStudio project or setwd() to it).
# Inputs are read from data/, figures are written to plots/.

# Packages -----------------------------------------------------------------------
if (!requireNamespace("pacman", quietly = TRUE)) install.packages("pacman")
pacman::p_load(readxl, dplyr, tidyr, ggplot2, countrycode)

# Shared colour map for World Bank income groups ----------------------------------
income_color_map <- c(
  "Low income"          = "#6A0DAD", # Dark purple
  "Lower middle income" = "#B19CD9", # Light purple
  "Upper middle income" = "#A1D99B", # Light green
  "High income"         = "#2E8B57"  # Dark green
)

# World Bank income classification (FY2025, based on 2023 GNI per capita) ---------
classification_lookup_data <- read_excel("data/CLASS.xlsx", sheet = "List of economies") %>%
  select(Code, `Income group`)


# =================================================================================
# PART 1 - CROSS-SECTIONAL ANALYSIS (UN SDG Global Database, 2021)
# =================================================================================

data_indicator <- read_excel("data/sdg_indicator_10_1_1.xlsx", sheet = 2)

# Observations by year (rows = countries x quantiles)
data_indicator %>%
  count(TimePeriod, sort = TRUE)
# 2021 has the most observations: 102 rows = 51 countries x 2 quantiles (B40 and _T)

data_2021 <- data_indicator %>%
  filter(TimePeriod == 2021)

unique(data_2021$Quantile) # "B40" and "_T"

# One row per country, B40 and _T as separate columns.
# Columns are renamed BY NAME: pivot_wider() orders new columns by first appearance,
# so renaming by position would silently swap Bottom40 and Total.
data_cross <- data_2021 %>%
  select(GeoAreaCode, GeoAreaName, Quantile, Value) %>%
  pivot_wider(names_from = Quantile, values_from = Value) %>%
  rename(
    CountryCode = GeoAreaCode,
    Country     = GeoAreaName,
    Bottom40    = B40,
    Total       = `_T`
  ) %>%
  mutate(
    Bottom40 = as.numeric(Bottom40),
    Total    = as.numeric(Total),
    ISO3     = countrycode(CountryCode, origin = "un", destination = "iso3c")
  )

# Add income group
data_for_plot <- data_cross %>%
  left_join(classification_lookup_data, by = c("ISO3" = "Code"))

# Summary statistics
mean_bottom40   <- mean(data_for_plot$Bottom40, na.rm = TRUE)   # 3.20
median_bottom40 <- median(data_for_plot$Bottom40, na.rm = TRUE) # 2.93
mean_total      <- mean(data_for_plot$Total, na.rm = TRUE)      # 2.33
median_total    <- median(data_for_plot$Total, na.rm = TRUE)    # 1.86

print(paste("Mean of Bottom40:", round(mean_bottom40, 2)))
print(paste("Median of Bottom40:", median_bottom40))
print(paste("Mean of Total:", round(mean_total, 2)))
print(paste("Median of Total:", median_total))

# Shared prosperity gap: positive = bottom 40% grew faster than the average
data_for_plot <- data_for_plot %>%
  mutate(Gap_B40_Total = Bottom40 - Total)

print(paste("Countries with a positive gap:",
            sum(data_for_plot$Gap_B40_Total > 0, na.rm = TRUE), "of", nrow(data_for_plot)))

# Plot 1: growth rate of the bottom 40% by country
Growth_Rate_of_the_Bottom_40_by_Country_2021 <- ggplot(
  data_for_plot,
  aes(x = reorder(Country, Bottom40), y = Bottom40, fill = `Income group`)
) +
  geom_col() +
  scale_fill_manual(values = income_color_map) +
  labs(
    title    = "Growth Rate of the Bottom 40% by Country (2021)",
    subtitle = "Colored by World Bank Income Group Classification",
    x = "Country",
    y = "Growth Rate of Bottom 40% (%)",
    fill = "Income Group"
  ) +
  theme_minimal() +
  theme(
    axis.text.x   = element_text(angle = 45, hjust = 1, size = 8),
    plot.title    = element_text(hjust = 0.5),
    plot.subtitle = element_text(hjust = 0.5),
    legend.position = "top"
  )
print(Growth_Rate_of_the_Bottom_40_by_Country_2021)

# Plot 2: shared prosperity gap
Shared_Prosperity_Gap_Bottom_40_vs_Total_Population <- ggplot(
  data_for_plot,
  aes(x = reorder(Country, Gap_B40_Total), y = Gap_B40_Total, fill = `Income group`)
) +
  geom_col() +
  scale_fill_manual(values = income_color_map) +
  labs(
    title    = "Shared Prosperity Gap: Bottom 40% vs. Total Population (2021)",
    subtitle = "Positive = Inclusive growth; Negative = Unequal growth",
    x = "Country",
    y = "Gap in Growth Rate (percentage points)",
    fill = "Income Group"
  ) +
  theme_minimal() +
  theme(
    axis.text.x   = element_text(angle = 45, hjust = 1, size = 8),
    plot.title    = element_text(hjust = 0.5),
    plot.subtitle = element_text(hjust = 0.5),
    legend.position = "top"
  )
print(Shared_Prosperity_Gap_Bottom_40_vs_Total_Population)


# =================================================================================
# PART 2 - TEMPORAL ANALYSIS (World Bank Global Database of Shared Prosperity)
# =================================================================================

# The historical file stacks every release since 2014; keep only the AM2024 release,
# whose growth spells are circa 2016-2021 (one row per country).
gdsp_data <- read_excel("data/GDSP-and-Median-Income-Historical-AM24-v2.xlsx", sheet = "data") %>%
  filter(Release == "AM2024") %>%
  rename(countryname = country) %>%
  select(-income) %>% # use the same classification file as Part 1
  left_join(classification_lookup_data, by = c("code" = "Code")) %>%
  mutate(across(c(starts_with("growth"), starts_with("mean"), starts_with("median")),
                ~ as.numeric(as.character(.))))

# Selected countries: high/upper-middle and low/lower-middle income across regions.
# Selected by ISO3 code so naming differences (e.g. "Korea, Rep.") cannot drop countries.
selected_countries_iso3 <- c(
  "CHL", "COL", "BOL",                      # Latin America
  "CHN", "PHL", "MYS", "LKA", "VNM",        # Asia
  "POL", "TUR", "DEU", "GBR",               # Europe
  "EGY", "IRN", "TUN", "ISR",               # Middle East & North Africa
  "KEN", "UGA", "GMB",                      # Sub-Saharan Africa
  "AUS", "KOR", "USA"                       # Other high income
)

gdsp_selected <- gdsp_data %>%
  filter(code %in% selected_countries_iso3)

gdsp_selected %>% select(countryname, period, `Income group`) # check the selection

gdsp_plot_data <- gdsp_selected %>%
  rename(IncomeGroup = `Income group`, Country = countryname) %>%
  select(Country, IncomeGroup, growthb40, growthm50, growthtotal) %>%
  filter(!is.na(growthb40) | !is.na(growthm50) | !is.na(growthtotal)) %>%
  filter(!is.na(IncomeGroup)) %>%
  pivot_longer(
    cols = c(growthb40, growthm50, growthtotal),
    names_to  = "Growth_Type_Facet",
    values_to = "Growth_Rate"
  ) %>%
  mutate(Growth_Type_Facet = factor(Growth_Type_Facet,
                                    levels = c("growthb40", "growthm50", "growthtotal"),
                                    labels = c("Bottom 40%", "Median", "Total")))

# Plot 3: bottom 40% annualized growth
Plot_Bottom40 <- gdsp_plot_data %>%
  filter(Growth_Type_Facet == "Bottom 40%") %>%
  ggplot(aes(x = Country, y = Growth_Rate, fill = IncomeGroup)) +
  geom_col(width = 0.6) +
  scale_fill_manual(values = income_color_map, name = "Income Group") +
  labs(title = "Annualized Growth Rate: Bottom 40% (2016–2021)",
       x = "Country", y = "Growth Rate (%)") +
  theme_minimal() +
  theme(axis.text.x = element_text(angle = 45, hjust = 1, size = 8),
        plot.title = element_text(hjust = 0.5),
        legend.position = "top")
print(Plot_Bottom40)

# Plot 4: total population annualized growth
Plot_Total <- gdsp_plot_data %>%
  filter(Growth_Type_Facet == "Total") %>%
  ggplot(aes(x = Country, y = Growth_Rate, fill = IncomeGroup)) +
  geom_col(width = 0.6) +
  scale_fill_manual(values = income_color_map, name = "Income Group") +
  labs(title = "Annualized Growth Rate: Total Population (2016–2021)",
       x = "Country", y = "Growth Rate (%)") +
  theme_minimal() +
  theme(axis.text.x = element_text(angle = 45, hjust = 1, size = 8),
        plot.title = element_text(hjust = 0.5),
        legend.position = "top")
print(Plot_Total)


# --- Global Prosperity Gap (GPG): shortfall from $25/day --------------------------
benchmark_gpg <- 25 # $25 per day, 2017 PPP

gdsp_selectedcountries_gpg <- gdsp_selected %>%
  mutate(
    Shortfall_B40    = pmax(0, benchmark_gpg - meanb402), # most recent B40 mean
    Shortfall_Median = pmax(0, benchmark_gpg - median2)   # most recent median
  )

print(gdsp_selectedcountries_gpg %>%
        select(countryname, meanb402, Shortfall_B40, median2, Shortfall_Median))

# Plot 5: GPG shortfall of the bottom 40%
Global_Prosperity_Gap_Bottom_40 <- gdsp_selectedcountries_gpg %>%
  filter(!is.na(Shortfall_B40) & !is.na(`Income group`)) %>%
  ggplot(aes(x = reorder(countryname, Shortfall_B40), y = Shortfall_B40, fill = `Income group`)) +
  geom_col() +
  coord_flip() +
  scale_fill_manual(values = income_color_map, name = "Income Group") +
  labs(
    title    = "Global Prosperity Gap (Bottom 40%)",
    subtitle = "Distance to the $25/day Benchmark (Selected Countries)",
    x = "Country",
    y = "Shortfall ($/day, PPP)"
  ) +
  theme_minimal() +
  theme(plot.title = element_text(hjust = 0.5),
        plot.subtitle = element_text(hjust = 0.5),
        legend.position = "top")
print(Global_Prosperity_Gap_Bottom_40)


# =================================================================================
# SAVE PLOTS
# =================================================================================
if (!dir.exists("plots")) dir.create("plots")

ggsave("plots/Bottom40_Growth_Rate_2021.png", Growth_Rate_of_the_Bottom_40_by_Country_2021,
       width = 12, height = 8, dpi = 300)
ggsave("plots/Shared_Prosperity_Gap_2021.png", Shared_Prosperity_Gap_Bottom_40_vs_Total_Population,
       width = 12, height = 8, dpi = 300)
ggsave("plots/B40_Growth_2016_2021.png", Plot_Bottom40,
       width = 12, height = 8, dpi = 300)
ggsave("plots/Total_Growth_2016_2021.png", Plot_Total,
       width = 12, height = 8, dpi = 300)
ggsave("plots/Global_Prosperity_Gap_B40.png", Global_Prosperity_Gap_Bottom_40,
       width = 12, height = 8, dpi = 300)

sessionInfo() # record package versions for reproducibility
