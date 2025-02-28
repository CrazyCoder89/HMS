import streamlit as st
import sqlite3
from datetime import datetime

# Initialize session state
if "allow_los" not in st.session_state:
    st.session_state["allow_los"] = False
if "ward_type" not in st.session_state:
    st.session_state["ward_type"] = ""

# Initialize Database
def init_db():
    conn = sqlite3.connect("database/hms_database.db")
    c = conn.cursor()
    
    # Table to store bed availability
    c.execute("""
        CREATE TABLE IF NOT EXISTS hospital_beds (
            ward_type TEXT PRIMARY KEY,
            total_beds INTEGER,
            occupied_beds INTEGER,
            available_beds INTEGER
        )
    """)
    
    # Table to track patient bed assignments
    c.execute("""
        CREATE TABLE IF NOT EXISTS patient_beds (
            patient_id TEXT PRIMARY KEY,
            ward_type TEXT,
            bed_assigned INTEGER,
            assigned_at TIMESTAMP
        )
    """)
    
    # Initialize bed data (if not exists)
    c.execute("SELECT COUNT(*) FROM hospital_beds")
    if c.fetchone()[0] == 0:
        c.executemany("""
            INSERT INTO hospital_beds (ward_type, total_beds, occupied_beds, available_beds) 
            VALUES (?, ?, ?, ?)
        """, [
            ("ICU", 50, 46, 4),
            ("Ward", 100, 85, 15)
        ])
    
    conn.commit()
    conn.close()

init_db()

# Fetch Current Bed Status
def fetch_bed_status():
    conn = sqlite3.connect("database/hms_database.db")
    c = conn.cursor()
    c.execute("SELECT * FROM hospital_beds")
    data = {row[0]: {"Total Beds": row[1], "Occupied Beds": row[2], "Available Beds": row[3]} for row in c.fetchall()}
    conn.close()
    return data

# Assign a Bed to a Patient
def assign_bed(patient_id, ward_type):
    conn = sqlite3.connect("database/hms_database.db")
    c = conn.cursor()

    # Check if patient already has a bed
    c.execute("SELECT * FROM patient_beds WHERE patient_id = ?", (patient_id,))
    existing_patient = c.fetchone()

    if existing_patient:
        conn.close()
        return False, "❌ Patient already has a bed assigned!"

    # Check bed availability
    c.execute("SELECT available_beds FROM hospital_beds WHERE ward_type = ?", (ward_type,))
    available_beds = c.fetchone()[0]

    if available_beds > 0:
        # Assign bed
        c.execute("INSERT INTO patient_beds (patient_id, ward_type, bed_assigned, assigned_at) VALUES (?, ?, ?, ?)",
                  (patient_id, ward_type, 1, datetime.now()))

        # Update bed count
        c.execute("""
            UPDATE hospital_beds 
            SET occupied_beds = occupied_beds + 1, available_beds = available_beds - 1 
            WHERE ward_type = ?
        """, (ward_type,))
        
        conn.commit()
        conn.close()
        return True, f"✅ Bed assigned to patient {patient_id} in {ward_type}."
    else:
        conn.close()
        return False, f"❌ No available beds in {ward_type}."

# Revoke a Bed Assignment
def revoke_bed(patient_id):
    conn = sqlite3.connect("database/hms_database.db")
    c = conn.cursor()

    # Check if patient has a bed assigned
    c.execute("SELECT ward_type FROM patient_beds WHERE patient_id = ?", (patient_id,))
    result = c.fetchone()

    if not result:
        conn.close()
        return False, "❌ No bed found for this patient."

    ward_type = result[0]

    # Remove bed assignment
    c.execute("DELETE FROM patient_beds WHERE patient_id = ?", (patient_id,))

    # Update bed count
    c.execute("""
        UPDATE hospital_beds 
        SET occupied_beds = occupied_beds - 1, available_beds = available_beds + 1 
        WHERE ward_type = ?
    """, (ward_type,))

    conn.commit()
    conn.close()
    return True, f"✅ Bed revoked for patient {patient_id}."

# Streamlit UI
st.title("🏥 Hospital Bed Management")

# Display Bed Availability
st.write("### Current Bed Status")
hospital_data = fetch_bed_status()
st.json(hospital_data)

# User Inputs
patient_id = st.text_input("Enter Patient ID:")
ward_type = st.selectbox("Select Ward Type:", ["ICU", "Ward"])

# Assign Bed Button
if st.button("Assign Bed"):
    if not patient_id.strip():
        st.warning("⚠ Please enter a valid Patient ID.")
    else:
        success, message = assign_bed(patient_id.strip(), ward_type)
        st.write(message)
        st.rerun()

# Revoke Bed Button
if st.button("Revoke Bed"):
    if not patient_id.strip():
        st.warning("⚠ Please enter a valid Patient ID.")
    else:
        success, message = revoke_bed(patient_id.strip())
        st.write(message)
        st.rerun()

# Back Button
st.divider()
if st.button("🔙 Back to Dashboard"):
    st.switch_page("pages/staff_dashboard.py")
