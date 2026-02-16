import base64
import operator
import os
from typing import Annotated, TypedDict

import streamlit as st
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import END, START, StateGraph
from langgraph.prebuilt import ToolNode
from langsmith import traceable

import constants


def get_langchain_model():
    model_name = st.session_state.get("selected_model_version", constants.MODEL_NAME)
    return ChatGoogleGenerativeAI(
        model=model_name,
        google_api_key=os.getenv("GEMINI_API_KEY"),
        temperature=constants.TEMPERATURE,
        max_output_tokens=constants.MAX_RESPONSE_TOKENS,
        streaming=True,
    )


class NexaState(TypedDict):
    messages: Annotated[list[BaseMessage], operator.add]
    system_instructions: str


def call_nexa_model(state: NexaState):
    primary_large_language_model = get_langchain_model()
    from tools_engine import (
        Calculator,
        get_current_date,
        get_current_time,
        get_search_tool,
    )

    available_tools = [
        get_current_time,
        get_current_date,
        get_search_tool(),
        Calculator,
    ]

    llm_with_tool_access = primary_large_language_model.bind_tools(available_tools)
    context_payload = [SystemMessage(content=state["system_instructions"])] + state[
        "messages"
    ]

    agent_inference_response = llm_with_tool_access.invoke(context_payload)

    return {"messages": [agent_inference_response]}


def get_nexa_app():
    from tools_engine import (
        Calculator,
        get_current_date,
        get_current_time,
        get_search_tool,
    )

    nexa_tool_suite = [
        get_current_time,
        get_current_date,
        get_search_tool(),
        Calculator,
    ]
    nexa_state_blueprint = StateGraph(NexaState)

    nexa_state_blueprint.add_node("reasoning_agent", call_nexa_model)
    nexa_state_blueprint.add_node("action_tools", ToolNode(nexa_tool_suite))

    nexa_state_blueprint.add_edge(START, "reasoning_agent")

    nexa_state_blueprint.add_conditional_edges(
        "reasoning_agent",
        lambda current_state: (
            "action_tools" if current_state["messages"][-1].tool_calls else END
        ),
    )

    return (nexa_state_blueprint.add_edge("action_tools", "reasoning_agent")).compile()


@traceable(name="ReAct_Neural_Chatbot", run_type="chain")
def execute_neural_processing(llm_instance, message_log, active_session_id):
    system_instructions = constants.get_dynamic_system_instructions()
    app = get_nexa_app()

    with st.chat_message(constants.ASSISTANT_ROLE, avatar=constants.BOT_AVATAR):
        status_placeholder = st.empty()
        status_placeholder.status("Nexa thinking...", expanded=False)

        formatted_history = []
        for chat_entry in message_log:
            msg_class = (
                HumanMessage(content=chat_entry["content"])
                if chat_entry["role"] == constants.USER_ROLE
                else AIMessage(content=chat_entry["content"])
            )
            formatted_history.append(msg_class)

        try:
            ai_chatbot_runtime_response = app.invoke(
                {
                    "messages": formatted_history,
                    "system_instructions": system_instructions,
                }
            )
            status_placeholder.empty()

            raw_inference_content = ai_chatbot_runtime_response["messages"][-1].content

            if isinstance(raw_inference_content, list):
                final_inference_text = " ".join(
                    [
                        (
                            str(content_block.get("text", ""))
                            if isinstance(content_block, dict)
                            else str(content_block)
                        )
                        for content_block in raw_inference_content
                    ]
                )
            else:
                final_inference_text = str(raw_inference_content)

            final_text = final_inference_text.strip()

            st.session_state.chat_sessions[active_session_id]["messages"].append(
                {"role": constants.ASSISTANT_ROLE, "content": final_text}
            )
            execution_process_completed = True
        except Exception as e:
            status_placeholder.empty()
            st.error(f"Graph Error: {e}")
            execution_process_completed = False

    return execution_process_completed


def format_multimodal_content(user_text, uploaded_files=None, recorded_audio=None):
    content_sequence = [{"type": "text", "text": user_text or "Analyze inputs."}]

    if uploaded_files:
        for uploaded_file in uploaded_files:
            if "image" in uploaded_file.type:
                b64_image = base64.b64encode(uploaded_file.getvalue()).decode("utf-8")
                content_sequence.append(
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:{uploaded_file.type};base64,{b64_image}"
                        },
                    }
                )

    if recorded_audio:
        b64_audio = base64.b64encode(recorded_audio.getvalue()).decode("utf-8")
        content_sequence.append(
            {"type": "media", "mime_type": recorded_audio.type, "data": b64_audio}
        )

    return content_sequence
