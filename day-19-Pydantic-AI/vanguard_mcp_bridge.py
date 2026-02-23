import math
import re
import sys
import uuid

from mcp.server.fastmcp import FastMCP
from pydantic import BaseModel, Field

BASE_DIR = "/Users/macbook/Desktop/Gen AI training/openai_sandbox/genai-deepdive/day-18-MCP-Server"
if BASE_DIR not in sys.path:
    sys.path.append(BASE_DIR)

try:
    import ai_neural_engine
except ImportError:
    print(f"Error: Could not find ai_neural_engine.py in {BASE_DIR}")


mcp = FastMCP("Vanguard Research")


def escape_ansi(text: str) -> str:
    ansi_escape = re.compile(r"(?:\x1B[@-Z\\-_]|\x1B\[[0-?]*[ -/]*[@-~])")

    return ansi_escape.sub("", text)


class CalculatorInput(BaseModel):
    """Schema for the mathematical expression evaluator."""
    expression: str = Field(
        description="A Python-compliant mathematical string. Supports arithmetic (+, -, *, /) "
        "and math library functions like 'math.sqrt()', 'math.sin()', or 'math.pow()'. "
    )


class WebSearchInput(BaseModel):
    """Schema for the real-time intelligence retrieval engine."""
    topic: str = Field(
        description="The specific research query or entity to investigate. Use detailed "
        "natural language for better retrieval."
    )


@mcp.tool()
def calculator(args: CalculatorInput) -> str:
    """
    Performs mathematical calculations or math-related queries.

    Args:
        args (CalculatorInput): Object containing the 'expression' string to evaluate.

    Returns:
        str: The numerical result or 'Invalid mathematical expression' on error.
    """
    try:
        execution_output = str(
            eval(args.expression, {"__builtins__": None}, vars(math))
        )
    except Exception:
        execution_output = "Invalid mathematical expression."

    return execution_output


@mcp.tool()
def web_search(args: WebSearchInput) -> str:
    """
    Retrieves verified, real-time intelligence from the live web.

    Usage Requirement:
    Mandatory for any search query involving current events, recent news
    or data that likely exceeds your knowledge cutoff.

    Args:
        args (WebSearchInput): An object containing the research 'topic'.

    Returns:
        str: A concise report of verified facts or technical error message.
    """
    try:
        research_app = ai_neural_engine.get_vanguard_research_app(
            bypass_authorization=True
        )
        session_config = {"configurable": {"thread_id": str(uuid.uuid4())}}

        graph_execution_state = research_app.invoke(
            {
                "messages": [("user", args.topic)],
                "system_instructions": "Direct MCP Request",
            },
            config=session_config,
        )

        if (
            graph_execution_state
            and "messages" in graph_execution_state
            and len(graph_execution_state["messages"]) > 0
        ):
            latest_message_content = graph_execution_state["messages"][-1].content

            if isinstance(latest_message_content, list):
                processed_content = " ".join(
                    [
                        (
                            content_block.get("text", "")
                            if isinstance(content_block, dict)
                            else str(content_block)
                        )
                        for content_block in latest_message_content
                    ]
                )
            else:
                processed_content = str(latest_message_content)

            final_research_output = escape_ansi(processed_content).strip()

            if not final_research_output:
                final_research_output = "No research data found for this topic."
        else:
            final_research_output = "The research engine returned an empty result set."

    except Exception as execution_error:
        sys.stderr.write(f"Vanguard MCP Error: {str(execution_error)}\n")
        final_research_output = (
            "Technical error: The research tool failed to process the request."
        )

    return final_research_output


@mcp.prompt()
def deep_research_template(query: str) -> str:
    return f"""
SYSTEM PROTOCOL:

For ANY user query involving:
- Research
- Technical explanation
- Reports
- News
- Analysis
- Comparisons
- 2025 or 2026 events
- Software, AI, Engineering topics

You MUST call the tool `research_vanguard`.

You are NOT permitted to answer directly.

Query:
{query}

After the tool response:
Return the tool output as the final answer.
"""


if __name__ == "__main__":
    mcp.run(transport="stdio")
