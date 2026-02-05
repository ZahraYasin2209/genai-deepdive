import base64
import os

import constants
import streamlit as st
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langsmith import traceable


def get_langchain_model():
    model_name = st.session_state.get("selected_model_version", constants.MODEL_NAME)
    api_key = st.secrets.get("GEMINI_API_KEY") or os.getenv("GEMINI_API_KEY")

    if not api_key:
        st.error(
            "Neural Configuration Error: GEMINI_API_KEY not found. Please configure secrets."
        )
        st.stop()

    return ChatGoogleGenerativeAI(
        model=model_name,
        google_api_key=api_key,
        temperature=constants.TEMPERATURE,
        max_output_tokens=constants.MAX_RESPONSE_TOKENS,
        streaming=True,
    )


@traceable(name="Neural Core Processing")
def execute_neural_processing(llm_instance, message_log, active_session_id):
    from tools_engine import (
        DateResponse,
        TimeResponse,
        get_current_date,
        get_current_time,
    )

    tool_registry = {
        "get_current_time": get_current_time,
        "get_current_date": get_current_date,
    }

    schema_registry = {
        "get_current_time": TimeResponse,
        "get_current_date": DateResponse,
    }

    llm_with_tools = llm_instance.bind_tools(list(tool_registry.values()))

    with st.chat_message(constants.ASSISTANT_ROLE, avatar=constants.BOT_AVATAR):
        response_stream_container = st.empty()
        status_placeholder = st.empty()
        status_placeholder.status("Loading...", expanded=False)

        formatted_history = [SystemMessage(content=constants.SYSTEM_INSTRUCTION)]

        for chat_entry in message_log:
            content_payload = chat_entry["content"]

            if isinstance(content_payload, list):
                structured_multimodal_payload = []
                for content_fragment in content_payload:
                    if content_fragment.get("type") == "media":
                        structured_multimodal_payload.append(
                            {
                                "type": "media",
                                "mime_type": content_fragment["mime_type"],
                                "data": content_fragment["data"],
                            }
                        )
                    else:
                        structured_multimodal_payload.append(content_fragment)
                content_payload = structured_multimodal_payload

            msg_class = (
                HumanMessage if chat_entry["role"] == constants.USER_ROLE else AIMessage
            )
            formatted_history.append(msg_class(content=content_payload))

        execution_process_completed = False

        try:
            initial_ai_chatbot_msg = llm_with_tools.invoke(formatted_history)

            if initial_ai_chatbot_msg.tool_calls:
                status_placeholder.empty()
                tool_call = initial_ai_chatbot_msg.tool_calls[0]
                tool_name = tool_call["name"]

                tool_to_call = tool_registry.get(tool_name)
                raw_observation = tool_to_call.invoke(tool_call["args"])

                tool_msg = ToolMessage(
                    content=str(raw_observation), tool_call_id=tool_call["id"]
                )

                structured_llm = llm_instance.with_structured_output(
                    schema_registry[tool_name]
                )

                triggering_user_query = [
                    user_message
                    for user_message in formatted_history
                    if isinstance(user_message, HumanMessage)
                ][-1]

                json_response = structured_llm.invoke(
                    [triggering_user_query, initial_ai_chatbot_msg, tool_msg]
                )

                final_inference_text = (
                    f"```json\n{json_response.model_dump_json(indent=4)}\n```"
                )
                response_stream_container.markdown(final_inference_text)
            else:
                final_inference_text = ""
                loading_cleared = False

                for partial_chunk in llm_instance.stream(formatted_history):
                    if not partial_chunk.content:
                        continue

                    if not loading_cleared:
                        status_placeholder.empty()
                        loading_cleared = True

                    final_inference_text += partial_chunk.content
                    response_stream_container.markdown(final_inference_text + "▌")

                response_stream_container.markdown(final_inference_text)

            st.session_state.chat_sessions[active_session_id]["messages"].append(
                {"role": constants.ASSISTANT_ROLE, "content": final_inference_text}
            )
            execution_process_completed = True
        except Exception as e:
            status_placeholder.empty()
            st.error(f"Neural Core Error: {e}")
            execution_process_completed = False

    return execution_process_completed


@traceable(name="Multimodal Formatter")
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
