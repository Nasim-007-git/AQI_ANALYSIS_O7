import pandas as pd
import numpy as np
import streamlit as st

# CPCB (Central Pollution Control Board, India) AQI calculation guidelines
# Breakpoints for 6 major pollutants
BREAKPOINTS = {
    'PM2.5': {
        'conc': [0, 30, 60, 90, 120, 250, 500],
        'index': [0, 50, 100, 200, 300, 400, 500]
    },
    'PM10': {
        'conc': [0, 50, 100, 250, 350, 430, 500],
        'index': [0, 50, 100, 200, 300, 400, 500]
    },
    'NO2': {
        'conc': [0, 40, 80, 180, 280, 400, 800],
        'index': [0, 50, 100, 200, 300, 400, 500]
    },
    'SO2': {
        'conc': [0, 40, 80, 380, 800, 1600, 1600],
        'index': [0, 50, 100, 200, 300, 400, 500]
    },
    'CO': {
        'conc': [0, 1.0, 2.0, 10.0, 17.0, 34.0, 50.0],
        'index': [0, 50, 100, 200, 300, 400, 500]
    },
    'O3': {
        'conc': [0, 50, 100, 168, 208, 748, 1000],
        'index': [0, 50, 100, 200, 300, 400, 500]
    }
}

def calculate_sub_index(pollutant, concentration):
    """Calculate the sub-index for a specific pollutant using CPCB breakpoints."""
    if concentration < 0:
        return 0
        
    bp = BREAKPOINTS.get(pollutant)
    if not bp:
        return 0
        
    conc_limits = bp['conc']
    index_limits = bp['index']
    
    # Handle values above maximum breakpoint
    if concentration > conc_limits[-1]:
        # Linear extrapolation for extreme values
        ratio = (index_limits[-1] - index_limits[-2]) / (conc_limits[-1] - conc_limits[-2])
        return min(500, index_limits[-1] + ratio * (concentration - conc_limits[-1]))
        
    for i in range(1, len(conc_limits)):
        if concentration <= conc_limits[i]:
            c_low, c_high = conc_limits[i-1], conc_limits[i]
            i_low, i_high = index_limits[i-1], index_limits[i]
            
            # Linear Interpolation Formula
            sub_index = i_low + (i_high - i_low) / (c_high - c_low) * (concentration - c_low)
            return round(sub_index)
            
    return 0

def get_aqi_details(aqi_value):
    """Return category, color, and health advisory for a given AQI value."""
    if aqi_value <= 50:
        return {
            'category': 'Good',
            'color': '#00b050',
            'bg_color': 'rgba(0, 176, 80, 0.15)',
            'text_color': '#00b050',
            'advisory': 'Minimal Impact. Air quality is considered satisfactory, and air pollution poses little or no risk.'
        }
    elif aqi_value <= 100:
        return {
            'category': 'Satisfactory',
            'color': '#92d050',
            'bg_color': 'rgba(146, 208, 80, 0.15)',
            'text_color': '#76b833',
            'advisory': 'Minor breathing discomfort to sensitive people. May cause minor respiratory irritation.'
        }
    elif aqi_value <= 200:
        return {
            'category': 'Moderate',
            'color': '#ffc000',
            'bg_color': 'rgba(255, 192, 0, 0.15)',
            'text_color': '#d49e00',
            'advisory': 'Breathing discomfort to people with lungs, asthma, and heart diseases.'
        }
    elif aqi_value <= 300:
        return {
            'category': 'Poor',
            'color': '#e46c0a',
            'bg_color': 'rgba(228, 108, 10, 0.15)',
            'text_color': '#e46c0a',
            'advisory': 'Breathing discomfort to most people on prolonged exposure. Sensitive groups should limit outdoor activity.'
        }
    elif aqi_value <= 400:
        return {
            'category': 'Very Poor',
            'color': '#ff0000',
            'bg_color': 'rgba(255, 0, 0, 0.15)',
            'text_color': '#ff0000',
            'advisory': 'Respiratory illness to the people on prolonged exposure. Effect may be more pronounced in people with lung and heart diseases.'
        }
    else:
        return {
            'category': 'Severe',
            'color': '#943126',
            'bg_color': 'rgba(148, 49, 38, 0.15)',
            'text_color': '#943126',
            'advisory': 'May cause respiratory impact even on healthy people and serious health impacts on people with lung/heart diseases. Healthy people should avoid outdoor activities.'
        }

