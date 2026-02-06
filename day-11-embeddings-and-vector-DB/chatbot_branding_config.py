import streamlit as st
from mappings import ANARKALI_ORACLE_LOCALIZATION_MAPPINGS


APP_CONTENT = ANARKALI_ORACLE_LOCALIZATION_MAPPINGS


def inject_custom_styles():
    st.markdown(
        """
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Noto+Nastaliq+Urdu:wght@400;700&family=Inter:wght@400;700&display=swap');

        .stApp { background: #0f172a; color: #f8fafc; }

        div[data-baseweb="select"] + label, .stSelectbox label p {
            color: #00f2ff !important;
            font-weight: bold;
            text-transform: uppercase;
        }

        .glass-card {
            background: rgba(30, 41, 59, 0.5);
            backdrop-filter: blur(10px);
            border: 1px solid rgba(255, 255, 255, 0.1);
            border-radius: 12px;
            padding: 20px;
            margin-top: 15px;
        }

        .source-header {
            color: #ffffff !important;
            border-bottom: 2px solid #3b82f6;
            padding-bottom: 5px;
            margin-top: 30px;
        }

        .source-content { color: #ffffff !important; font-style: italic; }

        div.stButton > button {
            background-color: transparent !important;
            color: #60a5fa !important;
            border: 1px solid #60a5fa !important;
            width: 100%;
        }
        div.stButton > button:hover {
            background-color: #3b82f6 !important;
            color: white !important;
        }
        </style>
    """,
        unsafe_allow_html=True,
    )
