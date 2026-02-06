import streamlit as st


def display_response_card(text, header=None, alignment="left", direction="ltr"):
    header_html = f'<h4 style="color: #60a5fa;">{header}</h4>' if header else ""
    st.markdown(
        f"""
        <div class="glass-card" style="direction: {direction}; text-align: {alignment};">
            {header_html}
            <p style="font-size: 1.1rem;">{text}</p>
        </div>
    """,
        unsafe_allow_html=True,
    )


def display_source_fragment(document):
    tag = document.metadata.get("reference_tag", "LOG")
    st.markdown(
        f"""
        <div class="glass-card" style="border-left: 3px solid #1e40af; margin-top: 10px;">
            <span style="color: #60a5fa; font-family: monospace; font-weight: bold;">[ {tag} ]</span>
            <p class="source-content">"{document.page_content}"</p>
        </div>
    """,
        unsafe_allow_html=True,
    )
