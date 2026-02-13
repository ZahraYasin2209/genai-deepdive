import os

from deepeval.metrics import GEval
from deepeval.models import GeminiModel
from deepeval.test_case import LLMTestCase, LLMTestCaseParams
from langchain_core.messages import AIMessage, HumanMessage
from langsmith import Client, evaluate

from ai_neural_engine import get_vanguard_research_app
from constants import (
    BOT_FAILURE_COMMENT,
    EVALUATION_THRESHOLD,
    FAILURE_SCORE_FALLBACK,
    LANGSMITH_DATASET_NAME,
    MODEL_NAME,
    PROTOCOL_ADHERENCE_CRITERIA,
    PROTOCOL_SCORE_KEY,
    get_dynamic_system_instructions,
)


client = Client()
llm_eval_model = GeminiModel(model=MODEL_NAME, api_key=os.getenv("GEMINI_API_KEY"))


def protocol_evaluator(run, example):
    protocol_assessment_result = {
        "key": PROTOCOL_SCORE_KEY,
        "score": FAILURE_SCORE_FALLBACK,
        "comment": BOT_FAILURE_COMMENT,
    }

    if run.outputs.get("output"):
        adherence_metric = GEval(
            name="Research Protocol Adherence",
            criteria=PROTOCOL_ADHERENCE_CRITERIA,
            evaluation_params=[
                LLMTestCaseParams.INPUT,
                LLMTestCaseParams.ACTUAL_OUTPUT,
            ],
            threshold=EVALUATION_THRESHOLD,
            model=llm_eval_model,
        )

        adherence_metric.measure(
            LLMTestCase(
                input=example.inputs.get("input"),
                actual_output=run.outputs.get("output"),
            )
        )
        protocol_assessment_result = {
            "key": PROTOCOL_SCORE_KEY,
            "score": adherence_metric.score,
            "comment": adherence_metric.reason,
        }
        print(
            f"DEBUG - Score: {adherence_metric.score} | Reason: {adherence_metric.reason}"
        )

    return protocol_assessment_result


def vanguard_bot_target(inputs):
    user_intelligence_query = inputs.get("input", "")

    try:
        vanguard_research_engine = get_vanguard_research_app()

        vanguard_execution_state = vanguard_research_engine.invoke(
            {
                "messages": [HumanMessage(content=user_intelligence_query)],
                "system_instructions": get_dynamic_system_instructions(),
            }
        )

        final_inference_text = ""
        for agent_message in reversed(vanguard_execution_state["messages"]):
            if (
                isinstance(agent_message, AIMessage)
                and agent_message.content
                and not agent_message.tool_calls
            ):
                if isinstance(agent_message.content, list):
                    intelligence_report_fragments = [
                        (
                            content_block.get("text", "")
                            if isinstance(content_block, dict)
                            else str(content_block)
                        )
                        for content_block in agent_message.content
                    ]
                    final_inference_text = "".join(intelligence_report_fragments)
                else:
                    final_inference_text = str(agent_message.content)

                if final_inference_text.strip():
                    break

        inference_payload = {"output": final_inference_text.strip()}

    except Exception as e:
        inference_payload = {"output": f"Internal Error: {str(e)}"}

    return inference_payload


def setup_vanguard_dataset():
    if not client.has_dataset(dataset_name=LANGSMITH_DATASET_NAME):
        client.create_dataset(LANGSMITH_DATASET_NAME)

    test_cases = [
        {"input": "When is the India vs Pakistan T20 match in 2026?"},
        {"input": "Technical report on 2026 healthcare innovations."},
        {"input": "Role of AI in software development."},
        {"input": "Briefly explain the Covid-19 side-effects."},
    ]

    client.create_examples(inputs=test_cases, dataset_name=LANGSMITH_DATASET_NAME)


if __name__ == "__main__":
    setup_vanguard_dataset()

    print(f"Starting Vanguard Research Evaluation...")
    evaluate(
        vanguard_bot_target,
        data=LANGSMITH_DATASET_NAME,
        evaluators=[protocol_evaluator],
        experiment_prefix="Vanguard-Protocol-Test",
        num_repetitions=1,
    )
