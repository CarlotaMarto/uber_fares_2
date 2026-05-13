import streamlit as st
import plotly.express as px
from utils import load_data

df = load_data()

st.title("Geospatial Hub")

# Executive Summary
st.markdown("### Executive Summary")

# Simple geographic stats
avg_dist = df['distance_km'].mean()
max_dist = df['distance_km'].max()
short_trips_pct = (len(df[df['distance_km'] < 5]) / len(df)) * 100

kpi1, kpi2, kpi3 = st.columns(3)
with kpi1:
    st.metric(label="Total Mapped Pickups", value=f"{len(df):,}")
with kpi2:
    st.metric(label="Avg Trip Distance", value=f"{avg_dist:.1f} km")
with kpi3:
    st.metric(label="Micro-trips (< 5km)", value=f"{short_trips_pct:.1f}%")

st.markdown("""
> **Tip:** When traveling within Manhattan, short trips under 5km are your best bet. If you need to travel to the airports (JFK, Newark, LaGuardia), be prepared for specialized pricing zones. Exploring the map below can help you find areas where demand (and prices) are generally lower!
""")

st.divider()

# Core Visuals
st.markdown("### Interactive City Heatmaps")
st.markdown("<p style='color: #666666; font-size: 14px;'>Explore high-demand zones and pricing hotspots across the NYC metropolitan area.</p>", unsafe_allow_html=True)

map_view = st.radio("Select Map View:", ["Pricing Density (Heatmap)", "Segment Mapping (Clusters)"], horizontal=True)

if map_view == "Segment Mapping (Clusters)":
    uber_palette = ["#06C167", "#000000", "#333333", "#666666", "#999999", "#CCCCCC", "#1f7a46", "#048043"]
    fig_cluster = px.scatter_mapbox(
        df, lat='pickup_latitude', lon='pickup_longitude', color='cluster',
        title='Pickup locations colored by Machine Learning Segment', hover_data=['fare_amount', 'distance_km'],
        height=600, color_discrete_sequence=uber_palette, zoom=10, mapbox_style="carto-positron"
    )
    fig_cluster.update_layout(margin=dict(l=0, r=0, t=40, b=0))
    st.plotly_chart(fig_cluster, use_container_width=True)
else:
    fig_density = px.density_mapbox(
        df, lat='pickup_latitude', lon='pickup_longitude', z='fare_amount', radius=8,
        center=dict(lat=40.7128, lon=-74.0060), zoom=10, range_color=[0, 80],
        mapbox_style="carto-darkmatter", title='Heatmap: High Demand & Expensive Fare Zones',
        color_continuous_scale="Greens", height=600, labels={'fare_amount': 'Fare ($)'}
    )
    fig_density.update_layout(margin=dict(l=0, r=0, t=40, b=0), coloraxis_colorbar=dict(title="Fare ($)", tickprefix="$"))
    st.plotly_chart(fig_density, use_container_width=True)

st.markdown("<br>", unsafe_allow_html=True)

# Deep Dive
with st.expander("Advanced Analytics & Deep Dive", expanded=False):
    st.markdown("Analyze dynamic chronological demand flows using animated time-lapse mapping.")
    
    # Map 2: Animated map
    uber_palette = ["#06C167", "#000000", "#333333", "#666666", "#999999", "#CCCCCC", "#1f7a46", "#048043"]
    map_df_anim = df.dropna(subset=['pickup_hour']).sort_values('pickup_hour')
    map_df_anim['Hour'] = map_df_anim['pickup_hour'].astype(int).astype(str) + ":00"

    fig_map = px.scatter_mapbox(
        map_df_anim, lat='pickup_latitude', lon='pickup_longitude', color='cluster',
        size='fare_amount', hover_data=['fare_amount', 'distance_km'], zoom=9.5,
        animation_frame='Hour',
        title='Interactive Time-Lapse: Geographical Demand by Hour', mapbox_style="carto-positron",
        height=600, color_discrete_sequence=uber_palette
    )
    fig_map.update_layout(margin=dict(l=0, r=0, t=40, b=0))
    fig_map.layout.updatemenus[0].buttons[0].args[1]['frame']['duration'] = 800
    
    st.plotly_chart(fig_map, use_container_width=True)
    st.caption("Hit the Play button to watch ridership demand flow dynamically. Notice how the morning rush explicitly starts pulling heavily from outside boroughs, before collapsing entirely back into Manhattan's core for the evening peak.")


from utils import render_footer
render_footer()
