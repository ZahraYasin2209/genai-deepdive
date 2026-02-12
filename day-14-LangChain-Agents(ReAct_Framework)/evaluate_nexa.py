import gc
import os
import time

from deepeval.metrics import GEval
from deepeval.models import GeminiModel
from deepeval.test_case import LLMTestCase, LLMTestCaseParams
from langchain_core.messages import HumanMessage, ToolMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langsmith import Client, evaluate
from tools_engine import get_search_tool

from constants import (
    BOT_FAILURE_COMMENT,
    EVALUATION_TEMPERATURE,
    EVALUATION_TEMPERATURES_LIST,
    EVALUATION_THRESHOLD,
    FAILURE_SCORE_FALLBACK,
    LANGSMITH_DATASET_NAME,
    MODEL_NAME,
    PROTOCOL_ADHERENCE_CRITERIA,
    PROTOCOL_SCORE_KEY,
    SECONDARY_MODEL_NAME
)


client = Client()

eval_model = GeminiModel(model=MODEL_NAME, api_key=os.getenv("GEMINI_API_KEY"))


def protocol_evaluator(run, example):
    input_text = example.inputs.get("input")
    actual_output = run.outputs.get("output")

    if actual_output is None:
        protocol_eval_result = {
            "key": PROTOCOL_SCORE_KEY,
            "score": FAILURE_SCORE_FALLBACK,
            "comment": BOT_FAILURE_COMMENT,
        }
    else:
        metric = GEval(
            name="Backend Protocol Adherence",
            criteria=PROTOCOL_ADHERENCE_CRITERIA,
            evaluation_params=[
                LLMTestCaseParams.INPUT,
                LLMTestCaseParams.ACTUAL_OUTPUT,
            ],
            threshold=EVALUATION_THRESHOLD,
            model=eval_model,
        )
        metric.measure(LLMTestCase(input=input_text, actual_output=actual_output))
        protocol_eval_result = {
            "key": PROTOCOL_SCORE_KEY,
            "score": metric.score,
            "comment": metric.reason,
        }

    return protocol_eval_result


def nexa_bot_target(inputs):
    user_query = inputs.get("input", "")
    historical_triggers = ["yesterday", "past", "last week"]

    inference_payload = {"output": "Error: Model failed to generate a valid response."}

    if any(
        user_query_word in user_query.lower() for user_query_word in historical_triggers
    ):
        inference_payload = {
            "output": "I can only provide the current time and date. I do not have access to historical data."
        }
    else:
        try:
            raw_llm = ChatGoogleGenerativeAI(
                model=inputs.get("model_name"),
                temperature=inputs.get("temperature", EVALUATION_TEMPERATURE),
            )
            tavily_tool = get_search_tool()
            llm_with_tools = raw_llm.bind_tools([tavily_tool])

            input_messages = [HumanMessage(content=user_query)]
            ai_msg = llm_with_tools.invoke(input_messages)

            if ai_msg.tool_calls:
                tool_call = ai_msg.tool_calls[0]
                tool_message = ToolMessage(
                    content=str(tavily_tool.invoke(tool_call["args"])),
                    tool_call_id=tool_call["id"],
                )

                final_response = llm_with_tools.invoke(
                    [input_messages[0], ai_msg, tool_message]
                )
                inference_payload = {"output": str(final_response.content)}
            else:
                inference_payload = {"output": str(ai_msg.content)}

        except Exception as e:
            print(f"Error in target: {e}")

    return inference_payload


if not client.has_dataset(dataset_name=LANGSMITH_DATASET_NAME):
    langsmith_dataset = client.create_dataset(LANGSMITH_DATASET_NAME)
else:
    langsmith_dataset = client.read_dataset(dataset_name=LANGSMITH_DATASET_NAME)
    existing_examples = list(client.list_examples(dataset_id=langsmith_dataset.id))
    if len(existing_examples) < 4:
        for input_example in existing_examples:
            client.delete_example(input_example.id)

        client.create_examples(
            inputs=[
                {"input": "Square of 16?"},
                {"input": "What was the time yesterday at noon?"},
                {
                    "input": "When will T20 cricket match between India & Pakistan takes place?"
                },
                {"input": "Which event is recently celebrated in Lahore?"},
            ],
            dataset_id=langsmith_dataset.id,
        )


def run_final_evals():
    for target_model_name in [MODEL_NAME, SECONDARY_MODEL_NAME]:
        print(f"Running MODEL TEST: {target_model_name}")

        evaluate(
            lambda dataset_row_input, model=target_model_name: nexa_bot_target(
                {
                    **dataset_row_input,
                    "model_name": model,
                    "temperature": EVALUATION_TEMPERATURE,
                }
            ),
            data=LANGSMITH_DATASET_NAME,
            evaluators=[protocol_evaluator],
            experiment_prefix=f"REPORT-Model-{target_model_name}",
        )
        gc.collect()
        time.sleep(1)

    for target_temperature in EVALUATION_TEMPERATURES_LIST:
        print(f"Running TEMP TEST: {target_temperature}")
        evaluate(
            lambda dataset_row_input, temperature=target_temperature: nexa_bot_target(
                {
                    **dataset_row_input,
                    "model_name": MODEL_NAME,
                    "temperature": temperature,
                }
            ),
            data=LANGSMITH_DATASET_NAME,
            evaluators=[protocol_evaluator],
            experiment_prefix=f"REPORT-Temp-{target_temperature}",
        )
        gc.collect()
        time.sleep(1)


if __name__ == "__main__":
    run_final_evals()
