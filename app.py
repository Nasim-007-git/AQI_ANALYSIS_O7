import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime

# Import custom utilities
from utils import generate_historical_data, calculate_overall_aqi, get_aqi_details, inject_custom_css

# Page Configuration
st.set_page_config(
    page_title="Air Quality, Pollution & Climate Analytics",
    page_icon="🌦️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply custom styles
inject_custom_css()

# Load/Generate Data with caching
@st.cache_data
def load_data():
    import os
    csv_path = "air_quality_dataset.csv"
    if os.path.exists(csv_path):
        return pd.read_csv(csv_path, parse_dates=['Date'])
    else:
        df = generate_historical_data()
        df.to_csv(csv_path, index=False)
        return df

df_raw = load_data()

# App Header
st.markdown('<div class="glowing-header">Air Quality, Pollution & Climate Analytics</div>', unsafe_allow_html=True)
st.markdown('<div class="glowing-subheader">Interactive Exploratory Data Analysis & CPCB Air Quality Index (AQI) Dashboard</div>', unsafe_allow_html=True)

# ----------------- SIDEBAR FILTERS -----------------
st.sidebar.markdown("# 🔍 Dashboard Filters")
st.sidebar.markdown("Filter the historical dataset below.")

# City Selector
all_cities = sorted(df_raw['City'].unique())
selected_city = st.sidebar.selectbox("Select City", ["All Cities"] + all_cities, index=0)

# Date Range Selector
min_date = df_raw['Date'].min().to_pydatetime()
max_date = df_raw['Date'].max().to_pydatetime()
selected_date_range = st.sidebar.date_input(
    "Select Date Range",
    value=(min_date, max_date),
    min_value=min_date,
    max_value=max_date
)

# Filter logic
df_filtered = df_raw.copy()

# Filter by City
if selected_city != "All Cities":
    df_filtered = df_filtered[df_filtered['City'] == selected_city]

# Filter by Date
if isinstance(selected_date_range, tuple) and len(selected_date_range) == 2:
    start_dt, end_dt = pd.to_datetime(selected_date_range[0]), pd.to_datetime(selected_date_range[1])
    df_filtered = df_filtered[(df_filtered['Date'] >= start_dt) & (df_filtered['Date'] <= end_dt)]

# Informational Sidebar Widget
st.sidebar.markdown("---")
st.sidebar.markdown("### 📘 CPCB AQI Categories")
aqi_cat_colors = {
    "Good (0-50)": "#00b050",
    "Satisfactory (51-100)": "#92d050",
    "Moderate (101-200)": "#ffc000",
    "Poor (201-300)": "#e46c0a",
    "Very Poor (301-400)": "#ff0000",
    "Severe (401-500+)": "#943126"
}
for cat, color in aqi_cat_colors.items():
    st.sidebar.markdown(f'<span style="color:{color}; font-weight:bold;">■ {cat}</span>', unsafe_allow_html=True)

st.sidebar.markdown("---")
st.sidebar.markdown("Created for Python & Data Science Training Project.")

# ----------------- TABS SETUP -----------------
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Climate & AQI Dashboard", 
    "📈 Pollutant Deep Dive (EDA)", 
    "🌦️ Climate vs. Pollution", 
    "🧮 Live CPCB AQI Calculator",
    "ℹ️ About"
])

