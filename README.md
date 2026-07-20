# Air Quality, Pollution & Climate Analytics Dashboard

An interactive Python & Data Science web application built using **Streamlit** to explore air quality patterns, meteorological correlations, and real-time AQI metrics based on the **Central Pollution Control Board (CPCB) India** guidelines.

This project focuses on visual exploratory data analysis (EDA), correlation modeling, and interactive sub-index calculations, rather than machine learning predictions, highlighting direct physical science interactions.

---

## 🚀 Features

### 1. 📊 Climate & AQI Dashboard
* **Glassmorphic KPI Cards**: Real-time average/peak AQI, temperature, and humidity counters formatted with custom CSS.
* **Aggregated Trends**: Interactive Plotly line charts displaying weekly or monthly averages of AQI.
* **AQI Distribution**: Visual breakdown of daily air quality conditions categorized by standard CPCB severity brackets.
* **Downloadable Data**: Fully filterable raw data table with a button to export the current slice as a CSV.

### 2. 📈 Pollutant Deep Dive (EDA)
* **Single Pollutant Analysis**: Detailed histograms and box plots mapping individual concentrations.
* **Correlation Heatmap Matrix**: Annotated statistical mapping showing linear relationships between PM2.5, PM10, NO2, SO2, CO, O3, and weather features.
* **Particulate Correlation**: Scatter plot comparison of PM2.5 vs. PM10 verifying coarse-to-fine ratio.

### 3. 🌦️ Climate & Pollution Correlation
* **Interactive Weather Scatter**: Scatter plots with Ordinary Least Squares (OLS) regression trendlines showing the influence of weather parameters on AQI/pollutant density.
* **Physical Insights Panel**: Educational explanations detailing wind dispersion, rain washout, winter boundary layer trapping, and summer ozone photochemical reactions.

### 4. 🧮 Live CPCB AQI Calculator
* **Custom Parameter Sliders**: Adjust values of PM2.5, PM10, NO2, SO2, CO, and O3.
* **CPCB Gauge Indicator**: Interactive circular gauge highlighting the calculated AQI, health status, and advisory.
* **Sub-Index Table**: Breakdown showing sub-index values for all pollutants, automatically highlighting the **dominant pollutant** driving the AQI.

### 5. ℹ️ About Page
* Core project documentation detailing the linear interpolation breakpoint boundaries set by CPCB India.

---

## 📁 Project Structure

* `app.py`: Main Streamlit frontend dashboard application.
* `utils.py`: Helper functions for CPCB AQI calculations, synthetic data generation, and custom dark-theme CSS injection.
* `run_app.py`: Automation script to launch the server and force open the default web browser.
* `air_quality_dataset.csv`: 2-year daily historical dataset generated for Delhi, Mumbai, Bengaluru, and Kolkata.
* `verify_project.py`: Automated testing suite.
* `requirements.txt`: Python package dependencies.

---

## 🛠️ Installation & Setup

Ensure you have **Python 3.8+** installed on your system.

### 1. Clone or Download the Project
```bash
git clone <your-repository-url>
cd air_quality_project
