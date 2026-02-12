from dotenv import load_dotenv
from langchain_core.messages import HumanMessage

from ai_neural_engine import get_nexa_app
import constants

load_dotenv()


def execute_nexa_protocol_test(user_prompt, expect_refusal_logic=False):
    nexa_graph_app = get_nexa_app()

    nexa_initial_state = {
        "messages": [HumanMessage(content=user_prompt)],
        "system_instructions": constants.get_dynamic_system_instructions()
    }

    print(f"\n--- INITIATING TEST FOR: '{user_prompt}' ---")
    extracted_inference_text = ""

    for execution_step in nexa_graph_app.stream(nexa_initial_state):
        for activated_node, state_snapshot in execution_step.items():
            raw_node_output = state_snapshot["messages"][-1].content

            if isinstance(raw_node_output, list):
                extracted_inference_text = " ".join([
                    str(block.get("text", block)) if isinstance(block, dict) else str(block)
                    for block in raw_node_output
                ])
            else:
                extracted_inference_text = str(raw_node_output)

    print(f"FINAL INFERENCE: {extracted_inference_text}")

    refusal_string_detected = "do not have access to historical data" in extracted_inference_text

    if expect_refusal_logic and refusal_string_detected:
        print("TEST PASSED: Agent successfully enforced historical data refusal protocol.")
    elif not expect_refusal_logic and not refusal_string_detected:
        print("TEST PASSED: Agent successfully processed valid computational/logical query.")
    else:
        print("TEST FAILED: Agent behavior deviated from defined temporal protocols.")


if __name__ == "__main__":
    execute_nexa_protocol_test(
        user_prompt="What is 144 * 2?",
        expect_refusal_logic=False
    )

    execute_nexa_protocol_test(
        user_prompt="What was the time yesterday at 5 PM?",
        expect_refusal_logic=True
    )

    execute_nexa_protocol_test(
        user_prompt="When will cricket match of India vs. Pakistan take place?",
        expect_refusal_logic=False
    )
