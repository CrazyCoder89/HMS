import streamlit as st
import sqlite3
import pickle
import numpy as np


# --- Load Trained Model ---
model_path = r"C:\Users\KRISH\.spyder-py3\HMS\models\CVRA2.pkl"
with open(model_path, "rb") as file:
    model = pickle.load(file)

# --- SQLite Connection Function ---
def get_db_connection():
    db_path = r"C:\Users\KRISH\.spyder-py3\HMS\hms_database.sqlite"
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row  # allows fetching rows as dict-like objects
    return conn

# --- Fetch Patient Data by Patient ID ---
def fetch_patient_data(patient_id):
    conn = get_db_connection()
    cursor = conn.cursor()

    query = """
    SELECT age, gender, smoking, diabetes, hypertension, CAD, HB, TLC, glucose, urea, creatinine, BNP, EF
    FROM patients
    WHERE patient_id = ?
    """
    cursor.execute(query, (patient_id,))
    result = cursor.fetchone()

    conn.close()

    if result:
        # Convert result to dict
        return dict(result)
    else:
        return None

# --- Streamlit UI ---
st.title("❤️ Cardiovascular Risk Analysis")

# --- Input Patient ID ---
patient_id = st.text_input("🔍 Enter Patient ID to Fetch Data")

if st.button("📥 Fetch Patient Data"):
    patient_data = fetch_patient_data(patient_id)

    if patient_data:
        st.success(f"✅ Data found for Patient ID: **{patient_id}**")

        # Pre-fill form with patient data (editable if needed)
        age = patient_data['age']
        gender = "Male" if patient_data['gender'] == 1 else "Female"
        smoking = "Yes" if patient_data['smoking'] == 1 else "No"
        diabetes = "Yes" if patient_data['diabetes'] == 1 else "No"
        hypertension = "Yes" if patient_data['hypertension'] == 1 else "No"
        cad = "Yes" if patient_data['CAD'] == 1 else "No"
        hb = patient_data['HB']
        tlc = patient_data['TLC']
        glucose = patient_data['glucose']
        urea = patient_data['urea']
        creatinine = patient_data['creatinine']
        bnp = patient_data['BNP']
        ef = patient_data['EF']

        # --- Editable Form (Optional) ---
        age = st.number_input("📅 Age", value=age, min_value=18, max_value=120, step=1)
        gender = st.selectbox("⚧️ Gender", ["Male", "Female"], index=0 if gender == "Male" else 1)
        smoking = st.selectbox("🚬 Smoking", ["Yes", "No"], index=0 if smoking == "Yes" else 1)
        diabetes = st.selectbox("💉 Diabetes (DM)", ["Yes", "No"], index=0 if diabetes == "Yes" else 1)
        hypertension = st.selectbox("💊 Hypertension (HTN)", ["Yes", "No"], index=0 if hypertension == "Yes" else 1)
        cad = st.selectbox("❤️ Coronary Artery Disease (CAD)", ["Yes", "No"], index=0 if cad == "Yes" else 1)

        hb = st.number_input("🩸 Hemoglobin (HB)", value=hb, min_value=5.0, max_value=20.0, step=0.1)
        tlc = st.number_input("🧬 Total Leukocyte Count (TLC)", value=tlc, min_value=2000, max_value=20000, step=100)
        glucose = st.number_input("🍬 Glucose", value=glucose, min_value=50, max_value=500, step=1)
        urea = st.number_input("💧 Urea", value=urea, min_value=5, max_value=200, step=1)
        creatinine = st.number_input("🩺 Creatinine", value=creatinine, min_value=0.1, max_value=10.0, step=0.1)
        bnp = st.number_input("💓 BNP", value=bnp, min_value=10, max_value=5000, step=10)
        ef = st.number_input("💥 Ejection Fraction (EF %)", value=ef, min_value=10, max_value=80, step=1)

        # --- Convert Inputs to Numeric (for model) ---
        gender = 1 if gender == "Male" else 0
        smoking = 1 if smoking == "Yes" else 0
        diabetes = 1 if diabetes == "Yes" else 0
        hypertension = 1 if hypertension == "Yes" else 0
        cad = 1 if cad == "Yes" else 0

        input_features = np.array([[age, gender, smoking, diabetes, hypertension, cad, hb, tlc, glucose, urea, creatinine, bnp, ef]])

        # --- Run Prediction ---
        if st.button("📊 Run Risk Analysis"):
            prediction = model.predict(input_features)[0]
            risk_level = "🔴 High Risk" if prediction == 1 else "🟢 Low Risk"

            st.subheader("🧬 Prediction Result")
            st.success(f"🏥 Cardiovascular Risk Level: **{risk_level}**")

    else:
        st.error(f"❌ No data found for Patient ID: **{patient_id}**")
