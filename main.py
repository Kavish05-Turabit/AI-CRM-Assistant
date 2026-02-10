import streamlit as st

st.set_page_config(layout="wide",page_title="AI CRM Assistant")

# Define the Pages needed for this application.
login_page = st.Page("views/login_view.py",title="Login",icon=":material/login:")
chat_page = st.Page("views/chat_view.py",title="AI Assistant",icon=":material/chat:")

# Redirect to login page if access token is missing else show the chat page.
if "access_token" not in st.session_state:
    pages = st.navigation([login_page])
else:
    pages = st.navigation([chat_page])

pages.run()


