import base64
import os

import streamlit as st
from constants import get_dynamic_system_instructions
from langchain_classic.agents import AgentExecutor, create_tool_calling_agent
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_google_genai import ChatGoogleGenerativeAI
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


@traceable(name="ReAct_Neural_Chatbot", run_type="chain")
def execute_neural_processing(llm_instance, message_log, active_session_id):
    from tools_engine import (
        Calculator,
        DateResponse,
        TimeResponse,
        get_current_date,
        get_current_time,
        get_search_tool,
    )

    execution_process_completed = False

    tools = [get_current_time, get_current_date, get_search_tool(), Calculator]

    system_instructions = get_dynamic_system_instructions()

    schema_registry = {
        "get_current_time": TimeResponse,
        "get_current_date": DateResponse,
    }

    nexa_prompt_template = ChatPromptTemplate.from_messages(
        [
            ("system", "{system_instructions}"),
            MessagesPlaceholder(variable_name="chat_history"),
            ("human", "{input}"),
            MessagesPlaceholder(variable_name="agent_scratchpad"),
        ]
    ).with_config({"run_name": "Nexa_Custom_Prompt_Template"})

    reasoning_agent = create_tool_calling_agent(
        llm=llm_instance,
        tools=tools,
        prompt=nexa_prompt_template,
    ).with_config({"run_name": "ReAct_Nexa_Chatbot"})

    neural_agent_executor = AgentExecutor(
        agent=reasoning_agent,
        tools=tools,
        verbose=False,
        handle_parsing_errors=True,
        return_intermediate_steps=True,
    ).with_config({"run_name": "ReAct_Neural_Execution_Engine"})

    with st.chat_message(constants.ASSISTANT_ROLE, avatar=constants.BOT_AVATAR):
        response_stream_container = st.empty()
        status_placeholder = st.empty()
        status_placeholder.status("Loading...", expanded=False)

        formatted_history = [SystemMessage(content=system_instructions)]
        for chat_entry in message_log[:-1]:
            msg_class = (
                HumanMessage if chat_entry["role"] == constants.USER_ROLE else AIMessage
            )
            formatted_history.append(msg_class(content=chat_entry["content"]))

        latest_user_query = message_log[-1]["content"]

        try:
            ai_chatbot_runtime_response = neural_agent_executor.invoke(
                {
                    "input": latest_user_query,
                    "chat_history": formatted_history[1:],
                    "system_instructions": system_instructions,
                }
            )

            status_placeholder.empty()
            raw_inference_content = ai_chatbot_runtime_response.get("output")

            if isinstance(raw_inference_content, list):
                final_inference_text = " ".join(
                    [
                        (
                            content_block.get("text", "")
                            if isinstance(content_block, dict)
                            else str(content_block)
                        )
                        for content_block in raw_inference_content
                    ]
                )
            else:
                final_inference_text = str(raw_inference_content or "")

            final_inference_text = final_inference_text.strip()
            ai_agent_decision_steps = ai_chatbot_runtime_response.get(
                "intermediate_steps", []
            )

            if ai_agent_decision_steps:
                last_executed_step, raw_tool_observation = ai_agent_decision_steps[-1]
                tool_name = str(last_executed_step.tool)

                if tool_name in schema_registry:
                    structured_llm = llm_instance.with_structured_output(
                        schema_registry[tool_name]
                    )

                    json_res = structured_llm.invoke(
                        f"Format this observation: {raw_tool_observation}"
                    )
                    final_inference_text = (
                        f"```json\n{json_res.model_dump_json(indent=4)}\n```"
                    )

            response_stream_container.markdown(final_inference_text)
            st.session_state.chat_sessions[active_session_id]["messages"].append(
                {"role": constants.ASSISTANT_ROLE, "content": final_inference_text}
            )
            execution_process_completed = True

        except Exception as e:
            status_placeholder.empty()
            execution_process_completed = False
            st.error(f"Neural Core Error: {e}")

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