# ----------------- TAB 1: DASHBOARD OVERVIEW -----------------
with tab1:
    st.markdown("### 📊 Overall Environmental Summary")
    
    # Calculate aggregate stats
    avg_aqi = int(df_filtered['AQI'].mean())
    max_aqi = int(df_filtered['AQI'].max())
    avg_temp = df_filtered['Temperature'].mean()
    avg_hum = df_filtered['Humidity'].mean()
    
    # Get AQI Category details for the average
    aqi_det = get_aqi_details(avg_aqi)
    
    # Custom Card layout using columns
    c1, c2, c3, c4 = st.columns(4)
    
    with c1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Average AQI</div>
            <div class="metric-value" style="color: {aqi_det['color']}">{avg_aqi}</div>
            <div class="status-badge" style="background-color: {aqi_det['bg_color']}; color: {aqi_det['text_color']}">
                {aqi_det['category']}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
    with c2:
        max_aqi_det = get_aqi_details(max_aqi)
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Peak AQI</div>
            <div class="metric-value" style="color: {max_aqi_det['color']}">{max_aqi}</div>
            <div class="status-badge" style="background-color: {max_aqi_det['bg_color']}; color: {max_aqi_det['text_color']}">
                {max_aqi_det['category']}
            </div>
        </div>
        """, unsafe_allow_html=True)
        
    with c3:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Average Temperature</div>
            <div class="metric-value">{avg_temp:.1f}<span class="metric-unit">°C</span></div>
            <div style="margin-top: 1.3rem; color: #8b949e; font-size: 0.85rem;">
                Range: {df_filtered['Temperature'].min():.1f}°C to {df_filtered['Temperature'].max():.1f}°C
            </div>
        </div>
        """, unsafe_allow_html=True)
        
    with c4:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-title">Average Humidity</div>
            <div class="metric-value">{avg_hum:.1f}<span class="metric-unit">%</span></div>
            <div style="margin-top: 1.3rem; color: #8b949e; font-size: 0.85rem;">
                Range: {df_filtered['Humidity'].min():.1f}% to {df_filtered['Humidity'].max():.1f}%
            </div>
        </div>
        """, unsafe_allow_html=True)

    # Health Advisory banner based on filtered average
    st.markdown(f"""
    <div class="advisory-box" style="background-color: {aqi_det['bg_color']}; border-color: {aqi_det['color']}; color: #f0f6fc">
        <strong>Health Advisory for Average Air Quality ({aqi_det['category']}):</strong> {aqi_det['advisory']}
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Graphs Section
    g1, g2 = st.columns([2, 1])
    
    with g1:
        st.markdown("#### AQI Trend Over Time")
        # Rolling average or daily plot
        # For readability, if dataset is too large, we resample/group by week
        df_trend = df_filtered.copy()
        df_trend = df_trend.set_index('Date')
        
        # Select visualization frequency
        freq = st.selectbox("Aggregate Trend By", ["Daily", "Weekly Average", "Monthly Average"], index=1)
        
        if freq == "Daily":
            df_plot = df_trend.reset_index()
        elif freq == "Weekly Average":
            df_plot = df_trend.groupby(['City', pd.Grouper(freq='W')]).mean(numeric_only=True).reset_index()
        else:
            df_plot = df_trend.groupby(['City', pd.Grouper(freq='ME')]).mean(numeric_only=True).reset_index()
            
        fig_trend = px.line(
            df_plot, 
            x='Date', 
            y='AQI', 
            color='City', 
            title=f"{freq} AQI Trend",
            color_discrete_sequence=px.colors.qualitative.G10,
            template="plotly_dark"
        )
        fig_trend.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(showgrid=True, gridcolor='#30363d'),
            yaxis=dict(showgrid=True, gridcolor='#30363d')
        )
        st.plotly_chart(fig_trend, use_container_width=True)
        
    with g2:
        st.markdown("#### AQI Category Distribution")
        # Pie chart of AQI Categories
        cat_counts = df_filtered['AQI_Category'].value_counts().reset_index()
        cat_counts.columns = ['Category', 'Days']
        
        # Color mapping to CPCB standards
        color_map = {
            'Good': '#00b050',
            'Satisfactory': '#92d050',
            'Moderate': '#ffc000',
            'Poor': '#e46c0a',
            'Very Poor': '#ff0000',
            'Severe': '#943126'
        }
        
        fig_pie = px.pie(
            cat_counts, 
            values='Days', 
            names='Category', 
            title="Distribution of Air Quality Conditions",
            color='Category',
            color_discrete_map=color_map,
            template="plotly_dark"
        )
        fig_pie.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        st.plotly_chart(fig_pie, use_container_width=True)

    st.markdown("---")
    st.markdown("#### 📂 Filtered Raw Data View")
    
    # Allow user to search/inspect data
    st.dataframe(
        df_filtered.style.format({
            'PM2.5': '{:.1f}', 'PM10': '{:.1f}', 'NO2': '{:.1f}',
            'SO2': '{:.1f}', 'CO': '{:.2f}', 'O3': '{:.1f}',
            'Temperature': '{:.1f}', 'Humidity': '{:.1f}',
            'WindSpeed': '{:.1f}', 'Rainfall': '{:.1f}', 'AQI': '{:d}'
        }), 
        use_container_width=True, 
        height=250
    )
    
    # Download filtered CSV button
    csv_data = df_filtered.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Filtered Data as CSV",
        data=csv_data,
        file_name=f"air_quality_filtered_{selected_city}.csv",
        mime="text/csv"
    )

