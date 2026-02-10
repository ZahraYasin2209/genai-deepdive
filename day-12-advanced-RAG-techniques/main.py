import logging
import os
import time

from dotenv import load_dotenv

load_dotenv(override=True)
os.environ["LANGCHAIN_PROJECT"] = "Lahore-Archivist-Monitoring"

import streamlit as st
from langchain_classic.chains import RetrievalQA
from langsmith import traceable

from constants import CHATBOT_PAGE_TITLE
from rag_knowledge_engine import RAGManager
from ui_components import render_retrieval_control_panel


@traceable(name="Lahore_Archivist_Oracle_Inference")
def run_archivist_query(user_query, retriever, engine):
    inference_chain = RetrievalQA.from_chain_type(
        llm=engine.llm_generation_model,
        chain_type="stuff",
        retriever=retriever,
        return_source_documents=True,
        chain_type_kwargs={"prompt": engine.inference_prompt_template},
    )

    return inference_chain.invoke(user_query)


logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("LahoreArchivist")

st.set_page_config(page_title=CHATBOT_PAGE_TITLE, layout="wide")

if not os.getenv("GEMINI_API_KEY"):
    st.error("Missing GEMINI_API_KEY. Please check your .env file.")
    st.stop()


@st.cache_resource(show_spinner=False)
def initialize_rag_retrieval_system():
    logger.info("Building Global Knowledge Engine...")
    knowledge_manager = RAGManager()

    experimental_retriever_cache = {
        "VectorStoreRetriever": knowledge_manager.get_vector_store_retriever(),
        "MultiQueryRetriever": knowledge_manager.get_multi_query_retriever(),
        "ParentDocumentRetriever": knowledge_manager.get_parent_document_retriever(),
    }

    return knowledge_manager, experimental_retriever_cache


try:
    with st.spinner("Synchronizing AI Knowledge Base and Indexing Archives..."):
        knowledge_engine, retriever_strategy_cache = initialize_rag_retrieval_system()
except Exception as initialization_error:
    st.error(f"Critical System Failure: {initialization_error}")
    st.stop()

selected_retrieval_strategy = render_retrieval_control_panel()
st.title("The Lahore Archivist")
user_inquiry = st.text_input(
    "Consult the Oracle:", placeholder="Enter your question here..."
)

if user_inquiry:
    active_retriever = retriever_strategy_cache.get(selected_retrieval_strategy)

    if active_retriever:
        execution_start_timestamp = time.time()
        logger.info(
            f"Starting {selected_retrieval_strategy} pipeline for: {user_inquiry}"
        )

        with st.spinner(f"Executing {selected_retrieval_strategy} Pipeline..."):
            retrieval_response = run_archivist_query(
                user_inquiry, active_retriever, knowledge_engine
            )

        processing_latency = round(time.time() - execution_start_timestamp, 2)
        st.metric("Inference Latency", f"{processing_latency}s")

        st.subheader("Archivist's Detailed Response:")
        st.success(retrieval_response["result"])

        st.subheader("Evidence: Retrieved Fragments")
        if retrieval_response.get("source_documents"):
            for fragment_position, source_document in enumerate(
                retrieval_response["source_documents"]
            ):
                display_number = fragment_position + 1
                with st.expander(f"Context Fragment {display_number} Details"):
                    st.info(source_document.page_content)
        else:
            st.warning("The selected strategy failed to retrieve supporting fragments.")
    else:
        st.error(
            f"The strategy '{selected_retrieval_strategy}' is not properly initialized."
        )
