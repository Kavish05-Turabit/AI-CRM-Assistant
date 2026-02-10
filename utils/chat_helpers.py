import requests
import streamlit as st

BASE_URL = "http://127.0.0.1:8000/chat"


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


def get_user_chats():
    headers = st.session_state.get("headers", {})
    try:
        response = requests.get(
            f"{BASE_URL}/sessions",
            headers=headers
        )
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        st.error(e)
    return []


def get_chat_messages(chat_id):
    headers = st.session_state.get("headers", {})
    try:
        response = requests.get(
            f"{BASE_URL}/messages/{chat_id}",
            headers=headers
        )
        if response.status_code == 200:
            return response.json()
    except Exception as e:
        st.error(e)
    return []


def send_message(role, message, chat_id):
    payload = {
        "sender_type": role,
        "chat_text": message,
        "chat_id": chat_id
    }
    headers = st.session_state.get("headers", {})
    try:
        requests.post(
            f"{BASE_URL}",
            headers=headers,
            json=payload
        )
    except Exception as e:
        st.error(e)
