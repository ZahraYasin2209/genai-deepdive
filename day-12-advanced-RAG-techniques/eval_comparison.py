import os

from deepeval.metrics import AnswerRelevancyMetric, FaithfulnessMetric
from deepeval.models import GeminiModel
from deepeval.test_case import LLMTestCase
from dotenv import load_dotenv
from langchain_classic.chains import RetrievalQA
from langchain_classic.retrievers import (
    SelfQueryRetriever,
    TimeWeightedVectorStoreRetriever,
)
from langchain_classic.retrievers.document_compressors import LLMChainExtractor
from langchain_classic.retrievers import ContextualCompressionRetriever
from langchain_community.retrievers import BM25Retriever
from langchain_community.vectorstores import FAISS
from langsmith import Client
from langsmith.evaluation import evaluate

from constants import (
    EVALUATION_DECAY_RATE,
    EVALUATION_THRESHOLD,
    GENERATIVE_MODEL_NAME,
    RETRIEVAL_TOP_K_RESULTS,
    TARGET_DATASET,
    TEMPERATURE,
)
from rag_knowledge_engine import RAGManager


load_dotenv()


langsmith_client = Client()
knowledge_engine = RAGManager()
llm_generation_model = knowledge_engine.llm_generation_model
embedding_engine = knowledge_engine.embedding_engine
archive_source_chunks = knowledge_engine.loaded_documents


def get_bm25_retriever():
    return BM25Retriever.from_documents(
        knowledge_engine.search_index_splitter.split_documents(archive_source_chunks)
    )


def get_contextual_compression_retriever():
    return ContextualCompressionRetriever(
        base_compressor=LLMChainExtractor.from_llm(llm_generation_model),
        base_retriever=knowledge_engine.get_vector_store_retriever(),
    )


def get_time_weighted_vector_store_retriever():
    return TimeWeightedVectorStoreRetriever(
        vectorstore=FAISS.from_documents(
            knowledge_engine.search_index_splitter.split_documents(
                archive_source_chunks
            ),
            embedding_engine,
        ),
        decay_rate=EVALUATION_DECAY_RATE,
        k=RETRIEVAL_TOP_K_RESULTS,
    )


def get_self_query_retriever():
    metadata_field_info = [
        {"name": "source", "description": "The origin document file", "type": "string"}
    ]

    vectorstore = FAISS.from_documents(
        knowledge_engine.search_index_splitter.split_documents(archive_source_chunks),
        embedding_engine,
    )

    try:
        return SelfQueryRetriever.from_llm(
            llm_generation_model,
            vectorstore,
            "Lahore Haveli Archives",
            metadata_field_info,
            use_experimental_translator=True,
            verbose=True,
        )
    except Exception:
        print("CRITICAL: Something is missing.")
        return knowledge_engine.get_vector_store_retriever()


RETRIEVER_STRATEGIES = {
    "VectorStoreRetriever": knowledge_engine.get_vector_store_retriever,
    "MultiQueryRetriever": knowledge_engine.get_multi_query_retriever,
    "ParentDocumentRetriever": knowledge_engine.get_parent_document_retriever,
    "BM25Retriever": get_bm25_retriever,
    "ContextualCompressionRetriever": get_contextual_compression_retriever,
    "TimeWeightedVectorStoreRetriever": get_time_weighted_vector_store_retriever,
    "SelfQueryRetriever": get_self_query_retriever,
}


def run_rag_inference(dataset_input: dict, retriever_strategy_label: str) -> dict:
    get_active_retriever = RETRIEVER_STRATEGIES.get(retriever_strategy_label)

    rag_response_pipeline = RetrievalQA.from_chain_type(
        llm=llm_generation_model,
        chain_type="stuff",
        retriever=get_active_retriever(),
        return_source_documents=True,
        chain_type_kwargs={"prompt": knowledge_engine.inference_prompt_template},
    )

    prediction_output = rag_response_pipeline.invoke(dataset_input["question"])

    return {
        "answer": prediction_output["result"],
        "retrieved_contexts": [
            archival_retrieved_context.page_content
            for archival_retrieved_context in prediction_output["source_documents"]
        ],
    }


def compute_deepeval_metrics(prediction_run, dataset_example):
    gemini_eval_judge = GeminiModel(
        model=GENERATIVE_MODEL_NAME,
        api_key=os.getenv("GEMINI_API_KEY"),
        temperature=TEMPERATURE,
    )

    validation_case = LLMTestCase(
        input=dataset_example.inputs["question"],
        actual_output=prediction_run.outputs["answer"],
        retrieval_context=prediction_run.outputs["retrieved_contexts"],
        expected_output=dataset_example.outputs["answer"],
    )

    faithfulness_scorer = FaithfulnessMetric(
        threshold=EVALUATION_THRESHOLD, model=gemini_eval_judge
    )
    relevancy_scorer = AnswerRelevancyMetric(
        threshold=EVALUATION_THRESHOLD, model=gemini_eval_judge
    )

    faithfulness_scorer.measure(validation_case)
    relevancy_scorer.measure(validation_case)

    return {
        "results": [
            {"key": "faithfulness_score", "score": faithfulness_scorer.score},
            {"key": "answer_relevancy_score", "score": relevancy_scorer.score},
        ]
    }


if __name__ == "__main__":
    if not langsmith_client.has_dataset(dataset_name=TARGET_DATASET):
        print(f"Error: Dataset '{TARGET_DATASET}' not found in LangSmith.")
    else:
        for retriever_strategy_label in RETRIEVER_STRATEGIES.keys():
            print(f"Benchmarking Strategy: {retriever_strategy_label}...")

            evaluate(
                lambda inputs: run_rag_inference(inputs, retriever_strategy_label),
                data=TARGET_DATASET,
                evaluators=[compute_deepeval_metrics],
                experiment_prefix=f"Experiment-{retriever_strategy_label}",
            )
        print(f"Full Comparison Completed. Results in LangSmith.")
