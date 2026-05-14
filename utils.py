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
    user_type = st.session_state.get('user_type', '')
    role_param = ""
    if user_type == "Uber User":
        role_param = "?role=user"
    elif user_type in ["Uber Owner", "Uber Analyst"]:
        role_param = "?role=owner"

    logged_user = st.session_state.get('logged_in_user', '')
    user_svg = '<svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" style="margin-left: 8px;"><circle cx="12" cy="8" r="4"></circle><path d="M18 20v-2a4 4 0 0 0-4-4H10a4 4 0 0 0-4 4v2"></path><circle cx="12" cy="12" r="10"></circle></svg>'
    
    if logged_user:
        user_display = f'<div style="display: flex; align-items: center; color: #FFFFFF; font-family: \'Inter\', sans-serif; font-size: 14px; font-weight: 500; opacity: 0.9; margin-left: 20px; border-left: 1px solid #333; padding-left: 20px;">{logged_user}{user_svg}</div>'
    else:
        user_display = f'<a href="?action=login" target="_self" style="display: flex; align-items: center; color: #FFFFFF; text-decoration: none; font-family: \'Inter\', sans-serif; font-size: 14px; font-weight: 500; opacity: 0.8; margin-left: 20px; border-left: 1px solid #333; padding-left: 20px;">Sign In{user_svg}</a>'

    if user_type == "Uber User":
        nav_links = f'<a href="/{role_param}" target="_self" class="nav-link">About Us</a><a href="geospatial-hub{role_param}" target="_self" class="nav-link">Maps</a><a href="temporal-analysis{role_param}" target="_self" class="nav-link">Time</a><a href="distributions{role_param}" target="_self" class="nav-link">Prices</a><a href="segment-encyclopedia{role_param}" target="_self" class="nav-link">Profiles</a><span style="color: #555555; margin-right: 25px;">|</span><a href="savings{role_param}" target="_self" class="nav-link">Savings</a>'
        right_button = f"""<div style="display: flex; align-items: center;"><a href="ride-simulator{role_param}" target="_self" class="btn-simulator">Ride Simulator</a>{user_display}</div>"""
    elif user_type in ["Uber Owner", "Uber Analyst"]:
        nav_links = f'<a href="/{role_param}" target="_self" class="nav-link">About Us</a><a href="geospatial-hub{role_param}" target="_self" class="nav-link">Maps</a><a href="temporal-analysis{role_param}" target="_self" class="nav-link">Time</a><a href="distributions{role_param}" target="_self" class="nav-link">Prices</a><a href="segment-encyclopedia{role_param}" target="_self" class="nav-link">Profiles</a><span style="color: #555555; margin-right: 25px;">|</span><a href="advanced-analysis{role_param}" target="_self" class="nav-link">Advanced</a><a href="business-strategy{role_param}" target="_self" class="nav-link">Strategy</a>'
        right_button = f"""<div style="display: flex; align-items: center;"><a href="ride-simulator{role_param}" target="_self" class="btn-simulator">Ride Simulator</a>{user_display}</div>"""
    else:
        nav_links = ""
        right_button = f"""<div style="display: flex; align-items: center;">{user_display}</div>"""

    # Global Map Background
    bg_b64 = get_base64_bin_help("map_with_black_car_midright.png")
    bg_css = ""
    if bg_b64:
        bg_css = f"""
        .stApp {{
            background-image: linear-gradient(rgba(255, 255, 255, 0.55), rgba(255, 255, 255, 0.70)), url('data:image/png;base64,{bg_b64}');
            background-size: cover;
            background-attachment: fixed;
            background-position: center;
        }}
        """

    st.markdown(
        f"""
        <style>
        {bg_css}
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
        
        /* Hide sidebar entirely */
        [data-testid="collapsedControl"] {{display: none !important;}}
        [data-testid="stSidebar"] {{display: none !important;}}
        
        /* Hide Streamlit structural branding and anchor links */
        #MainMenu {{visibility: hidden;}}
        header {{visibility: hidden;}}
        footer {{visibility: hidden;}}
        .header-anchor, [data-testid="stHeaderAnchor"], [data-testid="stHeaderActionElements"], a.header-anchor, .st-header-anchor, .stMarkdown h1 a, .stMarkdown h2 a, .stMarkdown h3 a {{display: none !important; visibility: hidden !important; opacity: 0 !important; pointer-events: none !important;}}
        
        /* Plotly Modebar Customization: Hide Pan and Replace Camera with Download Arrow */
        a[data-title*="Pan"], .modebar-btn[data-title*="Pan"] {{display: none !important;}}
        a[data-title*="Download"] svg, .modebar-btn[data-title*="Download"] svg {{display: none !important;}}
        a[data-title*="Download"]::before, .modebar-btn[data-title*="Download"]::before {{content: "⬇" !important; font-size: 16px !important; font-weight: bold !important; padding: 0 4px !important; color: #333333 !important;}}
        
        /* Streamlit Tabs Customization: Override default red highlight with cyan/blue */
        div[data-testid="stTabs"] button[aria-selected="true"] {{color: #0ea5e9 !important; border-bottom-color: #0ea5e9 !important;}}
        div[data-testid="stTabs"] button:hover {{color: #0ea5e9 !important; border-bottom-color: rgba(14, 165, 233, 0.5) !important;}}
        
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
        """, unsafe_allow_html=True)
    logo_b64 = get_base64_bin_help("uber_logo.jpg")
    mime = "jpeg"
    if not logo_b64:
        logo_b64 = get_base64_bin_help("uber_logo.png")
        mime = "png"
    
    logo_html = f"<img src='data:image/{mime};base64,{logo_b64}' style='height: 32px; margin-right: 8px; border-radius: 4px;'/>" if logo_b64 else ""

    st.markdown(f"""
<div class="uber-navbar" style="justify-content: space-between;">
<div style="display: flex; align-items: center;">
<a href="/" target="_self" class="uber-logo-text" style="margin-right: 30px; text-decoration: none; color: #FFFFFF !important; display: flex; align-items: center;">{logo_html}Uber</a>
<div style="border-left: 1px solid #333; padding-left: 20px; display: flex; align-items: center;">
{nav_links}
</div>
</div>
<div>
{right_button}
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
        st.image("uber_logo.png", width=120)
        st.caption("This project is optimized for executive-level business intelligence and strategic decision making.")
        
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('''
    <div style="background-color: #000000; padding: 20px; border-radius: 4px; display: flex; justify-content: space-between; color: #666666; font-size: 12px; font-family: \'Inter\', sans-serif;">
        <div>© 2026 Uber Fare Explorer Project - Academic Use Only</div>
        <div>Built for Machine Learning II</div>
    </div>
    ''', unsafe_allow_html=True)
