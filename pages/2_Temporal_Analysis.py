import streamlit as st
import plotly.express as px
from utils import load_data

df = load_data()

st.title("Temporal Demand & Pricing")

# Pre-calculate KPIs
hour_counts = df['pickup_datetime'].dt.hour.value_counts()
busiest_hour = f"{hour_counts.idxmax()}:00"
dow_counts = df['pickup_datetime'].dt.day_name().value_counts()
busiest_day = dow_counts.idxmax()
avg_fare_by_hour = df.groupby(df['pickup_datetime'].dt.hour)['fare_amount'].mean()
max_avg_fare = avg_fare_by_hour.max()

# Executive Summary
st.markdown("### Executive Summary")
kpi1, kpi2, kpi3 = st.columns(3)
with kpi1:
    st.metric(label="Busiest Hour", value=busiest_hour)
with kpi2:
    st.metric(label="Busiest Day", value=busiest_day)
with kpi3:
    st.metric(label="Peak Avg Fare (5:00 AM)", value=f"${max_avg_fare:.2f}")

st.markdown("""
> **Tip:** Fares remain remarkably stable regardless of the day of the week! However, to avoid long wait times and the absolute highest surge prices, try to avoid booking between 4:00 AM and 5:00 AM for airport runs, or during the Friday and Saturday evening rushes.
""")

st.divider()

# Core Visuals
st.markdown("### Core Temporal Demand")
col1, col2 = st.columns(2)

with col1:
    hc_reset = hour_counts.reset_index()
    hc_reset.columns = ["Hour of Day", "Number of Trips"]
    fig_hour = px.bar(hc_reset, x="Hour of Day", y="Number of Trips", title="Trips by Hour of Day", color_discrete_sequence=["#06C167"])
    st.plotly_chart(fig_hour, use_container_width=True)

with col2:
    dow_reset = dow_counts.reindex(["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]).reset_index()
    dow_reset.columns = ["Day of Week", "Number of Trips"]
    fig_dow = px.bar(dow_reset, x="Day of Week", y="Number of Trips", title="Trips by Day of Week", color_discrete_sequence=["#06C167"])
    st.plotly_chart(fig_dow, use_container_width=True)

st.markdown("<br>", unsafe_allow_html=True)

# Deep Dive
with st.expander("🔍 Advanced Analytics & Deep Dive", expanded=False):
    st.markdown("Explore macroeconomic trends, pricing anomalies, and multi-year trajectory data.")
    
    tab1, tab2, tab3 = st.tabs(["Pricing Variance", "Monthly & Annual Growth", "Macro Trajectory"])
    
    with tab1:
        st.markdown("**Intra-Week Pricing Dynamics**")
        deep_col1, deep_col2 = st.columns(2)
        with deep_col1:
            avg_fare_hour = df.groupby(df['pickup_datetime'].dt.hour)['fare_amount'].mean().reset_index()
            avg_fare_hour.columns = ["Hour of Day", "Avg Fare ($)"]
            fig_fare_hour = px.line(avg_fare_hour, x="Hour of Day", y="Avg Fare ($)", title="Average Fare by Hour", color_discrete_sequence=["#06C167"], markers=True)
            st.plotly_chart(fig_fare_hour, use_container_width=True)
            st.caption("Fares consistently skyrocket between 4:00 AM and 5:00 AM. This fascinating premium is driven exclusively by long uncrowded runs to the airport for early-morning flights.")
        with deep_col2:
            avg_fare_dow = df.groupby(df['pickup_datetime'].dt.day_name())['fare_amount'].mean().reindex(["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]).reset_index()
            avg_fare_dow.columns = ["Day of Week", "Avg Fare ($)"]
            fig_fare_dow = px.bar(avg_fare_dow, x="Day of Week", y="Avg Fare ($)", title="Average Fare by Day", color_discrete_sequence=["#06C167"])
            st.plotly_chart(fig_fare_dow, use_container_width=True)
            st.caption("Average fares remain notably stable regardless of the actual day of the week, with only mild upticks occurring through the prime weekend blocks.")
            
    with tab2:
        st.markdown("**Long-Term Scale & Inflation**")
        deep_col3, deep_col4 = st.columns(2)
        with deep_col3:
            avg_fare_year = df.groupby(df['pickup_datetime'].dt.year)['fare_amount'].mean().reset_index()
            avg_fare_year.columns = ["Year", "Avg Fare ($)"]
            avg_fare_year["Year"] = avg_fare_year["Year"].astype(str)
            fig_fare_year = px.bar(avg_fare_year.sort_values("Year"), x="Year", y="Avg Fare ($)", title="Average Fare by Year", color_discrete_sequence=["#06C167"])
            st.plotly_chart(fig_fare_year, use_container_width=True)
            st.caption("Over a multi-year timeframe, we observe a steady overall rise in the average fare, smoothly reflecting the platform's gradual pricing power and broader inflation rates.")
        with deep_col4:
            year_counts = df['pickup_datetime'].dt.year.value_counts().reset_index()
            year_counts.columns = ["Year", "Number of Trips"]
            year_counts["Year"] = year_counts["Year"].astype(str)
            fig_year = px.bar(year_counts.sort_values("Year"), x="Year", y="Number of Trips", title="Trips by Year", color_discrete_sequence=["#06C167"])
            st.plotly_chart(fig_year, use_container_width=True)
            st.caption("Highlights the platform's multi-year structural progression as ride-sharing evolved from an emerging technology into essential public infrastructure.")
            
    with tab3:
        st.markdown("**Granular Trajectory**")
        date_counts = df['pickup_datetime'].dt.date.value_counts().reset_index()
        date_counts.columns = ["Date", "Number of Trips"]
        fig_date = px.line(date_counts.sort_values("Date"), x="Date", y="Number of Trips", title="Trips Over Time (Granular Daily View)", color_discrete_sequence=["#06C167"])
        st.plotly_chart(fig_date, use_container_width=True)
        st.caption("Viewing granular day-to-day ridership volume allows us to identify extreme macro-outliers—such as dramatic drops from blizzards or intense spikes from major city-wide events.")


from utils import render_footer
render_footer()
