import sqlite3

import streamlit as st

import components_renderer
import constants
from ai_neural_engine import get_vanguard_research_app


def initialize_app_state():
    state_schema = {
        "chat_sessions": {},
        "active_chat_id": None,
        "suggestion_trigger": None,
        "global_context": "Nexa AI",
    }

    for app_state_key, initial_value in state_schema.items():
        if app_state_key not in st.session_state:
            st.session_state[app_state_key] = initial_value


def get_active_view_key():
    active_id = st.session_state.active_chat_id
    sessions = st.session_state.chat_sessions
    view_key = "welcome"

    if active_id and sessions.get(active_id, {}).get("messages"):
        view_key = "chat"

    return view_key


def get_active_session_title():
    active_id = st.session_state.active_chat_id
    sessions = st.session_state.chat_sessions
    session_title = "New Chat"

    if active_id and active_id in sessions:
        session_title = sessions[active_id]["title"]

    return session_title


def render_sidebar_navigation():
    chat_sessions = st.session_state.chat_sessions

    with st.sidebar:
        components_renderer.render_nexa_brand_identity(
            icon_pixel_size=constants.LOGO_SIZE_SIDEBAR
        )

        search_query = st.text_input(
            "Search", placeholder=constants.SEARCH_PROMPT, label_visibility="collapsed"
        )

        if st.button(
            "New Chat", icon=":material/add_circle:", use_container_width=True
        ):
            st.session_state.active_chat_id = None
            st.rerun()

        st.caption("Recent Intelligence")

        ordered_ids = list(chat_sessions.keys())[::-1]
        filtered_ids = [
            search_id
            for search_id in ordered_ids
            if search_query.lower() in chat_sessions[search_id]["title"].lower()
        ]

        for search_id in filtered_ids:
            session_link_col, management_menu_col = st.columns(
                constants.SIDEBAR_COLUMN_RATIO
            )

            with session_link_col:
                session_title = chat_sessions[search_id]["title"]

                if st.button(
                    session_title, key=f"nav_{search_id}", use_container_width=True
                ):
                    st.session_state.active_chat_id = search_id
                    st.rerun()

            with management_menu_col:
                with st.popover("", icon=":material/more_vert:"):
                    updated_name = st.text_input(
                        "Rename Node:",
                        value=chat_sessions[search_id]["title"],
                        key=f"ren_{search_id}",
                    )

                    if updated_name != chat_sessions[search_id]["title"]:
                        chat_sessions[search_id]["title"] = updated_name
                        st.rerun()

                    if st.button(
                        "Delete", icon=":material/delete:", key=f"del_{search_id}"
                    ):
                        delete_session_permanently(search_id)


def sync_sidebar_with_db():
    try:
        vanguard_app_instance = get_vanguard_research_app()
        db_cursor = sqlite3.connect("vanguard_memory.db").cursor()

        db_cursor.execute("SELECT DISTINCT thread_id FROM checkpoints")
        persisted_thread_identifiers = [row[0] for row in db_cursor.fetchall()]
        sqlite3.connect("vanguard_memory.db").close()

        for current_thread_id in persisted_thread_identifiers:
            if current_thread_id in st.session_state.chat_sessions:
                continue

            runtime_configuration = {
                "configurable": {"thread_id": str(current_thread_id)}
            }
            persisted_graph_state = vanguard_app_instance.get_state(
                runtime_configuration
            )

            dynamic_session_title = f"Session: {current_thread_id[:8]}"
            processed_message_log = []

            for message_object in persisted_graph_state.values.get("messages", []):
                extracted_message_body = ""

                if isinstance(message_object.content, list):
                    fragments = []
                    for content_block in message_object.content:
                        if isinstance(content_block, dict):
                            if "text" in content_block:
                                fragments.append(content_block["text"])
                            else:
                                fragments.append(str(content_block))
                        else:
                            fragments.append(str(content_block))
                    extracted_message_body = "".join(fragments)

                else:
                    extracted_message_body = str(message_object.content)

                if extracted_message_body.strip():
                    assigned_role = (
                        constants.USER_ROLE
                        if message_object.type == "human"
                        else constants.ASSISTANT_ROLE
                    )
                    processed_message_log.append(
                        {
                            "role": assigned_role,
                            "content": extracted_message_body.strip(),
                        }
                    )

            if processed_message_log:
                user_initiated_messages = [
                    entry
                    for entry in processed_message_log
                    if entry["role"] == constants.USER_ROLE
                ]
                if user_initiated_messages:
                    dynamic_session_title = user_initiated_messages[0]["content"][:30]

            st.session_state.chat_sessions[current_thread_id] = {
                "title": dynamic_session_title,
                "messages": processed_message_log,
            }

    except Exception as error_context:
        print("Sidebar synchronization protocol failed:", error_context)


def delete_session_permanently(session_id):
    try:
        conn = sqlite3.connect("vanguard_memory.db")
        cursor = conn.cursor()

        params = (str(session_id),)

        tables = ["checkpoints", "writes", "checkpoint_writes", "checkpoint_blobs"]
        for db_table in tables:
            try:
                cursor.execute(f"DELETE FROM {db_table} WHERE thread_id = ?", params)
            except sqlite3.OperationalError:
                continue

        conn.commit()
        conn.close()

        if session_id in st.session_state.chat_sessions:
            del st.session_state.chat_sessions[session_id]

        if st.session_state.active_chat_id == session_id:
            st.session_state.active_chat_id = None

        st.toast(f"Intelligence Node {session_id[:8]} Purged", icon="🗑️")
        st.rerun()

    except Exception as e:
        st.error(f"Permanent Wipe Failed: {e}")
