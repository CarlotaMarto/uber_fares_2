import streamlit as st
import pandas as pd
from utils import load_data

df = load_data()

st.title("Passenger Profiles")

st.markdown("""
<p style="color: #666666; font-size: 18px; margin-bottom: 30px;">
    We analyzed every single ride and grouped them into <b>8 distinct passenger profiles</b>. 
    Explore the cards below to see exactly who is using the platform and how they travel.
</p>
""", unsafe_allow_html=True)

if 'cluster' in df.columns:
    clusters = [
        {"id": "0: Airport / Long-Distance", "desc": "High-speed hauls to JFK/EWR. Profitable and specialized.", "color": "#06C167", "speed": "4s", "emoji": "✈️"},
        {"id": "1: Standard Weekday", "desc": "The rhythm of the city. Reliable daytime transit.", "color": "#000000", "speed": "8s", "emoji": "🏙️"},
        {"id": "2: Weekend Rush-Hour", "desc": "Busy leisure hours. Navigating the Saturday surge.", "color": "#333333", "speed": "12s", "emoji": "🛍️"},
        {"id": "3: Standard Weekend", "desc": "Relaxed weekend vibes for brunches and sightseeing.", "color": "#666666", "speed": "10s", "emoji": "🍦"},
        {"id": "4: High Passenger / SUV", "desc": "Big groups. Big vehicles. Big impact.", "color": "#999999", "speed": "9s", "emoji": "🚐"},
        {"id": "5: Fare / GPS Anomalies", "desc": "The outliers. Edge-cases and flat-rate tolls.", "color": "#CCCCCC", "speed": "15s", "emoji": "⚠️"},
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
</div>
<p style="color: #666666; font-size: 15px; margin-top: 5px; min-height: 45px;">{c['desc']}</p>
<div style="display: flex; gap: 30px; margin-top: 20px; border-top: 1px solid #F0F0F0; padding-top: 15px;">
<div><span style="color: #999999; font-size: 11px; text-transform: uppercase; font-weight: 700;">Avg Fare</span><br><b style="font-size: 20px; color: #000000;">${avg_fare:.2f}</b></div>
<div><span style="color: #999999; font-size: 11px; text-transform: uppercase; font-weight: 700;">Avg Distance</span><br><b style="font-size: 20px; color: #000000;">{avg_dist:.2f}km</b></div>
</div>
</div>
""", unsafe_allow_html=True)
else:
    st.info("Cluster data missing.")

from utils import render_footer
render_footer()
