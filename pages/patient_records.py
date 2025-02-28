import streamlit as st
import sqlite3
import pandas as pd

# Database Connection
def get_patient_medical_records(patient_id):
    conn = sqlite3.connect("database/hms_database.db")  
    query = """SELECT visit_date, diagnosis, treatment, prescriptions, lab_results, notes 
               FROM medical_records WHERE patient_id=? ORDER BY visit_date DESC"""
    records = pd.read_sql_query(query, conn, params=(patient_id,))
    conn.close()
    return records

# Function to Save New Record
def save_medical_record(patient_id, visit_date, diagnosis, treatment, prescriptions, lab_results, notes):
    conn = sqlite3.connect("database/hms_database.db")  
    cursor = conn.cursor()
    
    cursor.execute(
        """INSERT INTO medical_records (patient_id, visit_date, diagnosis, treatment, prescriptions, lab_results, notes) 
        VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (patient_id, visit_date, diagnosis, treatment, prescriptions, lab_results, notes)
    )
    
    conn.commit()
    conn.close()

# Page UI
st.title("📋 Patient Medical Records")

# Patient ID Input
patient_id = st.text_input("🔍 Enter Patient ID to Fetch Records")

# Fetch Button
if st.button("Fetch Medical Records"):
    if patient_id:
        records = get_patient_medical_records(patient_id)
        if not records.empty:
            st.success(f"✅ Medical records found for **Patient ID: {patient_id}**")
            st.dataframe(records)
        else:
            st.warning("⚠️ No medical records found for this patient.")
    else:
        st.error("❌ Please enter a valid Patient ID.")

# Add New Record
st.header("🆕 Add New Medical Record")

visit_date = st.date_input("📅 Visit Date")
diagnosis = st.text_area("🩺 Diagnosis")
treatment = st.text_area("💊 Treatment Plan")
prescriptions = st.text_area("📝 Prescriptions")
lab_results = st.text_area("🧪 Lab Results")
notes = st.text_area("🗒️ Additional Notes")

if st.button("Save Medical Record"):
    if patient_id and diagnosis:
        save_medical_record(patient_id, visit_date, diagnosis, treatment, prescriptions, lab_results, notes)
        st.success("✅ Medical record added successfully!")
    else:
        st.error("❌ Patient ID and Diagnosis are required!")

# Back Button
st.divider()
if st.button("🔙 Back to Dashboard"):
    st.switch_page("pages/doctor_dashboard.py")
