import streamlit as st
try:
    st.page_link(st.Page("app.py", title="Home", url_path="home"), label="Home")
    st.page_link(st.Page("pages/1_Distributions.py", title="Distributions", url_path="distributions"), label="1. Distributions")
    st.write("st.Page objects worked!")
except Exception as e:
    st.write("Error:", str(e))
