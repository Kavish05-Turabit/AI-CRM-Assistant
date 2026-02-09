import streamlit as st
from ai_core.agent import GeminiAssistant
from utils import chat_helpers as ch

st.title("AI Assistant")
st.set_page_config(layout="wide",page_title="AI CRM Assistant")


if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"],width="content"):
        st.markdown(message["content"])

if "agent" not in st.session_state:
    st.session_state["agent"] = GeminiAssistant(model="gemini")

if "current_chat_id" not in st.session_state:
    chat_id = ch.get_chat_session()
    st.session_state["current_chat_id"] = chat_id

llm = st.session_state.agent

if prompt := st.chat_input("Ask something..."):

    st.session_state.messages.append({"role": "user", "content": prompt})
    ch.send_message("user",prompt)
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("ai"):
        with st.spinner("Loading..."):
            ai_response = llm.send_message(prompt)
            st.markdown(ai_response)
            st.session_state.messages.append({"role": "ai", "content": ai_response})
            ch.send_message("ai",ai_response)


