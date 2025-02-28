import streamlit as st
import sqlite3
import pickle
import numpy as np

# Load ICU and Ward LOS models
@st.cache_resource
def load_model(file_path):
    with open(file_path, "rb") as file:
        return pickle.load(file)

icu_model = load_model(r"C:\Users\KRISH\.spyder-py3\HMS\models\random_forest_icu.pkl")  # ICU Model
ward_model = load_model(r"C:\Users\KRISH\.spyder-py3\HMS\models\xgboost_ward.pkl")  # Ward Model

# Database Connection
def get_patient_data(patient_id):
    conn = sqlite3.connect("database/hms_database.db")  
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM patients WHERE patient_id=?", (patient_id,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        return {
            "name": row[1], "age": row[2], "gender": row[3], "smoking": row[4], 
            "diabetes": row[5], "hypertension": row[6], "CAD": row[7], "admission_type": row[8],
            "HB": row[9], "TLC": row[10], "glucose": row[11], "urea": row[12], "creatinine": row[13], 
            "BNP": row[14], "EF": row[15]
        }
    return None

def save_patient_data(patient_id, additional_data):
    conn = sqlite3.connect("database/hms_database.db")  
    cursor = conn.cursor()
    
    cursor.execute(
        """UPDATE patients SET platelets=?, acs=?, hfref=?, stemi=?, chb=?, af=?, vt=?, uti=?, 
        cardiogenic_shock=?, shock=?, pulmonary_embolism=?, rural=? WHERE patient_id=?""",
        (
            additional_data["platelets"], additional_data["acs"], additional_data["hfref"], 
            additional_data["stemi"], additional_data["chb"], additional_data["af"], 
            additional_data["vt"], additional_data["uti"], additional_data["cardiogenic_shock"], 
            additional_data["shock"], additional_data["pulmonary_embolism"], additional_data["rural"],
            patient_id
        )
    )
    conn.commit()
    conn.close()

# Select ICU or Ward
st.title("🏥 Length of Stay (LOS) Prediction")

ward_type = st.selectbox("🏥 Select Patient Type:", ["ICU", "Ward"])
selected_model = icu_model if ward_type == "ICU" else ward_model

# Patient ID Input
patient_id = st.text_input("🔍 Enter Patient ID to Fetch Details")
patient_data = None

# Fetch Details Button
if st.button("Fetch Details"):
    patient_data = get_patient_data(patient_id)
    if patient_data:
        st.success(f"✅ Data Found for **{patient_data['name']}**")
    else:
        st.error("❌ Patient Not Found! Please enter details manually.")

# Take inputs (Either from database or manually)
st.header("📌 Enter Patient Details")

col1, col2, col3 = st.columns(3)

with col1:
    age = st.number_input("Age", min_value=0, max_value=120, value=patient_data["age"] if patient_data else 50)
    hb = st.number_input("HB", min_value=0.0, max_value=500.0, value=patient_data["HB"] if patient_data else 50.0)
    tlc = st.number_input("TLC", min_value=0.0, max_value=500.0, value=patient_data["TLC"] if patient_data else 50.0)

with col2:
    glucose = st.number_input("Glucose", min_value=0.0, max_value=1000.0, value=patient_data["glucose"] if patient_data else 50.0)
    urea = st.number_input("Urea", min_value=0.0, max_value=500.0, value=patient_data["urea"] if patient_data else 50.0)
    creatinine = st.number_input("Creatinine", min_value=0.0, max_value=10.0, value=patient_data["creatinine"] if patient_data else 1.0)

with col3:
    ef = st.number_input("EF", min_value=0.0, max_value=100.0, value=patient_data["EF"] if patient_data else 50.0)
    bnp = st.number_input("BNP", min_value=0.0, max_value=5000.0, value=patient_data["BNP"] if patient_data else 500.0)
    admission_type = st.radio("Type of Admission", ["Emergency", "OPD"], index=0 if patient_data and patient_data["admission_type"] == 1 else 1)

admission_type = 1 if admission_type == "Emergency" else 0
cad = st.radio("Coronary Artery Disease (CAD)?", ["Yes", "No"], index=0 if patient_data and patient_data["CAD"] == 1 else 1)
cad = 1 if cad == "Yes" else 0

# Additional Details
st.header("📌 Additional Patient Details")

col4, col5, col6 = st.columns(3)

with col4:
    platelets = st.number_input("Platelets", min_value=0.0, max_value=1000.0, value=100.0)
    rural = st.radio("Rural?", ["Yes", "No"])
    acs = st.radio("Acute Coronary Syndrome (ACS)?", ["Yes", "No"])

with col5:
    hfref = st.radio("Heart Failure (HFREF)?", ["Yes", "No"])
    stemi = st.radio("STEMI?", ["Yes", "No"])
    chb = st.radio("Complete Heart Block (CHB)", ["Yes", "No"])

with col6:
    af = st.radio("Atrial Fibrillation (AF)?", ["Yes", "No"])
    vt = st.radio("Ventricular Tachycardia (VT)?", ["Yes", "No"])
    uti = st.radio("Urinary Tract Infection (UTI)?", ["Yes", "No"])

cardiogenic_shock = st.radio("Cardiogenic Shock?", ["Yes", "No"])
shock = st.radio("Shock?", ["Yes", "No"])
pulmonary_embolism = st.radio("Pulmonary Embolism?", ["Yes", "No"])

# Convert categorical inputs to numerical
rural = 1 if rural == "Yes" else 0
acs = 1 if acs == "Yes" else 0
hfref = 1 if hfref == "Yes" else 0
stemi = 1 if stemi == "Yes" else 0
chb = 1 if chb == "Yes" else 0
af = 1 if af == "Yes" else 0
vt = 1 if vt == "Yes" else 0
uti = 1 if uti == "Yes" else 0
cardiogenic_shock = 1 if cardiogenic_shock == "Yes" else 0
shock = 1 if shock == "Yes" else 0
pulmonary_embolism = 1 if pulmonary_embolism == "Yes" else 0

# Convert input to NumPy array
input_features = np.array([
    hb, tlc, platelets, glucose, urea, creatinine, ef, bnp,
    age, rural, admission_type, cad, acs, hfref, stemi, chb, af, vt, uti, 
    cardiogenic_shock, shock, pulmonary_embolism
]).reshape(1, -1)

# Predict button
if st.button("Predict LOS"):
    prediction = selected_model.predict(input_features)[0]
    st.success(f"🛏️ Predicted Length of Stay: {prediction:.2f} days")

# Back Button
st.divider()
if st.button("🔙 Back to Dashboard"):
    st.switch_page("pages/doctor_dashboard.py")
    