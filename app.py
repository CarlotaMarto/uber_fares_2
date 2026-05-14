import streamlit as st
from utils import inject_custom_css

# This must be the very first Streamlit command
st.set_page_config(
    page_title="Uber Fare Explorer",
    page_icon="uber_logo.png",
    layout="wide",
    initial_sidebar_state="collapsed",
)

@st.dialog("User Authentication")
def auth_modal(mode="login"):
    if mode == "login":
        st.markdown("<h2 style='text-align: center; color: #333333; font-family: sans-serif; margin-bottom: 20px; font-weight: 700;'>Login</h2>", unsafe_allow_html=True)
        st.text_input("Email", placeholder="name@company.com", key="email_login")
        st.text_input("Password", type="password", placeholder="••••••••", key="pass_login")
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("SIGN IN", type="primary", use_container_width=True):
            st.session_state['logged_in_user'] = "Jane Doe"
            if 'action' in st.query_params:
                del st.query_params['action']
            st.success("Successfully signed in! Select your dashboard role below.")
            st.rerun()
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #666; font-size: 14px;'>Forgot your password?</p>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #666; font-size: 14px;'>Don't have an account? <a href='?action=register' target='_self' style='color: #0ea5e9; font-weight: bold; text-decoration: none;'>Sign up!</a></p>", unsafe_allow_html=True)
    else:
        st.markdown("<h2 style='text-align: center; color: #333333; font-family: sans-serif; margin-bottom: 20px; font-weight: 700;'>Create Account</h2>", unsafe_allow_html=True)
        st.text_input("First Name", placeholder="Jane", key="fn_reg")
        st.text_input("Last Name", placeholder="Doe", key="ln_reg")
        st.text_input("Email", placeholder="name@company.com", key="email_reg")
        st.text_input("Password", type="password", placeholder="••••••••", key="pass_reg")
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("REGISTER", type="primary", use_container_width=True):
            fn = st.session_state.get('fn_reg', 'Jane')
            ln = st.session_state.get('ln_reg', 'Doe')
            full = f"{fn} {ln}".strip()
            st.session_state['logged_in_user'] = full if full else "Jane Doe"
            if 'action' in st.query_params:
                del st.query_params['action']
            st.success("Successfully registered! You can now select your dashboard role below.")
            st.rerun()
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("<p style='text-align: center; color: #666; font-size: 14px;'>Already have an account? <a href='?action=login' target='_self' style='color: #0ea5e9; font-weight: bold; text-decoration: none;'>Sign in!</a></p>", unsafe_allow_html=True)

if 'action' in st.query_params:
    action = st.query_params['action']
    auth_modal(mode="login" if action=="login" else "register")

if 'role' in st.query_params:
    if st.query_params['role'] == 'user':
        st.session_state['user_type'] = 'Uber User'
    elif st.query_params['role'] in ['owner', 'analyst']:
        st.session_state['user_type'] = 'Uber Analyst'

# Inject the global CSS and Top Navbar onto every page
inject_custom_css()

