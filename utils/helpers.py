import requests
import streamlit as st


def check_user_login(email: str, password: str):
    payload = {
        "username": email,
        "password": password
    }
    try:
        response = requests.post("http://127.0.0.1:8000/login/", data=payload)
        if response.status_code == 200:
            data = response.json()
            st.session_state["access_token"] = data["access_token"]
            st.session_state["current_emp"] = data["emp_id"]
            st.session_state["current_emp_name"] = data["emp_name"]
            st.session_state["access_level"] = data["access"]
            st.session_state["headers"] = {"Authorization": f"Bearer {data['access_token']}"}
            st.rerun()
        else:
            try:
                error_details = response.json().get("detail", "Unknown Error")
            except Exception as e:
                error_details = "Internal Server Error"
            st.error(f"❌ {error_details}")
    except requests.exceptions.ConnectionError as e:
        st.error(f"❌ Connection failed. Server might be Down!")
    except requests.exceptions.Timeout:
        st.error(f"❌ Too many requests. Server timed out!")
    except Exception as e:
        st.error(f"❌ Error! -> {e.__repr__()}")
