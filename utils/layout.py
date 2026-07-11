import streamlit as st

_CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Fraunces:ital,opsz,wght@0,9..144,400;0,9..144,500;0,9..144,600;1,9..144,500&family=JetBrains+Mono:wght@500;600&display=swap');

:root {
    --brand: #1C3D5A;
    --brand-hover: #142B40;
    --brand-blue: #4A7BA6;
    --brand-blue-hover: #3A6488;
    --brand-yellow: #B8892B;
    --bg-page: #F5F7FA;
    --bg-card: #FFFFFF;
    --bg-muted: #EDF1F5;
    --border: rgba(20, 40, 65, 0.12);
    --shadow-sm: 0 1px 2px rgba(20, 40, 65, 0.06);
    --shadow-md: 0 8px 24px rgba(20, 40, 65, 0.14);
    --ink-primary: #13203A;
    --ink-secondary: #445068;
    --ink-muted: #7A879C;
    --good: #1E7A4C;
    --critical: #B33A3A;
    --radius-lg: 16px;
    --radius-md: 10px;
    --radius-sm: 999px;
    --font-serif: 'Fraunces', Georgia, serif;
    --font-mono: 'JetBrains Mono', 'Courier New', monospace;
}

#MainMenu { visibility: hidden; }
footer { visibility: hidden; }

.stApp {
    background: var(--bg-page);
    color: var(--ink-primary);
}

.stApp, .stApp p, .stApp span, .stApp label,
.stApp li, .stApp div[data-testid="stMarkdownContainer"] {
    color: var(--ink-primary);
}

.stApp h1, .stApp h2, .stApp h3, .stApp h4, .stApp h5, .stApp h6 {
    color: var(--ink-primary);
    font-family: var(--font-serif);
}

.block-container {
    padding-top: 2.5rem;
    padding-left: 3rem;
    padding-right: 3rem;
    padding-bottom: 2rem;
    max-width: 1200px;
}

/* Sidebar */
section[data-testid="stSidebar"] {
    background: var(--bg-card);
    border-right: 1px solid var(--border);
}
section[data-testid="stSidebar"] * {
    color: var(--ink-primary);
}

/* Typography */
.bg-title {
    text-align: left;
    font-family: var(--font-serif);
    font-size: 34px;
    font-weight: 600;
    letter-spacing: -0.01em;
    color: var(--ink-primary);
    padding-bottom: 8px;
    border-bottom: 1px solid var(--border);
    margin-bottom: 4px;
}

.bg-subtitle {
    text-align: left;
    font-size: 15px;
    color: var(--ink-secondary);
    margin-bottom: 8px;
}

.bg-section {
    font-family: var(--font-serif);
    font-size: 23px;
    font-weight: 600;
    color: var(--ink-primary);
    margin-top: 20px;
    margin-bottom: 10px;
    padding-bottom: 8px;
    border-bottom: 1px solid var(--border);
}

.bg-footer {
    text-align: center;
    font-size: 13px;
    color: var(--ink-muted);
    margin-top: 40px;
}

.bg-footer h3 {
    font-family: var(--font-serif);
    font-size: 17px;
    font-weight: 600;
    color: var(--brand);
}

/* Buttons -- pill-shaped, matching the reference's rounded CTAs */
.stButton > button,
.stDownloadButton > button,
.stFormSubmitButton > button {
    width: 100%;
    height: 44px;
    border-radius: var(--radius-sm);
    font-weight: 600;
    background: var(--brand);
    color: white;
    border: none;
    transition: background 0.15s ease;
}

.stButton > button:hover,
.stDownloadButton > button:hover,
.stFormSubmitButton > button:hover {
    background: var(--brand-hover);
    color: white;
}

.stButton > button p, .stButton > button span, .stButton > button div,
.stDownloadButton > button p, .stDownloadButton > button span, .stDownloadButton > button div,
.stFormSubmitButton > button p, .stFormSubmitButton > button span, .stFormSubmitButton > button div {
    color: white !important;
}

.stButton > button:focus-visible {
    outline: 2px solid var(--brand);
    outline-offset: 2px;
}

/* Bordered containers (st.container(border=True)) read as cards */
div[data-testid="stVerticalBlockBorderWrapper"] {
    background: var(--bg-card);
    border-radius: var(--radius-lg) !important;
    border-color: var(--border) !important;
    box-shadow: var(--shadow-sm);
}

/* Metrics as stat cards */
div[data-testid="stMetric"] {
    background: var(--bg-card);
    border: 1px solid var(--border);
    border-radius: var(--radius-md);
    padding: 14px 16px;
    box-shadow: var(--shadow-sm);
}
div[data-testid="stMetricLabel"], div[data-testid="stMetricLabel"] * {
    color: var(--ink-muted) !important;
    font-family: var(--font-mono);
    font-weight: 600;
    text-transform: uppercase;
    font-size: 11px;
    letter-spacing: 0.04em;
}
div[data-testid="stMetricValue"], div[data-testid="stMetricValue"] * {
    color: var(--ink-primary) !important;
    font-weight: 700;
}