if 'user_type' not in st.session_state:
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    st.markdown("<h1 style='text-align: center; color: #000000;'>Welcome to Uber Fare Explorer</h1>", unsafe_allow_html=True)
    st.markdown("<p style='text-align: center; font-size: 24px; color: #666666; max-width: 720px; margin: 0 auto;'>Choose the experience that matches your role and get started with focused insights tailored for user or analyst.</p>", unsafe_allow_html=True)
    st.markdown("<br><br>", unsafe_allow_html=True)

    user_cols = st.columns(2, gap='large')
    with user_cols[0]:
        from utils import get_base64_bin_help
        import os
        
        user_bg_b64 = ""
        user_mime = "png"
        for ext in ["webp", "jpg", "png", "jpeg"]:
            if os.path.exists(f"uber_users_image.{ext}"):
                user_bg_b64 = get_base64_bin_help(f"uber_users_image.{ext}")
                user_mime = ext if ext != "jpg" else "jpeg"
                break

        if user_bg_b64:
            user_bg_style = f"background: linear-gradient(to bottom right, rgba(255, 255, 255, 0.1), rgba(255, 255, 255, 0.3)), url('data:image/{user_mime};base64,{user_bg_b64}'); background-size: cover; background-position: center;"
        else:
            user_bg_style = "background: #ffffff;"

        st.markdown(
            f"""
<div style="border: 1px solid #E5E7EB; border-radius: 24px; padding: 28px; {user_bg_style} box-shadow: 0 30px 80px rgba(15, 23, 42, 0.06); transition: transform 0.3s ease;">
  <div style="background: rgba(255, 255, 255, 0.75); padding: 24px; border-radius: 16px; backdrop-filter: blur(8px); box-shadow: 0 4px 6px rgba(0,0,0,0.05);">
    <p style='font-size: 16px; letter-spacing: 0.2em; text-transform: uppercase; color: #0ea5e9; margin-bottom: 16px; font-weight: 800;'>Uber User</p>
    <h2 style='margin: 0 0 16px; font-size: 28px; line-height: 1.1; color: #000000;'>Ride smarter</h2>
    <p style='color: #334155; font-size: 16px; line-height: 1.75; margin-bottom: 24px;'>Discover fare trends, busiest times and neighborhood cost signals to plan better trips and save money.</p>
    <a href="?role=user" target="_self" style="display: block; width: 100%; text-align: center; background: #000000; color: #ffffff; padding: 12px; border-radius: 8px; text-decoration: none; font-weight: 600; border: 1px solid #000000; font-family: sans-serif;">Enter as User</a>
  </div>
</div>
            """,
            unsafe_allow_html=True,
        )

    with user_cols[1]:
        from utils import get_base64_bin_help
        
        bg_image_b64 = ""
        owner_mime = "png"
        for ext in ["jpg", "png", "jpeg", "webp"]:
            if os.path.exists(f"dashboard_bg.{ext}"):
                bg_image_b64 = get_base64_bin_help(f"dashboard_bg.{ext}")
                owner_mime = ext if ext != "jpg" else "jpeg"
                break

        if bg_image_b64:
            bg_style = f"background: linear-gradient(to bottom right, rgba(255, 255, 255, 0.1), rgba(255, 255, 255, 0.3)), url('data:image/{owner_mime};base64,{bg_image_b64}'); background-size: cover; background-position: center;"
        else:
            bg_style = "background: #ffffff;"

        st.markdown(
            f"""
<div style="border: 1px solid #E5E7EB; border-radius: 24px; padding: 28px; {bg_style} box-shadow: 0 30px 80px rgba(15, 23, 42, 0.06); transition: transform 0.3s ease;">
  <div style="background: rgba(255, 255, 255, 0.75); padding: 24px; border-radius: 16px; backdrop-filter: blur(8px); box-shadow: 0 4px 6px rgba(0,0,0,0.05);">
    <p style='font-size: 16px; letter-spacing: 0.2em; text-transform: uppercase; color: #0ea5e9; margin-bottom: 16px; font-weight: 800;'>Uber Analyst</p>
    <h2 style='margin: 0 0 16px; font-size: 28px; line-height: 1.1; color: #000000;'>Manage operations</h2>
    <p style='color: #334155; font-size: 16px; line-height: 1.75; margin-bottom: 24px;'>Access business-level insights for cost savings, operational efficiency and pricing optimization.</p>
    <a href="?role=analyst" target="_self" style="display: block; width: 100%; text-align: center; background: #000000; color: #ffffff; padding: 12px; border-radius: 8px; text-decoration: none; font-weight: 600; border: 1px solid #000000; font-family: sans-serif;">Enter as Analyst</a>
  </div>
</div>
            """,
            unsafe_allow_html=True,
        )

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
p8 = st.Page("pages/8_Savings.py", title="Savings", url_path="savings")

# Define pages based on user type
user_type = st.session_state.get('user_type', 'Uber User')
if user_type == "Uber User":
    pages = [p_home, p1, p2, p3, p4, p8, p7]
else:  # Uber Owner
    pages = [p_home, p1, p2, p3, p4, p5, p6, p7]

# Run the router and completely hide the default sidebar menu
pg = st.navigation(pages, position="hidden")
pg.run()
