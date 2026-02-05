import streamlit as st
from ai_core.setup import GeminiAssistant

st.title("AI CRM Assistant")
st.set_page_config(layout="centered",page_title="AI CRM Assistant")


if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

llm = GeminiAssistant(api_key="AIzaSyDt0hh5ZaaaTTG6S9yhlyxBi0phrti-xSM")

if prompt := st.chat_input("Ask something..."):

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    ai_response = llm.send_message(prompt)

    st.session_state.messages.append({"role": "ai", "content": ai_response})
    with st.chat_message("ai"):
        st.markdown(ai_response)


