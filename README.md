# Air Quality, Pollution & Climate Analytics Dashboard

An interactive Python & Data Science web application built using **Streamlit** to explore air quality patterns, meteorological correlations, and real-time AQI metrics based on Central Pollution Control Board (CPCB) India guidelines.

<a href="https://aqianalysiso7-7q9mzkvfbxcqqbzgkbmtem.streamlit.app/">Deployed Project Link</a>

---

## 🚀 Features

* **📊 Climate & AQI Dashboard**: Displays key environmental stats using glassmorphic KPI cards, daily/weekly/monthly trends, and AQI category distributions.
* **📈 Pollutant Deep Dive (EDA)**: Dynamic profiling of individual pollutants (PM2.5, PM10, NO2, SO2, CO, O3) with distribution histograms and box plots.
* **🌦️ Climate vs. Pollution**: Interactive scatter plots with OLS regression trendlines illustrating how Temperature, Humidity, Wind Speed, and Rain affect pollution levels.
* **🧮 Live CPCB AQI Calculator**: Interactive sliders to calculate index values and show health warnings and dominant pollutants.
* **ℹ️ About Page**: Full documentation of CPCB breakpoints, logic, and data sources.

---

## 📁 Project Structure

* `app.py`: Main Streamlit dashboard application.
* `utils.py`: Helper functions for CPCB AQI sub-index calculations, data generation, and custom CSS.
* `run_app.py`: Script to launch the server and automatically open the dashboard in your default browser.
* `air_quality_dataset.csv`: 2-year daily historical dataset generated for Delhi, Mumbai, Bengaluru, and Kolkata.
* `verify_project.py`: Automated verification testing suite.
* `requirements.txt`: Python package dependencies.

---

## 💻 How to Run Locally

### 1. Clone the repository
```bash
git clone <your-repo-url>
cd air_quality_project
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Run the dashboard
Launch the dashboard (this will automatically open the browser page):
```bash
python run_app.py
```
*(Alternatively, run `python -m streamlit run app.py`)*
