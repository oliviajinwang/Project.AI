import streamlit as st

st.markdown(
    """
    <style>
    .hero-wrap {
        min-height: 82vh;
        display: flex;
        flex-direction: column;
        align-items: center;
        justify-content: center;
        text-align: center;
    }
    .hero-title {
        font-size: 76px;
        font-weight: 800;
        letter-spacing: -0.02em;
        color: #000000;
        line-height: 1.05;
        margin-bottom: 16px;
    }
    .hero-subtitle {
        font-size: 20px;
        color: #3D3D42;
        max-width: 640px;
    }
    .scroll-hint {
        margin-top: 48px;
        font-size: 13px;
        font-weight: 600;
        letter-spacing: 0.03em;
        text-transform: uppercase;
        color: #63636B;
        animation: bounce 2s ease-in-out infinite;
    }
    @keyframes bounce {
        0%, 100% { transform: translateY(0); opacity: 0.6; }
        50% { transform: translateY(10px); opacity: 1; }
    }

    @keyframes fadeInUp {
        from { opacity: 0; transform: translateY(56px); }
        to { opacity: 1; transform: translateY(0); }
    }

    /* Scroll-driven reveal for the two role cards. Falls back to a plain
       fade-in on load for browsers without animation-timeline support
       (Firefox / older Safari) so the cards are never stuck invisible. */
    .st-key-patient_card, .st-key-clinic_card {
        opacity: 0;
        animation: fadeInUp 0.9s cubic-bezier(0.16, 1, 0.3, 1) both;
        animation-timeline: view();
        animation-range: entry 0% cover 40%;
    }
    .st-key-clinic_card { animation-delay: 0.12s; }

    @supports not (animation-timeline: view()) {
        .st-key-patient_card, .st-key-clinic_card {
            opacity: 1;
            animation: fadeInUp 0.7s ease-out both;
        }
        .st-key-patient_card { animation-delay: 0.1s; }
        .st-key-clinic_card { animation-delay: 0.25s; }
    }
    </style>

    <div class="hero-wrap">
        <div class="hero-title">BrainGuard AI</div>
        <div class="hero-subtitle">AI-Powered Dementia Risk Assessment &amp; Patient Management System</div>
        <div class="scroll-hint">Scroll down to continue &#8595;</div>
    </div>
    """,
    unsafe_allow_html=True,
)

st.write("Please select how you'd like to continue:")
st.write("")

col1, col2 = st.columns(2)
with col1:
    with st.container(border=True, key="patient_card"):
        st.markdown("<span class='accent-bar accent-bar-blue'></span>", unsafe_allow_html=True)
        st.subheader("Patient")
        st.markdown("<span class='tag tag-yellow'>No sign-in required</span>", unsafe_allow_html=True)
        st.write("Check your own modifiable dementia risk factors.")
        if st.button("Continue as Patient", type="primary", width="stretch", key="patient_cta"):
            st.session_state.role = "patient"
            st.rerun()

with col2:
    with st.container(border=True, key="clinic_card"):
        st.markdown("<span class='accent-bar accent-bar-violet'></span>", unsafe_allow_html=True)
        st.subheader("Clinic Staff")
        st.markdown("<span class='tag tag-yellow'>Full diagnostics</span>", unsafe_allow_html=True)
        st.write("Access the full patient management and diagnostics dashboard.")
        if st.button("Continue as Clinic Staff", type="primary", width="stretch", key="clinic_cta"):
            st.session_state.role = "clinic"
            st.rerun()
