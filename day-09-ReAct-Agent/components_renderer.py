import constants
import streamlit as st


def render_nexa_brand_identity(icon_pixel_size: int = constants.LOGO_SIZE_SIDEBAR):
    branding_markup = f"""
    <div style='display: flex; align-items: center; gap: 12px; margin-bottom: 20px;'>
        <svg viewBox="0 0 24 24" width="{icon_pixel_size}" height="{icon_pixel_size}" xmlns="http://www.w3.org/2000/svg">
            <path d="M12 2L2 7l10 5 10-5-10-5zM2 17l10 5 10-5M2 12l10 5 10-5"
                  fill="none" stroke="#6366f1" stroke-width="2"
                  stroke-linecap="round" stroke-linejoin="round"/>
        </svg>
        <h4 style='margin: 0; font-weight: 800;'>{constants.APP_NAME}</h4>
    </div>
    """
    st.markdown(branding_markup, unsafe_allow_html=True)


def render_settings_sidebar():
    with st.sidebar:
        st.divider()
        with st.expander("⚙️ System Settings", expanded=False):
            st.selectbox(
                "Model Version",
                [constants.MODEL_NAME, "gemini-2.0-flash"],
                key="selected_model_version",
            )

            if st.button("Clear Session Cache", use_container_width=True):
                st.session_state.active_chat_id = None
                st.session_state.suggestion_trigger = None
                st.toast("UI Cache Cleared", icon="🧹")
                st.rerun()

            if st.button(
                "Delete All History", type="secondary", use_container_width=True
            ):
                st.session_state.chat_sessions = {}
                st.session_state.active_chat_id = None
                st.rerun()


def render_welcome_interface():
    st.markdown("<br><br><br>", unsafe_allow_html=True)
    st.markdown(
        f"<h1 style='text-align: center; color: #5d87e6; font-size: 3.8rem; font-weight: 900;'>"
        f"Elevate with {constants.APP_NAME}</h1>",
        unsafe_allow_html=True,
    )

    suggestion_items = constants.SUGGESTIONS
    interface_columns = st.columns(len(suggestion_items))
    for column_index, (suggestion_id, card_content) in enumerate(
        suggestion_items.items()
    ):
        with interface_columns[column_index]:
            if st.button(
                card_content["label"],
                icon=card_content["icon"],
                use_container_width=True,
            ):
                st.session_state.suggestion_trigger = card_content["prompt"]
                st.rerun()


def render_multimodal_item(content_segment: dict):
    FORMAT_TO_COMPONENT_MAP = {
        "text": lambda content: st.markdown(content["text"]),
        "image_url": lambda content: st.image(content["image_url"]["url"]),
        "media": lambda content: st.audio(
            f"data:{content['mime_type']};base64,{content['data']}"
        ),
    }

    selected_rendering_protocol = FORMAT_TO_COMPONENT_MAP.get(
        content_segment.get("type"),
        lambda content: st.error("Unrecognized Media Format"),
    )

    return selected_rendering_protocol(content_segment)


def render_active_chat_log():
    current_session_id = st.session_state.active_chat_id

    for chat_msg in st.session_state.chat_sessions[current_session_id]["messages"]:
        chatbot_avatar = (
            constants.BOT_AVATAR
            if chat_msg["role"] == constants.ASSISTANT_ROLE
            else None
        )

        with st.chat_message(chat_msg["role"], avatar=chatbot_avatar):
            message_content = chat_msg["content"]

            if isinstance(message_content, list):
                [
                    render_multimodal_item(content_segment)
                    for content_segment in message_content
                ]
            else:
                st.markdown(message_content)

    return True


VIEW_DISPATCHER = {"welcome": render_welcome_interface, "chat": render_active_chat_log}
