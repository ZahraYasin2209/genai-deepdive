import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_classic.retrievers import MultiQueryRetriever, ParentDocumentRetriever
from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores import FAISS
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.stores import InMemoryStore
from langchain_google_genai import ChatGoogleGenerativeAI, GoogleGenerativeAIEmbeddings
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langsmith import traceable

from constants import (
    CHILD_CHUNK_OVERLAP,
    CHILD_CHUNK_SIZE,
    DEFAULT_KNOWLEDGE_SOURCE,
    EMBEDDING_MODEL_NAME,
    GENERATIVE_MODEL_NAME,
    PARENT_CHUNK_OVERLAP,
    PARENT_CHUNK_SIZE,
    RETRIEVAL_TOP_K_RESULTS,
    SYSTEM_INSTRUCTIONS,
    TEMPERATURE,
    USER_QUESTION_TEMPLATE,
)


load_dotenv()


class RAGManager:
    def __init__(self, file_path=DEFAULT_KNOWLEDGE_SOURCE):
        api_key = os.getenv("GEMINI_API_KEY")
        self.embedding_engine = GoogleGenerativeAIEmbeddings(
            model=EMBEDDING_MODEL_NAME, google_api_key=api_key
        )

        self.llm_generation_model = ChatGoogleGenerativeAI(
            model=GENERATIVE_MODEL_NAME, temperature=TEMPERATURE, google_api_key=api_key
        )

        base_directory = Path(__file__).parent
        self.loaded_documents = TextLoader(str(base_directory / file_path)).load()

        self.search_index_splitter = RecursiveCharacterTextSplitter(
            chunk_size=CHILD_CHUNK_SIZE, chunk_overlap=CHILD_CHUNK_OVERLAP
        )

        self.context_parent_splitter = RecursiveCharacterTextSplitter(
            chunk_size=PARENT_CHUNK_SIZE, chunk_overlap=PARENT_CHUNK_OVERLAP
        )

        self.inference_prompt_template = ChatPromptTemplate.from_messages(
            [("system", SYSTEM_INSTRUCTIONS), ("human", USER_QUESTION_TEMPLATE)]
        )

    @traceable(name="Semantic_Vector_Lookup", run_type="retriever")
    def get_vector_store_retriever(self):
        search_optimized_fragments = self.search_index_splitter.split_documents(
            self.loaded_documents
        )

        semantic_vector_store = FAISS.from_documents(
            search_optimized_fragments, self.embedding_engine
        )

        return semantic_vector_store.as_retriever(
            search_kwargs={"k": RETRIEVAL_TOP_K_RESULTS}
        )

    @traceable(name="Multi_Query_Expansion_Engine", run_type="retriever")
    def get_multi_query_retriever(self):
        return MultiQueryRetriever.from_llm(
            retriever=self.get_vector_store_retriever(), llm=self.llm_generation_model
        )

    @traceable(name="Hierarchical_Parent_Doc_Scanner", run_type="retriever")
    def get_parent_document_retriever(self):
        parent_documents_storage = InMemoryStore()
        initialization_placeholder = [Document(page_content="init", metadata={})]
        searchable_vector_index = FAISS.from_documents(
            initialization_placeholder, self.embedding_engine
        )

        parent_doc_retriever = ParentDocumentRetriever(
            vectorstore=searchable_vector_index,
            docstore=parent_documents_storage,
            child_splitter=self.search_index_splitter,
            parent_splitter=self.context_parent_splitter,
        )
        parent_doc_retriever.add_documents(self.loaded_documents)

        return parent_doc_retriever
