import streamlit as st
import sqlite3

# Initialize session state variables
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "username" not in st.session_state:
    st.session_state["username"] = None
if "role" not in st.session_state:
    st.session_state["role"] = None

def check_login(username, password):
    """Check login credentials from SQLite database"""
    conn = sqlite3.connect("database/hms_database.db")
    c = conn.cursor()
    c.execute("SELECT role FROM users WHERE username=? AND password=?", (username, password))
    result = c.fetchone()
    conn.close()
    return result[0] if result else None  # Return role (Doctor or Staff)

def show_login():
    """Display login form"""
    st.title("🔑 Login to HMS")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        role = check_login(username, password)
        if role:
            st.session_state["logged_in"] = True
            st.session_state["username"] = username
            st.session_state["role"] = role
            st.success(f"✅ Welcome, {username}! Role: {role}")

            # ✅ Navigate based on role
            if role == "Staff":
                st.switch_page("pages/staff_dashboard.py")  
            elif role == "Doctor":
                st.switch_page("pages/doctor_dashboard.py")  
        else:
            st.error("❌ Invalid username or password")

if __name__ == "__main__":
    show_login()
