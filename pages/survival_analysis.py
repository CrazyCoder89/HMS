import streamlit as st
import sqlite3
import pandas as pd
import pickle
from sklearn.ensemble import RandomForestClassifier

# Load the trained Random Forest model
rf_model = pickle.load(open(r"C:\Users\KRISH\.spyder-py3\HMS\models\survival2.pkl", 'rb'))  # Replace with correct path

# Function to fetch patient details from the database
def get_patient_details(patient_id):
    conn = sqlite3.connect("database/hms_database.db")
    c = conn.cursor()
    c.execute("""
        SELECT age, gender, admission_type, smoking, hypertension, diabetes, CAD
        FROM patients WHERE patient_id=?
    """, (patient_id,))
    result = c.fetchone()
    conn.close()
    return result if result else None

# Streamlit UI
st.markdown("""
    <style>
        .stButton>button {
            background-color: #4CAF50;
            color: white;
            border-radius: 10px;
            font-size: 16px;
            padding: 10px;
        }
        .high-survival {
            background-color: #DFF2BF;
            padding: 15px;
            border-radius: 10px;
            font-size: 20px;
            text-align: center;
            font-weight: bold;
            color: #4F8A10;
            border: 2px solid #4F8A10;
        }
        .low-survival {
            background-color: #FFBABA;
            padding: 15px;
            border-radius: 10px;
            font-size: 20px;
            text-align: center;
            font-weight: bold;
            color: #D8000C;
            border: 2px solid #D8000C;
        }
    </style>
""", unsafe_allow_html=True)

st.title("🏥 Survival Model Analysis")
st.subheader("🔍 Predict Survival Risk")

# Input Patient ID
tab1, tab2 = st.tabs(["📋 Patient Lookup", "🔢 Manual Entry"])

with tab1:
    patient_id = st.text_input("Enter Patient ID:")
    if st.button("🔍 Fetch Data"):
        patient_data = get_patient_details(patient_id)
        if patient_data:
            age, gender, admission_type, smoking, hypertension, diabetes, CAD = patient_data
            st.success("✅ Patient data retrieved!")
        else:
            st.error("❌ No patient found with this ID!")
            patient_data = None

with tab2:
    age = st.number_input("🧑 Age", value=0)
    gender = st.radio("⚤ Gender", [0, 1], format_func=lambda x: "Male" if x == 1 else "Female")
    type_of_admission = st.selectbox("🏥 Type of Admission", [0, 1], format_func=lambda x: "Emergency" if x == 0 else "OPD")
    smoking = st.selectbox("🚬 Smoking", [0, 1], format_func=lambda x: "Yes" if x == 1 else "No")
    htn = st.selectbox("❤️ Hypertension", [0, 1], format_func=lambda x: "Yes" if x == 1 else "No")
    dm = st.selectbox("🩸 Diabetes", [0, 1], format_func=lambda x: "Yes" if x == 1 else "No")
    cad = st.selectbox("🫀 CAD", [0, 1], format_func=lambda x: "Yes" if x == 1 else "No")

# Additional inputs
alcohol = st.selectbox("🍺 Alcohol", [0, 1], format_func=lambda x: "Yes" if x == 1 else "No")
prior_cmp = st.selectbox("🔄 Prior CMP", [0, 1], format_func=lambda x: "Yes" if x == 1 else "No")
ckd = st.selectbox("🩺 CKD", [0, 1], format_func=lambda x: "Yes" if x == 1 else "No")
heart_failure = st.selectbox("💔 Heart Failure", [0, 1], format_func=lambda x: "Yes" if x == 1 else "No")
hfref = st.selectbox("🔍 HFREF", [0, 1], format_func=lambda x: "Yes" if x == 1 else "No")
hfnef = st.selectbox("⚕️ HFNEF", [0, 1], format_func=lambda x: "Yes" if x == 1 else "No")

# Button to make prediction
if st.button("🩺 Predict Survival"):
    input_data = pd.DataFrame({
        'age': [age], 'gender': [gender], 'type_of_admission': [type_of_admission], 'smoking': [smoking],
        'alcohol': [alcohol], 'htn': [htn], 'dm': [dm], 'cad': [cad], 'prior_cmp': [prior_cmp],
        'ckd': [ckd], 'heart_failure': [heart_failure], 'hfref': [hfref], 'hfnef': [hfnef]
    })
    prediction = rf_model.predict(input_data)
    
    # Convert class to readable survival status
    survival_status = "High ✅" if prediction[0] == 1 else "Low ❌"
    survival_class = "high-survival" if prediction[0] == 1 else "low-survival"

    # Display result in a stylish way
    st.markdown(f"""
        <div class="{survival_class}">
            🩺 <strong>Chances of Survival:</strong> {survival_status}
        </div>
    """, unsafe_allow_html=True)

# Back Button
st.divider()
if st.button("🔙 Back to Dashboard"):
    st.switch_page("pages/doctor_dashboard.py")
    
    