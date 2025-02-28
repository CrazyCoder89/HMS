import streamlit as st
import sqlite3
from datetime import datetime

# Custom CSS for styling
st.markdown(
    """
    <style>
        .stButton>button {
            width: 100%;
            height: 50px;
            font-size: 18px;
            border-radius: 10px;
            transition: 0.3s;
        }
        .stButton>button:hover {
            background-color: #4CAF50;
            color: white;
        }
        .header-container {
            text-align: center;
            padding: 10px;
            background-color: #2E3B4E;
            color: white;
            border-radius: 10px;
        }
    </style>
    """,
    unsafe_allow_html=True
)

# Fetch doctor's name from session
if "username" not in st.session_state or "role" not in st.session_state:
    st.error("You must be logged in to access the dashboard.")
    st.stop()

doctor_name = st.session_state["username"]
role = st.session_state["role"]

if role != "Doctor":
    st.error("Unauthorized access. This page is for doctors only.")
    st.stop()

# Header
st.markdown(f"<div class='header-container'><h1>👨‍⚕️ Dr. {doctor_name}'s Dashboard</h1></div>", unsafe_allow_html=True)

st.write("### Choose an option below:")

# Layout with buttons
col1, col2 = st.columns(2)

with col1:
    if st.button("📊 Survival Model Analysis"):
        st.switch_page("pages/survival_analysis.py")
    if st.button("📅 Length of Stay Prediction"):
        st.switch_page("pages/los_prediction.py")

with col2:
    if st.button("⚕️ Risk Analysis"):
        st.switch_page("pages/risk_analysis.py")
    if st.button("📋 Patient Medical Records"):
        st.switch_page("pages/patient_records.py")

# Footer
st.markdown("---")
st.caption(f"Logged in as: **Dr. {doctor_name}** | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")


# Logout Button
st.divider()
if st.button("❌ Logout"):
    st.session_state["logged_in"] = False
    st.session_state["username"] = None
    st.session_state["role"] = None
    st.switch_page("Main.py")