# ----------------- TAB 2: POLLUTANT DEEP DIVE -----------------
with tab2:
    st.markdown("### 📈 Detailed Pollutant Profiling (EDA)")
    st.markdown("Analyze individual pollutant distributions, concentrations, and correlations.")
    
    pollutants = ['PM2.5', 'PM10', 'NO2', 'SO2', 'CO', 'O3']
    
    col_p1, col_p2 = st.columns(2)
    with col_p1:
        selected_pollutant = st.selectbox("Select Pollutant to Analyze", pollutants, index=0)
    with col_p2:
        group_by_option = st.selectbox("Group Statistics By", ["City", "Month"], index=0)
        
    p_col1, p_col2 = st.columns(2)
    
    with p_col1:
        st.markdown(f"#### Distribution and Density of {selected_pollutant}")
        # Histogram showing pollutant concentration distribution
        fig_hist = px.histogram(
            df_filtered, 
            x=selected_pollutant, 
            color='City', 
            marginal="box", # Adds a box plot above the histogram
            title=f"Concentration Profile: {selected_pollutant}",
            opacity=0.75,
            color_discrete_sequence=px.colors.qualitative.Safe,
            template="plotly_dark"
        )
        fig_hist.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(showgrid=True, gridcolor='#30363d'),
            yaxis=dict(showgrid=True, gridcolor='#30363d')
        )
        st.plotly_chart(fig_hist, use_container_width=True)
        
    with p_col2:
        st.markdown(f"#### Box Plot Analysis (Outlier Detection)")
        # Box plot based on grouping
        if group_by_option == "City":
            fig_box = px.box(
                df_filtered,
                x='City',
                y=selected_pollutant,
                color='City',
                title=f"{selected_pollutant} Levels across Cities",
                color_discrete_sequence=px.colors.qualitative.G10,
                template="plotly_dark"
            )
        else:
            # Create a month-name column for plotting
            df_box_month = df_filtered.copy()
            df_box_month['Month_Name'] = df_box_month['Date'].dt.strftime('%b')
            month_order = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']
            
            fig_box = px.box(
                df_box_month,
                x='Month_Name',
                y=selected_pollutant,
                category_orders={'Month_Name': month_order},
                color='Month_Name',
                title=f"{selected_pollutant} Levels across Months",
                color_discrete_sequence=px.colors.sequential.Sunsetdark,
                template="plotly_dark"
            )
            
        fig_box.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(showgrid=True, gridcolor='#30363d'),
            yaxis=dict(showgrid=True, gridcolor='#30363d')
        )
        st.plotly_chart(fig_box, use_container_width=True)

    st.markdown("---")
    
    col_corr1, col_corr2 = st.columns([1, 1])
    
    with col_corr1:
        st.markdown("#### Pollutants Correlation Heatmap")
        st.markdown("Correlation coefficients show linear strength between variables (close to 1 = strong positive, -1 = strong negative).")
        # Calculate correlation matrix
        corr_cols = pollutants + ['Temperature', 'Humidity', 'WindSpeed', 'Rainfall']
        corr_matrix = df_filtered[corr_cols].corr()
        
        # Custom visual heatmap using Plotly Graph Objects for annotations
        fig_heat = go.Figure(data=go.Heatmap(
            z=corr_matrix.values,
            x=corr_matrix.columns,
            y=corr_matrix.index,
            colorscale='RdBu_r', # Red-Blue reversed (red positive, blue negative)
            zmin=-1, zmax=1,
            text=np.round(corr_matrix.values, 2),
            texttemplate="%{text}",
            hoverongaps = False
        ))
        
        fig_heat.update_layout(
            title="Correlation Matrix",
            template="plotly_dark",
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            width=550,
            height=500
        )
        st.plotly_chart(fig_heat, use_container_width=True)
        
    with col_corr2:
        st.markdown("#### Particulate Matter comparison ($PM_{2.5}$ vs. $PM_{10}$)")
        st.markdown("PM2.5 (fine respirable particles) is a fraction of PM10 (coarse particles). Usually, they are highly correlated.")
        
        fig_scatter_pm = px.scatter(
            df_filtered,
            x='PM10',
            y='PM2.5',
            color='City',
            hover_data=['Date', 'AQI_Category'],
            title="PM2.5 vs PM10 Concentration Scatter",
            opacity=0.6,
            color_discrete_sequence=px.colors.qualitative.G10,
            template="plotly_dark"
        )
        fig_scatter_pm.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            xaxis=dict(showgrid=True, gridcolor='#30363d'),
            yaxis=dict(showgrid=True, gridcolor='#30363d')
        )
        st.plotly_chart(fig_scatter_pm, use_container_width=True)

