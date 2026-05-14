import streamlit as st
import base64
from utils import load_data, inject_custom_css

st.set_page_config(
    page_title="Uber Fare Explorer",
    page_icon="uber_logo.png",
    layout="wide",
    initial_sidebar_state="expanded",
)

inject_custom_css()
df = load_data()

import os
image_paths = ["uber first page.avif", "uber first page.jpg", "uber first page.png", "uber_first_page.jpg", "uber_first_page.png", "splash_image.jpg"]
img_b64 = ""
for img_path in image_paths:
    if os.path.exists(img_path):
        with open(img_path, "rb") as image_file:
            img_b64 = base64.b64encode(image_file.read()).decode()
        break

st.markdown("<br><br>", unsafe_allow_html=True)
html_content = f"""
<div style="width: 100%; padding: 10px;">
<h1 style="margin-top: 0; color: #000000; font-size: 86px; font-weight: 800; letter-spacing: -2.5px; line-height: 1.1;">Uber Fare Data Explorer</h1>

<p style="color: #222222; font-size: 22px; line-height: 1.5; margin-bottom: 40px;">
A deep-dive, interactive presentation designed for non-technical stakeholders to securely analyze historical <b>Uber ride metrics across New York City</b> (spanning from 2009 to 2015).
</p>

<img src="data:image/png;base64,{img_b64}" style="width: 100%; border-radius: 16px; box-shadow: 0 10px 30px rgba(0,0,0,0.1); object-fit: cover; max-height: 600px; margin-bottom: 60px;">

<hr style="border: 0; height: 1px; background-color: #E2E2E2; margin-bottom: 60px;">
<h3 style="color: #000000; font-size: 24px; text-transform: uppercase; letter-spacing: 1.5px; margin-bottom: 20px; font-weight: 700;">Global Dataset Overview</h3>
</div>
"""
st.markdown(html_content, unsafe_allow_html=True)

kpi_html = f"""
    <div style="display: flex; justify-content: space-between; gap: 20px; margin-bottom: 1.5rem; padding: 0 10px;">
        <div style="flex: 1; background-color: #000000; border-radius: 8px; padding: 20px; box-shadow: 0 4px 10px rgba(0,0,0,0.15);">
            <div style="color: #A6A6A6; font-size: 13px; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 8px;">Total Trips</div>
            <div style="color: #FFFFFF; font-size: 30px; font-weight: bold;">{len(df):,}</div>
        </div>
        <div style="flex: 1; background-color: #000000; border-radius: 8px; padding: 20px; box-shadow: 0 4px 10px rgba(0,0,0,0.15);">
            <div style="color: #A6A6A6; font-size: 13px; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 8px;">Avg Fare</div>
            <div style="color: #FFFFFF; font-size: 30px; font-weight: bold;">${df['fare_amount'].mean():.2f}</div>
        </div>
        <div style="flex: 1; background-color: #000000; border-radius: 8px; padding: 20px; box-shadow: 0 4px 10px rgba(0,0,0,0.15);">
            <div style="color: #A6A6A6; font-size: 13px; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 8px;">Avg Distance</div>
            <div style="color: #FFFFFF; font-size: 30px; font-weight: bold;">{df['distance_km'].mean():.2f} <span style="font-size:18px;">km</span></div>
        </div>
        <div style="flex: 1; background-color: #000000; border-radius: 8px; padding: 20px; box-shadow: 0 4px 10px rgba(0,0,0,0.15);">
            <div style="color: #A6A6A6; font-size: 13px; font-weight: 600; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 8px;">Date Range</div>
            <div style="color: #FFFFFF; font-size: 16px; font-weight: bold; line-height: 1.3;">
                {df['pickup_datetime'].min().date()}<br>to {df['pickup_datetime'].max().date()}
            </div>
        </div>
    </div>
"""
st.markdown(kpi_html, unsafe_allow_html=True)

st.markdown("""
<div style="padding: 10px;">
<br>
<h3 style="color: #000000; font-size: 24px; text-transform: uppercase; letter-spacing: 1.5px; margin-bottom: 20px; font-weight: 700;">How to use this dashboard</h3>
<ul style="color: #333333; font-size: 26px; line-height: 1.6; padding-left: 25px; margin-bottom: 80px;">
<li style="margin-bottom: 10px;"><b>Top Navigation Bar:</b> Use the black menu at the very top of the screen to seamlessly explore completely different dimensions: Financials, Geospatial data, and Temporal trends.</li>
<li style="margin-bottom: 10px;"><b>Interactive Insight Expanders:</b> Every single visualization is accompanied by a dedicated "View Insight" panel beneath it, instantly translating the raw mathematical data into plain English.</li>
</ul>
</div>
""", unsafe_allow_html=True)

# Footer Section
from utils import render_footer
render_footer()
