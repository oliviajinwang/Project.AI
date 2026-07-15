import streamlit as st

from utils.hero_signal import render_brain_signal_hero
from utils.ui import icon, render_public_header, render_trust_indicators


st.markdown(
    """
    <style>
    /* ================================================================
       Landing-page styles. The interactive "Brain Health Signal" hero
       (canvas point-cloud brain + BRAINGUARD morph) lives in its own
       component -- see utils/hero_signal.py. Everything below the hero
       stays conventional modern-healthcare styling.
       ================================================================ */

    /* Full-page hero: break the component iframe out of the content column
       to span the whole viewport width, and size it so header + hero fill
       the first screen. The overlay below then pulls the tagline + CTA up
       onto the animation itself. */
    section.stMain { overflow-x:hidden; }
    .st-key-hero_block iframe {
        display:block;
        width:100vw !important;
        margin-left:calc(50% - 50vw);
        height:calc(100vh - 170px) !important;
        min-height:560px;
    }
    .st-key-hero_overlay { position:relative; z-index:5; margin-top:-215px; pointer-events:none; }
    .st-key-hero_overlay .stButton > button { pointer-events:auto; }

    /* Streamlit's own stMarkdownContainer p rule outranks a bare class
       selector, so match its specificity to keep the auto side margins. */
    div[data-testid="stMarkdownContainer"] p.hero-message { text-align:center; font-size:clamp(17px,1.7vw,19px); line-height:1.6; color:var(--ink-secondary); max-width:540px; margin:6px auto 0; padding:10px 20px; background:radial-gradient(ellipse closest-side, rgba(252,250,246,0.94) 60%, transparent 100%); }
    .hero-message strong { color:var(--ink-primary); font-weight:600; }

    /* Faint chrome + cyan glow on the single primary CTA -- the strongest
       Y2K interactive accent is spent here, not on every button. */
    .st-key-hero_cta { max-width:320px; margin:24px auto 0; }
    .st-key-hero_cta .stButton > button { box-shadow:0 0 0 1px var(--y2k-silver), 0 0 22px var(--y2k-cyan-glow), 0 4px 10px rgba(30,87,83,0.18); }
    .st-key-hero_cta .stButton > button:hover { box-shadow:0 0 0 1px var(--y2k-cyan), 0 0 30px var(--y2k-cyan-glow), 0 4px 10px rgba(30,87,83,0.18); }

    /* Thin chrome divider marking the end of the hero section. */
    .y2k-divider { position:relative; height:1px; margin:34px auto 30px; max-width:200px; background:linear-gradient(90deg, transparent, var(--y2k-silver-dark) 22%, var(--y2k-cyan) 50%, var(--y2k-silver-dark) 78%, transparent); }
    .y2k-divider::after { content:""; position:absolute; top:50%; left:50%; width:5px; height:5px; background:var(--y2k-cyan); border-radius:50%; transform:translate(-50%,-50%); box-shadow:0 0 6px var(--y2k-cyan-glow); }

    /* ---- Below-the-fold content: conventional, readable ---- */
    .bg-mission-grid { display:grid; grid-template-columns:1.6fr .9fr; gap:24px; align-items:start; }
    .bg-mission-note { border-left:3px solid var(--y2k-silver-dark); padding:18px 20px; background:#F3F8F6; border-radius:0 var(--radius-md) var(--radius-md) 0; color:var(--ink-secondary); font-size:16px; line-height:1.55; clip-path:polygon(0 0, 100% 0, 100% calc(100% - 14px), calc(100% - 14px) 100%, 0 100%); }
    .bg-mission-note strong { color:var(--ink-primary); }
    .landing-audience-icon { display:flex; align-items:center; justify-content:center; width:46px; height:46px; border-radius:14px; background:var(--brand-teal-soft); color:var(--brand); border:1px solid var(--y2k-silver); box-shadow:inset 0 0 0 1px rgba(255,255,255,.5); margin-bottom:16px; }

    @media (max-width: 768px) {
        .bg-mission-grid { grid-template-columns:1fr; }
        .st-key-hero_overlay { margin-top:-185px; }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


def _go_to_role_select() -> None:
    st.session_state.show_role_select = True


render_public_header()

with st.container(key="hero_block"):
    render_brain_signal_hero()
    # Overlaid on the hero's lower band via the negative-margin CSS above,
    # keeping the tagline and CTA inside the first screen.
    with st.container(key="hero_overlay"):
        st.markdown(
            "<p class='hero-message'><strong>Your brain health is shaped by more than "
            "genetics.</strong><br>Explore factors you may be able to influence.</p>",
            unsafe_allow_html=True,
            width="stretch",  # markdown otherwise shrink-wraps, leaving the text off-center
        )
        with st.container(key="hero_cta"):
            st.button(
                "Check my risk factors →",
                on_click=_go_to_role_select,
                type="primary",
                width="stretch",
            )

st.markdown("<div class='y2k-divider' aria-hidden='true'></div>", unsafe_allow_html=True)

render_trust_indicators()

st.markdown("<div class='bg-section'>What BrainGuard AI is for</div>", unsafe_allow_html=True)
st.markdown(
    "<div class='bg-mission-grid'><div><p>BrainGuard AI is an educational and clinical "
    "decision-support prototype that estimates dementia-related risk from lifestyle, "
    "cognitive, and structural factors. It explains which factors influenced each "
    "estimate so people and care teams can have more informed conversations.</p>"
    "<p>It is not a diagnosis, a medical device, or a substitute for professional "
    "medical evaluation.</p></div>"
    "<aside class='bg-mission-note'><strong>A supportive starting point</strong><br>"
    "Results describe patterns in a research-trained model. They do not predict an "
    "individual's future or replace a clinician's assessment.</aside></div>",
    unsafe_allow_html=True,
)

st.markdown("<div class='bg-section'>Designed for people and care teams</div>", unsafe_allow_html=True)
col1, col2, col3 = st.columns(3, gap="large")
for col, title, body, symbol in (
    (col1, "For individuals", "Understand lifestyle factors in straightforward language before your next appointment.", "brain"),
    (col2, "For families", "Prepare for a supportive conversation and keep questions focused on what matters most.", "family"),
    (col3, "For clinicians", "Review structured assessments and patient information in one focused workspace.", "clinic"),
):
    with col:
        with st.container(border=True, key=f"landing_{symbol}_card"):
            st.markdown(f"<div class='landing-audience-icon'>{icon(symbol, size=25)}</div>", unsafe_allow_html=True)
            st.subheader(title)
            st.write(body)

st.markdown("<div class='bg-section'>Important information</div>", unsafe_allow_html=True)
st.warning(
    "BrainGuard AI is an educational and clinical decision-support prototype. A lower-risk result does not rule out dementia, and a result needing attention does not mean a person has or will develop dementia. Always consult a qualified clinician about concerns with memory, thinking, or daily functioning."
)
