import os
import glob

# Add render_footer to utils.py
with open("utils.py", "a") as f:
    f.write("""

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
    <div style="background-color: #000000; padding: 20px; border-radius: 4px; display: flex; justify-content: space-between; color: #666666; font-size: 12px; font-family: \\'Inter\\', sans-serif;">
        <div>© 2024 Uber Fare Explorer Project - Academic Use Only</div>
        <div>Built for Machine Learning II</div>
    </div>
    ''', unsafe_allow_html=True)
""")

# Append to all pages (except 0_Home.py, which we will handle manually or edit here)
pages = glob.glob("pages/*.py")
for page in pages:
    if "0_Home" in page:
        continue
    
    with open(page, "a") as f:
        f.write("\n\nfrom utils import render_footer\nrender_footer()\n")