# ----------------- TAB 3: CLIMATE & POLLUTION -----------------
with tab3:
    st.markdown("### 🌦️ Climate Factor Influences on Air Quality")
    st.markdown("Discover how weather metrics like Temperature, Humidity, Wind Speed, and Rain directly affect AQI and Pollutants.")
    
    col_cl1, col_cl2 = st.columns(2)
    
    with col_cl1:
        x_var = st.selectbox("Select Weather Parameter (X-axis)", ['Temperature', 'Humidity', 'WindSpeed', 'Rainfall'], index=2)
    with col_cl2:
        y_var = st.selectbox("Select Pollution Parameter (Y-axis)", ['AQI', 'PM2.5', 'PM10', 'NO2', 'SO2', 'CO', 'O3'], index=0)
        
    # Interactive Climate Scatter
    fig_cl = px.scatter(
        df_filtered,
        x=x_var,
        y=y_var,
        color='City',
        trendline="ols", # Ordinary Least Squares regression line
        hover_data=['Date', 'AQI_Category'],
        title=f"Influence of {x_var} on {y_var}",
        opacity=0.65,
        color_discrete_sequence=px.colors.qualitative.Vivid,
        template="plotly_dark"
    )
    
    fig_cl.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis=dict(showgrid=True, gridcolor='#30363d'),
        yaxis=dict(showgrid=True, gridcolor='#30363d')
    )
    st.plotly_chart(fig_cl, use_container_width=True)
    
    # OLS trendline summary note
    st.markdown("---")
    st.markdown("### 🔍 Meteorological Science Insights")
    
    insight_cols = st.columns(2)
    with insight_cols[0]:
        st.markdown("""
        **🌬️ Wind Speed Cleansing Effect (Ventilation)**
        - Higher wind speeds enhance dispersion and dilute the concentrations of ground-level pollutants like $PM_{2.5}$ and $CO$.
        - Calm wind conditions (low wind speed) lead to stagnation, allowing pollutants to accumulate in localized pockets.
        
        **☔ Precipitation Washout (Rainwash Effect)**
        - Rainfall acts as a natural scrubber. Rain droplets scavenge particulate matter ($PM_{2.5}$, $PM_{10}$) and soluble gases ($SO_2$, $NO_2$), depositing them onto the ground.
        - This is clearly visible in the **Monsoon season** (July - September) when AQI drops to the lowest (greenest) levels.
        """)
        
    with insight_cols[1]:
        st.markdown("""
        **🌡️ Temperature Inversion & Seasonality**
        - In winter, ground air cools rapidly under clear night skies, while warmer air aloft acts as a lid (Temperature Inversion). This traps pollutants close to the ground, causing severe fog/smog.
        - In summer, strong solar radiation and high temperatures trigger photochemical reactions, leading to higher ground-level Ozone ($O_3$) synthesis from VOCs and NOx.
        
        **💧 Relative Humidity Effects**
        - High relative humidity coupled with low temperature facilitates particle coagulation and condensation, leading to larger, denser aerosol particles which degrade visibility and elevate PM readings.
        """)

