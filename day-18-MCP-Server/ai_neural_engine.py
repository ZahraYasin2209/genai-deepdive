import base64
import operator
import os
import pathlib
import sqlite3
import sys
from typing import Annotated, TypedDict

import streamlit as st
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph import END, START, StateGraph
from langgraph.prebuilt import ToolNode

import constants
from tools_engine import get_search_tool


DB_PATH = "/Users/macbook/Desktop/Gen AI training/openai_sandbox/genai-deepdive/day-18-MCP-Server/vanguard_memory.db"

BASE_DIR = str(pathlib.Path(__file__).parent.resolve())

if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

try:
    import ai_neural_engine
except ImportError as e:
    sys.stderr.write(f"Import Error: {str(e)}\n")
    sys.stderr.write(f"Current BASE_DIR detected: {BASE_DIR}\n")


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
        SystemMessage(content=constants.HARVESTER_INSTRUCTIONS)
    ] + state["messages"]

    return {"messages": [intelligence_llm_model.invoke(intelligence_research_prompt)]}


def vanguard_writer_node(state: VanguardResearchMultiAgentArchitecture):
    technical_llm_model = get_langchain_model()
    writing_prompt = [
        SystemMessage(
            content=f"{state['system_instructions']}\n{constants.SYNTHESIZER_INSTRUCTIONS}"
        )
    ] + state["messages"]

    return {"messages": [technical_llm_model.invoke(writing_prompt)]}


def load_session_history(thread_id):
    vanguard_app = get_vanguard_research_app()
    graph_state_snapshot = vanguard_app.get_state(
        {"configurable": {"thread_id": str(thread_id)}}
    )
    formatted_conversational_log = []

    seen_messages = set()

    for agent_message in graph_state_snapshot.values.get("messages", []):
        if agent_message.type == "tool" or (
            hasattr(agent_message, "tool_calls") and agent_message.tool_calls
        ):
            continue

        message_role = (
            constants.USER_ROLE
            if agent_message.type == "human"
            else constants.ASSISTANT_ROLE
        )

        raw_message_payload = ""
        if isinstance(agent_message.content, list):
            for content_fragment in agent_message.content:
                if isinstance(content_fragment, dict) and "text" in content_fragment:
                    raw_message_payload += content_fragment["text"]
                else:
                    raw_message_payload += str(content_fragment)
        else:
            raw_message_payload = str(agent_message.content)

        raw_message_payload = raw_message_payload.strip()
        if (
            raw_message_payload
            and (message_role, raw_message_payload) not in seen_messages
        ):
            formatted_conversational_log.append(
                {"role": message_role, "content": raw_message_payload}
            )
            seen_messages.add((message_role, raw_message_payload))

    return formatted_conversational_log


@st.cache_resource
def get_vanguard_research_app(bypass_authorization=False):
    db_connection = sqlite3.connect(DB_PATH, check_same_thread=False)
    vanguard_checkpointer = SqliteSaver(db_connection)

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

    interrupt_list = [] if bypass_authorization else ["external_tools_node"]

    return vanguard_graph_blueprint.compile(
        checkpointer=vanguard_checkpointer, interrupt_before=interrupt_list
    )


def execute_neural_processing(message_log, active_session_id):
    vanguard_app = get_vanguard_research_app()

    active_thread_checkpoint = vanguard_app.get_state(
        {"configurable": {"thread_id": str(active_session_id)}}
    )

    with st.chat_message(constants.ASSISTANT_ROLE, avatar=constants.BOT_AVATAR):
        if (
            active_thread_checkpoint.next
            and "external_tools_node" in active_thread_checkpoint.next
        ):
            st.warning("**Vanguard Security Protocol**: Authorization Required.")

            if st.button("Authorize Intelligence Harvest"):
                resumed_state = vanguard_app.invoke(
                    None, config={"configurable": {"thread_id": str(active_session_id)}}
                )

                final_intelligence_report = ""
                for agent_msg in reversed(resumed_state["messages"]):
                    if (
                        isinstance(agent_msg, AIMessage)
                        and agent_msg.content
                        and not getattr(agent_msg, "tool_calls", None)
                    ):
                        if isinstance(agent_msg.content, list):
                            final_intelligence_report = "".join(
                                [
                                    (
                                        content_block["text"]
                                        if isinstance(content_block, dict)
                                        and "text" in content_block
                                        else str(content_block)
                                    )
                                    for content_block in agent_msg.content
                                ]
                            )
                        else:
                            final_intelligence_report = str(agent_msg.content)
                        break

                if final_intelligence_report:
                    st.markdown(final_intelligence_report.strip())
                    st.session_state.chat_sessions[active_session_id][
                        "messages"
                    ].append(
                        {
                            "role": constants.ASSISTANT_ROLE,
                            "content": final_intelligence_report.strip(),
                        }
                    )
                    st.rerun()
                else:
                    st.error(
                        "Intelligence Synthesizer failed to produce a report after harvest."
                    )
            st.stop()

        formatted_history = [
            (
                HumanMessage(content=msg_class["content"])
                if msg_class["role"] == constants.USER_ROLE
                else AIMessage(content=msg_class["content"])
            )
            for msg_class in message_log
        ]

        try:
            ai_chatbot_runtime_response = vanguard_app.invoke(
                {
                    "messages": formatted_history,
                    "system_instructions": constants.get_dynamic_system_instructions(),
                },
                config={"configurable": {"thread_id": str(active_session_id)}},
            )

            post_invoke_snapshot = vanguard_app.get_state(
                {"configurable": {"thread_id": str(active_session_id)}}
            )
            if post_invoke_snapshot.next:
                st.rerun()

            final_intelligence_report = ""

            for msg_class in reversed(ai_chatbot_runtime_response["messages"]):
                if (
                    isinstance(msg_class, AIMessage)
                    and msg_class.content
                    and not msg_class.tool_calls
                ):
                    if isinstance(msg_class.content, list):
                        fragments = []
                        for content_block in msg_class.content:
                            if (
                                isinstance(content_block, dict)
                                and "text" in content_block
                            ):
                                fragments.append(content_block["text"])
                            else:
                                fragments.append(str(content_block))
                        final_intelligence_report = "".join(fragments)
                    else:
                        final_intelligence_report = str(msg_class.content)

                    final_intelligence_report = final_intelligence_report.strip()
                    break

            if final_intelligence_report:
                st.markdown(final_intelligence_report.strip())
                st.session_state.chat_sessions[active_session_id]["messages"].append(
                    {
                        "role": constants.ASSISTANT_ROLE,
                        "content": final_intelligence_report,
                    }
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
