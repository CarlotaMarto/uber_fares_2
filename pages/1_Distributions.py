import streamlit as st
import plotly.express as px
from utils import load_data

df = load_data()

st.title("Fare & Passenger Analysis")

# Executive Summary
st.markdown("### Executive Summary")
kpi1, kpi2, kpi3 = st.columns(3)
with kpi1:
    st.metric(label="Total Trips Analyzed", value=f"{len(df):,}")
with kpi2:
    st.metric(label="Median Fare", value=f"€{df['fare_amount'].median():.2f}")
with kpi3:
    solo_riders = len(df[df['passenger_count'] == 1])
    solo_pct = (solo_riders / len(df)) * 100
    st.metric(label="Solo Ridership", value=f"{solo_pct:.1f}%")

st.markdown("""
> **Tip:** If you're traveling solo for a short distance (under €20), you are in the "sweet spot" of the platform! Most riders use the app for quick inner-city trips. However, if you're planning a long rural haul, consider booking in advance as longer trips can incur unpredictable pricing anomalies.
""")

st.divider()

# Core Visuals
st.markdown("### Core Distributions")
col1, col2 = st.columns(2)

with col1:
    fig_hist = px.histogram(df, x="fare_amount", nbins=30, title="Fare Distribution Volume", color_discrete_sequence=["#06C167"], labels={'fare_amount': 'Fare (€)'})
    st.plotly_chart(fig_hist, use_container_width=True)

with col2:
    pass_counts = df["passenger_count"].value_counts().reset_index()
    pass_counts.columns = ["Passenger Count", "Trips"]
    fig_bar = px.bar(pass_counts, x="Passenger Count", y="Trips", title="Trips by Passenger Count", color_discrete_sequence=["#06C167"])
    st.plotly_chart(fig_bar, use_container_width=True)

st.markdown("<br>", unsafe_allow_html=True)

# Deep Dive
with st.expander("Advanced Analytics & Deep Dive", expanded=False):
    st.markdown("Explore mathematical edge-cases, statistical variances, and non-linear pricing anomalies.")
    
    deep_col1, deep_col2 = st.columns(2)
    with deep_col1:
        fig_scatter = px.scatter(df, x="distance_km", y="fare_amount", opacity=0.5, title="Fare vs. Distance (Anomaly Detection)", color_discrete_sequence=["#06C167"], labels={'fare_amount': 'Fare (€)', 'distance_km': 'Distance (km)'})
        st.plotly_chart(fig_scatter, use_container_width=True)
        st.caption("While there is a clear linear relationship between distance and fare, striking vertical pricing anomalies exist at 0km. These represent edge-cases like flat-rate tolls, severe gridlocks, or GPS cutouts.")
        
    with deep_col2:
        fig_box = px.box(df, x='passenger_count', y='fare_amount', title='Fare Variance by Capacity', color_discrete_sequence=["#06C167"], labels={'fare_amount': 'Fare (€)', 'passenger_count': 'Passenger Count'})
        st.plotly_chart(fig_box, use_container_width=True)
        st.caption("Surprisingly, the median fare does not drastically increase for larger passenger counts, implying larger vehicles are fundamentally booked for identical trip lengths as solo sedans.")

from utils import render_footer
render_footer()
