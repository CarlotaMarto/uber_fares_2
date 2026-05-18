import streamlit as st
import time
import pandas as pd
import plotly.graph_objects as go
from utils import load_data, render_footer, get_base64_bin_help

df = load_data()

# Predefined coordinates for NYC Locations to enable precise mapping and reverse geocoding
nyc_coords = {
    "Times Square, Manhattan": (40.7580, -73.9855),
    "Central Park, Manhattan": (40.7851, -73.9683),
    "Empire State Building, Manhattan": (40.7484, -73.9857),
    "Wall Street, Financial District": (40.7064, -74.0094),
    "JFK International Airport, Queens": (40.6413, -73.7781),
    "LaGuardia Airport, Queens": (40.7769, -73.8740),
    "Brooklyn Bridge Park, Brooklyn": (40.7023, -73.9967),
    "Barclays Center, Brooklyn": (40.6826, -73.9754)
}

# Helper to find the nearest NYC landmark/address
def get_nearest_address(lat, lon):
    min_dist = float('inf')
    best_loc = "NYC Location"
    for loc, (c_lat, c_lon) in nyc_coords.items():
        dist = (lat - c_lat)**2 + (lon - c_lon)**2
        if dist < min_dist:
            min_dist = dist
            best_loc = loc
    return best_loc

# Modal window utilizing st.dialog
if hasattr(st, "dialog"):
    @st.dialog("Historical Reference Map", width="large")
    def show_map_dialog(distance_km, simulated_hour, estimated_price, origem, destino):
        render_map_inside(distance_km, simulated_hour, estimated_price, origem, destino)
else:
    def show_map_dialog(distance_km, simulated_hour, estimated_price, origem, destino):
        st.info("Reference Map Visualization:")
        render_map_inside(distance_km, simulated_hour, estimated_price, origem, destino)

