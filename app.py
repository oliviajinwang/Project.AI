import streamlit as st

from utils.db import init_db
from utils.layout import inject_css

st.set_page_config(
    page_title="BrainGuard AI",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded",
)

init_db()
inject_css()

st.session_state.setdefault("role", None)
st.session_state.setdefault("clinic_authenticated", False)

if st.session_state.role is None:
    nav = st.navigation([st.Page("views/role_select.py", title="Welcome")], position="hidden")
    nav.run()

elif st.session_state.role == "patient":
    st.sidebar.markdown("### 🧑 Patient Portal")
    st.sidebar.markdown("---")

    pages = [
        st.Page("views/patient_check.py", title="Quick Risk Check", icon="🧑", default=True),
        st.Page("views/register_patient.py", title="Register Patient", icon="🧑‍🤝‍🧑"),
        st.Page("views/dementia_check.py", title="Dementia Check", icon="🧠"),
        st.Page("views/medical_report.py", title="Medical Report", icon="📄"),
    ]
    nav = st.navigation(pages)

    st.sidebar.markdown("---")
    if st.sidebar.button("🔁 Switch Role"):
        st.session_state.role = None
        st.rerun()

    nav.run()

elif st.session_state.role == "clinic":
    if not st.session_state.clinic_authenticated:
        nav = st.navigation([st.Page("views/clinic_login.py", title="Clinic Login")], position="hidden")
        nav.run()
    else:
        st.sidebar.markdown("### 🩺 Clinic Portal")
        st.sidebar.markdown("---")

        pages = [
            st.Page("views/dashboard.py", title="Dashboard", icon="🏠", default=True),
            st.Page("views/history.py", title="Patient History", icon="📜"),
            st.Page("views/about.py", title="About", icon="ℹ️"),
        ]
        nav = st.navigation(pages)

        st.sidebar.markdown("---")
        if st.sidebar.button("🔁 Log Out / Switch Role"):
            st.session_state.role = None
            st.session_state.clinic_authenticated = False
            st.rerun()

        nav.run()
