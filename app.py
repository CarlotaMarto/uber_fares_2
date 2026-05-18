import streamlit as st
from utils import inject_custom_css

# This must be the very first Streamlit command
st.set_page_config(
    page_title="Uber Fare Explorer",
    page_icon="uber_logo.jpg",
    layout="wide",
    initial_sidebar_state="collapsed",
)

@st.dialog("User Authentication")
def auth_modal(mode="login"):
    role = st.query_params.get('role', '')
    role_qs = f"?role={role}&" if role else "?"
    if mode == "login":
        st.markdown("<h2 style='text-align: center; color: #333333; font-family: sans-serif; margin-bottom: 20px; font-weight: 700;'>Login</h2>", unsafe_allow_html=True)
        with st.form("login_form", border=False):
            st.text_input("First Name", placeholder="Jane", key="fn_login")
            st.text_input("Last Name", placeholder="Doe", key="ln_login")
            st.text_input("Email", placeholder="name@company.com", key="email_login")
            st.text_input("Password", type="password", placeholder="••••••••", key="pass_login")
            st.markdown("<br>", unsafe_allow_html=True)
            submitted = st.form_submit_button("SIGN IN", type="primary", use_container_width=True)
            if submitted:
                email = st.session_state.get('email_login', 'user@example.com')
                fn = st.session_state.get('fn_login', 'Jane')
                ln = st.session_state.get('ln_login', 'Doe')
                full = f"{fn} {ln}".strip().title()
                st.session_state['logged_in_user'] = full if full else "Jane Doe"
                st.session_state['user_email'] = email
                st.session_state['auth_success'] = True
                st.session_state['just_authenticated'] = True
                if 'action' in st.query_params:
                    del st.query_params['action']
                st.rerun()
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(f"<p style='text-align: center; color: #666; font-size: 14px;'><a href='{role_qs}action=forgot' target='_self' style='color: #0ea5e9; font-weight: bold; text-decoration: none;'>Forgot your password?</a></p>", unsafe_allow_html=True)
        st.markdown(f"<p style='text-align: center; color: #666; font-size: 14px;'>Don't have an account? <a href='{role_qs}action=register' target='_self' style='color: #0ea5e9; font-weight: bold; text-decoration: none;'>Sign up!</a></p>", unsafe_allow_html=True)
    elif mode == "register":
        st.markdown("<h2 style='text-align: center; color: #333333; font-family: sans-serif; margin-bottom: 20px; font-weight: 700;'>Create Account</h2>", unsafe_allow_html=True)
        with st.form("reg_form", border=False):
            st.text_input("First Name", placeholder="Jane", key="fn_reg")
            st.text_input("Last Name", placeholder="Doe", key="ln_reg")
            st.text_input("Email", placeholder="name@company.com", key="email_reg")
            st.text_input("Password", type="password", placeholder="••••••••", key="pass_reg")
            st.markdown("<br>", unsafe_allow_html=True)
            submitted = st.form_submit_button("REGISTER", type="primary", use_container_width=True)
            if submitted:
                email = st.session_state.get('email_reg', 'user@example.com')
                fn = st.session_state.get('fn_reg', 'Jane')
                ln = st.session_state.get('ln_reg', 'Doe')
                full = f"{fn} {ln}".strip().title()
                st.session_state['logged_in_user'] = full if full else "Jane Doe"
                st.session_state['user_email'] = email
                st.session_state['auth_success'] = True
                st.session_state['just_authenticated'] = True
                if 'action' in st.query_params:
                    del st.query_params['action']
                st.rerun()
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(f"<p style='text-align: center; color: #666; font-size: 14px;'>Already have an account? <a href='{role_qs}action=login' target='_self' style='color: #0ea5e9; font-weight: bold; text-decoration: none;'>Sign in!</a></p>", unsafe_allow_html=True)
    elif mode == "forgot":
        st.markdown("<h2 style='text-align: center; color: #333333; font-family: sans-serif; margin-bottom: 20px; font-weight: 700;'>Reset Password</h2>", unsafe_allow_html=True)
        
        # Check if code is already sent in session state
        reset_code = st.session_state.get('reset_code')
        
        if not reset_code:
            # Step 1: Request verification code
            with st.form("forgot_form", border=False):
                email = st.text_input("Email", placeholder="name@company.com", key="email_forgot")
                st.markdown("<br>", unsafe_allow_html=True)
                submitted = st.form_submit_button("SEND RESET CODE", type="primary", use_container_width=True)
                if submitted:
                    if not email:
                        st.error("Please enter your email.")
                    else:
                        import random
                        from utils import send_reset_email
                        code = f"{random.randint(100000, 999999)}"
                        st.session_state['reset_code'] = code
                        st.session_state['reset_email'] = email
                        
                        # Send email
                        send_reset_email(email, code)
                        st.toast("Verification code sent to your email!")
                        st.rerun()
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown(f"<p style='text-align: center; color: #666; font-size: 14px;'><a href='{role_qs}action=login' target='_self' style='color: #0ea5e9; font-weight: bold; text-decoration: none;'>Back to Sign in</a></p>", unsafe_allow_html=True)
        else:
            # Step 2: Verification and reset password
            with st.form("reset_form", border=False):
                st.markdown(f"<p style='text-align: center; color: #666; font-size: 14px;'>Verification code sent to <b>{st.session_state.get('reset_email', '')}</b></p>", unsafe_allow_html=True)
                entered_code = st.text_input("Verification Code", placeholder="123456", key="entered_code")
                new_pass = st.text_input("New Password", type="password", placeholder="••••••••", key="new_pass")
                confirm_pass = st.text_input("Re-enter New Password", type="password", placeholder="••••••••", key="confirm_pass")
                st.markdown("<br>", unsafe_allow_html=True)
                submitted = st.form_submit_button("RESET PASSWORD", type="primary", use_container_width=True)
                if submitted:
                    if not entered_code or not new_pass or not confirm_pass:
                        st.error("Please fill in all fields.")
                    elif entered_code.strip() != reset_code:
                        st.error("Incorrect verification code.")
                    elif new_pass != confirm_pass:
                        st.error("Passwords do not match.")
                    else:
                        st.session_state['just_reset'] = True
                        # Clean up
                        del st.session_state['reset_code']
                        del st.session_state['reset_email']
                        
                        # Go back to login
                        st.query_params['action'] = 'login'
                        st.rerun()
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown(f"<p style='text-align: center; color: #666; font-size: 14px;'>Didn't receive the code? <a href='{role_qs}action=forgot&restart=1' target='_self' style='color: #0ea5e9; font-weight: bold; text-decoration: none;'>Resend / Start over</a></p>", unsafe_allow_html=True)
            st.markdown(f"<p style='text-align: center; color: #666; font-size: 14px;'><a href='{role_qs}action=login' target='_self' style='color: #0ea5e9; font-weight: bold; text-decoration: none;'>Back to Sign in</a></p>", unsafe_allow_html=True)

