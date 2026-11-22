# NYC Taxi Fare Analysis — Business Intelligence II

**Author:** Daniela Borja Polanco
**Course:** Business Intelligence II, Carl von Ossietzky Universität Oldenburg (Summer Term 2025)

## Overview

This project predicts New York City yellow taxi fares and identifies the variables that drive them. It uses NYC Taxi and Limousine Commission (TLC) trip records from 2023. The two target variables are `fare_amount` (base metered fare) and `total_amount` (final charge to the passenger). An external dataset of weekly average gasoline prices from NYSERDA was added to test whether fuel costs affect fares.

**Methods:** data preprocessing, exploratory data analysis, outlier detection, visualization, and supervised regression comparing Linear Regression, Random Forest and Histogram-Based Gradient Boosting. Models were evaluated with MAE, MSE and RMSE on an 80/20 train/test split.

## Structure

```
NYC_Taxi_Fare_Analysis_BusinessIntelligence/
├── paper/
│   ├── 20250210_PaperTerm_BI2_Practical_Exercise_Borja-Polanco.pdf   # term paper
│   └── 20250210_BI2_Practical_Exercise_Borja-Polanco.html            # notebook export, viewable in a browser
└── code/
    └── 20250210_BI2_Practical_Exercise_Borja-Polanco.ipynb           # full analysis and models
```

## Data

The dataset is too large for GitHub and isn't included. Download it from [Kaggle: NYC Taxi Trip Records 2023](https://www.kaggle.com/datasets/nagasai524/nyc-taxi-trip-records-from-jan-2023-to-jun-2023) (original source: [NYC TLC Trip Record Data](https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page)). Save it in `code/` as `nyc_yellow_taxi_trip_records_from_Jan_to_Aug_2023.csv`.

Gasoline prices come from [NYSERDA Weekly Average Motor Gasoline Prices](https://www.nyserda.ny.gov/Energy-Prices/Motor-Gasoline/Weekly-Average-Motor-Gasoline-Prices).

## Tools

Python · pandas · NumPy · Matplotlib · Seaborn · scikit-learn · Jupyter
