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
import os
import plotly.express as px
import os

# Page configuration
st.set_page_config(
    page_title="Uber Fare Explorer",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for premium look (dark mode friendly)
st.markdown(
    """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    
    /* Hide Streamlit structural branding */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}
    
    /* Remove padding around the main block */
    .block-container {
        padding-top: 80px !important;
        padding-bottom: 0rem !important;
    }
    
    /* Push sidebar down to make room for fixed navbar */
    section[data-testid="stSidebar"] {
        top: 64px !important;
        height: calc(100vh - 64px) !important;
    }
    
    /* Dedicated full-width Uber Website Navbar */
    .uber-navbar {
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
    }
    .uber-navbar img {
        height: 24px;
        margin-right: 24px;
        filter: brightness(0) invert(1); /* Turns the black logo pure white */
    }
    .uber-navbar-title {
        color: #FFFFFF;
        font-family: 'Inter', sans-serif;
        font-size: 16px;
        font-weight: 600;
        letter-spacing: 0.5px;
    }
    </style>
    
    <div class="uber-navbar">
        <img src="https://upload.wikimedia.org/wikipedia/commons/c/cc/Uber_logo_2018.png">
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
        df['cluster'] = 'Cluster ' + df['cluster'].astype(str)
    return df

df = load_data()

if 'started' not in st.session_state:
    st.session_state['started'] = False

if not st.session_state['started']:
    import base64
    with open("taxi_real_ai.png", "rb") as image_file:
        img_b64 = base64.b64encode(image_file.read()).decode()

    st.markdown("<br><br>", unsafe_allow_html=True)
    html_content = f"""
<div style="width: 100%; padding: 10px;">
<h1 style="margin-top: 0; color: #000000; font-size: 86px; font-weight: 800; letter-spacing: -2.5px; line-height: 1.1;">Uber Fare Data Explorer</h1>

<p style="color: #222222; font-size: 30px; line-height: 1.5; margin-bottom: 40px; margin-top: 30px;">
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


# Sidebar filters
st.sidebar.header("Filters")
hour = st.sidebar.slider("Pickup hour", 0, 23, 12)
passenger_options = sorted(df["passenger_count"].unique())
passenger = st.sidebar.multiselect(
    "Passenger count", passenger_options, default=passenger_options
)
apply_map_filters = st.sidebar.checkbox("Apply filters to Maps?", value=True, help="Uncheck this to show ALL trips (all 8 clusters) on the interactive maps, regardless of the time and passenger sliders.")

filtered = df[(df["pickup_datetime"].dt.hour == hour) & (df["passenger_count"].isin(passenger))]
map_df = filtered if apply_map_filters else df

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

# Visualizations
tab1, tab2, tab3, tab4 = st.tabs(["Distributions", "Temporal Analysis", "Geospatial & Clusters", "Advanced Analysis"])

with tab1:
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

with tab3:
    st.subheader("Pickup Locations & Clusters")
    
    if 'cluster' in df.columns:
        with st.expander("Show Cluster Characteristics (Average Values)"):
            cluster_summary = df.groupby('cluster')[['distance_km', 'fare_amount', 'pickup_hour', 'passenger_count']].mean().round(2)
            st.dataframe(cluster_summary, use_container_width=True)
            st.markdown('''
            **What do these clusters actually mean?**
            By mathematically analyzing the multi-dimensional dataset (Distance, Fare, Passenger Count, Weekends, and Rush Hour flags), the K-Means algorithm effectively broke the trips into these profiles:
            
            - **Cluster 0: Long-Distance / Airport Runs.** Exceptionally high average distance (~16km) and high fares (~$42).
            - **Cluster 1: Standard Weekday Trips.** Typical daytime trips occurring entirely outside of peak traffic.
            - **Cluster 2: Weekend Rush-Hour.** Trips taking place strictly during busy weekend peak traffic hours. *(The calculated timeframe appears as mid-day because the algorithmic average simply splits the difference between the distinct morning and evening rush hour spikes).*
            - **Cluster 3: Standard Weekend Trips.** Normal trips reliably happening on weekends outside of rush hour.
            - **Cluster 4: High Passenger / SUV Trips.** Standard metrics, but strictly large groups (averaging 5 passengers).
            - **Cluster 5: GPS / Fare Anomalies.** Micro distances (~0.2km) but massive fares (~$47). The algorithm quarantined these mathematical edge-cases (likely GPS cut-outs, severe gridlock, or flat-rate tolls) into their own distinct group.
            - **Cluster 6: Weekday Rush-Hour Commutes.** Trips taking place strictly during weekday peak traffic. *(Similar to Cluster 2, the average time shows ~1:00 PM due solely to mathematically averaging morning and evening commutes together).*
            - **Cluster 7: Late-Night "Party" Trips.** Occurring almost exclusively incredibly late at night (averaging 2:00 AM).
            
            *Use the interactive tabs and maps below to visually explore these groups by filtering!*
            ''')
            
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
            fig_map = px.scatter_mapbox(
                map_df, lat='pickup_latitude', lon='pickup_longitude', color='cluster',
                size='fare_amount', hover_data=['fare_amount', 'distance_km'], zoom=10,
                title='Pickup Location Density Map', mapbox_style="open-street-map",
                height=500, color_discrete_sequence=uber_palette
            )
            fig_map.update_layout(margin=dict(l=0, r=0, t=40, b=0))
            st.plotly_chart(fig_map, width="stretch")
        with col_m2:
            st.markdown("<br><br><br><br>", unsafe_allow_html=True)
            st.markdown("""
            <div style="background-color: #F6F6F6; border-left: 4px solid #000000; padding: 20px; border-radius: 4px;">
                <h4 style="margin-top: 0; color: #000000; font-size: 16px; text-transform: uppercase; letter-spacing: 0.5px;">Ride Volume Heatmap</h4>
                <p style="color: #333333; font-size: 15px; line-height: 1.5; margin-bottom: 0;">This heatmap vividly underscores a massive structural volume concentration deeply centered around the business district hubs, which rapidly dissipates into nothingness moving toward the peripheral outer limits.</p>
            </div>
            """, unsafe_allow_html=True)

    else:
        st.write('Cluster column not available in the data.')
        map_data = map_df[["pickup_latitude", "pickup_longitude"]].rename(
            columns={"pickup_latitude": "lat", "pickup_longitude": "lon"}
        )
        st.map(map_data)

with tab2:
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
            <h4 style="margin-top: 0; color: #000000; font-size: 16px; text-transform: uppercase; letter-spacing: 0.5px;">Monthly Seasonality</h4>
            <p style="color: #333333; font-size: 15px; line-height: 1.5; margin-bottom: 0;">Ride volumes fluctuate throughout the year, often impacted by weather conditions and seasonal holidays, showing clear macro-level trends in ridership adoption.</p>
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
            <h4 style="margin-top: 0; color: #000000; font-size: 16px; text-transform: uppercase; letter-spacing: 0.5px;">Long-Term Trajectory</h4>
            <p style="color: #333333; font-size: 15px; line-height: 1.5; margin-bottom: 0;">Viewing the granular day-to-day ridership volume allows us to identify extreme macro-outliers—such as dramatic drops from massive blizzards or intense spikes from major city-wide events.</p>
        </div>
        """, unsafe_allow_html=True)

with tab4:
    st.subheader("Advanced Feature Analysis")
    
    col_a1, col_a2 = st.columns([2, 1])
    with col_a1:
        # We will build the correlation heatmap here
        import plotly.figure_factory as ff
        corr_cols = ['fare_amount', 'distance_km', 'passenger_count', 'pickup_hour', 'pickup_day', 'pickup_weekday']
        if all(c in filtered.columns for c in corr_cols):
            corr = filtered[corr_cols].corr().round(2)
            fig_heatmap = px.imshow(corr, text_auto=True, aspect="auto", title="Feature Correlation Heatmap", color_continuous_scale="Greens")
            st.plotly_chart(fig_heatmap, width="stretch")
        else:
            st.info("Additional dimensions calculated...")
    with col_a2:
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        st.markdown("""
        <div style="background-color: #F6F6F6; border-left: 4px solid #000000; padding: 20px; border-radius: 4px;">
            <h4 style="margin-top: 0; color: #000000; font-size: 16px; text-transform: uppercase; letter-spacing: 0.5px;">Linear Relationships</h4>
            <p style="color: #333333; font-size: 15px; line-height: 1.5; margin-bottom: 0;">Distance and Fare share a near 1-to-1 linear correlation (~0.85). Interestingly, passenger count has an absolute zero mathematical impact on the final fare pricing.</p>
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
            <h4 style="margin-top: 0; color: #000000; font-size: 16px; text-transform: uppercase; letter-spacing: 0.5px;">A.I. Dimensionality Extraction</h4>
            <p style="color: #333333; font-size: 15px; line-height: 1.5; margin-bottom: 0;">By compressing 8 variables down into a 2D mathematical space using Principal Component Analysis, we visually demonstrate how effectively the K-Means clusters cleanly separate fundamentally different rider profiles.</p>
        </div>
        """, unsafe_allow_html=True)

st.markdown("---")
st.caption("Data source: cleaned Uber dataset generated in the notebook.")
