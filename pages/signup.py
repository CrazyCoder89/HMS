import streamlit as st
import sqlite3

# Initialize session state variables
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "username" not in st.session_state:
    st.session_state["username"] = None
if "role" not in st.session_state:
    st.session_state["role"] = None
    
def create_users_table():
    conn = sqlite3.connect("database/hms_database.db")
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users 
                 (id INTEGER PRIMARY KEY, username TEXT UNIQUE, password TEXT, role TEXT)''')
    conn.commit()
    conn.close()

def check_username_exists(username):
    """Check if a username already exists in the database."""
    conn = sqlite3.connect("database/hms_database.db")
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE username=?", (username,))
    user = c.fetchone()
    conn.close()
    return user is not None  # Returns True if user exists

def add_user(username, password, role):
    """Add a new user if the username is not already taken."""
    if check_username_exists(username):
        st.error("⚠️ Username already exists. Please choose a different one.")
        return
    
    conn = sqlite3.connect("database/hms_database.db")
    c = conn.cursor()
    c.execute("INSERT INTO users (username, password, role) VALUES (?, ?, ?)", (username, password, role))
    conn.commit()
    conn.close()
    
    st.success("✅ Account created successfully! You can now login.")
    st.switch_page("pages/login.py")  # Redirect to Login Page

def show_signup():
    st.title("📝 Sign Up for HMS")

    create_users_table()  # Ensure the table exists

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    confirm_password = st.text_input("Confirm Password", type="password")

    role = st.selectbox("Select Role", ["Doctor", "Staff"])  # No "Admin" for security reasons

    if st.button("Sign Up"):
        if not username or not password or not confirm_password:
            st.error("⚠️ Please fill in all fields.")
        elif password != confirm_password:
            st.error("⚠️ Passwords do not match!")
        else:
            add_user(username, password, role)

if __name__ == "__main__":
    show_signup()
