import streamlit as st
import sqlite3
import uuid  # To generate unique Patient IDs

# Ensure user is logged in
if "logged_in" not in st.session_state or not st.session_state["logged_in"]:
    st.switch_page("pages/login.py")

# Page Configuration
st.set_page_config(page_title="Add New Patient", layout="wide")

st.title("➕ Add New Patient")

# Database Connection
conn = sqlite3.connect("database/hms_database.db")
c = conn.cursor()

# Create Patients Table if Not Exists
c.execute("""
    CREATE TABLE IF NOT EXISTS patients (
        patient_id TEXT PRIMARY KEY,
        name TEXT,
        age INTEGER,
        gender TEXT,
        smoking TEXT,
        diabetes TEXT,
        hypertension TEXT,
        CAD TEXT,
        admission_type TEXT,
        HB REAL,
        TLC REAL,
        glucose REAL,
        urea REAL,
        creatinine REAL,
        BNP REAL,
        EF REAL
    )
""")
conn.commit()

# Generate a unique Patient ID
patient_id = str(uuid.uuid4())[:8]  # Shorter version of UUID

# Patient Information Form
with st.form("add_patient_form", clear_on_submit=True):
    st.subheader("👤 Patient Information")
    st.text(f"📄 **Generated Patient ID:** {patient_id}")  # Display Patient ID
    name = st.text_input("Full Name")
    age = st.number_input("Age", min_value=0, max_value=120, step=1)
    gender = st.radio("Gender", ("Male", "Female"))

    st.subheader("🏥 Admission Details")
    admission_type = st.selectbox("Admission Type", ("EMERGENCY", "OPD"))  # Fixed label

    st.subheader("🩺 Medical History")
    smoking = st.selectbox("Smoking", ("No", "Yes"))
    diabetes = st.selectbox("Diabetes", ("No", "Yes"))
    hypertension = st.selectbox("Hypertension", ("No", "Yes"))
    CAD = st.selectbox("Coronary Artery Disease (CAD)", ("No", "Yes"))

    st.subheader("🔬 Lab Reports")
    HB = st.number_input("Hemoglobin (HB)", min_value=0.0, max_value=20.0, step=0.1)
    TLC = st.number_input("Total Leukocyte Count (TLC)", min_value=0.0, max_value=50.0, step=0.1)
    glucose = st.number_input("Glucose Level", min_value=0.0, max_value=500.0, step=1.0)
    urea = st.number_input("Urea Level", min_value=0.0, max_value=200.0, step=0.1)
    creatinine = st.number_input("Creatinine Level", min_value=0.0, max_value=10.0, step=0.1)
    BNP = st.number_input("BNP (Brain Natriuretic Peptide)", min_value=0.0, max_value=5000.0, step=1.0)
    EF = st.number_input("Ejection Fraction (EF)", min_value=0.0, max_value=100.0, step=1.0)

    submit_button = st.form_submit_button("✅ Add Patient")

# Insert Data into Database
if submit_button:
    if name:
        c.execute("""
            INSERT INTO patients (patient_id, name, age, gender, smoking, diabetes, hypertension, CAD, admission_type, HB, TLC, glucose, urea, creatinine, BNP, EF)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (patient_id, name, age, gender, smoking, diabetes, hypertension, CAD, admission_type, HB, TLC, glucose, urea, creatinine, BNP, EF))
        conn.commit()
        st.success(f"✅ Patient {name} added successfully! 📄 Patient ID: **{patient_id}**")
    else:
        st.error("⚠️ Please enter a valid name!")

conn.close()

# Back Button
st.divider()
if st.button("🔙 Back to Dashboard"):
    st.switch_page("pages/staff_dashboard.py")


