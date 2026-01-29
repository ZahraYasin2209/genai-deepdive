import streamlit as st

import components_renderer
import constants


def initialize_app_state():
    state_schema = {
        "chat_sessions": {},
        "active_chat_id": None,
        "suggestion_trigger": None
    }
    
    for app_state_key, initial_value in state_schema.items():
        if app_state_key not in st.session_state:
            st.session_state[app_state_key] = initial_value


def render_sidebar_navigation():
    chat_sessions = st.session_state.chat_sessions
    
    with st.sidebar:
        components_renderer.render_nexa_brand_identity(
            icon_pixel_size=constants.LOGO_SIZE_SIDEBAR
        )
        
        search_query = st.text_input(
            "Search", 
            placeholder="Search the Core...", 
            label_visibility="collapsed"
        )
        
        if st.button("New Chat", icon=":material/add_circle:", use_container_width=True):
            st.session_state.active_chat_id = None
            st.rerun()

        st.caption("Recents")

        ordered_ids = list(chat_sessions.keys())[::-1]

        filtered_ids = [
            search_id for search_id in ordered_ids 
            if search_query.lower() in chat_sessions[search_id]["title"].lower()
        ]

        for chat_id in filtered_ids:
            node_column, menu_column = st.columns(constants.SIDEBAR_COLUMN_RATIO)
            
            with node_column:
                if st.button(
                    chat_sessions[chat_id]["title"], 
                    key=f"nav_{chat_id}", 
                    use_container_width=True
                ):
                    st.session_state.active_chat_id = chat_id
                    st.rerun()
            
            with menu_column:
                with st.popover("", icon=":material/more_vert:"):
                    current_name = chat_sessions[chat_id]["title"]
                    new_name = st.text_input(
                        "Rename Node:", value=current_name, key=f"ren_{chat_id}"
                    )
                    
                    if new_name != current_name:
                        chat_sessions[chat_id]["title"] = new_name
                        st.rerun()
                    
                    if st.button(
                        "Delete Chat", 
                        icon=":material/delete:", 
                        key=f"del_{chat_id}", 
                        use_container_width=True
                    ):
                        st.session_state.chat_sessions.pop(chat_id, None)
                        if st.session_state.active_chat_id == chat_id:
                            st.session_state.active_chat_id = None
                        st.rerun()

        st.container(height=constants.SIDEBAR_SPACER_HEIGHT, border=False)
        st.write("---")
        st.button("Settings & Help", icon=":material/settings:", use_container_width=True)


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