# ----------------- TAB 4: LIVE AQI CALCULATOR -----------------
with tab4:
    st.markdown("### 🧮 Live CPCB AQI Calculator")
    st.markdown("Input local concentration levels of pollutants below to calculate the instant Air Quality Index (AQI) based on CPCB standards.")
    
    calc_col1, calc_col2 = st.columns([1, 1.2])
    
    with calc_col1:
        st.markdown("#### Input Pollutant Concentrations")
        
        # User sliders for 6 core CPCB pollutants
        pm25_val = st.slider("PM2.5 (Fine particulate matter) - 24hr avg (µg/m³)", 
                             min_value=0.0, max_value=500.0, value=45.0, step=0.5)
        
        pm10_val = st.slider("PM10 (Coarse particulate matter) - 24hr avg (µg/m³)", 
                             min_value=0.0, max_value=600.0, value=85.0, step=1.0)
        
        no2_val = st.slider("NO2 (Nitrogen Dioxide) - 24hr avg (µg/m³)", 
                            min_value=0.0, max_value=500.0, value=25.0, step=1.0)
        
        so2_val = st.slider("SO2 (Sulfur Dioxide) - 24hr avg (µg/m³)", 
                            min_value=0.0, max_value=800.0, value=12.0, step=0.5)
        
        co_val = st.slider("CO (Carbon Monoxide) - 8hr avg (mg/m³)", 
                           min_value=0.0, max_value=34.0, value=1.2, step=0.1)
        
        o3_val = st.slider("O3 (Ozone) - 8hr avg (µg/m³)", 
                           min_value=0.0, max_value=400.0, value=30.0, step=1.0)
        
    with calc_col2:
        st.markdown("#### Air Quality Index Result")
        
        # Calculate instant AQI
        p_inputs = {
            'PM2.5': pm25_val,
            'PM10': pm10_val,
            'NO2': no2_val,
            'SO2': so2_val,
            'CO': co_val,
            'O3': o3_val
        }
        
        overall_aqi, details, sub_indices = calculate_overall_aqi(p_inputs)
        
        # Gauge chart to represent AQI visually
        fig_gauge = go.Figure(go.Indicator(
            mode = "gauge+number",
            value = overall_aqi,
            domain = {'x': [0, 1], 'y': [0, 1]},
            title = {'text': f"Calculated AQI: {details['category']}", 'font': {'size': 20, 'color': '#f0f6fc'}},
            gauge = {
                'axis': {'range': [0, 500], 'tickwidth': 1, 'tickcolor': "#8b949e"},
                'bar': {'color': details['color']},
                'bgcolor': "rgba(22, 27, 34, 0.8)",
                'borderwidth': 1,
                'bordercolor': "#30363d",
                'steps': [
                    {'range': [0, 50], 'color': 'rgba(0, 176, 80, 0.15)'},
                    {'range': [50, 100], 'color': 'rgba(146, 208, 80, 0.15)'},
                    {'range': [100, 200], 'color': 'rgba(255, 192, 0, 0.15)'},
                    {'range': [200, 300], 'color': 'rgba(228, 108, 10, 0.15)'},
                    {'range': [300, 400], 'color': 'rgba(255, 0, 0, 0.15)'},
                    {'range': [400, 500], 'color': 'rgba(148, 49, 38, 0.15)'}
                ],
                'threshold': {
                    'line': {'color': "white", 'width': 4},
                    'thickness': 0.75,
                    'value': overall_aqi
                }
            }
        ))
        
        fig_gauge.update_layout(
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font = {'color': '#f0f6fc', 'family': "Outfit"},
            width=400,
            height=300,
            margin=dict(l=20, r=20, t=50, b=20)
        )
        
        st.plotly_chart(fig_gauge, use_container_width=True)
        
        # Display health advisory box
        st.markdown(f"""
        <div class="advisory-box" style="background-color: {details['bg_color']}; border-color: {details['color']}; color: #f0f6fc">
            <h4 style="margin:0; color: {details['text_color']}">Health Category: {details['category']}</h4>
            <p style="margin: 0.5rem 0 0 0;">{details['advisory']}</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("---")
        
        # Pollutant sub-indices details
        st.markdown("##### Sub-index breakdown of individual pollutants")
        st.markdown("The dominant pollutant (highest sub-index) determines the final overall AQI.")
        
        # Find dominant pollutant
        dominant = max(sub_indices, key=sub_indices.get) if sub_indices else 'None'
        
        sub_indices_df = pd.DataFrame({
            'Pollutant': list(sub_indices.keys()),
            'Concentration': [f"{p_inputs[p]:.2f}" if p == 'CO' else f"{p_inputs[p]:.1f}" for p in sub_indices.keys()],
            'Unit': ['mg/m³' if p == 'CO' else 'µg/m³' for p in sub_indices.keys()],
            'Calculated Sub-index': list(sub_indices.values())
        })
        
        # Apply visual styling highlighting the dominant pollutant
        def highlight_dominant(row):
            is_dom = row['Pollutant'] == dominant
            return ['background-color: rgba(228, 108, 10, 0.25); font-weight: bold;' if is_dom else '' for _ in row]
            
        st.dataframe(
            sub_indices_df.style.apply(highlight_dominant, axis=1),
            use_container_width=True,
            hide_index=True
        )
        
        st.info(f"👉 **Dominant Pollutant**: **{dominant}** (Sub-index: {sub_indices[dominant]}). This is the pollutant driving the AQI.")

# ----------------- TAB 5: ABOUT THE PROJECT -----------------
with tab5:
    st.markdown("### ℹ️ About the Project")
    
    col_a1, col_a2 = st.columns([2, 1])
    
    with col_a1:
        st.markdown("""
        #### 🌍 Overview
        This dashboard was developed as a comprehensive **Python & Data Science Training Project** focusing on environmental and meteorological analytics. 
        It integrates data processing, mathematical modeling, and interactive visualization to examine how weather patterns directly affect atmospheric pollution.
        
        #### 🧪 Key Capabilities
        * **Interactive Data Filtering**: Query the 2-year daily records of major Indian cities (Delhi, Mumbai, Bengaluru, Kolkata) with custom time ranges.
        * **Exploratory Data Analysis (EDA)**: Inspect distributions, box plots, and dynamic correlation matrices of pollutants and meteorological factors.
        * **Climate Scenarios**: Discover structural patterns like **precipitation washout (rain wash)**, **wind ventilation**, and **winter inversion** (smog trap).
        * **CPCB AQI Calculator**: Live computation engine that implements the official Central Pollution Control Board (CPCB) linear interpolation algorithm to find the dominant pollutant and overall AQI.
        """)
        
    with col_a2:
        st.markdown("""
        <div class="metric-card" style="border-left: 5px solid #58a6ff;">
            <div class="metric-title" style="color: #58a6ff; font-weight: bold; margin-bottom: 0.8rem;">Project Details</div>
            <div style="font-size: 0.95rem; line-height: 1.6; color: #c9d1d9;">
                <strong>Title</strong>: Air Quality, Pollution & Climate Analytics<br>
                <strong>Language</strong>: Python (v3.8+)<br>
                <strong>Framework</strong>: Streamlit (Web Dashboard)<br>
                <strong>Libraries</strong>: Pandas, NumPy, Plotly, Statsmodels, Seaborn<br>
                <strong>Design Theme</strong>: Dark Glassmorphism Custom CSS<br>
            </div>
        </div>
        """, unsafe_allow_html=True)
        
        st.markdown("""
        <div class="metric-card" style="border-left: 5px solid #2ecc71;">
            <div class="metric-title" style="color: #2ecc71; font-weight: bold; margin-bottom: 0.8rem;">CPCB India AQI Scale</div>
            <div style="font-size: 0.85rem; line-height: 1.5; color: #8b949e;">
                Calculations are modeled strictly on CPCB guidelines, using the maximum sub-index of PM2.5, PM10, NO2, SO2, CO, and O3 to calculate health impact.
            </div>
        </div>
        """, unsafe_allow_html=True)

