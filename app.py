import streamlit as st
from utils import inject_custom_css

# This must be the very first Streamlit command
st.set_page_config(
    page_title="Uber Fare Explorer",
    page_icon="uber_logo.jpg",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# Inject the global CSS and Top Navbar onto every page
inject_custom_css()

if 'user_type' not in st.session_state:
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    st.markdown("<h1 style='text-align: center; color: #000000;'>Welcome to Uber Fare Explorer</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-size: 18px; color: #666666; max-width: 720px; margin: 0 auto;'>Choose the experience that matches your role and get started with focused insights tailored for riders or owners.</p>", unsafe_allow_html=True)
    st.markdown("<br><br>", unsafe_allow_html=True)

    user_cols = st.columns(2, gap='large')
    with user_cols[0]:
        st.markdown(
            """
            <div style='border: 1px solid #E5E7EB; border-radius: 24px; padding: 28px; background: #ffffff; box-shadow: 0 30px 80px rgba(15, 23, 42, 0.06);'>
                <p style='font-size: 12px; letter-spacing: 0.2em; text-transform: uppercase; color: #0ea5e9; margin-bottom: 16px;'>Uber User</p>
                <h2 style='margin: 0 0 16px; font-size: 28px; line-height: 1.1;'>Ride smarter</h2>
                <p style='color: #475569; font-size: 16px; line-height: 1.75;'>Discover fare trends, busiest times and neighborhood cost signals to plan better trips and save money.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("Enter as User", use_container_width=True, key='user_button'):
            st.session_state['user_type'] = 'Uber User'
            st.rerun()

    with user_cols[1]:
        st.markdown(
            """
            <div style='border: 1px solid #E5E7EB; border-radius: 24px; padding: 28px; background: #ffffff; box-shadow: 0 30px 80px rgba(15, 23, 42, 0.06);'>
                <p style='font-size: 12px; letter-spacing: 0.2em; text-transform: uppercase; color: #0ea5e9; margin-bottom: 16px;'>Uber Owner</p>
                <h2 style='margin: 0 0 16px; font-size: 28px; line-height: 1.1;'>Manage operations</h2>
                <p style='color: #475569; font-size: 16px; line-height: 1.75;'>Access business-level insights for cost savings, operational efficiency and pricing optimization.</p>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("Enter as Owner", use_container_width=True, key='owner_button'):
            st.session_state['user_type'] = 'Uber Owner'
            st.rerun()

    st.stop()

# Explicitly define the pages and their exact URL paths
p_home = st.Page("pages/0_Home.py", title="Home", url_path="home", default=True)
p1 = st.Page("pages/1_Distributions.py", title="Distributions", url_path="distributions")
p2 = st.Page("pages/2_Temporal_Analysis.py", title="Temporal Analysis", url_path="temporal-analysis")
p3 = st.Page("pages/3_Segment_Encyclopedia.py", title="Segment Encyclopedia", url_path="segment-encyclopedia")
p4 = st.Page("pages/4_Geospatial_Hub.py", title="Geospatial Hub", url_path="geospatial-hub")
p5 = st.Page("pages/5_Advanced_Analysis.py", title="Advanced Analysis", url_path="advanced-analysis")
p6 = st.Page("pages/6_Business_Strategy.py", title="Business Strategy", url_path="business-strategy")
p7 = st.Page("pages/7_Ride_Simulator.py", title="Ride Simulator", url_path="ride-simulator")

# Define pages based on user type
user_type = st.session_state.get('user_type', 'Uber User')
if user_type == "Uber User":
    pages = [p_home, p1, p2, p3, p4]
else:  # Uber Owner
    pages = [p_home, p5, p6, p7]

# Run the router and completely hide the default sidebar menu
pg = st.navigation(pages, position="hidden")
pg.run()
