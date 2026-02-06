import os

from dotenv import load_dotenv
from langchain_classic.chains import RetrievalQA
from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores import FAISS
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter

from constants import (
    DEFAULT_KNOWLEDGE_SOURCE,
    DOCUMENT_CHUNK_OVERLAP,
    DOCUMENT_CHUNK_SIZE,
    EMBEDDING_MODEL_NAME,
    GENERATIVE_MODEL_NAME,
    LANGUAGE_URDU,
    RETRIEVAL_TOP_K_RESULTS,
    TEMPERATURE,
)


load_dotenv()


class ArchiveIntelligence:
    def __init__(self, data_source_path=DEFAULT_KNOWLEDGE_SOURCE):
        self.data_source_path = data_source_path
        self.embedding_engine = GoogleGenerativeAIEmbeddings(model=EMBEDDING_MODEL_NAME)
        self.inference_engine = ChatGoogleGenerativeAI(
            model=GENERATIVE_MODEL_NAME, temperature=TEMPERATURE
        )
        self.vector_store = self.initialize_knowledge_base()

    def initialize_knowledge_base(self):
        if not os.path.exists(self.data_source_path):
            raise FileNotFoundError(f"Missing Source Archive: {self.data_source_path}")

        raw_documents = TextLoader(self.data_source_path).load()
        self.raw_manuscript_content = raw_documents[0].page_content

        text_segmenter = RecursiveCharacterTextSplitter(
            chunk_size=DOCUMENT_CHUNK_SIZE, chunk_overlap=DOCUMENT_CHUNK_OVERLAP
        )

        semantic_fragments = text_segmenter.split_documents(raw_documents)
        for segment_index, text_segment in enumerate(semantic_fragments):
            unique_reference_id = f"ARCHIVE-ID-{segment_index + 1}"
            text_segment.metadata["reference_tag"] = unique_reference_id

        self.total_indexed_fragments = len(semantic_fragments)

        return FAISS.from_documents(semantic_fragments, self.embedding_engine)

    def retrieve_and_generate(self, user_query, language_preference="English"):
        retrieval_logic_chain = RetrievalQA.from_chain_type(
            llm=self.inference_engine,
            chain_type="stuff",
            retriever=self.vector_store.as_retriever(
                search_kwargs={"k": RETRIEVAL_TOP_K_RESULTS}
            ),
            return_source_documents=True,
        )

        language_instruction = (
            "Respond in Urdu."
            if language_preference == LANGUAGE_URDU
            else "Respond in English."
        )
        execution_result = retrieval_logic_chain.invoke(
            f"{language_instruction} {user_query}"
        )

        return execution_result["result"], execution_result["source_documents"]
