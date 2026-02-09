import requests
import streamlit as st


def get_chat_session():
    headers = st.session_state.headers
    try:
        response = requests.get(
            "http://127.0.0.1:8000/chat/",
            headers=headers
        )
        data = response.json()
        return data["new_id"]
    except Exception as e:
        st.error(e)


def send_message(role, message):
    chat_id = st.session_state.current_chat_id
    payload = {
        "sender_type": role,
        "chat_text": message,
        "chat_id": chat_id
    }
    headers = st.session_state.headers
    try:
        response = requests.post(
            "http://127.0.0.1:8000/chat/",
            headers=headers,
            json=payload
        )
    except Exception as e:
        st.error(e)
