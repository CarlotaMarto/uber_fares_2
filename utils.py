import streamlit as st
import pandas as pd
import base64
import os

@st.cache_data
def load_data():
    df = pd.read_csv("uber_with_clusters.csv") if os.path.exists("uber_with_clusters.csv") else pd.read_csv("uber_cleaned.csv")
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
        df['cluster'] = pd.to_numeric(df['cluster'], errors='coerce')
        df['cluster'] = df['cluster'].map(cluster_labels).fillna("Unknown Cluster")
    return df

def get_base64_bin_help(bin_file):
    if not os.path.exists(bin_file):
        return ""
    with open(bin_file, 'rb') as f:
        data = f.read()
    return base64.b64encode(data).decode()

def inject_custom_css():
    st.markdown(
        f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
        
        /* Hide sidebar entirely */
        [data-testid="collapsedControl"] {{display: none !important;}}
        [data-testid="stSidebar"] {{display: none !important;}}
        
        /* Hide Streamlit structural branding */
        #MainMenu {{visibility: hidden;}}
        header {{visibility: hidden;}}
        footer {{visibility: hidden;}}
        
        /* Remove padding around the main block */
        .block-container {{
            padding-top: 80px !important;
            padding-bottom: 0rem !important;
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
        .uber-logo-text {{
            color: #FFFFFF !important;
            font-family: 'Inter', sans-serif;
            font-size: 28px;
            font-weight: 400;
            letter-spacing: -0.5px;
            margin-right: 40px;
            text-decoration: none !important;
        }}
        .nav-link {{
            color: #FFFFFF !important;
            font-family: 'Inter', sans-serif;
            font-size: 14px;
            font-weight: 500;
            text-decoration: none !important;
            margin-right: 25px;
            opacity: 0.7;
            transition: opacity 0.2s;
        }}
        .nav-link:hover {{
            opacity: 1.0;
        }}
        .btn-simulator {{
            color: #06C167 !important;
            font-family: 'Inter', sans-serif;
            font-size: 16px !important;
            font-weight: 800 !important;
            text-decoration: none !important;
            margin-right: 20px;
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
            background-color: rgba(255,255,255,0.5);
            border-radius: 1px;
        }}
        </style>
        
        <div class="uber-navbar" style="justify-content: space-between;">
            <div style="display: flex; align-items: center;">
                <a href="/" target="_top" class="uber-logo-text" style="margin-right: 30px; text-decoration: none; color: #FFFFFF !important;">Uber</a>
                <div style="border-left: 1px solid #333; padding-left: 20px; display: flex; align-items: center;">
                    <a href="geospatial-hub" target="_top" class="nav-link">Maps</a>
                    <a href="temporal-analysis" target="_top" class="nav-link">Time</a>
                    <a href="distributions" target="_top" class="nav-link">Prices</a>
                    <a href="advanced-analysis" target="_top" class="nav-link">Advanced</a>
                    <a href="segment-encyclopedia" target="_top" class="nav-link">Profiles</a>
                    <a href="business-strategy" target="_top" class="nav-link">Strategy</a>
                </div>
            </div>
            <div>
                <a href="ride-simulator" target="_top" class="btn-simulator">Ride Simulator</a>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
    
    st.markdown("<br>", unsafe_allow_html=True)


def render_footer():
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("---")
    
    f_col1, f_col2, f_col3, f_col4 = st.columns([1, 1, 1, 1.5])
    
    with f_col1:
        st.markdown("<h4 style='color: #A6A6A6; font-size: 14px; text-transform: uppercase; letter-spacing: 1.5px; margin-bottom: 20px;'>Navigation</h4>", unsafe_allow_html=True)
        st.markdown("Use the Navigation Bar at the top of the screen.")
        
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
    st.markdown('''
    <div style="background-color: #000000; padding: 20px; border-radius: 4px; display: flex; justify-content: space-between; color: #666666; font-size: 12px; font-family: \'Inter\', sans-serif;">
        <div>© 2024 Uber Fare Explorer Project - Academic Use Only</div>
        <div>Built for Machine Learning II</div>
    </div>
    ''', unsafe_allow_html=True)
