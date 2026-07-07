import streamlit as st

_CSS = """
<style>
#MainMenu { visibility: hidden; }
footer { visibility: hidden; }

.stApp {
    background: #F5F3FA;
}

.block-container {
    padding-top: 2rem;
    padding-left: 3rem;
    padding-right: 3rem;
    padding-bottom: 2rem;
}

.bg-title {
    text-align: center;
    font-size: 48px;
    font-weight: bold;
    color: #4B3F72;
}

.bg-subtitle {
    text-align: center;
    font-size: 20px;
    color: #666666;
}

.bg-section {
    font-size: 26px;
    font-weight: bold;
    color: #4B3F72;
    margin-top: 20px;
    margin-bottom: 10px;
}

.bg-footer {
    text-align: center;
    font-size: 14px;
    color: gray;
    margin-top: 40px;
}

.stButton > button {
    width: 100%;
    height: 46px;
    border-radius: 10px;
    font-weight: bold;
    background: #4B3F72;
    color: white;
    border: none;
}

.stButton > button:hover {
    background: #6A4C93;
    color: white;
}
</style>
"""


def inject_css() -> None:
    st.markdown(_CSS, unsafe_allow_html=True)


def render_footer() -> None:
    st.markdown(
        """
        <div class='bg-footer'>
        <hr>
        <h3 style="color:#4B3F72;">🧠 BrainGuard AI</h3>
        <p>Explainable AI Dementia Risk Assessment &amp; Patient Management System</p>
        <p style="color:gray;">This tool supports clinical judgment; it is not a diagnosis.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