def calculate_overall_aqi(pollutant_dict):
    """
    Calculate the overall AQI which is the maximum of individual sub-indices.
    According to guidelines, AQI is only calculated if at least three parameters 
    are monitored, out of which one should be PM10 or PM2.5.
    """
    sub_indices = {}
    for p, conc in pollutant_dict.items():
        if p in BREAKPOINTS and conc is not None:
            sub_indices[p] = calculate_sub_index(p, conc)
            
    if not sub_indices:
        return 0, 'N/A', sub_indices
        
    # Check CPCB criteria: at least one PM pollutant and at least 3 total pollutants
    has_pm = ('PM2.5' in sub_indices) or ('PM10' in sub_indices)
    has_three = len(sub_indices) >= 3
    
    # We will compute the max regardless for dashboard convenience, but add a warning if criteria aren't met
    overall_aqi = max(sub_indices.values())
    details = get_aqi_details(overall_aqi)
    
    return overall_aqi, details, sub_indices

def generate_historical_data():
    """
    Generate realistic multi-city, multi-season air quality and climate dataset.
    Cities: Delhi (High pollution, high seasonal variation), Mumbai (Coastal, moderate),
            Bengaluru (Clean, pleasant climate), Kolkata (Humid, moderate-high).
    Timeline: 2024-01-01 to 2025-12-31 (Daily data).
    """
    cities = {
        'Delhi': {
            'base_temp': 25, 'temp_amp': 15,
            'base_humidity': 55, 'humidity_amp': 25,
            'base_wind': 8, 'wind_amp': 4,
            'pm25_base': 85, 'pm10_base': 160, 'no2_base': 45, 'so2_base': 15, 'co_base': 1.8, 'o3_base': 40,
            'winter_pollution_factor': 2.8, # Severe winter pollution
            'monsoon_wash_factor': 0.35
        },
        'Mumbai': {
            'base_temp': 28, 'temp_amp': 4,
            'base_humidity': 75, 'humidity_amp': 15,
            'base_wind': 14, 'wind_amp': 5,
            'pm25_base': 40, 'pm10_base': 85, 'no2_base': 25, 'so2_base': 12, 'co_base': 0.9, 'o3_base': 25,
            'winter_pollution_factor': 1.3,
            'monsoon_wash_factor': 0.25
        },
        'Bengaluru': {
            'base_temp': 23, 'temp_amp': 5,
            'base_humidity': 60, 'humidity_amp': 20,
            'base_wind': 12, 'wind_amp': 4,
            'pm25_base': 25, 'pm10_base': 55, 'no2_base': 18, 'so2_base': 8, 'co_base': 0.6, 'o3_base': 30,
            'winter_pollution_factor': 1.15,
            'monsoon_wash_factor': 0.4
        },
        'Kolkata': {
            'base_temp': 27, 'temp_amp': 9,
            'base_humidity': 70, 'humidity_amp': 20,
            'base_wind': 10, 'wind_amp': 5,
            'pm25_base': 55, 'pm10_base': 110, 'no2_base': 35, 'so2_base': 10, 'co_base': 1.2, 'o3_base': 35,
            'winter_pollution_factor': 1.9,
            'monsoon_wash_factor': 0.3
        }
    }
    
    dates = pd.date_range(start='2024-01-01', end='2025-12-31', freq='D')
    data_list = []
    
    # Set seed for reproducibility
    np.random.seed(42)
    
    for city_name, params in cities.items():
        for date in dates:
            day_of_year = date.dayofyear
            # Determine season factor using cosine wave (min in summer, max in winter/late autumn)
            # 1 = winter/autumn, 0 = monsoon/summer
            season_cos = np.cos(2 * np.pi * (day_of_year - 15) / 365) # Max in Jan
            
            # Climate indicators
            # Temp: Max in May (day ~ 135), Min in Jan (day ~ 15)
            temp_wave = -np.cos(2 * np.pi * (day_of_year - 135) / 365)
            temp = params['base_temp'] + params['temp_amp'] * temp_wave + np.random.normal(0, 1.5)
            
            # Humidity: Max in monsoon (July-Aug, day ~ 210)
            hum_wave = np.cos(2 * np.pi * (day_of_year - 210) / 365)
            humidity = params['base_humidity'] + params['humidity_amp'] * hum_wave + np.random.normal(0, 5)
            humidity = np.clip(humidity, 15, 98)
            
            # Wind speed: High in pre-monsoon/monsoon (May-July)
            wind_wave = np.cos(2 * np.pi * (day_of_year - 165) / 365)
            wind_speed = params['base_wind'] + params['wind_amp'] * wind_wave + np.random.normal(0, 2)
            wind_speed = np.clip(wind_speed, 1, 45)
            
            # Rainfall: high in Monsoon (June - September, day 150 to 270)
            if 152 <= day_of_year <= 273:
                # Rainy days probability
                is_rainy = np.random.choice([0, 1], p=[0.4, 0.6])
                rainfall = is_rainy * (np.random.exponential(15) + 2)
            else:
                is_rainy = np.random.choice([0, 1], p=[0.93, 0.07])
                rainfall = is_rainy * np.random.exponential(3)
                
            # Air Quality calculation
            # Establish base pollution factors with season
            # Winter has high pollution (stubble burning + temperature inversion trapping pollutants)
            # Monsoon has low pollution due to rainwash
            # Wind speed clears pollutants (negative correlation)
            
            # Winter factor: Nov (day 305) to Feb (day 59)
            is_winter = (day_of_year >= 305) or (day_of_year <= 59)
            is_monsoon = (152 <= day_of_year <= 273)
            
            pollution_multiplier = 1.0
            if is_winter:
                # Winter peaks in mid-December/January
                winter_strength = (season_cos + 1) / 2 # 0 to 1
                pollution_multiplier = 1.0 + (params['winter_pollution_factor'] - 1.0) * winter_strength
            elif is_monsoon:
                # Rainfall wash out effect
                pollution_multiplier = 1.0 - (1.0 - params['monsoon_wash_factor']) * (humidity / 100.0)
                
            # Wind speed cleansing effect: higher wind clears particles
            wind_cleansing = 1.0 - 0.015 * (wind_speed - params['base_wind'])
            pollution_multiplier *= np.clip(wind_cleansing, 0.4, 1.6)
            
            # Calculate final concentrations with random fluctuations
            pm25 = params['pm25_base'] * pollution_multiplier + np.random.normal(0, params['pm25_base']*0.15)
            pm10 = params['pm10_base'] * pollution_multiplier + np.random.normal(0, params['pm10_base']*0.15)
            no2 = params['no2_base'] * pollution_multiplier + np.random.normal(0, params['no2_base']*0.1)
            so2 = params['so2_base'] * (1.0 + 0.1 * season_cos) + np.random.normal(0, params['so2_base']*0.1)
            co = params['co_base'] * pollution_multiplier + np.random.normal(0, params['co_base']*0.08)
            
            # Ozone: Max in high solar radiation days (summer, hot, sunny)
            o3_sun_factor = np.clip((temp - 20) / 20.0, 0.1, 1.8)
            o3 = params['o3_base'] * o3_sun_factor * (1.0 - 0.4 * (humidity / 100.0)) + np.random.normal(0, 5)
            
            # Clip variables to be positive
            pm25 = np.clip(pm25, 2, 800)
            pm10 = np.clip(pm10, 5, 1000)
            no2 = np.clip(no2, 1, 300)
            so2 = np.clip(so2, 0.5, 150)
            co = np.clip(co, 0.1, 15)
            o3 = np.clip(o3, 1, 250)
            
            # Calculate actual CPCB AQI
            p_dict = {'PM2.5': pm25, 'PM10': pm10, 'NO2': no2, 'SO2': so2, 'CO': co, 'O3': o3}
            overall_aqi, details, _ = calculate_overall_aqi(p_dict)
            
            data_list.append({
                'Date': date,
                'City': city_name,
                'PM2.5': round(pm25, 1),
                'PM10': round(pm10, 1),
                'NO2': round(no2, 1),
                'SO2': round(so2, 1),
                'CO': round(co, 2),
                'O3': round(o3, 1),
                'Temperature': round(temp, 1),
                'Humidity': round(humidity, 1),
                'WindSpeed': round(wind_speed, 1),
                'Rainfall': round(rainfall, 1),
                'AQI': overall_aqi,
                'AQI_Category': details['category']
            })
            
    df = pd.DataFrame(data_list)
    return df

