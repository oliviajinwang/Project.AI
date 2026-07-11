import streamlit as st

from utils.assistant import assistant_available, get_assistant_response
from utils.db import display_id, get_patient, resolve_patient_id_from_query
from utils.patient_conversation import append_patient_exchange, get_patient_conversation, now_timestamp

st.markdown("<div class='bg-section'>Ask BrainGuard AI</div>", unsafe_allow_html=True)
st.write(
    "Ask about how this tool works, what a result means, or general dementia risk factors."
)
st.caption(
    "This assistant can't diagnose anyone or give personal medical advice — for anything "
    "about a real person's health, please talk to a physician."
)

if not assistant_available():
    st.info(
        "Extended Q&A isn't configured right now, but I can still answer common questions "
        "about this tool and general dementia risk factors below."
    )

st.session_state.setdefault("assistant_messages", [])
st.session_state.setdefault("assistant_patient_id", None)

with st.expander("Link this chat to a registered Patient ID (optional)", expanded=False):
    st.caption(
        "When linked, your conversation is saved to that patient's record so clinic staff "
        "can review it under Patient AI Conversation. Unlinked chats stay in this session only."
    )
    link_col, clear_col = st.columns([3, 1])
    with link_col:
        link_query = st.text_input(
            "Patient ID or full name",
            value=display_id(st.session_state.assistant_patient_id)
            if st.session_state.assistant_patient_id
            else "",
            placeholder="e.g. P0008 or Jane Doe",
            key="assistant_link_query",
        )
    with clear_col:
        st.write("")
        st.write("")
        if st.button("Unlink", use_container_width=True):
            st.session_state.assistant_patient_id = None
            st.session_state.assistant_messages = []
            st.rerun()

    if st.button("Link patient", type="primary"):
        resolved = resolve_patient_id_from_query(link_query) if link_query.strip() else None
        if resolved is None:
            st.error("No registered patient matched that ID or name.")
        else:
            st.session_state.assistant_patient_id = resolved
            # Load this patient's own history so the session never shows another patient's chat.
            st.session_state.assistant_messages = [
                {"role": m["role"], "content": m["content"], "timestamp": m["timestamp"]}
                for m in get_patient_conversation(resolved)
            ]
            st.success(f"Linked to {display_id(resolved)} — {get_patient(resolved)['full_name']}.")
            st.rerun()

linked_id = st.session_state.get("assistant_patient_id")
if linked_id:
    linked_row = get_patient(linked_id)
    linked_name = linked_row["full_name"] if linked_row else "Unknown"
    st.caption(f"Saving to patient record {display_id(linked_id)} ({linked_name}).")

for message in st.session_state["assistant_messages"]:
    with st.chat_message(message["role"]):
        if message.get("timestamp"):
            st.caption(message["timestamp"])
        st.write(message["content"])

user_message = st.chat_input("Ask a question...")
if user_message:
    user_ts = now_timestamp()
    st.session_state["assistant_messages"].append(
        {"role": "user", "content": user_message, "timestamp": user_ts}
    )
    with st.chat_message("user"):
        st.caption(user_ts)
        st.write(user_message)

    reply = get_assistant_response(user_message, st.session_state["assistant_messages"])
    assistant_ts = now_timestamp()
    st.session_state["assistant_messages"].append(
        {"role": "assistant", "content": reply, "timestamp": assistant_ts}
    )
    with st.chat_message("assistant"):
        st.caption(assistant_ts)
        st.write(reply)

    if linked_id:
        append_patient_exchange(
            linked_id,
            user_message,
            reply,
            user_timestamp=user_ts,
            assistant_timestamp=assistant_ts,
        )

if st.session_state["assistant_messages"]:
    if st.button("Clear conversation"):
        st.session_state["assistant_messages"] = []
        st.rerun()
