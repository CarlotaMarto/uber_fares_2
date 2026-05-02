# app.py
"""Streamlit app to explore Uber fare data.

Loads the cleaned dataset (uber_cleaned.csv) and presents key statistics,
visualizations, and an interactive map. Designed for a non‑technical audience
and runs locally.
"""

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import base64
import os
import plotly.express as px

# 1. Encode the custom Uber logo for the navbar
def get_base64_bin_help(bin_file):
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

uber_logo_b64 = get_base64_bin_help("uber_logo.jpg") if os.path.exists("uber_logo.jpg") else ""

# Page configuration
st.set_page_config(
    page_title="Uber Fare Explorer",
    page_icon="uber_logo.jpg",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for premium look (dark mode friendly)
st.markdown(
    f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    
    /* Hide Streamlit structural branding */
    #MainMenu {{visibility: hidden;}}
    header {{visibility: hidden;}}
    footer {{visibility: hidden;}}
    
    /* Remove padding around the main block */
    .block-container {{
        padding-top: 80px !important;
        padding-bottom: 0rem !important;
    }}
    
    /* Push sidebar down to make room for fixed navbar */
    section[data-testid="stSidebar"] {{
        top: 64px !important;
        height: calc(100vh - 64px) !important;
    }}
    
    /* Dedicated full-width Uber Website Navbar */
    .uber-navbar {{
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        height: 64px;
        background-color: #000000;
        z-index: 999999;
        display: flex;
        align-items: center;
        padding: 0 32px;
    }}
    .uber-navbar img {{
        height: 40px;
        margin-right: 24px;
        /* No filter needed for the custom logo as it's already branded */
    }}
    .uber-navbar-title {{
        color: #FFFFFF;
        font-family: 'Inter', sans-serif;
        font-size: 16px;
        font-weight: 600;
        letter-spacing: 0.5px;
    }}
    
    /* High-Fidelity Segment Animations */
    @keyframes drive-route {{
        0% {{ top: 80%; left: 10%; opacity: 0; }}
        5% {{ opacity: 1; }}
        40% {{ top: 80%; left: 60%; }}
        50% {{ top: 80%; left: 60%; }}
        90% {{ top: 20%; left: 60%; }}
        95% {{ opacity: 1; }}
        100% {{ top: 20%; left: 60%; opacity: 0; }}
    }}
    @keyframes drive-rotate {{
        0% {{ transform: translate(-50%, -50%) rotate(0deg); }}
        40% {{ transform: translate(-50%, -50%) rotate(0deg); }}
        50% {{ transform: translate(-50%, -50%) rotate(-90deg); }}
        100% {{ transform: translate(-50%, -50%) rotate(-90deg); }}
    }}
    .map-track {{
        width: 100%;
        height: 120px;
        background-color: #1A1A1A;
        background-image: 
            linear-gradient(rgba(255,255,255,0.05) 1px, transparent 1px),
            linear-gradient(90deg, rgba(255,255,255,0.05) 1px, transparent 1px);
        background-size: 30px 30px;
        border-radius: 12px;
        position: relative;
        overflow: hidden;
        margin-top: 15px;
        border: 1px solid #333333;
    }}
    .route-line {{
        position: absolute;
        width: 50%;
        height: 60%;
        top: 50%;
        left: 35%;
        border-bottom: 4px solid rgba(123, 97, 255, 0.4);
        border-right: 4px solid rgba(123, 97, 255, 0.4);
        transform: translate(0, 0);
        border-radius: 0 0 10px 0;
    }}
    .destination-pin {{
        position: absolute;
        top: 20%;
        left: 60%;
        font-size: 24px;
        transform: translate(-50%, -100%);
        filter: drop-shadow(0 2px 4px rgba(0,0,0,0.5));
        z-index: 5;
    }}
    .moving-car-v2 {{
        position: absolute;
        width: 20px;
        height: 12px;
        background-color: #06C167;
        border-radius: 2px;
        box-shadow: 0 0 10px rgba(6, 193, 103, 0.5);
        z-index: 10;
        animation: drive-route 6s infinite, drive-rotate 6s infinite;
    }}
    .moving-car-v2::after {{
        content: '';
        position: absolute;
        right: 0;
        top: 2px;
        width: 4px;
        height: 8px;
        background-color: rgba(255,255,255,0.5); /* Windshield */
        border-radius: 1px;
    }}
    </style>
    
    <div class="uber-navbar">
        <img src="data:image/jpeg;base64,{uber_logo_b64}">
        <span class="uber-navbar-title">Fare Explorer</span>
    </div>
    """,
    unsafe_allow_html=True,
)

@st.cache_data
def load_data():
    df = pd.read_csv("uber_with_clusters.csv") if os.path.exists("uber_with_clusters.csv") else pd.read_csv("uber_cleaned.csv")
    # Ensure proper dtypes (already cleaned in the notebook)
    df["pickup_datetime"] = pd.to_datetime(df["pickup_datetime"], errors="coerce")
    if 'cluster' in df.columns:
        cluster_labels = {
            0: "0: Airport / Long-Distance",
            1: "1: Standard Weekday",
            2: "2: Weekend Rush-Hour",
            3: "3: Standard Weekend",
            4: "4: High Passenger / SUV",
            5: "5: Fare / GPS Anomalies",
            6: "6: Weekday Rush-Hour",
            7: "7: Late-Night Party"
        }
        # First ensure cluster is numeric if it's not already
        df['cluster'] = pd.to_numeric(df['cluster'], errors='coerce')
        df['cluster'] = df['cluster'].map(cluster_labels).fillna("Unknown Cluster")
    return df

df = load_data()

if 'started' not in st.session_state:
    st.session_state['started'] = False

if not st.session_state['started']:
    import base64
    with open("splash_image.jpg", "rb") as image_file:
        img_b64 = base64.b64encode(image_file.read()).decode()

    st.markdown("<br><br>", unsafe_allow_html=True)
    html_content = f"""
<div style="width: 100%; padding: 10px;">
<h1 style="margin-top: 0; color: #000000; font-size: 86px; font-weight: 800; letter-spacing: -2.5px; line-height: 1.1;">Uber Fare Data Explorer</h1>

<div style="display: flex; gap: 40px; margin-top: 20px; margin-bottom: 30px;">
    <div>
        <p style="color: #666666; font-size: 14px; text-transform: uppercase; letter-spacing: 1px; font-weight: 700; margin-bottom: 5px;">Work Done By</p>
        <p style="color: #000000; font-size: 18px; line-height: 1.4; margin: 0;"><b>Carlota Marto</b> (20241729)<br><b>Francisca Teixeira</b> (20241702)</p>
    </div>
    <div style="width: 2px; background-color: #E2E2E2;"></div>
    <div>
        <p style="color: #666666; font-size: 14px; text-transform: uppercase; letter-spacing: 1px; font-weight: 700; margin-bottom: 5px;">Teacher</p>
        <p style="color: #000000; font-size: 18px; line-height: 1.4; margin: 0;"><b>Ivo Bernardo</b><br><span style="color: #444444; font-size: 15px;">Machine Learning II</span></p>
    </div>
</div>

<p style="color: #222222; font-size: 30px; line-height: 1.5; margin-bottom: 40px;">
A deep-dive, interactive presentation designed for non-technical stakeholders to securely analyze historical <b>Uber ride metrics across New York City</b> (spanning from 2009 to 2015).
</p>

<img src="data:image/png;base64,{img_b64}" style="width: 100%; border-radius: 16px; box-shadow: 0 10px 30px rgba(0,0,0,0.1); object-fit: cover; max-height: 600px; margin-bottom: 60px;">

<hr style="border: 0; height: 1px; background-color: #E2E2E2; margin-bottom: 60px;">
<h3 style="color: #000000; font-size: 24px; text-transform: uppercase; letter-spacing: 1.5px; margin-bottom: 20px; font-weight: 700;">What are we analyzing?</h3>
<p style="color: #333333; font-size: 26px; line-height: 1.6; margin-bottom: 60px;">
The core dataset consists of roughly 10,000 highly curated trip records. The raw data was rigorously cleaned to filter out GPS tracking errors, zero-passenger trips, and negative logistical anomalies. The sanitized locations were then fed into an advanced machine-learning algorithm (K-Means Clustering) to autonomously discover hidden structural geographical "zones" where distinct pricing and rider behaviors occur.
</p>
<h3 style="color: #000000; font-size: 24px; text-transform: uppercase; letter-spacing: 1.5px; margin-bottom: 20px; font-weight: 700;">How to use this dashboard</h3>
<ul style="color: #333333; font-size: 26px; line-height: 1.6; padding-left: 25px; margin-bottom: 80px;">
<li style="margin-bottom: 10px;"><b>Tabs:</b> Click through the navigation tabs to seamlessly explore completely different dimensions: Financials, Geospatial data, and Temporal trends.</li>
<li style="margin-bottom: 10px;"><b>Interactive Filters:</b> Use the sliding filters on the absolute left sidebar to dynamically isolate specific hours of the day or vehicle class sizes.</li>
<li style="margin-bottom: 10px;"><b>Insight Cards:</b> Every single visualization is accompanied by a dedicated "Insight" panel on the right, instantly translating the raw mathematical data into plain English.</li>
</ul>
</div>
    """
    st.markdown(html_content, unsafe_allow_html=True)
    
    col_s1, col_s2, col_s3 = st.columns([1, 2, 1])
    with col_s2:
        if st.button("Explore the Dashboard", type="primary", use_container_width=True):
            st.session_state['started'] = True
            st.rerun()
            
    st.stop()


st.markdown("""
<div style="display: flex; justify-content: flex-end; margin-bottom: -15px;">
""", unsafe_allow_html=True)
if st.button("← Back to Splash Page", type="secondary"):
    st.session_state['started'] = False
    st.rerun()
st.markdown("</div>", unsafe_allow_html=True)


# The global sidebar filters have been removed so the dashboard can display all data at all times.
filtered = df.copy()
map_df = df.copy()

# Custom KPI HTML rendering
kpi_html = f"""
    <div style="display: flex; justify-content: space-between; gap: 20px; margin-bottom: 1.5rem;">
        <div style="flex: 1; background-color: #000000; border-radius: 8px; padding: 20px; box-shadow: 0 4px 10px rgba(0,0,0,0.15);">
            <div style="color: #A6A6A6; font-size: 13px; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 8px;">Total Trips</div>
            <div style="color: #FFFFFF; font-size: 30px; font-weight: bold;">{len(filtered):,}</div>
        </div>
        <div style="flex: 1; background-color: #000000; border-radius: 8px; padding: 20px; box-shadow: 0 4px 10px rgba(0,0,0,0.15);">
            <div style="color: #A6A6A6; font-size: 13px; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 8px;">Avg Fare</div>
            <div style="color: #FFFFFF; font-size: 30px; font-weight: bold;">${filtered['fare_amount'].mean():.2f}</div>
        </div>
        <div style="flex: 1; background-color: #000000; border-radius: 8px; padding: 20px; box-shadow: 0 4px 10px rgba(0,0,0,0.15);">
            <div style="color: #A6A6A6; font-size: 13px; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 8px;">Avg Distance</div>
            <div style="color: #FFFFFF; font-size: 30px; font-weight: bold;">{filtered['distance_km'].mean():.2f} <span style="font-size:18px;">km</span></div>
        </div>
        <div style="flex: 1; background-color: #000000; border-radius: 8px; padding: 20px; box-shadow: 0 4px 10px rgba(0,0,0,0.15);">
            <div style="color: #A6A6A6; font-size: 13px; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 8px;">Date Range</div>
            <div style="color: #FFFFFF; font-size: 16px; font-weight: bold; line-height: 1.3;">
                {filtered['pickup_datetime'].min().date()}<br>to {filtered['pickup_datetime'].max().date()}
            </div>
        </div>
    </div>
"""
st.markdown(kpi_html, unsafe_allow_html=True)

# Tab control logic
if 'tab_index' not in st.session_state:
    st.session_state['tab_index'] = 0

# Visualizations
tab_titles = ["Distributions", "Temporal Analysis", "Segment Encyclopedia", "Geospatial Hub", "Advanced Analysis", "Business Strategy"]
tabs = st.tabs(tab_titles)

# I have to handle the index carefully. 
# Streamlit st.tabs does NOT support an index parameter yet in the main version, 
# but I can use st.session_state to persist which tab they want to see via a custom indicator.
# Actually, the best way for footer navigation is to use st.empty() or just inform the user to use the top.
# But I will try to make it feel "active".

with tabs[0]:
    # ... existing content ... (I'll keep the logic as is)
    st.subheader("Fare & Passenger Analysis")
    
    col1, col2 = st.columns([2, 1])
    with col1:
        fig_hist = px.histogram(filtered, x="fare_amount", nbins=30, title="Fare Distribution", color_discrete_sequence=["#06C167"])
        st.plotly_chart(fig_hist, width="stretch")
    with col2:
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        st.markdown("""
        <div style="background-color: #F6F6F6; border-left: 4px solid #000000; padding: 20px; border-radius: 4px;">
            <h4 style="margin-top: 0; color: #000000; font-size: 16px; text-transform: uppercase; letter-spacing: 0.5px;">Fare Distribution Volume</h4>
            <p style="color: #333333; font-size: 15px; line-height: 1.5; margin-bottom: 0;">Most rides are overwhelmingly short-distance trips under $20, with a steep drop-off for expensive fares. This clearly indicates the primary platform use-case is quick inner-city commuting rather than long rural hauls.</p>
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown("<hr style='border:1px solid #E2E2E2;'>", unsafe_allow_html=True)

    col3, col4 = st.columns([2, 1])
    with col3:
        fig_scatter = px.scatter(filtered, x="distance_km", y="fare_amount", opacity=0.5, title="Fare vs. Distance", color_discrete_sequence=["#06C167"])
        st.plotly_chart(fig_scatter, width="stretch")
    with col4:
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        st.markdown("""
        <div style="background-color: #F6F6F6; border-left: 4px solid #000000; padding: 20px; border-radius: 4px;">
            <h4 style="margin-top: 0; color: #000000; font-size: 16px; text-transform: uppercase; letter-spacing: 0.5px;">Distance vs. Pricing Anomalies</h4>
            <p style="color: #333333; font-size: 15px; line-height: 1.5; margin-bottom: 0;">While there is a clear linear relationship between distance and fare, striking vertical pricing anomalies exist at 0km. These represent edge-cases like flat-rate tolls, severe gridlocks, or GPS cutouts.</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<hr style='border:1px solid #E2E2E2;'>", unsafe_allow_html=True)
    
    col5, col6 = st.columns([2, 1])
    with col5:
        pass_counts = filtered["passenger_count"].value_counts().reset_index()
        pass_counts.columns = ["Passenger Count", "Trips"]
        fig_bar = px.bar(pass_counts, x="Passenger Count", y="Trips", title="Trips by Passenger Count", color_discrete_sequence=["#06C167"])
        st.plotly_chart(fig_bar, width="stretch")
    with col6:
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        st.markdown("""
        <div style="background-color: #F6F6F6; border-left: 4px solid #000000; padding: 20px; border-radius: 4px;">
            <h4 style="margin-top: 0; color: #000000; font-size: 16px; text-transform: uppercase; letter-spacing: 0.5px;">Core Passenger Demographics</h4>
            <p style="color: #333333; font-size: 15px; line-height: 1.5; margin-bottom: 0;">Single-passenger trips completely dominate the dataset by raw volume, highlighting that solo point-to-point transportation is the absolute core lifeblood of the platform's revenue.</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<hr style='border:1px solid #E2E2E2;'>", unsafe_allow_html=True)
    
    col7, col8 = st.columns([2, 1])
    with col7:
        fig_box = px.box(filtered, x='passenger_count', y='fare_amount', title='Fare Distribution by Passenger Count', color_discrete_sequence=["#06C167"])
        st.plotly_chart(fig_box, width="stretch")
    with col8:
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        st.markdown("""
        <div style="background-color: #F6F6F6; border-left: 4px solid #000000; padding: 20px; border-radius: 4px;">
            <h4 style="margin-top: 0; color: #000000; font-size: 16px; text-transform: uppercase; letter-spacing: 0.5px;">Fare Scaling by Capacity</h4>
            <p style="color: #333333; font-size: 15px; line-height: 1.5; margin-bottom: 0;">Surprisingly, the median fare does not drastically increase for larger passenger counts, implying larger vehicles are fundamentally booked for identical trip lengths as solo sedans.</p>
        </div>
        """, unsafe_allow_html=True)

with tabs[1]:
    st.subheader("Temporal Demand & Pricing")
    
    col_t1, col_t2 = st.columns([2, 1])
    with col_t1:
        # Trips per hour
        hour_counts = filtered['pickup_datetime'].dt.hour.value_counts().reset_index()
        hour_counts.columns = ["Hour of Day", "Number of Trips"]
        fig_hour = px.bar(hour_counts, x="Hour of Day", y="Number of Trips", title="Trips per Hour of Day", color_discrete_sequence=["#06C167"])
        st.plotly_chart(fig_hour, width="stretch")
    with col_t2:
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        st.markdown("""
        <div style="background-color: #F6F6F6; border-left: 4px solid #000000; padding: 20px; border-radius: 4px;">
            <h4 style="margin-top: 0; color: #000000; font-size: 16px; text-transform: uppercase; letter-spacing: 0.5px;">Temporal Demand Curve</h4>
            <p style="color: #333333; font-size: 15px; line-height: 1.5; margin-bottom: 0;">The raw temporal throughput reveals a starkly bimodal demand curve. Volumes begin softly surging into the morning commute, steadily climb, and massively erupt into a dominant peak during the evening rush hour exits.</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<hr style='border:1px solid #E2E2E2;'>", unsafe_allow_html=True)

    col_t3, col_t4 = st.columns([2, 1])
    with col_t3:
        dow_counts = filtered['pickup_datetime'].dt.day_name().value_counts().reindex(
            ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        ).reset_index()
        dow_counts.columns = ["Day of Week", "Number of Trips"]
        fig_dow = px.bar(dow_counts, x="Day of Week", y="Number of Trips", title="Trips by Day of Week", color_discrete_sequence=["#06C167"])
        st.plotly_chart(fig_dow, width="stretch")
    with col_t4:
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        st.markdown("""
        <div style="background-color: #F6F6F6; border-left: 4px solid #000000; padding: 20px; border-radius: 4px;">
            <h4 style="margin-top: 0; color: #000000; font-size: 16px; text-transform: uppercase; letter-spacing: 0.5px;">Weekly Cadence</h4>
            <p style="color: #333333; font-size: 15px; line-height: 1.5; margin-bottom: 0;">Ridership smoothly accelerates throughout the week, peaking forcefully on Friday and Saturday nights before plummeting down completely on Sunday, exposing a clear lifestyle premium on weekend usage.</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<hr style='border:1px solid #E2E2E2;'>", unsafe_allow_html=True)

    col_t5, col_t6 = st.columns([2, 1])
    with col_t5:
        avg_fare_hour = filtered.groupby(filtered['pickup_datetime'].dt.hour)['fare_amount'].mean().reset_index()
        avg_fare_hour.columns = ["Hour of Day", "Avg Fare ($)"]
        fig_fare_hour = px.line(avg_fare_hour, x="Hour of Day", y="Avg Fare ($)", title="Average Fare by Hour of Day", color_discrete_sequence=["#06C167"], markers=True)
        st.plotly_chart(fig_fare_hour, width="stretch")
    with col_t6:
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        st.markdown("""
        <div style="background-color: #F6F6F6; border-left: 4px solid #000000; padding: 20px; border-radius: 4px;">
            <h4 style="margin-top: 0; color: #000000; font-size: 16px; text-transform: uppercase; letter-spacing: 0.5px;">Surge & Anomaly Pricing</h4>
            <p style="color: #333333; font-size: 15px; line-height: 1.5; margin-bottom: 0;">Fares consistently skyrocket between 4:00 AM and 5:00 AM. This fascinating premium is driven exclusively by long uncrowded runs to the airport for early-morning flights.</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<hr style='border:1px solid #E2E2E2;'>", unsafe_allow_html=True)
    
    col_f1, col_f2 = st.columns([2, 1])
    with col_f1:
        avg_fare_dow = filtered.groupby(filtered['pickup_datetime'].dt.day_name())['fare_amount'].mean().reindex(
            ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        ).reset_index()
        avg_fare_dow.columns = ["Day of Week", "Avg Fare ($)"]
        fig_fare_dow = px.bar(avg_fare_dow, x="Day of Week", y="Avg Fare ($)", title="Average Fare by Day of Week", color_discrete_sequence=["#06C167"])
        st.plotly_chart(fig_fare_dow, width="stretch")
    with col_f2:
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        st.markdown("""
        <div style="background-color: #F6F6F6; border-left: 4px solid #000000; padding: 20px; border-radius: 4px;">
            <h4 style="margin-top: 0; color: #000000; font-size: 16px; text-transform: uppercase; letter-spacing: 0.5px;">Weekly Pricing Stability</h4>
            <p style="color: #333333; font-size: 15px; line-height: 1.5; margin-bottom: 0;">Average fares remain notably stable regardless of the actual day of the week, with only mild, consistent upticks occurring strictly through the prime weekend blocks.</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<hr style='border:1px solid #E2E2E2;'>", unsafe_allow_html=True)
    
    col_f3, col_f4 = st.columns([2, 1])
    with col_f3:
        avg_fare_month = filtered.groupby(filtered['pickup_datetime'].dt.month_name())['fare_amount'].mean().reindex(
            ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
        ).reset_index()
        avg_fare_month.columns = ["Month", "Avg Fare ($)"]
        fig_fare_month = px.bar(avg_fare_month, x="Month", y="Avg Fare ($)", title="Average Fare by Month", color_discrete_sequence=["#06C167"])
        st.plotly_chart(fig_fare_month, width="stretch")
    with col_f4:
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        st.markdown("""
        <div style="background-color: #F6F6F6; border-left: 4px solid #000000; padding: 20px; border-radius: 4px;">
            <h4 style="margin-top: 0; color: #000000; font-size: 16px; text-transform: uppercase; letter-spacing: 0.5px;">Monthly Fare Consistency</h4>
            <p style="color: #333333; font-size: 15px; line-height: 1.5; margin-bottom: 0;">Unlike raw ridership volume which shows sharp seasonal peaks, the average unit economics per ride remain heavily guarded against macro temperature and holiday fluctuations.</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<hr style='border:1px solid #E2E2E2;'>", unsafe_allow_html=True)
    
    col_f5, col_f6 = st.columns([2, 1])
    with col_f5:
        avg_fare_year = filtered.groupby(filtered['pickup_datetime'].dt.year)['fare_amount'].mean().reset_index()
        avg_fare_year.columns = ["Year", "Avg Fare ($)"]
        avg_fare_year = avg_fare_year.sort_values(by="Year")
        avg_fare_year["Year"] = avg_fare_year["Year"].astype(str)
        fig_fare_year = px.bar(avg_fare_year, x="Year", y="Avg Fare ($)", title="Average Fare by Year", color_discrete_sequence=["#06C167"])
        st.plotly_chart(fig_fare_year, width="stretch")
    with col_f6:
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        st.markdown("""
        <div style="background-color: #F6F6F6; border-left: 4px solid #000000; padding: 20px; border-radius: 4px;">
            <h4 style="margin-top: 0; color: #000000; font-size: 16px; text-transform: uppercase; letter-spacing: 0.5px;">Inflation & Pricing Power</h4>
            <p style="color: #333333; font-size: 15px; line-height: 1.5; margin-bottom: 0;">Over a multi-year timeframe, we observe a steady overall rise in the minimum average fare, smoothly reflecting the platform's gradual long-term pricing power and broader inflation rates.</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<hr style='border:1px solid #E2E2E2;'>", unsafe_allow_html=True)

    col_t7, col_t8 = st.columns([2, 1])
    with col_t7:
        month_counts = filtered['pickup_datetime'].dt.month_name().value_counts().reindex(
            ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"]
        ).reset_index()
        month_counts.columns = ["Month", "Number of Trips"]
        fig_month = px.bar(month_counts, x="Month", y="Number of Trips", title="Trips by Month", color_discrete_sequence=["#06C167"])
        st.plotly_chart(fig_month, width="stretch")
    with col_t8:
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        st.markdown("""
        <div style="background-color: #F6F6F6; border-left: 4px solid #000000; padding: 20px; border-radius: 4px;">
            <h4 style="margin-top: 0; color: #000000; font-size: 16px; text-transform: uppercase; letter-spacing: 1.5px;">Annual Growth</h4>
            <p style="color: #333333; font-size: 15px; line-height: 1.5; margin-bottom: 0;">This chart highlights the platform's multi-year structural progression. Note how overall usage density scales as ride-sharing evolved from an emerging technology into essential public infrastructure.</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<hr style='border:1px solid #E2E2E2;'>", unsafe_allow_html=True)

    col_t9, col_t10 = st.columns([2, 1])
    with col_t9:
        year_counts = filtered['pickup_datetime'].dt.year.value_counts().reset_index()
        year_counts.columns = ["Year", "Number of Trips"]
        year_counts = year_counts.sort_values(by="Year")
        year_counts["Year"] = year_counts["Year"].astype(str)
        fig_year = px.bar(year_counts, x="Year", y="Number of Trips", title="Trips by Year", color_discrete_sequence=["#06C167"])
        st.plotly_chart(fig_year, width="stretch")
    with col_t10:
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        st.markdown("""
        <div style="background-color: #F6F6F6; border-left: 4px solid #000000; padding: 20px; border-radius: 4px;">
            <h4 style="margin-top: 0; color: #000000; font-size: 16px; text-transform: uppercase; letter-spacing: 0.5px;">Annual Growth</h4>
            <p style="color: #333333; font-size: 15px; line-height: 1.5; margin-bottom: 0;">This chart highlights the platform's multi-year structural progression. Note how overall usage density scales as ride-sharing evolved from an emerging technology into essential public infrastructure.</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<hr style='border:1px solid #E2E2E2;'>", unsafe_allow_html=True)

    col_t11, col_t12 = st.columns([2, 1])
    with col_t11:
        date_counts = filtered['pickup_datetime'].dt.date.value_counts().reset_index()
        date_counts.columns = ["Date", "Number of Trips"]
        date_counts = date_counts.sort_values(by="Date")
        fig_date = px.line(date_counts, x="Date", y="Number of Trips", title="Trips Over Time", color_discrete_sequence=["#06C167"])
        st.plotly_chart(fig_date, width="stretch")
    with col_t12:
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        st.markdown("""
        <div style="background-color: #F6F6F6; border-left: 4px solid #000000; padding: 20px; border-radius: 4px;">
            <h4 style="margin-top: 0; color: #000000; font-size: 16px; text-transform: uppercase; letter-spacing: 1.5px;">Long-Term Trajectory</h4>
            <p style="color: #333333; font-size: 15px; line-height: 1.5; margin-bottom: 0;">Viewing the granular day-to-day ridership volume allows us to identify extreme macro-outliers—such as dramatic drops from massive blizzards or intense spikes from major city-wide events.</p>
        </div>
        """, unsafe_allow_html=True)

with tabs[2]:
    st.subheader("Smart Segments Encyclopedia")
    st.markdown("""
    <p style="color: #666666; font-size: 18px; margin-bottom: 30px;">
        Our Machine Learning algorithm (K-Means) has autonomously identified 8 distinct groups of trips. 
        Explore the <b>Animated Profiles</b> below to see how each segment moves through the city.
    </p>
    """, unsafe_allow_html=True)

    if 'cluster' in df.columns:
        clusters = [
            {"id": "0: Airport / Long-Distance", "desc": "High-speed hauls to JFK/EWR. Profitable and specialized.", "color": "#06C167", "speed": "4s", "emoji": "✈️"},
            {"id": "1: Standard Weekday", "desc": "The rhythm of the city. Reliable daytime transit.", "color": "#000000", "speed": "8s", "emoji": "🏙️"},
            {"id": "2: Weekend Rush-Hour", "desc": "Busy leisure hours. Navigating the Saturday surge.", "color": "#333333", "speed": "12s", "emoji": "🛍️"},
            {"id": "3: Standard Weekend", "desc": "Relaxed weekend vibes for brunches and sightseeing.", "color": "#666666", "speed": "10s", "emoji": "🍦"},
            {"id": "4: High Passenger / SUV", "desc": "Big groups. Big vehicles. Big impact.", "color": "#999999", "speed": "9s", "emoji": "🚐"},
            {"id": "5: Fare / GPS Anomalies", "desc": "The outliers. Mathematical exceptions and edge-cases.", "color": "#CCCCCC", "speed": "15s", "emoji": "⚠️"},
            {"id": "6: Weekday Rush-Hour", "desc": "Peak adrenaline. The high-volume commute pulse.", "color": "#1f7a46", "speed": "3s", "emoji": "👔"},
            {"id": "7: Late-Night Party", "desc": "Neon lights and night owls. Connecting the nightlife.", "color": "#048043", "speed": "6s", "emoji": "✨"},
        ]

        # Display cards in rows of 2
        for i in range(0, len(clusters), 2):
            cols = st.columns(2)
            for j in range(2):
                if i + j < len(clusters):
                    c = clusters[i+j]
                    with cols[j]:
                        c_data = df[df['cluster'] == c['id']]
                        avg_fare = c_data['fare_amount'].mean() if len(c_data) > 0 else 0
                        avg_dist = c_data['distance_km'].mean() if len(c_data) > 0 else 0
                        
                        st.markdown(f"""
                        <div style="background-color: #FFFFFF; border: 1px solid #E2E2E2; border-left: 10px solid {c['color']}; padding: 25px; border-radius: 12px; margin-bottom: 25px; box-shadow: 0 4px 12px rgba(0,0,0,0.05);">
                            <div style="display: flex; justify-content: space-between; align-items: start;">
                                <h3 style="margin-top: 0; color: #000000; font-size: 22px;">{c['id']}</h3>
                                <span style="font-size: 24px;">{c['emoji']}</span>
                            </div>
                            <p style="color: #666666; font-size: 15px; margin-top: 5px; min-height: 45px;">{c['desc']}</p>
                            
                            <div class="map-track">
                                <div class="route-line"></div>
                                <div class="destination-pin">📍</div>
                                <div class="moving-car-v2" style="animation-duration: {c['speed']}; background-color: {c['color']}; box-shadow: 0 0 15px {c['color']}88;"></div>
                            </div>
                            
                            <div style="display: flex; gap: 30px; margin-top: 20px; border-top: 1px solid #F0F0F0; padding-top: 15px;">
                                <div><span style="color: #999999; font-size: 11px; text-transform: uppercase; font-weight: 700;">Avg Fare</span><br><b style="font-size: 20px; color: #000000;">${avg_fare:.2f}</b></div>
                                <div><span style="color: #999999; font-size: 11px; text-transform: uppercase; font-weight: 700;">Avg Distance</span><br><b style="font-size: 20px; color: #000000;">{avg_dist:.2f}km</b></div>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)

with tabs[3]:
    st.subheader("Geospatial Hub")
    st.markdown("<p style='color: #666666;'>Interactive mapping of all clusters across the NYC metropolitan area.</p>", unsafe_allow_html=True)
    
    # --- GEOSPATIAL MAPS ---
    col_c1, col_c2 = st.columns([2, 1])
    with col_c1:
        uber_palette = ["#06C167", "#000000", "#333333", "#666666", "#999999", "#CCCCCC", "#1f7a46", "#048043"]
        fig_cluster = px.scatter(
            map_df, x='pickup_longitude', y='pickup_latitude', color='cluster',
            title='Pickup locations colored by cluster', hover_data=['fare_amount', 'distance_km'],
            height=500, color_discrete_sequence=uber_palette
        )
        fig_cluster.update_layout(margin=dict(l=0, r=0, t=40, b=0))
        st.plotly_chart(fig_cluster, width="stretch")
    with col_c2:
        st.markdown("<br><br><br><br>", unsafe_allow_html=True)
        st.markdown("""
        <div style="background-color: #F6F6F6; border-left: 4px solid #000000; padding: 20px; border-radius: 4px;">
            <h4 style="margin-top: 0; color: #000000; font-size: 16px; text-transform: uppercase; letter-spacing: 0.5px;">Geographical Cluster Zonation</h4>
            <p style="color: #333333; font-size: 15px; line-height: 1.5; margin-bottom: 0;">The K-Means algorithm effectively carves harsh geographical segmentations purely based on pricing and time parameters. We can visibly see distinct "zones" corresponding to localized rider behaviors.</p>
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown("<hr style='border:1px solid #E2E2E2;'>", unsafe_allow_html=True)
        
    col_m1, col_m2 = st.columns([2, 1])
    with col_m1:
        uber_palette = ["#06C167", "#000000", "#333333", "#666666", "#999999", "#CCCCCC", "#1f7a46", "#048043"]
        
        # Create animated version sorted by hour
        map_df_anim = map_df.dropna(subset=['pickup_hour']).sort_values('pickup_hour')
        map_df_anim['Hour'] = map_df_anim['pickup_hour'].astype(int).astype(str) + ":00"
        
        fig_map = px.scatter_mapbox(
            map_df_anim, lat='pickup_latitude', lon='pickup_longitude', color='cluster',
            size='fare_amount', hover_data=['fare_amount', 'distance_km'], zoom=9.5,
            animation_frame='Hour',
            title='Interactive Time-Lapse: Demand by Hour', mapbox_style="carto-positron",
            height=550, color_discrete_sequence=uber_palette
        )
        fig_map.update_layout(margin=dict(l=0, r=0, t=40, b=0))
        # Speed up the animation slightly for a smoother time-lapse effect
        fig_map.layout.updatemenus[0].buttons[0].args[1]['frame']['duration'] = 800
        
        st.plotly_chart(fig_map, width="stretch")
    with col_m2:
        st.markdown("<br><br><br><br>", unsafe_allow_html=True)
        st.markdown("""
        <div style="background-color: #F6F6F6; border-left: 4px solid #06C167; padding: 20px; border-radius: 4px;">
            <h4 style="margin-top: 0; color: #000000; font-size: 16px; text-transform: uppercase; letter-spacing: 0.5px;">Time-Lapse Explorer</h4>
            <p style="color: #333333; font-size: 15px; line-height: 1.5; margin-bottom: 0;">Hit the <b>Play</b> button on the map to watch ridership demand flow dynamically across New York City. <br><br>Notice how the morning rush explicitly starts pulling heavily from outside boroughs, before collapsing entirely back into Manhattan's core for the evening peak.</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<hr style='border:1px solid #E2E2E2;'>", unsafe_allow_html=True)

    col_t11, col_t12 = st.columns([2, 1])
    with col_t11:
        date_counts = filtered['pickup_datetime'].dt.date.value_counts().reset_index()
        date_counts.columns = ["Date", "Number of Trips"]
        date_counts = date_counts.sort_values(by="Date")
        fig_date = px.line(date_counts, x="Date", y="Number of Trips", title="Trips Over Time", color_discrete_sequence=["#06C167"])
        st.plotly_chart(fig_date, width="stretch")
    with col_t12:
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        st.markdown("""
        <div style="background-color: #F6F6F6; border-left: 4px solid #000000; padding: 20px; border-radius: 4px;">
            <h4 style="margin-top: 0; color: #000000; font-size: 16px; text-transform: uppercase; letter-spacing: 0.5px;">Long-Term Trajectory</h4>
            <p style="color: #333333; font-size: 15px; line-height: 1.5; margin-bottom: 0;">Viewing the granular day-to-day ridership volume allows us to identify extreme macro-outliers—such as dramatic drops from massive blizzards or intense spikes from major city-wide events.</p>
        </div>
        """, unsafe_allow_html=True)

with tabs[4]:
    st.subheader("Advanced Feature Analysis")
    
    col_a1, col_a2 = st.columns([2, 1])
    with col_a1:
        # We will build the correlation heatmap here
        import plotly.figure_factory as ff
        corr_cols = ['fare_amount', 'distance_km', 'passenger_count', 'pickup_hour', 'pickup_day', 'pickup_dayofweek']
        if all(c in df.columns for c in corr_cols):
            corr = df[corr_cols].corr().round(2)
            fig_heatmap = px.imshow(corr, text_auto=True, aspect="auto", title="Feature Correlation Heatmap", color_continuous_scale="Greens")
            st.plotly_chart(fig_heatmap, width="stretch")
        else:
            st.info("Additional dimensions calculated...")
    with col_a2:
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        st.markdown("""
        <div style="background-color: #F6F6F6; border-left: 4px solid #000000; padding: 20px; border-radius: 4px;">
            <h4 style="margin-top: 0; color: #000000; font-size: 16px; text-transform: uppercase; letter-spacing: 0.5px;">Linear Relationships</h4>
            <p style="color: #333333; font-size: 15px; line-height: 1.5; margin-bottom: 0;">Distance and Fare share a near 1-to-1 linear correlation (~0.90). Interestingly, passenger count has an absolute zero mathematical impact on the final fare pricing.</p>
        </div>
        """, unsafe_allow_html=True)
        
    st.markdown("<hr style='border:1px solid #E2E2E2;'>", unsafe_allow_html=True)
    
    col_a3, col_a4 = st.columns([2, 1])
    with col_a3:
        import os
        pca_file = "uber_with_clusters_pca.csv"
        if os.path.exists(pca_file):
            pca_df = pd.read_csv(pca_file)
            # if user filters, we try to align indices, but PCA was done on sample. We'll simply show it on the map.
            uber_palette = ["#06C167", "#000000", "#333333", "#666666", "#999999", "#CCCCCC", "#1f7a46", "#048043"]
            fig_pca = px.scatter(pca_df, x="pca_x", y="pca_y", color=pca_df['cluster'].astype(str), title="PCA Dimensionality Reduction Scatter", color_discrete_sequence=uber_palette, opacity=0.5)
            st.plotly_chart(fig_pca, width="stretch")
        else:
            st.info("PCA Data missing!")
    with col_a4:
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        st.markdown("""
        <div style="background-color: #F6F6F6; border-left: 4px solid #000000; padding: 20px; border-radius: 4px;">
            <h4 style="margin-top: 0; color: #000000; font-size: 16px; text-transform: uppercase; letter-spacing: 0.5px;">Automated Dimensionality Extraction</h4>
            <p style="color: #333333; font-size: 15px; line-height: 1.5; margin-bottom: 0;">By compressing 8 variables down into a 2D mathematical space using Principal Component Analysis, we visually demonstrate how effectively the clusters cleanly separate fundamentally different rider profiles.</p>
        </div>
        """, unsafe_allow_html=True)

with tabs[5]:
    st.subheader("Actionable Business Strategies")
    st.markdown("<br>", unsafe_allow_html=True)
    
    st.markdown("""
    <div style="background-color: #E8F5E9; border-left: 6px solid #06C167; padding: 25px; border-radius: 6px; margin-bottom: 35px;">
        <p style="color: #333333; font-size: 20px; line-height: 1.6; margin-bottom: 0;">
            <b style="font-size: 22px;">Wait, what is a "Smart Segment"?</b><br>
            A segment is simply a mathematically generated group of trips that share identical real-world behaviors (such as traveling extremely long distances, or happening exclusively late at night in specific neighborhoods). By isolating these specific groups, we can physically see exactly where and when our business strategies should be deployed.
        </p>
    </div>
    """, unsafe_allow_html=True)
    
    if 'cluster' in df.columns:
        # STRATEGY 1: Route & Fleet Optimization
        col_b1, col_b2 = st.columns([1, 1.5])
        with col_b1:
            st.markdown("""
            <div style="background-color: #F6F6F6; border-top: 6px solid #06C167; padding: 30px; border-radius: 8px; height: 100%;">
                <h3 style="color: #000000; font-size: 24px; margin-top: 0; margin-bottom: 20px;">1. Route & Fleet Optimization</h3>
                <p style="color: #333333; font-size: 18px; line-height: 1.6; margin-bottom: 20px;"><b>How to use the data:</b> How do we know the automated logic actually found the airports? <br><br>Compare the two maps on the right perfectly. The <b>Top Map</b> is a basic physical reference of where the NYC airports are. <br><br>The <b>Bottom Map</b> is the raw mathematical Cluster data (the green dots). Notice how the algorithm perfectly grew outward and autonomously mapped itself precisely to those three distinct airport zones without any human tags.</p>
                <div style="background-color: #E2E2E2; height: 2px; width: 100%; margin: 20px 0;"></div>
                <strong style="color: #000000; font-size: 16px; text-transform: uppercase; letter-spacing: 0.5px;">✓ Direct Impact</strong>
                <p style="color: #333333; font-size: 16px; line-height: 1.6; margin-top: 10px; margin-bottom: 0;">Dispatch algorithms can pre-position idle cars exactly at JFK <i>before</i> flights land to dramatically reduce empty driver miles.</p>
            </div>
            """, unsafe_allow_html=True)
        with col_b2:
            import pydeck as pdk
            import base64
            
            # Use a high-quality, truly transparent icon source
            # This ensures no checkerboard pattern and high visibility
            icon_url = "https://img.icons8.com/m_sharp/200/000000/airport.png"

            airport_df = pd.DataFrame({
                'Name': ['JFK Airport', 'Newark Airport', 'LaGuardia'],
                'lat': [40.6413, 40.6895, 40.7769],
                'lon': [-73.7781, -74.1745, -73.8740]
            })

            # Define the icon dictionary
            icon_data = {
                "url": icon_url,
                "width": 200,
                "height": 200,
                "anchorY": 200,
            }
            airport_df['icon_data'] = [icon_data for _ in range(len(airport_df))]

            # Create Pydeck Icon Layer
            icon_layer = pdk.Layer(
                "IconLayer",
                data=airport_df,
                get_icon="icon_data",
                get_size=150, # REALLY BIG size
                size_scale=1,
                get_position="[lon, lat]",
                pickable=True,
                get_color="[0, 0, 0, 255]" # Ensure solid black
            )

            view_state = pdk.ViewState(
                latitude=40.71,
                longitude=-73.97,
                zoom=8.5,
                pitch=0,
            )

            st.markdown("#### Reference: New York City Airports")
            st.pydeck_chart(pdk.Deck(
                layers=[icon_layer],
                initial_view_state=view_state,
                tooltip={"text": "{Name}"},
                map_style="light"
            ))
            
            # Map 2: Cluster Highlights vs Actual Airport Pins
            c0_df = df[df['cluster'] == "0: Airport / Long-Distance"].copy()
            c0_df['Label'] = 'Automated Cluster 0 (The Green Dots)'
            fig_air = px.scatter_mapbox(
                c0_df, lat='pickup_latitude', lon='pickup_longitude', color='Label',
                title='Proof: Strategic Airport Runs', mapbox_style="carto-positron",
                color_discrete_sequence=["#06C167"], height=250, opacity=0.3
            )
            fig_air.update_layout(margin=dict(l=0, r=0, t=40, b=10))
            st.plotly_chart(fig_air, width="stretch")
            
        st.markdown("<br><hr style='border:1px solid #E2E2E2;'><br>", unsafe_allow_html=True)

        # STRATEGY 2: Dynamic Pricing
        col_b3, col_b4 = st.columns([1.5, 1])
        with col_b3:
            # Graph for Pricing: Time series comparing Cluster 7 vs Baseline AND Geographic Map
            cnumber = "7: Late-Night Party"
            c7_df = df[df['cluster'] == cnumber].copy()
            c7_demand = c7_df.groupby(c7_df['pickup_datetime'].dt.hour)['fare_amount'].count().reset_index()
            c7_demand.columns = ['Hour of Day', 'Total Nightlife Trips']
            fig_price = px.bar(c7_demand, x='Hour of Day', y='Total Nightlife Trips', title="1. Time: The 'Nightclub Surge' Peak (2:00 AM)", color_discrete_sequence=["#000000"])
            fig_price.update_layout(height=250, margin=dict(l=0, r=0, t=40, b=0), xaxis=dict(tickmode='linear', tick0=0, dtick=1))
            st.plotly_chart(fig_price, width="stretch")

            c7_df['Label'] = 'Nightclubs / Entertainment Districts'
            fig_night_map = px.scatter_mapbox(
                c7_df, lat='pickup_latitude', lon='pickup_longitude', color='Label',
                title='2. Geography: Deep Urban Hotspots', mapbox_style="carto-positron",
                color_discrete_sequence=["#06C167"], height=350, opacity=0.8
            )
            fig_night_map.update_layout(margin=dict(l=0, r=0, t=40, b=0))
            st.plotly_chart(fig_night_map, width="stretch")
        with col_b4:
            st.markdown("""
            <div style="background-color: #F6F6F6; border-top: 6px solid #000000; padding: 30px; border-radius: 8px; height: 100%;">
                <h3 style="color: #000000; font-size: 24px; margin-top: 0; margin-bottom: 20px;">2. Surgical Dynamic Pricing</h3>
                <p style="color: #333333; font-size: 18px; line-height: 1.6; margin-bottom: 20px;"><b>How to use the data:</b> Look at the bar chart isolating the "Nightlife" cluster. There is an unmistakable, explosive spike right between 1:00 AM and 3:00 AM—this perfectly matches the time nightclubs close in Downtown Manhattan and Brooklyn.</p>
                <div style="background-color: #E2E2E2; height: 2px; width: 100%; margin: 20px 0;"></div>
                <strong style="color: #000000; font-size: 16px; text-transform: uppercase; letter-spacing: 0.5px;">✓ Direct Impact</strong>
                <p style="color: #333333; font-size: 16px; line-height: 1.6; margin-top: 10px; margin-bottom: 0;">Instead of turning practically all of NY into a "surge zone", we can literally geo-fence high prices instantly onto nightclub strips at 2:00 AM to capitalize on highly urgent, nightlife demand.</p>
            </div>
            """, unsafe_allow_html=True)
            
        st.markdown("<br><hr style='border:1px solid #E2E2E2;'><br>", unsafe_allow_html=True)

        # STRATEGY 3: Hyper-Targeted Marketing
        col_b5, col_b6 = st.columns([1, 1.5])
        with col_b5:
            st.markdown("""
            <div style="background-color: #F6F6F6; border-top: 6px solid #333333; padding: 30px; border-radius: 8px; height: 100%;">
                <h3 style="color: #000000; font-size: 24px; margin-top: 0; margin-bottom: 20px;">3. Target Marketing Demographics</h3>
                <p style="color: #333333; font-size: 18px; line-height: 1.6; margin-bottom: 20px;"><b>How to use the data:</b> When you compare the <b>Large Vehicle users</b> against <b>Solo Commuters</b>, the passenger counts are fundamentally different (almost 5-to-1). They require vastly different advertising approaches.</p>
                <div style="background-color: #E2E2E2; height: 2px; width: 100%; margin: 20px 0;"></div>
                <strong style="color: #000000; font-size: 16px; text-transform: uppercase; letter-spacing: 0.5px;">✓ Direct Impact</strong>
                <p style="color: #333333; font-size: 16px; line-height: 1.6; margin-top: 10px; margin-bottom: 0;">We can push 'UberXL' discounts purely to family demographic user IDs, while offering 'Business Commuter' flat rates specifically to the solo commuters.</p>
            </div>
            """, unsafe_allow_html=True)
        with col_b6:
            c14_df = df[df['cluster'].isin(["1: Standard Weekday", "4: High Passenger / SUV"])].copy()
            c14_df['Profile'] = c14_df['cluster'].map({"1: Standard Weekday": 'Solo Commuters', "4: High Passenger / SUV": 'Families / Group SUV'})
            c14_avg = c14_df.groupby('Profile')['passenger_count'].mean().reset_index()
            fig_market = px.bar(c14_avg, x='Profile', y='passenger_count', title="Demographic Targeting by Avg. Passengers", color_discrete_sequence=["#06C167", "#333333"])
            fig_market.update_layout(height=500, margin=dict(l=0, r=0, t=40, b=0))
            st.plotly_chart(fig_market, width="stretch")
            
    else:
        st.info("Cluster data is required to view these insights. Please ensure you are loading 'uber_with_clusters.csv'.")
    st.markdown("<br><br>", unsafe_allow_html=True)

# Footer Section
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("---")

# Using columns for the footer content to match the Wix style
f_col1, f_col2, f_col3, f_col4 = st.columns([1, 1, 1, 1.5])

with f_col1:
    st.markdown("<h4 style='color: #A6A6A6; font-size: 14px; text-transform: uppercase; letter-spacing: 1.5px; margin-bottom: 20px;'>Navigation</h4>", unsafe_allow_html=True)
    # Since st.tabs doesn't support deep linking easily, we provide instructions or buttons that scroll back up
    # However, to be most helpful, I'll provide clickable links that scroll to the top of the page.
    for title in tab_titles:
        st.markdown(f"[{title}](#uber-fare-data-explorer)")

with f_col2:
    st.markdown("<h4 style='color: #A6A6A6; font-size: 14px; text-transform: uppercase; letter-spacing: 1.5px; margin-bottom: 20px;'>Work Done By</h4>", unsafe_allow_html=True)
    st.markdown("**Carlota Marto**<br>20241729", unsafe_allow_html=True)
    st.markdown("**Francisca Teixeira**<br>20241702", unsafe_allow_html=True)

with f_col3:
    st.markdown("<h4 style='color: #A6A6A6; font-size: 14px; text-transform: uppercase; letter-spacing: 1.5px; margin-bottom: 20px;'>Teacher</h4>", unsafe_allow_html=True)
    st.markdown("**Ivo Bernardo**<br>Machine Learning II", unsafe_allow_html=True)

with f_col4:
    st.image("uber_logo.jpg", width=120)
    st.caption("This project is optimized for executive-level business intelligence and strategic decision making.")

st.markdown("<br>", unsafe_allow_html=True)
st.markdown("""
<div style="background-color: #000000; padding: 20px; border-radius: 4px; display: flex; justify-content: space-between; color: #666666; font-size: 12px; font-family: 'Inter', sans-serif;">
    <div>© 2024 Uber Fare Explorer Project - Academic Use Only</div>
    <div>Built for Machine Learning II</div>
</div>
""", unsafe_allow_html=True)
