import sqlite3
import pickle
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import streamlit as st

# -------- Initialize Session State --------
if "page" not in st.session_state:
    st.session_state["page"] = "pharmacy"
if "pharmacy_total" not in st.session_state:
    st.session_state["pharmacy_total"] = 0
if "patient_id" not in st.session_state:
    st.session_state["patient_id"] = ""

# -------- Database Setup --------
def init_db():
    conn = sqlite3.connect("database/hms_database.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS billing (
            patient_id TEXT PRIMARY KEY,
            pharmacy_total REAL DEFAULT 0,
            hospital_total REAL DEFAULT 0,
            grand_total REAL DEFAULT 0
        )
    """)
    conn.commit()
    conn.close()

def fetch_patient_details(patient_id):
    conn = sqlite3.connect("database/hms_database.db")
    c = conn.cursor()
    c.execute("SELECT age, gender, admission_type FROM patients WHERE patient_id = ?", (patient_id,))
    patient_details = c.fetchone()
    conn.close()
    return patient_details if patient_details else (None, None, None)

init_db()

def update_bill(patient_id, pharmacy_total, hospital_total, grand_total):
    conn = sqlite3.connect("database/hms_database.db")
    c = conn.cursor()
    c.execute("SELECT * FROM billing WHERE patient_id = ?", (patient_id,))
    existing_record = c.fetchone()
    
    if existing_record:
        c.execute("""
            UPDATE billing
            SET pharmacy_total = ?, hospital_total = ?, grand_total = ?
            WHERE patient_id = ?
        """, (pharmacy_total, hospital_total, grand_total, patient_id))
    else:
        c.execute("""
            INSERT INTO billing (patient_id, pharmacy_total, hospital_total, grand_total)
            VALUES (?, ?, ?, ?)
        """, (patient_id, pharmacy_total, hospital_total, grand_total))
    
    conn.commit()
    conn.close()

# -------- PHARMACY BILL PAGE --------
def pharmacy_bill():
    st.title("🛒 Pharmacy Billing System")
    
    patient_id = st.text_input("Enter Patient ID:", value=st.session_state["patient_id"])
    st.session_state["patient_id"] = patient_id.strip()
    
    if not patient_id:
        st.warning("⚠ Please enter a valid Patient ID to proceed.")
        return
    
    medicines = st.number_input("💊 Medicines Cost (₹)", min_value=0, value=500)
    injections = st.number_input("💉 Injections Cost (₹)", min_value=0, value=300)
    surgical_items = st.number_input("🔪 Surgical Items Cost (₹)", min_value=0, value=1000)
    consultation_fee = st.number_input("🩺 Consultation Fee (₹)", min_value=0, value=700)
    lab_tests = st.number_input("🧪 Lab Tests Cost (₹)", min_value=0, value=1500)
    
    pharmacy_total = medicines + injections + surgical_items + consultation_fee + lab_tests
    
    if st.button("Proceed to Hospital Bill"):
        st.session_state["pharmacy_total"] = pharmacy_total
        st.session_state["page"] = "hospital"
        st.rerun()

# -------- HOSPITAL BILL PAGE --------
def hospital_bill():
    st.title("🏥 Hospital Bill Estimator")
    
    patient_id = st.session_state["patient_id"]
    st.subheader(f"Patient ID: {patient_id}")
    
    age, gender, admission_type = fetch_patient_details(patient_id)
    if age is None:
        st.error("Patient details not found! Please enter a valid Patient ID.")
        return
    
    st.write(f"👤 Age: {age}")
    st.write(f"⚧ Gender: {gender}")
    st.write(f"🏥 Admission Type: {admission_type}")
    
    with open("models/hospital_bill.pkl", "rb") as file:
        model = pickle.load(file)
    with open("models/feature_names.pkl", "rb") as f:
        feature_names = pickle.load(f)
    
    los = st.number_input("Length of Stay (Days)", min_value=1, max_value=30, value=5)
    
    diseases = {
        "STEMI": 10000, "ACS": 8000, "Heart Failure": 12000, "CVA Infarct": 7000,
        "DVT": 5000, "Shock": 15000, "Pulmonary Embolism": 9000, "AKI": 11000,
        "VT": 6000, "CHB": 7500, "Severe Chest Infection": 6500,
        "Cardiogenic Shock": 13000, "CVA Bleed": 9500, "Infective Endocarditis": 10000
    }
    disease_inputs = {disease: st.checkbox(disease, value=False) for disease in diseases.keys()}
    
    gender_encoded = 0 if gender == "Male" else 1
    admission_encoded = 0 if admission_type == "General Ward" else 1
    disease_values = [1 if disease_inputs[d] else 0 for d in diseases.keys()]
    
    selected_diseases = {d: cost for d, cost in diseases.items() if disease_inputs[d]}
    disease_cost = sum(selected_diseases.values())
    
    input_dict = {"Age": age, "Gender_Female": gender_encoded, "Admission_Type_ICU": admission_encoded, "Length_of_Stay": los}
    for disease in diseases.keys():
        input_dict[disease] = 1 if disease_inputs[disease] else 0
    
    input_df = pd.DataFrame([input_dict]).reindex(columns=feature_names, fill_value=0)
    
    if st.button("Estimate Total Bill"):
        base_bill = model.predict(input_df)[0]
        stay_charge = los * 500
        admission_charge = 5000 if admission_type == "ICU" else 2000
        hospital_total = base_bill + stay_charge + admission_charge + disease_cost
        grand_total = hospital_total + st.session_state["pharmacy_total"]
        
        update_bill(patient_id, st.session_state["pharmacy_total"], hospital_total, grand_total)
        
        st.subheader("📌 Detailed Bill Breakdown")
        st.write(f"🏥 Base Charge: ₹{base_bill:,.2f}")
        st.write(f"📅 Stay Charge: ₹{stay_charge:,.2f}")
        st.write(f"🩺 Admission Charge: ₹{admission_charge:,.2f}")
        st.write(f"💊 Pharmacy Cost: ₹{st.session_state['pharmacy_total']:,.2f}")
        if selected_diseases:
            st.write("🦠 Disease-Specific Charges:")
            for disease, cost in selected_diseases.items():
                st.write(f"• {disease}: ₹{cost:,.2f}")
        st.success(f"💰 Grand Total: ₹{grand_total:,.2f}")

        # -------- Graphs --------
        st.subheader("📊 Cost Analysis")

        # Hospital Cost Breakdown (Bar Chart)
        fig, ax = plt.subplots()
        labels = ["Base Charge", "Stay Charge", "Admission Charge", "Disease Cost"]
        values = [base_bill, stay_charge, admission_charge, disease_cost]
        ax.bar(labels, values, color=['blue', 'red', 'green', 'purple'])
        ax.set_ylabel("Cost (₹)")
        ax.set_title("Hospital Cost Breakdown")
        st.pyplot(fig)

        # Grand Total Breakdown (Pie Chart)
        fig, ax = plt.subplots()
        total_labels = ["Pharmacy", "Hospital"]
        total_values = [st.session_state["pharmacy_total"], hospital_total]
        ax.pie(total_values, labels=total_labels, autopct="%1.1f%%", colors=["orange", "blue"], startangle=90)
        ax.set_title("Grand Total Cost Distribution")
        st.pyplot(fig)
        
        # Disease Cost Contribution (Pie Chart)
        if selected_diseases:
            fig, ax = plt.subplots()
            ax.pie(selected_diseases.values(), labels=selected_diseases.keys(), autopct="%1.1f%%", startangle=140)
            ax.set_title("Disease Contribution to Total Hospital Bill")
            st.pyplot(fig)

if st.session_state["page"] == "pharmacy":
    pharmacy_bill()
else:
    hospital_bill()

# Back Button
st.divider()
if st.button("🔙 Back to Dashboard"):
    st.switch_page("pages/staff_dashboard.py")