import streamlit as st
from chatbot_branding_config import APP_CONTENT, inject_custom_styles
from rag_knowledge_engine import ArchiveIntelligence
from ui_components_renderer import display_response_card, display_source_fragment

from constants import PAGE_TITLE


st.set_page_config(page_title=PAGE_TITLE, layout="centered")
inject_custom_styles()


if "archive_engine" not in st.session_state:
    st.session_state.archive_engine = ArchiveIntelligence()


with st.sidebar:
    st.markdown("### SYSTEM DIAGNOSTICS")
    st.info(
        f"**Knowledge Nodes:** {st.session_state.archive_engine.total_indexed_fragments}\n\n"
        f"**Inference Engine:** Gemini-2.5-Flash\n\n"
        f"**Vector Store:** FAISS Local"
    )

title_layout_spacer, language_selector_column = st.columns([3, 1])
with language_selector_column:
    selected_language_preference = st.selectbox(
        label="🌐 Language / زبان", options=["English", "Urdu"]
    )

active_content = APP_CONTENT[selected_language_preference]

st.markdown(
    f'<div style="direction: {active_content["dir"]}; text-align: {active_content["align"]};">'
    f'<h1>{active_content["title"]}</h1>'
    f'<p style="color: #94a3b8;">{active_content["subtitle"]}</p></div>',
    unsafe_allow_html=True,
)

with st.expander(active_content["btn_story"]):
    st.write(st.session_state.archive_engine.raw_manuscript_content)

st.markdown("---")

user_query_input = st.text_input(
    active_content["input_label"], placeholder=active_content["placeholder"]
)

if user_query_input:
    with st.spinner(active_content["searching"]):
        generated_answer, source_citations = (
            st.session_state.archive_engine.retrieve_and_generate(
                user_query_input, language_preference=selected_language_preference
            )
        )

        display_response_card(
            generated_answer,
            header="VERIFIED ARCHIVE RESPONSE",
            alignment=active_content["align"],
            direction=active_content["dir"],
        )

        st.markdown(
            f'<h3 class="source-header">{active_content["sources"]}</h3>',
            unsafe_allow_html=True,
        )

        for citation_document in source_citations:
            display_source_fragment(citation_document)