def inject_custom_css():
    """Inject premium CSS to style the Streamlit app beautifully."""
    st.markdown("""
        <style>
        /* Import Outfit Google Font */
        @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;700;900&display=swap');
        
        html, body, [class*="css"] {
            font-family: 'Outfit', -apple-system, BlinkMacSystemFont, sans-serif;
        }
        
        /* Main Container Customizations */
        .main {
            background-color: #0d1117;
            color: #c9d1d9;
        }
        
        /* Glowing main header */
        .glowing-header {
            font-size: 2.8rem;
            font-weight: 900;
            background: linear-gradient(135deg, #00f2fe 0%, #4facfe 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            text-align: center;
            margin-bottom: 0.5rem;
            text-shadow: 0 0 15px rgba(79, 172, 254, 0.2);
            letter-spacing: -0.5px;
        }
        
        .glowing-subheader {
            font-size: 1.2rem;
            font-weight: 400;
            color: #8b949e;
            text-align: center;
            margin-bottom: 2rem;
        }
        
        /* Premium Card styling (Glassmorphism) */
        .metric-card {
            background: rgba(22, 27, 34, 0.8);
            border: 1px solid rgba(48, 54, 61, 0.8);
            border-radius: 16px;
            padding: 1.5rem;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.25);
            transition: all 0.3s cubic-bezier(0.25, 0.8, 0.25, 1);
            margin-bottom: 1rem;
        }
        
        .metric-card:hover {
            transform: translateY(-5px);
            border-color: #58a6ff;
            box-shadow: 0 8px 30px rgba(88, 166, 255, 0.15);
        }
        
        .metric-title {
            font-size: 0.95rem;
            font-weight: 500;
            color: #8b949e;
            margin-bottom: 0.5rem;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }
        
        .metric-value {
            font-size: 2.2rem;
            font-weight: 700;
            color: #f0f6fc;
            line-height: 1.2;
        }
        
        .metric-unit {
            font-size: 1rem;
            font-weight: 400;
            color: #8b949e;
            margin-left: 0.2rem;
        }
        
        /* Custom Status badge style */
        .status-badge {
            display: inline-block;
            padding: 0.4rem 1rem;
            border-radius: 50px;
            font-weight: 700;
            font-size: 0.9rem;
            text-transform: uppercase;
            letter-spacing: 0.5px;
            text-align: center;
            margin-top: 0.5rem;
            box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
        }
        
        /* Custom sidebar */
        section[data-testid="stSidebar"] {
            background-color: #161b22;
            border-right: 1px solid #30363d;
        }
        
        section[data-testid="stSidebar"] .stMarkdown h1 {
            color: #58a6ff;
            font-weight: 700;
            font-size: 1.5rem;
        }
        
        /* Stylized tabs */
        .stTabs [data-baseweb="tab-list"] {
            gap: 8px;
            background-color: #161b22;
            padding: 8px 12px;
            border-radius: 12px;
            border: 1px solid #30363d;
        }

        .stTabs [data-baseweb="tab"] {
            height: 40px;
            white-space: pre-wrap;
            background-color: transparent;
            border-radius: 8px;
            color: #8b949e;
            font-size: 0.95rem;
            font-weight: 500;
            border: none;
            padding: 0 16px;
            transition: all 0.2s ease;
        }

        .stTabs [data-baseweb="tab"]:hover {
            color: #f0f6fc;
            background-color: #21262d;
        }

        .stTabs [aria-selected="true"] {
            background-color: #30363d !important;
            color: #58a6ff !important;
            font-weight: 700 !important;
        }
        
        /* Progress Bar style */
        .stProgress > div > div > div > div {
            background-color: #58a6ff;
        }
        
        /* Styled warning alert */
        .advisory-box {
            border-left: 5px solid;
            border-radius: 8px;
            padding: 1rem;
            margin-top: 1rem;
            font-size: 0.95rem;
            line-height: 1.5;
        }
        
        </style>
    """, unsafe_allow_html=True)
