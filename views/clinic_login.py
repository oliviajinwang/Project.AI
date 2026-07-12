import streamlit as st

from utils.db import create_clinician, verify_clinician

st.markdown("<div class='bg-section'>Clinic Access</div>", unsafe_allow_html=True)

tab_login, tab_register = st.tabs(["Log In", "Create Account"])

with tab_login:
    st.write("Log in with your clinician account to continue.")
    login_username = st.text_input("Username", key="login_username")
    login_password = st.text_input("Password", type="password", key="login_password")

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Log In", type="primary", width="stretch"):
            clinician = verify_clinician(login_username, login_password)
            if clinician:
                st.session_state.clinic_authenticated = True
                st.session_state.clinic_user = clinician["username"]
                st.session_state.clinic_display_name = clinician["display_name"]
                st.rerun()
            else:
                st.error("Invalid username or password.")
    with col2:
        if st.button("Back", width="stretch", key="login_back"):
            st.session_state.role = None
            st.rerun()

with tab_register:
    st.write("New clinicians can create an account here.")
    reg_username = st.text_input("Choose a username", key="reg_username")
    reg_display_name = st.text_input("Display name", key="reg_display_name")
    reg_password = st.text_input("Choose a password", type="password", key="reg_password")
    reg_password_confirm = st.text_input("Confirm password", type="password", key="reg_password_confirm")

    if st.button("Create Account", type="primary", key="reg_submit"):
        if not reg_username.strip() or not reg_password:
            st.error("Username and password are required.")
        elif len(reg_password) < 8:
            st.error("Password must be at least 8 characters.")
        elif reg_password != reg_password_confirm:
            st.error("Passwords don't match.")
        else:
            created = create_clinician(reg_username.strip(), reg_password, reg_display_name.strip())
            if created:
                st.success("Account created — you can now log in from the Log In tab.")
            else:
                st.error("That username is already taken.")