def render_map_inside(distance_km, simulated_hour, estimated_price, origem, destino):
    st.markdown(
        f"""
        <p style='color: #333333; font-size: 15px; margin-bottom: 20px; font-family: sans-serif; line-height: 1.5;'>
            <b>How was the fare calculated?</b><br>
            The fare is computed using a <b>Base Fare (€3.50)</b> + a <b>Distance Fare (€1.85 per km)</b>, 
            multiplied by a <b>Time-of-Day Surge multiplier</b> depending on the hour of the trip (e.g. morning/evening rush hours, or late-night adjustments).<br><br>
            <b>Historical Reference Map</b><br>
            This interactive map displays up to 15 real reference trips from our historical database with matching distances 
            (<b>{distance_km - 2.5:.1f} km - {distance_km + 2.5:.1f} km</b>) and pick-up hours. 
            Hover over any path to see its original start time, pickup/dropoff landmarks, and price!
        </p>
        """, 
        unsafe_allow_html=True
    )
    
    sim_pickup_lat, sim_pickup_lon = nyc_coords[origem]
    sim_dropoff_lat, sim_dropoff_lon = nyc_coords[destino]
    
    # Filter dataset for similar distance AND similar time of day (within ±3 hours)
    df_hours = df['pickup_datetime'].dt.hour
    hour_diff = (df_hours - simulated_hour).abs()
    import numpy as np
    hour_dist = np.minimum(hour_diff, 24 - hour_diff)
    
    hist_df = df[
        (df['distance_km'] >= distance_km - 2.5) &
        (df['distance_km'] <= distance_km + 2.5) &
        (hour_dist <= 3)
    ].copy()
    
    if len(hist_df) < 3:
        # Fallback to distance-only if hour matching is too restrictive
        hist_df = df[
            (df['distance_km'] >= distance_km - 2.5) &
            (df['distance_km'] <= distance_km + 2.5)
        ].copy()
    
    if len(hist_df) > 15:
        hist_df = hist_df.sample(15, random_state=42)
        
    fig = go.Figure()
    
    # Draw original historical trips (Black)
    for idx, row in hist_df.iterrows():
        p_lat = row['pickup_latitude']
        p_lon = row['pickup_longitude']
        d_lat = row['dropoff_latitude']
        d_lon = row['dropoff_longitude']
        
        pickup_time = row['pickup_datetime']
        time_str = "N/A"
        try:
            if pd.notna(pickup_time):
                if hasattr(pickup_time, 'strftime'):
                    time_str = pickup_time.strftime('%H:%M')
                else:
                    dt = pd.to_datetime(pickup_time)
                    time_str = dt.strftime('%H:%M')
        except Exception:
            pass
            
        pickup_addr = get_nearest_address(p_lat, p_lon)
        dropoff_addr = get_nearest_address(d_lat, d_lon)
        price_str = f"€{row['fare_amount']:.2f}"
        
        hover_text = (
            f"<b>Original Historical Trip</b><br>"
            f"Start Time: {time_str}<br>"
            f"Pickup Address: {pickup_addr}<br>"
            f"Dropoff Address: {dropoff_addr}<br>"
            f"Price: {price_str}"
        )
        
        fig.add_trace(go.Scattermapbox(
            mode="lines+markers",
            lat=[p_lat, d_lat],
            lon=[p_lon, d_lon],
            line=dict(color="#000000", width=2),
            marker=dict(size=6, color="#000000"),
            hoverinfo="text",
            hovertext=hover_text,
            showlegend=False
        ))
        
    # Draw simulated trip (Vibrant Green)
    sim_hover_text = (
        f"<b>Simulated Trip (Current)</b><br>"
        f"Hour: {simulated_hour:02d}:00<br>"
        f"Pickup: {origem}<br>"
        f"Dropoff: {destino}<br>"
        f"Estimated Price: €{estimated_price:.2f}"
    )
    
    fig.add_trace(go.Scattermapbox(
        mode="lines+markers",
        lat=[sim_pickup_lat, sim_dropoff_lat],
        lon=[sim_pickup_lon, sim_dropoff_lon],
        line=dict(color="#06C167", width=5),
        marker=dict(size=9, color="#06C167"),
        hoverinfo="text",
        hovertext=sim_hover_text,
        showlegend=False
    ))
    
    # Draw black car marker at the midpoint of simulated trip
    mid_lat = (sim_pickup_lat + sim_dropoff_lat) / 2
    mid_lon = (sim_pickup_lon + sim_dropoff_lon) / 2
    
    fig.add_trace(go.Scattermapbox(
        mode="markers",
        lat=[mid_lat],
        lon=[mid_lon],
        marker=dict(size=14, color="#000000"),
        hoverinfo="text",
        hovertext="<b>Simulated Midpoint</b>",
        showlegend=False
    ))
    
    # Set Mapbox layout with high contrast carto-positron map
    fig.update_layout(
        mapbox=dict(
            style="carto-positron",
            center=dict(lat=(sim_pickup_lat + sim_dropoff_lat)/2, lon=(sim_pickup_lon + sim_dropoff_lon)/2),
            zoom=11
        ),
        margin=dict(l=0, r=0, t=0, b=0),
        height=500
    )
    
    st.plotly_chart(fig, use_container_width=True, config={'scrollZoom': True, 'modeBarButtonsToAdd': ['zoomInMapbox', 'zoomOutMapbox']})
    
    # Legend panel (NO emojis in system labels)
    st.markdown(
        """
        <div style='display: flex; gap: 20px; align-items: center; font-size: 14px; font-family: sans-serif; margin-top: 15px;'>
            <div style='display: flex; align-items: center; gap: 8px;'>
                <div style='width: 20px; height: 3px; background-color: #000000;'></div>
                <span>Original Reference Trips (Black)</span>
            </div>
            <div style='display: flex; align-items: center; gap: 8px;'>
                <div style='width: 20px; height: 4px; background-color: #06C167;'></div>
                <span>Simulated Trip (Green)</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


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
/* Fare Card & Overlay Button Styling */
.overlay-button-container {
    position: relative !important;
    height: 102px !important;
    margin-bottom: -102px !important;
    z-index: 999 !important;
}
.overlay-button-container button {
    background-color: transparent !important;
    border: none !important;
    color: transparent !important;
    height: 102px !important;
    width: 100% !important;
    cursor: pointer !important;
    box-shadow: none !important;
    margin: 0 !important;
    padding: 0 !important;
}
.overlay-button-container button:hover {
    background-color: transparent !important;
    border: none !important;
    color: transparent !important;
}
.overlay-button-container button:active {
    background-color: transparent !important;
    border: none !important;
    color: transparent !important;
}
.card-container-wrapper {
    position: relative;
    width: 100%;
    height: 102px;
    margin-bottom: 25px;
    pointer-events: none;
}
.fare-card {
    border-left: 6px solid #06C167;
    background-color: #FFFFFF;
    border-top: 1px solid #E2E2E2;
    border-right: 1px solid #E2E2E2;
    border-bottom: 1px solid #E2E2E2;
    border-radius: 12px;
    padding: 25px;
    box-shadow: 0 4px 12px rgba(0,0,0,0.05);
    display: flex;
    justify-content: space-between;
    align-items: center;
    height: 102px;
    box-sizing: border-box;
    transition: transform 0.2s, box-shadow 0.2s;
}
/* Trigger hover effect on the card when hovering the overlay button! */
.overlay-button-container:hover + .card-container-wrapper .fare-card {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 16px rgba(0,0,0,0.1) !important;
}
.car-image {
    width: 60px;
    height: 40px;
    background-color: #F0F0F0;
    border-radius: 8px;
    display: flex;
    justify-content: center;
    align-items: center;
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="uber-title">Request a ride for now or later</div>', unsafe_allow_html=True)
st.markdown('<div class="uber-subtitle">Add your trip details, hop in, and go.</div>', unsafe_allow_html=True)

import datetime

col_time, _ = st.columns([1, 2])
with col_time:
    time_choice = st.selectbox("When do you want to travel?", ["Pickup now", "Schedule for later"], label_visibility="collapsed")
    
    simulated_hour = datetime.datetime.now().hour
    if "Schedule" in time_choice:
        schedule_time = st.time_input("Select time", value=datetime.datetime.now())
        if schedule_time:
            simulated_hour = schedule_time.hour

st.markdown("<br>", unsafe_allow_html=True)

origem = st.selectbox("Pickup location", options=list(nyc_coords.keys()), index=0)
destino = st.selectbox("Dropoff location", options=list(nyc_coords.keys()), index=4)

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
                surge_msg = "Standard Time"
                
            estimated_price = (base_fare + (distance_km * per_km)) * surge
            
            # Store calculated results in session state for cross-rerun persistence
            st.session_state['prices_calculated'] = True
            st.session_state['sim_distance'] = distance_km
            st.session_state['sim_duration'] = duration_min
            st.session_state['sim_surge'] = surge_msg
            st.session_state['sim_price'] = estimated_price
            st.session_state['sim_origem'] = origem
            st.session_state['sim_destino'] = destino
            st.session_state['sim_hour'] = simulated_hour
            
            # Force trigger dynamic rerun to render the results cleanly
            st.rerun()

# Render persistent results if available
if st.session_state.get('prices_calculated', False):
    distance_km = st.session_state['sim_distance']
    duration_min = st.session_state['sim_duration']
    surge_msg = st.session_state['sim_surge']
    estimated_price = st.session_state['sim_price']
    origem = st.session_state['sim_origem']
    destino = st.session_state['sim_destino']
    
    st.markdown("---")
    st.markdown(f"**Estimated Trip:** {distance_km:.1f} km ≈ {duration_min} min drive")
    st.caption(surge_msg)

    simulated_hour = st.session_state.get('sim_hour', simulated_hour)

    # ── Toggle state ───────────────────────────────────────────────────────────
    if 'show_map' not in st.session_state:
        st.session_state['show_map'] = False
    show_map = st.session_state.get('show_map', False)
    map_arrow = "▲ hide map" if show_map else "▼ click here to view map"

    # ── Fare card ──────────────────────────────────────────────────────────────
    st.markdown(f"""
    <div style="
        border-left: 6px solid #06C167;
        background-color: #FFFFFF;
        border-top: 1px solid #E2E2E2;
        border-right: 1px solid #E2E2E2;
        border-bottom: 1px solid #E2E2E2;
        border-radius: 12px;
        padding: 22px 28px 18px 28px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.06);
        margin-bottom: 0;
    ">
        <div style="display:flex; justify-content:space-between; align-items:center;">
            <div>
                <div style="font-weight:700; font-size:20px; color:#000000; font-family:sans-serif;">Estimated Fare</div>
                <div style="color:#888888; font-size:13px; font-family:sans-serif; margin-top:4px;">
                    Based on historical model data
                </div>
            </div>
            <div style="font-weight:700; font-size:36px; color:#06C167; font-family:sans-serif;">€{estimated_price:.2f}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ── Green link-style toggle button ─────────────────────────────────────────
    st.markdown("""
    <style>
    div[data-testid="stButton"].map-toggle > button {
        background: none !important;
        border: none !important;
        box-shadow: none !important;
        color: #06C167 !important;
        font-size: 13px !important;
        font-weight: 600 !important;
        padding: 4px 0 0 28px !important;
        margin: 0 !important;
        cursor: pointer !important;
        text-decoration: none !important;
    }
    div[data-testid="stButton"].map-toggle > button:hover {
        color: #04a356 !important;
        background: none !important;
        border: none !important;
        box-shadow: none !important;
        text-decoration: underline !important;
    }
    div[data-testid="stButton"].map-toggle > button:focus {
        box-shadow: none !important;
        outline: none !important;
    }
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="map-toggle">', unsafe_allow_html=True)
    if st.button(map_arrow, key="map_toggle_btn"):
        st.session_state['show_map'] = not show_map
        st.rerun()
    st.markdown('</div>', unsafe_allow_html=True)

    # ── Map revealed on toggle ─────────────────────────────────────────────────
    if st.session_state.get('show_map', False):
        render_map_inside(distance_km, simulated_hour, estimated_price, origem, destino)

render_footer()