if 'role' in st.query_params:
    if st.query_params['role'] == 'user':
        st.session_state['user_type'] = 'Uber User'
    elif st.query_params['role'] in ['owner', 'analyst']:
        st.session_state['user_type'] = 'Uber Analyst'

if 'restart' in st.query_params:
    if 'reset_code' in st.session_state:
        del st.session_state['reset_code']
    if 'reset_email' in st.session_state:
        del st.session_state['reset_email']
    del st.query_params['restart']

if 'action' in st.query_params and not st.session_state.get('auth_success', False):
    if 'user_type' in st.session_state:
        action = st.query_params['action']
        if action == "forgot":
            auth_modal(mode="forgot")
        else:
            auth_modal(mode="login" if action=="login" else "register")
    else:
        if 'action' in st.query_params:
            del st.query_params['action']

if st.session_state.get('just_reset', False):
    st.toast("Password reset successfully! Please sign in with your new password.")
    st.session_state['just_reset'] = False

if st.session_state.get('auth_success', False):
    if st.session_state.get('just_authenticated', False):
        from utils import send_welcome_email
        user_email = st.session_state.get('user_email', '')
        user_name = st.session_state.get('logged_in_user', 'Jane Doe')
        site_url = "https://uberfares2-bwwu3ppswfnzujfisnbeoc.streamlit.app/" 
        user_type = st.session_state.get('user_type', 'User')
        send_welcome_email(user_email, user_name, site_url, user_type)
        if user_email:
            st.toast("Check your email box!")
        st.session_state['just_authenticated'] = False
        
    # Reset it so it doesn't stay forever, but we need it to be False eventually.
    # Wait, if we reset it, and query_params still has action, it will reopen.
    # But since we did del st.query_params['action'] and reran, next rerun SHOULD NOT have it.
    # So we can safely reset it here if we assume the browser updated the URL.
    st.session_state['auth_success'] = False

if 'user_type' not in st.session_state:
    # Inject styling for the welcome screen
    inject_custom_css()
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
inject_custom_css(pg.url_path)
pg.run()
