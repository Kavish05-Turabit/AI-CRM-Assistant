import requests
import streamlit as st

BASE_URL = "http://127.0.0.1:8000/chat"


def get_chat_session():
    """
    Create a new chat session everytime user logs in.
    All new chats belong to this session until logout.

    :return: Id of the current chat session
    """
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
    """
    Gives all sessions belonging to the current user.
    Fetches the current user using JWT token.

    :return: All sessions belonging to the current user.
    """
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


def get_chat_messages(chat_id: int):
    """
    Get all the messages for a given session using chat_id

    :param chat_id:
    :return: All messages belonging to chat ID
    """
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


def send_message(role: str, message: str, chat_id: int):
    """
    Send Message to API for the current Chat Session

    :param role:
    :param message:
    :param chat_id:
    """
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
