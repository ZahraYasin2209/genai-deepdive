import streamlit as st

import constants


def render_nexa_brand_identity(icon_pixel_size: int = constants.LOGO_SIZE_SIDEBAR):
    branding_markup = f"""
    <div style='display: flex; align-items: center; gap: 12px; margin-bottom: 20px;'>
        <svg viewBox="0 0 24 24" width="{icon_pixel_size}" height="{icon_pixel_size}" xmlns="http://www.w3.org/2000/svg">
            <defs>
                <linearGradient id="brandGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                    <stop offset="0%" style="stop-color:#6366f1"/>
                    <stop offset="100%" style="stop-color:#06b6d4"/>
                </linearGradient>
            </defs>
            <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5" 
                  fill="none" stroke="url(#brandGradient)" stroke-width="2" 
                  stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
        <h4 style='margin: 0; color: var(--text-color); font-weight: 800;'>
            {constants.APP_NAME}
        </h4>
    </div>
    """
    st.markdown(branding_markup, unsafe_allow_html=True)


def render_welcome_interface():
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    st.markdown(
        f"""
        <div style='text-align: center;'>
            <h1 style='font-size: 3.8rem; background: -webkit-linear-gradient(45deg, #6366f1, #06b6d4); 
            -webkit-background-clip: text; -webkit-text-fill-color: transparent; font-weight: 900;'>
                Elevate with {constants.APP_NAME}
            </h1>
            <p style='color: var(--text-color); opacity: 0.8; font-size: 1.3rem;'>
                Advanced intelligence for the modern software engineer.
            </p>
        </div>
        """, 
        unsafe_allow_html=True
    )

    suggestion_items = constants.SUGGESTIONS
    interface_columns = st.columns(len(suggestion_items))

    for column_index, (suggestion_id, card_content) in enumerate(suggestion_items.items()):
        with interface_columns[column_index]:
            if st.button(card_content["label"], icon=card_content["icon"], use_container_width=True):
                st.session_state.suggestion_trigger = card_content["prompt"]
                st.rerun()


def render_active_chat_log():
    current_session_id = st.session_state.active_chat_id
    chat_sessions = st.session_state.chat_sessions

    if current_session_id in chat_sessions:
        for chat_entry in chat_sessions[current_session_id]["messages"]:
            with st.chat_message(chat_entry["role"]):
                st.markdown(chat_entry["content"])


VIEW_DISPATCHER = {
    "welcome": render_welcome_interface,
    "chat": render_active_chat_log
}
