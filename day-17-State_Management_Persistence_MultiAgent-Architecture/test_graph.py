from dotenv import load_dotenv
from langchain_core.messages import HumanMessage

import constants
from ai_neural_engine import get_vanguard_research_app


load_dotenv()


def execute_vanguard_protocol_test(user_prompt, expect_refusal_logic=False):
    app = get_vanguard_research_app()

    vanguard_initial_state = {
        "messages": [HumanMessage(content=user_prompt)],
        "system_instructions": constants.get_dynamic_system_instructions(),
    }

    print(f"\n[STARTING VANGUARD TEST]: '{user_prompt}'")

    final_synthesized_text = ""

    for execution_step in app.stream(vanguard_initial_state):
        for activated_node_name, state_snapshot in execution_step.items():
            print(f"\n[NODE ACTIVATED]: {activated_node_name}")

            node_generated_message = state_snapshot["messages"][-1]
            raw_content = node_generated_message.content

            if isinstance(raw_content, list):
                node_text_output = " ".join(
                    [
                        (
                            str(content_block.get("text", content_block))
                            if isinstance(content_block, dict)
                            else str(content_block)
                        )
                        for content_block in raw_content
                    ]
                )
            else:
                node_text_output = str(raw_content)

            final_synthesized_text = node_text_output
            print(f"Node Intelligence: {node_text_output[:120]}...")

    print(f"\n[FINAL INTELLIGENCE REPORT]:\n{final_synthesized_text}")

    is_refusal_detected = (
        "do not have access to historical data" in final_synthesized_text.lower()
    )

    test_status = "FAILED"
    if expect_refusal_logic == is_refusal_detected:
        test_status = "PASSED"

    print(f"\n[RESULT]: {test_status} - Agent logic aligned with Vanguard protocols.")

    return test_status


if __name__ == "__main__":
    execute_vanguard_protocol_test(
        user_prompt="What is 144 * 2?", expect_refusal_logic=False
    )

    execute_vanguard_protocol_test(
        user_prompt="When will the India vs Pakistan cricket match take place in 2026?",
        expect_refusal_logic=False,
    )

    execute_vanguard_protocol_test(
        user_prompt="Generate a brief technical report on side effects of Covid-19.",
        expect_refusal_logic=False,
    )
