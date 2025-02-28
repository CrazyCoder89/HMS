import streamlit as st
import sqlite3

# Ensure user is logged in
if "logged_in" not in st.session_state or not st.session_state["logged_in"]:
    st.switch_page("pages/login")

# Page Configuration
st.set_page_config(page_title="Staff Dashboard", layout="wide")

st.title("👨‍⚕️ Staff Dashboard")
st.write(f"Welcome, **{st.session_state['username']}**! Manage hospital operations efficiently.")

# Function to fetch staff details
def get_staff_info(username):
    """Fetch staff details from the database"""
    conn = sqlite3.connect("database/hms_database.db")
    c = conn.cursor()
    c.execute("SELECT username, role FROM users WHERE username=?", (username,))
    staff_info = c.fetchone()
    conn.close()
    return staff_info

# Display staff info
staff_info = get_staff_info(st.session_state["username"])
if staff_info:
    st.subheader("👤 Staff Information")
    st.write(f"**Name:** {staff_info[0]}")
    st.write(f"**Role:** {staff_info[1]}")
else:
    st.error("⚠️ Unable to fetch staff details.")

# Staff Task Buttons
st.subheader("🛠️ Staff Actions")

col1, col2 = st.columns(2)

with col1:
    if st.button("➕ Add New Patient"):
        st.switch_page("pages/add_patient.py")  # Redirect to Add Patient Page

    if st.button("💰 Billing & Payments"):
        st.switch_page("pages/billing.py")  # Redirect to Billing Page

with col2:
    if st.button("📢 Manage Health Campaigns"):
        st.switch_page("pages/pollution_campaign.py")  # Redirect to Health Campaign Page

    if st.button("🛏️ Bed Availability"):
        st.switch_page("pages/bed_availability.py")  # Redirect to Bed Availability Page

# Logout Button
st.divider()
if st.button("❌ Logout"):
    st.session_state["logged_in"] = False
    st.session_state["username"] = None
    st.session_state["role"] = None
    st.switch_page("Main.py")
