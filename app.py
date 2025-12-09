import streamlit as st
import requests
import uuid

# --- Configuration ---

API_URL = st.secrets["API_URL"]
API_KEY = st.secrets["API_KEY"]

# --- Page Setup ---
st.set_page_config(page_title="Doctors Appointment Bot", page_icon="🏥")
st.title("🏥 Appointment Booking Assistant")

# --- Session State (Memory) ---
# We generate a random Thread ID for this specific user session
# This ensures the Durable Agent remembers context for THIS user.
if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())

if "messages" not in st.session_state:
    st.session_state.messages = []

# --- Display Chat History (left = assistant, right = user) ---
# Simple bubble styles for user and assistant
bubble_style_user = (
    "background-color:#DCF8C6;padding:10px;border-radius:10px;max-width:70%;margin:5px;"
)
bubble_style_agent = (
    "background-color:#F1F0F0;padding:10px;border-radius:10px;max-width:70%;margin:5px;"
)

for message in st.session_state.messages:
    role = message.get("role", "assistant")
    content = message.get("content", "")
    if role == "user":
        _, right_col = st.columns([1, 3])
        with right_col:
            st.markdown(f'<div style="{bubble_style_user}">{content}</div>', unsafe_allow_html=True)
    else:
        left_col, _ = st.columns([3, 1])
        with left_col:
            st.markdown(f'<div style="{bubble_style_agent}">{content}</div>', unsafe_allow_html=True)

# --- Handle User Input ---
if prompt := st.chat_input("How can I help you today?"):
    # 1. Save user message to session state
    st.session_state.messages.append({"role": "user", "content": prompt})

    # Immediately render the user's message on the right
    _, right_col = st.columns([1, 3])
    with right_col:
        st.markdown(f'<div style="{bubble_style_user}">{prompt}</div>', unsafe_allow_html=True)

    # 2. Show assistant placeholder on the left while calling API
    left_col, _ = st.columns([3, 1])
    with left_col:
        message_placeholder = st.empty()
        message_placeholder.markdown(f'<div style="{bubble_style_agent}">Thinking...</div>', unsafe_allow_html=True)

    try:
        # We pass the key in the URL query parameter 'code'
        full_url = f"{API_URL}?code={API_KEY}&thread_id={st.session_state.thread_id}"

        response = requests.post(
            full_url,
            data=prompt,
            headers={"Content-Type": "text/plain"},
        )

        if response.status_code == 200:
            agent_reply = response.text
            # Update placeholder with assistant bubble
            with left_col:
                message_placeholder.markdown(f'<div style="{bubble_style_agent}">{agent_reply}</div>', unsafe_allow_html=True)
            st.session_state.messages.append({"role": "assistant", "content": agent_reply})
        else:
            error_msg = f"Error {response.status_code}: {response.text}"
            with left_col:
                message_placeholder.error(error_msg)

    except Exception as e:
        with left_col:
            message_placeholder.error(f"Connection Failed: {str(e)}")