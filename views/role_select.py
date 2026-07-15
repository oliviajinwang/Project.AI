import streamlit as st

from utils.ui import icon, render_public_header


st.markdown(
    """
    <style>
    .st-key-role_selection { max-width:1120px; margin:0 auto; }
    .role-selection-intro { max-width:660px; margin:42px auto 28px; text-align:center; }
    .role-selection-intro h1 { font-size:clamp(32px,4vw,46px); letter-spacing:-.035em; margin:0 0 10px; }
    .role-selection-intro p { font-size:17px; color:var(--ink-secondary); line-height:1.55; }
    .st-key-role_self_card, .st-key-role_caregiver_card, .st-key-role_clinic_card { min-height:340px; display:flex; flex-direction:column; }
    .role-card-bottom { margin-top:auto; padding-top:18px; }
    .role-card-tag { display:inline-block; margin:0 0 12px; padding:5px 9px; border-radius:999px; background:#F3F0E9; color:var(--ink-secondary); font-size:12px; font-weight:700; }
    .st-key-role_back button { background:transparent; color:var(--brand) !important; border:0; box-shadow:none; min-height:36px; width:auto; padding:4px 0; }
    .st-key-role_back button p, .st-key-role_back button span { color:var(--brand) !important; }
    @media (max-width: 768px) { .role-selection-intro { margin-top:28px; } .st-key-role_self_card, .st-key-role_caregiver_card, .st-key-role_clinic_card { min-height:0; } }
    </style>
    """,
    unsafe_allow_html=True,
)


def _go_back() -> None:
    st.session_state.show_role_select = False


def _choose_patient(mode: str) -> None:
    # This display-only context does not alter patient data, forms, or scoring.
    st.session_state.patient_entry_mode = mode
    st.session_state.role = "patient"


def _choose_clinic() -> None:
    st.session_state.role = "clinic"


render_public_header()
with st.container(key="role_back"):
    st.button("Back", icon=":material/arrow_back:", on_click=_go_back, key="role_back_button")

with st.container(key="role_selection"):
    st.markdown(
        "<div class='role-selection-intro bg-enter'><h1>How can BrainGuard AI support you today?</h1><p>Choose the space that best fits your next step. You can always switch roles later.</p></div>",
        unsafe_allow_html=True,
    )
    self_col, caregiver_col, clinic_col = st.columns(3, gap="large")

    with self_col:
        with st.container(border=True, key="role_self_card"):
            st.markdown(f"<div class='role-card-icon'>{icon('brain', size=26)}</div>", unsafe_allow_html=True)
            st.markdown("<div class='role-card-kicker'>Personal check</div>", unsafe_allow_html=True)
            st.subheader("Checking for myself")
            st.markdown("<div class='role-card-copy'>Take a short, plain-language lifestyle risk check and see factors you may want to discuss at a routine appointment.</div>", unsafe_allow_html=True)
            st.markdown("<span class='role-card-tag'>No sign-in required</span>", unsafe_allow_html=True)
            with st.container(key="role_self_action"):
                if st.button("Start my risk check", type="primary", width="stretch", key="role_self_button"):
                    _choose_patient("self")
                    st.rerun()

    with caregiver_col:
        with st.container(border=True, key="role_caregiver_card"):
            st.markdown(f"<div class='role-card-icon caregiver'>{icon('family', size=26)}</div>", unsafe_allow_html=True)
            st.markdown("<div class='role-card-kicker'>Family support</div>", unsafe_allow_html=True)
            st.subheader("Helping a family member")
            st.markdown("<div class='role-card-copy'>Use the same guided check to prepare thoughtful questions and next steps for someone you care about.</div>", unsafe_allow_html=True)
            st.markdown("<span class='role-card-tag'>Plain-language guidance</span>", unsafe_allow_html=True)
            with st.container(key="role_caregiver_action"):
                if st.button("Help a family member", type="primary", width="stretch", key="role_caregiver_button"):
                    _choose_patient("caregiver")
                    st.rerun()

    with clinic_col:
        with st.container(border=True, key="role_clinic_card"):
            st.markdown(f"<div class='role-card-icon clinic'>{icon('clinic', size=26)}</div>", unsafe_allow_html=True)
            st.markdown("<div class='role-card-kicker'>Professional workspace</div>", unsafe_allow_html=True)
            st.subheader("Clinical staff")
            st.markdown("<div class='role-card-copy'>Sign in to review patient records, prioritize follow-up, and use decision-support assessment tools.</div>", unsafe_allow_html=True)
            st.markdown("<span class='role-card-tag'>Secure staff access</span>", unsafe_allow_html=True)
            with st.container(key="role_clinic_action"):
                if st.button("Go to clinical staff sign in", type="primary", width="stretch", key="role_clinic_button"):
                    _choose_clinic()
                    st.rerun()

st.caption("BrainGuard AI is a demonstration prototype. Do not enter real personal or protected health information (PHI).")
