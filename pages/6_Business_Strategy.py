import streamlit as st
import plotly.express as px
import pandas as pd
from utils import load_data, render_footer

df = load_data()

st.title("Data-Driven Business Strategies")

# Pre-calculate data needed
# 1. Profitability: fare per km
df['fare_per_km'] = df['fare_amount'] / df['distance_km']
# Clean up infinite/NaN from division by zero
df_profit = df[(df['distance_km'] > 0.5) & (df['fare_amount'] > 0)].copy()

# 2. Fleet sizing
passenger_counts = df['passenger_count'].value_counts().reset_index()
passenger_counts.columns = ['Passengers', 'Trips']
passenger_counts['Percentage'] = (passenger_counts['Trips'] / len(df)) * 100
passenger_counts = passenger_counts.sort_values('Passengers')

st.divider()

# Download Report Section for Analysts
st.markdown("""
<div style="background-color: #000000; padding: 25px; border-radius: 12px; border: 1px solid #333333; margin-bottom: 30px; display: flex; justify-content: space-between; align-items: center;">
    <div style="flex: 1;">
        <h3 style="color: #FFFFFF; margin: 0; font-size: 20px;">Download Executive Insights Report</h3>
        <p style="color: #888888; margin: 5px 0 0 0; font-size: 14px;">Get a professional, high-fidelity PDF summary of all machine learning clusters and business strategies.</p>
    </div>
</div>
""", unsafe_allow_html=True)

