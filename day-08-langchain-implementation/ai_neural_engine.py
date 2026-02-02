import os
import base64
import streamlit as st
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

import constants


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


def execute_neural_processing(llm_instance, message_log, active_session_id):
    with st.chat_message(constants.ASSISTANT_ROLE, avatar=constants.BOT_AVATAR):
        with st.status("Loading...", expanded=False) as status:
            formatted_history = [SystemMessage(content=constants.SYSTEM_INSTRUCTION)]

            for chat_entry in message_log:
                content_payload = chat_entry["content"]

                if isinstance(content_payload, list):
                    structured_multimodal_payload = []
                    for content_fragment in content_payload:
                        if content_fragment.get("type") == "media_data":
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
                    HumanMessage
                    if chat_entry["role"] == constants.USER_ROLE
                    else AIMessage
                )
                formatted_history.append(msg_class(content=content_payload))

            response_stream_container = st.empty()
            final_inference_text = ""

            try:
                for partial_chunk in llm_instance.stream(formatted_history):
                    final_inference_text += partial_chunk.content
                    response_stream_container.markdown(final_inference_text + "▌")

                response_stream_container.markdown(final_inference_text)
                status.update(label="Inference Complete", state="complete")

                st.session_state.chat_sessions[active_session_id]["messages"].append(
                    {"role": constants.ASSISTANT_ROLE, "content": final_inference_text}
                )
                st.rerun()
            except Exception as e:
                st.error(f"Neural Core Error: {e}")

    return True


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
            {"type": "media_data", "mime_type": recorded_audio.type, "data": b64_audio}
        )

    return content_sequence
