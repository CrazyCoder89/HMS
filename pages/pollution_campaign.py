import streamlit as st
import pickle
import numpy as np
import pandas as pd

# Load the trained model
@st.cache_resource
def load_model():
    with open(r"C:\Users\KRISH\.spyder-py3\HMS\models\Pollution.pkl", "rb") as file:
        models = pickle.load(file)
    return models

models = load_model()

# Streamlit App UI
st.title("🏥 Health Campaign & Disease Prediction")
st.subheader("Enter Area Details & Environmental Data")

# Input Form in Center
with st.form("health_campaign_form"):
    area_name = st.text_input("🏙️ Area Name")
    city = st.text_input("🌆 City")
    state = st.text_input("🗺️ State")
    
    # Environmental Data Inputs
    pm2_5_avg = st.number_input("PM2.5 AVG", min_value=0.0, max_value=500.0, value=55.0)
    pm10_avg = st.number_input("PM10 AVG", min_value=0.0, max_value=600.0, value=80.0)
    no2_avg = st.number_input("NO2 AVG", min_value=0.0, max_value=200.0, value=40.0)
    nh3_avg = st.number_input("NH3 AVG", min_value=0.0, max_value=200.0, value=20.0)
    so2_avg = st.number_input("SO2 AVG", min_value=0.0, max_value=100.0, value=15.0)
    co_avg = st.number_input("CO AVG", min_value=0.0, max_value=10.0, value=1.0)
    ozone_avg = st.number_input("OZONE AVG", min_value=0.0, max_value=300.0, value=80.0)
    max_temp = st.number_input("Max Temperature (°C)", min_value=-10.0, max_value=50.0, value=35.0)
    min_temp = st.number_input("Min Temperature (°C)", min_value=-10.0, max_value=50.0, value=20.0)
    humidity = st.number_input("Humidity (%)", min_value=0.0, max_value=100.0, value=60.0)
    
    submit_button = st.form_submit_button("📌 Submit & Predict")

if submit_button:
    # Prepare input array for prediction
    input_features = np.array([[pm2_5_avg, pm10_avg, no2_avg, nh3_avg, so2_avg, co_avg, ozone_avg, max_temp, min_temp, humidity]])
    prediction = models.predict(input_features)[0]
    
    # Function to suggest diseases based on pollutants
    def suggest_diseases(pm10, no2, so2, co, ozone, temp, humidity):
        diseases = []
        if pm10 > 100:
            diseases.append("Respiratory issues (Asthma, COPD, Allergies)")
        if no2 > 40 or so2 > 20:
            diseases.append("Bronchitis, Eye Irritation, Lung Damage")
        if co > 2:
            diseases.append("Cardiovascular Disease, Headaches, Fatigue")
        if ozone > 100:
            diseases.append("Throat Irritation, Breathing Issues")
        if temp > 40:
            diseases.append("Heatstroke, Dehydration")
        if humidity > 80:
            diseases.append("Flu, Pneumonia, Bacterial Infections")
        return diseases if diseases else ["No significant health risks detected"]
    
    diseases = suggest_diseases(pm10_avg, no2_avg, so2_avg, co_avg, ozone_avg, max_temp, humidity)
    
    # Function to classify risk
    def classify_risk(predicted_value):
        if predicted_value > 300:
            return "High Risk"
        elif predicted_value > 150:
            return "Moderate Risk"
        else:
            return "Low Risk"
    
    risk_category = classify_risk(prediction)
    
    # Save campaign data (Optional: Can be stored in a database)
    campaign_data = {
        "Area": area_name,
        "City": city,
        "State": state,
        "PM2.5": pm2_5_avg,
        "PM10": pm10_avg,
        "NO2": no2_avg,
        "NH3": nh3_avg,
        "SO2": so2_avg,
        "CO": co_avg,
        "Ozone": ozone_avg,
        "Max Temp": max_temp,
        "Min Temp": min_temp,
        "Humidity": humidity,
        "Risk Category": risk_category,
        "Diseases": diseases
    }
    df = pd.DataFrame([campaign_data])
    df.to_csv("health_campaigns.csv", mode='a', index=False, header=False)
    
    # Display results
    st.subheader(f"🏥 Predicted Risk Category: {risk_category}")
    st.success(f"📊 Predicted AQI: {prediction}")
    st.warning("⚠️ Potential Diseases:")
    for disease in diseases:
        st.write(f"- {disease}")
    
    st.info("✅ Data has been saved for the health campaign.")

# Back Button
st.divider()
if st.button("🔙 Back to Dashboard"):
    st.switch_page("pages/staff_dashboard.py")
    
    
    