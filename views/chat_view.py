import streamlit as st
from ai_core.agent import GeminiAssistant
from utils import chat_helpers as ch

st.set_page_config(layout="wide", page_title="AI CRM Assistant")
st.title("AI Assistant")

# initialize agent for this chat session
if "agent" not in st.session_state:
    st.session_state["agent"] = GeminiAssistant()

MODEL_OPTIONS = {
    "Gemini": ["gemini-2.5-flash", "gemini-2.5-flash-lite", "gemini-3-flash"],
    "Groq": ["llama-3.3-70b-versatile", "qwen/qwen3-32b"]
}

# Fetch the new chat ID created for this session and mark it active
if "live_chat_id" not in st.session_state:
    new_id = ch.get_chat_session()
    st.session_state["live_chat_id"] = new_id
    st.session_state["active_view_id"] = new_id

if "messages" not in st.session_state:
    st.session_state.messages = []

if "loaded_chat_id" not in st.session_state:
    st.session_state["loaded_chat_id"] = None

live_id = st.session_state["live_chat_id"]
active_id = st.session_state["active_view_id"]

with st.sidebar:
    st.title(st.session_state.current_emp_name)
    st.title("Chats")

    is_live = (active_id == live_id)
    btn_type = "primary" if is_live else "secondary"

    if st.button("Current Chat", use_container_width=True, type=btn_type):
        st.session_state["active_view_id"] = live_id
        st.rerun()

    with st.popover("Configure", icon=":material/settings:",width="stretch"):
        st.write("Configuration")
        selected_provider = st.selectbox(
            "AI Provider",
            options=["Gemini", "Groq"],
            index=0,
            key="temp_provider_selection"
        )
        selected_model = st.selectbox(
            "Model",
            options=MODEL_OPTIONS[selected_provider],
            index=0,
            key="temp_model_selection",
        )
        api_key_input = st.text_input(
            "API Key",
            type="password",
            placeholder=f"Enter {selected_provider} Key",
            key="temp_api_key"
        )
        if st.button("Save"):
            st.session_state.agent.config_model(
                selected_model,
                provider=selected_provider,
                api_key=api_key_input
            )

    st.divider()

    sessions = ch.get_user_chats()
    sessions.sort(key=lambda x: x['chat_id'], reverse=True)

    for session in sessions:
        s_id = session['chat_id']

        if s_id == live_id:
            continue

        msgs = ch.get_chat_messages(s_id)
        if len(msgs) < 2:
            continue

        s_title = session['init_time'] or f"Chat {s_id}"
        b_type = "primary" if active_id == s_id else "secondary"

        if st.button(s_title, key=s_id, use_container_width=True, type=b_type):
            st.session_state["active_view_id"] = s_id
            st.rerun()

# Add messages for the current chat to session state
if st.session_state["loaded_chat_id"] != active_id:
    raw_msgs = ch.get_chat_messages(active_id)
    st.session_state.messages = []
    for m in raw_msgs:
        role = "user" if m['sender_type'] == "user" else "ai"
        st.session_state.messages.append({"role": role, "content": m['chat_text']})

    st.session_state["loaded_chat_id"] = active_id

# Display all messages for this chat session
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# Show the prompt input bar only if user is currently in active session
if active_id == live_id:
    llm = st.session_state.agent
    if prompt := st.chat_input("Ask something..."):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        ch.send_message("user", prompt, active_id)

        with st.chat_message("ai"):
            with st.spinner("Loading..."):
                ai_response = llm.send_message(prompt)
                if ai_response:
                    st.markdown(ai_response)

                    st.session_state.messages.append({"role": "ai", "content": ai_response})
                    ch.send_message("ai", ai_response, active_id)
else:
    st.info("This is a past conversation. Chat is disabled.")
