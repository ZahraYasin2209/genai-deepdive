import base64
import operator
import os
import sqlite3
from typing import Annotated, TypedDict

import streamlit as st
from langchain_core.messages import AIMessage, BaseMessage, HumanMessage, SystemMessage
from langchain_google_genai import ChatGoogleGenerativeAI
from langgraph.checkpoint.sqlite import SqliteSaver
from langgraph.graph import END, START, StateGraph
from langgraph.prebuilt import ToolNode

import constants
from tools_engine import get_search_tool


class VanguardResearchMultiAgentArchitecture(TypedDict):
    messages: Annotated[list[BaseMessage], operator.add]
    system_instructions: str


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

    for agent_message in graph_state_snapshot.values.get("messages", []):
        has_active_tool_calls = (
            hasattr(agent_message, "tool_calls") and agent_message.tool_calls
        )
        if not has_active_tool_calls:
            message_role = (
                constants.USER_ROLE
                if agent_message.type == "human"
                else constants.ASSISTANT_ROLE
            )
            raw_message_payload = agent_message.content

            if isinstance(raw_message_payload, list):
                sanitized_text_output = "".join(
                    [
                        content_fragment["text"]
                        for content_fragment in raw_message_payload
                        if isinstance(content_fragment, dict)
                        and "text" in content_fragment
                    ]
                )
                formatted_conversational_log.append(
                    {"role": message_role, "content": sanitized_text_output}
                )
            else:
                formatted_conversational_log.append(
                    {"role": message_role, "content": str(raw_message_payload)}
                )

    return formatted_conversational_log


@st.cache_resource
def get_vanguard_research_app():
    db_connection = sqlite3.connect("vanguard_memory.db", check_same_thread=False)
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

    return vanguard_graph_blueprint.compile(
        checkpointer=vanguard_checkpointer, interrupt_before=["external_tools_node"]
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
                        and not agent_msg.tool_calls
                    ):
                        if isinstance(agent_msg.content, list):
                            intelligence_content_fragments = [
                                (
                                    content_block["text"]
                                    if isinstance(content_block, dict)
                                    and "text" in content_block
                                    else str(content_block)
                                )
                                for content_block in agent_msg.content
                            ]
                            final_intelligence_report = "".join(
                                intelligence_content_fragments
                            )
                        else:
                            final_intelligence_report = str(agent_msg.content)
                        break

                if final_intelligence_report.strip():
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
                        fragments = [
                            (
                                block["text"]
                                if isinstance(block, dict) and "text" in block
                                else str(block)
                            )
                            for block in msg_class.content
                        ]
                        final_intelligence_report = "".join(fragments)
                    else:
                        final_intelligence_report = str(msg_class.content)
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
