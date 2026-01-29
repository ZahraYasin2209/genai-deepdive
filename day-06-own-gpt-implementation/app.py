import os
import uuid

import streamlit as st
from dotenv import load_dotenv
from google import genai

import components_renderer
import constants
import session_manager


def main():
    st.set_page_config(
        page_title=constants.APP_NAME, 
        page_icon=constants.PAGE_ICON, 
        layout="wide"
    )
    load_dotenv()

    session_manager.initialize_app_state()
    session_manager.render_sidebar_navigation()
    
    ai_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    chat_sessions = st.session_state.chat_sessions

    header_title = session_manager.get_active_session_title()
    header_left, header_mid, _ = st.columns(constants.HEADER_COLUMN_RATIO)
    
    with header_left: 
        components_renderer.render_nexa_brand_identity(
            icon_pixel_size=constants.LOGO_SIZE_HEADER
        )
    with header_mid: 
        st.markdown(f"<h3 style='text-align: center;'>{header_title}</h3>", unsafe_allow_html=True)

    active_view_key = session_manager.get_active_view_key()
    components_renderer.VIEW_DISPATCHER[active_view_key]()

    user_input = st.chat_input(constants.CHAT_INPUT_TEXT)
    if st.session_state.suggestion_trigger:
        user_input = st.session_state.suggestion_trigger
        st.session_state.suggestion_trigger = None

    if user_input:
        active_id = st.session_state.active_chat_id
        if not active_id:
            active_id = str(uuid.uuid4())
            chat_sessions[active_id] = {"title": user_input[:30], "messages": []}
            st.session_state.active_chat_id = active_id
        
        chat_sessions[active_id]["messages"].append({
            "role": constants.USER_ROLE, 
            "content": user_input
        })
        st.rerun()

    active_id = st.session_state.active_chat_id
    if active_id and chat_sessions[active_id]["messages"]:
        active_messages = chat_sessions[active_id]["messages"]
        last_entry = active_messages[-1]
        
        if last_entry["role"] == constants.USER_ROLE:
            with st.chat_message(constants.ASSISTANT_ROLE):
                try:
                    response = ai_client.models.generate_content(
                        model=constants.MODEL_NAME, 
                        contents=last_entry["content"]
                    )
                    chat_sessions[active_id]["messages"].append({
                        "role": constants.ASSISTANT_ROLE, 
                        "content": response.text
                    })
                    st.rerun()
                except Exception:
                    st.error("Neural Quota exceeded. Please wait.")


if __name__ == "__main__":
    main()
