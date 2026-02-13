import base64
import operator
import os
from typing import Annotated, TypedDict

import streamlit as st
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.graph import END, START, StateGraph
from langgraph.prebuilt import ToolNode

import constants
from tools_engine import get_search_tool


class VanguardResearchMultiAgentArchitecture(TypedDict):
    messages: Annotated[list[BaseMessage], operator.add]
    system_instructions: str


def get_langchain_model():
    return ChatGoogleGenerativeAI(
        model=constants.MODEL_NAME,
        google_api_key=os.getenv("GEMINI_API_KEY"),
        temperature=constants.TEMPERATURE,
        max_output_tokens=constants.MAX_RESPONSE_TOKENS,
        streaming=True,
    )


def vanguard_researcher_node(state: VanguardResearchMultiAgentArchitecture):
    intelligence_llm_model = get_langchain_model().bind_tools([get_search_tool()])
    intelligence_research_prompt = [
        SystemMessage(
            content=(
                "You are the Intelligence Harvester. Use the Search tool for ANY 2026 data. "
                "CRITICAL: Do not write code. Do not say 'I will search.' JUST CALL THE TOOL. "
                "Pass all raw dates and facts to the history for the Writer."
            )
        )
    ] + state["messages"]

    return {"messages": [intelligence_llm_model.invoke(intelligence_research_prompt)]}


def vanguard_writer_node(state: VanguardResearchMultiAgentArchitecture):
    technical_llm_model = get_langchain_model()

    writing_prompt = [
        SystemMessage(
            content=(
                f"{state['system_instructions']}\n"
                "WRITER ROLE: You are the Lead Synthesis Engineer for Vanguard Research. "
                "\n1. REVIEW the raw data in history. "
                "\n2. SELECT the top 3-5 most critical innovations/facts. "
                "\n3. FORMAT: Use a concise table for comparisons and bullet points for details. "
                "\n4. LIMIT: Do not create tables with more than 5 rows. Prioritize scannability. "
                "\n5. Ensure the report is professional and formatted in clear Markdown."
            )
        )
    ] + state["messages"]

    synthesized_report_response = technical_llm_model.invoke(writing_prompt)

    return {"messages": [synthesized_report_response]}


def get_vanguard_research_app():
    vanguard_graph_blueprint = StateGraph(VanguardResearchMultiAgentArchitecture)

    vanguard_graph_blueprint.add_node("harvester_node", vanguard_researcher_node)
    vanguard_graph_blueprint.add_node("synthesizer_node", vanguard_writer_node)
    vanguard_graph_blueprint.add_node(
        "external_tools_node", ToolNode([get_search_tool()])
    )

    vanguard_graph_blueprint.add_edge(START, "harvester_node")

    def intelligence_flow_router(state_data: VanguardResearchMultiAgentArchitecture):
        latest_research_output = state_data["messages"][-1]

        next_destination = (
            "external_tools_node"
            if latest_research_output.tool_calls
            else "synthesizer_node"
        )

        return next_destination

    vanguard_graph_blueprint.add_conditional_edges(
        "harvester_node", intelligence_flow_router
    )

    vanguard_graph_blueprint.add_edge("external_tools_node", "harvester_node")

    vanguard_graph_blueprint.add_edge("synthesizer_node", END)

    return vanguard_graph_blueprint.compile()


def execute_neural_processing(message_log, active_session_id):
    app = get_vanguard_research_app()

    with st.chat_message(constants.ASSISTANT_ROLE, avatar=constants.BOT_AVATAR):
        status_placeholder = st.empty()
        status_placeholder.status(
            f"{constants.APP_NAME} coordinating...", expanded=False
        )

        formatted_history = [
            (
                HumanMessage(content=msg_class["content"])
                if msg_class["role"] == constants.USER_ROLE
                else AIMessage(content=msg_class["content"])
            )
            for msg_class in message_log
        ]

        try:
            ai_chatbot_runtime_response = app.invoke(
                {
                    "messages": formatted_history,
                    "system_instructions": constants.get_dynamic_system_instructions(),
                }
            )
            status_placeholder.empty()

            final_intelligence_report = ""

            for agent_message in reversed(ai_chatbot_runtime_response["messages"]):
                if isinstance(agent_message, AIMessage) and agent_message.content:

                    if isinstance(agent_message.content, list):
                        intelligence_content_fragments = []

                        for content_segment in agent_message.content:
                            if isinstance(content_segment, dict):
                                intelligence_content_fragments.append(
                                    content_segment.get("text", "")
                                )
                            else:
                                intelligence_content_fragments.append(
                                    str(content_segment)
                                )

                        final_intelligence_report = "".join(
                            intelligence_content_fragments
                        )
                    else:
                        final_intelligence_report = str(agent_message.content)

                    if final_intelligence_report.strip():
                        break

            st.markdown(final_intelligence_report.strip())
            st.session_state.chat_sessions[active_session_id]["messages"].append(
                {"role": constants.ASSISTANT_ROLE, "content": final_intelligence_report}
            )
            execution_process_completed = True
        except Exception as e:
            st.error(f"Execution Error: {e}")
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
