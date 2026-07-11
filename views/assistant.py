import streamlit as st

from utils.assistant import assistant_available, get_assistant_response

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

for message in st.session_state["assistant_messages"]:
    with st.chat_message(message["role"]):
        st.write(message["content"])

user_message = st.chat_input("Ask a question...")
if user_message:
    st.session_state["assistant_messages"].append({"role": "user", "content": user_message})
    with st.chat_message("user"):
        st.write(user_message)

    reply = get_assistant_response(user_message, st.session_state["assistant_messages"])
    st.session_state["assistant_messages"].append({"role": "assistant", "content": reply})
    with st.chat_message("assistant"):
        st.write(reply)

if st.session_state["assistant_messages"]:
    if st.button("Clear conversation"):
        st.session_state["assistant_messages"] = []
        st.rerun()
