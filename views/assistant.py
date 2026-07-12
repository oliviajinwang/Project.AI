import streamlit as st

from utils.assistant import assistant_available, get_assistant_response
from utils.db import display_id, get_patient, resolve_patient_id_from_query
from utils.patient_conversation import (
    append_patient_exchange,
    get_patient_conversation,
    now_timestamp,
)

st.markdown("<div class='bg-section'>My AI Assistant</div>", unsafe_allow_html=True)
st.write(
    "Each registered patient has a personal AI conversation, saved automatically "
    "under their Patient ID and shared with the clinic record."
)
st.caption(
    "This assistant cannot diagnose anyone or give personal medical advice. "
    "Messages are stored in the selected patient record."
)

if not assistant_available():
    st.info(
        "Extended Q&A is not configured, but common questions about BrainGuard AI "
        "and general dementia risk factors will still work."
    )

st.session_state.setdefault("assistant_patient_id", None)
st.session_state.setdefault("assistant_messages", [])


def _load_patient_chat(patient_id: int) -> None:
    st.session_state.assistant_patient_id = int(patient_id)
    st.session_state.assistant_messages = [
        {
            "role": message["role"],
            "content": message["content"],
            "timestamp": message["timestamp"],
        }
        for message in get_patient_conversation(patient_id)
    ]


def _sign_out_patient_chat() -> None:
    st.session_state.assistant_patient_id = None
    st.session_state.assistant_messages = []


patient_id = st.session_state.get("assistant_patient_id")

if not patient_id:
    st.markdown("#### Continue as a registered patient")
    st.caption(
        "Enter the Patient ID shown during registration. Exact names are also "
        "accepted for this prototype."
    )

    sign_col, _ = st.columns([2, 1])
    with sign_col:
        identity = st.text_input(
            "Patient ID or exact full name",
            placeholder="e.g. P0006",
            key="assistant_sign_in_query",
        )

    if st.button("Open my AI conversation", type="primary"):
        resolved = resolve_patient_id_from_query(identity) if identity.strip() else None

        if resolved is None:
            st.error(
                "No registered patient matched that entry. Register first, then use "
                "the Patient ID shown after registration."
            )
        else:
            row = get_patient(resolved)
            if row is None:
                st.error("That patient record could not be loaded.")
            else:
                _load_patient_chat(resolved)
                st.success(
                    f"Signed in as {row['full_name']} ({display_id(resolved)})."
                )
                st.rerun()

    st.stop()

patient_row = get_patient(patient_id)
if patient_row is None:
    st.error("That patient record no longer exists. Please sign in again.")
    _sign_out_patient_chat()
    st.rerun()

patient_name = patient_row["full_name"]
patient_label = display_id(patient_id)

_load_patient_chat(patient_id)

header_left, header_right = st.columns([3, 1])
with header_left:
    st.markdown(f"### {patient_name}")
    st.caption(
        f"Patient ID {patient_label} · messages save automatically to this record"
    )

with header_right:
    if st.button("Switch patient", use_container_width=True):
        _sign_out_patient_chat()
        st.rerun()

if not st.session_state["assistant_messages"]:
    with st.chat_message("assistant"):
        st.write(
            "Hello! I can explain BrainGuard AI, its results, and general dementia "
            "risk factors. I cannot diagnose symptoms or give personal medical advice."
        )

for message in st.session_state["assistant_messages"]:
    role = message["role"]
    label = "You" if role == "user" else "BrainGuard AI"

    with st.chat_message(role):
        st.caption(f"{label} · {message.get('timestamp', '')}")
        st.write(message["content"])

user_message = st.chat_input(f"Message as {patient_name}…")

if user_message:
    user_timestamp = now_timestamp()
    history_for_model = list(st.session_state["assistant_messages"])

    with st.chat_message("user"):
        st.caption(f"You · {user_timestamp}")
        st.write(user_message)

    with st.chat_message("assistant"):
        with st.spinner("BrainGuard AI is responding…"):
            reply = get_assistant_response(user_message, history_for_model)
        assistant_timestamp = now_timestamp()
        st.caption(f"BrainGuard AI · {assistant_timestamp}")
        st.write(reply)

    saved_messages = append_patient_exchange(
        patient_id,
        user_message,
        reply,
        user_timestamp=user_timestamp,
        assistant_timestamp=assistant_timestamp,
    )

    st.session_state.assistant_messages = [
        {
            "role": message["role"],
            "content": message["content"],
            "timestamp": message["timestamp"],
        }
        for message in saved_messages
    ]

    st.rerun()