/* Tabs */
.stTabs [data-baseweb="tab"] {
    font-weight: 600;
    color: var(--ink-secondary);
}
.stTabs [aria-selected="true"] {
    color: var(--brand) !important;
}
.stTabs [data-baseweb="tab-highlight"] {
    background-color: var(--brand) !important;
}

/* Dataframes */
div[data-testid="stDataFrame"] {
    border: 1px solid var(--border);
    border-radius: var(--radius-md);
    overflow: hidden;
}

/* Status badge (risk labels) */
.risk-badge {
    display: inline-block;
    padding: 4px 12px;
    border-radius: 999px;
    font-family: var(--font-mono);
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.05em;
    text-transform: uppercase;
    color: white !important;
}

/* Starting-screen role cards: white outline buttons for max contrast
   against the card, instead of a filled button blending into the page */
.st-key-patient_cta button, .st-key-clinic_cta button {
    background: white;
    border: 1.5px solid var(--brand);
}
.st-key-patient_cta button p, .st-key-patient_cta button span, .st-key-patient_cta button div,
.st-key-clinic_cta button p, .st-key-clinic_cta button span, .st-key-clinic_cta button div {
    color: var(--brand) !important;
}
.st-key-patient_cta button:hover, .st-key-clinic_cta button:hover {
    background: var(--brand);
}
.st-key-patient_cta button:hover p, .st-key-patient_cta button:hover span, .st-key-patient_cta button:hover div,
.st-key-clinic_cta button:hover p, .st-key-clinic_cta button:hover span, .st-key-clinic_cta button:hover div {
    color: white !important;
}

.accent-bar {
    display: block;
    height: 3px;
    width: 40px;
    border-radius: 999px;
    margin-bottom: 12px;
}
.accent-bar-blue { background: var(--brand-blue); }
.accent-bar-violet { background: var(--brand); }

.tag {
    display: inline-block;
    padding: 4px 12px;
    border-radius: 999px;
    font-family: var(--font-mono);
    font-size: 11px;
    font-weight: 600;
    letter-spacing: 0.03em;
    margin: 4px 0 8px 0;
}
.tag-yellow {
    background: rgba(184, 137, 43, 0.14);
    color: var(--brand-yellow);
}

hr {
    border-color: var(--border);
}

/* Switch Role / Log Out: a floating pill in the bottom-right corner of
   the main content area instead of the sidebar, positioned so it never
   overlaps the Dashboard's charts (fixed, small footprint, corner only). */
.st-key-switch_role_btn {
    position: fixed;
    bottom: 24px;
    right: 32px;
    z-index: 9999;
    width: auto !important;
}
.st-key-switch_role_btn button {
    width: auto !important;
    height: auto !important;
    padding: 10px 22px !important;
    border-radius: 999px !important;
    box-shadow: var(--shadow-md);
}

/* Full-viewport opaque cover shown for one render pass while switching
   roles, so stale dashboard/portal content can never peek through while
   the browser prunes it. */
.st-key-switching_overlay {
    position: fixed;
    inset: 0;
    z-index: 999999;
    background: var(--bg-page);
    display: flex;
    align-items: center;
    justify-content: center;
}
.st-key-switching_overlay div[data-testid="stMarkdownContainer"] {
    display: flex;
    justify-content: center;
    width: 100%;
}
.st-key-switching_overlay p {
    font-size: 18px;
    font-weight: 600;
    color: var(--ink-secondary);
    text-align: center;
}
</style>
"""


_HIDE_SIDEBAR_CSS = """
<style>
section[data-testid="stSidebar"] { display: none !important; }
</style>
"""


def inject_css() -> None:
    st.markdown(_CSS, unsafe_allow_html=True)


def hide_sidebar() -> None:
    # st.navigation(..., position="hidden") only hides the nav *links* --
    # Streamlit still allocates the sidebar's own container (white
    # background + collapse arrow), which showed up as a persistent empty
    # white block next to the Welcome/About/login screens. Call this only
    # once app.py has finished resolving st.session_state.role for the
    # current run (it must NOT be folded into inject_css(), which has to
    # stay early -- before the switch-role overlay renders -- or the
    # overlay's own CSS, defined in the same stylesheet, wouldn't be
    # loaded yet and it would render unstyled).
    st.markdown(_HIDE_SIDEBAR_CSS, unsafe_allow_html=True)


def render_footer() -> None:
    st.markdown(
        """
        <div class='bg-footer'>
        <hr>
        <h3>BrainGuard AI</h3>
        <p>Explainable AI Dementia Risk Assessment &amp; Patient Management System</p>
        <p>This tool supports clinical judgment; it is not a diagnosis.</p>
        </div>
        """,
        unsafe_allow_html=True,
    )