# We use a column to center the real streamlit button over the CSS card or just put it below
col_rep1, col_rep2, col_rep3 = st.columns([1, 1, 1])
with col_rep2:
    if st.button("GENERATE PDF REPORT", type="primary", use_container_width=True):
        with st.spinner("Compiling Analytics..."):
            from report_generator import create_executive_pdf_report
            user_name = st.session_state.get('logged_in_user', 'Uber Analyst')
            pdf_path = create_executive_pdf_report(user_name)
            if pdf_path and os.path.exists(pdf_path):
                with open(pdf_path, "rb") as f:
                    st.download_button(
                        label="⬇️ DOWNLOAD PDF NOW",
                        data=f,
                        file_name="Uber_Executive_Report.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )
                st.success("Report generated successfully!")
            else:
                st.error("Failed to generate report. Please check data files.")

st.divider()

if 'cluster' in df.columns:
    # STRATEGY 1: Profitability Optimization ($/km)
    st.markdown("### 1. Profitability Optimization (Fare per KM)")
    col_a1, col_a2 = st.columns([1, 1.5])
    with col_a1:
        st.markdown("""
        <div style="background-color: #F6F6F6; border-top: 6px solid #06C167; padding: 25px; border-radius: 8px; height: 100%;">
            <h4 style="color: #000000; margin-top: 0;">Metric: Average Fare per Kilometer</h4>
            <p style="color: #333333; font-size: 16px;"><b>Analysis:</b> By calculating `fare_amount / distance_km`, we identify exactly which hours yield the highest profit margins for drivers, regardless of the total distance driven.</p>
            <div style="background-color: #E2E2E2; height: 2px; width: 100%; margin: 15px 0;"></div>
            <strong style="color: #000000; text-transform: uppercase;">✓ Actionable Strategy</strong>
            <p style="color: #333333; font-size: 16px; margin-top: 10px;">Implement highly targeted driver incentives during the <b>5:00 AM - 7:00 AM</b> window. Though absolute volume is lower, the intrinsic profitability per km is at its absolute peak, maximizing fleet yield.</p>
        </div>
        """, unsafe_allow_html=True)
    with col_a2:
        hourly_profit = df_profit.groupby(df_profit['pickup_datetime'].dt.hour)['fare_per_km'].mean().reset_index()
        hourly_profit.columns = ['Hour', 'Avg $/km']
        fig1 = px.line(hourly_profit, x='Hour', y='Avg $/km', title="Average Profitability by Hour of Day", markers=True)
        fig1.update_traces(line_color="#06C167", line_width=4, marker=dict(size=8, color="#000000"))
        fig1.update_layout(height=350, margin=dict(l=0, r=0, t=40, b=0), xaxis=dict(tickmode='linear', dtick=2))
        st.plotly_chart(fig1, use_container_width=True)

    st.markdown("<br><br>", unsafe_allow_html=True)

    # STRATEGY 2: Fleet Right-Sizing
    st.markdown("### 2. Fleet Capacity Utilization")
    col_b1, col_b2 = st.columns([1.5, 1])
    with col_b1:
        fig2 = px.bar(passenger_counts, x='Passengers', y='Percentage', text=passenger_counts['Percentage'].apply(lambda x: f"{x:.1f}%"), title="Passenger Volume Distribution (%)")
        fig2.update_traces(marker_color="#000000", textposition='outside')
        fig2.update_layout(height=350, margin=dict(l=0, r=0, t=40, b=0), xaxis=dict(type='category'))
        st.plotly_chart(fig2, use_container_width=True)
    with col_b2:
        st.markdown("""
        <div style="background-color: #F6F6F6; border-top: 6px solid #000000; padding: 25px; border-radius: 8px; height: 100%;">
            <h4 style="color: #000000; margin-top: 0;">Metric: Wasted Seat Ratio</h4>
            <p style="color: #333333; font-size: 16px;"><b>Analysis:</b> Over 69% of all trips consist of exactly 1 passenger. Using standard 4-seat sedans results in an average capacity utilization of just 25% per solo trip.</p>
            <div style="background-color: #E2E2E2; height: 2px; width: 100%; margin: 15px 0;"></div>
            <strong style="color: #000000; text-transform: uppercase;">✓ Actionable Strategy</strong>
            <p style="color: #333333; font-size: 16px; margin-top: 10px;"><b>Fleet Right-sizing:</b> Shift vehicle financing incentives toward ultra-compact or 2-seater EVs. Alternatively, massively subsidize "Uber Pool" algorithms to force consolidation of these solo riders, drastically cutting carbon footprint and operating costs.</p>
        </div>
        """, unsafe_allow_html=True)

    st.markdown("<br><br>", unsafe_allow_html=True)

    # STRATEGY 3: Distance vs Volume by Segment
    st.markdown("### 3. The Volume vs. Distance Matrix")
    col_c1, col_c2 = st.columns([1, 1.5])
    with col_c1:
        st.markdown("""
        <div style="background-color: #F6F6F6; border-top: 6px solid #333333; padding: 25px; border-radius: 8px; height: 100%;">
            <h4 style="color: #000000; margin-top: 0;">Metric: Cluster Economics</h4>
            <p style="color: #333333; font-size: 16px;"><b>Analysis:</b> This scatter plot isolates our ML clusters to compare their raw volume (X-axis) against their average distance (Y-axis), visualizing the dichotomy of the business model.</p>
            <div style="background-color: #E2E2E2; height: 2px; width: 100%; margin: 15px 0;"></div>
            <strong style="color: #000000; text-transform: uppercase;">✓ Actionable Strategy</strong>
            <p style="color: #333333; font-size: 16px; margin-top: 10px;">Allocate marketing budget inversely to distance: Focus 80% of retention budget on the massive <b>short-distance urban clusters</b> (high frequency, high volume), and treat long-distance airport clusters purely as premium, un-discounted cash cows.</p>
        </div>
        """, unsafe_allow_html=True)
    with col_c2:
        cluster_econ = df.groupby('cluster').agg({'distance_km': 'mean', 'fare_amount': 'count'}).reset_index()
        cluster_econ.columns = ['Cluster', 'Avg Distance (km)', 'Total Trips']
        # Shorten cluster names for chart
        cluster_econ['Cluster Name'] = cluster_econ['Cluster'].apply(lambda x: x.split(':')[1].strip() if ':' in x else x)
        
        fig3 = px.scatter(cluster_econ, x='Total Trips', y='Avg Distance (km)', color='Cluster Name', size='Total Trips', text='Cluster Name', title="Economic Matrix: Volume vs Distance")
        fig3.update_traces(textposition='top center', marker=dict(line=dict(width=1, color='DarkSlateGrey')))
        fig3.update_layout(height=400, margin=dict(l=0, r=0, t=40, b=0), showlegend=False)
        # Ensure text is not clipped
        fig3.update_yaxes(range=[0, cluster_econ['Avg Distance (km)'].max() * 1.3])
        st.plotly_chart(fig3, use_container_width=True)

else:
    st.info("Cluster data is required to view these insights. Please ensure you are loading 'uber_with_clusters.csv'.")

render_footer()
