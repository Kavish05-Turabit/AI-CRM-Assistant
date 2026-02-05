import streamlit as st

import utils.helpers as hp

st.markdown('<p style="font-family:sans-serif; '
            'color:Purple; text-align:center; font-size: 62px;">'
            'AI CRM Assistant</p>', unsafe_allow_html=True)

st.title("Login to continue", text_alignment="center")

col1, col2, col3 = st.columns([2, 3, 2])

with col2:
    with st.form(key="Login Form"):
        email = st.text_input("Email", placeholder="Enter company email")
        password = st.text_input("Password", type="password", placeholder="Enter password")
        login = st.form_submit_button("Login")

    if login:
        if email.strip() == "":
            st.error("Please enter email")
            st.stop()
        if password.strip() == "":
            st.error("Please enter password")
            st.stop()

        hp.check_user_login(email,password)
