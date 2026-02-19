import streamlit as st
import requests
import uuid

API = "http://localhost:8000/chat"

st.set_page_config(page_title="Gold Loan Agent")
st.title("💰 Gold Loan Agent")


# RESPONSE NORMALIZER
def normalize_response(response):
    if isinstance(response, list):
        texts = []
        for item in response:
            if isinstance(item, dict) and "text" in item:
                texts.append(item["text"])
        return "\n".join(texts)

    if isinstance(response, str):
        return response

    return None


# SESSION INIT
if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())

if "history" not in st.session_state:
    st.session_state.history = []

if "started" not in st.session_state:
    st.session_state.started = False

if "pending_message" not in st.session_state:
    st.session_state.pending_message = None

thread_id = st.session_state.thread_id


# AUTO START
if not st.session_state.started:
    try:
        with st.spinner("Starting assistant..."):
            r = requests.post(
                API,
                json={"thread_id": thread_id},
                timeout=30
            )

        if r.status_code != 200:
            st.error("❌ Backend error. Check FastAPI logs.")
            st.stop()

        data = r.json()
        reply = normalize_response(data.get("response"))

        if not reply:
            reply = "Hello! 👋 Let’s get started with your loan application. Please tell me your full name."

        st.session_state.history.append(("assistant", reply))
        st.session_state.started = True
        st.rerun()

    except Exception as e:
        st.error(f"❌ Failed to start conversation: {e}")
        st.stop()


# RENDER CHAT
for role, msg in st.session_state.history:
    st.chat_message(role).write(msg)


# USER INPUT
user_input = st.chat_input("Type here...")

if user_input:
    st.session_state.pending_message = user_input
    st.session_state.history.append(("user", user_input))
    st.rerun()


# SEND TO BACKEND (FIXED)
if st.session_state.pending_message:
    try:
        with st.spinner("Checking..."):
            r = requests.post(
                API,
                json={
                    "thread_id": thread_id,
                    "message": st.session_state.pending_message  # ✅ FIX
                },
                timeout=30
            )

        if r.status_code != 200:
            reply = "❌ Backend error. Please try again."
        else:
            reply = normalize_response(r.json().get("response"))

        if not reply:
            reply = "❌ No response from assistant."

    except Exception as e:
        reply = f"❌ Server error: {e}"

    st.session_state.history.append(("assistant", reply))
    st.session_state.pending_message = None
    st.rerun()
