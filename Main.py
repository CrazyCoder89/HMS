import streamlit as st

# Initialize session state variables
if "logged_in" not in st.session_state:
    st.session_state["logged_in"] = False
if "username" not in st.session_state:
    st.session_state["username"] = None
if "role" not in st.session_state:
    st.session_state["role"] = None
    
    
def main():
    st.set_page_config(page_title="Hospital Management System", layout="wide")
    
    st.title("🏥 Sanjeevni-Your Trusted Partner in Patient Care")
    st.write("Sanjeevni provides high-quality healthcare services.")

    st.subheader("Key Features:")
    st.markdown("- 📊 Dashboard for hospital insights")
    st.markdown("- ⏳ Predict length of stay")
    st.markdown("- ❤️ Cardiovascular risk analysis")
    st.markdown("- 🌍 Pollution-based health campaigns")
    st.markdown("- 💰 Pharmacy billing management")
    st.markdown("- 🛏️ Bed availability tracking")
    st.markdown("- 👨‍⚕️ Doctor-patient management")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Login to Account"):
            st.switch_page("pages/login.py")  # ✅ Redirect to Login Page

    with col2:
        if st.button("Signup"):
            st.switch_page("pages/signup.py")  # ✅ Redirect to Signup Page

if __name__ == "__main__":
    main()
