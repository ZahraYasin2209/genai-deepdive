import uuid

from dotenv import load_dotenv

load_dotenv()

import streamlit as st

import ai_neural_engine
import components_renderer
import constants
import session_manager


def main():
    st.set_page_config(
        page_title=constants.APP_NAME, page_icon=constants.PAGE_ICON, layout="wide"
    )

    session_manager.initialize_app_state()

    if "sidebar_synced" not in st.session_state:
        session_manager.sync_sidebar_with_db()
        st.session_state.sidebar_synced = True

        # Render the navigation
    # session_manager.render_sidebar_navigation()
    # components_renderer.render_settings_sidebar()

    session_manager.render_sidebar_navigation()

    # 4. LOAD HISTORY: If a session is active but empty in RAM, pull from DB
    active_id = st.session_state.active_chat_id
    if active_id and active_id in st.session_state.chat_sessions:
        if not st.session_state.chat_sessions[active_id]["messages"]:
            # Load from DB into UI memory
            st.session_state.chat_sessions[active_id]["messages"] = (
                ai_neural_engine.load_session_history(active_id)
            )

    header_title = session_manager.get_active_session_title()
    _, header_mid, _ = st.columns(constants.HEADER_COLUMN_RATIO)

    with header_mid:
        st.markdown(
            f"<h3 style='text-align: center;'>{header_title}</h3>",
            unsafe_allow_html=True,
        )

    active_view_key = session_manager.get_active_view_key()
    components_renderer.VIEW_DISPATCHER[active_view_key]()

    user_payload = st.chat_input(
        constants.USER_INPUT_TEXT, accept_file=True, accept_audio=True
    )

    user_input = st.session_state.suggestion_trigger or (
        user_payload.text if user_payload else None
    )

    if st.session_state.suggestion_trigger:
        st.session_state.suggestion_trigger = None

    if user_input or (user_payload and (user_payload.files or user_payload.audio)):
        extracted_image_buffers = (
            [
                file_artifact
                for file_artifact in user_payload.files
                if "image" in file_artifact.type
            ]
            if user_payload
            else None
        )

        neural_payload = ai_neural_engine.format_multimodal_content(
            user_input,
            extracted_image_buffers,
            user_payload.audio if user_payload else None,
        )

        active_id = st.session_state.active_chat_id or str(uuid.uuid4())

        if active_id not in st.session_state.chat_sessions:
            display_name = user_input if isinstance(user_input, str) else "New Research"
            if not display_name and user_payload.text:
                display_name = user_payload.text[:30]

            st.session_state.chat_sessions[active_id] = {
                "title": display_name,
                "messages": [],
            }
            st.session_state.active_chat_id = active_id

        # FIX: Append the full neural_payload, not just the raw user_input
        st.session_state.chat_sessions[active_id]["messages"].append(
            {"role": constants.USER_ROLE, "content": neural_payload}
        )
        st.rerun()

    current_active_session_id = st.session_state.active_chat_id

    if (
        current_active_session_id
        and st.session_state.chat_sessions[current_active_session_id]["messages"]
    ):
        conversational_history_log = st.session_state.chat_sessions[
            current_active_session_id
        ]["messages"]
        if conversational_history_log[-1]["role"] == constants.USER_ROLE:
            if ai_neural_engine.execute_neural_processing(
                message_log=conversational_history_log,
                active_session_id=current_active_session_id,
            ):
                st.rerun()


if __name__ == "__main__":
    main()
