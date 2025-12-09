import streamlit as st
import requests
import uuid

# --- Configuration ---

API_URL = st.secrets["API_URL"]
API_KEY = st.secrets["API_KEY"]

# --- Page Setup ---
st.set_page_config(page_title="Dr. Smith's Appointment Bot", page_icon="🏥")
st.title("🏥 Appointment Booking Assistant")

# --- Session State (Memory) ---
# We generate a random Thread ID for this specific user session
# This ensures the Durable Agent remembers context for THIS user.
if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())

if "messages" not in st.session_state:
    st.session_state.messages = []

# --- Display Chat History ---
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# --- Handle User Input ---
if prompt := st.chat_input("How can I help you today?"):
    # 1. Show User Message
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # 2. Call Azure Function (The Agent)
    with st.chat_message("assistant"):
        message_placeholder = st.empty()
        message_placeholder.markdown("Thinking...")

        try:
            # We pass the key in the URL query parameter 'code'
            full_url = f"{API_URL}?code={API_KEY}&thread_id={st.session_state.thread_id}"
            
            response = requests.post(
                full_url,
                data=prompt, 
                headers={"Content-Type": "text/plain"}
            )
            
            if response.status_code == 200:
                agent_reply = response.text
                message_placeholder.markdown(agent_reply)
                st.session_state.messages.append({"role": "assistant", "content": agent_reply})
            else:
                error_msg = f"Error {response.status_code}: {response.text}"
                message_placeholder.error(error_msg)
        
        except Exception as e:
            message_placeholder.error(f"Connection Failed: {str(e)}")