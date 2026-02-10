import streamlit as st


def render_retrieval_control_panel():
    st.sidebar.title("RAG Configurations")
    active_retrieval_strategy = st.sidebar.selectbox(
        "Select Retrieval Strategy:",
        ["VectorStoreRetriever", "MultiQueryRetriever", "ParentDocumentRetriever"]
    )
    st.sidebar.info(f"**Active Mode:** {active_retrieval_strategy}")

    return active_retrieval_strategy
