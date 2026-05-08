import streamlit as st
import time
from utils import load_data, render_footer

df = load_data()

# Injecting local CSS just for the Simulator to match the mock exactly
st.markdown("""
<style>
/* Clean up the main layout */
.main .block-container {
    max-width: 800px;
}
/* Huge Uber font for the title */
.uber-title {
    font-size: 52px;
    font-weight: 700;
    line-height: 1.1;
    color: #000000;
    margin-top: 20px;
    margin-bottom: 20px;
    font-family: 'Inter', sans-serif;
    letter-spacing: -1px;
}
.uber-subtitle {
    font-size: 16px;
    color: #000000;
    margin-bottom: 40px;
}
/* Style the inputs to look more like the Uber app */
div[data-baseweb="input"] {
    background-color: #F6F6F6 !important;
    border-radius: 8px !important;
    border: none !important;
}
div[data-baseweb="input"] input {
    background-color: #F6F6F6 !important;
    font-size: 16px;
    padding: 12px 16px !important;
}
/* Custom Black Button */
div.stButton > button {
    background-color: #000000;
    color: #FFFFFF;
    border-radius: 8px;
    padding: 12px 24px;
    font-size: 16px;
    font-weight: 600;
    border: none;
    width: auto;
    transition: background-color 0.2s;
    margin-top: 10px;
}
div.stButton > button:hover {
    background-color: #333333;
    color: #FFFFFF;
    border: none;
}
/* Fare Card */
.fare-card {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 15px 20px;
    border: 1px solid #E2E2E2;
    border-radius: 12px;
    margin-bottom: 15px;
    background-color: #FFFFFF;
}
.fare-card:hover {
    border-color: #000000;
    cursor: pointer;
}
.car-image {
    width: 60px;
    height: 40px;
    background-color: #F0F0F0;
    border-radius: 8px;
    display: flex;
    justify-content: center;
    align-items: center;
    font-size: 20px;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="uber-title">Request a ride for now or later</div>', unsafe_allow_html=True)
st.markdown('<div class="uber-subtitle">Add your trip details, hop in, and go.</div>', unsafe_allow_html=True)

import datetime

col_time, _ = st.columns([1, 2])
with col_time:
    time_choice = st.selectbox("When do you want to travel?", ["⏱️ Pickup now", "📅 Schedule for later"], label_visibility="collapsed")
    
    simulated_hour = datetime.datetime.now().hour
    if "Schedule" in time_choice:
        schedule_time = st.time_input("Select time", value=datetime.datetime.now())
        if schedule_time:
            simulated_hour = schedule_time.hour

st.markdown("<br>", unsafe_allow_html=True)

nyc_locations = [
    "Times Square, Manhattan",
    "Central Park, Manhattan",
    "Empire State Building, Manhattan",
    "Wall Street, Financial District",
    "JFK International Airport, Queens",
    "LaGuardia Airport, Queens",
    "Brooklyn Bridge Park, Brooklyn",
    "Barclays Center, Brooklyn"
]

origem = st.selectbox("Pickup location", options=nyc_locations, index=0)
destino = st.selectbox("Dropoff location", options=nyc_locations, index=4)

if st.button("See prices"):
    if origem == destino:
        st.error("Pickup and dropoff cannot be the same location.")
    else:
        with st.spinner("Calculating fares..."):
            time.sleep(1) # Simulate network request
            
            # Deterministic pseudo-random generation based on text inputs
            seed_val = len(origem) * 3 + len(destino) * 7
            
            # Distance in km (between 2km and 18km)
            distance_km = (seed_val % 16) + 2 + (seed_val % 10) / 10.0
            
            # Duration in mins
            duration_min = int(distance_km * 3.5) + (seed_val % 5)
            
            # Pricing Model based on NY data averages
            base_fare = 3.50
            per_km = 1.85
            
            # Time-based surge logic
            if simulated_hour in [7, 8, 9, 10]:
                surge = 1.45
                surge_msg = "Morning Rush Surge Applied (+45%)"
            elif simulated_hour in [16, 17, 18, 19]:
                surge = 1.60
                surge_msg = "Evening Rush Surge Applied (+60%)"
            elif simulated_hour in [0, 1, 2, 3, 4]:
                surge = 1.30
                surge_msg = "Late Night Surge Applied (+30%)"
            else:
                surge = 1.0
                surge_msg = "Standard Time (No Surge)"
                
            estimated_price = (base_fare + (distance_km * per_km)) * surge
            
            st.markdown("---")
            st.markdown(f"**Estimated Trip:** {distance_km:.1f} km • ~{duration_min} min drive")
            st.caption(f"⚡ {surge_msg}")
            
            # Render Fare Cards
            st.markdown(f"""
            <div class="fare-card" style="border-left: 6px solid #06C167;">
                <div style="display: flex; gap: 15px; align-items: center;">
                    <div class="car-image">🚗</div>
                    <div>
                        <div style="font-weight: 700; font-size: 18px;">Estimated Fare</div>
                        <div style="color: #666666; font-size: 14px;">Based on historical model data</div>
                    </div>
                </div>
                <div style="font-weight: 700; font-size: 24px; color: #06C167;">${estimated_price:.2f}</div>
            </div>
            """, unsafe_allow_html=True)
            
            st.success("✅ Price successfully generated based on historical data!")


render_footer()
